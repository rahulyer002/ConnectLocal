"""
gtfs_processing.py
-------------------
Processes PTV GTFS Schedule data for Metropolitan Train, Tram and Bus.

Inputs:
  Data/raw/gtfs/train/  (stops, routes, trips, stop_times, calendar,
                          pathways, levels, transfers, calendar_dates)
  Data/raw/gtfs/tram/   (same structure)
  Data/raw/gtfs/bus/    (same structure)

Outputs:
  Data/processed/gtfs_stops.csv       — all stops with route info + accessibility
  Data/processed/gtfs_routes.csv      — all routes with mode label
  Data/processed/gtfs_patterns.csv    — avg departures per stop per hour
  Data/processed/gtfs_pathways.csv    — elevator/stairs/walkway info (train only)
  Data/processed/gtfs_transfers.csv   — transfer points between routes

Processing steps:
  1. Load stops from train/tram/bus, add mode column
  2. Filter stops: Melbourne metro area only
     (lat: -38.2 to -37.5, lon: 144.5 to 145.6)
  3. Join route names to stops via trips + stop_times
  4. Process pathways: flag elevator vs stairs vs walkway
  5. Process transfers: keep meaningful transfer points
  6. Aggregate stop_times: avg departures per stop per hour
     (stop_times is 15M rows — process in chunks)
  7. Map stops to nearest suburb via haversine
  8. Export all processed files

Key fields for elderly:
  wheelchair_boarding: 1 = accessible, 2 = not accessible
  pathway_mode: 5 = elevator (best), 2 = stairs (avoid)
  wheelchair_accessible (trips): 1 = accessible vehicle
"""

from __future__ import annotations
from pathlib import Path
import math
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw" / "gtfs"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Melbourne metro bounding box
LAT_MIN, LAT_MAX = -38.2, -37.5
LON_MIN, LON_MAX = 144.5, 145.6

# GTFS route_type → human label
ROUTE_TYPE_LABEL = {
    "0": "Tram",
    "1": "Metro",
    "2": "Rail",
    "3": "Bus",
    "400": "Train",  # PTV uses 400 for train
    "700": "Bus",
    "900": "Tram",
}

# Pathway mode → human label
PATHWAY_MODE_LABEL = {
    "1": "Walkway",
    "2": "Stairs",
    "3": "Moving Walkway",
    "4": "Escalator",
    "5": "Elevator",
    "6": "Fare Gate",
    "7": "Exit Gate",
}

MODES = {
    "train": RAW_DIR / "train",
    "tram": RAW_DIR / "tram",
    "bus": RAW_DIR / "bus",
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def read_gtfs(mode_dir: Path, filename: str, **kwargs) -> pd.DataFrame:
    """Read a GTFS txt file, handle BOM and quoted fields."""
    path = mode_dir / filename
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, **kwargs)
    df.columns = df.columns.str.strip()
    # Strip surrounding quotes from all string values
    df = df.apply(lambda col: col.str.strip('"').str.strip() if col.dtype == object else col)
    return df


def load_suburb_reference() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_reference.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return pd.read_csv(path)


# ─── Stops ────────────────────────────────────────────────────────────────────

def load_all_stops() -> pd.DataFrame:
    """Load and combine stops from all three modes."""
    dfs = []
    for mode, mode_dir in MODES.items():
        df = read_gtfs(mode_dir, "stops.txt")
        if df.empty:
            print(f"WARNING: No stops.txt for {mode}")
            continue
        df["mode"] = mode
        dfs.append(df)
        print(f"Loaded {len(df)} {mode} stops")

    combined = pd.concat(dfs, ignore_index=True)
    print(f"\nTotal stops (all modes): {len(combined)}")
    return combined


def clean_stops(df: pd.DataFrame) -> pd.DataFrame:
    """Clean stops and filter to Melbourne metro area."""
    df = df.copy()

    df["stop_lat"] = pd.to_numeric(df["stop_lat"], errors="coerce")
    df["stop_lon"] = pd.to_numeric(df["stop_lon"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["stop_lat", "stop_lon"]).copy()

    # Filter to Melbourne metro bounding box
    df = df[
        (df["stop_lat"] >= LAT_MIN) & (df["stop_lat"] <= LAT_MAX) &
        (df["stop_lon"] >= LON_MIN) & (df["stop_lon"] <= LON_MAX)
    ].copy()

    print(f"Filtered stops: {before} → {len(df)} (Melbourne metro area)")

    # Wheelchair boarding: 0/blank=unknown, 1=accessible, 2=not accessible
    df["wheelchair_boarding"] = df["wheelchair_boarding"].fillna("0")
    df["is_wheelchair_accessible"] = df["wheelchair_boarding"] == "1"
    df["is_wheelchair_inaccessible"] = df["wheelchair_boarding"] == "2"

    print(f"Wheelchair accessible stops: {df['is_wheelchair_accessible'].sum()}")
    print(f"Not accessible stops: {df['is_wheelchair_inaccessible'].sum()}")
    print(f"Unknown accessibility: {(df['wheelchair_boarding'] == '0').sum()}")

    # Rename for consistency
    df = df.rename(columns={
        "stop_id": "stop_id",
        "stop_name": "stop_name",
        "stop_lat": "lat",
        "stop_lon": "lon",
        "location_type": "location_type",
        "parent_station": "parent_station",
    })

    return df


# ─── Routes ───────────────────────────────────────────────────────────────────

def load_all_routes() -> pd.DataFrame:
    """Load and combine routes from all three modes."""
    dfs = []
    for mode, mode_dir in MODES.items():
        df = read_gtfs(mode_dir, "routes.txt")
        if df.empty:
            continue
        df["mode"] = mode
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)

    combined["mode_label"] = combined["route_type"].map(ROUTE_TYPE_LABEL).fillna("Other")

    print(f"\nTotal routes: {len(combined)}")
    print(f"By mode:\n{combined['mode_label'].value_counts()}")
    return combined


# ─── Trips + route join ───────────────────────────────────────────────────────

def load_all_trips() -> pd.DataFrame:
    dfs = []
    for mode, mode_dir in MODES.items():
        df = read_gtfs(mode_dir, "trips.txt")
        if df.empty:
            continue
        df["mode"] = mode
        dfs.append(df)
    return pd.concat(dfs, ignore_index=True)


def build_stop_route_map(stops: pd.DataFrame) -> pd.DataFrame:
    """
    Build a mapping of stop_id → list of routes serving it.
    Process stop_times in chunks (15M rows).
    """
    print("\nBuilding stop → route mapping from stop_times (chunked)...")

    stop_routes: dict[str, set] = {}

    for mode, mode_dir in MODES.items():
        stop_times_path = mode_dir / "stop_times.txt"
        if not stop_times_path.exists():
            print(f"  No stop_times.txt for {mode} — skipping route mapping")
            continue

        trips_df = read_gtfs(mode_dir, "trips.txt")
        routes_df = read_gtfs(mode_dir, "routes.txt")

        # Build trip_id → route_short_name map
        trip_route = trips_df.merge(
            routes_df[["route_id", "route_short_name"]],
            on="route_id", how="left"
        )[["trip_id", "route_short_name"]].drop_duplicates()
        trip_to_route = dict(zip(trip_route["trip_id"], trip_route["route_short_name"]))

        chunk_size = 500_000
        chunk_count = 0
        for chunk in pd.read_csv(
            stop_times_path, encoding="utf-8-sig", dtype=str,
            chunksize=chunk_size
        ):
            chunk.columns = chunk.columns.str.strip()
            chunk = chunk.apply(
                lambda col: col.str.strip('"').str.strip()
                if col.dtype == object else col
            )

            for _, row in chunk[["stop_id", "trip_id"]].iterrows():
                sid = str(row["stop_id"]).strip()
                route = trip_to_route.get(str(row["trip_id"]).strip(), "")
                if sid not in stop_routes:
                    stop_routes[sid] = set()
                if route:
                    stop_routes[sid].add(route)

            chunk_count += 1
            if chunk_count % 5 == 0:
                print(f"  {mode}: processed {chunk_count * chunk_size:,} rows...")

        print(f"  {mode}: done")

    stops = stops.copy()
    stops["routes_served"] = stops["stop_id"].map(
        lambda sid: ",".join(sorted(
            str(r) for r in stop_routes.get(sid, [])
            if r and str(r).strip() not in ("", "nan", "None")
        ))
    )
    stops["route_count"] = stops["routes_served"].apply(
        lambda r: len([x for x in r.split(",") if x]) if r else 0
    )

    return stops


# ─── Stop departure patterns ──────────────────────────────────────────────────

def compute_departure_patterns() -> pd.DataFrame:
    """
    Aggregate stop_times to avg departures per stop per hour.
    Process all three modes in chunks.
    Output: stop_id, hour, mode, avg_departures_per_hour
    """
    print("\nComputing departure patterns per stop per hour (chunked)...")
    all_records = []

    for mode, mode_dir in MODES.items():
        stop_times_path = mode_dir / "stop_times.txt"
        if not stop_times_path.exists():
            print(f"  No stop_times.txt for {mode}")
            continue

        # Load calendar to get weekday services
        calendar = read_gtfs(mode_dir, "calendar.txt")
        weekday_services = set(
            calendar[
                (calendar["monday"] == "1") |
                (calendar["tuesday"] == "1") |
                (calendar["wednesday"] == "1") |
                (calendar["thursday"] == "1") |
                (calendar["friday"] == "1")
            ]["service_id"].tolist()
        )

        trips = read_gtfs(mode_dir, "trips.txt")
        weekday_trips = set(
            trips[trips["service_id"].isin(weekday_services)]["trip_id"].tolist()
        )

        stop_hour_counts: dict[tuple, list] = {}
        chunk_size = 500_000

        for chunk in pd.read_csv(
            stop_times_path, encoding="utf-8-sig", dtype=str,
            chunksize=chunk_size
        ):
            chunk.columns = chunk.columns.str.strip()
            chunk = chunk.apply(
                lambda col: col.str.strip('"').str.strip()
                if col.dtype == object else col
            )

            # Filter to weekday trips only
            chunk = chunk[chunk["trip_id"].isin(weekday_trips)]

            # Parse hour from departure_time
            def parse_hour(t: str) -> int | None:
                try:
                    h = int(str(t).split(":")[0])
                    return h % 24  # handle times > 24:00
                except Exception:
                    return None

            chunk["hour"] = chunk["departure_time"].apply(parse_hour)
            chunk = chunk.dropna(subset=["hour"])
            chunk["hour"] = chunk["hour"].astype(int)
            chunk["stop_id"] = chunk["stop_id"].str.strip()

            for _, row in chunk[["stop_id", "hour"]].iterrows():
                key = (row["stop_id"], row["hour"])
                if key not in stop_hour_counts:
                    stop_hour_counts[key] = []
                stop_hour_counts[key].append(1)

        # Convert to dataframe
        records = [
            {
                "stop_id": k[0],
                "hour": k[1],
                "departure_count": len(v),
                "mode": mode,
            }
            for k, v in stop_hour_counts.items()
        ]
        all_records.extend(records)
        print(f"  {mode}: {len(records):,} stop-hour combinations")

    patterns = pd.DataFrame(all_records)

    # Compute avg departures
    # departure_count here = total departures across all weekdays
    # Divide by number of weekdays in the dataset to get avg per day
    patterns["avg_departures_per_hour"] = (patterns["departure_count"] / 5).round(1)

    print(f"\nTotal departure patterns: {len(patterns):,}")
    return patterns


# ─── Pathways ────────────────────────────────────────────────────────────────

def process_pathways() -> pd.DataFrame:
    """
    Process train station pathways.
    Key for elderly: identify elevator (mode=5) vs stairs (mode=2).
    Only train has meaningful pathway data.
    """
    train_dir = MODES["train"]
    pathways = read_gtfs(train_dir, "pathways.txt")
    levels = read_gtfs(train_dir, "levels.txt")

    if pathways.empty:
        print("No pathways data found")
        return pd.DataFrame()

    pathways["pathway_mode"] = pathways["pathway_mode"].astype(str).str.strip('"')
    pathways["pathway_mode_label"] = pathways["pathway_mode"].map(PATHWAY_MODE_LABEL)
    pathways["has_elevator"] = pathways["pathway_mode"] == "5"
    pathways["has_stairs"] = pathways["pathway_mode"] == "2"
    pathways["traversal_time"] = pd.to_numeric(pathways["traversal_time"], errors="coerce")

    print(f"\nPathway modes:\n{pathways['pathway_mode_label'].value_counts()}")
    print(f"Stations with elevator access: {pathways[pathways['has_elevator']]['from_stop_id'].nunique()}")

    return pathways[[
        "pathway_id",
        "from_stop_id",
        "to_stop_id",
        "pathway_mode",
        "pathway_mode_label",
        "has_elevator",
        "has_stairs",
        "is_bidirectional",
        "traversal_time",
    ]]


# ─── Transfers ────────────────────────────────────────────────────────────────

def process_transfers() -> pd.DataFrame:
    """Process train transfers — connection points between services."""
    train_dir = MODES["train"]
    transfers = read_gtfs(train_dir, "transfers.txt")

    if transfers.empty:
        return pd.DataFrame()

    transfers["min_transfer_time"] = pd.to_numeric(
        transfers["min_transfer_time"], errors="coerce"
    )
    transfers["transfer_type"] = transfers["transfer_type"].astype(str)

    print(f"\nTransfers: {len(transfers)}")
    print(f"Transfer types:\n{transfers['transfer_type'].value_counts()}")

    return transfers


# ─── Map stops to suburbs ─────────────────────────────────────────────────────

def map_stops_to_suburbs(stops: pd.DataFrame, suburb_ref: pd.DataFrame) -> pd.DataFrame:
    """Map each stop to nearest suburb centroid."""
    print("\nMapping stops to suburbs...")
    stops = stops.copy()
    suburb_ids = []
    suburb_names = []

    for _, row in stops.iterrows():
        distances = suburb_ref.apply(
            lambda s: haversine_km(row["lat"], row["lon"],
                                   s["centroid_lat"], s["centroid_lng"]),
            axis=1
        )
        nearest = distances.idxmin()
        suburb_ids.append(suburb_ref.loc[nearest, "suburb_id"])
        suburb_names.append(suburb_ref.loc[nearest, "suburb_name"])

    stops["suburb_id"] = suburb_ids
    stops["suburb_name"] = suburb_names
    return stops


# ─── Export ───────────────────────────────────────────────────────────────────

def export_stops(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "gtfs_stops.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved stops: {out} | Shape: {df.shape}")
    print(f"Wheelchair accessible: {df['is_wheelchair_accessible'].sum()}")
    print(f"By mode:\n{df['mode'].value_counts()}")


def export_routes(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "gtfs_routes.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved routes: {out} | Shape: {df.shape}")


def export_patterns(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "gtfs_patterns.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved patterns: {out} | Shape: {df.shape}")


def export_pathways(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "gtfs_pathways.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved pathways: {out} | Shape: {df.shape}")


def export_transfers(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "gtfs_transfers.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved transfers: {out} | Shape: {df.shape}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    suburb_ref = load_suburb_reference()

    # Stops
    raw_stops = load_all_stops()
    stops = clean_stops(raw_stops)

    # Routes
    routes = load_all_routes()
    export_routes(routes)

    # Pathways (train only)
    pathways = process_pathways()
    if not pathways.empty:
        export_pathways(pathways)

    # Transfers (train only)
    transfers = process_transfers()
    if not transfers.empty:
        export_transfers(transfers)

    # Map stops to suburbs
    stops = map_stops_to_suburbs(stops, suburb_ref)

    # Departure patterns (reads stop_times in chunks)
    print("\nNote: Computing departure patterns reads 15M rows — may take 5-10 mins...")
    patterns = compute_departure_patterns()
    export_patterns(patterns)

    # Join route info to stops
    print("\nBuilding stop route map...")
    stops = build_stop_route_map(stops)
    export_stops(stops)

    print("\nDone! Processed files:")
    print("  gtfs_stops.csv")
    print("  gtfs_routes.csv")
    print("  gtfs_patterns.csv")
    print("  gtfs_pathways.csv")
    print("  gtfs_transfers.csv")


if __name__ == "__main__":
    main()

"""
pedestrian_sensors_processing.py
----------------------------------
Cleans the City of Melbourne pedestrian sensor locations dataset.

Input:  Data/raw/pedestrian_sensor_locations.csv (145 rows)
Output: Data/processed/pedestrian_sensors.csv

Processing steps:
  1. Strip BOM, clean column names
  2. Filter: keep only active sensors (status = 'A')
  3. Clean and validate coordinates
  4. Map each sensor to nearest suburb
  5. Export processed CSV
"""

from __future__ import annotations
from pathlib import Path
import math
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─── Load ─────────────────────────────────────────────────────────────────────

def load_sensors() -> pd.DataFrame:
    path = RAW_DIR / "pedestrian_sensor_locations.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    print(f"Loaded {len(df)} sensors")
    print(f"Columns: {df.columns.tolist()}")
    return df


def load_suburb_reference() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_reference.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return pd.read_csv(path)


# ─── Clean ────────────────────────────────────────────────────────────────────

def clean_sensors(df: pd.DataFrame) -> pd.DataFrame:
    # Clean coordinates
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")

    before = len(df)
    df = df.dropna(subset=["latitude", "longitude"]).copy()
    print(f"Dropped {before - len(df)} sensors with missing coordinates")

    # Status breakdown
    print(f"\nStatus breakdown:\n{df['status'].value_counts()}")
    print(f"Location type:\n{df['location_type'].value_counts()}")

    # Filter active sensors only
    df = df[df["status"] == "A"].copy()
    print(f"\nKept {len(df)} active sensors")

    # Rename for consistency
    df = df.rename(columns={
        "location_id": "sensor_id",
        "sensor_description": "sensor_description",
        "latitude": "lat",
        "longitude": "lon",
    })

    return df

def deduplicate_sensors(df: pd.DataFrame) -> pd.DataFrame:
    """
    Some sensors appear multiple times with different direction labels.
    Keep first occurrence per sensor_id.
    Prefer Outdoor over Indoor entries.
    """
    # Sort: Outdoor before Indoor, then by sensor_id
    df["_sort"] = df["location_type"].apply(lambda x: 0 if x == "Outdoor" else 1)
    df = df.sort_values(["sensor_id", "_sort"]).drop(columns=["_sort"])
    before = len(df)
    df = df.drop_duplicates(subset=["sensor_id"], keep="first")
    print(f"Deduplicated sensors: {before} → {len(df)}")
    return df
# ─── Enrich ───────────────────────────────────────────────────────────────────

def map_to_suburbs(df: pd.DataFrame, suburb_ref: pd.DataFrame) -> pd.DataFrame:
    """Map each sensor to nearest suburb centroid."""
    df = df.copy()
    suburb_ids = []
    suburb_names = []

    for _, row in df.iterrows():
        distances = suburb_ref.apply(
            lambda s: haversine_km(row["lat"], row["lon"],
                                   s["centroid_lat"], s["centroid_lng"]),
            axis=1
        )
        nearest = distances.idxmin()
        suburb_ids.append(suburb_ref.loc[nearest, "suburb_id"])
        suburb_names.append(suburb_ref.loc[nearest, "suburb_name"])

    df["suburb_id"] = suburb_ids
    df["suburb_name"] = suburb_names
    return df


# ─── Build table ─────────────────────────────────────────────────────────────

def build_table(df: pd.DataFrame) -> pd.DataFrame:
    return df[[
        "sensor_id",
        "sensor_name",
        "sensor_description",
        "location_type",
        "status",
        "lat",
        "lon",
        "direction_1",
        "direction_2",
        "suburb_id",
        "suburb_name",
    ]].copy()


# ─── Export ───────────────────────────────────────────────────────────────────

def export(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "pedestrian_sensors.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved: {out}")
    print(f"Shape: {df.shape}")
    print("\nPreview:")
    print(df.head())
    print("\nLocation type breakdown:")
    print(df["location_type"].value_counts())


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    sensors = load_sensors()
    suburb_ref = load_suburb_reference()

    sensors = clean_sensors(sensors)
    sensors = deduplicate_sensors(sensors)  # ← add this
    sensors = map_to_suburbs(sensors, suburb_ref)
    result = build_table(sensors)
    export(result)


if __name__ == "__main__":
    main()

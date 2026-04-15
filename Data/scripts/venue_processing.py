from __future__ import annotations

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_event_input() -> pd.DataFrame:
    """
    Backend teammate should export API event data here.
    Expected minimum columns:
    - venue
    - address
    - latitude
    - longitude
    """
    path = PROCESSED_DIR / "event_raw.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing event input file: {path}\n"
            "Export the API event data to Data/processed/event_raw.csv first."
        )

    return pd.read_csv(path)


def load_suburb_reference() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_reference.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing suburb reference file: {path}. "
            "Run suburb_reference_processing.py first."
        )

    suburb_ref = pd.read_csv(path)
    suburb_ref["suburb_id"] = suburb_ref["suburb_id"].astype(str)

    return suburb_ref


def validate_event_columns(events: pd.DataFrame) -> None:
    required = ["venue", "address", "latitude", "longitude"]
    missing = [col for col in required if col not in events.columns]

    if missing:
        raise KeyError(
            f"Missing required event columns: {missing}\n"
            f"Available columns are: {events.columns.tolist()}"
        )


def classify_venue_type(name: str, address: str) -> str:
    text = f"{str(name)} {str(address)}".lower()

    if any(k in text for k in ["park", "garden", "gardens", "reserve", "domain"]):
        return "Outdoor Space"
    elif any(k in text for k in ["cinema", "theatre", "museum", "gallery"]):
        return "Cultural Venue"
    elif any(k in text for k in ["community", "club", "hall", "centre", "center"]):
        return "Community Venue"
    elif any(k in text for k in ["stadium", "arena", "sports"]):
        return "Sports Venue"
    elif any(k in text for k in ["library", "town hall", "civic"]):
        return "Civic Venue"
    else:
        return "General Venue"


def map_venues_to_suburbs(
    venues: pd.DataFrame,
    suburb_ref: pd.DataFrame
) -> pd.DataFrame:
    venues = venues.copy()

    suburb_ids = []

    for _, venue in venues.iterrows():
        distances = (
            (suburb_ref["centroid_lat"] - venue["lat"]) ** 2 +
            (suburb_ref["centroid_lng"] - venue["lng"]) ** 2
        ) ** 0.5

        nearest_idx = distances.idxmin()
        suburb_ids.append(suburb_ref.loc[nearest_idx, "suburb_id"])

    venues["suburb_id"] = suburb_ids

    return venues


def process_venues(events: pd.DataFrame, suburb_ref: pd.DataFrame) -> pd.DataFrame:
    validate_event_columns(events)

    venues = events[["venue", "address", "latitude", "longitude"]].copy()

    venues = venues.rename(columns={
        "venue": "name",
        "latitude": "lat",
        "longitude": "lng"
    })

    venues["lat"] = pd.to_numeric(venues["lat"], errors="coerce")
    venues["lng"] = pd.to_numeric(venues["lng"], errors="coerce")

    venues = venues.dropna(subset=["name", "lat", "lng"]).copy()

    # Deduplicate by identifying unique venues
    venues = venues.drop_duplicates(
        subset=["name", "address", "lat", "lng"]
    ).reset_index(drop=True)

    # Map suburb
    venues = map_venues_to_suburbs(venues, suburb_ref)
    venues["suburb_id"] = venues["suburb_id"].astype(str)

    # Derive type
    venues["venue_type"] = venues.apply(
        lambda row: classify_venue_type(row["name"], row["address"]),
        axis=1
    )

    # Iteration 1 placeholders / defaults
    venues["wheelchair_accessible"] = None
    venues["has_public_toilet"] = None
    venues["nearest_toilet_metres"] = None
    venues["nearest_bench_metres"] = None
    venues["canopy_cover_pct"] = None
    venues["opening_hours"] = None

    venues["venue_id"] = range(1, len(venues) + 1)

    venues = venues[[
        "venue_id",
        "suburb_id",
        "name",
        "address",
        "lat",
        "lng",
        "venue_type",
        "wheelchair_accessible",
        "has_public_toilet",
        "nearest_toilet_metres",
        "nearest_bench_metres",
        "canopy_cover_pct",
        "opening_hours"
    ]]

    return venues


def export_venues(venues: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / "venue.csv"
    venues.to_csv(output_path, index=False)

    print(f"\nSaved venue file to: {output_path}")
    print("\nPreview:")
    print(venues.head())
    print("\nShape:")
    print(venues.shape)
    print("\nVenue type breakdown:")
    print(venues["venue_type"].value_counts(dropna=False))


def main() -> None:
    events = load_event_input()
    suburb_ref = load_suburb_reference()

    print("Event input columns:")
    print(events.columns.tolist())

    venues = process_venues(events, suburb_ref)
    export_venues(venues)


if __name__ == "__main__":
    main()
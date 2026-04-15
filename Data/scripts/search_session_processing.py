from __future__ import annotations

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_suburb_profile() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_profile.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing suburb profile file: {path}. Run abs_processing.py first."
        )
    return pd.read_csv(path)


def load_open_space() -> pd.DataFrame:
    path = PROCESSED_DIR / "open_space.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing open space file: {path}. Run open_space_processing.py first."
        )
    return pd.read_csv(path)


def count_results_for_suburb(
    suburb_id: str,
    open_space: pd.DataFrame,
    category_filter: str | None = None
) -> int:
    df = open_space.copy()
    df["suburb_id"] = df["suburb_id"].astype(str)

    filtered = df[df["suburb_id"] == str(suburb_id)]

    if category_filter:
        filtered = filtered[filtered["category"] == category_filter]

    return len(filtered)


def build_search_session_table(
    suburb_profile: pd.DataFrame,
    open_space: pd.DataFrame
) -> pd.DataFrame:
    suburb_profile = suburb_profile.copy()
    suburb_profile["suburb_id"] = suburb_profile["suburb_id"].astype(str)

    # Pick some realistic suburbs from current data
    sample_suburbs = suburb_profile.head(10).copy()

    search_rows = []
    search_id = 1

    demo_filters = [
        {"category_filters": "Green Space", "free_only": True, "radius_metres": 1000},
        {"category_filters": "Urban Space", "free_only": True, "radius_metres": 1500},
        {"category_filters": "Recreation", "free_only": False, "radius_metres": 2000},
    ]

    for _, suburb in sample_suburbs.iterrows():
        for filter_config in demo_filters:
            suburb_id = suburb["suburb_id"]
            suburb_name = suburb["suburb_name"]
            search_lat = suburb["centroid_lat"]
            search_lng = suburb["centroid_lng"]
            category_filter = filter_config["category_filters"]

            results_returned = count_results_for_suburb(
                suburb_id=suburb_id,
                open_space=open_space,
                category_filter=category_filter
            )

            search_rows.append({
                "search_id": search_id,
                "suburb_id": suburb_id,
                "suburb_input": suburb_name,
                "search_lat": search_lat,
                "search_lng": search_lng,
                "radius_metres": filter_config["radius_metres"],
                "category_filters": category_filter,
                "free_only": filter_config["free_only"],
                "results_returned": results_returned
            })

            search_id += 1

    search_session = pd.DataFrame(search_rows)

    return search_session


def export_search_session(search_session: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / "search_session.csv"
    search_session.to_csv(output_path, index=False)

    print(f"\nSaved search_session file to: {output_path}")
    print("\nPreview:")
    print(search_session.head(10))
    print("\nShape:")
    print(search_session.shape)
    print("\nCategory filter breakdown:")
    print(search_session["category_filters"].value_counts(dropna=False))


def main() -> None:
    suburb_profile = load_suburb_profile()
    open_space = load_open_space()

    search_session = build_search_session_table(suburb_profile, open_space)
    export_search_session(search_session)


if __name__ == "__main__":
    main()
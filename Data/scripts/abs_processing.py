from __future__ import annotations

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = (
    BASE_DIR
    / "raw"
    / "2021_GCP_SA2_for_VIC_short-header"
    / "2021 Census GCP Statistical Area 2 for VIC"
)
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_csv(filename: str) -> pd.DataFrame:
    path = RAW_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing file: {path}")
    return pd.read_csv(path)


def load_suburb_reference() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_reference.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing suburb reference file: {path}. Run suburb_reference_processing.py first."
        )

    suburb_ref = pd.read_csv(path)
    suburb_ref["suburb_id"] = suburb_ref["suburb_id"].astype(str)

    return suburb_ref


def add_population_features(suburb: pd.DataFrame, g01: pd.DataFrame) -> pd.DataFrame:
    g01_subset = g01[[
        "SA2_CODE_2021",
        "Tot_P_P"
    ]].copy()

    g01_subset = g01_subset.rename(columns={
        "SA2_CODE_2021": "suburb_id",
        "Tot_P_P": "population_total"
    })

    g01_subset["suburb_id"] = g01_subset["suburb_id"].astype(str)
    suburb["suburb_id"] = suburb["suburb_id"].astype(str)

    suburb = suburb.merge(g01_subset, on="suburb_id", how="left")

    return suburb


def add_age_features(suburb: pd.DataFrame, g01: pd.DataFrame) -> pd.DataFrame:
    g01_subset = g01[[
        "SA2_CODE_2021",
        "Age_65_74_yr_P",
        "Age_75_84_yr_P",
        "Age_85ov_P"
    ]].copy()

    g01_subset = g01_subset.rename(columns={
        "SA2_CODE_2021": "suburb_id",
        "Age_65_74_yr_P": "population_65_74",
        "Age_75_84_yr_P": "population_75_84",
        "Age_85ov_P": "population_85_plus"
    })

    g01_subset["suburb_id"] = g01_subset["suburb_id"].astype(str)
    suburb["suburb_id"] = suburb["suburb_id"].astype(str)

    suburb = suburb.merge(g01_subset, on="suburb_id", how="left")

    return suburb


def add_assistance_features(suburb: pd.DataFrame, g18: pd.DataFrame) -> pd.DataFrame:
    g18_subset = g18[[
        "SA2_CODE_2021",
        "P_Tot_Need_for_assistance"
    ]].copy()

    g18_subset = g18_subset.rename(columns={
        "SA2_CODE_2021": "suburb_id",
        "P_Tot_Need_for_assistance": "need_assistance"
    })

    g18_subset["suburb_id"] = g18_subset["suburb_id"].astype(str)
    suburb["suburb_id"] = suburb["suburb_id"].astype(str)

    suburb = suburb.merge(g18_subset, on="suburb_id", how="left")

    return suburb


def add_landmark_count(suburb: pd.DataFrame) -> pd.DataFrame:
    suburb = suburb.copy()

    landmarks_path = PROCESSED_DIR / "landmarks.csv"
    if not landmarks_path.exists():
        raise FileNotFoundError(
            f"Missing landmarks file: {landmarks_path}. Run landmarks_processing.py first."
        )

    landmarks = pd.read_csv(landmarks_path)

    suburb["suburb_id"] = suburb["suburb_id"].astype(str)
    landmarks["suburb_id"] = landmarks["suburb_id"].astype(str)

    landmark_counts = (
        landmarks.groupby("suburb_id")
        .size()
        .reset_index(name="landmark_count")
    )

    suburb = suburb.merge(landmark_counts, on="suburb_id", how="left")
    suburb["landmark_count"] = suburb["landmark_count"].fillna(0).astype(int)

    # print("\nLandmark suburb_id sample:")
    # print(landmarks["suburb_id"].head())

    # print("\nSuburb suburb_id sample:")
    # print(suburb["suburb_id"].head())
    # print("\nTotal landmarks:", len(landmarks))
    # print("Unique suburb_ids in landmarks:", landmarks["suburb_id"].nunique())

    return suburb


def export_suburb_profile(suburb: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / "suburb_profile.csv"
    suburb.to_csv(output_path, index=False)

    print(f"\nSaved processed file to: {output_path}")
    print("\nPreview:")
    print(suburb.head())
    print("\nColumns:")
    print(suburb.columns.tolist())
    print("\nShape:")
    print(suburb.shape)


def main() -> None:
    g01 = load_csv("2021Census_G01_VIC_SA2.csv")
    g04 = load_csv("2021Census_G04A_VIC_SA2.csv")
    g11 = load_csv("2021Census_G11A_VIC_SA2.csv")
    g16 = load_csv("2021Census_G16A_VIC_SA2.csv")
    g17 = load_csv("2021Census_G17A_VIC_SA2.csv")
    g18 = load_csv("2021Census_G18_VIC_SA2.csv")

    print("G01 columns:")
    print(g01.columns.tolist())
    print("\nG04A columns:")
    print(g04.columns.tolist())
    print("\nG11A columns:")
    print(g11.columns.tolist())
    print("\nG16A columns:")
    print(g16.columns.tolist())
    print("\nG17A columns:")
    print(g17.columns.tolist())
    print("\nG18 columns:")
    print(g18.columns.tolist())

    # load suburb reference as master suburb table
    suburb = load_suburb_reference()

    #  merge ABS features onto suburb reference
    suburb = add_population_features(suburb, g01)
    suburb = add_age_features(suburb, g01)
    suburb = add_assistance_features(suburb, g18)

    # add derived landmark count
    suburb = add_landmark_count(suburb)

    # export final suburb profile
    export_suburb_profile(suburb)

    print("\nSuburbs with landmarks:")
    print(
        suburb[suburb["landmark_count"] > 0]
        .sort_values("landmark_count", ascending=False)
        .head(10)
    )
if __name__ == "__main__":
    main()
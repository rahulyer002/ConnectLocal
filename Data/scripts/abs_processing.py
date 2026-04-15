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

def build_base_suburb(g01: pd.DataFrame) -> pd.DataFrame:
    suburb = g01[["SA2_CODE_2021"]].copy()

    # Add suburb name if available in G01
    if "SA2_NAME_2021" in g01.columns:
        suburb["suburb_name"] = g01["SA2_NAME_2021"]

    suburb["population_total"] = g01["Tot_P_P"]

    suburb = suburb.rename(columns={
        "SA2_CODE_2021": "suburb_id"
    })

    return suburb


def add_age_features(suburb: pd.DataFrame, g01: pd.DataFrame) -> pd.DataFrame:
    suburb = suburb.copy()

    suburb["population_65_74"] = g01["Age_65_74_yr_P"]
    suburb["population_75_84"] = g01["Age_75_84_yr_P"]
    suburb["population_85_plus"] = g01["Age_85ov_P"]

    return suburb


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

def build_base_suburb(g01: pd.DataFrame) -> pd.DataFrame:
    suburb = g01[["SA2_CODE_2021"]].copy()

    # Add suburb name if available in G01
    if "SA2_NAME_2021" in g01.columns:
        suburb["suburb_name"] = g01["SA2_NAME_2021"]

    suburb["population_total"] = g01["Tot_P_P"]

    suburb = suburb.rename(columns={
        "SA2_CODE_2021": "suburb_id"
    })

    return suburb


def add_age_features(suburb: pd.DataFrame, g01: pd.DataFrame) -> pd.DataFrame:
    suburb = suburb.copy()

    suburb["population_65_74"] = g01["Age_65_74_yr_P"]
    suburb["population_75_84"] = g01["Age_75_84_yr_P"]
    suburb["population_85_plus"] = g01["Age_85ov_P"]

    return suburb

def add_assistance_features(suburb: pd.DataFrame, g18: pd.DataFrame) -> pd.DataFrame:
    suburb = suburb.copy()

    suburb["need_assistance"] = g18["P_Tot_Need_for_assistance"]

    return suburb


def export_suburb_profile(suburb: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / "suburb_profile.csv"
    suburb.to_csv(output_path, index=False)

    print(f"\nSaved processed file to: {output_path}")
    print("\nPreview:")
    print(suburb.head())
    print("\nColumns:")
    print(suburb.columns.tolist())


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

    # Build base suburb table
    suburb = build_base_suburb(g01)

    #Add age features
    suburb = add_age_features(suburb, g01)

    # Add assistance features
    suburb = add_assistance_features(suburb, g18)

    # Export processed file
    export_suburb_profile(suburb)

if __name__ == "__main__":
    main()





def export_suburb_profile(suburb: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / "suburb_profile.csv"
    suburb.to_csv(output_path, index=False)

    print(f"\nSaved processed file to: {output_path}")
    print("\nPreview:")
    print(suburb.head())
    print("\nColumns:")
    print(suburb.columns.tolist())


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

    # Build base suburb table
    suburb = build_base_suburb(g01)

    #Add age features
    suburb = add_age_features(suburb, g01)

    # Add assistance features
    suburb = add_assistance_features(suburb, g18)

    # Export processed file
    export_suburb_profile(suburb)

if __name__ == "__main__":
    main()



"""
trees_processing.py
--------------------
Cleans and enriches the City of Melbourne Urban Forest trees dataset.

Input:  Data/raw/urban_forest_trees.csv (82,064 rows)
Output: Data/processed/trees.csv
        Data/processed/open_space_shade.csv (shade score per open space)

Processing steps:
  1. Strip BOM, rename columns
  2. Drop unnecessary columns (Easting, Northing, geolocation, CoordinateLocation)
  3. Impute missing Diameter Breast Height (DBH) using genus median
  4. Impute missing Useful Life Expectancy from Age Description
  5. Filter: drop trees with useful life < 10 years (dying/hazardous)
  6. Derive shade_score per tree = normalised DBH (0-1 scale)
  7. Map trees to nearest open space (haversine <= 100m)
  8. Compute shade_score per open space = sum of tree shade scores nearby
  9. Map trees to nearest suburb
  10. Export trees.csv and open_space_shade.csv
"""

from __future__ import annotations
from pathlib import Path
import math
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Age Description → Useful Life Expectancy Value mapping
AGE_TO_LIFE = {
    "Young": 40,
    "Semi-mature": 30,
    "Mature": 20,
    "Over-mature": 10,
    "Senescent": 5,
}

# Useful Life Expectancy string → numeric
LIFE_LABEL_TO_VALUE = {
    "< 10 years": 5,
    "11 - 20 years": 15,
    "21 - 30 years": 25,
    "31 - 40 years": 35,
    "> 41 years": 50,
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ─── Load ─────────────────────────────────────────────────────────────────────

def load_trees() -> pd.DataFrame:
    path = RAW_DIR / "urban_forest_trees.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig", low_memory=False)
    df.columns = df.columns.str.strip()
    print(f"Loaded {len(df)} trees")
    return df


def load_suburb_reference() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_reference.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return pd.read_csv(path)


def load_open_spaces() -> pd.DataFrame:
    path = PROCESSED_DIR / "open_space.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}. Run open_space_processing.py first.")
    return pd.read_csv(path)


# ─── Clean ────────────────────────────────────────────────────────────────────

def clean_trees(df: pd.DataFrame) -> pd.DataFrame:
    # Rename columns to snake_case
    df = df.rename(columns={
        "CoM ID": "tree_id",
        "Common Name": "common_name",
        "Scientific Name": "scientific_name",
        "Genus": "genus",
        "Family": "family",
        "Diameter Breast Height": "dbh_cm",
        "Year Planted": "year_planted",
        "Age Description": "age_description",
        "Useful Life Expectency": "useful_life_label",
        "Useful Life Expectency Value": "useful_life_years",
        "Precinct": "precinct",
        "Located in": "located_in",
        "Latitude": "lat",
        "Longitude": "lon",
    })

    # Drop columns we don't need
    drop_cols = ["Date Planted", "UploadDate", "CoordinateLocation",
                 "Easting", "Northing", "geolocation", "Scientific Name",
                 "Family", "scientific_name"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Clean coordinates
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["lat", "lon"]).copy()
    print(f"Dropped {before - len(df)} rows with missing coordinates")

    # Clean DBH
    df["dbh_cm"] = pd.to_numeric(df["dbh_cm"], errors="coerce")

    # Clean useful_life_years
    df["useful_life_years"] = pd.to_numeric(df["useful_life_years"], errors="coerce")

    return df


# ─── Impute ───────────────────────────────────────────────────────────────────

def impute_dbh(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing DBH using genus median.
    If genus median also missing, use overall median.
    Missing DBH: ~44,863 rows (55%).
    """
    df = df.copy()
    missing_before = df["dbh_cm"].isna().sum()

    genus_medians = df.groupby("genus")["dbh_cm"].median()
    overall_median = df["dbh_cm"].median()

    def fill_dbh(row):
        if pd.notna(row["dbh_cm"]):
            return row["dbh_cm"]
        genus_med = genus_medians.get(row["genus"], None)
        return genus_med if pd.notna(genus_med) else overall_median

    df["dbh_cm"] = df.apply(fill_dbh, axis=1)
    df["dbh_imputed"] = df["dbh_cm"].isna()  # track which were imputed

    missing_after = df["dbh_cm"].isna().sum()
    print(f"DBH imputation: {missing_before} missing → {missing_after} remaining")
    return df


def impute_useful_life(df: pd.DataFrame) -> pd.DataFrame:
    """
    Impute missing useful_life_years using:
    1. useful_life_label string → numeric mapping
    2. age_description → numeric mapping
    """
    df = df.copy()
    missing_before = df["useful_life_years"].isna().sum()

    def fill_life(row):
        if pd.notna(row["useful_life_years"]):
            return row["useful_life_years"]
        # Try label mapping
        label = str(row.get("useful_life_label", "")).strip()
        if label in LIFE_LABEL_TO_VALUE:
            return LIFE_LABEL_TO_VALUE[label]
        # Try age description
        age = str(row.get("age_description", "")).strip()
        for key, val in AGE_TO_LIFE.items():
            if key.lower() in age.lower():
                return val
        return None

    df["useful_life_years"] = df.apply(fill_life, axis=1)
    missing_after = df["useful_life_years"].isna().sum()
    print(f"Useful life imputation: {missing_before} missing → {missing_after} remaining")
    return df


# ─── Filter ───────────────────────────────────────────────────────────────────

def filter_trees(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove trees that are dying or hazardous.
    Useful life < 10 years = not worth routing seniors past them.
    """
    before = len(df)
    df = df[
        df["useful_life_years"].isna() |  # keep unknowns
        (df["useful_life_years"] >= 10)
    ].copy()
    print(f"Filtered out {before - len(df)} dying trees (useful life < 10 years)")
    print(f"Remaining: {len(df)} trees")
    return df


# ─── Shade score ─────────────────────────────────────────────────────────────

def compute_shade_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Shade score per tree = normalised DBH on 0-1 scale.
    Larger DBH = wider canopy = more shade.
    Score = DBH / max(DBH) capped at 1.0
    """
    df = df.copy()
    max_dbh = df["dbh_cm"].max()
    df["shade_score"] = (df["dbh_cm"] / max_dbh).round(4)
    print(f"Shade score computed. Max DBH: {max_dbh}cm")
    print(f"Shade score stats:\n{df['shade_score'].describe()}")
    return df


# ─── Map to suburbs ───────────────────────────────────────────────────────────

def map_to_suburbs(df: pd.DataFrame, suburb_ref: pd.DataFrame) -> pd.DataFrame:
    """
    Vectorised haversine — much faster than row-by-row.
    Processes 82K trees in ~30 seconds instead of 30 minutes.
    """
    print("Mapping trees to suburbs (vectorised)...")
    df = df.copy()

    s_lats = suburb_ref["centroid_lat"].values
    s_lons = suburb_ref["centroid_lng"].values
    s_ids = suburb_ref["suburb_id"].values

    R = 6371
    t_lats = np.radians(df["lat"].values)
    t_lons = np.radians(df["lon"].values)
    s_lats_r = np.radians(s_lats)
    s_lons_r = np.radians(s_lons)

    suburb_ids = []
    batch = 1000

    for i in range(0, len(df), batch):
        if i % 10000 == 0:
            print(f"  {i:,} / {len(df):,} trees mapped...")

        batch_lats = t_lats[i:i+batch]
        batch_lons = t_lons[i:i+batch]

        dphi = s_lats_r[np.newaxis, :] - batch_lats[:, np.newaxis]
        dlambda = s_lons_r[np.newaxis, :] - batch_lons[:, np.newaxis]
        a = (np.sin(dphi / 2) ** 2 +
             np.cos(batch_lats[:, np.newaxis]) *
             np.cos(s_lats_r[np.newaxis, :]) *
             np.sin(dlambda / 2) ** 2)
        dists = R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        nearest_idx = np.argmin(dists, axis=1)
        suburb_ids.extend(s_ids[nearest_idx].tolist())

    df["suburb_id"] = suburb_ids
    print(f"Done mapping {len(df):,} trees to suburbs")
    return df


# ─── Shade score per open space ───────────────────────────────────────────────

def compute_open_space_shade(trees: pd.DataFrame, open_spaces: pd.DataFrame) -> pd.DataFrame:
    """
    Vectorised — computes shade score for all open spaces at once.
    For each open space: sum of shade_score of trees within 100m radius.
    """
    print("\nComputing shade scores per open space (vectorised)...")

    t_lats = np.radians(trees["lat"].values)
    t_lons = np.radians(trees["lon"].values)
    t_scores = trees["shade_score"].values
    R = 6371

    results = []
    for i, space in enumerate(open_spaces.itertuples()):
        if i % 10 == 0:
            print(f"  {i}/{len(open_spaces)} open spaces...")

        s_lat = np.radians(space.lat)
        s_lon = np.radians(space.lng)

        dphi = t_lats - s_lat
        dlambda = t_lons - s_lon
        a = (np.sin(dphi / 2) ** 2 +
             np.cos(s_lat) * np.cos(t_lats) *
             np.sin(dlambda / 2) ** 2)
        dists = R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

        mask = dists <= 0.1
        nearby_scores = t_scores[mask]
        tree_count = int(mask.sum())
        raw_shade = float(nearby_scores.sum())

        results.append({
            "space_id": space.space_id,
            "space_name": space.space_name,
            "nearby_tree_count": tree_count,
            "raw_shade_score": round(raw_shade, 4),
        })

    shade_df = pd.DataFrame(results)
    max_shade = shade_df["raw_shade_score"].max()
    if max_shade > 0:
        shade_df["shade_score_100"] = (
            (shade_df["raw_shade_score"] / max_shade) * 100
        ).round(1)
    else:
        shade_df["shade_score_100"] = 0.0

    print(f"\nOpen space shade scores:\n{shade_df['shade_score_100'].describe()}")
    return shade_df


# ─── Build final table ────────────────────────────────────────────────────────

def build_trees_table(df: pd.DataFrame) -> pd.DataFrame:
    return df[[
        "tree_id",
        "common_name",
        "genus",
        "dbh_cm",
        "useful_life_years",
        "useful_life_label",
        "age_description",
        "located_in",
        "precinct",
        "lat",
        "lon",
        "shade_score",
        "suburb_id",
    ]].copy()


# ─── Export ───────────────────────────────────────────────────────────────────

def export_trees(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "trees.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved trees: {out} | Shape: {df.shape}")
    print("\nLocated in breakdown:")
    print(df["located_in"].value_counts())
    print("\nShade score summary:")
    print(df["shade_score"].describe())


def export_open_space_shade(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "open_space_shade.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved open space shade: {out} | Shape: {df.shape}")
    print("\nPreview:")
    print(df.head(10))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    trees = load_trees()
    suburb_ref = load_suburb_reference()
    open_spaces = load_open_spaces()

    trees = clean_trees(trees)
    trees = impute_dbh(trees)
    trees = impute_useful_life(trees)
    trees = filter_trees(trees)
    trees = compute_shade_score(trees)

    print("\nMapping trees to suburbs (this may take a few minutes)...")
    trees = map_to_suburbs(trees, suburb_ref)

    print("\nComputing shade scores per open space...")
    open_space_shade = compute_open_space_shade(trees, open_spaces)

    trees_table = build_trees_table(trees)
    export_trees(trees_table)
    export_open_space_shade(open_space_shade)

    print("\nMissing value summary:")
    print(trees_table.isna().sum())


if __name__ == "__main__":
    main()
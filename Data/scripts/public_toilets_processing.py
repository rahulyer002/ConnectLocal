"""
public_toilets_processing.py
----------------------------
Cleans and enriches the City of Melbourne public toilets dataset.

Input:  Data/raw/public_toilets.csv
Output: Data/processed/public_toilets.csv

Processing steps:
  1. Strip BOM, clean column names
  2. Standardise boolean fields (yes/no/U → True/False/None)
  3. Drop rows with missing coordinates
  4. Map each toilet to nearest suburb via haversine
  5. Generate sequential toilet_id
  6. Export processed CSV
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
    """Straight-line distance in km between two lat/lon points."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def to_bool(val: str) -> bool | None:
    """Convert yes/no/U/blank to True/False/None."""
    v = str(val).strip().lower()
    if v == "yes":
        return True
    elif v == "no":
        return False
    return None


# ─── Load ─────────────────────────────────────────────────────────────────────

def load_toilets() -> pd.DataFrame:
    path = RAW_DIR / "public_toilets.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    print(f"Loaded {len(df)} toilets")
    print(f"Columns: {df.columns.tolist()}")
    return df


def load_suburb_reference() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_reference.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}. Run suburb_reference_processing.py first.")
    return pd.read_csv(path)


# ─── Clean ────────────────────────────────────────────────────────────────────

def clean_toilets(df: pd.DataFrame) -> pd.DataFrame:
    # Drop missing coordinates
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["lat", "lon"]).copy()
    print(f"Dropped {before - len(df)} rows with missing coordinates")

    # Standardise boolean fields
    df["has_female"] = df["female"].apply(to_bool)
    df["has_male"] = df["male"].apply(to_bool)
    df["has_wheelchair"] = df["wheelchair"].apply(to_bool)
    df["has_baby_facility"] = df["baby_facil"].apply(to_bool)

    print(f"Wheelchair accessible: {df['has_wheelchair'].sum()} / {len(df)}")
    print(f"Baby facility: {df['has_baby_facility'].sum()} / {len(df)}")

    return df


# ─── Enrich ───────────────────────────────────────────────────────────────────

def map_to_suburbs(df: pd.DataFrame, suburb_ref: pd.DataFrame) -> pd.DataFrame:
    """Map each toilet to nearest suburb centroid."""
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


# ─── Build final table ────────────────────────────────────────────────────────

def build_table(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["toilet_id"] = range(1, len(df) + 1)

    result = df[[
        "toilet_id",
        "suburb_id",
        "suburb_name",
        "name",
        "lat",
        "lon",
        "has_female",
        "has_male",
        "has_wheelchair",
        "has_baby_facility",
        "operator",
    ]].copy()

    result["operator"] = result["operator"].fillna("City of Melbourne")
    return result


# ─── Export ───────────────────────────────────────────────────────────────────

def export(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "public_toilets.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved: {out}")
    print(f"Shape: {df.shape}")
    print("\nPreview:")
    print(df.head())
    print("\nWheelchair breakdown:")
    print(df["has_wheelchair"].value_counts(dropna=False))


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    toilets = load_toilets()
    suburb_ref = load_suburb_reference()

    toilets = clean_toilets(toilets)
    toilets = map_to_suburbs(toilets, suburb_ref)
    result = build_table(toilets)
    export(result)


if __name__ == "__main__":
    main()

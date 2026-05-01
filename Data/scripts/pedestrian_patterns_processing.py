"""
pedestrian_patterns_processing.py
-----------------------------------
Processes City of Melbourne pedestrian counts into hourly crowd patterns.

Input:  Data/raw/pedestrian_counts_2025.csv (semicolon-delimited, 112.9MB)
Output: Data/processed/pedestrian_patterns.csv

Processing steps:
  1. Load CSV (semicolon delimiter)
  2. Parse sensing_date → date, day_of_week
  3. hourday = hour of day (0-23)
  4. Drop rows with null pedestriancount
  5. Winsorise outliers at 99th percentile (event spikes)
  6. Join to pedestrian_sensors.csv for lat/lon
  7. GROUP BY sensor_id, day_of_week, hour:
     → avg_count, median_count, p25, p75, max_count
  8. Classify crowd_level: Low / Moderate / High based on percentiles
  9. Compute best_hour_flag: True if avg_count < overall p25 (quiet window)
  10. Export pedestrian_patterns.csv

This is the core training data for the crowd forecast ML model.
"""

from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

DAY_NAMES = {
    0: "Monday", 1: "Tuesday", 2: "Wednesday",
    3: "Thursday", 4: "Friday", 5: "Saturday", 6: "Sunday"
}


# ─── Load ─────────────────────────────────────────────────────────────────────

def load_counts() -> pd.DataFrame:
    path = RAW_DIR / "pedestrian_counts_2025.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")

    print("Loading pedestrian counts (112MB — may take a moment)...")
    df = pd.read_csv(path, sep=";", encoding="utf-8-sig", low_memory=False)
    df.columns = df.columns.str.strip()
    print(f"Loaded {len(df):,} rows")
    print(f"Columns: {df.columns.tolist()}")
    return df


def load_sensors() -> pd.DataFrame:
    path = PROCESSED_DIR / "pedestrian_sensors.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing: {path}. Run pedestrian_sensors_processing.py first."
        )
    return pd.read_csv(path)


# ─── Clean ────────────────────────────────────────────────────────────────────

def clean_counts(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Parse date
    df["sensing_date"] = pd.to_datetime(df["sensing_date"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["sensing_date"]).copy()
    print(f"Dropped {before - len(df)} rows with invalid dates")

    # Extract date features
    df["day_of_week"] = df["sensing_date"].dt.dayofweek  # 0=Monday
    df["day_name"] = df["day_of_week"].map(DAY_NAMES)
    df["month"] = df["sensing_date"].dt.month
    df["hour"] = df["hourday"].astype(int)

    # Clean count
    df["pedestriancount"] = pd.to_numeric(df["pedestriancount"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["pedestriancount"]).copy()
    print(f"Dropped {before - len(df)} rows with null pedestriancount")
    df["pedestriancount"] = df["pedestriancount"].astype(int)

    # Clean location_id
    df["location_id"] = pd.to_numeric(df["location_id"], errors="coerce")
    df = df.dropna(subset=["location_id"]).copy()
    df["location_id"] = df["location_id"].astype(int)

    print(f"\nClean rows: {len(df):,}")
    print(f"Date range: {df['sensing_date'].min()} → {df['sensing_date'].max()}")
    print(f"Unique sensors: {df['location_id'].nunique()}")
    print(f"Hour range: {df['hour'].min()} - {df['hour'].max()}")

    return df


# ─── Winsorise outliers ───────────────────────────────────────────────────────

def winsorise(df: pd.DataFrame, col: str, upper_pct: float = 99) -> pd.DataFrame:
    """
    Cap extreme values at the 99th percentile.
    Event spikes (e.g. NYE, Grand Prix) can be 10-20x normal.
    Winsorising prevents these from skewing our crowd baselines.
    """
    df = df.copy()
    upper = np.percentile(df[col].dropna(), upper_pct)
    before_max = df[col].max()
    df[col] = df[col].clip(upper=upper)
    print(f"Winsorised {col}: max {before_max} → {upper:.0f} (p{upper_pct})")
    return df


# ─── Aggregate to patterns ────────────────────────────────────────────────────

def aggregate_patterns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate raw counts to hourly patterns per sensor per day_of_week.
    This is the core ML training dataset.
    
    Output: one row per (sensor_id, day_of_week, hour)
    """
    print("\nAggregating to hourly patterns...")

    patterns = df.groupby(["location_id", "day_of_week", "hour"]).agg(
        avg_count=("pedestriancount", "mean"),
        median_count=("pedestriancount", "median"),
        p25_count=("pedestriancount", lambda x: np.percentile(x, 25)),
        p75_count=("pedestriancount", lambda x: np.percentile(x, 75)),
        max_count=("pedestriancount", "max"),
        sample_count=("pedestriancount", "count"),
    ).reset_index()

    patterns = patterns.rename(columns={"location_id": "sensor_id"})

    patterns["avg_count"] = patterns["avg_count"].round(1)
    patterns["median_count"] = patterns["median_count"].round(1)
    patterns["p25_count"] = patterns["p25_count"].round(1)
    patterns["p75_count"] = patterns["p75_count"].round(1)
    patterns["day_name"] = patterns["day_of_week"].map(DAY_NAMES)

    print(f"Aggregated to {len(patterns):,} pattern rows")
    print(f"Unique sensors: {patterns['sensor_id'].nunique()}")
    return patterns


# ─── Crowd level classification ───────────────────────────────────────────────

def classify_crowd_level(patterns: pd.DataFrame) -> pd.DataFrame:
    """
    Classify each (sensor, day, hour) as Low / Moderate / High crowd.
    
    Based on global percentiles across all sensors:
      Low:      avg_count <= global_p33
      Moderate: avg_count <= global_p66
      High:     avg_count >  global_p66
    
    This tells elderly users: "Fitzroy Gardens at 10am Tuesday is QUIET"
    """
    patterns = patterns.copy()

    global_p33 = np.percentile(patterns["avg_count"], 33)
    global_p66 = np.percentile(patterns["avg_count"], 66)

    print(f"\nCrowd thresholds: Low <= {global_p33:.0f}, Moderate <= {global_p66:.0f}, High > {global_p66:.0f}")

    def classify(count):
        if count <= global_p33:
            return "Low"
        elif count <= global_p66:
            return "Moderate"
        else:
            return "High"

    patterns["crowd_level"] = patterns["avg_count"].apply(classify)

    # Best hour flag: True if this hour is Low crowd for this sensor
    patterns["is_quiet_hour"] = patterns["crowd_level"] == "Low"

    print(f"Crowd level breakdown:\n{patterns['crowd_level'].value_counts()}")
    return patterns


# ─── Join sensor lat/lon ─────────────────────────────────────────────────────

def join_sensor_locations(patterns: pd.DataFrame, sensors: pd.DataFrame) -> pd.DataFrame:
    """Join sensor lat/lon and suburb info onto patterns."""
    sensors["sensor_id"] = sensors["sensor_id"].astype(int)
    patterns["sensor_id"] = patterns["sensor_id"].astype(int)

    patterns = patterns.merge(
        sensors[["sensor_id", "sensor_description", "lat", "lon",
                 "suburb_id", "suburb_name", "location_type"]],
        on="sensor_id",
        how="left"
    )

    missing = patterns["lat"].isna().sum()
    print(f"\nSensors not matched to locations: {missing} rows")
    return patterns


# ─── Compute best times summary ───────────────────────────────────────────────

def compute_best_times(patterns: pd.DataFrame) -> pd.DataFrame:
    """
    For each sensor, find the top 3 quietest hours per day.
    This powers the 7-day forecast feature.
    """
    best = (
        patterns[patterns["crowd_level"] == "Low"]
        .groupby(["sensor_id", "sensor_description", "day_of_week", "day_name"])
        .apply(lambda g: g.nsmallest(3, "avg_count")[["hour", "avg_count", "crowd_level"]])
        .reset_index(drop=False)
    )

    print(f"\nBest times computed: {len(best)} quiet windows")
    return best


# ─── Export ───────────────────────────────────────────────────────────────────

def export(patterns: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "pedestrian_patterns.csv"
    patterns.to_csv(out, index=False)
    print(f"\nSaved: {out}")
    print(f"Shape: {patterns.shape}")
    print("\nPreview (Bourke St, weekday mornings):")
    sample = patterns[
        (patterns["day_of_week"] < 5) &
        (patterns["hour"].between(9, 12))
    ].head(10)
    print(sample[["sensor_id", "sensor_description", "day_name",
                  "hour", "avg_count", "crowd_level"]].to_string())


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    counts = load_counts()
    sensors = load_sensors()

    counts = clean_counts(counts)
    counts = winsorise(counts, "pedestriancount", upper_pct=99)

    patterns = aggregate_patterns(counts)
    patterns = classify_crowd_level(patterns)
    patterns = join_sensor_locations(patterns, sensors)

    export(patterns)

    print("\nColumn summary:")
    print(patterns.dtypes)
    print("\nMissing values:")
    print(patterns.isna().sum())

    print("\nSample — Bourke St on a Friday:")
    sample = patterns[
        (patterns["sensor_description"].str.contains("Bourke", na=False)) &
        (patterns["day_of_week"] == 4)
    ].sort_values("hour")
    print(sample[["hour", "avg_count", "crowd_level"]].to_string())


if __name__ == "__main__":
    main()

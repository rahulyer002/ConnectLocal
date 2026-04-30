"""
microclimate_processing.py
---------------------------
Cleans the City of Melbourne microclimate sensor datasets.

Inputs:
  Data/raw/microclimate_sensor_locations.csv (16 rows)
  Data/raw/microclimate_readings.csv (56 rows — historical)

Outputs:
  Data/processed/microclimate_sensors.csv  — active sensor locations
  Data/processed/microclimate_readings.csv — cleaned historical readings

Processing steps:
  1. Sensor locations:
     - Strip BOM, clean column names
     - Filter: status = 'C' (current/active) only
     - Parse lat/lon
     - Map to nearest suburb
  2. Historical readings:
     - Strip BOM, clean column names
     - Parse Local_Time → date, hour
     - Pivot Type column → wide format (one col per measurement type)
     - Filter to useful sensor types for our use case:
       TPH.TEMP (temperature), TPH.RH (humidity),
       WS (wind speed), PM2.5 (air quality)
     - Join sensor location to get lat/lon
     - Export cleaned readings

Note: Only 6 active sensors, all in Melbourne CBD.
      Live readings come from microclimate-sensors-data API at runtime.
      This processed file is used for model training / pattern analysis only.
"""

from __future__ import annotations
from pathlib import Path
import math
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Sensor types we care about for the resonance engine
USEFUL_TYPES = {
    "TPH.TEMP": "temperature_c",
    "TPH.RH": "humidity_pct",
    "TPH.PRESSURE": "pressure_hpa",
    "WS": "wind_speed_kmh",
    "PM2.5": "pm25_ug_m3",
    "PM10": "pm10_ug_m3",
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

def load_sensor_locations() -> pd.DataFrame:
    path = RAW_DIR / "microclimate_sensor_locations.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    print(f"Loaded {len(df)} microclimate sensor locations")
    return df


def load_readings() -> pd.DataFrame:
    path = RAW_DIR / "microclimate_readings.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    df = pd.read_csv(path, encoding="utf-8-sig")
    df.columns = df.columns.str.strip()
    print(f"Loaded {len(df)} microclimate readings")
    print(f"Columns: {df.columns.tolist()}")
    return df


def load_suburb_reference() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_reference.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    return pd.read_csv(path)


# ─── Process sensor locations ────────────────────────────────────────────────

def clean_sensor_locations(df: pd.DataFrame, suburb_ref: pd.DataFrame) -> pd.DataFrame:
    # Parse coordinates
    df["lat"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["lon"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"]).copy()

    print(f"\nSite status breakdown:\n{df['site_status'].value_counts()}")

    # Keep all — both C (current) and R (retired) for historical analysis
    # Mark active separately
    df["is_active"] = df["site_status"] == "C"
    print(f"Active sensors (C): {df['is_active'].sum()}")
    print(f"Retired sensors (R): {(~df['is_active']).sum()}")

    # Map to suburbs
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

    result = df[[
        "site_id",
        "gatewayhub_id",
        "site_status",
        "is_active",
        "start_reading",
        "end_reading",
        "lat",
        "lon",
        "suburb_id",
        "suburb_name",
    ]].copy()

    return result


# ─── Process readings ────────────────────────────────────────────────────────

def clean_readings(df: pd.DataFrame, sensor_locations: pd.DataFrame) -> pd.DataFrame:
    """
    Readings are in long format: one row per (timestamp, sensor, type).
    We clean and keep only useful types.
    
    Columns: Local_Time, ID, Site_ID, Sensor_ID, Value, Type, Units, Gatewayhub_ID, Site_Status
    """
    df = df.copy()

    # Parse timestamp
    df["Local_Time"] = pd.to_datetime(df["Local_Time"], errors="coerce", utc=True)
    df = df.dropna(subset=["Local_Time"]).copy()

    df["date"] = df["Local_Time"].dt.date
    df["hour"] = df["Local_Time"].dt.hour
    df["day_of_week"] = df["Local_Time"].dt.dayofweek  # 0=Monday

    # Clean value
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

    # Filter to useful sensor types only
    print(f"\nSensor types in readings:\n{df['Type'].value_counts()}")
    df = df[df["Type"].isin(USEFUL_TYPES.keys())].copy()
    df["measurement"] = df["Type"].map(USEFUL_TYPES)

    # Join sensor location for lat/lon
    sensor_locations["site_id"] = sensor_locations["site_id"].astype(str)
    df["Site_ID"] = df["Site_ID"].astype(str)

    df = df.merge(
        sensor_locations[["site_id", "lat", "lon", "suburb_name"]],
        left_on="Site_ID",
        right_on="site_id",
        how="left"
    )

    result = df[[
        "Site_ID",
        "date",
        "hour",
        "day_of_week",
        "measurement",
        "Value",
        "lat",
        "lon",
        "suburb_name",
    ]].rename(columns={
        "Site_ID": "site_id",
        "Value": "value",
    })

    print(f"\nCleaned readings shape: {result.shape}")
    print(f"Measurement types:\n{result['measurement'].value_counts()}")
    return result


# ─── Safety thresholds ────────────────────────────────────────────────────────

def compute_safety_baselines(readings: pd.DataFrame) -> pd.DataFrame:
    """
    Compute baseline statistics per measurement type.
    Used by the resonance score engine to classify current conditions.
    
    For elderly safety:
      temperature > 35°C → danger
      wind_speed > 40 km/h → uncomfortable
      pm25 > 25 ug/m³ → poor air quality
      humidity > 80% → uncomfortable
    """
    stats = readings.groupby("measurement")["value"].agg(
        ["mean", "std", "min", "max", "median"]
    ).round(3)

    print(f"\nBaseline stats per measurement:\n{stats}")
    return stats


# ─── Export ───────────────────────────────────────────────────────────────────

def export_sensors(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "microclimate_sensors.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved microclimate sensors: {out}")
    print(f"Shape: {df.shape}")
    print("\nPreview:")
    print(df)


def export_readings(df: pd.DataFrame) -> None:
    out = PROCESSED_DIR / "microclimate_readings_clean.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved microclimate readings: {out}")
    print(f"Shape: {df.shape}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    suburb_ref = load_suburb_reference()
    raw_locations = load_sensor_locations()
    raw_readings = load_readings()

    # Process sensor locations
    sensor_locations = clean_sensor_locations(raw_locations, suburb_ref)
    export_sensors(sensor_locations)

    # Process readings
    readings = clean_readings(raw_readings, sensor_locations)
    compute_safety_baselines(readings)
    export_readings(readings)

    print("\nNote: Only 6 active sensors, all in Melbourne CBD.")
    print("Live readings for Epic 4 come from microclimate-sensors-data API at runtime.")


if __name__ == "__main__":
    main()

from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def process_landmarks() -> pd.DataFrame:
    path = RAW_DIR / "landmarks.csv"
    df = pd.read_csv(path)

    coords = df["Co-ordinates"].str.split(",", expand=True)
    df["lat"] = coords[0].str.strip().astype(float)
    df["lng"] = coords[1].str.strip().astype(float)

    df = df.rename(columns={
        "Feature Name": "name",
        "Theme": "theme",
        "Sub Theme": "sub_theme"
    })

    df["landmark_id"] = range(1, len(df) + 1)

    df["is_welcoming_space"] = None
    df["clue_small_area"] = None 

    df = df[[
        "landmark_id",
        "name",
        "theme",
        "sub_theme",
        "lat",
        "lng",
        "is_welcoming_space",
        "clue_small_area"
    ]]

    return df


def load_suburb_reference() -> pd.DataFrame:
    path = PROCESSED_DIR / "suburb_reference.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing suburb reference file: {path}. "
            "Create suburb_reference.csv with suburb_id, suburb_name, centroid_lat, centroid_lng."
        )

    suburb_ref = pd.read_csv(path)

    required_cols = ["suburb_id", "suburb_name", "centroid_lat", "centroid_lng"]
    missing = [col for col in required_cols if col not in suburb_ref.columns]
    if missing:
        raise ValueError(f"suburb_reference.csv is missing columns: {missing}")

    return suburb_ref


def calculate_squared_distance(
    lat1: pd.Series, lng1: pd.Series, lat2: float, lng2: float
) -> pd.Series:
    return (lat1 - lat2) ** 2 + (lng1 - lng2) ** 2


def map_landmarks_to_suburbs(
    landmarks: pd.DataFrame, suburb_ref: pd.DataFrame
) -> pd.DataFrame:
    landmarks = landmarks.copy()

    suburb_ids = []
    suburb_names = []

    for _, landmark in landmarks.iterrows():
        distances = calculate_squared_distance(
            suburb_ref["centroid_lat"],
            suburb_ref["centroid_lng"],
            landmark["lat"],
            landmark["lng"],
        )

        nearest_idx = distances.idxmin()
        suburb_ids.append(suburb_ref.loc[nearest_idx, "suburb_id"])
        suburb_names.append(suburb_ref.loc[nearest_idx, "suburb_name"])

    landmarks["suburb_id"] = suburb_ids
    landmarks["suburb_name"] = suburb_names

    return landmarks



def main():
    landmarks = process_landmarks()

    suburb_ref = load_suburb_reference()
    landmarks = map_landmarks_to_suburbs(landmarks, suburb_ref)

    output_path = PROCESSED_DIR / "landmarks.csv"
    landmarks.to_csv(output_path, index=False)

    print("Saved landmarks:")
    print(landmarks.head())



if __name__ == "__main__":
    main()
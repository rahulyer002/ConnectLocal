from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "processed"
RAW_DIR = BASE_DIR/ "raw"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def load_landmarks() -> pd.DataFrame:
    path = PROCESSED_DIR / "landmarks.csv"

    if not path.exists():
        raise FileNotFoundError(
            f"Missing landmarks file: {path}. Run landmarks_processing.py first."
        )

    return pd.read_csv(path)

def load_public_toilets() -> pd.DataFrame:
    path = BASE_DIR/ "raw" / "public_toilets.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"Missing toilets file: {path}"
        )
    return pd.read_csv(path)


def filter_open_spaces(landmarks: pd.DataFrame) -> pd.DataFrame:
    df = landmarks.copy()

    # Define keywords for open spaces
    keywords = [
        "Park",
        "Garden",
        "Reserve",
        "Recreation",
        "Playground",
        "Square"
    ]

    # Filter based on theme/sub_theme
    mask = (
        df["theme"].str.contains("|".join(keywords), case=False, na=False) |
        df["sub_theme"].str.contains("|".join(keywords), case=False, na=False)
    )

    exclude_keywords = [
    "School",
    "Club",
    "Office",
    "Carpark"
    ]

    mask_exclude = ~(
        df["sub_theme"].str.contains("|".join(exclude_keywords), case=False, na=False)
    )

    df = df[mask & mask_exclude]

    return df


def build_open_space_table(df: pd.DataFrame) -> pd.DataFrame:
    open_space = df.copy()

    # Generate ID
    open_space["space_id"] = range(1, len(open_space) + 1)

    # Rename fields to match ERD
    open_space = open_space.rename(columns={
        "name": "space_name",
        "theme": "space_type"
    })

    # Add placeholders for future features
    open_space["category"] = None
    open_space["area_ha"] = None
    open_space["public_access"] = True
    open_space["managed_by"] = None
    open_space["walkability_score"] = None
    open_space["public_access"] = True
    open_space["managed_by"] = "Local Council"
    open_space["area_ha"] = None
    open_space["space_type"] = open_space["space_type"].fillna("General Open Space")
    open_space["walkability_score"] = None  


    # Select final columns (aligned with ERD)
    open_space = open_space[[
        "space_id",
        "suburb_id",
        "space_name",
        "space_type",
        "category",
        "area_ha",
        "public_access",
        "managed_by",
        "lat",
        "lng",
        "walkability_score"
    ]]

    return open_space

def add_toilet_proximity(
    open_space: pd.DataFrame,
    toilets: pd.DataFrame,
    threshold: float = 0.005
) -> pd.DataFrame:
    """
    Adds has_toilet_nearby flag based on proximity.
    threshold ~0.005 = a few hundred metres
    """
    open_space = open_space.copy()
    toilets = toilets.copy()

    # Clean coordinates
    toilets["lat"] = pd.to_numeric(toilets["lat"], errors="coerce")
    toilets["lon"] = pd.to_numeric(toilets["lon"], errors="coerce")
    toilets = toilets.dropna(subset=["lat", "lon"])

    has_toilet = []

    for _, row in open_space.iterrows():
        distances = (
            (toilets["lat"] - row["lat"]) ** 2 +
            (toilets["lon"] - row["lng"]) ** 2
        ) ** 0.5

        has_toilet.append((distances <= threshold).any())

    open_space["has_toilet_nearby"] = has_toilet

    return open_space


def export_open_space(open_space: pd.DataFrame) -> None:
    output_path = PROCESSED_DIR / "open_space.csv"
    open_space.to_csv(output_path, index=False)

    print(f"\nSaved open_space file to: {output_path}")
    print("\nPreview:")
    print(open_space.head())
    print("\nShape:", open_space.shape)

def derive_category(row):
    name = str(row["space_name"]).lower()

    if any(x in name for x in ["park", "garden", "reserve", "domain"]):
        return "Green Space"
    elif any(x in name for x in ["square", "plaza"]):
        return "Urban Space"
    elif any(x in name for x in ["club", "leisure", "recreation"]):
        return "Recreation"
    else:
        return "Other"


def compute_pedestrian_density(ped_counts: pd.DataFrame) -> pd.DataFrame:
    # Average traffic per location
    density = (
        ped_counts.groupby("Location")["Total_of_Directions"]
        .mean()
        .reset_index()
        .rename(columns={"Total_of_Directions": "avg_pedestrian"})
    )

    return density

def add_walkability_score(open_space: pd.DataFrame, ped_counts: pd.DataFrame) -> pd.DataFrame:
    import math

    open_space = open_space.copy()

    # Parse pedestrian locations into lat/lng
    ped_counts[["lat", "lng"]] = ped_counts["Location"].str.split(",", expand=True).astype(float)

    # Aggregate density
    density = compute_pedestrian_density(ped_counts)

    ped_counts = ped_counts.merge(density, on="Location", how="left")

    ped_points = ped_counts[["lat", "lng", "avg_pedestrian"]].dropna().drop_duplicates()

    scores = []

    for _, space in open_space.iterrows():
        space_lat = space["lat"]
        space_lng = space["lng"]

        nearby_values = []

        for _, ped in ped_points.iterrows():
            dist = math.sqrt(
                (space_lat - ped["lat"])**2 +
                (space_lng - ped["lng"])**2
            )

            if dist <= 0.01:  # ~1km radius
                nearby_values.append(ped["avg_pedestrian"])

        if len(nearby_values) == 0:
            scores.append(None)
        else:
            avg_density = sum(nearby_values) / len(nearby_values)

            # Convert to score (lower crowd = higher score)
            score = 1 / (1 + avg_density)
            scores.append(score)

    open_space["walkability_score"] = scores

    return open_space


def main():
    landmarks = load_landmarks()
    toilets = load_public_toilets()

    print("\nPublic toilets columns:")
    print(toilets.columns.tolist())

    open_space = filter_open_spaces(landmarks)
    open_space = build_open_space_table(open_space)
    open_space = add_toilet_proximity(open_space, toilets, threshold=0.005)


    ped_counts = pd.read_csv(RAW_DIR / "pedestrian_counts.csv")
    ped_network = pd.read_csv(RAW_DIR / "pedestrian_network.csv")

    # print("\nPedestrian counts columns:")
    # print(ped_counts.columns.tolist())

    # print("\nPedestrian network columns:")
    # print(ped_network.columns.tolist())

    open_space = add_walkability_score(open_space, ped_counts)

    open_space["category"] = open_space.apply(derive_category, axis=1)


    export_open_space(open_space)
    # print("\nToilet coverage summary:")
    # print(open_space["has_toilet_nearby"].value_counts())



    print("\nWalkability summary:")
    print(open_space["walkability_score"].describe())

    print("\nMissing walkability:")
    print(open_space["walkability_score"].isna().sum())

    print("\nCategory breakdown:")
    print(open_space["category"].value_counts())


if __name__ == "__main__":
    main()


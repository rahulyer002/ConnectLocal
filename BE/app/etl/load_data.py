"""
ETL script to load processed CSVs into RDS.
Run once: python -m app.etl.load_data
"""
import pandas as pd
from pathlib import Path
from app.database import engine, Base
from app.models import Suburb, Landmark, OpenSpace, Category
from sqlalchemy.orm import Session

DATA_DIR = Path(__file__).resolve().parents[3] / "Data" / "processed"


def load_suburbs():
    print("Loading suburbs...")
    df = pd.read_csv(DATA_DIR / "suburb_profile.csv")
    df = df.rename(columns={"centroid_lng": "centroid_lng"})
    df["landmark_count"] = df["landmark_count"].fillna(0).astype(int)

    with Session(engine) as session:
        session.query(Suburb).delete()
        for _, row in df.iterrows():
            session.add(Suburb(
                suburb_id=int(row["suburb_id"]),
                suburb_name=row["suburb_name"],
                centroid_lat=float(row["centroid_lat"]),
                centroid_lng=float(row["centroid_lng"]),
                population_total=int(row["population_total"]) if pd.notna(row["population_total"]) else None,
                population_65_74=int(row["population_65_74"]) if pd.notna(row["population_65_74"]) else None,
                population_75_84=int(row["population_75_84"]) if pd.notna(row["population_75_84"]) else None,
                population_85_plus=int(row["population_85_plus"]) if pd.notna(row["population_85_plus"]) else None,
                need_assistance=int(row["need_assistance"]) if pd.notna(row["need_assistance"]) else None,
                landmark_count=int(row["landmark_count"]),
            ))
        session.commit()
    print(f"  Loaded {len(df)} suburbs")


def load_landmarks():
    print("Loading landmarks...")
    df = pd.read_csv(DATA_DIR / "landmarks.csv")

    with Session(engine) as session:
        session.query(Landmark).delete()
        for _, row in df.iterrows():
            session.add(Landmark(
                landmark_id=int(row["landmark_id"]),
                suburb_id=int(row["suburb_id"]) if pd.notna(row["suburb_id"]) else None,
                suburb_name=row["suburb_name"] if pd.notna(row.get("suburb_name")) else None,
                name=row["name"],
                theme=row["theme"] if pd.notna(row["theme"]) else None,
                sub_theme=row["sub_theme"] if pd.notna(row["sub_theme"]) else None,
                lat=float(row["lat"]),
                lng=float(row["lng"]),
                is_welcoming_space=bool(row["is_welcoming_space"]) if pd.notna(row.get("is_welcoming_space")) else None,
                clue_small_area=row["clue_small_area"] if pd.notna(row.get("clue_small_area")) else None,
            ))
        session.commit()
    print(f"  Loaded {len(df)} landmarks")


def load_open_spaces():
    print("Loading open spaces...")
    df = pd.read_csv(DATA_DIR / "open_space.csv")

    def to_bool(val):
        if pd.isna(val):
            return None
        if isinstance(val, bool):
            return val
        return str(val).strip().lower() in ("true", "1", "yes")

    with Session(engine) as session:
        session.query(OpenSpace).delete()
        for _, row in df.iterrows():
            session.add(OpenSpace(
                space_id=int(row["space_id"]),
                suburb_id=int(row["suburb_id"]) if pd.notna(row["suburb_id"]) else None,
                space_name=row["space_name"],
                space_type=row["space_type"] if pd.notna(row["space_type"]) else None,
                category=row["category"] if pd.notna(row["category"]) else None,
                area_ha=float(row["area_ha"]) if pd.notna(row["area_ha"]) else None,
                public_access=to_bool(row["public_access"]),
                managed_by=row["managed_by"] if pd.notna(row["managed_by"]) else None,
                lat=float(row["lat"]),
                lng=float(row["lng"]),
                walkability_score=float(row["walkability_score"]) if pd.notna(row["walkability_score"]) else None,
                has_toilet_nearby=to_bool(row["has_toilet_nearby"]),
                comfort_score=float(row["comfort_score"]) if pd.notna(row["comfort_score"]) else None,
            ))
        session.commit()
    print(f"  Loaded {len(df)} open spaces")


def load_categories():
    print("Loading categories...")
    df = pd.read_csv(DATA_DIR / "category.csv")

    def to_bool(val):
        if pd.isna(val):
            return False
        return str(val).strip().lower() in ("true", "1", "yes")

    with Session(engine) as session:
        session.query(Category).delete()
        for _, row in df.iterrows():
            session.add(Category(
                category_id=int(row["category_id"]),
                parent_id=float(row["parent_id"]) if pd.notna(row["parent_id"]) else None,
                name=row["name"],
                senior_tag=to_bool(row["senior_tag"]),
            ))
        session.commit()
    print(f"  Loaded {len(df)} categories")


def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    load_suburbs()
    load_landmarks()
    load_open_spaces()
    load_categories()

    print("\nAll data loaded successfully!")


if __name__ == "__main__":
    main()
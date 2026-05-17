"""
ETL script — loads all processed CSVs into RDS.
Run: python -m app.etl.load_data
"""
import pandas as pd
from pathlib import Path
from app.database import engine, Base
from app.models.psychological_distress import PsychologicalDistress
from app.models import (
    Suburb, Landmark, OpenSpace, Category,
    PublicToilet, Tree, PedestrianSensor, PedestrianPattern,
    MicroClimateSensor, GtfsStop, GtfsRoute, GtfsPattern, GtfsPathway,
    OsmBench, OsmAccessibleToilet, OsmWheelchairPlace,
)
from sqlalchemy.orm import Session
from sqlalchemy import text

DATA_DIR = Path(__file__).resolve().parents[3] / "Data" / "processed"
BATCH = 1000


def to_bool(val) -> bool | None:
    if pd.isna(val):
        return None
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("true", "1", "yes")


def batch_insert(session: Session, model, records: list) -> None:
    for i in range(0, len(records), BATCH):
        session.bulk_insert_mappings(model, records[i:i+BATCH])
        session.commit()
        if i % 10000 == 0 and i > 0:
            print(f"    Inserted {i:,} rows...")


# ─── Existing tables ──────────────────────────────────────────────────────────

def load_suburbs():
    print("Loading suburbs...")
    df = pd.read_csv(DATA_DIR / "suburb_profile.csv")
    df["landmark_count"] = df["landmark_count"].fillna(0).astype(int)
    with Session(engine) as session:
        session.execute(text("DELETE FROM suburb"))
        session.commit()
        records = [
            dict(
                suburb_id=int(r.suburb_id),
                suburb_name=r.suburb_name,
                centroid_lat=float(r.centroid_lat),
                centroid_lng=float(r.centroid_lng),
                population_total=int(r.population_total) if pd.notna(r.population_total) else None,
                population_65_74=int(r.population_65_74) if pd.notna(r.population_65_74) else None,
                population_75_84=int(r.population_75_84) if pd.notna(r.population_75_84) else None,
                population_85_plus=int(r.population_85_plus) if pd.notna(r.population_85_plus) else None,
                need_assistance=int(r.need_assistance) if pd.notna(r.need_assistance) else None,
                landmark_count=int(r.landmark_count),
            )
            for r in df.itertuples()
        ]
        batch_insert(session, Suburb, records)
    print(f"  Loaded {len(df)} suburbs")


def load_landmarks():
    print("Loading landmarks...")
    df = pd.read_csv(DATA_DIR / "landmarks.csv")
    with Session(engine) as session:
        session.execute(text("DELETE FROM landmark"))
        session.commit()
        records = [
            dict(
                landmark_id=int(r.landmark_id),
                suburb_id=int(r.suburb_id) if pd.notna(r.suburb_id) else None,
                suburb_name=r.suburb_name if pd.notna(r.suburb_name) else None,
                name=r.name,
                theme=r.theme if pd.notna(r.theme) else None,
                sub_theme=r.sub_theme if pd.notna(r.sub_theme) else None,
                lat=float(r.lat),
                lng=float(r.lng),
                is_welcoming_space=to_bool(r.is_welcoming_space),
                clue_small_area=r.clue_small_area if pd.notna(r.clue_small_area) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, Landmark, records)
    print(f"  Loaded {len(df)} landmarks")


def load_open_spaces():
    print("Loading open spaces...")
    df = pd.read_csv(DATA_DIR / "open_space.csv")
    with Session(engine) as session:
        session.execute(text("DELETE FROM open_space"))
        session.commit()
        records = [
            dict(
                space_id=int(r.space_id),
                suburb_id=int(r.suburb_id) if pd.notna(r.suburb_id) else None,
                space_name=r.space_name,
                space_type=r.space_type if pd.notna(r.space_type) else None,
                category=r.category if pd.notna(r.category) else None,
                area_ha=float(r.area_ha) if pd.notna(r.area_ha) else None,
                public_access=to_bool(r.public_access),
                managed_by=r.managed_by if pd.notna(r.managed_by) else None,
                lat=float(r.lat),
                lng=float(r.lng),
                walkability_score=float(r.walkability_score) if pd.notna(r.walkability_score) else None,
                has_toilet_nearby=to_bool(r.has_toilet_nearby),
                comfort_score=float(r.comfort_score) if pd.notna(r.comfort_score) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, OpenSpace, records)
    print(f"  Loaded {len(df)} open spaces")



def load_categories():
    print("Loading categories...")
    df = pd.read_csv(DATA_DIR / "category.csv")
    with Session(engine) as session:
        session.execute(text("DELETE FROM category"))
        session.commit()
        records = [
            dict(
                category_id=int(r.category_id),
                parent_id=float(r.parent_id) if pd.notna(r.parent_id) else None,
                name=r.name,
                senior_tag=to_bool(r.senior_tag),
            )
            for r in df.itertuples()
        ]
        batch_insert(session, Category, records)
    print(f"  Loaded {len(df)} categories")


# ─── New tables ───────────────────────────────────────────────────────────────

def load_public_toilets():
    print("Loading public toilets...")
    df = pd.read_csv(DATA_DIR / "public_toilets.csv")
    df = df.drop_duplicates(subset=["toilet_id"], keep="first")
    with Session(engine) as session:
        session.execute(text("DELETE FROM public_toilet"))
        session.commit()
        records = [
            dict(
                toilet_id=int(r.toilet_id),
                suburb_id=int(r.suburb_id) if pd.notna(r.suburb_id) else None,
                suburb_name=r.suburb_name if pd.notna(r.suburb_name) else None,
                name=r.name if pd.notna(r.name) else None,
                lat=float(r.lat),
                lon=float(r.lon),
                has_female=to_bool(r.has_female),
                has_male=to_bool(r.has_male),
                has_wheelchair=to_bool(r.has_wheelchair),
                has_baby_facility=to_bool(r.has_baby_facility),
                operator=r.operator if pd.notna(r.operator) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, PublicToilet, records)
    print(f"  Loaded {len(df)} toilets")


def load_pedestrian_sensors():
    print("Loading pedestrian sensors...")
    df = pd.read_csv(DATA_DIR / "pedestrian_sensors.csv")
    before = len(df)
    df = df.drop_duplicates(subset=["sensor_id"], keep="first")
    print(f"  Deduplicated: {before} → {len(df)} sensors")
    with Session(engine) as session:
        session.execute(text("DELETE FROM pedestrian_sensor"))
        session.commit()
        records = [
            dict(
                sensor_id=int(r.sensor_id),
                sensor_name=r.sensor_name if pd.notna(r.sensor_name) else None,
                sensor_description=r.sensor_description if pd.notna(r.sensor_description) else None,
                location_type=r.location_type if pd.notna(r.location_type) else None,
                status=r.status if pd.notna(r.status) else None,
                lat=float(r.lat),
                lon=float(r.lon),
                direction_1=r.direction_1 if pd.notna(r.direction_1) else None,
                direction_2=r.direction_2 if pd.notna(r.direction_2) else None,
                suburb_id=int(r.suburb_id) if pd.notna(r.suburb_id) else None,
                suburb_name=r.suburb_name if pd.notna(r.suburb_name) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, PedestrianSensor, records)
    print(f"  Loaded {len(df)} sensors")


def load_microclimate_sensors():
    print("Loading microclimate sensors...")
    df = pd.read_csv(DATA_DIR / "microclimate_sensors.csv")
    df = df.drop_duplicates(subset=["site_id"], keep="first")
    with Session(engine) as session:
        session.execute(text("DELETE FROM microclimate_sensor"))
        session.commit()
        records = [
            dict(
                site_id=int(r.site_id),
                gatewayhub_id=r.gatewayhub_id if pd.notna(r.gatewayhub_id) else None,
                site_status=r.site_status if pd.notna(r.site_status) else None,
                is_active=to_bool(r.is_active),
                start_reading=r.start_reading if pd.notna(r.start_reading) else None,
                end_reading=r.end_reading if pd.notna(r.end_reading) else None,
                lat=float(r.lat),
                lon=float(r.lon),
                suburb_id=int(r.suburb_id) if pd.notna(r.suburb_id) else None,
                suburb_name=r.suburb_name if pd.notna(r.suburb_name) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, MicroClimateSensor, records)
    print(f"  Loaded {len(df)} microclimate sensors")


def load_pedestrian_patterns():
    print("Loading pedestrian patterns (18K rows)...")
    df = pd.read_csv(DATA_DIR / "pedestrian_patterns.csv")
    df = df.drop_duplicates(subset=["sensor_id", "day_of_week", "hour"], keep="first")
    with Session(engine) as session:
        session.execute(text("DELETE FROM pedestrian_pattern"))
        session.commit()
        records = [
            dict(
                sensor_id=int(r.sensor_id),
                day_of_week=int(r.day_of_week),
                hour=int(r.hour),
                avg_count=float(r.avg_count),
                median_count=float(r.median_count),
                p25_count=float(r.p25_count),
                p75_count=float(r.p75_count),
                max_count=int(r.max_count),
                sample_count=int(r.sample_count),
                day_name=r.day_name if pd.notna(r.day_name) else None,
                crowd_level=r.crowd_level if pd.notna(r.crowd_level) else None,
                is_quiet_hour=to_bool(r.is_quiet_hour),
                sensor_description=r.sensor_description if pd.notna(r.sensor_description) else None,
                lat=float(r.lat) if pd.notna(r.lat) else None,
                lon=float(r.lon) if pd.notna(r.lon) else None,
                suburb_id=int(r.suburb_id) if pd.notna(r.suburb_id) else None,
                suburb_name=r.suburb_name if pd.notna(r.suburb_name) else None,
                location_type=r.location_type if pd.notna(r.location_type) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, PedestrianPattern, records)
    print(f"  Loaded {len(df)} patterns")


def load_gtfs_stops():
    print("Loading GTFS stops (22K rows)...")
    df = pd.read_csv(DATA_DIR / "gtfs_stops.csv", dtype=str)
    df = df.drop_duplicates(subset=["stop_id"], keep="first")
    with Session(engine) as session:
        session.execute(text("DELETE FROM gtfs_stop"))
        session.commit()
        records = [
            dict(
                stop_id=str(r.stop_id),
                stop_name=r.stop_name if pd.notna(r.stop_name) else None,
                lat=float(r.lat) if pd.notna(r.lat) else None,
                lon=float(r.lon) if pd.notna(r.lon) else None,
                mode=r.mode if pd.notna(r.mode) else None,
                location_type=r.location_type if pd.notna(r.location_type) else None,
                parent_station=r.parent_station if pd.notna(r.parent_station) else None,
                wheelchair_boarding=r.wheelchair_boarding if pd.notna(r.wheelchair_boarding) else None,
                is_wheelchair_accessible=r.is_wheelchair_accessible == "True",
                is_wheelchair_inaccessible=r.is_wheelchair_inaccessible == "True",
                routes_served=r.routes_served if pd.notna(r.routes_served) else None,
                route_count=int(r.route_count) if pd.notna(r.route_count) else 0,
                suburb_id=int(float(r.suburb_id)) if pd.notna(r.suburb_id) else None,
                suburb_name=r.suburb_name if pd.notna(r.suburb_name) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, GtfsStop, records)
    print(f"  Loaded {len(df)} stops")


def load_gtfs_routes():
    print("Loading GTFS routes...")
    df = pd.read_csv(DATA_DIR / "gtfs_routes.csv", dtype=str)
    df = df.drop_duplicates(subset=["route_id"], keep="first")
    with Session(engine) as session:
        session.execute(text("DELETE FROM gtfs_route"))
        session.commit()
        records = [
            dict(
                route_id=str(r.route_id),
                agency_id=r.agency_id if pd.notna(r.agency_id) else None,
                route_short_name=r.route_short_name if pd.notna(r.route_short_name) else None,
                route_long_name=r.route_long_name if pd.notna(r.route_long_name) else None,
                route_type=r.route_type if pd.notna(r.route_type) else None,
                route_color=r.route_color if pd.notna(r.route_color) else None,
                route_text_color=r.route_text_color if pd.notna(r.route_text_color) else None,
                mode=r.mode if pd.notna(r.mode) else None,
                mode_label=r.mode_label if pd.notna(r.mode_label) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, GtfsRoute, records)
    print(f"  Loaded {len(df)} routes")


def load_gtfs_patterns():
    print("Loading GTFS patterns (417K rows — batched)...")
    df = pd.read_csv(DATA_DIR / "gtfs_patterns.csv", dtype=str)
    df["departure_count"] = pd.to_numeric(df["departure_count"], errors="coerce").fillna(0)
    df["avg_departures_per_hour"] = pd.to_numeric(df["avg_departures_per_hour"], errors="coerce").fillna(0)
    df["hour"] = pd.to_numeric(df["hour"], errors="coerce").fillna(0)
    with Session(engine) as session:
        session.execute(text("DELETE FROM gtfs_pattern"))
        session.commit()
        records = [
            dict(
                stop_id=str(r.stop_id),
                hour=int(r.hour),
                departure_count=int(r.departure_count),
                mode=r.mode if pd.notna(r.mode) else None,
                avg_departures_per_hour=float(r.avg_departures_per_hour),
            )
            for r in df.itertuples()
        ]
        batch_insert(session, GtfsPattern, records)
    print(f"  Loaded {len(df)} patterns")


def load_gtfs_pathways():
    print("Loading GTFS pathways...")
    df = pd.read_csv(DATA_DIR / "gtfs_pathways.csv", dtype=str)
    df = df.drop_duplicates(subset=["pathway_id"], keep="first")
    with Session(engine) as session:
        session.execute(text("DELETE FROM gtfs_pathway"))
        session.commit()
        records = [
            dict(
                pathway_id=str(r.pathway_id),
                from_stop_id=r.from_stop_id if pd.notna(r.from_stop_id) else None,
                to_stop_id=r.to_stop_id if pd.notna(r.to_stop_id) else None,
                pathway_mode=r.pathway_mode if pd.notna(r.pathway_mode) else None,
                pathway_mode_label=r.pathway_mode_label if pd.notna(r.pathway_mode_label) else None,
                has_elevator=r.has_elevator == "True",
                has_stairs=r.has_stairs == "True",
                is_bidirectional=r.is_bidirectional if pd.notna(r.is_bidirectional) else None,
                traversal_time=float(r.traversal_time) if pd.notna(r.traversal_time) else None,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, GtfsPathway, records)
    print(f"  Loaded {len(df)} pathways")



def load_trees():
    print("Loading trees (82K rows — may take a moment)...")
    df = pd.read_csv(DATA_DIR / "trees.csv")
    df = df.drop_duplicates(subset=["tree_id"], keep="first")
    # NOTE: trees.csv ships with every row's suburb_id set to the catch-all
    # 297979799 (same NaN-argmin bug upstream). Recompute from lat/lon using
    # the cleaned suburb reference so trees actually land on real suburbs.
    suburbs = _load_suburb_reference()
    with Session(engine) as session:
        session.execute(text("DELETE FROM tree"))
        session.commit()
        records = []
        for r in df.itertuples():
            if pd.isna(r.lat) or pd.isna(r.lon):
                continue
            sub_id, sub_name = _nearest_suburb(float(r.lat), float(r.lon), suburbs)
            records.append(dict(
                tree_id=int(r.tree_id),
                common_name=r.common_name if pd.notna(r.common_name) else None,
                genus=r.genus if pd.notna(r.genus) else None,
                dbh_cm=float(r.dbh_cm) if pd.notna(r.dbh_cm) else None,
                useful_life_years=float(r.useful_life_years) if pd.notna(r.useful_life_years) else None,
                useful_life_label=r.useful_life_label if pd.notna(r.useful_life_label) else None,
                age_description=r.age_description if pd.notna(r.age_description) else None,
                located_in=r.located_in if pd.notna(r.located_in) else None,
                precinct=r.precinct if pd.notna(r.precinct) else None,
                lat=float(r.lat),
                lon=float(r.lon),
                shade_score=float(r.shade_score) if pd.notna(r.shade_score) else None,
                suburb_id=sub_id,
            ))
        batch_insert(session, Tree, records)
    print(f"  Loaded {len(records)} trees")


def load_psychological_distress():
    print("Loading psychological distress data...")
    df = pd.read_csv(DATA_DIR / "psychological_distress.csv")
    with Session(engine) as session:
        session.execute(text("DELETE FROM psychological_distress"))
        session.commit()
        records = [
            dict(
                age_group=r.age_group,
                psychological_distress_percent=float(r.psychological_distress_percent),
                year=r.year,
                source=r.source,
            )
            for r in df.itertuples()
        ]
        batch_insert(session, PsychologicalDistress, records)
    print(f"  Loaded {len(df)} records")
# ─── NEW datasets — OSM accessibility + shade merge ──────────────────────────

# Victoria bbox — strips international noise (~280 rows had lat 28°/lon -80°)
VIC_BBOX = (-39.0, -34.0, 140.5, 150.0)  # lat_min, lat_max, lon_min, lon_max
OSM_DIR = DATA_DIR / "osm_accessibility"


def _filter_to_vic(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)
    df = df[
        (df["latitude"].between(VIC_BBOX[0], VIC_BBOX[1]))
        & (df["longitude"].between(VIC_BBOX[2], VIC_BBOX[3]))
    ].copy()
    print(f"  Filtered to Victoria bbox: {before:,} → {len(df):,}")
    return df


def _nearest_suburb(lat: float, lon: float, suburb_df: pd.DataFrame) -> tuple[int, str]:
    """
    Spatial join: pick nearest suburb by centroid using squared degree distance
    (cheap and accurate enough at Melbourne scale).
    """
    dlat = suburb_df["centroid_lat"].values - lat
    dlng = suburb_df["centroid_lng"].values - lon
    dist2 = dlat * dlat + dlng * dlng
    idx = int(dist2.argmin())
    return (
        int(suburb_df.iloc[idx]["suburb_id"]),
        str(suburb_df.iloc[idx]["suburb_name"]),
    )


def _classify_amenity(raw) -> str:
    """Bucket the raw OSM amenity tag into elderly-relevant categories."""
    if raw is None or pd.isna(raw):
        return "other"
    v = str(raw).lower()
    if v in ("pharmacy", "doctors", "dentist", "clinic", "hospital", "veterinary"):
        return "healthcare"
    if v in ("library", "post_office", "bank", "atm", "place_of_worship",
             "community_centre", "townhall"):
        return "essentials"
    if v in ("restaurant", "cafe", "fast_food", "bar", "pub", "ice_cream",
             "food_court", "biergarten"):
        return "social"
    if v in ("social_facility", "shelter"):
        return "aged_care_social"
    if v in ("bus_station", "ferry_terminal", "taxi"):
        return "transit"
    return "other"


def _load_suburb_reference() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "suburb_profile.csv")[
        ["suburb_id", "suburb_name", "centroid_lat", "centroid_lng"]
    ]
    return df.dropna(subset=["centroid_lat", "centroid_lng"]).reset_index(drop=True)


def load_osm_benches():
    print("Loading OSM benches...")
    df = pd.read_csv(OSM_DIR / "osm_benches_clean.csv")
    df = _filter_to_vic(df).drop_duplicates(subset=["osm_id"])
    suburbs = _load_suburb_reference()

    with Session(engine) as session:
        session.execute(text("DELETE FROM osm_bench"))
        session.commit()
        records = []
        for r in df.itertuples():
            sub_id, sub_name = _nearest_suburb(r.latitude, r.longitude, suburbs)
            records.append(dict(
                osm_id=str(r.osm_id),
                name=str(r.name) if pd.notna(r.name) else "Bench",
                lat=float(r.latitude),
                lon=float(r.longitude),
                suburb_id=sub_id,
                suburb_name=sub_name,
            ))
        batch_insert(session, OsmBench, records)
    print(f"  Loaded {len(records):,} benches")


def load_suburb_inference():
    """Compute and persist precomputed inference rows for every suburb.

    Idempotent — truncates the table before insert. Must run AFTER all the
    underlying tables (osm_bench, tree, gtfs_stop, landmark, open_space) have
    been populated, otherwise scores will be zero.
    """
    print("Computing suburb inference (scores, personas, peers)...")
    from app.services import inference_service
    from app.models.suburb_inference import SuburbInference

    with Session(engine) as session:
        rows = inference_service.compute_all(session)
        if not rows:
            print("  No suburbs found — skipping.")
            return
        session.execute(text("DELETE FROM suburb_inference"))
        session.commit()
        batch_insert(session, SuburbInference, rows)
    print(f"  Computed {len(rows)} suburb inference rows.")

def load_osm_accessible_toilets():
    print("Loading OSM accessible toilets...")
    df = pd.read_csv(OSM_DIR / "osm_accessible_toilets_clean.csv")
    df = _filter_to_vic(df).drop_duplicates(subset=["osm_id"])
    suburbs = _load_suburb_reference()

    with Session(engine) as session:
        session.execute(text("DELETE FROM osm_accessible_toilet"))
        session.commit()
        records = []
        for _, r in df.iterrows():
            sub_id, sub_name = _nearest_suburb(r["latitude"], r["longitude"], suburbs)
            records.append(dict(
                osm_id=str(r["osm_id"]),
                name=str(r["name"]) if pd.notna(r["name"]) else "Accessible Toilet",
                wheelchair=str(r["wheelchair"]).lower() if pd.notna(r["wheelchair"]) else None,
                toilets_wheelchair=(
                    str(r["toilets:wheelchair"]).lower()
                    if "toilets:wheelchair" in r and pd.notna(r["toilets:wheelchair"])
                    else None
                ),
                opening_hours=str(r["opening_hours"]) if pd.notna(r["opening_hours"]) else None,
                operator=str(r["operator"]) if pd.notna(r["operator"]) else None,
                is_accessible=bool(r["is_accessible"]),
                lat=float(r["latitude"]),
                lon=float(r["longitude"]),
                suburb_id=sub_id,
                suburb_name=sub_name,
            ))
        batch_insert(session, OsmAccessibleToilet, records)
    print(f"  Loaded {len(records):,} accessible toilets")


def load_osm_wheelchair_places():
    print("Loading OSM wheelchair-accessible places...")
    df = pd.read_csv(OSM_DIR / "osm_wheelchair_accessible_places_clean.csv")
    df = _filter_to_vic(df).drop_duplicates(subset=["osm_id"])
    df["amenity_category"] = df["amenity"].apply(_classify_amenity)
    suburbs = _load_suburb_reference()

    with Session(engine) as session:
        session.execute(text("DELETE FROM osm_wheelchair_place"))
        session.commit()
        records = []
        for r in df.itertuples():
            sub_id, sub_name = _nearest_suburb(r.latitude, r.longitude, suburbs)
            records.append(dict(
                osm_id=str(r.osm_id),
                name=str(r.name) if pd.notna(r.name) else None,
                amenity=str(r.amenity) if pd.notna(r.amenity) else None,
                amenity_category=str(r.amenity_category),
                wheelchair=str(r.wheelchair).lower() if pd.notna(r.wheelchair) else None,
                operator=str(r.operator) if pd.notna(r.operator) else None,
                opening_hours=str(r.opening_hours) if pd.notna(r.opening_hours) else None,
                description=str(r.description) if pd.notna(r.description) else None,
                is_accessible=bool(r.is_accessible),
                lat=float(r.latitude),
                lon=float(r.longitude),
                suburb_id=sub_id,
                suburb_name=sub_name,
            ))
        batch_insert(session, OsmWheelchairPlace, records)
    print(f"  Loaded {len(records):,} wheelchair-accessible places")


def load_open_space_shade():
    """Merge open_space_shade.csv into open_space.shade_score_100 and nearby_tree_count.

    Self-heals the schema first — Base.metadata.create_all only creates new tables;
    it won't add new columns to existing ones, so we ALTER directly.
    """
    print("Merging open space shade data...")

    # Idempotent column add (IF NOT EXISTS makes this safe to re-run)
    with Session(engine) as session:
        session.execute(text("""
            ALTER TABLE open_space
              ADD COLUMN IF NOT EXISTS shade_score_100   double precision,
              ADD COLUMN IF NOT EXISTS nearby_tree_count integer
        """))
        session.commit()

    df = pd.read_csv(DATA_DIR / "open_space_shade.csv")
    updated = 0
    with Session(engine) as session:
        for r in df.itertuples():
            res = session.execute(
                text("""
                    UPDATE open_space
                       SET shade_score_100 = :ss,
                           nearby_tree_count = :nc
                     WHERE space_id = :sid
                """),
                {
                    "ss": float(r.shade_score_100),
                    "nc": int(r.nearby_tree_count),
                    "sid": int(r.space_id),
                },
            )
            updated += res.rowcount or 0
        session.commit()
    print(f"  Merged shade data into {updated} open_space rows (of {len(df)})")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.\n")

    load_psychological_distress()
    load_suburbs()
    load_landmarks()
    load_open_spaces()
    load_open_space_shade()        # NEW — must run after load_open_spaces()
    load_categories()
    load_public_toilets()
    load_pedestrian_sensors()
    load_microclimate_sensors()
    load_pedestrian_patterns()
    load_gtfs_stops()
    load_gtfs_routes()
    load_gtfs_patterns()
    load_gtfs_pathways()
    load_trees()
    load_osm_benches()              # NEW
    load_osm_accessible_toilets()   # NEW
    load_osm_wheelchair_places() 
    load_suburb_inference()   # NEW

    print("\nAll data loaded successfully!")
    print("\nTables loaded:")
    tables = [
        "suburb", "landmark", "open_space", "category",
        "public_toilet", "pedestrian_sensor", "microclimate_sensor",
        "pedestrian_pattern", "gtfs_stop", "gtfs_route",
        "gtfs_pattern", "gtfs_pathway", "tree",
        "osm_bench", "osm_accessible_toilet", "osm_wheelchair_place",
    ]
    for t in tables:
        print(f"  ✅ {t}")


if __name__ == "__main__":
    main()
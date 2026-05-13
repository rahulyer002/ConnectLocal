import pandas as pd
import geopandas as gpd
from pathlib import Path


# set up project folders

base_dir = Path(__file__).resolve().parents[1]

raw_dir = base_dir / "raw"
processed_dir = base_dir / "processed" / "osm_accessibility"

processed_dir.mkdir(parents=True, exist_ok=True)


# raw input files from overpass turbo exports

benches_file = raw_dir / "benches_melbourne.geojson"
toilets_file = raw_dir / "accessible_toilet_melbourne.geojson"
wheelchair_file = raw_dir / "wheelchair_accessible_melbourne.geojson"


# helper function to load geojson safely

def load_geojson(file_path):

    if not file_path.exists():
        raise FileNotFoundError(f"Could not find file: {file_path}")

    gdf = gpd.read_file(file_path)

    # convert to standard lat/lng coordinate system
    gdf = gdf.to_crs(epsg=4326)

    return gdf


# clean osm data into a consistent format for backend/frontend use

def clean_osm_dataset(gdf, amenity_type):

    gdf = gdf.copy()

    # convert polygons and lines into centre points
    # easier for frontend markers and suburb joins
    gdf["geometry"] = gdf.geometry.centroid

    # extract coordinates
    gdf["latitude"] = gdf.geometry.y
    gdf["longitude"] = gdf.geometry.x

    # keep useful osm columns if they exist
    useful_columns = [
        "id",
        "@id",
        "name",
        "amenity",
        "wheelchair",
        "toilets:wheelchair",
        "opening_hours",
        "operator",
        "description",
        "latitude",
        "longitude",
        "geometry"
    ]

    existing_columns = [col for col in useful_columns if col in gdf.columns]

    cleaned = gdf[existing_columns].copy()

    # create a standard osm id column
    if "@id" in cleaned.columns:
        cleaned["osm_id"] = cleaned["@id"]

    elif "id" in cleaned.columns:
        cleaned["osm_id"] = cleaned["id"]

    else:
        cleaned["osm_id"] = None

    cleaned["amenity_type"] = amenity_type

    # fallback names if missing
    if "name" not in cleaned.columns:
        cleaned["name"] = None

    cleaned["name"] = cleaned["name"].fillna(
        amenity_type.replace("_", " ").title()
    )

    # accessibility flags
    cleaned["is_accessible"] = False

    if "wheelchair" in cleaned.columns:

        cleaned.loc[
            cleaned["wheelchair"].astype(str).str.lower() == "yes",
            "is_accessible"
        ] = True

    if "toilets:wheelchair" in cleaned.columns:

        cleaned.loc[
            cleaned["toilets:wheelchair"].astype(str).str.lower() == "yes",
            "is_accessible"
        ] = True

    # accessible toilets should always be accessible
    if amenity_type == "accessible_toilet":
        cleaned["is_accessible"] = True

    # final backend-friendly structure
    final_columns = [
        "osm_id",
        "name",
        "amenity_type",
        "amenity",
        "wheelchair",
        "toilets:wheelchair",
        "opening_hours",
        "operator",
        "description",
        "is_accessible",
        "latitude",
        "longitude",
        "geometry"
    ]

    # create missing columns if needed
    for col in final_columns:

        if col not in cleaned.columns:
            cleaned[col] = None

    cleaned = cleaned[final_columns]

    # remove rows missing coordinates
    cleaned = cleaned.dropna(subset=["latitude", "longitude"])

    # remove duplicates
    cleaned = cleaned.drop_duplicates(
        subset=["osm_id", "latitude", "longitude"]
    )

    return gpd.GeoDataFrame(
        cleaned,
        geometry="geometry",
        crs="EPSG:4326"
    )


# save both csv and geojson outputs for the team

def save_outputs(gdf, output_name):

    csv_path = processed_dir / f"{output_name}.csv"
    geojson_path = processed_dir / f"{output_name}.geojson"

    # csv for backend/database use
    gdf.drop(columns="geometry").to_csv(csv_path, index=False)

    # geojson for maps/frontend
    gdf.to_file(geojson_path, driver="GeoJSON")

    print(f"Saved CSV: {csv_path}")
    print(f"Saved GeoJSON: {geojson_path}")


# load raw osm datasets

benches_raw = load_geojson(benches_file)
toilets_raw = load_geojson(toilets_file)
wheelchair_raw = load_geojson(wheelchair_file)


# clean each dataset

benches_clean = clean_osm_dataset(
    benches_raw,
    "bench"
)

toilets_clean = clean_osm_dataset(
    toilets_raw,
    "accessible_toilet"
)

wheelchair_clean = clean_osm_dataset(
    wheelchair_raw,
    "wheelchair_accessible_place"
)


# save cleaned individual datasets

save_outputs(
    benches_clean,
    "osm_benches_clean"
)

save_outputs(
    toilets_clean,
    "osm_accessible_toilets_clean"
)

save_outputs(
    wheelchair_clean,
    "osm_wheelchair_accessible_places_clean"
)


# combine everything into one accessibility dataset

combined = pd.concat(
    [
        benches_clean,
        toilets_clean,
        wheelchair_clean
    ],
    ignore_index=True
)

combined = gpd.GeoDataFrame(
    combined,
    geometry="geometry",
    crs="EPSG:4326"
)

save_outputs(
    combined,
    "osm_accessibility_amenities_combined"
)


# small summary file for quick reference

summary = combined.groupby(
    "amenity_type"
).size().reset_index(
    name="record_count"
)

summary_path = processed_dir / "osm_accessibility_summary.csv"

summary.to_csv(summary_path, index=False)


print("\nProcessing complete.\n")
print(summary)

print(f"\nSummary saved to: {summary_path}")
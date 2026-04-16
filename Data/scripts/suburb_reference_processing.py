from pathlib import Path
import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "raw" / "SA2_2021_AUST_SHP_GDA2020"
PROCESSED_DIR = BASE_DIR / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def process_suburb_reference() -> gpd.GeoDataFrame:
    shp_path = RAW_DIR / "SA2_2021_AUST_GDA2020.shp"

    if not shp_path.exists():
        raise FileNotFoundError(f"Missing shapefile: {shp_path}")

    gdf = gpd.read_file(shp_path)

    print("Shapefile columns:")
    print(gdf.columns.tolist())

    # Keep only Victoria SA2 areas
    if "STE_NAME21" in gdf.columns:
        gdf = gdf[gdf["STE_NAME21"] == "Victoria"].copy()
    elif "STE_CODE21" in gdf.columns:
        gdf = gdf[gdf["STE_CODE21"] == "2"].copy()
    else:
        raise KeyError("Could not find STE_NAME21 or STE_CODE21 in shapefile columns.")

    # Centroids should be calculated in a projected CRS, then converted to lat/lng
    gdf_projected = gdf.to_crs(epsg=3111)  # Vicgrid / suitable projected CRS for Victoria
    centroids_projected = gdf_projected.geometry.centroid
    centroids_wgs84 = gpd.GeoSeries(centroids_projected, crs="EPSG:3111").to_crs(epsg=4326)

    gdf["centroid_lat"] = centroids_wgs84.y
    gdf["centroid_lng"] = centroids_wgs84.x

    suburb_ref = gdf[[
        "SA2_CODE21",
        "SA2_NAME21",
        "centroid_lat",
        "centroid_lng"
    ]].copy()

    suburb_ref = suburb_ref.rename(columns={
        "SA2_CODE21": "suburb_id",
        "SA2_NAME21": "suburb_name"
    })

    suburb_ref["suburb_id"] = suburb_ref["suburb_id"].astype(str)

    return suburb_ref


def main() -> None:
    suburb_ref = process_suburb_reference()

    output_path = PROCESSED_DIR / "suburb_reference.csv"
    suburb_ref.to_csv(output_path, index=False)

    print("\nSaved suburb reference:")
    print(output_path)
    print("\nPreview:")
    print(suburb_ref.head())
    print("\nShape:")
    print(suburb_ref.shape)


if __name__ == "__main__":
    main()
"""
Point-based queries over the OSM accessibility tables.

For suburb-based versions see suburb_service.get_accessibility_summary_for_suburb.
"""
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.osm_bench import OsmBench
from app.models.osm_accessible_toilet import OsmAccessibleToilet
from app.models.osm_wheelchair_place import OsmWheelchairPlace
from app.models.tree import Tree
from app.services.epic_data_service import haversine_km


def get_benches_nearby(db: Session, lat: float, lon: float, radius_km: float = 0.5, limit: int = 50) -> list[dict]:
    rows = db.query(OsmBench).all()
    out = []
    for b in rows:
        d = haversine_km(lat, lon, b.lat, b.lon)
        if d <= radius_km:
            out.append({
                "osm_id": b.osm_id,
                "name": b.name,
                "lat": b.lat,
                "lon": b.lon,
                "distance_km": d,
                "suburb_name": b.suburb_name,
            })
    out.sort(key=lambda x: x["distance_km"])
    return out[:limit]


def get_accessible_toilets_nearby(
    db: Session, lat: float, lon: float, radius_km: float = 1.0,
    only_confirmed_wheelchair: bool = False, limit: int = 30,
) -> list[dict]:
    q = db.query(OsmAccessibleToilet)
    if only_confirmed_wheelchair:
        q = q.filter(OsmAccessibleToilet.wheelchair.in_(["yes", "designated"]))
    rows = q.all()
    out = []
    for t in rows:
        d = haversine_km(lat, lon, t.lat, t.lon)
        if d <= radius_km:
            out.append({
                "osm_id": t.osm_id,
                "name": t.name,
                "wheelchair": t.wheelchair,
                "opening_hours": t.opening_hours,
                "operator": t.operator,
                "lat": t.lat,
                "lon": t.lon,
                "distance_km": d,
                "suburb_name": t.suburb_name,
                "source": "openstreetmap",
            })
    out.sort(key=lambda x: x["distance_km"])
    return out[:limit]


def get_wheelchair_places_nearby(
    db: Session, lat: float, lon: float, radius_km: float = 2.0,
    category: str | None = None, amenity: str | None = None,
    operator: str | None = None, limit: int = 50,
) -> list[dict]:
    q = db.query(OsmWheelchairPlace)
    if category:
        q = q.filter(OsmWheelchairPlace.amenity_category == category.lower())
    if amenity:
        q = q.filter(func.lower(OsmWheelchairPlace.amenity) == amenity.lower())
    if operator:
        q = q.filter(func.lower(OsmWheelchairPlace.operator).contains(operator.lower()))
    rows = q.all()
    out = []
    for p in rows:
        d = haversine_km(lat, lon, p.lat, p.lon)
        if d <= radius_km:
            out.append({
                "osm_id": p.osm_id,
                "name": p.name,
                "amenity": p.amenity,
                "category": p.amenity_category,
                "wheelchair": p.wheelchair,
                "operator": p.operator,
                "opening_hours": p.opening_hours,
                "lat": p.lat,
                "lon": p.lon,
                "distance_km": d,
                "suburb_name": p.suburb_name,
            })
    out.sort(key=lambda x: x["distance_km"])
    return out[:limit]


def get_trees_nearby(
    db: Session, lat: float, lon: float, radius_km: float = 0.2,
    min_shade: float = 0.0, limit: int = 100,
) -> list[dict]:
    """82k trees — default radius 200m for performance + relevance."""
    rows = db.query(Tree).filter(Tree.shade_score >= min_shade).all()
    out = []
    for t in rows:
        d = haversine_km(lat, lon, t.lat, t.lon)
        if d <= radius_km:
            out.append({
                "tree_id": t.tree_id,
                "common_name": t.common_name,
                "genus": t.genus,
                "shade_score": t.shade_score,
                "useful_life_label": t.useful_life_label,
                "age_description": t.age_description,
                "located_in": t.located_in,
                "precinct": t.precinct,
                "lat": t.lat,
                "lon": t.lon,
                "distance_km": d,
            })
    out.sort(key=lambda x: x["distance_km"])
    return out[:limit]


def get_shade_score_for_point(db: Session, lat: float, lon: float, radius_m: float = 50) -> dict:
    radius_km = radius_m / 1000.0
    rows = db.query(Tree).all()
    nearby = [t for t in rows if haversine_km(lat, lon, t.lat, t.lon) <= radius_km]
    total_shade = sum((t.shade_score or 0) for t in nearby)
    species = [t.common_name for t in nearby if t.common_name]
    top_species = [{"name": n, "count": c} for n, c in Counter(species).most_common(3)]
    return {
        "lat": lat,
        "lon": lon,
        "radius_m": radius_m,
        "tree_count": len(nearby),
        "total_shade_score": round(total_shade, 4),
        "avg_shade_per_tree": round(total_shade / len(nearby), 4) if nearby else 0,
        "shade_grade": (
            "Excellent" if total_shade > 0.5 else
            "Good" if total_shade > 0.1 else
            "Moderate" if total_shade > 0.02 else
            "Sparse"
        ),
        "top_species": top_species,
    }

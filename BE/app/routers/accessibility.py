"""
Standalone point-based OSM accessibility endpoints.
For suburb-scoped versions see /api/suburbs/{id}/accessibility.
"""
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.accessibility_service import (
    get_benches_nearby,
    get_accessible_toilets_nearby,
    get_wheelchair_places_nearby,
)

router = APIRouter()


@router.get("/benches")
def benches(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    radius_km: float = Query(0.5, description="Search radius in km"),
    limit: int = Query(50, description="Max results"),
    db: Session = Depends(get_db),
):
    """Public benches near a coordinate — rest points along a walk."""
    items = get_benches_nearby(db, lat, lon, radius_km, limit)
    return {
        "total": len(items),
        "search_lat": lat, "search_lon": lon, "radius_km": radius_km,
        "benches": items,
        "data_source": "OpenStreetMap",
    }


@router.get("/toilets")
def osm_toilets(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(1.0),
    confirmed_wheelchair_only: bool = Query(
        False, description="If true, only return toilets tagged wheelchair=yes or designated"
    ),
    limit: int = Query(30),
    db: Session = Depends(get_db),
):
    """
    Accessible toilets from OSM. ~25× the coverage of /api/greenspace/toilets,
    which is City-of-Melbourne LGA only.
    """
    items = get_accessible_toilets_nearby(
        db, lat, lon, radius_km, confirmed_wheelchair_only, limit
    )
    return {
        "total": len(items),
        "search_lat": lat, "search_lon": lon, "radius_km": radius_km,
        "toilets": items,
        "data_source": "OpenStreetMap",
        "note": "wheelchair tag: yes/designated (best), limited/no, or null (unknown)",
    }


@router.get("/places")
def wheelchair_places(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(2.0),
    category: str | None = Query(
        None,
        description="essentials | social | healthcare | aged_care_social | transit | other",
    ),
    amenity: str | None = Query(None, description="OSM amenity e.g. cafe, library, pharmacy"),
    operator: str | None = Query(None),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    """Wheelchair-accessible venues — cafes, libraries, pharmacies, aged care, etc."""
    items = get_wheelchair_places_nearby(
        db, lat, lon, radius_km, category, amenity, operator, limit
    )
    return {
        "total": len(items),
        "filters": {"category": category, "amenity": amenity, "operator": operator},
        "places": items,
        "data_source": "OpenStreetMap",
    }


@router.get("/places/categories")
def place_categories(db: Session = Depends(get_db)):
    """Distinct category + amenity values for filter dropdowns."""
    from app.models.osm_wheelchair_place import OsmWheelchairPlace
    rows = db.query(
        OsmWheelchairPlace.amenity_category, OsmWheelchairPlace.amenity
    ).distinct().all()
    by_category: dict[str, list[str]] = {}
    for cat, am in rows:
        if not cat:
            continue
        by_category.setdefault(cat, [])
        if am and am not in by_category[cat]:
            by_category[cat].append(am)
    return {"categories": by_category}

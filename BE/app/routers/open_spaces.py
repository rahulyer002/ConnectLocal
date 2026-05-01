from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import data_service

router = APIRouter()


@router.get("/nearby")
def get_open_spaces_nearby(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    radius_km: float = Query(default=2.0, description="Search radius in km"),
    category: str = Query(default=None, description="Filter by category: Green Space | Urban Space | Recreation | Other"),
    has_toilet: bool = Query(default=None, description="Filter to spaces with nearby toilet"),
    limit: int = Query(default=20, description="Max results"),
    db: Session = Depends(get_db),
):
    """
    Returns open spaces near a location sorted by distance.
    Includes comfort score, walkability score, toilet proximity.
    Useful for suggesting outdoor meetup spots for elderly users.
    """
    results = data_service.get_open_spaces_nearby(
        db, lat, lon, radius_km, category, has_toilet, limit
    )
    return {
        "total": len(results),
        "search_lat": lat,
        "search_lon": lon,
        "radius_km": radius_km,
        "open_spaces": results,
    }

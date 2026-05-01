from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import data_service

router = APIRouter()


@router.get("/nearby")
def get_landmarks_nearby(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    radius_km: float = Query(default=2.0, description="Search radius in km"),
    theme: str = Query(default=None, description="Filter by theme e.g. 'Community Use', 'Health Services', 'Leisure/Recreation'"),
    limit: int = Query(default=20, description="Max results"),
    db: Session = Depends(get_db),
):
    """
    Returns landmarks near a location sorted by distance.
    Includes libraries, community centres, parks, health services etc.
    """
    results = data_service.get_landmarks_nearby(db, lat, lon, radius_km, theme, limit)
    return {
        "total": len(results),
        "search_lat": lat,
        "search_lon": lon,
        "radius_km": radius_km,
        "landmarks": results,
    }


@router.get("/themes")
def get_landmark_themes(db: Session = Depends(get_db)):
    """
    Returns all unique landmark themes.
    Use for filter dropdowns in the frontend.
    """
    return data_service.get_landmark_themes(db)
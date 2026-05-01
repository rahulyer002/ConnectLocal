"""
app/routers/greenspace.py
--------------------------
Epic 4 — Green Space & Comfort APIs.

Endpoints:
  GET /api/greenspace/nearby   — open spaces ranked by comfort + shade + toilet
  GET /api/greenspace/toilets  — public toilets near a location
"""

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.epic_data_service import (
    get_green_spaces_nearby,
    get_nearby_toilets,
)

router = APIRouter()


@router.get("/nearby")
def get_green_spaces(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    radius_km: float = Query(default=2.0, description="Search radius in km"),
    has_toilet: bool = Query(default=None, description="Filter to spaces with nearby toilet"),
    limit: int = Query(default=10, description="Max results"),
    db: Session = Depends(get_db),
):
    """
    Returns open spaces near a location ranked by comfort score.

    Comfort score (0-100) combines:
      - Walkability (pedestrian-friendly surface)
      - Toilet proximity
      - Category bonus (park > reserve > plaza)

    Use this to suggest the most comfortable outdoor spaces for elderly users.
    """
    spaces = get_green_spaces_nearby(db, lat, lon, radius_km, has_toilet, limit)

    return {
        "total": len(spaces),
        "search_lat": lat,
        "search_lon": lon,
        "radius_km": radius_km,
        "green_spaces": spaces,
        "sorted_by": "comfort_score (highest first)",
    }


@router.get("/toilets")
def get_toilets_nearby(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    radius_km: float = Query(default=0.5, description="Search radius in km"),
    wheelchair_only: bool = Query(default=False, description="Only wheelchair accessible toilets"),
    db: Session = Depends(get_db),
):
    """
    Returns public toilets near a location.
    All toilets are City of Melbourne operated.
    Only covers City of Melbourne LGA (CBD + inner suburbs).

    Fields:
      has_wheelchair — wheelchair accessible cubicle
      has_female / has_male — gender specific
      has_baby_facility — baby change table
    """
    toilets = get_nearby_toilets(db, lat, lon, radius_km, wheelchair_only)

    return {
        "total": len(toilets),
        "search_lat": lat,
        "search_lon": lon,
        "radius_km": radius_km,
        "wheelchair_only": wheelchair_only,
        "toilets": toilets,
        "data_note": "City of Melbourne public toilets only. Does not cover outer suburbs.",
    }
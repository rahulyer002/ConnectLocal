"""
Standalone point-based tree-canopy endpoints.
For suburb-scoped versions see /api/suburbs/{id}/trees.
"""
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.accessibility_service import get_trees_nearby, get_shade_score_for_point

router = APIRouter()


@router.get("/nearby")
def trees_nearby(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_km: float = Query(0.2, description="Default 200m — trees are dense"),
    min_shade: float = Query(0.0, description="Minimum shade_score (0-1)"),
    limit: int = Query(100),
    db: Session = Depends(get_db),
):
    """Individual tree records near a coordinate."""
    items = get_trees_nearby(db, lat, lon, radius_km, min_shade, limit)
    return {"total": len(items), "trees": items}


@router.get("/shade")
def shade_for_point(
    lat: float = Query(...),
    lon: float = Query(...),
    radius_m: float = Query(50, description="Radius in metres (default 50m)"),
    db: Session = Depends(get_db),
):
    """Aggregate canopy shade score for a single point — feeds Resonance scoring."""
    return get_shade_score_for_point(db, lat, lon, radius_m)

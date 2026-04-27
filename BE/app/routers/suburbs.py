from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import data_service

router = APIRouter()


@router.get("/profile")
def get_suburb_profile(
    suburb: str = Query(description="Suburb name e.g. fitzroy, carlton"),
    db: Session = Depends(get_db),
):
    """
    Returns demographic profile for a suburb.
    Population breakdown, elderly percentage, vulnerability indicators.
    """
    result = data_service.get_suburb_profile(db, suburb)
    if not result:
        raise HTTPException(status_code=404, detail=f"Suburb '{suburb}' not found")
    return result


@router.get("/search")
def search_suburbs(
    q: str = Query(description="Suburb name search query e.g. 'fit' returns fitzroy"),
    limit: int = Query(default=10, description="Max results"),
    db: Session = Depends(get_db),
):
    """
    Search suburbs by name. Used for autocomplete in location input.
    Returns suburb_id, suburb_name, centroid_lat, centroid_lng.
    """
    results = data_service.search_suburbs(db, q, limit)
    return {"total": len(results), "suburbs": results}
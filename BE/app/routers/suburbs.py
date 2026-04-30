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

from app.models.psychological_distress import PsychologicalDistress

@router.get("/psychological-distress")
def get_psychological_distress(db: Session = Depends(get_db)):
    """
    Returns psychological distress rates by age group.
    Source: ABS National Health Survey 2017-18.
    """
    rows = db.query(PsychologicalDistress).order_by(PsychologicalDistress.id).all()
    return {
        "source": "ABS National Health Survey, Psychological distress - Australia",
        "year": "2017-18",
        "note": "Percentage of population with high or very high psychological distress",
        "data": [
            {
                "age_group": r.age_group,
                "psychological_distress_percent": r.psychological_distress_percent,
            }
            for r in rows
        ],
        "elderly_highlight": {
            "age_group": "65+",
            "psychological_distress_percent": 9.9,
            "note": "Elderly (65+) have lower measured distress but face higher social isolation risk"
        }
    }
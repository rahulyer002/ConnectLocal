from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import data_service

router = APIRouter()


@router.get("")
def get_categories(
    senior_only: bool = Query(default=False, description="Return only senior-friendly categories"),
    db: Session = Depends(get_db),
):
    """
    Returns event/landmark categories.
    senior_only=true returns only categories tagged as senior-friendly.
    """
    results = data_service.get_categories(db, senior_only)
    return {"total": len(results), "categories": results}
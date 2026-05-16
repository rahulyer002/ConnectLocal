"""
Inference API — precomputed elderly-friendliness scores per suburb.

Endpoints
---------
GET /api/inference/{suburb_id}  — full inference payload for one suburb
GET /api/inference/rankings     — top-N suburbs by a chosen metric
GET /api/inference/health       — coverage diagnostic

Error contract
--------------
All errors return `{detail: "<plain English message>"}` (FastAPI default).
Specific status codes are deliberate — the frontend keys on them:

  400  malformed query (bad metric name, bad top range)
  404  no such suburb in the suburb table at all
  503  suburb exists but inference hasn't been computed yet
        (the ETL has not run since the table was created)
  500  anything unexpected — logged server-side, generic message to client
"""
import logging
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app.models.suburb import Suburb
from app.models.suburb_inference import SuburbInference
from app.services import inference_service

router = APIRouter()
log = logging.getLogger(__name__)


VALID_METRICS = {
    "outing_score",
    "score_rest", "score_relief", "score_amenities",
    "score_shade", "score_transit", "score_social",
    "elderly_pct",
}

VALID_PERSONAS = {
    "Urban Core", "Community Hub", "Leafy Retreat",
    "Outer / Limited Transit", "Elderly-Heavy",
    "Service Rich", "Suburban Mixed",
}


@router.get("/health")
def inference_health(db: Session = Depends(get_db)):
    """
    Coverage report: how many suburbs have inference computed, and when.
    Use this to verify the ETL ran. Never raises — always returns a status.
    """
    try:
        total_suburbs = db.query(Suburb).count()
        rows = db.query(SuburbInference).count()
        latest = db.query(SuburbInference).order_by(SuburbInference.generated_at.desc()).first()
        return {
            "status": "ok" if rows > 0 else "not-computed",
            "suburbs_total":      total_suburbs,
            "suburbs_with_score": rows,
            "coverage_pct":       round(rows / total_suburbs * 100, 1) if total_suburbs else 0.0,
            "last_generated_at":  latest.generated_at.isoformat() if latest and latest.generated_at else None,
        }
    except SQLAlchemyError as exc:
        log.error("inference_health DB error: %s", exc)
        return {"status": "db-error", "detail": "Unable to read inference table."}


@router.get("/rankings")
def get_rankings(
    metric:  str           = Query(default="outing_score", description=f"One of: {sorted(VALID_METRICS)}"),
    persona: Optional[str] = Query(default=None,           description=f"Optional filter. One of: {sorted(VALID_PERSONAS)}"),
    top:     int           = Query(default=10, ge=1, le=1000, description="Number of suburbs to return (1-1000)"),
    db: Session = Depends(get_db),
):
    """
    Top-N suburbs by a chosen metric, optionally filtered by persona.
    Powers the 'leaderboard' sidebar on the Suburb Explorer.
    """
    if metric not in VALID_METRICS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown metric '{metric}'. Choose one of: {sorted(VALID_METRICS)}",
        )
    if persona is not None and persona not in VALID_PERSONAS:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown persona '{persona}'. Choose one of: {sorted(VALID_PERSONAS)}",
        )

    try:
        rows = inference_service.get_rankings(db, metric=metric, persona=persona, top=top)
    except SQLAlchemyError as exc:
        log.error("get_rankings DB error: %s", exc)
        raise HTTPException(status_code=500, detail="Could not load ranking data right now.")

    if not rows:
        return {
            "metric": metric,
            "persona": persona,
            "total": 0,
            "suburbs": [],
            "note": "No inference rows match. Has the ETL been run yet? See GET /api/inference/health.",
        }

    name_map = inference_service.suburb_name_map(db, [r.suburb_id for r in rows])
    items = []
    for r in rows:
        d = r.to_dict_compact()
        d["suburb_name"] = name_map.get(int(r.suburb_id), "")
        items.append(d)

    return {"metric": metric, "persona": persona, "total": len(items), "suburbs": items}


@router.get("/{suburb_id}")
def get_inference(suburb_id: int, db: Session = Depends(get_db)):
    """
    Full inference payload for one suburb.

    404 if the suburb_id is unknown.
    503 if the suburb exists but inference has not been computed yet
        (loader hasn't run). The frontend should show a "still preparing"
        message rather than a generic error.
    """
    try:
        row = inference_service.get_for_suburb(db, suburb_id)
    except SQLAlchemyError as exc:
        log.error("get_inference DB error for %s: %s", suburb_id, exc)
        raise HTTPException(status_code=500, detail="Could not load suburb scores right now. Please try again.")

    if row is not None:
        try:
            payload = row.to_dict()
        except Exception as exc:
            log.exception("inference serialisation failed for %s: %s", suburb_id, exc)
            raise HTTPException(status_code=500, detail="Score data is malformed for this suburb.")
        suburb = db.query(Suburb).filter(Suburb.suburb_id == suburb_id).first()
        if suburb:
            payload["suburb_name"] = suburb.suburb_name
            payload["centroid"]    = {"lat": suburb.centroid_lat, "lng": suburb.centroid_lng}
        return payload

    suburb_exists = db.query(Suburb).filter(Suburb.suburb_id == suburb_id).first() is not None
    if not suburb_exists:
        raise HTTPException(status_code=404, detail=f"Suburb {suburb_id} not found.")

    raise HTTPException(
        status_code=503,
        detail=(
            f"Score data for suburb {suburb_id} is being prepared. "
            "Please try again in a moment, or contact the team to re-run the ETL."
        ),
    )

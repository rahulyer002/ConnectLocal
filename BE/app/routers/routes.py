"""
GTFS route metadata — exposes the previously-orphaned gtfs_route table.
"""
from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.gtfs_route import GtfsRoute
from app.models.gtfs_stop import GtfsStop

router = APIRouter()


@router.get("/search")
def routes_search(
    q: str | None = Query(None, description="Partial match on route name"),
    mode: str | None = Query(None, description="bus | tram | train"),
    limit: int = Query(50),
    db: Session = Depends(get_db),
):
    """Search routes by partial name and/or mode."""
    query = db.query(GtfsRoute)
    if mode:
        query = query.filter(GtfsRoute.mode == mode.lower())
    if q:
        like = f"%{q.lower()}%"
        query = query.filter(
            (func.lower(GtfsRoute.route_short_name).like(like))
            | (func.lower(GtfsRoute.route_long_name).like(like))
        )
    rows = query.limit(limit).all()
    return {
        "total": len(rows),
        "routes": [
            {
                "route_id": r.route_id,
                "short_name": r.route_short_name,
                "long_name": r.route_long_name,
                "mode": r.mode,
                "color_hex": f"#{r.route_color}" if r.route_color else None,
                "text_color_hex": f"#{r.route_text_color}" if r.route_text_color else None,
            }
            for r in rows
        ],
    }


@router.get("/by-stop/{stop_id}")
def routes_for_stop(stop_id: str, db: Session = Depends(get_db)):
    """All route metadata for a given GTFS stop."""
    stop = db.query(GtfsStop).filter(GtfsStop.stop_id == stop_id).first()
    if not stop or not stop.routes_served:
        return {"stop_id": stop_id, "total": 0, "routes": []}

    short_names = [s.strip() for s in stop.routes_served.split(",") if s.strip()]
    rows = db.query(GtfsRoute).filter(GtfsRoute.route_short_name.in_(short_names)).all()
    return {
        "stop_id": stop_id,
        "stop_name": stop.stop_name,
        "total": len(rows),
        "routes": [
            {
                "route_id": r.route_id,
                "short_name": r.route_short_name,
                "long_name": r.route_long_name,
                "mode": r.mode,
                "color_hex": f"#{r.route_color}" if r.route_color else None,
            }
            for r in rows
        ],
    }

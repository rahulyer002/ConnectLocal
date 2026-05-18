"""
app/routers/resonance.py
-------------------------
Epic 4 — Personalised Timing & Resonance Engine APIs.

Endpoints:
  GET /api/resonance/score     — resonance score for a location right now
  GET /api/resonance/gonow     — top recommendations near user right now
  GET /api/resonance/forecast  — 7-day crowd forecast for a location
  GET /api/resonance/besttimes — top N quietest times to visit
  GET /api/safety/conditions   — live microclimate safety verdict
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.epic_data_service import (
    get_crowd_level_now,
    get_crowd_forecast,
    get_best_times,
    get_live_microclimate,
    compute_resonance_score,
    get_green_spaces_nearby,
    get_nearby_toilets,
)
import datetime

router = APIRouter()


@router.get("/score")
async def get_resonance_score(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    db: Session = Depends(get_db),
):
    crowd = get_crowd_level_now(db, lat, lon, radius_km=0.5)
    weather = await get_live_microclimate(lat, lon)
    spaces = get_green_spaces_nearby(db, lat, lon, radius_km=1.0, limit=1)
    comfort_score = spaces[0]["comfort_score"] if spaces else None
    toilets = get_nearby_toilets(db, lat, lon, radius_km=0.3)
    has_toilet = len(toilets) > 0
    score = compute_resonance_score(
        crowd_level=crowd.get("crowd_level"),
        is_quiet=crowd.get("is_quiet"),
        weather=weather,
        comfort_score=comfort_score,
        has_toilet=has_toilet,
        shade_score=spaces[0].get("comfort_score") if spaces else None,
    )
    return {
        **score,
        "location": {"lat": lat, "lon": lon},
        "crowd": crowd,
        "weather": weather,
        "nearest_open_space": spaces[0] if spaces else None,
        "nearest_toilet": toilets[0] if toilets else None,
    }


@router.get("/gonow")
async def get_go_now(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    radius_km: float = Query(default=2.0, description="Search radius in km"),
    db: Session = Depends(get_db),
):
    weather = await get_live_microclimate(lat, lon)
    spaces = get_green_spaces_nearby(db, lat, lon, radius_km=radius_km, limit=10)
    recommendations = []
    for space in spaces:
        crowd = get_crowd_level_now(db, space["lat"], space["lon"], radius_km=1.0)
        toilets = get_nearby_toilets(db, space["lat"], space["lon"], radius_km=0.2)
        score = compute_resonance_score(
            crowd_level=crowd.get("crowd_level"),
            is_quiet=crowd.get("is_quiet"),
            weather=weather,
            comfort_score=space.get("comfort_score"),
            has_toilet=len(toilets) > 0,
            shade_score=space.get("comfort_score"),
        )
        recommendations.append({
            "space_id": space["space_id"],
            "space_name": space["space_name"],
            "space_type": space["space_type"],
            "lat": space["lat"],
            "lon": space["lon"],
            "distance_km": space["distance_km"],
            "resonance_score": score["resonance_score"],
            "grade": score["grade"],
            "crowd_level": crowd.get("crowd_level"),
            "is_quiet_now": crowd.get("is_quiet"),
            "has_toilet_nearby": len(toilets) > 0,
            "comfort_score": space.get("comfort_score"),
            "why_recommended": _build_recommendation_reason(score, crowd, toilets),
        })
    recommendations.sort(key=lambda x: x["resonance_score"], reverse=True)
    return {
        "generated_at": datetime.datetime.now().strftime("%A %d %b, %I:%M %p"),
        "weather": weather,
        "total_spaces_checked": len(spaces),
        "recommendations": recommendations[:3],
    }


@router.get("/besttimes")
def get_best_times_endpoint(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    radius_km: float = Query(default=1.0),
    top_n: int = Query(default=5),
    db: Session = Depends(get_db),
):
    """
    Top N quietest historical time-windows near a location.

    Returns 200 with `has_data: false` and an informative `message` when the
    location is outside the City of Melbourne pedestrian sensor coverage area
    rather than 404 — the frontend treats this as a friendly "outside coverage"
    state, not an error.
    """
    best = get_best_times(db, lat, lon, radius_km, top_n)
    if not best:
        return {
            "location": {"lat": lat, "lon": lon},
            "best_times": [],
            "has_data": False,
            "coverage_area": "City of Melbourne CBD and inner suburbs",
            "message": (
                "Historical foot-traffic patterns aren't available for this location. "
                "Our crowd data uses the City of Melbourne pedestrian sensor network, "
                "which covers the CBD and inner suburbs. Try a CBD postcode (e.g. 3000) "
                "to see this section."
            ),
        }
    return {
        "location": {"lat": lat, "lon": lon},
        "best_times": best,
        "has_data": True,
        "tip": "These are historically the quietest times near this location.",
    }


@router.get("/forecast")
def get_forecast(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    radius_km: float = Query(default=2.0),
    db: Session = Depends(get_db),
):
    """
    7-day hourly crowd forecast grouped by day, derived from 2 years of City of
    Melbourne pedestrian sensor data.

    Returns 200 with `has_data: false` and an informative `message` when the
    location is outside the sensor coverage area rather than 404.
    """
    forecast = get_crowd_forecast(db, lat, lon, radius_km)
    if not forecast:
        return {
            "location": {"lat": lat, "lon": lon},
            "forecast_days": [],
            "forecast": {},
            "has_data": False,
            "coverage_area": "City of Melbourne CBD and inner suburbs",
            "message": (
                "We don't have hourly crowd patterns for this location. "
                "Coverage is the City of Melbourne CBD and inner suburbs only. "
                "Try a CBD postcode (e.g. 3000) to see this section."
            ),
        }
    by_day: dict[str, list] = {}
    for f in forecast:
        day = f["day_name"]
        if day not in by_day:
            by_day[day] = []
        by_day[day].append({
            "hour": f["hour"],
            "hour_label": f"{f['hour']:02d}:00",
            "avg_count": f["avg_count"],
            "crowd_level": f["crowd_level"],
            "is_quiet": f["is_quiet_hour"],
        })
    return {
        "location": {"lat": lat, "lon": lon},
        "forecast_days": list(by_day.keys()),
        "forecast": by_day,
        "has_data": True,
        "data_note": "Based on 2 years of City of Melbourne pedestrian sensor data (2024-2026)",
    }


def _build_recommendation_reason(score: dict, crowd: dict, toilets: list) -> str:
    reasons = []
    if crowd.get("crowd_level") == "Low":
        reasons.append("quiet right now")
    if score["breakdown"]["weather_score"] >= 30:
        reasons.append("good weather conditions")
    if len(toilets) > 0:
        reasons.append("toilet nearby")
    if score["breakdown"]["comfort_score"] >= 15:
        reasons.append("comfortable and walkable")
    if not reasons:
        reasons.append("nearby and accessible")
    return "Great option — " + ", ".join(reasons)
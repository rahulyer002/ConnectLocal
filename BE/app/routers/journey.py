"""
app/routers/journey.py
-----------------------
Epic 3 — Door-to-Venue Journey Support APIs.

Endpoints:
  GET /api/journey/plan          — full door-to-venue journey plan
  GET /api/journey/stops/nearby  — nearest public transport stops
  GET /api/journey/departures    — scheduled departures from a stop
  GET /api/journey/walk          — walking route between two points
  GET /api/journey/accessibility — stop accessibility info
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.epic_data_service import (
    get_stops_nearby,
    get_stop_departures,
    get_stop_accessibility,
    get_walking_route,
    plan_journey,
)

router = APIRouter()


@router.get("/plan")
async def plan_journey_endpoint(
    from_lat: float = Query(description="Origin latitude (user home)"),
    from_lon: float = Query(description="Origin longitude (user home)"),
    to_lat: float = Query(description="Destination latitude (event venue)"),
    to_lon: float = Query(description="Destination longitude (event venue)"),
    arrive_by: str = Query(default=None, description="Desired arrival time ISO format e.g. 2026-05-01T19:00:00"),
    mode: str = Query(default="walking", description="Mode of transport: transit | walking | cycling"),
    db: Session = Depends(get_db),
):
    """
    Plans a door-to-venue journey using public transport + walking.

    Journey legs:
      1. Walk from home to nearest public transport stop (via OSRM)
      2. Wait for scheduled service (from GTFS timetable)
      3. Transit to stop nearest venue (scheduled timetable)
      4. Walk from stop to venue (via OSRM)

    Returns plain-English step-by-step directions optimised for elderly users.
    Includes wheelchair accessibility flags at each stop.

    If arrive_by is provided, calculates "Leave home by" time.

    Data sources:
      - PTV GTFS Schedule (static timetables — not live)
      - OSRM (walking routes)
    """
    result = await plan_journey(db, from_lat, from_lon, to_lat, to_lon, arrive_by, mode=mode)
    return result


@router.get("/stops/nearby")
def get_nearby_stops(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
    radius_km: float = Query(default=0.5, description="Search radius in km"),
    mode: str = Query(default=None, description="Filter by mode: train | tram | bus"),
    wheelchair_only: bool = Query(default=False, description="Only wheelchair accessible stops"),
    limit: int = Query(default=10, description="Max results"),
    db: Session = Depends(get_db),
):
    """
    Returns public transport stops near a location.

    For each stop:
      - stop_name, mode (train/tram/bus)
      - distance_km from user
      - is_wheelchair_accessible
      - routes_served (comma-separated route numbers)

    wheelchair_only=true returns only stops with confirmed wheelchair access.
    Note: Many stops have unknown accessibility (wheelchair_boarding=0).
    """
    stops = get_stops_nearby(db, lat, lon, radius_km, mode, wheelchair_only, limit)

    if not stops:
        return {
            "total": 0,
            "stops": [],
            "note": f"No {'wheelchair accessible ' if wheelchair_only else ''}stops found within {radius_km}km. Try increasing radius_km."
        }

    return {
        "total": len(stops),
        "search_lat": lat,
        "search_lon": lon,
        "radius_km": radius_km,
        "mode_filter": mode,
        "wheelchair_only": wheelchair_only,
        "stops": stops,
    }


@router.get("/departures")
def get_departures(
    stop_id: str = Query(description="GTFS stop ID e.g. 19854"),
    hour: int = Query(default=None, description="Hour of day 0-23. Defaults to current hour."),
    db: Session = Depends(get_db),
):
    """
    Returns scheduled departures from a stop for a given hour.

    Returns avg_departures_per_hour and frequency_mins (how often a service runs).

    Note: These are SCHEDULED timetables, not live departures.
    No PTV API key available for live data.

    frequency_mins = 60 / avg_departures_per_hour
    e.g. 6 departures/hour = every 10 minutes
    """
    departures = get_stop_departures(db, stop_id, hour)

    if not departures:
        raise HTTPException(
            status_code=404,
            detail=f"No timetable data found for stop {stop_id}"
        )

    return {
        "stop_id": stop_id,
        "departures": departures,
        "data_note": "Scheduled timetable only. Not real-time. Check PTV app for live departures.",
    }


@router.get("/walk")
async def get_walk_route(
    from_lat: float = Query(description="Origin latitude"),
    from_lon: float = Query(description="Origin longitude"),
    to_lat: float = Query(description="Destination latitude"),
    to_lon: float = Query(description="Destination longitude"),
):
    """
    Returns a walking route between two points.

    Powered by OSRM (Open Source Routing Machine).
    Returns distance, duration, and plain-English turn-by-turn steps.

    Useful for:
      - Walking from home to nearest stop
      - Walking from arrival stop to event venue
    """
    result = await get_walking_route(from_lat, from_lon, to_lat, to_lon)

    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])

    return {
        "from": {"lat": from_lat, "lon": from_lon},
        "to": {"lat": to_lat, "lon": to_lon},
        **result,
    }


@router.get("/accessibility")
def get_accessibility(
    stop_id: str = Query(description="GTFS stop ID"),
    db: Session = Depends(get_db),
):
    """
    Returns detailed accessibility information for a public transport stop.

    For train stations:
      - Elevator locations (pathway_mode = Elevator)
      - Stair locations (pathway_mode = Stairs)
      - Traversal time between platforms

    For trams and buses:
      - Ground level boarding (inherently accessible)
      - is_wheelchair_accessible flag

    elderly_recommendation: plain-English accessibility summary.
    """
    result = get_stop_accessibility(db, stop_id)

    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])

    return result
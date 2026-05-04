"""
app/routers/journey_google.py
------------------------------
Epic 3 — Google Maps Journey Planning APIs.

Endpoints:
  GET /api/journey/google/plan    — single mode route
  GET /api/journey/google/routes  — multiple route alternatives
"""

import re
import httpx
from fastapi import APIRouter, Query, HTTPException
from app.config import get_settings

settings = get_settings()
router = APIRouter()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _decode_polyline_to_geojson(encoded: str) -> dict:
    points = []
    index = 0
    lat = 0
    lng = 0

    while index < len(encoded):
        result = 0
        shift = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlat = ~(result >> 1) if result & 1 else result >> 1
        lat += dlat

        result = 0
        shift = 0
        while True:
            b = ord(encoded[index]) - 63
            index += 1
            result |= (b & 0x1F) << shift
            shift += 5
            if b < 0x20:
                break
        dlng = ~(result >> 1) if result & 1 else result >> 1
        lng += dlng

        points.append([lng / 1e5, lat / 1e5])

    return {"type": "LineString", "coordinates": points}


def _duration_label(seconds: float) -> str:
    mins = round(seconds / 60)
    if mins < 60:
        return f"{mins} min"
    hours = mins // 60
    rem = mins % 60
    return f"{hours}h {rem}min"


def _strip_html(text: str) -> str:
    text = re.sub(r'<[^>]+>', ' ', text).strip()
    return re.sub(r'\s+', ' ', text)


def _parse_steps(raw_steps: list) -> list:
    """Parses Google steps into clean structured format."""
    steps = []
    for step in raw_steps:
        instruction = _strip_html(step.get("html_instructions", ""))
        step_data = {
            "instruction": instruction,
            "distance_m": step["distance"]["value"],
            "duration_secs": step["duration"]["value"],
            "distance_label": step["distance"]["text"],
            "duration_label": step["duration"]["text"],
            "travel_mode": step.get("travel_mode", "").lower(),
        }

        if step.get("travel_mode") == "TRANSIT":
            td = step.get("transit_details", {})
            line = td.get("line", {})
            step_data["transit_info"] = {
                "line_name": line.get("short_name") or line.get("name", ""),
                "line_color": line.get("color", ""),
                "vehicle_type": line.get("vehicle", {}).get("type", "").lower(),
                "vehicle_name": line.get("vehicle", {}).get("name", ""),
                "departure_stop": td.get("departure_stop", {}).get("name", ""),
                "arrival_stop": td.get("arrival_stop", {}).get("name", ""),
                "num_stops": td.get("num_stops", 0),
                "departure_time": td.get("departure_time", {}).get("text", ""),
                "arrival_time": td.get("arrival_time", {}).get("text", ""),
                "headsign": td.get("headsign", ""),
            }

        # Include sub-steps for walking legs
        if step.get("steps"):
            step_data["sub_steps"] = [
                {
                    "instruction": _strip_html(s.get("html_instructions", "")),
                    "distance_m": s["distance"]["value"],
                    "duration_secs": s["duration"]["value"],
                    "distance_label": s["distance"]["text"],
                }
                for s in step["steps"]
            ]

        steps.append(step_data)
    return steps


def _parse_route(route: dict, leg: dict, index: int, arrive_by: str | None) -> dict:
    """Parses a single Google route into structured response."""
    steps = _parse_steps(leg.get("steps", []))

    # Calculate leave_by from arrive_by
    leave_by = None
    departure_time = None
    arrival_time = None

    if leg.get("departure_time"):
        departure_time = leg["departure_time"].get("text")
    if leg.get("arrival_time"):
        arrival_time = leg["arrival_time"].get("text")

    if arrive_by and leg.get("duration"):
        from datetime import datetime, timedelta
        try:
            arrival = datetime.fromisoformat(arrive_by)
            leave_dt = arrival - timedelta(seconds=leg["duration"]["value"])
            leave_by = leave_dt.strftime("%I:%M %p").lstrip("0")
        except Exception:
            pass

    # Build legs summary for UI
    legs_summary = []
    for step in steps:
        if step["travel_mode"] == "walking":
            legs_summary.append({
                "type": "walk",
                "label": f"Walk {step['distance_label']}",
                "duration_label": step["duration_label"],
                "distance_label": step["distance_label"],
            })
        elif step["travel_mode"] == "transit":
            ti = step.get("transit_info", {})
            legs_summary.append({
                "type": "transit",
                "label": f"{ti.get('vehicle_name', 'Transit')} {ti.get('line_name', '')} towards {ti.get('headsign', '')}",
                "duration_label": step["duration_label"],
                "num_stops": ti.get("num_stops"),
                "departure_time": ti.get("departure_time"),
                "vehicle_type": ti.get("vehicle_type"),
                "line_name": ti.get("line_name"),
                "line_color": ti.get("line_color"),
            })

    # Decode geometry
    encoded = route.get("overview_polyline", {}).get("points", "")
    geometry = _decode_polyline_to_geojson(encoded) if encoded else None

    # Calculate total walking distance
    total_walk_m = sum(
        s["distance_m"] for s in steps if s["travel_mode"] == "walking"
    )

    return {
        "route_index": index,
        "summary": route.get("summary", ""),
        "total_duration_secs": leg["duration"]["value"],
        "total_duration_mins": round(leg["duration"]["value"] / 60),
        "total_duration_label": leg["duration"]["text"],
        "total_distance_label": leg["distance"]["text"],
        "total_walk_m": total_walk_m,
        "total_walk_label": f"~{total_walk_m}m walking total" if total_walk_m < 1000 else f"~{total_walk_m/1000:.1f}km walking total",
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "leave_by": leave_by,
        "warnings": [w if isinstance(w, str) else w.get("summary", "") for w in route.get("warnings", [])],
        "legs_summary": legs_summary,
        "steps": steps,
        "geometry": geometry,
        "waypoints": {
            "origin": leg["start_address"],
            "destination": leg["end_address"],
            "origin_coords": {
                "lat": leg["start_location"]["lat"],
                "lon": leg["start_location"]["lng"],
            },
            "destination_coords": {
                "lat": leg["end_location"]["lat"],
                "lon": leg["end_location"]["lng"],
            },
        },
    }


async def _call_google_directions(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    mode: str,
    arrive_by: str | None = None,
    alternatives: bool = False,
) -> dict:
    """Core Google Directions API call."""
    google_mode_map = {
        "walking": "walking",
        "cycling": "bicycling",
        "transit": "transit",
    }
    google_mode = google_mode_map.get(mode, "walking")

    url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{from_lat},{from_lon}",
        "destination": f"{to_lat},{to_lon}",
        "mode": google_mode,
        "key": settings.GOOGLE_MAPS_API_KEY,
        "region": "au",
        "language": "en",
        "alternatives": "true" if alternatives else "false",
    }

    if google_mode == "transit":
        params["transit_mode"] = "bus|subway|train|tram"
        params["transit_routing_preference"] = "fewer_transfers"

    # If arrive_by provided, pass to Google as arrival_time
    if arrive_by and google_mode == "transit":
        from datetime import datetime
        try:
            arrival_dt = datetime.fromisoformat(arrive_by)
            params["arrival_time"] = int(arrival_dt.timestamp())
        except Exception:
            pass

    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, params=params)
        r.raise_for_status()
        return r.json()


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/plan")
async def google_plan_journey(
    from_lat: float = Query(description="Origin latitude"),
    from_lon: float = Query(description="Origin longitude"),
    to_lat: float = Query(description="Destination latitude"),
    to_lon: float = Query(description="Destination longitude"),
    mode: str = Query(default="transit", description="walking | cycling | transit"),
    arrive_by: str = Query(default=None, description="Desired arrival ISO e.g. 2026-05-04T09:30:00"),
):
    """
    Single journey plan using Google Maps Directions API.
    Returns accurate walking/cycling/transit route with real PTV data.
    """
    try:
        data = await _call_google_directions(
            from_lat, from_lon, to_lat, to_lon,
            mode=mode, arrive_by=arrive_by, alternatives=False
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Google API error: {str(e)}")

    if data.get("status") != "OK":
        raise HTTPException(
            status_code=502,
            detail=f"Google Directions: {data.get('status')} — {data.get('error_message', '')}"
        )

    route = data["routes"][0]
    leg = route["legs"][0]
    parsed = _parse_route(route, leg, index=0, arrive_by=arrive_by)

    return {
        "mode": mode,
        "provider": "google",
        **parsed,
    }


@router.get("/routes")
async def google_get_routes(
    from_lat: float = Query(description="Origin latitude"),
    from_lon: float = Query(description="Origin longitude"),
    to_lat: float = Query(description="Destination latitude"),
    to_lon: float = Query(description="Destination longitude"),
    arrive_by: str = Query(default=None, description="Desired arrival ISO e.g. 2026-05-04T09:30:00"),
):
    """
    Returns multiple transit route alternatives — powers the 'Choose Your Route' UI.

    Returns up to 3 route options sorted by comfort (least walking first).
    Each route includes:
      - total duration, departure time, leave_by time
      - legs summary (walk + transit segments)
      - full step-by-step directions
      - route geometry for map display
      - warnings (delays etc.)

    Matches prototype UI: 'Most comfortable for you' + alternative routes.
    """
    try:
        data = await _call_google_directions(
            from_lat, from_lon, to_lat, to_lon,
            mode="transit", arrive_by=arrive_by, alternatives=True
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Google API error: {str(e)}")

    if data.get("status") != "OK":
        raise HTTPException(
            status_code=502,
            detail=f"Google Directions: {data.get('status')} — {data.get('error_message', '')}"
        )

    routes = []
    for i, route in enumerate(data.get("routes", [])):
        leg = route["legs"][0]
        parsed = _parse_route(route, leg, index=i, arrive_by=arrive_by)
        routes.append(parsed)

    # Sort by total walking distance — least walking = most comfortable for elderly
    routes.sort(key=lambda r: r["total_walk_m"])

    # Tag the recommended route
    if routes:
        routes[0]["recommended"] = True
        routes[0]["recommendation_label"] = "Most comfortable for you"
        for r in routes[1:]:
            r["recommended"] = False
            # Label alternatives
            if r["total_duration_mins"] < routes[0]["total_duration_mins"]:
                r["recommendation_label"] = "Faster but more walking"
            else:
                r["recommendation_label"] = "Alternative route"

    # Calculate leave_by from arrive_by for display
    leave_by_display = None
    if arrive_by and routes:
        leave_by_display = routes[0].get("leave_by")

    return {
        "provider": "google",
        "mode": "transit",
        "total_routes_found": len(routes),
        "leave_home_by": leave_by_display,
        "arrive_by": arrive_by,
        "origin": {
            "lat": from_lat,
            "lon": from_lon,
        },
        "destination": {
            "lat": to_lat,
            "lon": to_lon,
        },
        "routes": routes,
    }
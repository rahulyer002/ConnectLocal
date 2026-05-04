"""
app/services/epic_data_service.py
-----------------------------------
Database query service for Epic 3 (Journey) and Epic 4 (Resonance) APIs.
All haversine calculations are vectorised for performance.
"""

from __future__ import annotations
import math
import httpx
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.public_toilet import PublicToilet
from app.models.tree import Tree
from app.models.pedestrian_sensor import PedestrianSensor
from app.models.pedestrian_pattern import PedestrianPattern
from app.models.microclimate_sensor import MicroClimateSensor
from app.models.gtfs_stop import GtfsStop
from app.models.gtfs_pattern import GtfsPattern
from app.models.gtfs_pathway import GtfsPathway
from app.models.open_space import OpenSpace

# ─── CoM Live API base URL ────────────────────────────────────────────────────
COM_BASE = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets"

# ─── Safety thresholds for elderly users ─────────────────────────────────────
TEMP_DANGER_HIGH = 35.0    # °C — heat stress risk
TEMP_DANGER_LOW = 5.0      # °C — hypothermia risk
WIND_UNCOMFORTABLE = 40.0  # km/h
PM25_POOR = 25.0           # ug/m³ — poor air quality
HUMIDITY_HIGH = 85.0       # %

# ─── Haversine ────────────────────────────────────────────────────────────────

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 2)


# ═══════════════════════════════════════════════════════════════════════════════
# EPIC 4 — RESONANCE ENGINE
# ═══════════════════════════════════════════════════════════════════════════════

# ─── Pedestrian patterns ──────────────────────────────────────────────────────

def get_crowd_level_now(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float = 1,
) -> dict:
    now = datetime.now()
    hour = now.hour
    day_of_week = now.weekday()

    sensors = db.query(PedestrianPattern).filter(
        PedestrianPattern.hour == hour,
        PedestrianPattern.day_of_week == day_of_week,
    ).all()

    nearby = []
    for s in sensors:
        if s.lat and s.lon:
            dist = haversine_km(lat, lon, s.lat, s.lon)
            if dist <= radius_km:
                nearby.append({
                    "sensor_id": s.sensor_id,
                    "sensor_description": s.sensor_description,
                    "distance_km": dist,
                    "avg_count": s.avg_count,
                    "crowd_level": s.crowd_level,
                    "is_quiet_hour": s.is_quiet_hour,
                    "p25_count": s.p25_count,
                    "p75_count": s.p75_count,
                })

    nearby.sort(key=lambda x: x["distance_km"])

    if not nearby:
        return {
            "crowd_level": "Unknown",
            "avg_count": None,
            "is_quiet": None,
            "sensors_found": 0,
            "hour": hour,
            "day_name": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][day_of_week],
        }

    nearest = nearby[0]
    return {
        "crowd_level": nearest["crowd_level"],
        "avg_count": nearest["avg_count"],
        "is_quiet": nearest["is_quiet_hour"],
        "sensors_found": len(nearby),
        "nearest_sensor": nearest["sensor_description"],
        "nearest_sensor_distance_km": nearest["distance_km"],
        "hour": hour,
        "day_name": ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"][day_of_week],
        "all_nearby": nearby[:3],
    }


def get_crowd_forecast(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float = 0.5,
) -> list[dict]:
    sensors = db.query(PedestrianSensor).all()

    nearest_sensor = None
    nearest_dist = float("inf")
    for s in sensors:
        dist = haversine_km(lat, lon, s.lat, s.lon)
        if dist < nearest_dist and dist <= radius_km:
            nearest_dist = dist
            nearest_sensor = s

    if not nearest_sensor:
        return []

    patterns = db.query(PedestrianPattern).filter(
        PedestrianPattern.sensor_id == nearest_sensor.sensor_id
    ).order_by(
        PedestrianPattern.day_of_week,
        PedestrianPattern.hour,
    ).all()

    DAY_NAMES = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    forecast = []
    for p in patterns:
        forecast.append({
            "day_of_week": p.day_of_week,
            "day_name": p.day_name,
            "hour": p.hour,
            "avg_count": p.avg_count,
            "crowd_level": p.crowd_level,
            "is_quiet_hour": p.is_quiet_hour,
        })

    return forecast


def get_best_times(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float = 1.0,
    top_n: int = 5,
) -> list[dict]:
    sensors = db.query(PedestrianSensor).all()
    print(f"[DEBUG] Total sensors in DB: {len(sensors)}")

    nearest_sensor = None
    nearest_dist = float("inf")
    for s in sensors:
        dist = haversine_km(lat, lon, s.lat, s.lon)
        if dist < nearest_dist and dist <= radius_km:
            nearest_dist = dist
            nearest_sensor = s

    print(f"[DEBUG] Nearest sensor: {nearest_sensor.sensor_description if nearest_sensor else None}, dist: {nearest_dist}")

    if not nearest_sensor:
        print(f"[DEBUG] No sensor found within {radius_km}km")
        return []

    all_patterns = db.query(PedestrianPattern).filter(
        PedestrianPattern.sensor_id == nearest_sensor.sensor_id,
    ).all()
    print(f"[DEBUG] Total patterns for sensor {nearest_sensor.sensor_id}: {len(all_patterns)}")
    if all_patterns:
        levels = set(p.crowd_level for p in all_patterns)
        print(f"[DEBUG] Crowd levels in DB: {levels}")

    patterns = db.query(PedestrianPattern).filter(
        PedestrianPattern.sensor_id == nearest_sensor.sensor_id,
        PedestrianPattern.is_quiet_hour == True,
        PedestrianPattern.hour >= 8,
        PedestrianPattern.hour <= 20,
    ).order_by(PedestrianPattern.avg_count).limit(top_n).all()

    print(f"[DEBUG] Quiet patterns found (is_quiet_hour=True, hour 8-20): {len(patterns)}")

    if not patterns:
        patterns = db.query(PedestrianPattern).filter(
            PedestrianPattern.sensor_id == nearest_sensor.sensor_id,
            PedestrianPattern.hour >= 8,
            PedestrianPattern.hour <= 20,
        ).order_by(PedestrianPattern.avg_count).limit(top_n).all()
        print(f"[DEBUG] Fallback — lowest crowd patterns: {len(patterns)}")

    return [
        {
            "day_name": p.day_name,
            "hour": p.hour,
            "hour_label": f"{p.hour:02d}:00",
            "avg_count": p.avg_count,
            "crowd_level": p.crowd_level,
        }
        for p in patterns
    ]


# ─── Live microclimate ────────────────────────────────────────────────────────

async def get_live_microclimate(lat: float, lon: float) -> dict:
    url = "https://data.melbourne.vic.gov.au/api/explore/v2.1/catalog/datasets/microclimate-sensors-data/records"
    params = {"limit": 100}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        records = data.get("results", [])
        print(f"[DEBUG] Microclimate records returned: {len(records)}")
        if records:
            print(f"[DEBUG] First record keys: {list(records[0].keys())}")
            print(f"[DEBUG] First record: {records[0]}")

        if not records:
            return _microclimate_unavailable()

        readings = {}
        for rec in records:
            for key in rec:
                val = rec[key]
                if val is None:
                    continue
                key_lower = key.lower()
                if "temp" in key_lower and "temperature_c" not in readings:
                    try:
                        readings["TPH.TEMP"] = float(val)
                    except Exception:
                        pass
                elif "humid" in key_lower and "TPH.RH" not in readings:
                    try:
                        readings["TPH.RH"] = float(val)
                    except Exception:
                        pass
                elif "wind" in key_lower and "speed" in key_lower and "WS" not in readings:
                    try:
                        readings["WS"] = float(val)
                    except Exception:
                        pass
                elif "pm2" in key_lower and "PM2.5" not in readings:
                    try:
                        readings["PM2.5"] = float(val)
                    except Exception:
                        pass
                elif "pressure" in key_lower and "TPH.PRESSURE" not in readings:
                    try:
                        readings["TPH.PRESSURE"] = float(val)
                    except Exception:
                        pass

        print(f"[DEBUG] Parsed readings: {readings}")

        if not readings:
            return _microclimate_unavailable()

        return _parse_microclimate(readings)

    except Exception as e:
        print(f"[DEBUG] Microclimate API error: {e}")
        return _microclimate_unavailable()


def _parse_microclimate(readings: dict) -> dict:
    temp = readings.get("TPH.TEMP")
    humidity = readings.get("TPH.RH")
    wind = readings.get("WS")
    pm25 = readings.get("PM2.5")
    pressure = readings.get("TPH.PRESSURE")

    warnings = []
    if temp is not None:
        if temp > TEMP_DANGER_HIGH:
            warnings.append(f"Very hot ({temp:.1f}°C) — stay hydrated, seek shade")
        elif temp < TEMP_DANGER_LOW:
            warnings.append(f"Very cold ({temp:.1f}°C) — dress warmly")
    if wind is not None and wind > WIND_UNCOMFORTABLE:
        warnings.append(f"Strong winds ({wind:.1f} km/h) — challenging outdoors")
    if pm25 is not None and pm25 > PM25_POOR:
        warnings.append(f"Poor air quality (PM2.5: {pm25:.1f}) — consider staying indoors")
    if humidity is not None and humidity > HUMIDITY_HIGH:
        warnings.append(f"High humidity ({humidity:.1f}%) — may feel uncomfortable")

    safety_verdict = "Good" if not warnings else ("Caution" if len(warnings) == 1 else "Poor")

    return {
        "available": True,
        "temperature_c": round(temp, 1) if temp else None,
        "humidity_pct": round(humidity, 1) if humidity else None,
        "wind_speed_kmh": round(wind, 1) if wind else None,
        "pm25_ug_m3": round(pm25, 1) if pm25 else None,
        "pressure_hpa": round(pressure, 1) if pressure else None,
        "safety_verdict": safety_verdict,
        "warnings": warnings,
        "is_safe_for_elderly": safety_verdict == "Good",
    }


def _microclimate_unavailable() -> dict:
    return {
        "available": False,
        "temperature_c": None,
        "humidity_pct": None,
        "wind_speed_kmh": None,
        "pm25_ug_m3": None,
        "safety_verdict": "Unknown",
        "warnings": ["Weather data temporarily unavailable"],
        "is_safe_for_elderly": None,
    }


# ─── Resonance score ──────────────────────────────────────────────────────────

def compute_resonance_score(
    crowd_level: str | None,
    is_quiet: bool | None,
    weather: dict,
    comfort_score: float | None,
    has_toilet: bool | None,
    shade_score: float | None,
) -> dict:
    crowd_map = {"Low": 35, "Moderate": 20, "High": 5, "Unknown": 17}
    crowd_pts = crowd_map.get(crowd_level or "Unknown", 17)
    if is_quiet:
        crowd_pts = min(35, crowd_pts + 5)

    weather_map = {"Good": 35, "Caution": 20, "Poor": 5, "Unknown": 25}
    weather_pts = weather_map.get(weather.get("safety_verdict", "Unknown"), 25)

    if comfort_score is not None:
        comfort_pts = round((comfort_score / 100) * 20, 1)
    else:
        comfort_pts = 10

    toilet_pts = 5 if has_toilet else 0

    if shade_score is not None:
        shade_pts = round((min(shade_score, 100) / 100) * 5, 1)
    else:
        shade_pts = 2.5

    total = round(crowd_pts + weather_pts + comfort_pts + toilet_pts + shade_pts, 1)
    total = max(0, min(100, total))

    return {
        "resonance_score": total,
        "grade": _score_grade(total),
        "breakdown": {
            "crowd_score": crowd_pts,
            "weather_score": weather_pts,
            "comfort_score": comfort_pts,
            "toilet_score": toilet_pts,
            "shade_score": shade_pts,
        },
        "weights": {
            "crowd": "35%",
            "weather": "35%",
            "comfort": "20%",
            "toilet": "5%",
            "shade": "5%",
        }
    }


def _score_grade(score: float) -> str:
    if score >= 80:
        return "Excellent"
    elif score >= 60:
        return "Good"
    elif score >= 40:
        return "Fair"
    else:
        return "Poor"


# ─── Green spaces ─────────────────────────────────────────────────────────────

def get_green_spaces_nearby(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float = 2.0,
    has_toilet: bool | None = None,
    limit: int = 10,
) -> list[dict]:
    query = db.query(OpenSpace)
    if has_toilet is not None:
        query = query.filter(OpenSpace.has_toilet_nearby == has_toilet)

    spaces = query.all()

    results = []
    for s in spaces:
        dist = haversine_km(lat, lon, s.lat, s.lng)
        if dist <= radius_km:
            results.append({
                "space_id": s.space_id,
                "space_name": s.space_name,
                "space_type": s.space_type,
                "category": s.category,
                "lat": s.lat,
                "lon": s.lng,
                "distance_km": dist,
                "comfort_score": s.comfort_score,
                "walkability_score": round(s.walkability_score, 4) if s.walkability_score else None,
                "has_toilet_nearby": s.has_toilet_nearby,
                "public_access": s.public_access,
                "managed_by": s.managed_by,
            })

    results.sort(key=lambda x: (x.get("comfort_score") or 0), reverse=True)
    return results[:limit]


def get_nearby_toilets(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float = 0.5,
    wheelchair_only: bool = False,
) -> list[dict]:
    query = db.query(PublicToilet)
    if wheelchair_only:
        query = query.filter(PublicToilet.has_wheelchair == True)

    toilets = query.all()
    results = []
    for t in toilets:
        dist = haversine_km(lat, lon, t.lat, t.lon)
        if dist <= radius_km:
            results.append({
                "toilet_id": t.toilet_id,
                "name": t.name,
                "lat": t.lat,
                "lon": t.lon,
                "distance_km": dist,
                "has_wheelchair": t.has_wheelchair,
                "has_female": t.has_female,
                "has_male": t.has_male,
                "has_baby_facility": t.has_baby_facility,
                "suburb_name": t.suburb_name,
            })

    results.sort(key=lambda x: x["distance_km"])
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# EPIC 3 — JOURNEY PLANNER
# ═══════════════════════════════════════════════════════════════════════════════

def get_stops_nearby(
    db: Session,
    lat: float,
    lon: float,
    radius_km: float = 0.5,
    mode: str | None = None,
    wheelchair_only: bool = False,
    limit: int = 10,
) -> list[dict]:
    query = db.query(GtfsStop)
    if mode:
        query = query.filter(GtfsStop.mode == mode.lower())
    if wheelchair_only:
        query = query.filter(GtfsStop.is_wheelchair_accessible == True)

    stops = query.all()
    results = []

    for s in stops:
        if not s.lat or not s.lon:
            continue
        dist = haversine_km(lat, lon, s.lat, s.lon)
        if dist <= radius_km:
            results.append({
                "stop_id": s.stop_id,
                "stop_name": s.stop_name,
                "mode": s.mode,
                "lat": s.lat,
                "lon": s.lon,
                "distance_km": dist,
                "is_wheelchair_accessible": s.is_wheelchair_accessible,
                "routes_served": s.routes_served,
                "route_count": s.route_count,
                "suburb_name": s.suburb_name,
            })

    results.sort(key=lambda x: x["distance_km"])
    return results[:limit]


def get_stop_departures(
    db: Session,
    stop_id: str,
    hour: int | None = None,
) -> list[dict]:
    if hour is None:
        hour = datetime.now().hour

    patterns = db.query(GtfsPattern).filter(
        GtfsPattern.stop_id == stop_id,
        GtfsPattern.hour == hour,
    ).all()

    if not patterns:
        patterns = db.query(GtfsPattern).filter(
            GtfsPattern.stop_id == stop_id,
            GtfsPattern.hour >= hour,
            GtfsPattern.hour <= hour + 3,
        ).order_by(GtfsPattern.hour).all()

    return [
        {
            "stop_id": p.stop_id,
            "hour": p.hour,
            "hour_label": f"{p.hour:02d}:00",
            "mode": p.mode,
            "avg_departures_per_hour": p.avg_departures_per_hour,
            "frequency_mins": round(60 / p.avg_departures_per_hour, 0) if p.avg_departures_per_hour > 0 else None,
        }
        for p in patterns
    ]


def get_stop_accessibility(
    db: Session,
    stop_id: str,
) -> dict:
    stop = db.query(GtfsStop).filter(GtfsStop.stop_id == stop_id).first()
    if not stop:
        return {"error": "Stop not found"}

    pathways = db.query(GtfsPathway).filter(
        GtfsPathway.from_stop_id == stop_id
    ).all()

    has_elevator = any(p.has_elevator for p in pathways)
    has_stairs_only = any(p.has_stairs for p in pathways) and not has_elevator

    return {
        "stop_id": stop.stop_id,
        "stop_name": stop.stop_name,
        "mode": stop.mode,
        "wheelchair_boarding": stop.wheelchair_boarding,
        "is_wheelchair_accessible": stop.is_wheelchair_accessible,
        "has_elevator": has_elevator,
        "has_stairs_only": has_stairs_only,
        "pathway_count": len(pathways),
        "pathways": [
            {
                "pathway_id": p.pathway_id,
                "to_stop_id": p.to_stop_id,
                "mode": p.pathway_mode_label,
                "has_elevator": p.has_elevator,
                "has_stairs": p.has_stairs,
                "traversal_time_secs": p.traversal_time,
            }
            for p in pathways
        ],
        "elderly_recommendation": (
            "Accessible — elevator available" if has_elevator
            else "Stairs only — may be difficult" if has_stairs_only
            else "Ground level — accessible" if stop.mode in ("tram", "bus")
            else "Check accessibility on arrival"
        ),
    }


async def get_walking_route(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
) -> dict:
    url = f"http://router.project-osrm.org/route/v1/walking/{from_lon},{from_lat};{to_lon},{to_lat}"
    params = {
        "overview": "false",
        "steps": "true",
        "annotations": "false",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            return {"error": "No walking route found"}

        route = data["routes"][0]
        leg = route["legs"][0]

        steps = []
        for step in leg.get("steps", []):
            maneuver = step.get("maneuver", {})
            if step.get("distance", 0) < 1:
                continue
            steps.append({
                "instruction": _maneuver_to_text(
                    maneuver.get("type", ""),
                    maneuver.get("modifier", ""),
                    step.get("name", ""),
                ),
                "distance_m": round(step["distance"]),
                "duration_secs": round(step["duration"]),
                "street_name": step.get("name", ""),
            })

        return {
            "distance_m": round(route["distance"]),
            "distance_label": _distance_label(route["distance"]),
            "duration_secs": round(route["duration"]),
            "duration_label": _duration_label(route["duration"]),
            "steps": steps,
        }

    except Exception as e:
        return {"error": f"Walking route unavailable: {str(e)}"}


def _maneuver_to_text(mtype: str, modifier: str, name: str) -> str:
    street = f" onto {name}" if name else ""
    if mtype == "depart":
        return f"Head {modifier}{street}"
    elif mtype == "turn":
        return f"Turn {modifier}{street}"
    elif mtype == "arrive":
        return "Arrive at your destination"
    elif mtype == "continue":
        return f"Continue{street}"
    elif mtype == "roundabout":
        return f"At the roundabout, take exit{street}"
    else:
        return f"Continue{street}"


def _distance_label(metres: float) -> str:
    if metres < 1000:
        return f"{round(metres)}m"
    return f"{metres/1000:.1f}km"


def _duration_label(seconds: float) -> str:
    mins = round(seconds / 60)
    if mins < 60:
        return f"{mins} min"
    hours = mins // 60
    rem = mins % 60
    return f"{hours}h {rem}min"


async def plan_journey(
    db: Session,
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    arrive_by: str | None = None,
    mode: str = "walking",
) -> dict:
    """
    Returns a single journey option based on requested mode.
    mode: walking | cycling | transit
    """

    if mode == "walking":
        walk_direct = await _get_route_osrm(from_lat, from_lon, to_lat, to_lon, mode="walking")
        walk_mins = round(walk_direct.get("duration_secs", 0) / 60)
        return {
            "mode": "walking",
            "label": "Walk",
            "total_duration_mins": walk_mins,
            "total_duration_label": _duration_label(walk_direct.get("duration_secs", 0)),
            "legs": [{
                "type": "walk",
                "description": "Walk to destination",
                "duration_mins": walk_mins,
                "distance_label": walk_direct.get("distance_label"),
                "geometry": walk_direct.get("geometry"),
                "steps": walk_direct.get("steps", []),
            }],
            "geometry_collection": {
                "type": "GeometryCollection",
                "geometries": [walk_direct["geometry"]] if walk_direct.get("geometry") else [],
            },
            "waypoints": {
                "origin": {"lat": from_lat, "lon": from_lon},
                "destination": {"lat": to_lat, "lon": to_lon},
            },
            "note": "Walking times are approximate. Powered by OSRM.",
        }

    elif mode == "cycling":
        bike_direct = await _get_route_osrm(from_lat, from_lon, to_lat, to_lon, mode="cycling")
        bike_mins = round(bike_direct.get("duration_secs", 0) / 60)
        return {
            "mode": "cycling",
            "label": "Cycle",
            "total_duration_mins": bike_mins,
            "total_duration_label": _duration_label(bike_direct.get("duration_secs", 0)),
            "legs": [{
                "type": "cycle",
                "description": "Cycle to destination",
                "duration_mins": bike_mins,
                "distance_label": bike_direct.get("distance_label"),
                "geometry": bike_direct.get("geometry"),
                "steps": bike_direct.get("steps", []),
            }],
            "geometry_collection": {
                "type": "GeometryCollection",
                "geometries": [bike_direct["geometry"]] if bike_direct.get("geometry") else [],
            },
            "waypoints": {
                "origin": {"lat": from_lat, "lon": from_lon},
                "destination": {"lat": to_lat, "lon": to_lon},
            },
            "note": "Cycling times are approximate. Powered by OSRM.",
        }

    else:  # transit
        origin_stops = get_stops_nearby(db, from_lat, from_lon, radius_km=0.5, limit=5)
        dest_stops = get_stops_nearby(db, to_lat, to_lon, radius_km=0.5, limit=5)

        if not origin_stops or not dest_stops:
            return {
                "mode": "transit",
                "error": "No nearby stops found. Try walking or cycling instead.",
            }

        origin_stop = origin_stops[0]
        dest_stop = dest_stops[0]

        walk_to_stop = await _get_route_osrm(
            from_lat, from_lon,
            origin_stop["lat"], origin_stop["lon"],
            mode="walking"
        )
        walk_to_venue = await _get_route_osrm(
            dest_stop["lat"], dest_stop["lon"],
            to_lat, to_lon,
            mode="walking"
        )

        now = datetime.now()
        departures = get_stop_departures(db, origin_stop["stop_id"], hour=now.hour)
        freq_mins = departures[0]["frequency_mins"] if departures else 15
        wait_mins = round(freq_mins / 2) if freq_mins else 8

        walk_to_stop_mins = round(walk_to_stop.get("duration_secs", 0) / 60)
        walk_to_venue_mins = round(walk_to_venue.get("duration_secs", 0) / 60)
        transit_dist_km = haversine_km(
            origin_stop["lat"], origin_stop["lon"],
            dest_stop["lat"], dest_stop["lon"]
        )
        transit_mins = max(5, round(transit_dist_km * 3))
        total_mins = walk_to_stop_mins + wait_mins + transit_mins + walk_to_venue_mins

        leave_by = None
        if arrive_by:
            try:
                from datetime import timedelta
                arrival = datetime.fromisoformat(arrive_by)
                leave_dt = arrival - timedelta(minutes=total_mins + 10)
                leave_by = leave_dt.strftime("%H:%M")
            except Exception:
                pass

        transit_geometry = {
            "type": "LineString",
            "coordinates": [
                [origin_stop["lon"], origin_stop["lat"]],
                [dest_stop["lon"], dest_stop["lat"]],
            ]
        }

        all_geometries = []
        if walk_to_stop.get("geometry"):
            all_geometries.append(walk_to_stop["geometry"])
        all_geometries.append(transit_geometry)
        if walk_to_venue.get("geometry"):
            all_geometries.append(walk_to_venue["geometry"])

        return {
            "mode": "transit",
            "label": "Public Transport",
            "total_duration_mins": total_mins,
            "total_duration_label": _duration_label(total_mins * 60),
            "leave_by": leave_by,
            "legs": [
                {
                    "type": "walk",
                    "description": f"Walk to {origin_stop['stop_name']}",
                    "duration_mins": walk_to_stop_mins,
                    "distance_label": walk_to_stop.get("distance_label"),
                    "geometry": walk_to_stop.get("geometry"),
                    "steps": walk_to_stop.get("steps", []),
                    "stop": origin_stop,
                },
                {
                    "type": "wait",
                    "description": f"Wait at {origin_stop['stop_name']}",
                    "duration_mins": wait_mins,
                    "mode": origin_stop.get("mode", "transit"),
                    "routes": origin_stop.get("routes_served", ""),
                    "departures": departures[:3],
                    "wheelchair_accessible": origin_stop.get("is_wheelchair_accessible"),
                    "geometry": None,
                },
                {
                    "type": "transit",
                    "description": f"Take {origin_stop.get('mode','transit')} to {dest_stop['stop_name']}",
                    "duration_mins": transit_mins,
                    "from_stop": origin_stop["stop_name"],
                    "to_stop": dest_stop["stop_name"],
                    "from_stop_coords": {"lat": origin_stop["lat"], "lon": origin_stop["lon"]},
                    "to_stop_coords": {"lat": dest_stop["lat"], "lon": dest_stop["lon"]},
                    "routes": origin_stop.get("routes_served", ""),
                    "geometry": transit_geometry,
                },
                {
                    "type": "walk",
                    "description": "Walk to destination",
                    "duration_mins": walk_to_venue_mins,
                    "distance_label": walk_to_venue.get("distance_label"),
                    "geometry": walk_to_venue.get("geometry"),
                    "steps": walk_to_venue.get("steps", []),
                },
            ],
            "geometry_collection": {
                "type": "GeometryCollection",
                "geometries": all_geometries,
            },
            "waypoints": {
                "origin": {"lat": from_lat, "lon": from_lon},
                "boarding_stop": {"lat": origin_stop["lat"], "lon": origin_stop["lon"], "name": origin_stop["stop_name"]},
                "alighting_stop": {"lat": dest_stop["lat"], "lon": dest_stop["lon"], "name": dest_stop["stop_name"]},
                "destination": {"lat": to_lat, "lon": to_lon},
            },
            "accessibility": {
                "origin_stop_accessible": origin_stop.get("is_wheelchair_accessible"),
                "dest_stop_accessible": dest_stop.get("is_wheelchair_accessible"),
            },
            "note": "Transit times are estimates from scheduled timetables. Not real-time.",
        }


async def _get_route_osrm(
    from_lat: float,
    from_lon: float,
    to_lat: float,
    to_lon: float,
    mode: str = "walking",
) -> dict:
    url = f"http://router.project-osrm.org/route/v1/{mode}/{from_lon},{from_lat};{to_lon},{to_lat}"
    params = {
        "overview": "full",
        "steps": "true",
        "annotations": "false",
        "geometries": "geojson",
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            return {"error": f"No {mode} route found"}

        route = data["routes"][0]
        leg = route["legs"][0]
        geometry = route.get("geometry")

        steps = []
        for step in leg.get("steps", []):
            maneuver = step.get("maneuver", {})
            if step.get("distance", 0) < 1:
                continue
            steps.append({
                "instruction": _maneuver_to_text(
                    maneuver.get("type", ""),
                    maneuver.get("modifier", ""),
                    step.get("name", ""),
                ),
                "distance_m": round(step["distance"]),
                "duration_secs": round(step["duration"]),
                "street_name": step.get("name", ""),
            })

        return {
            "distance_m": round(route["distance"]),
            "distance_label": _distance_label(route["distance"]),
            "duration_secs": round(route["duration"]),
            "duration_label": _duration_label(route["duration"]),
            "geometry": geometry,
            "steps": steps,
        }

    except Exception as e:
        return {"error": f"{mode} route unavailable: {str(e)}"}


async def get_walking_route(from_lat, from_lon, to_lat, to_lon) -> dict:
    return await _get_route_osrm(from_lat, from_lon, to_lat, to_lon, mode="walking")
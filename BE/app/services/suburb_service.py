"""
Suburb-centric composition service.

Powers:
  - /api/suburbs/map                       Layer 1, hex-map paint
  - /api/suburbs/{id}/snapshot             Layer 2, one-tap every-signal
  - /api/suburbs/{id}/<drill-down>         Layer 3, per-domain detail
  - /api/suburbs/compare                   cross-suburb summary

Every helper accepts a suburb_id and returns a JSON-ready dict.
"""
from __future__ import annotations
import asyncio
import datetime
from collections import Counter
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.suburb import Suburb
from app.models.landmark import Landmark
from app.models.open_space import OpenSpace
from app.models.pedestrian_pattern import PedestrianPattern
from app.models.gtfs_stop import GtfsStop
from app.models.gtfs_route import GtfsRoute
from app.models.tree import Tree
from app.models.osm_bench import OsmBench
from app.models.osm_accessible_toilet import OsmAccessibleToilet
from app.models.osm_wheelchair_place import OsmWheelchairPlace
from app.services import open_meteo
from app.services import eventfinda

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Map upstream crowd labels to the 4-band UI scheme shown in the Epic 6 mock
UI_LEVEL_MAP = {
    "Low": "Very Quiet",
    "Quiet": "Quiet",
    "Moderate": "Moderate",
    "High": "Busy",
    "Busy": "Busy",
}


def _resolve_suburb(db: Session, suburb_id: int) -> Suburb | None:
    return db.query(Suburb).filter(Suburb.suburb_id == suburb_id).first()


# ─── Pedestrian / crowd ───────────────────────────────────────────────────────

def get_pedestrian_signal(db: Session, suburb_id: int) -> dict:
    """
    Current crowd level + trend for a suburb.
    Aggregates pedestrian_pattern across all sensors with this suburb_id.
    """
    now = datetime.datetime.now()
    hour = now.hour
    dow = now.weekday()

    cur = db.query(PedestrianPattern).filter(
        PedestrianPattern.suburb_id == suburb_id,
        PedestrianPattern.day_of_week == dow,
        PedestrianPattern.hour == hour,
    ).all()

    if not cur:
        return {
            "available": False,
            "people_per_hour": None,
            "crowd_level": None,
            "trend": None,
            "sensors_count": 0,
            "hour": hour,
            "day": DAY_NAMES[dow],
        }

    cur_avg = sum((r.avg_count or 0) for r in cur) / len(cur)

    # Trend — compare previous hour's same-day-of-week avg
    prev_hour = (hour - 1) % 24
    prev = db.query(PedestrianPattern).filter(
        PedestrianPattern.suburb_id == suburb_id,
        PedestrianPattern.day_of_week == dow,
        PedestrianPattern.hour == prev_hour,
    ).all()
    prev_avg = (sum((r.avg_count or 0) for r in prev) / len(prev)) if prev else cur_avg

    ratio = (cur_avg / prev_avg) if prev_avg > 0 else 1.0
    if ratio > 1.2:
        trend = "Getting busier"
    elif ratio < 0.8:
        trend = "Getting quieter"
    else:
        trend = "Steady"

    # Crowd level — most common upstream label among current-hour sensors
    labels = [r.crowd_level for r in cur if r.crowd_level]
    raw_level = Counter(labels).most_common(1)[0][0] if labels else None
    ui_level = UI_LEVEL_MAP.get(raw_level, raw_level)

    return {
        "available": True,
        "people_per_hour": round(cur_avg),
        "crowd_level": ui_level,
        "raw_crowd_label": raw_level,
        "trend": trend,
        "sensors_count": len(cur),
        "hour": hour,
        "day": DAY_NAMES[dow],
    }


def get_best_times_for_suburb(db: Session, suburb_id: int, top_n: int = 5) -> list[dict]:
    """Quietest hours in the suburb between 8am-8pm (elderly-friendly window)."""
    rows = db.query(PedestrianPattern).filter(
        PedestrianPattern.suburb_id == suburb_id,
        PedestrianPattern.is_quiet_hour == True,  # noqa: E712
        PedestrianPattern.hour >= 8,
        PedestrianPattern.hour <= 20,
    ).order_by(PedestrianPattern.avg_count).limit(top_n).all()

    # Fallback: lowest-count hours regardless of quiet-flag
    if not rows:
        rows = db.query(PedestrianPattern).filter(
            PedestrianPattern.suburb_id == suburb_id,
            PedestrianPattern.hour >= 8,
            PedestrianPattern.hour <= 20,
        ).order_by(PedestrianPattern.avg_count).limit(top_n).all()

    return [
        {
            "day": p.day_name,
            "hour": p.hour,
            "hour_label": f"{p.hour:02d}:00",
            "avg_people_per_hour": round(p.avg_count) if p.avg_count else None,
            "crowd_level": p.crowd_level,
        }
        for p in rows
    ]


# ─── Accessibility (OSM) ──────────────────────────────────────────────────────

def get_accessibility_summary_for_suburb(db: Session, suburb_id: int, sample_limit: int = 5) -> dict:
    bench_count = db.query(OsmBench).filter(OsmBench.suburb_id == suburb_id).count()
    toilet_count = db.query(OsmAccessibleToilet).filter(OsmAccessibleToilet.suburb_id == suburb_id).count()
    place_count = db.query(OsmWheelchairPlace).filter(OsmWheelchairPlace.suburb_id == suburb_id).count()

    cats = db.query(
        OsmWheelchairPlace.amenity_category,
        func.count(OsmWheelchairPlace.osm_id),
    ).filter(
        OsmWheelchairPlace.suburb_id == suburb_id
    ).group_by(OsmWheelchairPlace.amenity_category).all()
    places_by_category = {(cat or "other"): cnt for cat, cnt in cats}

    sample_places = db.query(OsmWheelchairPlace).filter(
        OsmWheelchairPlace.suburb_id == suburb_id,
        OsmWheelchairPlace.name.isnot(None),
        OsmWheelchairPlace.amenity.isnot(None),
    ).limit(sample_limit).all()

    sample_toilets = db.query(OsmAccessibleToilet).filter(
        OsmAccessibleToilet.suburb_id == suburb_id,
    ).limit(sample_limit).all()

    return {
        "benches": bench_count,
        "accessible_toilets": toilet_count,
        "wheelchair_places": place_count,
        "places_by_category": places_by_category,
        "sample_places": [
            {
                "osm_id": p.osm_id, "name": p.name, "amenity": p.amenity,
                "category": p.amenity_category, "wheelchair": p.wheelchair,
                "operator": p.operator, "lat": p.lat, "lon": p.lon,
            }
            for p in sample_places
        ],
        "sample_toilets": [
            {
                "osm_id": t.osm_id, "name": t.name, "wheelchair": t.wheelchair,
                "opening_hours": t.opening_hours, "operator": t.operator,
                "lat": t.lat, "lon": t.lon,
            }
            for t in sample_toilets
        ],
    }


# ─── Transport ────────────────────────────────────────────────────────────────

def get_transport_summary_for_suburb(db: Session, suburb_id: int) -> dict:
    stops = db.query(GtfsStop).filter(GtfsStop.suburb_id == suburb_id).all()

    by_mode: dict[str, int] = {}
    wheelchair_count = 0
    routes_seen: set[str] = set()

    for s in stops:
        m = s.mode or "unknown"
        by_mode[m] = by_mode.get(m, 0) + 1
        if s.is_wheelchair_accessible:
            wheelchair_count += 1
        if s.routes_served:
            for token in s.routes_served.split(","):
                token = token.strip()
                if token:
                    routes_seen.add(token)

    route_meta = []
    if routes_seen:
        rows = db.query(GtfsRoute).filter(GtfsRoute.route_short_name.in_(routes_seen)).all()
        route_meta = [
            {
                "short_name": r.route_short_name,
                "long_name": r.route_long_name,
                "mode": r.mode,
                "color_hex": f"#{r.route_color}" if r.route_color else None,
                "text_color_hex": f"#{r.route_text_color}" if r.route_text_color else None,
            }
            for r in rows
        ]

    return {
        "total_stops": len(stops),
        "by_mode": by_mode,
        "wheelchair_accessible_stops": wheelchair_count,
        "wheelchair_accessibility_pct": round(100 * wheelchair_count / len(stops), 1) if stops else 0,
        "routes_count": len(routes_seen),
        "routes": route_meta,
    }


# ─── Green spaces ─────────────────────────────────────────────────────────────

def get_green_spaces_for_suburb(db: Session, suburb_id: int) -> dict:
    spaces = db.query(OpenSpace).filter(OpenSpace.suburb_id == suburb_id).all()

    with_toilet = sum(1 for s in spaces if s.has_toilet_nearby)
    shade_scores = [s.shade_score_100 for s in spaces if s.shade_score_100 is not None]
    avg_shade = round(sum(shade_scores) / len(shade_scores), 1) if shade_scores else None

    items = [
        {
            "space_id": s.space_id,
            "space_name": s.space_name,
            "space_type": s.space_type,
            "category": s.category,
            "lat": s.lat,
            "lng": s.lng,
            "comfort_score": s.comfort_score,
            "shade_score_100": s.shade_score_100,
            "nearby_tree_count": s.nearby_tree_count,
            "has_toilet_nearby": s.has_toilet_nearby,
            "managed_by": s.managed_by,
        }
        for s in spaces
    ]
    return {
        "total": len(spaces),
        "with_toilet": with_toilet,
        "avg_shade_score": avg_shade,
        "spaces": items,
    }


# ─── Landmarks ────────────────────────────────────────────────────────────────

def get_landmarks_for_suburb(db: Session, suburb_id: int, limit: int | None = None) -> list[dict]:
    q = db.query(Landmark).filter(Landmark.suburb_id == suburb_id)
    if limit:
        q = q.limit(limit)
    rows = q.all()
    return [
        {
            "landmark_id": r.landmark_id,
            "name": r.name,
            "theme": r.theme,
            "sub_theme": r.sub_theme,
            "is_welcoming_space": r.is_welcoming_space,
            "lat": r.lat,
            "lng": r.lng,
        }
        for r in rows
    ]


# ─── Trees ────────────────────────────────────────────────────────────────────

def get_trees_for_suburb(db: Session, suburb_id: int) -> dict:
    total = db.query(Tree).filter(Tree.suburb_id == suburb_id).count()
    if total == 0:
        return {"total": 0, "top_species": [], "avg_shade_score": None, "in_parks": 0, "in_streets": 0}

    top = db.query(
        Tree.common_name, func.count(Tree.tree_id).label("c")
    ).filter(
        Tree.suburb_id == suburb_id,
        Tree.common_name.isnot(None),
    ).group_by(Tree.common_name).order_by(desc("c")).limit(5).all()

    avg_shade = db.query(func.avg(Tree.shade_score)).filter(
        Tree.suburb_id == suburb_id
    ).scalar()

    in_park = db.query(Tree).filter(
        Tree.suburb_id == suburb_id, Tree.located_in == "Park"
    ).count()
    in_street = db.query(Tree).filter(
        Tree.suburb_id == suburb_id, Tree.located_in == "Street"
    ).count()

    return {
        "total": total,
        "in_parks": in_park,
        "in_streets": in_street,
        "top_species": [{"common_name": n, "count": c} for n, c in top],
        "avg_shade_score": round(avg_shade, 5) if avg_shade else None,
    }


# ─── Demographics (already on Suburb row) ─────────────────────────────────────

def get_demographics(suburb: Suburb) -> dict:
    elderly_total = (
        (suburb.population_65_74 or 0)
        + (suburb.population_75_84 or 0)
        + (suburb.population_85_plus or 0)
    )
    elderly_pct = (
        round(100 * elderly_total / suburb.population_total, 1)
        if suburb.population_total else None
    )
    return {
        "population_total": suburb.population_total,
        "population_65_74": suburb.population_65_74,
        "population_75_84": suburb.population_75_84,
        "population_85_plus": suburb.population_85_plus,
        "elderly_total": elderly_total,
        "elderly_pct": elderly_pct,
        "need_assistance": suburb.need_assistance,
    }


# ─── Events (external, async) ─────────────────────────────────────────────────

async def get_events_for_suburb(suburb_name: str, lat: float, lng: float, rows: int = 5) -> list[dict]:
    """Wraps the existing Eventfinda integration with suburb context."""
    try:
        data = await eventfinda.search_events(
            suburb=suburb_name,
            user_lat=lat,
            user_lon=lng,
            radius_km=3,
            rows=rows,
        )
        return (data or {}).get("events", [])
    except Exception as e:
        print(f"[suburb_service] eventfinda error for {suburb_name}: {e}")
        return []


# ─── THE SNAPSHOT — composes everything above ─────────────────────────────────

async def get_suburb_snapshot(db: Session, suburb_id: int) -> dict | None:
    suburb = _resolve_suburb(db, suburb_id)
    if not suburb:
        return None

    # Run async tasks concurrently — weather + events
    weather_task = open_meteo.get_weather(suburb.centroid_lat, suburb.centroid_lng)
    events_task = get_events_for_suburb(
        suburb.suburb_name, suburb.centroid_lat, suburb.centroid_lng, rows=5
    )
    weather, events = await asyncio.gather(weather_task, events_task)
    weather_summary = open_meteo.summarize_weather(weather)

    # DB queries are quick (all indexed by suburb_id)
    pedestrian = get_pedestrian_signal(db, suburb_id)
    accessibility = get_accessibility_summary_for_suburb(db, suburb_id, sample_limit=3)
    transport = get_transport_summary_for_suburb(db, suburb_id)
    green_spaces = get_green_spaces_for_suburb(db, suburb_id)
    landmarks = get_landmarks_for_suburb(db, suburb_id, limit=10)
    trees = get_trees_for_suburb(db, suburb_id)
    demographics = get_demographics(suburb)

    return {
        "suburb_id": suburb.suburb_id,
        "suburb_name": suburb.suburb_name,
        "centroid": {"lat": suburb.centroid_lat, "lng": suburb.centroid_lng},
        "generated_at": datetime.datetime.now().isoformat(),
        "crowd": pedestrian,
        "weather": {**weather, **weather_summary},
        "events": {"total": len(events), "items": events},
        "accessibility": accessibility,
        "transport": transport,
        "green_spaces": green_spaces,
        "landmarks": {"total": len(landmarks), "items": landmarks},
        "trees": trees,
        "demographics": demographics,
        "actions": {
            "find_events_url": f"/discover?suburb_id={suburb.suburb_id}",
            "plan_journey_url": (
                f"/journey?to_lat={suburb.centroid_lat}"
                f"&to_lng={suburb.centroid_lng}&to_name={suburb.suburb_name}"
            ),
            "best_times_url": f"/best-time/week?suburb_id={suburb.suburb_id}",
        },
    }


# ─── MAP PAINT — Layer 1 ──────────────────────────────────────────────────────

def get_map_crowd_levels(db: Session) -> list[dict]:
    """
    Returns crowd_level for ALL suburbs in one call — paints the hex map.
    Suburbs without sensor coverage get crowd_level=null + has_live_data=False.
    """
    now = datetime.datetime.now()
    hour = now.hour
    dow = now.weekday()

    rows = db.query(
        PedestrianPattern.suburb_id,
        func.avg(PedestrianPattern.avg_count).label("avg_count"),
        func.count(PedestrianPattern.id).label("sensor_count"),
    ).filter(
        PedestrianPattern.day_of_week == dow,
        PedestrianPattern.hour == hour,
        PedestrianPattern.suburb_id.isnot(None),
    ).group_by(PedestrianPattern.suburb_id).all()

    crowd_by_suburb = {r.suburb_id: (r.avg_count or 0, r.sensor_count) for r in rows}

    suburbs = db.query(Suburb).all()
    items = []
    for s in suburbs:
        if s.suburb_id in crowd_by_suburb:
            avg_c, sens_n = crowd_by_suburb[s.suburb_id]
            if avg_c < 100:
                level = "Very Quiet"
            elif avg_c < 500:
                level = "Quiet"
            elif avg_c < 1500:
                level = "Moderate"
            else:
                level = "Busy"
            items.append({
                "suburb_id": s.suburb_id,
                "suburb_name": s.suburb_name,
                "centroid_lat": s.centroid_lat,
                "centroid_lng": s.centroid_lng,
                "crowd_level": level,
                "people_per_hour": round(avg_c),
                "sensor_count": sens_n,
                "has_live_data": True,
            })
        else:
            items.append({
                "suburb_id": s.suburb_id,
                "suburb_name": s.suburb_name,
                "centroid_lat": s.centroid_lat,
                "centroid_lng": s.centroid_lng,
                "crowd_level": None,
                "people_per_hour": None,
                "sensor_count": 0,
                "has_live_data": False,
            })
    return items


def get_all_benches_for_suburb(db: Session, suburb_id: int) -> dict:
    rows = db.query(OsmBench).filter(OsmBench.suburb_id == suburb_id).all()
    return {
        "suburb_id": suburb_id,
        "total": len(rows),
        "benches": [
            {"osm_id": b.osm_id, "name": b.name, "lat": b.lat, "lon": b.lon}
            for b in rows
        ],
    }


def get_all_toilets_for_suburb(db: Session, suburb_id: int) -> dict:
    rows = db.query(OsmAccessibleToilet).filter(
        OsmAccessibleToilet.suburb_id == suburb_id
    ).all()
    return {
        "suburb_id": suburb_id,
        "total": len(rows),
        "toilets": [
            {
                "osm_id": t.osm_id,
                "name": t.name,
                "wheelchair": t.wheelchair,
                "opening_hours": t.opening_hours,
                "operator": t.operator,
                "lat": t.lat,
                "lon": t.lon,
            }
            for t in rows
        ],
    }


def get_all_wheelchair_places_for_suburb(
    db: Session, suburb_id: int, category: str | None = None
) -> dict:
    q = db.query(OsmWheelchairPlace).filter(OsmWheelchairPlace.suburb_id == suburb_id)
    if category:
        q = q.filter(OsmWheelchairPlace.amenity_category == category.lower())
    rows = q.all()
    return {
        "suburb_id": suburb_id,
        "category_filter": category,
        "total": len(rows),
        "places": [
            {
                "osm_id": p.osm_id,
                "name": p.name,
                "amenity": p.amenity,
                "category": p.amenity_category,
                "wheelchair": p.wheelchair,
                "operator": p.operator,
                "opening_hours": p.opening_hours,
                "lat": p.lat,
                "lon": p.lon,
            }
            for p in rows
        ],
    }


def get_all_stops_for_suburb(
    db: Session, suburb_id: int, mode: str | None = None
) -> dict:
    q = db.query(GtfsStop).filter(GtfsStop.suburb_id == suburb_id)
    if mode:
        q = q.filter(GtfsStop.mode == mode.lower())
    rows = q.all()
    return {
        "suburb_id": suburb_id,
        "mode_filter": mode,
        "total": len(rows),
        "stops": [
            {
                "stop_id": s.stop_id,
                "stop_name": s.stop_name,
                "mode": s.mode,
                "is_wheelchair_accessible": s.is_wheelchair_accessible,
                "routes_served": s.routes_served,
                "route_count": s.route_count,
                "lat": s.lat,
                "lon": s.lon,
            }
            for s in rows
        ],
    }
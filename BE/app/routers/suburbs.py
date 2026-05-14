"""
Suburb-centric APIs powering Epic 6 (Suburb Explorer hex map).

Layer 1 — /api/suburbs/map           — all suburbs with current crowd level
Layer 2 — /api/suburbs/{id}/snapshot — one-tap every-signal
Layer 3 — /api/suburbs/{id}/<sub>    — drill-down per domain (also standalone)
Compare — /api/suburbs/compare       — cross-suburb summary

Preserved from previous version:
  /profile  /search  /psychological-distress
"""
from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.suburb import Suburb
from app.models.psychological_distress import PsychologicalDistress
from app.services import data_service
from app.services import suburb_service
from app.services import open_meteo

router = APIRouter()


# ─── Existing endpoints (preserved) ──────────────────────────────────────────

@router.get("/profile")
def get_suburb_profile(
    suburb: str = Query(description="Suburb name e.g. fitzroy, carlton"),
    db: Session = Depends(get_db),
):
    """Demographic profile for a suburb."""
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
    """Search suburbs by name. Used for autocomplete in location input."""
    results = data_service.search_suburbs(db, q, limit)
    return {"total": len(results), "suburbs": results}


@router.get("/psychological-distress")
def get_psychological_distress(db: Session = Depends(get_db)):
    """Psychological distress rates by age group (ABS National Health Survey 2017-18)."""
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
            "note": "Elderly (65+) have lower measured distress but face higher social isolation risk",
        },
    }


# ─── Layer 1 — Map paint ─────────────────────────────────────────────────────

@router.get("/map")
def get_suburbs_map(db: Session = Depends(get_db)):
    """
    All suburbs with current crowd level for the hex map UI.
    Suburbs without sensor data have crowd_level=null and has_live_data=False.
    """
    items = suburb_service.get_map_crowd_levels(db)
    with_live = sum(1 for i in items if i["has_live_data"])
    return {
        "total": len(items),
        "with_live_data": with_live,
        "suburbs": items,
    }


# ─── Compare — placed BEFORE /{suburb_id}/... to avoid path-param shadowing ──

@router.get("/compare")
async def compare_suburbs(
    suburb_ids: str = Query(
        ..., description="Comma-separated suburb_ids e.g. 206041117,206041118"
    ),
    db: Session = Depends(get_db),
):
    """Side-by-side snapshot summary for 1-5 suburbs."""
    try:
        ids = [int(x.strip()) for x in suburb_ids.split(",") if x.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="suburb_ids must be integers")
    if not 1 <= len(ids) <= 5:
        raise HTTPException(status_code=400, detail="Provide 1-5 suburb_ids")

    results = []
    for sid in ids:
        snap = await suburb_service.get_suburb_snapshot(db, sid)
        if not snap:
            continue
        results.append({
            "suburb_id": snap["suburb_id"],
            "suburb_name": snap["suburb_name"],
            "crowd_level": snap["crowd"]["crowd_level"],
            "people_per_hour": snap["crowd"]["people_per_hour"],
            "temperature_c": snap["weather"].get("temperature_c"),
            "weather_summary": snap["weather"].get("summary"),
            "events_count": snap["events"]["total"],
            "benches": snap["accessibility"]["benches"],
            "accessible_toilets": snap["accessibility"]["accessible_toilets"],
            "wheelchair_places": snap["accessibility"]["wheelchair_places"],
            "stops_total": snap["transport"]["total_stops"],
            "wheelchair_stops": snap["transport"]["wheelchair_accessible_stops"],
            "green_spaces": snap["green_spaces"]["total"],
            "avg_shade_score": snap["green_spaces"]["avg_shade_score"],
            "elderly_pct": snap["demographics"]["elderly_pct"],
        })
    return {"compared": len(results), "suburbs": results}


# ─── Layer 2 — Snapshot ──────────────────────────────────────────────────────

@router.get("/{suburb_id}/snapshot")
async def get_snapshot(suburb_id: int, db: Session = Depends(get_db)):
    """
    The one-tap, every-signal endpoint feeding the Suburb Explorer right panel.
    Composes crowd + weather + events + accessibility + transport + green spaces
    + landmarks + trees + demographics in a single async response.
    """
    result = await suburb_service.get_suburb_snapshot(db, suburb_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Suburb id {suburb_id} not found")
    return result


# ─── Layer 3 — Drill-downs (also callable standalone) ────────────────────────

@router.get("/{suburb_id}/pedestrian")
def get_pedestrian(suburb_id: int, db: Session = Depends(get_db)):
    """Current crowd level + trend for the suburb."""
    return suburb_service.get_pedestrian_signal(db, suburb_id)


@router.get("/{suburb_id}/weather")
async def get_weather(suburb_id: int, db: Session = Depends(get_db)):
    """Open-Meteo weather + plain-language summary for the suburb centroid."""
    suburb = db.query(Suburb).filter(Suburb.suburb_id == suburb_id).first()
    if not suburb:
        raise HTTPException(status_code=404, detail="Suburb not found")
    weather = await open_meteo.get_weather(suburb.centroid_lat, suburb.centroid_lng)
    summary = open_meteo.summarize_weather(weather)
    return {
        "suburb_id": suburb_id,
        "suburb_name": suburb.suburb_name,
        **weather,
        **summary,
    }


@router.get("/{suburb_id}/events")
async def get_events(
    suburb_id: int,
    rows: int = Query(10, description="Max events to return"),
    db: Session = Depends(get_db),
):
    """Eventfinda events near the suburb centroid."""
    suburb = db.query(Suburb).filter(Suburb.suburb_id == suburb_id).first()
    if not suburb:
        raise HTTPException(status_code=404, detail="Suburb not found")
    items = await suburb_service.get_events_for_suburb(
        suburb.suburb_name, suburb.centroid_lat, suburb.centroid_lng, rows=rows,
    )
    return {
        "suburb_id": suburb_id,
        "suburb_name": suburb.suburb_name,
        "total": len(items),
        "events": items,
    }


@router.get("/{suburb_id}/accessibility")
def get_accessibility(
    suburb_id: int,
    sample_limit: int = Query(5, description="Number of sample places/toilets to return"),
    db: Session = Depends(get_db),
):
    """OSM accessibility summary: benches, accessible toilets, wheelchair places."""
    return suburb_service.get_accessibility_summary_for_suburb(db, suburb_id, sample_limit)


@router.get("/{suburb_id}/transport")
def get_transport(suburb_id: int, db: Session = Depends(get_db)):
    """Stops by mode + routes serving the suburb (with colours from gtfs_route)."""
    return suburb_service.get_transport_summary_for_suburb(db, suburb_id)


@router.get("/{suburb_id}/green-spaces")
def get_green_spaces(suburb_id: int, db: Session = Depends(get_db)):
    """Open spaces in the suburb, including shade scores from open_space_shade.csv."""
    return suburb_service.get_green_spaces_for_suburb(db, suburb_id)


@router.get("/{suburb_id}/landmarks")
def get_landmarks(suburb_id: int, db: Session = Depends(get_db)):
    """Council-curated landmarks in the suburb."""
    items = suburb_service.get_landmarks_for_suburb(db, suburb_id)
    return {"suburb_id": suburb_id, "total": len(items), "landmarks": items}


@router.get("/{suburb_id}/trees")
def get_trees(suburb_id: int, db: Session = Depends(get_db)):
    """Tree count + top species + average shade for the suburb."""
    return suburb_service.get_trees_for_suburb(db, suburb_id)


@router.get("/{suburb_id}/best-times")
def get_best_times(
    suburb_id: int,
    top_n: int = Query(5, description="Number of quietest hours to return"),
    db: Session = Depends(get_db),
):
    """Quietest hours in the suburb (8am-8pm window)."""
    items = suburb_service.get_best_times_for_suburb(db, suburb_id, top_n)
    return {"suburb_id": suburb_id, "total": len(items), "best_times": items}

@router.get("/{suburb_id}/benches")
def get_all_benches(suburb_id: int, db: Session = Depends(get_db)):
    """Every bench in the suburb — for plotting as map markers."""
    return suburb_service.get_all_benches_for_suburb(db, suburb_id)


@router.get("/{suburb_id}/toilets")
def get_all_toilets(suburb_id: int, db: Session = Depends(get_db)):
    """Every accessible toilet in the suburb — for plotting as map markers."""
    return suburb_service.get_all_toilets_for_suburb(db, suburb_id)


@router.get("/{suburb_id}/places")
def get_all_places(
    suburb_id: int,
    category: str | None = Query(
        None,
        description="essentials | social | healthcare | aged_care_social | transit | other",
    ),
    db: Session = Depends(get_db),
):
    """Every wheelchair-accessible venue in the suburb. Optionally filter by category."""
    return suburb_service.get_all_wheelchair_places_for_suburb(db, suburb_id, category)


@router.get("/{suburb_id}/stops")
def get_all_stops(
    suburb_id: int,
    mode: str | None = Query(None, description="bus | tram | train"),
    db: Session = Depends(get_db),
):
    """Every GTFS stop in the suburb. Optionally filter by mode."""
    return suburb_service.get_all_stops_for_suburb(db, suburb_id, mode)
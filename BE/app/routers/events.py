from fastapi import APIRouter, Query, HTTPException
from app.services import eventfinda, ticketmaster

router = APIRouter()


@router.get("/search")
async def search_events(
    suburb: str = Query(default="melbourne", description="Suburb name e.g. sunshine, fitzroy"),
    lat: float = Query(default=None, description="User latitude — overrides suburb"),
    lon: float = Query(default=None, description="User longitude — overrides suburb"),
    radius_km: int = Query(default=5, description="Search radius in km"),
    is_free: bool = Query(default=True, description="Free events only"),
    max_price: float = Query(default=20, description="Max ticket price AUD"),
    date_from: str = Query(default=None, description="Start date YYYY-MM-DD"),
    date_to: str = Query(default=None, description="End date YYYY-MM-DD"),
    category: str = Query(default=None, description="Category: workshops-classes | exhibitions | festivals-lifestyle | performing-arts"),
    rows: int = Query(default=10, description="Number of results"),
    offset: int = Query(default=0, description="Pagination offset"),
):
    try:
        return await eventfinda.search_events(
            suburb=suburb,
            user_lat=lat,
            user_lon=lon,
            radius_km=radius_km,
            is_free=is_free,
            max_price=max_price,
            date_from=date_from,
            date_to=date_to,
            category=category,
            rows=rows,
            offset=offset,
        )
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/recommended")
async def get_recommended_events(
    suburb: str = Query(default="melbourne", description="User's suburb"),
    lat: float = Query(default=None, description="User latitude"),
    lon: float = Query(default=None, description="User longitude"),
    companionship: int = Query(default=64, description="Companionship score 0-100"),
    social_connection: int = Query(default=79, description="Social connection score 0-100"),
    intimacy: int = Query(default=88, description="Intimacy score 0-100"),
    radius_km: int = Query(default=5),
):
    if companionship < 50:
        category = "workshops-classes"
    elif social_connection < 60:
        category = "festivals-lifestyle"
    else:
        category = "exhibitions"

    try:
        data = await eventfinda.search_events(
            suburb=suburb,
            user_lat=lat,
            user_lon=lon,
            is_free=True,
            category=category,
            rows=6,
        )
        return {
            "recommended_category": category,
            "score_profile": {
                "companionship": companionship,
                "social_connection": social_connection,
                "intimacy": intimacy,
            },
            "total": data.get("total"),
            "events": data.get("events", []),
        }
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/cultural")
async def get_cultural_events(
    classification: str = Query(default="Arts and Theatre"),
    date_from: str = Query(default=None),
    date_to: str = Query(default=None),
    size: int = Query(default=10),
):
    try:
        data = await ticketmaster.get_cultural_events(
            classification=classification,
            date_from=date_from,
            date_to=date_to,
            size=size,
        )
        return {
            "source": "ticketmaster",
            "note": "Cultural Outings — major Melbourne venues only",
            "total": data.get("total"),
            "events": data.get("events", []),
        }
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/{event_id}")
async def get_event_detail(event_id: str):
    try:
        return await eventfinda.get_event(event_id)
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))
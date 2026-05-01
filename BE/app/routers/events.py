from fastapi import APIRouter, Query, HTTPException
from app.services import eventfinda, ticketmaster

router = APIRouter()

# Eventfinda category slug mapping
CATEGORY_MAP = {
    "workshops-classes": "workshops-classes",
    "exhibitions": "exhibitions",
    "festivals-lifestyle": "festivals-lifestyle",
    "performing-arts": "performing-arts",
    "music": "music",
    "comedy": "comedy",
    "theatre": "theatre",
    "markets": "markets",
    "community": "community-causes",
    "sport": "sport",
    "education": "education",
    "jazz": "jazz",
    "classical": "classical-music",
    "film": "film",
    "food": "food-and-drink",
    "art": "visual-arts",
    "dance": "dance",
    "health": "health-wellbeing",
    "seniors": "community-causes",
}


@router.get("/search")
async def search_events(
    suburb: str = Query(default="melbourne", description="Suburb name, postcode, or full address e.g. 'Clayton, VIC 3168'"),
    lat: float = Query(default=None, description="User latitude — overrides suburb when provided"),
    lon: float = Query(default=None, description="User longitude — overrides suburb when provided"),
    radius_km: float = Query(default=None, description="Search radius in km. If not provided, no radius filtering applied."),
    is_free: bool = Query(default=False, description="Free events only"),
    max_price: float = Query(default=None, description="Max ticket price AUD (optional, only applied when is_free=false)"),
    date_from: str = Query(default=None, description="Start date YYYY-MM-DD"),
    date_to: str = Query(default=None, description="End date YYYY-MM-DD"),
    category: str = Query(default=None, description="Category: music | classical | classical-music | jazz | comedy | theatre | cabaret | rock | folk | cycling | education | art | creative | exhibitions | markets | food | film | dance | health | sport | performing-arts | workshops-classes | festivals-lifestyle | community"),
    rows: int = Query(default=10, description="Number of results per page"),
    offset: int = Query(default=0, description="Pagination offset"),
):
    # Map category to Eventfinda slug
    mapped_category = None
    if category:
        mapped_category = CATEGORY_MAP.get(category.lower(), category)

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
            category=mapped_category,
            rows=rows,
            offset=offset,
        )
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/recommended")
async def get_recommended_events(
    suburb: str = Query(default="melbourne", description="User suburb"),
    lat: float = Query(default=None, description="User latitude"),
    lon: float = Query(default=None, description="User longitude"),
    companionship: int = Query(default=64, description="Companionship score 0-100"),
    social_connection: int = Query(default=79, description="Social connection score 0-100"),
    intimacy: int = Query(default=88, description="Intimacy score 0-100"),
    radius_km: int = Query(default=5),
):
    # Map UCLA scores to Eventfinda category
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
            "search_context": data.get("search_context"),
        }
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))


@router.get("/cultural")
async def get_cultural_events(
    classification: str = Query(default="Arts and Theatre", description="Arts and Theatre | Music | Comedy | Sport"),
    date_from: str = Query(default=None, description="Start date YYYY-MM-DD"),
    date_to: str = Query(default=None, description="End date YYYY-MM-DD"),
    size: int = Query(default=10, description="Number of results"),
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
async def get_event_detail(
    event_id: str,
    lat: float = Query(default=None, description="User latitude — distance calculated from here"),
    lon: float = Query(default=None, description="User longitude — distance calculated from here"),
):
    try:
        return await eventfinda.get_event(event_id, user_lat=lat, user_lon=lon)
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))
    
@router.get("/categories/available")
async def get_available_categories(
    suburb: str = Query(default="melbourne"),
    radius_km: int = Query(default=5),
):
    """Debug — shows what categories are available near a location right now."""
    try:
        data = await eventfinda.search_events(
            suburb=suburb,
            radius_km=radius_km,
            rows=10,
            offset=0,
        )
        categories = {}
        for e in data.get("events", []):
            cat = e.get("category")
            if cat:
                categories[cat] = categories.get(cat, 0) + 1
        return {
            "suburb": suburb,
            "total_events": data.get("total"),
            "categories_found": categories,
        }
    except Exception as ex:
        raise HTTPException(status_code=502, detail=str(ex))
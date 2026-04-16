import httpx
import base64
import math
from app.config import get_settings

settings = get_settings()
BASE_URL = "https://api.eventfinda.com.au/v2"

SUBURB_COORDS = {
    "melbourne": (-37.8136, 144.9631),
    "sunshine": (-37.7882, 144.8321),
    "fitzroy": (-37.7996, 144.9775),
    "richmond": (-37.8182, 144.9917),
    "st kilda": (-37.8676, 144.9796),
    "footscray": (-37.8002, 144.8996),
    "brunswick": (-37.7659, 144.9627),
    "northcote": (-37.7696, 144.9993),
    "carlton": (-37.7985, 144.9671),
    "south yarra": (-37.8389, 144.9927),
    "docklands": (-37.8140, 144.9425),
    "south melbourne": (-37.8304, 144.9584),
    "south-melbourne": (-37.8304, 144.9584),
    "collingwood": (-37.8038, 144.9892),
    "prahran": (-37.8499, 144.9927),
    "hawthorn": (-37.8224, 145.0282),
    "box hill": (-37.8195, 145.1228),
    "box-hill": (-37.8195, 145.1228),
    "frankston": (-38.1442, 145.1258),
    "dandenong": (-37.9878, 145.2152),
    "werribee": (-37.9019, 144.6613),
    "glen waverley": (-37.8776, 145.1636),
    "glen-waverley": (-37.8776, 145.1636),
    "springvale": (-37.9499, 145.1513),
    "ringwood": (-37.8159, 145.2275),
    "essendon": (-37.7496, 144.9178),
    "coburg": (-37.7443, 144.9641),
    "heidelberg": (-37.7557, 145.0607),
    "glen iris": (-37.8599, 145.0469),
    "glen-iris": (-37.8599, 145.0469),
    "camberwell": (-37.8378, 145.0598),
    "south-yarra": (-37.8389, 144.9927),
    "st-kilda": (-37.8676, 144.9796),
    "port melbourne": (-37.8304, 144.9400),
    "port-melbourne": (-37.8304, 144.9400),
    "williamstown": (-37.8659, 144.8997),
    "newport": (-37.8456, 144.8882),
    "yarraville": (-37.8167, 144.8833),
    "moonee ponds": (-37.7667, 144.9167),
    "moonee-ponds": (-37.7667, 144.9167),
    "thornbury": (-37.7533, 144.9961),
    "preston": (-37.7469, 144.9997),
    "reservoir": (-37.7167, 145.0167),
    "bundoora": (-37.7000, 145.0667),
    "doncaster": (-37.7833, 145.1167),
    "balwyn": (-37.8167, 145.0833),
    "kew": (-37.8000, 145.0333),
    "malvern": (-37.8667, 145.0333),
    "caulfield": (-37.8833, 145.0167),
    "bentleigh": (-37.9167, 145.0333),
    "brighton": (-37.9167, 144.9833),
    "sandringham": (-37.9500, 145.0000),
    "mordialloc": (-37.9833, 145.0833),
    "cheltenham": (-37.9500, 145.0500),
    "clayton": (-37.9167, 145.1167),
    "oakleigh": (-37.9000, 145.0833),
    "chadstone": (-37.8833, 145.0833),
    "mount waverley": (-37.8833, 145.1333),
    "mount-waverley": (-37.8833, 145.1333),
    "southbank": (-37.8230, 144.9671),
    "inner-city": (-37.8136, 144.9631),
    "inner city": (-37.8136, 144.9631),
    "cbd": (-37.8136, 144.9631),
    "east melbourne": (-37.8136, 144.9850),
    "east-melbourne": (-37.8136, 144.9850),
    "west melbourne": (-37.8060, 144.9400),
    "west-melbourne": (-37.8060, 144.9400),
    "north melbourne": (-37.7969, 144.9431),
    "north-melbourne": (-37.7969, 144.9431),
    "fitzroy north": (-37.7863, 144.9775),
    "fitzroy-north": (-37.7863, 144.9775),
    "abbotsford": (-37.8038, 144.9975),
    "cremorne": (-37.8274, 144.9950),
    "windsor": (-37.8560, 144.9927),
    "elwood": (-37.8833, 144.9833),
    "balaclava": (-37.8667, 144.9833),
    "toorak": (-37.8500, 145.0167),
    "armadale": (-37.8560, 145.0167),
    "glen huntly": (-37.8833, 145.0500),
    "glen-huntly": (-37.8833, 145.0500),
    "prahan": (-37.8499, 144.9927),
    "brunswick east": (-37.7659, 144.9827),
    "brunswick-east": (-37.7659, 144.9827),
    "brunswick west": (-37.7659, 144.9427),
    "brunswick-west": (-37.7659, 144.9427),
    "fitzroy-north": (-37.7863, 144.9775),
    "alphington": (-37.7667, 145.0167),
    "ivanhoe": (-37.7667, 145.0500),
    "heidelberg west": (-37.7500, 145.0333),
    "heidelberg-west": (-37.7500, 145.0333),
    "watsonia": (-37.7167, 145.0833),
    "greensborough": (-37.7000, 145.1000),
    "eltham": (-37.7167, 145.1500),
    "diamond creek": (-37.6667, 145.1500),
    "lilydale": (-37.7500, 145.3500),
    "croydon": (-37.7833, 145.2833),
    "mitcham": (-37.8000, 145.2000),
    "nunawading": (-37.8333, 145.1833),
    "blackburn": (-37.8167, 145.1500),
    "forest hill": (-37.8333, 145.1667),
    "vermont": (-37.8500, 145.1833),
    "bayswater": (-37.8500, 145.2667),
    "boronia": (-37.8667, 145.2833),
    "ferntree gully": (-37.8833, 145.2833),
    "knox": (-37.8667, 145.2500),
    "rowville": (-37.9333, 145.2333),
    "noble park": (-37.9667, 145.1667),
    "keysborough": (-37.9833, 145.1667),
    "dingley village": (-37.9833, 145.1333),
    "braeside": (-37.9833, 145.0833),
    "parkdale": (-37.9833, 145.0333),
    "mentone": (-37.9833, 145.0500),
    "aspendale": (-38.0000, 145.1000),
    "edithvale": (-38.0167, 145.1000),
    "chelsea": (-38.0333, 145.1167),
    "bonbeach": (-38.0500, 145.1167),
    "carrum": (-38.0667, 145.1167),
    "seaford": (-38.1000, 145.1333),
    "karingal": (-38.1500, 145.1667),
    "langwarrin": (-38.1667, 145.1833),
    "mornington": (-38.2167, 145.0333),
    "mount eliza": (-38.1833, 145.0833),
    "mount martha": (-38.2667, 145.0333),
    "rosebud": (-38.3667, 144.9000),
    "dromana": (-38.3333, 144.9667),
    "mccrae": (-38.3500, 144.9333),
    "rye": (-38.3833, 144.8333),
    "blairgowrie": (-38.3833, 144.7833),
    "portsea": (-38.3333, 144.7167),
    "sorrento": (-38.3333, 144.7500),
    "point lonsdale": (-38.2833, 144.6167),
    "queenscliff": (-38.2667, 144.6500),
    "ocean grove": (-38.2667, 144.5167),
    "barwon heads": (-38.2667, 144.5000),
    "torquay": (-38.3333, 144.3167),
    "geelong": (-38.1500, 144.3667),
    "geelong west": (-38.1500, 144.3333),
    "newtown": (-38.1333, 144.3500),
    "belmont": (-38.1833, 144.3667),
    "highton": (-38.2000, 144.3500),
    "waurn ponds": (-38.2500, 144.3000),
}


def _get_auth_header() -> dict:
    credentials = f"{settings.EVENTFINDA_USERNAME}:{settings.EVENTFINDA_PASSWORD}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def _get_coords(suburb: str) -> tuple:
    return SUBURB_COORDS.get(suburb.lower().strip(), (-37.8136, 144.9631))


def _calc_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a)), 1)


def _suburb_from_url(url: str) -> tuple:
    try:
        parts = url.rstrip("/").split("/")
        for part in reversed(parts[-3:]):
            clean = part.lower()
            if clean in SUBURB_COORDS:
                lat, lon = SUBURB_COORDS[clean]
                return clean, lat, lon
            clean_space = clean.replace("-", " ")
            if clean_space in SUBURB_COORDS:
                lat, lon = SUBURB_COORDS[clean_space]
                return clean_space, lat, lon
    except Exception:
        pass
    return None, None, None


def _parse_event(e: dict, user_lat: float = None, user_lon: float = None) -> dict:
    location = e.get("location", {})

    # point is top-level field per Eventfinda docs
    point = e.get("point", {})
    lat = point.get("lat") if isinstance(point, dict) else None
    lon = point.get("lng") if isinstance(point, dict) else None

    # Fallback: extract from URL
    suburb = location.get("suburb") if isinstance(location, dict) else None
    if not lat or not lon:
        url_suburb, url_lat, url_lon = _suburb_from_url(e.get("url", ""))
        if url_lat and url_lon:
            lat = url_lat
            lon = url_lon
        if not suburb and url_suburb:
            suburb = url_suburb.replace("-", " ").title()

    # Ticket types
    ticket_types = e.get("ticket_types", {})
    tickets_list = ticket_types.get("ticket_types", []) if isinstance(ticket_types, dict) else []
    prices = [float(t["price"]) for t in tickets_list if t.get("price")]
    min_price = min(prices) if prices else None
    is_free = e.get("is_free", False) or (min_price == 0.0 if min_price is not None else False)

    # Sessions
    sessions = e.get("sessions", {})
    sessions_list = sessions.get("sessions", []) if isinstance(sessions, dict) else []
    first_session = sessions_list[0] if sessions_list else {}

    # Images
    images = e.get("images", {})
    images_list = images.get("images", []) if isinstance(images, dict) else []
    image_url = None
    if images_list:
        transforms = images_list[0].get("transforms", {}).get("transforms", [])
        large = next((t for t in transforms if t.get("transformation_id") == 7), None)
        image_url = large.get("url") if large else images_list[0].get("original_url")

    # Category
    category = e.get("category", {})
    category_name = category.get("name") if isinstance(category, dict) else category

    # Distance from user
    distance_km = None
    if user_lat and user_lon and lat and lon:
        distance_km = _calc_distance(user_lat, user_lon, float(lat), float(lon))

    return {
        "id": e.get("id"),
        "name": e.get("name"),
        "description": (e.get("description") or "")[:300],
        "datetime_start": first_session.get("datetime_start") or e.get("datetime_start"),
        "datetime_end": first_session.get("datetime_end") or e.get("datetime_end"),
        "datetime_summary": e.get("datetime_summary"),
        "is_free": is_free,
        "min_price": min_price,
        "venue": location.get("name") if isinstance(location, dict) else None,
        "suburb": suburb,
        "address": e.get("address"),
        "latitude": lat,
        "longitude": lon,
        "distance_km": distance_km,
        "url": e.get("url"),
        "category": category_name,
        "image_url": image_url,
        "is_cancelled": e.get("is_cancelled", False),
        "source": "eventfinda",
    }


async def search_events(
    suburb: str = "melbourne",
    user_lat: float = None,
    user_lon: float = None,
    radius_km: int = 5,
    is_free: bool = True,
    max_price: float = 20,
    date_from: str = None,
    date_to: str = None,
    category: str = None,
    rows: int = 10,
    offset: int = 0,
) -> dict:
    # Use GPS if provided, otherwise look up suburb
    if user_lat and user_lon:
        search_lat, search_lon = user_lat, user_lon
    else:
        search_lat, search_lon = _get_coords(suburb)

    params = {
        "point": f"{search_lat},{search_lon}",
        "radius": radius_km,
        "rows": rows,
        "offset": offset,
        "order": "distance",
    }
    if is_free:
        params["price_max"] = 0
    elif max_price:
        params["price_max"] = max_price
    if date_from:
        params["start_date"] = date_from
    if date_to:
        params["end_date"] = date_to
    if category:
        params["category_slug"] = category

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/events.json",
            params=params,
            headers=_get_auth_header(),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

    events_raw = data.get("events", [])
    if isinstance(events_raw, dict):
        events_raw = events_raw.get("events", [])

    total = data.get("@attributes", {}).get("count", len(events_raw))

    events = []
    for e in events_raw:
        parsed = _parse_event(e, search_lat, search_lon)
        events.append(parsed)

    events.sort(key=lambda x: x.get("distance_km") or 999)

    return {"total": total, "events": events}


async def get_event(event_id: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/events/{event_id}.json",
            headers=_get_auth_header(),
            timeout=15,
        )
        response.raise_for_status()
        return _parse_event(response.json())
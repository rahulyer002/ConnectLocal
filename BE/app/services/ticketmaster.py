import httpx
from app.config import get_settings

settings = get_settings()
BASE_URL = "https://app.ticketmaster.com/discovery/v2"


async def get_cultural_events(
    classification: str = "Arts and Theatre",
    date_from: str = None,
    date_to: str = None,
    size: int = 10,
) -> dict:
    params = {
        "apikey": settings.TICKETMASTER_API_KEY,
        "city": "Melbourne",
        "countryCode": "AU",
        "classificationName": classification,
        "size": size,
        "sort": "date,asc",
    }
    if date_from:
        params["startDateTime"] = f"{date_from}T00:00:00Z"
    if date_to:
        params["endDateTime"] = f"{date_to}T23:59:59Z"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/events.json",
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

    events = data.get("_embedded", {}).get("events", [])
    total = data.get("page", {}).get("totalElements", len(events))
    return {"total": total, "events": [_parse_tm_event(e) for e in events]}


def _parse_tm_event(e: dict) -> dict:
    venue = e.get("_embedded", {}).get("venues", [{}])[0]
    price_ranges = e.get("priceRanges", [])
    classification = e.get("classifications", [{}])[0]
    images = e.get("images", [])
    large_image = next(
        (i for i in images if i.get("width", 0) > 500),
        images[0] if images else {}
    )
    return {
        "id": e.get("id"),
        "name": e.get("name"),
        "date": e.get("dates", {}).get("start", {}).get("localDate"),
        "time": e.get("dates", {}).get("start", {}).get("localTime"),
        "url": e.get("url"),
        "min_price": price_ranges[0].get("min") if price_ranges else None,
        "max_price": price_ranges[0].get("max") if price_ranges else None,
        "currency": price_ranges[0].get("currency", "AUD") if price_ranges else "AUD",
        "venue_name": venue.get("name"),
        "venue_address": venue.get("address", {}).get("line1"),
        "suburb": venue.get("city", {}).get("name"),
        "latitude": venue.get("location", {}).get("latitude"),
        "longitude": venue.get("location", {}).get("longitude"),
        "genre": classification.get("genre", {}).get("name"),
        "segment": classification.get("segment", {}).get("name"),
        "image_url": large_image.get("url"),
        "source": "ticketmaster",
    }
"""
Open-Meteo client — free, no-key weather for any lat/lon.

Why: /api/safety/conditions uses CoM microclimate (17 CBD-only sensors).
Open-Meteo gives weather for every suburb centroid.
"""
import httpx

BASE_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes — see https://open-meteo.com/en/docs
WMO_CODES = {
    0: "Clear",
    1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Foggy", 48: "Foggy",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    56: "Freezing drizzle", 57: "Heavy freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Heavy freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow",
    77: "Snow grains",
    80: "Rain showers", 81: "Heavy rain showers", 82: "Violent rain showers",
    85: "Snow showers", 86: "Heavy snow showers",
    95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Severe thunderstorm",
}


async def get_weather(lat: float, lon: float) -> dict:
    """Returns current weather for a coordinate from Open-Meteo."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,apparent_temperature",
        "timezone": "Australia/Melbourne",
        "wind_speed_unit": "kmh",
        "temperature_unit": "celsius",
    }
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(BASE_URL, params=params)
            r.raise_for_status()
            data = r.json()
        cur = data.get("current", {})
        wmo = cur.get("weather_code")
        return {
            "available": True,
            "temperature_c": cur.get("temperature_2m"),
            "feels_like_c": cur.get("apparent_temperature"),
            "humidity_pct": cur.get("relative_humidity_2m"),
            "wind_speed_kmh": cur.get("wind_speed_10m"),
            "weather_code": wmo,
            "sky": WMO_CODES.get(wmo, "Unknown") if wmo is not None else None,
            "observed_at": cur.get("time"),
            "source": "open-meteo",
        }
    except Exception as e:
        print(f"[open_meteo] error: {e}")
        return {
            "available": False,
            "temperature_c": None,
            "feels_like_c": None,
            "humidity_pct": None,
            "wind_speed_kmh": None,
            "weather_code": None,
            "sky": None,
            "observed_at": None,
            "source": "open-meteo",
            "error": str(e),
        }


def summarize_weather(weather: dict) -> dict:
    """
    Generates a plain-language summary matching the Epic 6 UX
    (e.g. 'Mild and partly cloudy — comfortable for a short outing').
    """
    if not weather or not weather.get("available"):
        return {
            "summary": "Weather data unavailable.",
            "is_safe_for_elderly": None,
            "warnings": ["Weather temporarily unavailable"],
        }

    temp = weather.get("temperature_c")
    wind = weather.get("wind_speed_kmh")
    sky = (weather.get("sky") or "").lower()

    # Temperature adjective
    if temp is None:
        temp_word = ""
    elif temp < 5:
        temp_word = "Very cold"
    elif temp < 13:
        temp_word = "Cool"
    elif temp < 19:
        temp_word = "Mild"
    elif temp < 26:
        temp_word = "Pleasant"
    elif temp < 31:
        temp_word = "Warm"
    elif temp < 36:
        temp_word = "Hot"
    else:
        temp_word = "Very hot"

    # Sky qualifier
    if "rain" in sky or "drizzl" in sky or "shower" in sky:
        sky_clause = "and rainy"
    elif "thunder" in sky:
        sky_clause = "with thunderstorms"
    elif "snow" in sky:
        sky_clause = "and snowing"
    elif "overcast" in sky:
        sky_clause = "and overcast"
    elif "partly cloudy" in sky or "mainly clear" in sky:
        sky_clause = "and partly cloudy"
    elif "fog" in sky:
        sky_clause = "and foggy"
    elif "clear" in sky:
        sky_clause = "and clear"
    else:
        sky_clause = ""

    # Warnings drive verdict
    warnings = []
    if temp is not None:
        if temp > 35:
            warnings.append(f"Very hot ({temp:.0f}°C) — stay hydrated and seek shade")
        elif temp < 5:
            warnings.append(f"Very cold ({temp:.0f}°C) — dress warmly")
    if wind is not None and wind > 40:
        warnings.append(f"Strong winds ({wind:.0f} km/h)")
    if "rain" in sky or "shower" in sky or "thunder" in sky:
        warnings.append("Rain expected — bring an umbrella")

    if not warnings:
        verdict = "comfortable for a short outing"
    elif len(warnings) == 1:
        verdict = "take some care outdoors"
    else:
        verdict = "challenging conditions for outdoor activity"

    head = " ".join(p for p in [temp_word, sky_clause] if p).strip()
    summary = f"{head} — {verdict}" if head else f"Conditions — {verdict}"

    return {
        "summary": summary,
        "is_safe_for_elderly": len(warnings) == 0,
        "warnings": warnings,
    }

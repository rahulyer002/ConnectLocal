"""
app/routers/safety.py
----------------------
Epic 4 — Safety Conditions API.

Endpoints:
  GET /api/safety/conditions  — live microclimate safety verdict
"""

from fastapi import APIRouter, Query
from app.services.epic_data_service import get_live_microclimate

router = APIRouter()


@router.get("/conditions")
async def get_safety_conditions(
    lat: float = Query(description="User latitude"),
    lon: float = Query(description="User longitude"),
):
    """
    Returns live weather safety conditions for elderly users.
    Powered by City of Melbourne microclimate sensors.

    Safety verdict:
      Good    — comfortable for outdoor activity
      Caution — one concern (e.g. slightly warm)
      Poor    — multiple concerns (e.g. very hot + poor air quality)

    Note: Sensors are located in Melbourne CBD only.
    Readings are updated every 15 minutes.
    """
    weather = await get_live_microclimate(lat, lon)

    return {
        "location": {"lat": lat, "lon": lon},
        "conditions": weather,
        "advice": _build_advice(weather),
        "data_source": "City of Melbourne Microclimate Sensors",
        "update_frequency": "Every 15 minutes",
    }


def _build_advice(weather: dict) -> str:
    if not weather.get("available"):
        return "Weather data temporarily unavailable. Check local forecasts before heading out."

    verdict = weather.get("safety_verdict")
    temp = weather.get("temperature_c")
    wind = weather.get("wind_speed_kmh")

    if verdict == "Good":
        if temp and temp > 25:
            return "Warm but comfortable. Bring water and wear sun protection."
        elif temp and temp < 10:
            return "Cool conditions. Dress in warm layers."
        return "Conditions look good for an outing. Enjoy!"
    elif verdict == "Caution":
        return "Take care today. " + " ".join(weather.get("warnings", []))
    else:
        return "Conditions may be challenging for outdoor activity. " + " ".join(weather.get("warnings", []))
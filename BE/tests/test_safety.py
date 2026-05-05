"""Tests for /api/safety/conditions — live microclimate verdict.

NOTE: safety.py imports `get_live_microclimate` directly, so patch the router.
"""
from app.routers import safety as safety_router


async def _async(value):
    return value


def test_conditions_good_weather(client, monkeypatch):
    monkeypatch.setattr(safety_router, "get_live_microclimate", lambda lat, lon: _async({
        "available": True, "safety_verdict": "Good",
        "temperature_c": 20, "wind_speed_kmh": 12, "warnings": [],
    }))
    r = client.get("/api/safety/conditions?lat=-37.8&lon=144.97")
    assert r.status_code == 200
    body = r.json()
    assert body["conditions"]["safety_verdict"] == "Good"
    assert "advice" in body
    assert body["data_source"] == "City of Melbourne Microclimate Sensors"


def test_conditions_unavailable_returns_fallback_advice(client, monkeypatch):
    monkeypatch.setattr(safety_router, "get_live_microclimate", lambda lat, lon: _async({
        "available": False,
    }))
    r = client.get("/api/safety/conditions?lat=-37.8&lon=144.97")
    assert r.status_code == 200
    assert "temporarily unavailable" in r.json()["advice"]


def test_conditions_warm_weather_advice(client, monkeypatch):
    monkeypatch.setattr(safety_router, "get_live_microclimate", lambda lat, lon: _async({
        "available": True, "safety_verdict": "Good",
        "temperature_c": 28, "wind_speed_kmh": 8, "warnings": [],
    }))
    r = client.get("/api/safety/conditions?lat=-37.8&lon=144.97")
    assert r.status_code == 200
    advice = r.json()["advice"].lower()
    assert "water" in advice or "sun" in advice

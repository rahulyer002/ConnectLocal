"""Tests for /api/resonance — score, gonow, besttimes, forecast.

NOTE: resonance.py imports service functions by name (`from ... import get_crowd_level_now`)
so we patch them on the *router* module, not on epic_data_service.
"""
from app.routers import resonance as resonance_router


async def _async(value):
    return value


def _patch_common(monkeypatch):
    """Helpers shared by resonance tests."""
    monkeypatch.setattr(resonance_router, "get_crowd_level_now",
                        lambda *a, **k: {"crowd_level": "Low", "is_quiet": True})
    monkeypatch.setattr(resonance_router, "get_live_microclimate",
                        lambda *a, **k: _async({
                            "available": True, "safety_verdict": "Good",
                            "temperature_c": 22, "warnings": [],
                        }))
    monkeypatch.setattr(resonance_router, "get_green_spaces_nearby",
                        lambda *a, **k: [{
                            "space_id": "g1", "space_name": "Carlton Gardens",
                            "space_type": "Park", "lat": -37.8, "lon": 144.97,
                            "distance_km": 0.4, "comfort_score": 80,
                        }])
    monkeypatch.setattr(resonance_router, "get_nearby_toilets",
                        lambda *a, **k: [{"toilet_id": "t1"}])
    monkeypatch.setattr(resonance_router, "compute_resonance_score",
                        lambda **kw: {
                            "resonance_score": 88, "grade": "A",
                            "breakdown": {"crowd_score": 30, "weather_score": 32,
                                          "comfort_score": 18, "toilet_score": 5,
                                          "shade_score": 3},
                        })


def test_score_returns_full_payload(client, monkeypatch):
    _patch_common(monkeypatch)
    r = client.get("/api/resonance/score?lat=-37.8&lon=144.97")
    assert r.status_code == 200
    body = r.json()
    assert body["resonance_score"] == 88
    assert body["grade"] == "A"
    assert body["location"] == {"lat": -37.8, "lon": 144.97}
    assert body["nearest_open_space"]["space_id"] == "g1"


def test_gonow_returns_top_3_recommendations(client, monkeypatch):
    _patch_common(monkeypatch)
    r = client.get("/api/resonance/gonow?lat=-37.8&lon=144.97")
    assert r.status_code == 200
    body = r.json()
    assert "recommendations" in body
    assert len(body["recommendations"]) <= 3
    if body["recommendations"]:
        assert "why_recommended" in body["recommendations"][0]


def test_besttimes_404_when_no_sensors(client, monkeypatch):
    monkeypatch.setattr(resonance_router, "get_best_times", lambda *a, **k: [])
    r = client.get("/api/resonance/besttimes?lat=-37.8&lon=144.97")
    assert r.status_code == 404
    assert "No sensor data" in r.json()["detail"]


def test_forecast_groups_by_day(client, monkeypatch):
    monkeypatch.setattr(resonance_router, "get_crowd_forecast", lambda *a, **k: [
        {"day_name": "Monday", "hour": 9, "avg_count": 12, "crowd_level": "Low",  "is_quiet_hour": True},
        {"day_name": "Monday", "hour": 17, "avg_count": 80, "crowd_level": "High", "is_quiet_hour": False},
        {"day_name": "Tuesday", "hour": 10, "avg_count": 30, "crowd_level": "Medium", "is_quiet_hour": False},
    ])
    r = client.get("/api/resonance/forecast?lat=-37.8&lon=144.97")
    assert r.status_code == 200
    body = r.json()
    assert set(body["forecast_days"]) == {"Monday", "Tuesday"}
    assert len(body["forecast"]["Monday"]) == 2

"""Tests for /api/journey — plan, stops/nearby, departures, walk, accessibility.

NOTE: journey.py imports service functions directly into its namespace, so we
patch the router module rather than the service module.
"""
from app.routers import journey as journey_router


async def _async(value):
    return value


def test_stops_nearby_empty_returns_helpful_note(client, monkeypatch):
    monkeypatch.setattr(journey_router, "get_stops_nearby", lambda *a, **k: [])
    r = client.get("/api/journey/stops/nearby?lat=-37.8&lon=144.9&radius_km=0.5")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert body["stops"] == []
    assert "note" in body


def test_stops_nearby_returns_stop_list(client, monkeypatch):
    monkeypatch.setattr(journey_router, "get_stops_nearby", lambda *a, **k: [
        {"stop_id": "19854", "stop_name": "Flinders St", "mode": "train",
         "distance_km": 0.3, "is_wheelchair_accessible": True},
    ])
    r = client.get("/api/journey/stops/nearby?lat=-37.8&lon=144.9")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["stops"][0]["mode"] == "train"


def test_walk_route_502_on_osrm_error(client, monkeypatch):
    monkeypatch.setattr(journey_router, "get_walking_route",
                        lambda *a, **k: _async({"error": "OSRM unreachable"}))
    r = client.get("/api/journey/walk?from_lat=-37.8&from_lon=144.9&to_lat=-37.81&to_lon=144.91")
    assert r.status_code == 502
    assert "OSRM" in r.json()["detail"]


def test_accessibility_404_when_unknown_stop(client, monkeypatch):
    monkeypatch.setattr(journey_router, "get_stop_accessibility",
                        lambda *a, **k: {"error": "Unknown stop"})
    r = client.get("/api/journey/accessibility?stop_id=does-not-exist")
    assert r.status_code == 404

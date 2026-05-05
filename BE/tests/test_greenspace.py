"""Tests for /api/greenspace — nearby, toilets.

NOTE: greenspace.py does `from ...epic_data_service import get_green_spaces_nearby`,
which means the function gets bound into the router's namespace. We patch THERE,
not in the service module — patching the source module wouldn't update the
already-imported reference.
"""
from app.routers import greenspace as greenspace_router


def test_nearby_returns_sorted_spaces(client, monkeypatch):
    monkeypatch.setattr(greenspace_router, "get_green_spaces_nearby", lambda *a, **k: [
        {"space_id": "g1", "space_name": "Carlton Gardens", "comfort_score": 90,
         "lat": -37.8, "lon": 144.97, "distance_km": 0.4},
        {"space_id": "g2", "space_name": "Royal Park",      "comfort_score": 70,
         "lat": -37.78, "lon": 144.95, "distance_km": 1.1},
    ])
    r = client.get("/api/greenspace/nearby?lat=-37.8&lon=144.97&radius_km=2")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert body["green_spaces"][0]["space_id"] == "g1"
    assert "comfort_score" in body["sorted_by"]


def test_toilets_includes_data_note(client, monkeypatch):
    monkeypatch.setattr(greenspace_router, "get_nearby_toilets", lambda *a, **k: [
        {"toilet_id": "t1", "has_wheelchair": True},
    ])
    r = client.get("/api/greenspace/toilets?lat=-37.8&lon=144.97")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert "data_note" in body
    assert body["toilets"][0]["has_wheelchair"] is True


def test_toilets_wheelchair_only_param_passed_through(client, monkeypatch):
    captured = {}
    def fake(db, lat, lon, radius_km, wheelchair_only):
        captured.update(wheelchair_only=wheelchair_only)
        return []
    monkeypatch.setattr(greenspace_router, "get_nearby_toilets", fake)
    r = client.get("/api/greenspace/toilets?lat=-37.8&lon=144.97&wheelchair_only=true")
    assert r.status_code == 200
    assert captured["wheelchair_only"] is True

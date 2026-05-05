"""Tests for /api/open-spaces/nearby."""
from app.services import data_service


def test_nearby_returns_open_spaces(client, monkeypatch):
    monkeypatch.setattr(data_service, "get_open_spaces_nearby", lambda *a, **k: [
        {"space_id": "s1", "space_name": "Princes Park",
         "category": "Green Space", "comfort_score": 75, "distance_km": 0.6},
    ])
    r = client.get("/api/open-spaces/nearby?lat=-37.78&lon=144.96&radius_km=2")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["radius_km"] == 2.0
    assert body["open_spaces"][0]["category"] == "Green Space"


def test_nearby_passes_filters_through(client, monkeypatch):
    captured = {}
    def fake(db, lat, lon, radius_km, category, has_toilet, limit):
        captured.update(category=category, has_toilet=has_toilet)
        return []
    monkeypatch.setattr(data_service, "get_open_spaces_nearby", fake)
    r = client.get("/api/open-spaces/nearby?lat=-37.8&lon=144.97&category=Recreation&has_toilet=true")
    assert r.status_code == 200
    assert captured["category"] == "Recreation"
    assert captured["has_toilet"] is True


def test_nearby_requires_lat_lon(client):
    r = client.get("/api/open-spaces/nearby")
    assert r.status_code == 422  # FastAPI's validation error code

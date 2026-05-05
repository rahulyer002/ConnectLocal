"""Tests for /api/landmarks — nearby, themes."""
from app.services import data_service


def test_nearby_returns_landmarks_with_search_metadata(client, monkeypatch):
    monkeypatch.setattr(data_service, "get_landmarks_nearby", lambda *a, **k: [
        {"landmark_id": "l1", "name": "Carlton Library", "theme": "Community Use"},
    ])
    r = client.get("/api/landmarks/nearby?lat=-37.8&lon=144.97&radius_km=1")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert body["search_lat"] == -37.8
    assert body["radius_km"] == 1.0
    assert body["landmarks"][0]["theme"] == "Community Use"


def test_nearby_with_theme_filter(client, monkeypatch):
    captured = {}
    def fake(db, lat, lon, radius_km, theme, limit):
        captured["theme"] = theme
        return []
    monkeypatch.setattr(data_service, "get_landmarks_nearby", fake)
    r = client.get("/api/landmarks/nearby?lat=-37.8&lon=144.97&theme=Health Services")
    assert r.status_code == 200
    assert captured["theme"] == "Health Services"


def test_themes_returns_data_service_payload(client, monkeypatch):
    monkeypatch.setattr(data_service, "get_landmark_themes",
                        lambda db: ["Community Use", "Health Services", "Leisure/Recreation"])
    r = client.get("/api/landmarks/themes")
    assert r.status_code == 200
    assert "Community Use" in r.json()

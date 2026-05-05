"""Tests for /api/suburbs — profile, search, psychological-distress."""
from app.services import data_service


def test_search_returns_suburb_list(client, monkeypatch):
    monkeypatch.setattr(data_service, "search_suburbs", lambda db, q, limit: [
        {"suburb_id": 1, "suburb_name": "Fitzroy",    "centroid_lat": -37.8, "centroid_lng": 144.97},
        {"suburb_id": 2, "suburb_name": "Fitzroy North","centroid_lat": -37.78,"centroid_lng": 144.97},
    ])
    r = client.get("/api/suburbs/search?q=fit")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert body["suburbs"][0]["suburb_name"] == "Fitzroy"


def test_profile_404_when_suburb_unknown(client, monkeypatch):
    monkeypatch.setattr(data_service, "get_suburb_profile", lambda db, suburb: None)
    r = client.get("/api/suburbs/profile?suburb=atlantis")
    assert r.status_code == 404
    assert "atlantis" in r.json()["detail"]


def test_profile_returns_data_when_found(client, monkeypatch):
    monkeypatch.setattr(data_service, "get_suburb_profile", lambda db, suburb: {
        "suburb": "fitzroy", "population": 10000, "elderly_percent": 12.4,
    })
    r = client.get("/api/suburbs/profile?suburb=fitzroy")
    assert r.status_code == 200
    body = r.json()
    assert body["suburb"] == "fitzroy"
    assert body["elderly_percent"] == 12.4

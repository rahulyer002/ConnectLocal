"""Tests for /api/categories."""
from app.services import data_service


def test_categories_returns_full_list_by_default(client, monkeypatch):
    monkeypatch.setattr(data_service, "get_categories", lambda db, senior_only: [
        {"category_id": 1, "name": "Music",   "senior_friendly": False},
        {"category_id": 2, "name": "Markets", "senior_friendly": True},
        {"category_id": 3, "name": "Theatre", "senior_friendly": False},
    ])
    r = client.get("/api/categories")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert isinstance(body["categories"], list)


def test_categories_senior_only_filter_passed(client, monkeypatch):
    captured = {}
    def fake(db, senior_only):
        captured["senior_only"] = senior_only
        return [{"category_id": 2, "name": "Markets", "senior_friendly": True}]
    monkeypatch.setattr(data_service, "get_categories", fake)
    r = client.get("/api/categories?senior_only=true")
    assert r.status_code == 200
    assert captured["senior_only"] is True
    assert r.json()["total"] == 1

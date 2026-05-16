"""Tests for /api/inference — covers happy path, 4xx, 5xx and DB failures.

Conventions match the rest of the suite (see tests/test_suburbs.py):
  - the `client` fixture from conftest mounts a fresh app with a mocked DB
  - we monkeypatch the service layer rather than touching real Postgres
"""
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.services import inference_service


@pytest.fixture
def app_with_inference(app):
    """Reuses the conftest app and mounts the inference router on top."""
    from app.routers import inference
    app.include_router(inference.router, prefix="/api/inference")
    return app


@pytest.fixture
def iclient(app_with_inference):
    from fastapi.testclient import TestClient
    with TestClient(app_with_inference) as c:
        yield c


def _fake_row(suburb_id=206041117, outing=82.0):
    """Build a MagicMock that quacks like a SuburbInference ORM row."""
    row = MagicMock()
    row.suburb_id = suburb_id
    row.outing_score = outing
    row.persona = "Urban Core"
    row.elderly_pct = 8.2
    row.score_rest = 100.0
    row.score_relief = 83.4
    row.score_amenities = 100.0
    row.score_shade = 50.0
    row.score_transit = 72.6
    row.score_social = 75.0
    row.to_dict.return_value = {
        "suburb_id": suburb_id,
        "outing_score": outing,
        "persona": "Urban Core",
        "scores": {"rest": 100, "relief": 83, "amenities": 100, "shade": 50, "transit": 73, "social": 75},
        "strengths": ["rest", "amenities"],
        "gaps": [],
        "peer_suburbs": [
            {"suburb_id": 206041118, "suburb_name": "Docklands", "outing_score": 79.0, "reason": "Similar transit score"},
        ],
        "counts": {"bench_count": 277, "stop_count": 51, "welcoming_spaces": 5},
        "per_capita": {"benches_per_100_elderly": 20.4},
        "data_completeness_pct": 100.0,
        "generated_at": "2026-05-15T10:00:00",
    }
    row.to_dict_compact.return_value = {
        "suburb_id": suburb_id,
        "outing_score": outing,
        "persona": "Urban Core",
        "elderly_pct": 8.2,
        "scores": {"rest": 100, "relief": 83, "amenities": 100, "shade": 50, "transit": 73, "social": 75},
    }
    return row


def test_health_returns_status_when_no_rows(iclient, monkeypatch):
    from app.routers import inference as inf_router

    fake_db_query = MagicMock()
    fake_db_query.count.side_effect = [522, 0]
    fake_db_query.order_by.return_value.first.return_value = None

    def fake_db_factory():
        db = MagicMock()
        db.query.return_value = fake_db_query
        return db

    iclient.app.dependency_overrides[inf_router.get_db] = fake_db_factory
    r = iclient.get("/api/inference/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "not-computed"
    assert body["suburbs_total"] == 522
    assert body["suburbs_with_score"] == 0


def test_get_inference_happy_path(iclient, monkeypatch):
    monkeypatch.setattr(inference_service, "get_for_suburb", lambda db, sid: _fake_row(sid))
    monkeypatch.setattr(
        "app.routers.inference.Suburb",
        type("S", (), {"suburb_id": 0, "centroid_lat": 0, "centroid_lng": 0, "suburb_name": "x"}),
    )
    r = iclient.get("/api/inference/206041117")
    assert r.status_code == 200
    body = r.json()
    assert body["outing_score"] == 82.0
    assert body["persona"] == "Urban Core"
    assert "rest" in body["scores"]
    assert isinstance(body["peer_suburbs"], list)


def test_get_inference_404_when_suburb_unknown(iclient, monkeypatch):
    monkeypatch.setattr(inference_service, "get_for_suburb", lambda db, sid: None)

    fake_q = MagicMock()
    fake_q.filter.return_value.first.return_value = None

    def fake_db_factory():
        db = MagicMock()
        db.query.return_value = fake_q
        return db

    from app.routers import inference as inf_router
    iclient.app.dependency_overrides[inf_router.get_db] = fake_db_factory

    r = iclient.get("/api/inference/999999999")
    assert r.status_code == 404
    assert "999999999" in r.json()["detail"]


def test_get_inference_503_when_not_yet_computed(iclient, monkeypatch):
    monkeypatch.setattr(inference_service, "get_for_suburb", lambda db, sid: None)

    fake_q = MagicMock()
    fake_q.filter.return_value.first.return_value = MagicMock(suburb_id=206041117)

    def fake_db_factory():
        db = MagicMock()
        db.query.return_value = fake_q
        return db

    from app.routers import inference as inf_router
    iclient.app.dependency_overrides[inf_router.get_db] = fake_db_factory

    r = iclient.get("/api/inference/206041117")
    assert r.status_code == 503
    assert "being prepared" in r.json()["detail"].lower()


def test_get_inference_500_on_db_error(iclient, monkeypatch):
    def boom(db, sid):
        raise SQLAlchemyError("connection reset")
    monkeypatch.setattr(inference_service, "get_for_suburb", boom)
    r = iclient.get("/api/inference/206041117")
    assert r.status_code == 500
    assert "try again" in r.json()["detail"].lower()


def test_rankings_happy_path(iclient, monkeypatch):
    rows = [_fake_row(206041503, 91.0), _fake_row(206041117, 82.0)]
    monkeypatch.setattr(inference_service, "get_rankings", lambda db, metric, persona, top: rows)
    monkeypatch.setattr(inference_service, "suburb_name_map", lambda db, ids: {
        206041503: "Melbourne CBD - East",
        206041117: "Carlton",
    })
    r = iclient.get("/api/inference/rankings?metric=outing_score&top=2")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 2
    assert body["suburbs"][0]["suburb_name"] == "Melbourne CBD - East"
    assert body["suburbs"][0]["outing_score"] == 91.0


def test_rankings_400_on_unknown_metric(iclient):
    r = iclient.get("/api/inference/rankings?metric=elderly_friendliness_quotient")
    assert r.status_code == 400
    assert "elderly_friendliness_quotient" in r.json()["detail"]


def test_rankings_400_on_unknown_persona(iclient):
    r = iclient.get("/api/inference/rankings?persona=Wizards")
    assert r.status_code == 400
    assert "Wizards" in r.json()["detail"]


def test_rankings_400_on_out_of_range_top(iclient):
    r = iclient.get("/api/inference/rankings?top=999")
    assert r.status_code == 422


def test_rankings_empty_when_table_unpopulated(iclient, monkeypatch):
    monkeypatch.setattr(inference_service, "get_rankings", lambda db, metric, persona, top: [])
    r = iclient.get("/api/inference/rankings")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 0
    assert "ETL" in body.get("note", "")


def test_rankings_500_on_db_error(iclient, monkeypatch):
    def boom(db, metric, persona, top):
        raise SQLAlchemyError("connection reset")
    monkeypatch.setattr(inference_service, "get_rankings", boom)
    r = iclient.get("/api/inference/rankings")
    assert r.status_code == 500

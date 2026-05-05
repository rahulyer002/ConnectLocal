"""Tests for /api/events — search, recommended, cultural, detail."""
import pytest
from app.services import eventfinda, ticketmaster


@pytest.fixture
def fake_event_payload():
    return {
        "total": 1,
        "events": [{"id": "evt-1", "name": "Yoga in the Park", "category": "health-wellbeing"}],
        "search_context": {"suburb": "fitzroy"},
    }


async def _async_return(payload):
    return payload


def test_search_returns_200_and_event_list(client, monkeypatch, fake_event_payload):
    monkeypatch.setattr(eventfinda, "search_events",
                        lambda **kwargs: _async_return(fake_event_payload))
    r = client.get("/api/events/search?suburb=fitzroy")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 1
    assert isinstance(body["events"], list)
    assert body["events"][0]["id"] == "evt-1"


def test_search_propagates_502_on_upstream_failure(client, monkeypatch):
    async def boom(**kwargs):
        raise RuntimeError("Eventfinda is down")
    monkeypatch.setattr(eventfinda, "search_events", boom)
    r = client.get("/api/events/search?suburb=melbourne")
    assert r.status_code == 502
    assert "Eventfinda is down" in r.json()["detail"]


def test_recommended_includes_score_profile(client, monkeypatch, fake_event_payload):
    monkeypatch.setattr(eventfinda, "search_events",
                        lambda **kwargs: _async_return(fake_event_payload))
    r = client.get("/api/events/recommended?companionship=40&social_connection=50&intimacy=60")
    assert r.status_code == 200
    body = r.json()
    assert "recommended_category" in body
    assert body["score_profile"] == {
        "companionship": 40, "social_connection": 50, "intimacy": 60,
    }


def test_cultural_calls_ticketmaster_service(client, monkeypatch):
    payload = {"total": 2, "events": [{"id": "tm-1"}, {"id": "tm-2"}]}
    monkeypatch.setattr(ticketmaster, "get_cultural_events",
                        lambda **kwargs: _async_return(payload))
    r = client.get("/api/events/cultural?classification=Music&size=2")
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "ticketmaster"
    assert len(body["events"]) == 2

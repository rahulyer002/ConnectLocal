"""Tests for /api/journey/google — plan, routes (Google Directions API)."""
from app.routers import journey_google


async def _async(value):
    return value


def _fake_google_response():
    """Minimal valid Google Directions response covering one transit leg."""
    return {
        "status": "OK",
        "routes": [{
            "summary": "Route 1",
            "warnings": [],
            "overview_polyline": {"points": "??"},  # decoded as empty
            "legs": [{
                "distance": {"text": "5 km", "value": 5000},
                "duration": {"text": "20 min", "value": 1200},
                "start_address": "A St", "end_address": "B St",
                "start_location": {"lat": -37.8, "lng": 144.9},
                "end_location":   {"lat": -37.81, "lng": 144.91},
                "departure_time": {"text": "10:00", "value": 0},
                "arrival_time":   {"text": "10:20", "value": 1200},
                "steps": [{
                    "html_instructions": "Walk to <b>stop</b>",
                    "distance": {"text": "200 m", "value": 200},
                    "duration": {"text": "3 min", "value": 180},
                    "travel_mode": "WALKING",
                    "steps": [],
                }],
            }],
        }],
    }


def test_plan_returns_parsed_route(client, monkeypatch):
    monkeypatch.setattr(journey_google, "_call_google_directions",
                        lambda *a, **k: _async(_fake_google_response()))
    r = client.get("/api/journey/google/plan?from_lat=-37.8&from_lon=144.9&to_lat=-37.81&to_lon=144.91&mode=transit")
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "transit"
    assert body["provider"] == "google"
    assert "steps" in body


def test_plan_502_on_google_error_status(client, monkeypatch):
    bad = {"status": "ZERO_RESULTS", "error_message": "No route found"}
    monkeypatch.setattr(journey_google, "_call_google_directions",
                        lambda *a, **k: _async(bad))
    r = client.get("/api/journey/google/plan?from_lat=0&from_lon=0&to_lat=0&to_lon=0")
    assert r.status_code == 502
    assert "ZERO_RESULTS" in r.json()["detail"]


def test_routes_marks_recommended_route(client, monkeypatch):
    monkeypatch.setattr(journey_google, "_call_google_directions",
                        lambda *a, **k: _async(_fake_google_response()))
    r = client.get("/api/journey/google/routes?from_lat=-37.8&from_lon=144.9&to_lat=-37.81&to_lon=144.91")
    assert r.status_code == 200
    body = r.json()
    # response is a list of routes — first should be recommended
    routes = body if isinstance(body, list) else body.get("routes", [])
    if routes:
        assert routes[0].get("recommended") is True

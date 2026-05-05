# Backend tests

## Setup

These files belong **alongside your `app/` directory**. So your project should look like:

```
your-project/
├── app/                ← your existing FastAPI code
├── conftest.py         ← from this suite
├── pytest.ini          ← from this suite
├── requirements-test.txt
└── tests/              ← from this suite
```

Then:

```bash
pip install -r requirements-test.txt
pytest -v
```

## How tests are isolated

We don't hit the DB or any external APIs. Instead:

1. `conftest.py` builds a fresh FastAPI app on each test, including all routers.
2. `get_db` is overridden to return a `MagicMock` — no DB connection ever opens.
3. The dummy `Settings` env vars are set in the file so `get_settings()` succeeds even without a `.env` file.
4. Each test uses `monkeypatch` to replace the specific service function it cares about.

## Adding a test

Pick the router file, find the service function it calls, monkeypatch it:

```python
def test_my_endpoint(client, monkeypatch):
    from app.services import data_service
    monkeypatch.setattr(data_service, "get_landmarks_nearby",
                        lambda *a, **k: [{"name": "Library"}])
    r = client.get("/api/landmarks/nearby?lat=-37.8&lon=144.9")
    assert r.status_code == 200
    assert r.json()["total"] == 1
```

That's the whole pattern.

## Running a subset

```bash
pytest tests/test_events.py            # one file
pytest tests/test_events.py -k search  # one test by keyword
pytest --lf                            # only the last failures
```

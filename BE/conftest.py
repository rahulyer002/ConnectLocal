"""
conftest.py — shared test fixtures for the EasyReach backend.

What this does:
- Sets dummy env vars BEFORE app modules import (avoids Settings validation errors).
- Builds a fresh FastAPI app per test, registering every router under /api.
- Overrides get_db so we never touch a real database.
- Provides a `client` fixture (sync) for endpoint testing.
"""

import os

# ── Set fake env vars BEFORE any `app.*` import happens ──────────────────────
# pydantic-settings will validate these on Settings() construction.
os.environ.setdefault("EVENTFINDA_USERNAME", "test")
os.environ.setdefault("EVENTFINDA_PASSWORD", "test")
os.environ.setdefault("TICKETMASTER_API_KEY", "test")
os.environ.setdefault("DATABASE_URL_SYNC", "sqlite:///:memory:")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("GOOGLE_MAPS_API_KEY", "test-key")
os.environ.setdefault("ENVIRONMENT", "test")

from unittest.mock import MagicMock
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def app():
    """Build a fresh FastAPI app per test, including every router under /api."""
    from app.database import get_db
    from app.routers import (
        categories,
        events,
        greenspace,
        journey,
        journey_google,
        landmarks,
        open_spaces,
        resonance,
        safety,
        suburbs,
    )

    application = FastAPI()
    application.include_router(categories.router, prefix="/api/categories")
    application.include_router(events.router, prefix="/api/events")
    application.include_router(greenspace.router, prefix="/api/greenspace")
    application.include_router(journey.router, prefix="/api/journey")
    application.include_router(journey_google.router, prefix="/api/journey/google")
    application.include_router(landmarks.router, prefix="/api/landmarks")
    application.include_router(open_spaces.router, prefix="/api/open-spaces")
    application.include_router(resonance.router, prefix="/api/resonance")
    application.include_router(safety.router, prefix="/api/safety")
    application.include_router(suburbs.router, prefix="/api/suburbs")

    # Replace DB dependency with a no-op mock — no real connection ever opens.
    application.dependency_overrides[get_db] = lambda: MagicMock()
    return application


@pytest.fixture
def client(app):
    """Synchronous TestClient — works for both sync and async route handlers."""
    with TestClient(app) as c:
        yield c

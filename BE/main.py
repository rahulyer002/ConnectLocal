import json
import math
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import events, suburbs, landmarks, open_spaces, categories
from app.routers import resonance, safety, greenspace, journey
from app.routers import journey_google
from app.routers import accessibility
from app.routers import trees as trees_router
from app.routers import routes as routes_router
from app.routers import chatbot                                                  # ← NEW
from app.routers import inference

settings = get_settings()


def _nan_safe(obj):
    """Recursively replace NaN/Inf floats with None — JSON spec doesn't allow them."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _nan_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_nan_safe(v) for v in obj]
    return obj

class SafeJSONResponse(JSONResponse):
    """JSONResponse that coerces NaN/Inf to null instead of raising."""
    def render(self, content) -> bytes:
        return json.dumps(
            _nan_safe(content),
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")


app = FastAPI(
    title="ConnectLocal API",
    description="Backend API for ConnectLocal — helping older Australians find social opportunities",
    version="4.0.0",
    default_response_class=SafeJSONResponse,   # ← the key change
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Epic 1 & 2 — Events + Data ───────────────────────────────────────────────
app.include_router(events.router,      prefix="/api/events",      tags=["Events"])
app.include_router(suburbs.router,     prefix="/api/suburbs",     tags=["Suburbs (Epic 6)"])
app.include_router(landmarks.router,   prefix="/api/landmarks",   tags=["Landmarks"])
app.include_router(open_spaces.router, prefix="/api/open-spaces", tags=["Open Spaces"])
app.include_router(categories.router,  prefix="/api/categories",  tags=["Categories"])

# ─── Epic 3 — Journey Support ─────────────────────────────────────────────────
app.include_router(journey.router,        prefix="/api/journey",        tags=["Journey (Epic 3)"])
app.include_router(journey_google.router, prefix="/api/journey/google", tags=["Journey (Google)"])

# ─── Epic 4 — Resonance Engine ────────────────────────────────────────────────
app.include_router(resonance.router,   prefix="/api/resonance",   tags=["Resonance (Epic 4)"])
app.include_router(safety.router,      prefix="/api/safety",      tags=["Safety (Epic 4)"])
app.include_router(greenspace.router,  prefix="/api/greenspace",  tags=["Green Space (Epic 4)"])
# ─── Epic 5 — AI Chatbot ──────────────────────────────────────────────────────  ← NEW
app.include_router(chatbot.router,     prefix="/api/chatbot",     tags=["Chatbot (Epic 5)"])

# ─── NEW datasets — standalone point-based exposures ─────────────────────────
app.include_router(accessibility.router, prefix="/api/accessibility", tags=["Accessibility (OSM)"])
app.include_router(trees_router.router,  prefix="/api/trees",         tags=["Trees"])
app.include_router(routes_router.router, prefix="/api/routes",        tags=["Transport Routes"])
app.include_router(inference.router, prefix="/api/inference", tags=["Inference"])


@app.get("/")
async def root():
    return {
        "message": "ConnectLocal API is running",
        "version": "4.0.0",
        "epics": {
            "epic_1_2": "Events + Suburb/Landmark/OpenSpace data",
            "epic_3": "Journey planning — /api/journey",
            "epic_4": "Resonance engine — /api/resonance, /api/safety, /api/greenspace",
            "epic_6": "Suburb Explorer — /api/suburbs/map + /api/suburbs/{id}/snapshot",
        },
        "new_datasets": [
            "OSM benches, accessible toilets, wheelchair places — /api/accessibility/*",
            "Trees + shade scoring — /api/trees/*",
            "GTFS routes — /api/routes/*",
            "Per-suburb composition — /api/suburbs/{id}/*",
        ],
            "epic_5": "AI chatbot — /api/chatbot",
        }
    


@app.get("/health")
async def health():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

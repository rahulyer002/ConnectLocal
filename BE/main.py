from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import events, suburbs, landmarks, open_spaces, categories
from app.routers import resonance, safety, greenspace, journey
from app.routers import journey_google
from app.routers import chatbot                                                  # ← NEW

settings = get_settings()

app = FastAPI(
    title="ConnectLocal API",
    description="Backend API for ConnectLocal — helping older Australians find social opportunities",
    version="3.1.0",                                                              # ← bumped
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
app.include_router(suburbs.router,     prefix="/api/suburbs",     tags=["Suburbs"])
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


@app.get("/")
async def root():
    return {
        "message": "ConnectLocal API is running",
        "version": "3.1.0",
        "epics": {
            "epic_1_2": "Events + Suburb/Landmark/OpenSpace data",
            "epic_3": "Journey planning — /api/journey",
            "epic_4": "Resonance engine — /api/resonance, /api/safety, /api/greenspace",
            "epic_5": "AI chatbot — /api/chatbot",
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

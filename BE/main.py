from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.routers import events

settings = get_settings()

app = FastAPI(
    title="ConnectLocal API",
    description="Backend API for ConnectLocal — helping older Australians find social opportunities",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router, prefix="/api/events", tags=["Events"])

@app.get("/")
async def root():
    return {"message": "ConnectLocal API is running", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy","environment": settings.ENVIRONMENT}
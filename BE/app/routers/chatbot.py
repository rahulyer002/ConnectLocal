"""
Chatbot Router — single POST /message endpoint.

The frontend sends the full conversation history each turn (the service is
stateless) plus the user's current route for context. Returns the assistant's
reply, an optional proposed action, and suggested follow-up prompts.
"""
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import chatbot as chatbot_service

router = APIRouter()


# ─── Request / Response Models ───────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(
        ..., description="Full conversation history. Frontend stores in sessionStorage."
    )
    current_route: str = Field(
        default="/home", description="Vue router path the user is currently on."
    )


class ProposedAction(BaseModel):
    name: str
    args: dict[str, Any] = {}
    needs_confirmation: bool


class ChatResponse(BaseModel):
    reply: str
    proposed_action: Optional[ProposedAction] = None
    suggested_prompts: list[str] = []


# ─── Endpoints ───────────────────────────────────────────────────────────────

@router.post("/message", response_model=ChatResponse)
async def send_message(req: ChatRequest):
    """
    Send a message to the chatbot. Returns the assistant's reply plus an
    optional proposed action for the frontend to either auto-execute (if
    needs_confirmation=False) or display as an Allow/Cancel card.
    """
    if not req.messages:
        raise HTTPException(status_code=400, detail="At least one message is required")

    # Convert pydantic models to plain dicts for the service layer
    history = [m.model_dump() for m in req.messages]

    result = await chatbot_service.chat(
        messages=history,
        current_route=req.current_route,
    )
    return result


@router.get("/health")
async def health():
    """Smoke check — returns 200 if the router is wired up correctly."""
    from app.services.chatbot import _get_groq_api_key
    has_key = bool(_get_groq_api_key())
    return {
        "status": "ok" if has_key else "missing-api-key",
        "groq_configured": has_key,
    }

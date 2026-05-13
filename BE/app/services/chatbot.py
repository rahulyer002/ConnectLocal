"""
Chatbot Service — wraps Groq's OpenAI-compatible Chat Completions API.

Reads the system prompt from app/prompts/chatbot_system.md.
Sends the conversation history + available tools to Groq.
Parses the response, validates any proposed tool call, and returns a
structured response to the router.

We use httpx directly (not the groq SDK) so we don't add a new dependency —
your project already has httpx for Eventfinda, OSRM, etc.
"""
from __future__ import annotations
import json
import os
import logging
from pathlib import Path
from typing import Any, Optional

import httpx

from app.config import get_settings
from app.services.chatbot_actions import (
    ACTIONS,
    ALLOWED_ROUTES,
    NEEDS_CONFIRMATION,
)

log = logging.getLogger(__name__)

# ─── Configuration ───────────────────────────────────────────────────────────
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL   = "meta-llama/llama-4-scout-17b-16e-instruct"  # supports tool calling
GROQ_TIMEOUT = 12.0  # seconds — Groq is fast, anything over this is failing

# Cache the system prompt so we don't re-read the markdown file every request
_SYSTEM_PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "chatbot_system.md"
_system_prompt_cache: Optional[str] = None


def _load_system_prompt() -> str:
    """Read the system prompt from disk (cached after first call)."""
    global _system_prompt_cache
    if _system_prompt_cache is None:
        try:
            _system_prompt_cache = _SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
        except FileNotFoundError:
            log.error("System prompt file not found at %s", _SYSTEM_PROMPT_PATH)
            _system_prompt_cache = "You are a helpful assistant for the ConnectLocal website."
    return _system_prompt_cache


def _get_groq_api_key() -> Optional[str]:
    """
    Resolve the Groq API key. We check the env var directly because your
    Settings class doesn't include it yet — keeping the integration loose.
    Add GROQ_API_KEY to your .env file.
    """
    return os.getenv("GROQ_API_KEY") or getattr(get_settings(), "GROQ_API_KEY", "")


# ─── Suggested-prompt chips per route ────────────────────────────────────────
# Short, conversational, what the user might actually say. Keep to 3-4 per
# route. The frontend will show these under the input.

SUGGESTED_PROMPTS_BY_ROUTE = {
    "/home": [
        "Find free events this week",
        "Is now a good time to go out?",
        "What can this site help me with?",
    ],
    "/discover": [
        "Show only free events",
        "Events this weekend",
        "Plan a journey to one of these",
    ],
    "/journey": [
        "How long will this take?",
        "Is there a quieter route?",
        "Take me to events instead",
    ],
    "/best-time": [
        "Show conditions right now",
        "Show the weekly view",
        "Find a welcoming space nearby",
    ],
    "/best-time/now": [
        "What do these scores mean?",
        "Find a park with toilets",
        "Plan a journey from here",
    ],
    "/best-time/week": [
        "When is the quietest day?",
        "Find events at the quiet times",
        "Show me live conditions instead",
    ],
    "/checkin": [
        "What does this check do?",
        "Is my data private?",
        "Start the check-in",
    ],
    "/results": [
        "What does my score mean?",
        "Find events that might help",
        "Take me to the journey planner",
    ],
    "/welcoming-spaces": [
        "Show me libraries nearby",
        "What is a welcoming space?",
        "Find events in this suburb",
    ],
    "/about": [
        "How does this site work?",
        "Find events near me",
        "Plan a journey",
    ],
    "/resources": [
        "Find events near me",
        "Plan a journey",
        "Take me back home",
    ],
    "_default": [
        "Find free events near me",
        "Plan a journey",
        "Is now a good time to go out?",
    ],
}


def _suggested_prompts_for(route: str) -> list[str]:
    """Look up route prompts. Tries exact match first, then prefix match."""
    if not route:
        return SUGGESTED_PROMPTS_BY_ROUTE["_default"]
    if route in SUGGESTED_PROMPTS_BY_ROUTE:
        return SUGGESTED_PROMPTS_BY_ROUTE[route]
    # Prefix match — /events/123 falls through to default;
    # /best-time/anything-else falls through to /best-time
    for key in SUGGESTED_PROMPTS_BY_ROUTE:
        if key != "_default" and route.startswith(key + "/"):
            return SUGGESTED_PROMPTS_BY_ROUTE[key]
    return SUGGESTED_PROMPTS_BY_ROUTE["_default"]


# ─── Public entry point ──────────────────────────────────────────────────────

async def chat(
    messages: list[dict[str, Any]],
    current_route: str = "/home",
) -> dict[str, Any]:
    """
    Main entry point.

    Args:
        messages: full conversation history as OpenAI-style messages.
                  e.g. [{"role": "user", "content": "find free events"}]
                  The frontend stores history in sessionStorage and replays
                  it each turn — this service is stateless.
        current_route: the page the user is currently on. Used to add context
                       to the system prompt and to pick suggested prompts.

    Returns:
        {
            "reply": "Sure, I'll look for free events near you.",
            "proposed_action": {
                "name": "search_events",
                "args": {"is_free": True},
                "needs_confirmation": True
            } | None,
            "suggested_prompts": ["Show only free events", ...]
        }
    """
    api_key = _get_groq_api_key()
    if not api_key:
        log.error("GROQ_API_KEY not configured")
        return _fallback_response("The assistant is not configured yet. Please contact support.")

    # Build the full message list with system prompt and route context
    system_prompt = _load_system_prompt()
    route_context = f"\n\nThe user is currently on the page: {current_route}"

    full_messages = [
        {"role": "system", "content": system_prompt + route_context},
        *messages,
    ]

    payload = {
        "model": GROQ_MODEL,
        "messages": full_messages,
        "tools": ACTIONS,
        "tool_choice": "auto",
        "temperature": 0.3,        # low → more deterministic tool calls
        "max_tokens": 400,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=GROQ_TIMEOUT) as client:
            response = await client.post(GROQ_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as e:
        log.error("Groq returned HTTP %s: %s", e.response.status_code, e.response.text[:200])
        return _fallback_response(
            "I'm having trouble thinking right now. Please try again in a moment."
        )
    except httpx.TimeoutException:
        log.warning("Groq request timed out")
        return _fallback_response(
            "That took longer than expected. Please try again."
        )
    except Exception as e:
        log.exception("Unexpected error calling Groq: %s", e)
        return _fallback_response("Something went wrong. Please try again.")

    return _parse_groq_response(data, current_route)


# ─── Response parsing ────────────────────────────────────────────────────────

def _parse_groq_response(data: dict, current_route: str) -> dict[str, Any]:
    """Pull out the reply text and any tool call, validate the tool call."""
    try:
        message = data["choices"][0]["message"]
    except (KeyError, IndexError):
        log.error("Malformed Groq response: %s", json.dumps(data)[:300])
        return _fallback_response("I didn't quite catch that. Could you say it again?")

    reply_text = message.get("content") or ""
    tool_calls = message.get("tool_calls") or []

    proposed_action = None
    if tool_calls:
        # Process only the first tool call. Multi-action turns get confusing for
        # an elderly user — one thing at a time.
        proposed_action = _parse_tool_call(tool_calls[0])

    # If the model returned a tool call but no reply text, generate a sensible
    # placeholder. (Groq sometimes does this when tool_choice is "auto".)
    if proposed_action and not reply_text:
        reply_text = _default_reply_for_action(proposed_action)

    # If there's no reply and no action, something went wrong — fallback.
    if not reply_text and not proposed_action:
        reply_text = "I'm not sure how to help with that. Try one of the suggestions below."

    return {
        "reply": reply_text.strip(),
        "proposed_action": proposed_action,
        "suggested_prompts": _suggested_prompts_for(current_route),
    }


def _parse_tool_call(tool_call: dict) -> Optional[dict[str, Any]]:
    """Extract and validate a tool call. Returns None if invalid."""
    try:
        fn = tool_call["function"]
        name = fn["name"]
        args_raw = fn.get("arguments", "{}")
        args = json.loads(args_raw) if isinstance(args_raw, str) else args_raw
    except (KeyError, json.JSONDecodeError) as e:
        log.warning("Could not parse tool_call: %s — %s", e, tool_call)
        return None

    # Validate against the action catalogue
    valid_action_names = {a["function"]["name"] for a in ACTIONS}
    if name not in valid_action_names:
        log.warning("Model returned unknown action '%s' — treating as unknown", name)
        return {"name": "unknown", "args": {"reason": f"Invalid action: {name}"}, "needs_confirmation": False}

    # For navigate_to, double-check the route is in the allowed list
    if name == "navigate_to":
        if args.get("route") not in ALLOWED_ROUTES:
            log.warning("Model proposed navigating to disallowed route: %s", args.get("route"))
            return {"name": "unknown", "args": {"reason": "Invalid route"}, "needs_confirmation": False}

    return {
        "name": name,
        "args": args,
        "needs_confirmation": NEEDS_CONFIRMATION.get(name, True),
    }


def _default_reply_for_action(action: dict) -> str:
    """Sensible fallback reply text when the model emits a tool call but no prose."""
    name = action.get("name", "")
    if name == "search_events":
        return "Let me search for that now."
    if name == "plan_journey":
        return "I'll open the journey planner for you."
    if name == "start_checkin":
        return "I'll take you to the wellbeing check-in."
    if name == "check_best_time":
        return "Let me check the conditions for you."
    if name == "navigate_to":
        return "Taking you there now."
    if name == "find_welcoming_places":
        return "I'll show you welcoming places nearby."
    if name == "find_open_spaces":
        return "Let me find some good open spaces."
    return "Here you go."


def _fallback_response(message: str) -> dict[str, Any]:
    """Used when Groq is unreachable or returns garbage."""
    return {
        "reply": message,
        "proposed_action": None,
        "suggested_prompts": SUGGESTED_PROMPTS_BY_ROUTE["_default"],
    }

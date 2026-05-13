"""
Chatbot Action Catalogue
─────────────────────────────────────────────────────────────────────────────
The complete list of actions the chatbot is allowed to invoke. Each action
is defined as an OpenAI-style tool schema that Groq's function-calling API
understands.

Adding a new action: append to ACTIONS, then handle it in
`chatbot_dispatcher.dispatch()`. Nothing else needs to change.

The "unknown" action is the graceful-failure case — Groq returns this when
the user's request doesn't match any other action.
"""

# Routes the chatbot is allowed to navigate to. Keep this in sync with
# vue-router definitions in FE/vue-app/src/router/index.js
ALLOWED_ROUTES = [
    "/home",
    "/discover",
    "/journey",
    "/checkin",
    "/checkin/form",
    "/results",
    "/best-time",
    "/best-time/now",
    "/best-time/week",
    "/welcoming-spaces",
]

ACTIONS = [
    {
        "type": "function",
        "function": {
            "name": "navigate_to",
            "description": (
                "Navigate the user to a specific page in the app. Use this "
                "when the user wants to go somewhere without any filters or "
                "parameters — e.g. 'take me to the journey planner', "
                "'open the home page', 'go to my check-in'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "enum": ALLOWED_ROUTES,
                        "description": "The path to navigate to.",
                    }
                },
                "required": ["route"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_events",
            "description": (
                "Search for social events near a suburb with optional filters. "
                "Use this when the user mentions events, activities, things to "
                "do, or asks to find something to attend."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "suburb": {
                        "type": "string",
                        "description": (
                            "Melbourne suburb name e.g. 'Carlton'. If the user "
                            "did not mention a suburb, omit this field."
                        ),
                    },
                    "is_free": {
                        "type": "boolean",
                        "description": (
                            "Only return free events. Only set if the user "
                            "explicitly mentioned free/cheap/no cost."
                        ),
                    },
                    "this_week_only": {
                        "type": "boolean",
                        "description": (
                            "Only events in the next 7 days. Set if the user "
                            "said 'this week', 'this weekend', 'soon'."
                        ),
                    },
                    "category": {
                        "type": "string",
                        "enum": [
                            "music", "classical", "jazz", "comedy", "theatre",
                            "art", "exhibitions", "markets", "food", "film",
                            "dance", "health", "sport", "community",
                        ],
                        "description": (
                            "Category if the user mentioned a specific kind "
                            "of activity."
                        ),
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "plan_journey",
            "description": (
                "Open the journey planner with origin and destination filled "
                "in. Use this when the user wants to know how to get somewhere."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "to_place": {
                        "type": "string",
                        "description": "Destination — venue name, suburb, or landmark.",
                    },
                    "from_place": {
                        "type": "string",
                        "description": (
                            "Origin — venue, suburb, or 'my location'. Default "
                            "to 'my location' if the user did not specify."
                        ),
                    },
                    "arrive_by": {
                        "type": "string",
                        "description": (
                            "Desired arrival time in 24-hour HH:MM format if "
                            "mentioned, e.g. '14:30'. Omit if not stated."
                        ),
                    },
                },
                "required": ["to_place"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "start_checkin",
            "description": (
                "Start the wellbeing check-in flow. Use when the user wants to "
                "do the assessment, take the check-in, or asks about their "
                "loneliness/social wellbeing."
            ),
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_best_time",
            "description": (
                "Open the Best Time page showing current conditions and the "
                "best times to go out. Use when the user asks 'is now a good "
                "time to go out', 'when is it quiet', 'is it busy now'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "suburb": {
                        "type": "string",
                        "description": "Suburb to check, if mentioned.",
                    },
                    "scope": {
                        "type": "string",
                        "enum": ["now", "week"],
                        "description": (
                            "'now' for live conditions, 'week' for the weekly "
                            "crowd heatmap. Default 'now'."
                        ),
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_welcoming_places",
            "description": (
                "Show welcoming community places like libraries, community "
                "centres, civic buildings on a map. Use when the user asks "
                "for somewhere safe/quiet/welcoming to visit."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "suburb": {"type": "string"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_open_spaces",
            "description": (
                "Show outdoor open spaces (parks, green spaces) with comfort "
                "scores. Use when the user asks for parks, outdoor spots, or "
                "somewhere to walk."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "suburb": {"type": "string"},
                    "with_toilets": {
                        "type": "boolean",
                        "description": "Filter to spaces with public toilets nearby.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "explain_page",
            "description": (
                "Answer a question about what something on the site means or "
                "how a feature works, WITHOUT navigating anywhere. Use for "
                "questions like 'what does this score mean', 'how does the "
                "comfort score work', 'why are some events highlighted'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "What the user is asking about.",
                    }
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "unknown",
            "description": (
                "Use this when the user's request does not match any other "
                "action AND is not a general question. The system will show "
                "the user a few example things they can ask."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Brief reason this didn't match.",
                    }
                },
            },
        },
    },
]


# ─── Which actions need user confirmation before execution? ──────────────────
# Per the design decision: confirm every navigation, filter, or state change.
# explain_page is chat-only so no confirmation needed.
# unknown shows suggestions, not an action.

NEEDS_CONFIRMATION = {
    "navigate_to":          True,
    "search_events":        True,
    "plan_journey":         True,
    "start_checkin":        True,
    "check_best_time":      True,
    "find_welcoming_places": True,
    "find_open_spaces":     True,
    "explain_page":         False,  # text-only response
    "unknown":              False,  # shows suggestions
}


def list_action_names() -> list[str]:
    """Helper for prompts/logging — names only."""
    return [a["function"]["name"] for a in ACTIONS]

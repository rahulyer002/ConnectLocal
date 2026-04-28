import time
from typing import Any

_cache: dict[str, tuple[Any, float]] = {}


def cache_get(key: str) -> Any | None:
    if key in _cache:
        value, expires_at = _cache[key]
        if time.time() < expires_at:
            return value
        del _cache[key]
    return None


def cache_set(key: str, value: Any, ttl_seconds: int = 900) -> None:
    _cache[key] = (value, time.time() + ttl_seconds)
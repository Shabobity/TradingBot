"""Caching system with time-based expiry."""

import time
from typing import Any, Dict, Optional
from config import CACHE_TTL_SECONDS

_cache: Dict[str, Dict] = {}


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache if not expired."""
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def cache_set(key: str, data: Any) -> None:
    """Store value in cache with timestamp."""
    _cache[key] = {"ts": time.time(), "data": data}


def cache_clear() -> None:
    """Clear entire cache."""
    _cache.clear()

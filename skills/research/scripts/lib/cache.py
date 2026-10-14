"""Caching utilities for research skill."""

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

CACHE_DIR = Path.home() / ".cache" / "research"
# 24 hours matches the research window granularity. Queries for the
# same topic within a day reuse cached results instead of re-calling APIs.
DEFAULT_TTL_HOURS = 24
# Model lists change infrequently. 7 days avoids repeated model
# listing API calls while still catching new model releases.
MODEL_CACHE_TTL_DAYS = 7
DEBUG = os.environ.get("RESEARCH_DEBUG", "").lower() in ("1", "true", "yes")


def ensure_cache_dir():
    """Ensure cache directory exists."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_key(topic: str, from_date: str, to_date: str, sources: str) -> str:
    """Generate a cache key from query parameters."""
    key_data = f"{topic}|{from_date}|{to_date}|{sources}"
    return hashlib.sha256(key_data.encode()).hexdigest()[:16]


def get_cache_path(cache_key: str) -> Path:
    """Get path to cache file."""
    return CACHE_DIR / f"{cache_key}.json"


def is_cache_valid(cache_path: Path, ttl_hours: int = DEFAULT_TTL_HOURS) -> bool:
    """Check if cache file exists and is within TTL."""
    if not cache_path.exists():
        return False

    try:
        stat = cache_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        age_hours = (now - mtime).total_seconds() / 3600
        return age_hours < ttl_hours
    except OSError:
        return False


def load_cache(cache_key: str, ttl_hours: int = DEFAULT_TTL_HOURS) -> Optional[dict]:
    """Load data from cache if valid."""
    cache_path = get_cache_path(cache_key)

    if not is_cache_valid(cache_path, ttl_hours):
        return None

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def get_cache_age_hours(cache_path: Path) -> Optional[float]:
    """Get age of cache file in hours."""
    if not cache_path.exists():
        return None
    try:
        stat = cache_path.stat()
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - mtime).total_seconds() / 3600
    except OSError:
        return None


def load_cache_with_age(cache_key: str, ttl_hours: int = DEFAULT_TTL_HOURS) -> tuple:
    """Load data from cache with age info.

    Returns:
        Tuple of (data, age_hours) or (None, None) if invalid
    """
    cache_path = get_cache_path(cache_key)

    if not is_cache_valid(cache_path, ttl_hours):
        return None, None

    age = get_cache_age_hours(cache_path)

    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            return json.load(f), age
    except (json.JSONDecodeError, OSError):
        return None, None


def save_cache(cache_key: str, data: dict):
    """Save data to cache."""
    ensure_cache_dir()
    cache_path = get_cache_path(cache_key)

    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except OSError as e:
        if DEBUG:
            sys.stderr.write(f"[DEBUG] Cache write failed for {cache_key}: {e}\n")


def clear_cache():
    """Clear all cache files."""
    if CACHE_DIR.exists():
        for f in CACHE_DIR.glob("*.json"):
            try:
                f.unlink()
            except OSError:
                pass


# Model selection cache (longer TTL)
MODEL_CACHE_FILE = CACHE_DIR / "model_selection.json"


def load_model_cache() -> dict:
    """Load model selection cache."""
    if not is_cache_valid(MODEL_CACHE_FILE, MODEL_CACHE_TTL_DAYS * 24):
        return {}

    try:
        with open(MODEL_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def save_model_cache(data: dict):
    """Save model selection cache."""
    ensure_cache_dir()
    try:
        with open(MODEL_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f)
    except OSError as e:
        if DEBUG:
            sys.stderr.write(f"[DEBUG] Model cache write failed: {e}\n")


def get_cached_model(provider: str) -> Optional[str]:
    """Get cached model selection for a provider."""
    cache = load_model_cache()
    return cache.get(provider)


def set_cached_model(provider: str, model: str):
    """Cache model selection for a provider."""
    cache = load_model_cache()
    cache[provider] = model
    cache['updated_at'] = datetime.now(timezone.utc).isoformat()
    save_model_cache(cache)

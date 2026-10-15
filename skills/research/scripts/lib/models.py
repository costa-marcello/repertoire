"""Model auto-selection for research skill."""

import re
import sys
from typing import Dict, List, Optional, Tuple

from . import cache, http

# The model IDs below are hard-coded defaults that were current when this
# skill was written. Providers retire models, so verify them against the
# provider docs (platform.openai.com/docs/models, docs.x.ai/docs/models)
# when a call fails with "model not found". Users can override without
# editing code: OPENAI_MODEL_POLICY=pinned + OPENAI_MODEL_PIN=<id>, or
# XAI_MODEL_POLICY=pinned + XAI_MODEL_PIN=<id> (see SKILL.md, "API keys").

# OpenAI API. "auto" picks the newest mainline gpt-5 model from the models
# endpoint; this list is used only when that call fails or finds none.
OPENAI_MODELS_URL = "https://api.openai.com/v1/models"
OPENAI_FALLBACK_MODELS = ["gpt-5.2", "gpt-5.1", "gpt-5", "gpt-4o"]

# xAI API. The x_search tool needs a grok-4 family model. Both policy names
# map to one fixed default; it is not resolved from the models endpoint, so
# "latest" does not follow new releases. Pin a newer model to move on.
XAI_MODELS_URL = "https://api.x.ai/v1/models"
XAI_ALIASES = {
    "latest": "grok-4-1-fast",
    "stable": "grok-4-1-fast",
}


def parse_version(model_id: str) -> Optional[Tuple[int, ...]]:
    """Parse semantic version from model ID.

    Examples:
        gpt-5 -> (5,)
        gpt-5.2 -> (5, 2)
        gpt-5.2.1 -> (5, 2, 1)
    """
    match = re.search(r'(\d+(?:\.\d+)*)', model_id)
    if match:
        return tuple(int(x) for x in match.group(1).split('.'))
    return None


def is_mainline_openai_model(model_id: str) -> bool:
    """Check if model is a mainline GPT model (not mini/nano/chat/codex/pro)."""
    model_lower = model_id.lower()

    # Must be gpt-5 series
    if not re.match(r'^gpt-5(\.\d+)*$', model_lower):
        return False

    # Exclude variants
    excludes = ['mini', 'nano', 'chat', 'codex', 'pro', 'preview', 'turbo']
    for exc in excludes:
        if exc in model_lower:
            return False

    return True


def select_openai_model(
    api_key: str,
    policy: str = "auto",
    pin: Optional[str] = None,
    mock_models: Optional[List[Dict]] = None,
) -> str:
    """Select the best OpenAI model based on policy.

    Args:
        api_key: OpenAI API key
        policy: 'auto' or 'pinned'
        pin: Model to use if policy is 'pinned'
        mock_models: Mock model list for testing

    Returns:
        Selected model ID
    """
    if policy == "pinned" and pin:
        return pin

    # Check cache first. A mock list (--mock or a test) never reads or
    # writes the real cache.
    if mock_models is None:
        cached = cache.get_cached_model("openai")
        if cached:
            return cached

    # Fetch model list
    if mock_models is not None:
        models = mock_models
    else:
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            response = http.get(OPENAI_MODELS_URL, headers=headers)
            models = response.get("data", [])
        except http.HTTPError as e:
            # Fall back to known models, and say why (HTTP 401 means a bad key)
            sys.stderr.write(
                f"[MODELS] Could not list OpenAI models ({e}); using {OPENAI_FALLBACK_MODELS[0]}\n"
            )
            sys.stderr.flush()
            return OPENAI_FALLBACK_MODELS[0]

    # Filter to mainline models
    candidates = [m for m in models if is_mainline_openai_model(m.get("id", ""))]

    if not candidates:
        # No gpt-5 models found, use fallback
        return OPENAI_FALLBACK_MODELS[0]

    # Sort by version (descending), then by created timestamp
    def sort_key(m):
        version = parse_version(m.get("id", "")) or (0,)
        created = m.get("created", 0)
        return (version, created)

    candidates.sort(key=sort_key, reverse=True)
    selected = candidates[0]["id"]

    # Cache the selection
    if mock_models is None:
        cache.set_cached_model("openai", selected)

    return selected


def select_xai_model(
    api_key: str,
    policy: str = "latest",
    pin: Optional[str] = None,
    mock_models: Optional[List[Dict]] = None,
) -> str:
    """Select the best xAI model based on policy.

    Args:
        api_key: xAI API key
        policy: 'latest', 'stable', or 'pinned'
        pin: Model to use if policy is 'pinned'
        mock_models: Mock model list for testing

    Returns:
        Selected model ID
    """
    if policy == "pinned" and pin:
        return pin

    # Use alias system
    if policy in XAI_ALIASES:
        alias = XAI_ALIASES[policy]

        # A mock list (--mock or a test) never reads or writes the real cache
        if mock_models is not None:
            return alias

        # Check cache first
        cached = cache.get_cached_model("xai")
        if cached:
            return cached

        # Cache the alias
        cache.set_cached_model("xai", alias)
        return alias

    # Default to latest
    return XAI_ALIASES["latest"]


def get_models(
    config: Dict,
    mock_openai_models: Optional[List[Dict]] = None,
    mock_xai_models: Optional[List[Dict]] = None,
) -> Dict[str, Optional[str]]:
    """Get selected models for both providers.

    Returns:
        Dict with 'openai' and 'xai' keys
    """
    result = {"openai": None, "xai": None}

    if config.get("OPENAI_API_KEY"):
        result["openai"] = select_openai_model(
            config["OPENAI_API_KEY"],
            config.get("OPENAI_MODEL_POLICY", "auto"),
            config.get("OPENAI_MODEL_PIN"),
            mock_openai_models,
        )

    if config.get("XAI_API_KEY"):
        result["xai"] = select_xai_model(
            config["XAI_API_KEY"],
            config.get("XAI_MODEL_POLICY", "latest"),
            config.get("XAI_MODEL_PIN"),
            mock_xai_models,
        )

    return result

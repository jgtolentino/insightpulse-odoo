"""Client factories for interacting with OpenAI services."""

from __future__ import annotations

from functools import lru_cache
from typing import Optional, TYPE_CHECKING

from .config import OpenAIConfig

if TYPE_CHECKING:  # pragma: no cover - imported for typing only
    from openai import OpenAI


@lru_cache(maxsize=1)
def get_openai_client(config: Optional[OpenAIConfig] = None) -> "OpenAI":
    """Return a cached OpenAI client configured from the environment."""

    config = config or OpenAIConfig.from_env()
    api_key = config.ensure_api_key()

    from openai import OpenAI  # Imported lazily to keep rule-based workflows lightweight

    client = OpenAI(
        api_key=api_key,
        organization=config.organization,
        project=config.project,
    )
    return client

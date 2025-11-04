"""OpenAI-driven automation stack for InsightPulse Odoo."""

from .config import OpenAIConfig
from .clients import get_openai_client

__all__ = ["OpenAIConfig", "get_openai_client"]

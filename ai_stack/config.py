"""Configuration helpers for the OpenAI-powered automation stack."""

from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(slots=True)
class OpenAIConfig:
    """Runtime configuration for accessing OpenAI services."""

    api_key: str | None
    model: str = "gpt-4.1-mini"
    organization: str | None = None
    project: str | None = None

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        """Build configuration from the current environment."""

        return cls(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            organization=os.getenv("OPENAI_ORG_ID"),
            project=os.getenv("OPENAI_PROJECT"),
        )

    def ensure_api_key(self) -> str:
        """Return the API key or raise a helpful error."""

        if not self.api_key:
            raise RuntimeError(
                "Missing OPENAI_API_KEY environment variable. "
                "Set it to run the OpenAI-powered classifiers."
            )
        return self.api_key

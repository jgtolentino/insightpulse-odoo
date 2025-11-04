"""Runtime helpers for cookbook-style AI stacks."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from .clients import get_openai_client
from .config import OpenAIConfig
from .responses import ResponsesRunner


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class StackRuntime:
    """Centralise configuration, clients, and runtime toggles.

    The OpenAI cookbook recommends funnelling model access through a single
    runtime context so instrumentation and fallbacks are easier to maintain.
    """

    config: OpenAIConfig
    enable_tracing: bool = False

    @classmethod
    def from_env(cls, *, enable_tracing: bool = False) -> "StackRuntime":
        """Instantiate the runtime using environment-driven configuration."""

        config = OpenAIConfig.from_env()
        runtime = cls(config=config, enable_tracing=enable_tracing)
        runtime._log_configuration()
        return runtime

    def ensure_client(self):
        """Return a cached OpenAI client for the configured environment."""

        return get_openai_client(self.config)

    def responses_runner(self, *, model: str | None = None) -> ResponsesRunner:
        """Return a structured Responses runner bound to this runtime."""

        client = self.ensure_client()
        return ResponsesRunner(client=client, model=model or self.config.model)

    def _log_configuration(self) -> None:
        if LOGGER.isEnabledFor(logging.INFO):
            scrubbed = "***" if self.config.api_key else "missing"
            LOGGER.info(
                "Initialised StackRuntime (model=%s, api_key=%s, org=%s, project=%s)",
                self.config.model,
                scrubbed,
                self.config.organization or "-",
                self.config.project or "-",
            )


__all__ = ["StackRuntime"]

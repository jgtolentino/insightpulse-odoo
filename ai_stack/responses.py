"""Helpers around the OpenAI Responses API following cookbook patterns."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence, Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError


T = TypeVar("T", bound=BaseModel)


class StructuredResponseError(RuntimeError):
    """Raised when the Responses API cannot return structured data."""


@dataclass(slots=True)
class ResponsesRunner:
    """Thin wrapper that centralises structured Response calls."""

    client: OpenAI
    model: str

    def structured(
        self,
        *,
        input_messages: Sequence[dict],
        response_model: Type[T],
        **kwargs,
    ) -> T:
        """Execute a structured responses call returning ``response_model``."""

        try:
            parsed: T = self.client.responses.parse(  # type: ignore[assignment]
                model=self.model,
                input=list(input_messages),
                response_format=response_model,
                **kwargs,
            )
            return parsed
        except ValidationError as exc:
            raise StructuredResponseError("Structured response failed validation") from exc
        except Exception as exc:  # noqa: BLE001
            raise StructuredResponseError("Structured response invocation failed") from exc

    def raw(self, *, input_messages: Sequence[dict], **kwargs) -> Any:
        """Fallback to returning the raw ``Response`` payload."""

        try:
            return self.client.responses.create(
                model=self.model,
                input=list(input_messages),
                **kwargs,
            )
        except Exception as exc:  # noqa: BLE001
            raise StructuredResponseError("Raw response invocation failed") from exc


__all__ = ["ResponsesRunner", "StructuredResponseError"]

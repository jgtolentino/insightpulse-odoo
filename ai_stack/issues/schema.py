"""Structured outputs for LLM-backed issue classification."""

from __future__ import annotations

from pydantic import BaseModel, Field

from .types import AreaType, DecisionType


class IssueClassificationPayload(BaseModel):
    """Typed payload returned by the Responses API."""

    domain: str = Field(default="", description="Primary business domain focus")
    capabilities: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    decision: DecisionType = Field(default=DecisionType.IPAI)
    area: AreaType = Field(default=AreaType.CONNECTOR)
    acceptance_criteria: list[str] = Field(default_factory=list)

    model_config = {
        "use_enum_values": True,
        "populate_by_name": True,
        "extra": "ignore",
    }


__all__ = ["IssueClassificationPayload"]

from __future__ import annotations

import abc
import dataclasses
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

try:
    # Optional import; memory should be pluggable
    from memory.vector_store import AgentMemory
except ImportError:  # pragma: no cover
    AgentMemory = Any  # type: ignore[misc]


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class AgentState:
    """
    Shared state passed into and between agents during a workflow run.

    This is intentionally minimal and JSON-serializable so it can be
    persisted by `automation/workflow_engine.py`.
    """
    run_id: str
    actor: str                      # e.g. "bir_compliance_orchestrator"
    user_id: Optional[str] = None   # business user / owner
    tenant_id: Optional[str] = None
    context: Dict[str, Any] = dataclasses.field(default_factory=dict)
    created_at: datetime = dataclasses.field(default_factory=datetime.utcnow)
    updated_at: datetime = dataclasses.field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "actor": self.actor,
            "user_id": self.user_id,
            "tenant_id": self.tenant_id,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentState":
        return cls(
            run_id=data["run_id"],
            actor=data["actor"],
            user_id=data.get("user_id"),
            tenant_id=data.get("tenant_id"),
            context=data.get("context", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()


class BaseAgent(abc.ABC):
    """
    Base class for all agents in `agents/`.

    Responsibilities:
    - Define a stable interface: `plan()` and `execute()`.
    - Provide structured logging and telemetry hooks.
    - Optionally integrate with AgentMemory (via subclass).
    """

    id: str = "base_agent"
    description: str = "Abstract base agent"

    def __init__(
        self,
        state: AgentState,
        memory: Optional[AgentMemory] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.state = state
        self.memory = memory
        self.config = config or {}

    @abc.abstractmethod
    def plan(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Produce a high-level plan for the requested action.

        Examples:
        - List steps to gather Odoo records for BIR 2550Q.
        - Suggest reconciliation steps for a given period.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute the agent's core action.

        This must be idempotent or use `workflow_engine` for
        idempotency/retries. It should return a structured result.

        For high-risk operations, `execute()` should remain in
        "proposal" mode and rely on orchestrators for human approval.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------ #
    # Helper methods
    # ------------------------------------------------------------------ #

    def log_event(self, event: str, payload: Optional[Dict[str, Any]] = None) -> None:
        """
        Simple structured logging hook that can be picked up by
        `monitoring/agent_telemetry.py`.
        """
        data = {
            "event": event,
            "agent_id": self.id,
            "run_id": self.state.run_id,
            "actor": self.state.actor,
            "tenant_id": self.state.tenant_id,
            "user_id": self.state.user_id,
            "payload": payload or {},
            "timestamp": datetime.utcnow().isoformat(),
        }
        logger.info("agent_event=%s", json.dumps(data))


class MemoryEnhancedAgent(BaseAgent):
    """
    Base class for agents that use RAG / vector stores.

    This class assumes an `AgentMemory` implementation is passed in.
    """

    def __init__(
        self,
        state: AgentState,
        memory: AgentMemory,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(state=state, memory=memory, config=config)

    def retrieve_context(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Helper to retrieve relevant context snippets for a query, e.g.:

        - BIR regulation sections
        - COA / policy snippets
        - Prior agent run artifacts
        """
        if self.memory is None:
            self.log_event("memory_unavailable", {"query": query})
            return {"matches": []}

        matches = self.memory.search(query=query, top_k=top_k)
        self.log_event("memory_retrieval", {"query": query, "hits": len(matches)})
        return {"matches": matches}

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Type

from agents.base_agent import AgentState, BaseAgent
try:
    from memory.vector_store import AgentMemory
except ImportError:  # pragma: no cover
    AgentMemory = None  # type: ignore[assignment]


class AgentOrchestrator:
    """
    Central orchestrator for multi-agent workflows.

    This is deliberately simple and composable:
    - Creates and passes AgentState between agents.
    - Attaches shared AgentMemory when available.
    - Records a high-level execution trace (list of steps).

    Concrete orchestrators (e.g. month_end_close_orchestrator.py)
    will subclass this and implement domain-specific `run_*` methods.
    """

    def __init__(
        self,
        memory: Optional[AgentMemory] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.memory = memory
        self.config = config or {}

    # ------------------------------------------------------------------ #
    # Core helpers
    # ------------------------------------------------------------------ #

    def _new_state(self, actor: str, user_id: Optional[str] = None,
                   tenant_id: Optional[str] = None) -> AgentState:
        return AgentState(
            run_id=str(uuid.uuid4()),
            actor=actor,
            user_id=user_id,
            tenant_id=tenant_id,
        )

    def _run_agent(
        self,
        agent_cls: Type[BaseAgent],
        state: AgentState,
        *,
        step: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Instantiate an agent with the shared state and optional memory,
        call `plan()` then `execute()`, and return a structured result.
        """
        agent = agent_cls(state=state, memory=self.memory)
        plan = agent.plan(**kwargs)
        agent.log_event("plan_generated", {"step": step, "plan": plan})

        result = agent.execute(**kwargs)
        agent.log_event("step_executed", {"step": step, "result_summary": list(result.keys())})

        state.touch()
        return {
            "step": step,
            "agent_id": agent.id,
            "plan": plan,
            "result": result,
        }

    # ------------------------------------------------------------------ #
    # Example workflow skeletons
    # ------------------------------------------------------------------ #

    def run_month_end_close(
        self,
        user_id: str,
        tenant_id: str,
        *,
        start_date: str,
        end_date: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Example skeleton for a Month-End Close orchestrated workflow.

        Concrete implementation (in month_end_close_orchestrator.py) should:
        - Import this class and subclass it.
        - Override this method with actual agent steps and approval gates.
        """
        state = self._new_state(actor="month_end_close_orchestrator",
                                user_id=user_id, tenant_id=tenant_id)
        trace: List[Dict[str, Any]] = []

        # Placeholder: actual implementation is added in the specialized orchestrator.
        # e.g.:
        # 1. Reconciliation agent
        # 2. Expense validation agent
        # 3. Financial reporting agent

        return {
            "run_id": state.run_id,
            "workflow": "month_end_close",
            "start_date": start_date,
            "end_date": end_date,
            "trace": trace,
            "status": "not_implemented",
        }

    def run_bir_compliance(
        self,
        user_id: str,
        tenant_id: str,
        *,
        period: str,
        forms: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Example skeleton for a BIR compliance orchestrated workflow.

        The concrete orchestrator will:
        - Determine which forms are due (e.g. 1601-C, 2550Q).
        - Call the BIR compliance agent to prepare draft submissions.
        - (Optionally) hand off to RPA (BIR portal) after human approval.
        """
        state = self._new_state(actor="bir_compliance_orchestrator",
                                user_id=user_id, tenant_id=tenant_id)
        trace: List[Dict[str, Any]] = []

        return {
            "run_id": state.run_id,
            "workflow": "bir_compliance",
            "period": period,
            "forms": forms or [],
            "trace": trace,
            "status": "not_implemented",
        }

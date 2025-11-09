"""
Workflows package for InsightPulse Odoo agentic architecture.

This package contains orchestrators that compose agents into end-to-end
multi-step workflows with human-in-the-loop approval gates.
"""

from workflows.orchestrator import AgentOrchestrator

__all__ = ["AgentOrchestrator"]

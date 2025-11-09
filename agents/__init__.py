"""
Agents package for InsightPulse Odoo agentic architecture.

This package contains the base agent classes and domain-specific agents
for autonomous finance operations.
"""

from agents.base_agent import AgentState, BaseAgent, MemoryEnhancedAgent

__all__ = ["AgentState", "BaseAgent", "MemoryEnhancedAgent"]

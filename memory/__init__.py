"""
Memory package for InsightPulse Odoo agentic architecture.

This package provides vector stores, knowledge graphs, and hybrid knowledge bases
for agent RAG (Retrieval-Augmented Generation) operations.
"""

from memory.vector_store import AgentMemory, MemoryRecord

__all__ = ["AgentMemory", "MemoryRecord"]

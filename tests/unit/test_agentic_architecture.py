"""
Unit tests for the agentic architecture foundational components.

Tests cover:
- AgentState serialization and deserialization
- AgentOrchestrator initialization
- AgentMemory basic operations
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List

import pytest

from agents.base_agent import AgentState, BaseAgent, MemoryEnhancedAgent
from workflows.orchestrator import AgentOrchestrator
from memory.vector_store import AgentMemory, MemoryRecord


class TestAgentState:
    """Test AgentState serialization and state management."""

    def test_agent_state_creation(self):
        """Test creating an AgentState instance."""
        state = AgentState(
            run_id="test-run-123",
            actor="test_orchestrator",
            user_id="user-456",
            tenant_id="tenant-789",
        )
        
        assert state.run_id == "test-run-123"
        assert state.actor == "test_orchestrator"
        assert state.user_id == "user-456"
        assert state.tenant_id == "tenant-789"
        assert isinstance(state.context, dict)
        assert isinstance(state.created_at, datetime)
        assert isinstance(state.updated_at, datetime)

    def test_agent_state_to_dict(self):
        """Test serializing AgentState to dictionary."""
        state = AgentState(
            run_id="test-run-123",
            actor="test_orchestrator",
            user_id="user-456",
            tenant_id="tenant-789",
            context={"key": "value"},
        )
        
        state_dict = state.to_dict()
        
        assert state_dict["run_id"] == "test-run-123"
        assert state_dict["actor"] == "test_orchestrator"
        assert state_dict["user_id"] == "user-456"
        assert state_dict["tenant_id"] == "tenant-789"
        assert state_dict["context"]["key"] == "value"
        assert "created_at" in state_dict
        assert "updated_at" in state_dict

    def test_agent_state_from_dict(self):
        """Test deserializing AgentState from dictionary."""
        now = datetime.utcnow()
        state_dict = {
            "run_id": "test-run-123",
            "actor": "test_orchestrator",
            "user_id": "user-456",
            "tenant_id": "tenant-789",
            "context": {"key": "value"},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        
        state = AgentState.from_dict(state_dict)
        
        assert state.run_id == "test-run-123"
        assert state.actor == "test_orchestrator"
        assert state.user_id == "user-456"
        assert state.tenant_id == "tenant-789"
        assert state.context["key"] == "value"
        assert isinstance(state.created_at, datetime)
        assert isinstance(state.updated_at, datetime)

    def test_agent_state_roundtrip(self):
        """Test that AgentState can be serialized and deserialized without data loss."""
        original_state = AgentState(
            run_id="test-run-123",
            actor="test_orchestrator",
            user_id="user-456",
            tenant_id="tenant-789",
            context={"nested": {"data": "value"}},
        )
        
        # Serialize and deserialize
        state_dict = original_state.to_dict()
        restored_state = AgentState.from_dict(state_dict)
        
        assert restored_state.run_id == original_state.run_id
        assert restored_state.actor == original_state.actor
        assert restored_state.user_id == original_state.user_id
        assert restored_state.tenant_id == original_state.tenant_id
        assert restored_state.context == original_state.context

    def test_agent_state_touch(self):
        """Test that touch() updates the updated_at timestamp."""
        state = AgentState(
            run_id="test-run-123",
            actor="test_orchestrator",
        )
        
        original_updated_at = state.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        state.touch()
        
        assert state.updated_at > original_updated_at


class TestAgentOrchestrator:
    """Test AgentOrchestrator initialization and basic operations."""

    def test_orchestrator_initialization(self):
        """Test creating an AgentOrchestrator instance."""
        orchestrator = AgentOrchestrator()
        
        assert orchestrator.memory is None
        assert orchestrator.config == {}

    def test_orchestrator_with_config(self):
        """Test creating an AgentOrchestrator with custom config."""
        config = {"timeout": 30, "retries": 3}
        orchestrator = AgentOrchestrator(config=config)
        
        assert orchestrator.config == config

    def test_orchestrator_new_state(self):
        """Test that _new_state creates valid AgentState instances."""
        orchestrator = AgentOrchestrator()
        
        state = orchestrator._new_state(
            actor="test_orchestrator",
            user_id="user-123",
            tenant_id="tenant-456",
        )
        
        assert isinstance(state, AgentState)
        assert state.actor == "test_orchestrator"
        assert state.user_id == "user-123"
        assert state.tenant_id == "tenant-456"
        # run_id should be a valid UUID
        assert uuid.UUID(state.run_id)

    def test_orchestrator_month_end_close_skeleton(self):
        """Test the month_end_close skeleton returns expected structure."""
        orchestrator = AgentOrchestrator()
        
        result = orchestrator.run_month_end_close(
            user_id="user-123",
            tenant_id="tenant-456",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        
        assert "run_id" in result
        assert result["workflow"] == "month_end_close"
        assert result["start_date"] == "2024-01-01"
        assert result["end_date"] == "2024-01-31"
        assert result["status"] == "not_implemented"
        assert isinstance(result["trace"], list)

    def test_orchestrator_bir_compliance_skeleton(self):
        """Test the bir_compliance skeleton returns expected structure."""
        orchestrator = AgentOrchestrator()
        
        result = orchestrator.run_bir_compliance(
            user_id="user-123",
            tenant_id="tenant-456",
            period="2024-Q1",
            forms=["1601-C", "2550Q"],
        )
        
        assert "run_id" in result
        assert result["workflow"] == "bir_compliance"
        assert result["period"] == "2024-Q1"
        assert result["forms"] == ["1601-C", "2550Q"]
        assert result["status"] == "not_implemented"
        assert isinstance(result["trace"], list)


class TestAgentMemory:
    """Test AgentMemory basic operations."""

    def test_memory_initialization(self):
        """Test creating an AgentMemory instance."""
        memory = AgentMemory()
        
        assert memory.backend is None
        assert memory.collection_name == "insightpulse_memory"

    def test_memory_with_custom_collection(self):
        """Test creating an AgentMemory with custom collection name."""
        memory = AgentMemory(collection_name="test_collection")
        
        assert memory.collection_name == "test_collection"

    def test_memory_search_without_backend(self):
        """Test that search returns empty list when no backend is configured."""
        memory = AgentMemory()
        
        results = memory.search("test query", top_k=5)
        
        assert results == []

    def test_memory_add_records_without_backend(self):
        """Test that add_records is a no-op when no backend is configured."""
        memory = AgentMemory()
        records = [
            MemoryRecord(
                id="record-1",
                text="Test content",
                metadata={"source": "test"},
            )
        ]
        
        # Should not raise an exception
        memory.add_records(records)

    def test_memory_record_creation(self):
        """Test creating a MemoryRecord instance."""
        record = MemoryRecord(
            id="record-1",
            text="Test content",
            metadata={"source": "test", "category": "example"},
        )
        
        assert record.id == "record-1"
        assert record.text == "Test content"
        assert record.metadata["source"] == "test"
        assert record.metadata["category"] == "example"


class TestBaseAgent:
    """Test BaseAgent abstract class."""

    def test_base_agent_cannot_be_instantiated(self):
        """Test that BaseAgent cannot be instantiated directly."""
        state = AgentState(run_id="test", actor="test")
        
        # BaseAgent is abstract, so attempting to instantiate should fail
        # when calling plan() or execute()
        with pytest.raises(TypeError):
            BaseAgent(state=state)


class ConcreteTestAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""
    
    id = "test_agent"
    description = "Test agent for unit tests"

    def plan(self, **kwargs):
        return {"steps": ["step1", "step2"]}

    def execute(self, **kwargs):
        return {"status": "success", "data": kwargs}


class TestConcreteAgent:
    """Test concrete agent implementation."""

    def test_concrete_agent_creation(self):
        """Test creating a concrete agent instance."""
        state = AgentState(run_id="test", actor="test")
        agent = ConcreteTestAgent(state=state)
        
        assert agent.id == "test_agent"
        assert agent.description == "Test agent for unit tests"
        assert agent.state == state
        assert agent.memory is None
        assert agent.config == {}

    def test_concrete_agent_plan(self):
        """Test calling plan on concrete agent."""
        state = AgentState(run_id="test", actor="test")
        agent = ConcreteTestAgent(state=state)
        
        plan = agent.plan()
        
        assert "steps" in plan
        assert plan["steps"] == ["step1", "step2"]

    def test_concrete_agent_execute(self):
        """Test calling execute on concrete agent."""
        state = AgentState(run_id="test", actor="test")
        agent = ConcreteTestAgent(state=state)
        
        result = agent.execute(param1="value1", param2="value2")
        
        assert result["status"] == "success"
        assert result["data"]["param1"] == "value1"
        assert result["data"]["param2"] == "value2"

    def test_concrete_agent_log_event(self, caplog):
        """Test that log_event produces structured logs."""
        import logging
        caplog.set_level(logging.INFO)
        
        state = AgentState(run_id="test-123", actor="test")
        agent = ConcreteTestAgent(state=state)
        
        agent.log_event("test_event", {"key": "value"})
        
        # Check that log was created
        assert len(caplog.records) > 0
        log_message = caplog.records[0].message
        assert "agent_event=" in log_message
        assert "test_event" in log_message
        assert "test_agent" in log_message


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

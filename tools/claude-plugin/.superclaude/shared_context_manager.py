#!/usr/bin/env python3
"""
Shared Context Manager
Coordinates state and knowledge sharing between parallel agents
"""

import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class SharedContextManager:
    """
    Manages shared context and coordination between agents.

    Provides:
    - Shared memory for cross-agent communication
    - Dependency tracking
    - Artifact registry
    - Status coordination
    """

    def __init__(self, path: str = ".superclaude/shared-context/"):
        self.context_path = Path(path)
        self.context_path.mkdir(parents=True, exist_ok=True)

        # Context stores
        self.memory_path = self.context_path / "memory.json"
        self.artifacts_path = self.context_path / "artifacts.json"
        self.status_path = self.context_path / "status.json"

        # Initialize stores
        self.memory = self._load_store(self.memory_path)
        self.artifacts = self._load_store(self.artifacts_path)
        self.status = self._load_store(self.status_path)

    def _load_store(self, path: Path) -> Dict:
        """Load a JSON store or return empty dict."""
        if path.exists():
            with open(path) as f:
                return json.load(f)
        return {}

    def _save_store(self, path: Path, data: Dict):
        """Save a JSON store."""
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    # Memory Operations
    def set_memory(self, key: str, value: Any, agent: str = "system"):
        """
        Store a value in shared memory.

        Args:
            key: Memory key
            value: Value to store (will be JSON serialized)
            agent: Agent that set this memory
        """
        self.memory[key] = {
            "value": value,
            "agent": agent,
            "timestamp": datetime.now().isoformat()
        }
        self._save_store(self.memory_path, self.memory)

    def get_memory(self, key: str) -> Optional[Any]:
        """Retrieve a value from shared memory."""
        if key in self.memory:
            return self.memory[key]["value"]
        return None

    def has_memory(self, key: str) -> bool:
        """Check if a memory key exists."""
        return key in self.memory

    def list_memory_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List all memory keys, optionally filtered by pattern."""
        keys = list(self.memory.keys())
        if pattern:
            keys = [k for k in keys if pattern in k]
        return sorted(keys)

    # Artifact Registry
    def register_artifact(
        self,
        name: str,
        path: str,
        agent: str,
        artifact_type: str = "file",
        metadata: Optional[Dict] = None
    ):
        """
        Register an artifact created by an agent.

        Args:
            name: Artifact name/identifier
            path: Path to artifact
            agent: Agent that created it
            artifact_type: Type (file, directory, module, skill, etc.)
            metadata: Additional metadata
        """
        self.artifacts[name] = {
            "path": path,
            "agent": agent,
            "type": artifact_type,
            "metadata": metadata or {},
            "created": datetime.now().isoformat()
        }
        self._save_store(self.artifacts_path, self.artifacts)

    def get_artifact(self, name: str) -> Optional[Dict]:
        """Get artifact information."""
        return self.artifacts.get(name)

    def list_artifacts(
        self,
        agent: Optional[str] = None,
        artifact_type: Optional[str] = None
    ) -> List[Dict]:
        """
        List artifacts, optionally filtered.

        Args:
            agent: Filter by agent
            artifact_type: Filter by type

        Returns:
            List of artifact records
        """
        artifacts = []

        for name, info in self.artifacts.items():
            # Apply filters
            if agent and info["agent"] != agent:
                continue
            if artifact_type and info["type"] != artifact_type:
                continue

            artifacts.append({
                "name": name,
                **info
            })

        return sorted(artifacts, key=lambda x: x["created"], reverse=True)

    # Agent Status Coordination
    def update_agent_status(
        self,
        agent: str,
        status: str,
        message: Optional[str] = None,
        progress: Optional[float] = None
    ):
        """
        Update agent status.

        Args:
            agent: Agent name
            status: Status (idle, working, blocked, completed, failed)
            message: Status message
            progress: Progress percentage (0.0-1.0)
        """
        self.status[agent] = {
            "status": status,
            "message": message,
            "progress": progress,
            "updated": datetime.now().isoformat()
        }
        self._save_store(self.status_path, self.status)

    def get_agent_status(self, agent: str) -> Optional[Dict]:
        """Get agent status."""
        return self.status.get(agent)

    def get_all_agent_status(self) -> Dict[str, Dict]:
        """Get status for all agents."""
        return dict(self.status)

    # Dependency Management
    def mark_dependency_ready(self, dependency: str, agent: str):
        """Mark a dependency as ready for other agents."""
        self.set_memory(f"dependency:{dependency}", {
            "ready": True,
            "provided_by": agent,
            "completed": datetime.now().isoformat()
        })

    def is_dependency_ready(self, dependency: str) -> bool:
        """Check if a dependency is ready."""
        dep_data = self.get_memory(f"dependency:{dependency}")
        return dep_data and dep_data.get("ready", False)

    def wait_for_dependency(self, dependency: str, timeout: int = 300) -> bool:
        """
        Wait for a dependency to be ready (stub - would poll in real implementation).

        Args:
            dependency: Dependency to wait for
            timeout: Timeout in seconds

        Returns:
            True if ready, False if timeout
        """
        # In real implementation, this would poll with exponential backoff
        # For now, just check once
        return self.is_dependency_ready(dependency)

    # Coordination Primitives
    def acquire_lock(self, resource: str, agent: str) -> bool:
        """
        Acquire a lock on a resource.

        Args:
            resource: Resource to lock
            agent: Agent requesting lock

        Returns:
            True if lock acquired, False if already locked
        """
        lock_key = f"lock:{resource}"

        if self.has_memory(lock_key):
            lock_data = self.get_memory(lock_key)
            # Check if lock is stale (> 5 minutes)
            lock_time = datetime.fromisoformat(lock_data["timestamp"])
            age = (datetime.now() - lock_time).total_seconds()

            if age < 300:  # 5 minutes
                return False

        # Acquire lock
        self.set_memory(lock_key, {
            "locked_by": agent,
            "timestamp": datetime.now().isoformat()
        })
        return True

    def release_lock(self, resource: str, agent: str):
        """Release a lock on a resource."""
        lock_key = f"lock:{resource}"

        if self.has_memory(lock_key):
            lock_data = self.get_memory(lock_key)
            if lock_data.get("locked_by") == agent:
                # Remove lock
                if lock_key in self.memory:
                    del self.memory[lock_key]
                    self._save_store(self.memory_path, self.memory)

    # Summary Operations
    def save_summary(self, summary: Dict, filename: str = "summary.md"):
        """Save execution summary to markdown."""
        summary_path = self.context_path / filename

        with open(summary_path, 'w') as f:
            f.write(f"# Execution Summary\n\n")
            f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")

            # Write summary sections
            for key, value in summary.items():
                f.write(f"## {key.replace('_', ' ').title()}\n\n")

                if isinstance(value, dict):
                    for k, v in value.items():
                        f.write(f"- **{k}**: {v}\n")
                elif isinstance(value, list):
                    for item in value:
                        f.write(f"- {item}\n")
                else:
                    f.write(f"{value}\n")

                f.write("\n")

    def clear_all(self):
        """Clear all shared context (use with caution!)."""
        self.memory = {}
        self.artifacts = {}
        self.status = {}

        self._save_store(self.memory_path, self.memory)
        self._save_store(self.artifacts_path, self.artifacts)
        self._save_store(self.status_path, self.status)

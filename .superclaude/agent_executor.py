#!/usr/bin/env python3
"""
Agent Executor
Executes agent tasks and coordinates with SuperClaude framework
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class AgentExecutor:
    """
    Executes tasks for SuperClaude agents.

    Coordinates with:
    - Shared context for agent communication
    - Skills library for domain expertise
    - Claude Code for actual task execution
    """

    def __init__(self, config: Dict, shared_context):
        self.config = config
        self.shared_context = shared_context
        self.agents_config = config.get("agents", {})

    def execute_agent(
        self,
        agent: Dict,
        worktree_path: Optional[Path] = None
    ) -> Dict:
        """
        Execute all tasks for an agent.

        Args:
            agent: Agent configuration from workflow
            worktree_path: Path to agent's worktree (if parallel execution)

        Returns:
            Execution result with task outcomes
        """
        agent_name = agent["agent"]
        tasks = agent.get("tasks", [])

        print(f"\n{'='*60}")
        print(f"🤖 Executing Agent: {agent_name}")
        print(f"{'='*60}")

        if worktree_path:
            print(f"📂 Worktree: {worktree_path}")

        # Update agent status
        self.shared_context.update_agent_status(
            agent_name,
            "working",
            f"Starting {len(tasks)} tasks"
        )

        # Execute tasks
        task_results = []

        for i, task in enumerate(tasks, 1):
            print(f"\n📋 Task {i}/{len(tasks)}")

            try:
                result = self.execute_task(
                    agent_name=agent_name,
                    agent_config=self.agents_config.get(agent_name, {}),
                    task=task,
                    worktree_path=worktree_path
                )

                task_results.append({
                    "task": i,
                    "status": "completed",
                    "result": result
                })

                # Update progress
                progress = i / len(tasks)
                self.shared_context.update_agent_status(
                    agent_name,
                    "working",
                    f"Task {i}/{len(tasks)} completed",
                    progress
                )

            except Exception as e:
                task_results.append({
                    "task": i,
                    "status": "failed",
                    "error": str(e)
                })

                # Update status
                self.shared_context.update_agent_status(
                    agent_name,
                    "failed",
                    f"Task {i} failed: {str(e)}"
                )

                # Stop on failure unless continue_on_error
                if not task.get("continue_on_error", False):
                    break

        # Final status
        all_completed = all(r["status"] == "completed" for r in task_results)

        self.shared_context.update_agent_status(
            agent_name,
            "completed" if all_completed else "failed",
            f"Completed {len([r for r in task_results if r['status'] == 'completed'])}/{len(tasks)} tasks",
            1.0 if all_completed else None
        )

        return {
            "agent": agent_name,
            "tasks_completed": len([r for r in task_results if r["status"] == "completed"]),
            "tasks_failed": len([r for r in task_results if r["status"] == "failed"]),
            "task_results": task_results
        }

    def execute_task(
        self,
        agent_name: str,
        agent_config: Dict,
        task: Dict,
        worktree_path: Optional[Path] = None
    ) -> Dict:
        """
        Execute a single task.

        Args:
            agent_name: Name of agent executing task
            agent_config: Agent configuration
            task: Task configuration
            worktree_path: Path to agent's worktree

        Returns:
            Task execution result
        """
        # Determine task type
        if "command" in task:
            # Shell command task
            return self._execute_command_task(task, worktree_path)

        elif "task" in task:
            # Claude Code task (description-based)
            return self._execute_claude_task(
                agent_name,
                agent_config,
                task,
                worktree_path
            )

        elif "category" in task:
            # Deliverable-based task (from workflow definitions)
            return self._execute_deliverable_task(
                agent_name,
                agent_config,
                task,
                worktree_path
            )

        else:
            raise ValueError(f"Unknown task type: {task}")

    def _execute_command_task(
        self,
        task: Dict,
        worktree_path: Optional[Path]
    ) -> Dict:
        """Execute a shell command task."""
        command = task["command"]
        cwd = worktree_path if worktree_path else Path.cwd()

        print(f"  💻 Running command: {command[:100]}...")

        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=str(cwd),
                capture_output=True,
                text=True,
                timeout=task.get("timeout", 300)
            )

            if result.returncode != 0:
                raise RuntimeError(f"Command failed: {result.stderr}")

            return {
                "type": "command",
                "command": command,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Command timed out after {task.get('timeout', 300)}s")

    def _execute_claude_task(
        self,
        agent_name: str,
        agent_config: Dict,
        task: Dict,
        worktree_path: Optional[Path]
    ) -> Dict:
        """
        Execute a Claude Code task.

        This is a stub - in real implementation, this would:
        1. Format task with agent context and skills
        2. Invoke Claude Code with appropriate prompt
        3. Collect and validate results
        """
        task_description = task["task"]
        output_path = task.get("output")

        print(f"  🤖 Claude Task: {task_description}")

        # Get agent skills
        skills = agent_config.get("skills", [])
        if skills:
            print(f"  📚 Using skills: {', '.join(skills)}")

        # In real implementation, would invoke Claude Code here
        # For now, just log and create placeholder

        result = {
            "type": "claude_task",
            "description": task_description,
            "agent": agent_name,
            "skills_used": skills,
            "status": "simulated"
        }

        # Create output file if specified
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                f.write(f"# {task_description}\n\n")
                f.write(f"Created by: {agent_name}\n")
                f.write(f"Date: {datetime.now().isoformat()}\n\n")
                f.write("*This is a placeholder - would contain actual task output*\n")

            result["output"] = str(output_file)

            # Register artifact
            self.shared_context.register_artifact(
                name=output_file.stem,
                path=str(output_file),
                agent=agent_name,
                artifact_type="document"
            )

        return result

    def _execute_deliverable_task(
        self,
        agent_name: str,
        agent_config: Dict,
        task: Dict,
        worktree_path: Optional[Path]
    ) -> Dict:
        """
        Execute a deliverable-based task (from workflow definitions).

        These are high-level tasks with expected deliverables.
        """
        category = task["category"]
        description = task.get("description", "")
        deliverables = task.get("deliverables", [])

        print(f"  📦 Category: {category}")
        print(f"  📝 {description}")
        print(f"  🎯 Deliverables: {len(deliverables)}")

        # Track deliverable creation
        created_artifacts = []

        for deliverable in deliverables:
            deliverable_name = deliverable.get("name", "unnamed")
            files = deliverable.get("files", [])

            print(f"    ➤ {deliverable_name}")

            # Create deliverable files
            for file_path in files:
                # Determine full path
                if worktree_path:
                    full_path = worktree_path / file_path
                else:
                    full_path = Path(file_path)

                # Create directory
                full_path.parent.mkdir(parents=True, exist_ok=True)

                # Create file (placeholder - would be actual content)
                with open(full_path, 'w') as f:
                    f.write(f"# {deliverable_name}\n\n")
                    f.write(f"Category: {category}\n")
                    f.write(f"Agent: {agent_name}\n")
                    f.write(f"Created: {datetime.now().isoformat()}\n\n")
                    f.write("*This is a placeholder - would contain actual deliverable content*\n")

                created_artifacts.append(str(full_path))

                # Register artifact
                self.shared_context.register_artifact(
                    name=full_path.stem,
                    path=str(full_path),
                    agent=agent_name,
                    artifact_type="deliverable",
                    metadata={
                        "category": category,
                        "deliverable": deliverable_name
                    }
                )

        return {
            "type": "deliverable",
            "category": category,
            "description": description,
            "artifacts_created": len(created_artifacts),
            "artifacts": created_artifacts
        }

    def validate_task_result(self, task: Dict, result: Dict) -> bool:
        """
        Validate task execution result.

        Args:
            task: Task configuration
            result: Execution result

        Returns:
            True if validation passes
        """
        validation = task.get("validation", [])

        if not validation:
            return True

        # Check each validation criterion
        for criterion in validation:
            # File existence checks
            if "file_exists" in criterion:
                file_path = Path(criterion["file_exists"])
                if not file_path.exists():
                    print(f"  ❌ Validation failed: {file_path} does not exist")
                    return False

            # Output checks
            if "output_contains" in criterion:
                required_text = criterion["output_contains"]
                output = result.get("stdout", "") + result.get("output", "")
                if required_text not in output:
                    print(f"  ❌ Validation failed: Output does not contain '{required_text}'")
                    return False

        return True

#!/usr/bin/env python3
"""
SuperClaude Orchestrator
Main entry point for multi-agent coordination

Usage:
    python .superclaude/orchestrate.py --workflow bootstrap
    python .superclaude/orchestrate.py --workflow build_full_stack --parallel
"""

import argparse
import yaml
import json
import sys
from pathlib import Path
from typing import Dict, List
from datetime import datetime

from worktree_manager import WorktreeManager
from agent_executor import AgentExecutor
from shared_context_manager import SharedContextManager


class SuperClaudeOrchestrator:
    """
    Multi-agent orchestration engine.

    Coordinates multiple Claude Code agents working in parallel using:
    - Git worktrees for isolated work
    - Shared context for coordination
    - Intelligent merge strategies
    """

    def __init__(self, config_path: str = ".superclaude/config.yml"):
        # Load configuration
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize managers
        self.worktree_mgr = WorktreeManager(
            base_path=self.config.get("parallel_execution", {}).get("work_trees", {}).get("base_path", ".worktrees/")
        )
        self.shared_context = SharedContextManager(
            path=self.config.get("shared_memory", {}).get("path", ".superclaude/shared-context/")
        )
        self.agent_executor = AgentExecutor(
            config=self.config,
            shared_context=self.shared_context
        )

        # Track execution
        self.execution_log = []
        self.start_time = None
        self.end_time = None

    def load_workflow(self, workflow_name: str) -> Dict:
        """Load workflow definition from YAML."""
        workflow_path = Path(f".superclaude/workflows/{workflow_name}.yml")

        if not workflow_path.exists():
            raise FileNotFoundError(f"Workflow not found: {workflow_path}")

        with open(workflow_path) as f:
            return yaml.safe_load(f)

    def execute_workflow(
        self,
        workflow_name: str,
        parallel: bool = False,
        dry_run: bool = False
    ) -> Dict:
        """
        Execute a workflow.

        Args:
            workflow_name: Name of workflow (e.g., "bootstrap")
            parallel: Enable parallel execution
            dry_run: Simulate without executing

        Returns:
            Execution result with metrics
        """
        print(f"\n{'='*60}")
        print(f"🚀 SuperClaude Orchestrator")
        print(f"{'='*60}")
        print(f"Workflow: {workflow_name}")
        print(f"Parallel: {parallel}")
        print(f"Dry Run: {dry_run}")
        print(f"{'='*60}\n")

        # Load workflow
        workflow = self.load_workflow(workflow_name)
        self.start_time = datetime.now()

        # Validate prerequisites
        if not dry_run:
            self._validate_prerequisites(workflow.get("prerequisites", []))

        # Execute based on mode
        if parallel and workflow.get("workflow", {}).get("parallel", False):
            result = self._execute_parallel(workflow, dry_run)
        else:
            result = self._execute_sequential(workflow, dry_run)

        self.end_time = datetime.now()

        # Generate summary
        summary = self._generate_summary(workflow, result)

        # Save execution log
        self._save_execution_log(workflow_name, summary)

        return summary

    def _validate_prerequisites(self, prerequisites: List[str]):
        """Validate that prerequisites are met."""
        print("📋 Checking prerequisites...")

        for prereq in prerequisites:
            if prereq == "Bootstrap workflow completed":
                if not Path(".superclaude/shared-context/bootstrap-summary.md").exists():
                    raise RuntimeError("Bootstrap not completed. Run: make superclaude-bootstrap")

            # Add more checks as needed
            print(f"  ✅ {prereq}")

        print()

    def _execute_sequential(self, workflow: Dict, dry_run: bool) -> Dict:
        """Execute workflow steps sequentially."""
        print("🔄 Executing workflow sequentially\n")

        results = []
        steps = workflow.get("workflow", {}).get("steps", workflow.get("steps", []))

        for step_num, step in enumerate(steps, 1):
            print(f"📍 Step {step_num}/{len(steps)}: {step.get('name', step.get('description', 'Unknown'))}")

            if dry_run:
                print("  [DRY RUN] Skipping execution")
                results.append({"step": step_num, "status": "skipped"})
                continue

            # Execute step
            try:
                step_result = self._execute_step(step)
                results.append({"step": step_num, "status": "completed", "result": step_result})
                print(f"  ✅ Completed\n")
            except Exception as e:
                results.append({"step": step_num, "status": "failed", "error": str(e)})
                print(f"  ❌ Failed: {e}\n")

                # Stop on failure unless continue_on_error
                if not step.get("continue_on_error", False):
                    break

        return {"mode": "sequential", "results": results}

    def _execute_parallel(self, workflow: Dict, dry_run: bool) -> Dict:
        """Execute workflow agents in parallel using worktrees."""
        print("⚡ Executing workflow in parallel\n")

        agents = workflow.get("agents", [])

        if not agents:
            raise ValueError("No agents defined for parallel execution")

        # Setup worktrees
        print("🌳 Setting up git worktrees...")
        worktrees = {}

        for agent in agents:
            agent_name = agent["agent"]
            worktree_name = agent.get("worktree", f"worktree-{agent_name}")
            branch_name = agent.get("branch", f"feature/{agent_name}")

            if not dry_run:
                worktree_path = self.worktree_mgr.create_worktree(
                    name=worktree_name,
                    branch=branch_name
                )
                worktrees[agent_name] = worktree_path
                print(f"  ✅ {worktree_name} → {worktree_path}")
            else:
                print(f"  [DRY RUN] Would create {worktree_name}")

        print()

        # Execute agents in parallel
        print("🤖 Executing agents in parallel...")
        print("  (Note: Actual parallel execution requires multiple Claude Code instances)")
        print("  (For now, we'll execute sequentially but track for parallel merge)\n")

        results = []

        for agent in agents:
            agent_name = agent["agent"]
            print(f"👤 Agent: {agent_name}")
            print(f"   Worktree: {worktrees.get(agent_name, 'N/A')}")
            print(f"   Tasks: {len(agent.get('tasks', []))}")

            if dry_run:
                print("  [DRY RUN] Skipping execution\n")
                results.append({"agent": agent_name, "status": "skipped"})
                continue

            # Execute agent tasks
            try:
                agent_result = self.agent_executor.execute_agent(
                    agent=agent,
                    worktree_path=worktrees.get(agent_name)
                )
                results.append({"agent": agent_name, "status": "completed", "result": agent_result})
                print(f"  ✅ Completed\n")
            except Exception as e:
                results.append({"agent": agent_name, "status": "failed", "error": str(e)})
                print(f"  ❌ Failed: {e}\n")

        # Merge worktrees
        if not dry_run:
            print("🔀 Merging worktrees...")
            merge_result = self._merge_worktrees(workflow, worktrees)
            print(f"  ✅ Merge complete\n")
        else:
            merge_result = {"status": "skipped"}

        return {
            "mode": "parallel",
            "results": results,
            "merge": merge_result
        }

    def _execute_step(self, step: Dict) -> Dict:
        """Execute a single workflow step."""
        agent_name = step.get("agent")
        tasks = step.get("tasks", [])

        # Get agent config
        agent_config = self.config.get("agents", {}).get(agent_name, {})

        # Execute tasks
        task_results = []

        for task in tasks:
            task_result = self.agent_executor.execute_task(
                agent_name=agent_name,
                agent_config=agent_config,
                task=task
            )
            task_results.append(task_result)

        return {"tasks": task_results}

    def _merge_worktrees(self, workflow: Dict, worktrees: Dict) -> Dict:
        """Merge all worktrees back to main branch."""
        merge_strategy = workflow.get("merge_strategy", {})
        order = merge_strategy.get("order", list(worktrees.keys()))

        merge_results = []

        for worktree_name in order:
            if worktree_name not in worktrees:
                continue

            result = self.worktree_mgr.merge_worktree(
                worktree_path=worktrees[worktree_name],
                strategy=merge_strategy.get("type", "auto_merge")
            )
            merge_results.append(result)

        # Cleanup worktrees
        if merge_strategy.get("cleanup_on_complete", False):
            self.worktree_mgr.cleanup_all()

        return {"merges": merge_results}

    def _generate_summary(self, workflow: Dict, result: Dict) -> Dict:
        """Generate execution summary."""
        duration = (self.end_time - self.start_time).total_seconds()

        summary = {
            "workflow": workflow.get("workflow", {}).get("name"),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "duration_seconds": duration,
            "mode": result.get("mode"),
            "success": all(r.get("status") in ["completed", "skipped"]
                          for r in result.get("results", [])),
            "results": result
        }

        # Print summary
        print(f"\n{'='*60}")
        print(f"📊 Execution Summary")
        print(f"{'='*60}")
        print(f"Workflow: {summary['workflow']}")
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print(f"Mode: {summary['mode']}")
        print(f"Success: {'✅ Yes' if summary['success'] else '❌ No'}")
        print(f"{'='*60}\n")

        return summary

    def _save_execution_log(self, workflow_name: str, summary: Dict):
        """Save execution log for future reference."""
        log_dir = Path(".superclaude/logs")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(log_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"📁 Execution log saved: {log_file}")


def main():
    parser = argparse.ArgumentParser(
        description="SuperClaude Multi-Agent Orchestrator"
    )
    parser.add_argument(
        "--workflow",
        required=True,
        help="Workflow to execute (e.g., bootstrap, build_full_stack)"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel execution"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without running"
    )
    parser.add_argument(
        "--config",
        default=".superclaude/config.yml",
        help="Path to config file"
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = SuperClaudeOrchestrator(config_path=args.config)

    # Execute workflow
    try:
        result = orchestrator.execute_workflow(
            workflow_name=args.workflow,
            parallel=args.parallel,
            dry_run=args.dry_run
        )

        # Exit with appropriate code
        sys.exit(0 if result["success"] else 1)

    except Exception as e:
        print(f"\n❌ Orchestration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

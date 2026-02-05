#!/usr/bin/env python3
"""
Git Worktree Manager
Handles creation, cleanup, and merging of git worktrees for parallel agent execution
"""

import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional


class WorktreeManager:
    """
    Manages git worktrees for parallel agent execution.

    Each agent works in an isolated worktree (separate working directory)
    on its own branch, allowing true parallel development.
    """

    def __init__(self, base_path: str = ".worktrees/"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.worktrees: Dict[str, Path] = {}

    def create_worktree(
        self,
        name: str,
        branch: str,
        base_branch: str = "main"
    ) -> Path:
        """
        Create a new git worktree for agent to work in.

        Args:
            name: Worktree name (e.g., "worktree-ai")
            branch: Branch name (e.g., "feature/ai-infrastructure")
            base_branch: Branch to create from (default: "main")

        Returns:
            Path to worktree directory
        """
        worktree_path = self.base_path / name

        # Remove if already exists
        if worktree_path.exists():
            print(f"  Removing existing worktree: {name}")
            self.remove_worktree(name)

        # Create new branch from base
        try:
            subprocess.run(
                ["git", "branch", branch, base_branch],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            # Branch might already exist
            pass

        # Create worktree
        subprocess.run(
            ["git", "worktree", "add", str(worktree_path), branch],
            check=True,
            capture_output=True
        )

        self.worktrees[name] = worktree_path
        return worktree_path

    def remove_worktree(self, name: str):
        """Remove a worktree and its directory."""
        worktree_path = self.worktrees.get(name, self.base_path / name)

        if worktree_path.exists():
            # Remove git worktree
            subprocess.run(
                ["git", "worktree", "remove", str(worktree_path), "--force"],
                capture_output=True
            )

            # Clean up directory if still exists
            if worktree_path.exists():
                shutil.rmtree(worktree_path)

        # Remove from tracking
        if name in self.worktrees:
            del self.worktrees[name]

    def merge_worktree(
        self,
        worktree_path: Path,
        strategy: str = "auto_merge",
        target_branch: str = "main"
    ) -> Dict:
        """
        Merge worktree branch back to target branch.

        Args:
            worktree_path: Path to worktree
            strategy: Merge strategy ("auto_merge", "manual", "squash")
            target_branch: Branch to merge into (default: "main")

        Returns:
            Merge result with status and details
        """
        # Get branch name from worktree
        result = subprocess.run(
            ["git", "-C", str(worktree_path), "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        branch_name = result.stdout.strip()

        # Switch to target branch
        subprocess.run(
            ["git", "checkout", target_branch],
            check=True,
            capture_output=True
        )

        # Pull latest
        subprocess.run(
            ["git", "pull"],
            check=True,
            capture_output=True
        )

        # Merge based on strategy
        merge_result = {"branch": branch_name, "strategy": strategy}

        try:
            if strategy == "squash":
                # Squash merge
                subprocess.run(
                    ["git", "merge", "--squash", branch_name],
                    check=True,
                    capture_output=True
                )
                subprocess.run(
                    ["git", "commit", "-m", f"Merge {branch_name} (squashed)"],
                    check=True,
                    capture_output=True
                )
            else:
                # Regular merge
                subprocess.run(
                    ["git", "merge", branch_name, "--no-edit"],
                    check=True,
                    capture_output=True
                )

            merge_result["status"] = "success"
            merge_result["message"] = f"Successfully merged {branch_name}"

        except subprocess.CalledProcessError as e:
            merge_result["status"] = "conflict"
            merge_result["message"] = f"Merge conflict in {branch_name}"
            merge_result["error"] = e.stderr.decode() if e.stderr else str(e)

        return merge_result

    def list_worktrees(self) -> List[Dict]:
        """List all active worktrees."""
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )

        worktrees = []
        current = {}

        for line in result.stdout.split('\n'):
            if line.startswith('worktree '):
                if current:
                    worktrees.append(current)
                current = {'path': line.split(' ', 1)[1]}
            elif line.startswith('branch '):
                current['branch'] = line.split(' ', 1)[1]

        if current:
            worktrees.append(current)

        return worktrees

    def cleanup_all(self):
        """Remove all managed worktrees."""
        print(f"🧹 Cleaning up all worktrees...")

        for name in list(self.worktrees.keys()):
            self.remove_worktree(name)

        # Clean up base directory
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
            self.base_path.mkdir(parents=True, exist_ok=True)

        print(f"  ✅ Cleanup complete")

    def get_worktree_status(self, worktree_path: Path) -> Dict:
        """Get git status for a worktree."""
        try:
            # Get status
            result = subprocess.run(
                ["git", "-C", str(worktree_path), "status", "--short"],
                capture_output=True,
                text=True,
                check=True
            )

            # Count changes
            lines = result.stdout.strip().split('\n')
            modified = sum(1 for l in lines if l.startswith(' M'))
            added = sum(1 for l in lines if l.startswith('A '))
            deleted = sum(1 for l in lines if l.startswith(' D'))
            untracked = sum(1 for l in lines if l.startswith('??'))

            return {
                "clean": len(result.stdout.strip()) == 0,
                "modified": modified,
                "added": added,
                "deleted": deleted,
                "untracked": untracked
            }

        except subprocess.CalledProcessError as e:
            return {
                "error": str(e),
                "clean": False
            }

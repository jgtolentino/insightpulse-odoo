#!/usr/bin/env python3
"""
GitHub Issue Reporter for Visual Compliance Violations

This module creates GitHub issues for detected compliance violations,
organized by module and severity. It avoids creating duplicates by
checking existing issues first.
"""

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Set


class IssueLabel(str, Enum):
    """GitHub issue labels for violations"""
    COMPLIANCE = "compliance"
    CRITICAL = "critical"
    HIGH_PRIORITY = "high-priority"
    ENHANCEMENT = "enhancement"
    BUG = "bug"
    DOCUMENTATION = "documentation"


@dataclass
class GitHubIssue:
    """Represents a GitHub issue to be created"""
    title: str
    body: str
    labels: List[str]
    assignees: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        if self.assignees is None:
            result['assignees'] = []
        return result


class GitHubReporter:
    """
    Creates GitHub issues from compliance violations.

    Uses `gh` CLI tool for issue creation and management.
    """

    def __init__(
        self,
        repo: str = "jgtolentino/insightpulse-odoo",
        dry_run: bool = False,
    ):
        """
        Initialize GitHub reporter.

        Args:
            repo: GitHub repository in format "owner/repo"
            dry_run: If True, print issues without creating them
        """
        self.repo = repo
        self.dry_run = dry_run
        self.created_issues: List[str] = []

    def check_gh_cli(self) -> bool:
        """
        Check if gh CLI is installed and authenticated.

        Returns:
            True if gh CLI is available and authenticated
        """
        try:
            result = subprocess.run(
                ["gh", "auth", "status"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def get_existing_issues(self) -> Set[str]:
        """
        Get titles of existing open issues to avoid duplicates.

        Returns:
            Set of issue titles
        """
        try:
            result = subprocess.run(
                [
                    "gh", "issue", "list",
                    "--repo", self.repo,
                    "--state", "open",
                    "--label", "compliance",
                    "--json", "title",
                    "--limit", "1000",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                issues = json.loads(result.stdout)
                return {issue["title"] for issue in issues}

        except (subprocess.TimeoutExpired, json.JSONDecodeError, KeyError):
            pass

        return set()

    def format_violation_issue(
        self,
        module_name: str,
        violations: List[Dict[str, Any]],
        check_type: str,
    ) -> GitHubIssue:
        """
        Format violations into a GitHub issue.

        Args:
            module_name: Name of the module
            violations: List of violation dictionaries
            check_type: Type of compliance check (manifest, directory, naming, readme)

        Returns:
            GitHubIssue object
        """
        # Determine severity
        severities = [v.get("severity", "medium") for v in violations]
        max_severity = "critical" if "critical" in severities else severities[0]

        # Build title
        violation_count = len(violations)
        title = f"[{check_type.upper()}] {module_name}: {violation_count} compliance violation(s)"

        # Build body
        body_parts = [
            f"## Compliance Violations in `{module_name}`\n",
            f"**Check Type:** {check_type}",
            f"**Severity:** {max_severity}",
            f"**Violations:** {violation_count}\n",
        ]

        # Add violation details
        body_parts.append("### Violations\n")
        for i, violation in enumerate(violations, 1):
            vtype = violation.get("violation_type", "unknown")
            description = violation.get("description", "No description")
            current_value = violation.get("current_value", "")
            expected_value = violation.get("expected_value", "")

            body_parts.append(f"#### {i}. {vtype}\n")
            body_parts.append(f"**Description:** {description}\n")

            if current_value:
                body_parts.append(f"**Current:** `{current_value}`")
            if expected_value:
                body_parts.append(f"**Expected:** `{expected_value}`\n")

        # Add fix instructions
        if any(v.get("auto_fixable", False) for v in violations):
            body_parts.append("\n### Auto-Fix Available\n")
            body_parts.append("Some violations can be automatically fixed:\n")
            body_parts.append(f"```bash\npython agents/visual-compliance/src/visual_agent.py --fix\n```\n")

        # Add footer
        body_parts.append("\n---")
        body_parts.append("*This issue was automatically created by Visual Compliance Agent*")

        body = "\n".join(body_parts)

        # Determine labels
        labels = [IssueLabel.COMPLIANCE.value]

        if max_severity == "critical":
            labels.append(IssueLabel.CRITICAL.value)
        elif max_severity == "high":
            labels.append(IssueLabel.HIGH_PRIORITY.value)

        if check_type == "readme":
            labels.append(IssueLabel.DOCUMENTATION.value)
        elif check_type in ["manifest", "directory", "naming"]:
            labels.append(IssueLabel.BUG.value)

        return GitHubIssue(
            title=title,
            body=body,
            labels=labels,
        )

    def create_issue(self, issue: GitHubIssue) -> Optional[str]:
        """
        Create a GitHub issue.

        Args:
            issue: GitHubIssue object

        Returns:
            Issue URL if created, None otherwise
        """
        if self.dry_run:
            print(f"\n[DRY RUN] Would create issue:")
            print(f"  Title: {issue.title}")
            print(f"  Labels: {', '.join(issue.labels)}")
            print(f"  Body preview: {issue.body[:100]}...")
            return None

        try:
            # Build gh command
            cmd = [
                "gh", "issue", "create",
                "--repo", self.repo,
                "--title", issue.title,
                "--body", issue.body,
            ]

            # Add labels
            for label in issue.labels:
                cmd.extend(["--label", label])

            # Add assignees if specified
            if issue.assignees:
                for assignee in issue.assignees:
                    cmd.extend(["--assignee", assignee])

            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                issue_url = result.stdout.strip()
                print(f"✅ Created issue: {issue_url}")
                self.created_issues.append(issue_url)
                return issue_url
            else:
                print(f"❌ Failed to create issue: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            print(f"❌ Timeout creating issue: {issue.title}")
            return None

    def report_violations(
        self,
        results: Dict[str, Any],
        skip_duplicates: bool = True,
    ) -> List[str]:
        """
        Create GitHub issues for all violations.

        Args:
            results: Results dictionary from VisualComplianceAgent
            skip_duplicates: Skip issues that already exist

        Returns:
            List of created issue URLs
        """
        if not self.check_gh_cli():
            print("❌ Error: gh CLI is not installed or not authenticated")
            print("   Install: https://cli.github.com/")
            print("   Authenticate: gh auth login")
            return []

        # Get existing issues to avoid duplicates
        existing_titles = set()
        if skip_duplicates:
            print("📋 Checking for existing issues...")
            existing_titles = self.get_existing_issues()
            print(f"   Found {len(existing_titles)} existing compliance issues")

        # Group violations by module and check type
        violations_by_module: Dict[str, Dict[str, List[Dict[str, Any]]]] = {}

        for check_type, check_result in results.get("checks", {}).items():
            for violation in check_result.get("violations", []):
                module_name = violation.get("module_name", "unknown")

                if module_name not in violations_by_module:
                    violations_by_module[module_name] = {}

                if check_type not in violations_by_module[module_name]:
                    violations_by_module[module_name][check_type] = []

                violations_by_module[module_name][check_type].append(violation)

        # Create issues
        created_urls = []

        for module_name, checks in violations_by_module.items():
            for check_type, violations in checks.items():
                issue = self.format_violation_issue(module_name, violations, check_type)

                # Skip if duplicate
                if skip_duplicates and issue.title in existing_titles:
                    print(f"⏭️  Skipping duplicate: {issue.title}")
                    continue

                # Create issue
                issue_url = self.create_issue(issue)
                if issue_url:
                    created_urls.append(issue_url)

        return created_urls

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of issue creation.

        Returns:
            Summary dictionary
        """
        return {
            "repo": self.repo,
            "dry_run": self.dry_run,
            "issues_created": len(self.created_issues),
            "issue_urls": self.created_issues,
        }


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="GitHub Reporter - Create issues from compliance violations"
    )
    parser.add_argument(
        "--results",
        type=Path,
        help="Path to JSON results file from visual_agent.py",
    )
    parser.add_argument(
        "--repo",
        default="jgtolentino/insightpulse-odoo",
        help="GitHub repository (owner/repo)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print issues without creating them",
    )
    parser.add_argument(
        "--allow-duplicates",
        action="store_true",
        help="Allow creating duplicate issues",
    )

    args = parser.parse_args()

    # Load results
    if args.results:
        try:
            results = json.loads(args.results.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"❌ Error loading results: {e}")
            return 1
    else:
        # Read from stdin
        try:
            results = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON from stdin: {e}")
            return 1

    # Create reporter and process violations
    reporter = GitHubReporter(
        repo=args.repo,
        dry_run=args.dry_run,
    )

    created_urls = reporter.report_violations(
        results,
        skip_duplicates=not args.allow_duplicates,
    )

    # Print summary
    summary = reporter.get_summary()
    print(f"\n📊 Summary:")
    print(f"   Repository: {summary['repo']}")
    print(f"   Issues created: {summary['issues_created']}")

    if args.dry_run:
        print("\n⚠️  DRY RUN - No issues were actually created")

    return 0


if __name__ == "__main__":
    sys.exit(main())

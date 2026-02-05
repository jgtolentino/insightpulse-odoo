#!/usr/bin/env python3
"""
Visual Compliance Full Scan Skill

Orchestrates all compliance validators and generates comprehensive reports.
Uses skill registry for modular, pluggable architecture.
"""

from pathlib import Path
from typing import Any, Dict
import sys

# Add agents directory to path for skill registry import
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from agents.skill_registry import get_skill


def run_skill(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute full compliance scan using all validators.

    Args:
        params: Skill parameters
            - repo_path (str): Path to repository root (default: ".")
            - fix (bool): Enable auto-fix (default: False)
            - create_issues (bool): Create GitHub issues for violations (default: False)

    Returns:
        Skill result dictionary:
            - ok (bool): Whether all checks passed
            - summary (dict): Overall compliance summary
            - checks (dict): Results from each validator

    Example:
        >>> result = run_skill({"repo_path": ".", "fix": False})
        >>> print(f"Overall compliance: {result['ok']}")
        >>> print(f"Total violations: {result['summary']['total_violations']}")
    """
    # Extract parameters with defaults
    repo_path = params.get("repo_path", ".")
    enable_fix = params.get("fix", False)
    create_issues = params.get("create_issues", False)

    # Define validators to run
    validator_skills = [
        "odoo.manifest.validate",
        "odoo.directory.validate",
        "odoo.naming.validate",
        "odoo.readme.validate",
    ]

    # Execute each validator
    results = {}
    all_violations = []

    for skill_id in validator_skills:
        try:
            # Get skill from registry
            run_validator, meta = get_skill(skill_id)

            # Execute validator
            skill_params = {
                "repo_path": repo_path,
                "fix": enable_fix,
            }
            result = run_validator(skill_params)

            # Store result
            check_name = skill_id.replace("odoo.", "").replace(".validate", "")
            results[check_name] = result

            # Collect violations
            if "violations" in result:
                for violation in result["violations"]:
                    violation["check_type"] = check_name
                    all_violations.append(violation)

        except Exception as e:
            # Log error and continue with other validators
            print(f"❌ Error running skill '{skill_id}': {e}", file=sys.stderr)
            results[skill_id] = {
                "ok": False,
                "error": str(e),
                "violations": [],
            }

    # Calculate summary statistics
    total_violations = len(all_violations)
    violations_by_severity = {
        "critical": sum(1 for v in all_violations if v.get("severity") == "CRITICAL"),
        "high": sum(1 for v in all_violations if v.get("severity") == "HIGH"),
        "medium": sum(1 for v in all_violations if v.get("severity") == "MEDIUM"),
        "low": sum(1 for v in all_violations if v.get("severity") == "LOW"),
    }

    is_compliant = total_violations == 0

    summary = {
        "is_compliant": is_compliant,
        "total_violations": total_violations,
        "violations_by_severity": violations_by_severity,
        "checks_run": len(results),
        "checks_passed": sum(1 for r in results.values() if r.get("ok", False)),
    }

    # Create GitHub issues if requested
    if create_issues and not is_compliant:
        try:
            from ..reporters.github_reporter import GitHubReporter

            reporter = GitHubReporter()
            full_result = {
                "summary": summary,
                "checks": results,
            }
            created_issues = reporter.report_violations(full_result)
            summary["github_issues_created"] = len(created_issues)
        except Exception as e:
            print(f"⚠️  Warning: Could not create GitHub issues: {e}", file=sys.stderr)
            summary["github_issues_created"] = 0

    return {
        "ok": is_compliant,
        "summary": summary,
        "checks": results,
    }


def main():
    """CLI entry point for standalone execution."""
    import argparse
    import json

    parser = argparse.ArgumentParser(
        description="Visual Compliance Agent - Full Scan"
    )
    parser.add_argument(
        "--repo-root",
        type=str,
        default=".",
        help="Path to repository root (default: current directory)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Enable auto-fix for violations",
    )
    parser.add_argument(
        "--create-issues",
        action="store_true",
        help="Create GitHub issues for violations",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )
    parser.add_argument(
        "--github-annotations",
        action="store_true",
        help="Output GitHub Actions annotations",
    )

    args = parser.parse_args()

    # Run full scan
    params = {
        "repo_path": args.repo_root,
        "fix": args.fix,
        "create_issues": args.create_issues,
    }

    result = run_skill(params)

    # Output results
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.github_annotations:
        # Export GitHub Actions annotations
        for check_name, check_result in result["checks"].items():
            for violation in check_result.get("violations", []):
                severity = violation.get("severity", "warning").lower()
                annotation_type = "error" if severity == "critical" else "warning"

                module_path = violation.get("module_path", "")
                message = violation.get("description", "Compliance violation")

                print(
                    f"::{annotation_type} file={module_path}::{check_name}: {message}"
                )
    else:
        # Human-readable output
        print("=== Visual Compliance Agent - Full Scan ===\n")

        summary = result["summary"]
        print(f"Overall Compliance: {'✅ PASS' if result['ok'] else '❌ FAIL'}")
        print(f"Total Violations: {summary['total_violations']}")
        print(f"Checks Run: {summary['checks_run']}")
        print(f"Checks Passed: {summary['checks_passed']}")

        if not result["ok"]:
            print("\nViolations by Severity:")
            for severity, count in summary["violations_by_severity"].items():
                if count > 0:
                    emoji = {
                        "critical": "🔴",
                        "high": "🟠",
                        "medium": "🟡",
                        "low": "🔵",
                    }.get(severity, "⚪")
                    print(f"  {emoji} {severity.upper()}: {count}")

            print("\nCheck Results:")
            for check_name, check_result in result["checks"].items():
                status = "✅" if check_result.get("ok", False) else "❌"
                violation_count = len(check_result.get("violations", []))
                print(f"  {status} {check_name}: {violation_count} violation(s)")

    # Exit with appropriate code
    if result["ok"]:
        sys.exit(0)
    elif summary["violations_by_severity"]["critical"] > 0:
        sys.exit(2)  # Critical violations
    else:
        sys.exit(1)  # Non-critical violations


if __name__ == "__main__":
    main()

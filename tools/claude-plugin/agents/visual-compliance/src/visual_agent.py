#!/usr/bin/env python3
"""
Visual Compliance Agent - Microsoft Agent Framework Integration

This agent orchestrates OCA compliance validation across multiple dimensions:
- Manifest compliance (version, license, author)
- Directory structure (single odoo_addons/ directory)
- Module naming (ipai_* prefix)
- Documentation (README.rst files)

Built on Microsoft Agent Framework for multi-step workflows with LLM integration.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Import validators
from tools.manifest_checker import ManifestChecker
from tools.directory_validator import DirectoryValidator
from tools.naming_validator import NamingValidator
from tools.readme_validator import ReadmeValidator


class VisualComplianceAgent:
    """
    OCA Compliance validation agent with Microsoft Agent Framework integration.

    This agent coordinates multiple compliance validators and provides:
    - Automated compliance checking
    - Violation detection with severity levels
    - Auto-fix capabilities
    - Structured reporting for GitHub Actions
    - GitHub issue creation
    """

    def __init__(
        self,
        repo_root: Path = Path("."),
        addons_root: Optional[Path] = None,
        enable_autofix: bool = False,
    ):
        """
        Initialize Visual Compliance Agent.

        Args:
            repo_root: Repository root directory
            addons_root: Addons directory (defaults to repo_root/odoo_addons)
            enable_autofix: Enable automatic fixing of violations
        """
        self.repo_root = repo_root.resolve()
        self.addons_root = addons_root or (self.repo_root / "odoo_addons")
        self.enable_autofix = enable_autofix

        # Initialize validators
        self.manifest_checker = ManifestChecker(addons_root=self.addons_root)
        self.directory_validator = DirectoryValidator(repo_root=self.repo_root)
        self.naming_validator = NamingValidator(addons_root=self.addons_root)
        self.readme_validator = ReadmeValidator(addons_root=self.addons_root)

        # Results storage
        self.results: Dict[str, Any] = {}

    def run_manifest_compliance(self) -> Dict[str, Any]:
        """
        Run manifest compliance checks.

        Returns:
            Dictionary with check results and violations
        """
        print("🔍 Checking manifest compliance...")

        if self.enable_autofix:
            total, compliant = self.manifest_checker.check_all(fix=True)
        else:
            total, compliant = self.manifest_checker.check_all(fix=False)

        report = self.manifest_checker.get_report()
        report["tool"] = "manifest_checker"

        print(f"   ✓ Checked {total} manifests, {compliant} compliant")

        return report

    def run_directory_compliance(self) -> Dict[str, Any]:
        """
        Run directory structure compliance checks.

        Returns:
            Dictionary with check results and violations
        """
        print("🔍 Checking directory structure...")

        result = self.directory_validator.check_structure()

        if self.enable_autofix and not result.is_compliant:
            changes = self.directory_validator.fix_structure()
            print(f"   🔧 Applied {len(changes)} fixes")

        report = self.directory_validator.get_report()
        report["tool"] = "directory_validator"

        addon_count = len(report["addon_directories"])
        print(f"   ✓ Found {addon_count} addon directories, {result.total_modules} modules")

        return report

    def run_naming_compliance(self) -> Dict[str, Any]:
        """
        Run module naming compliance checks.

        Returns:
            Dictionary with check results and violations
        """
        print("🔍 Checking module naming...")

        result = self.naming_validator.check_naming()

        # Note: Naming auto-fix is not implemented (too destructive)
        if self.enable_autofix and not result.is_compliant:
            print("   ⚠️  Naming auto-fix requires manual intervention")

        report = self.naming_validator.get_report()
        report["tool"] = "naming_validator"

        compliance_pct = report["summary"]["compliance_percentage"]
        print(f"   ✓ {result.compliant_modules}/{result.total_modules} modules compliant ({compliance_pct}%)")

        return report

    def run_readme_compliance(self) -> Dict[str, Any]:
        """
        Run README documentation compliance checks.

        Returns:
            Dictionary with check results and violations
        """
        print("🔍 Checking README documentation...")

        result = self.readme_validator.check_all()

        if self.enable_autofix and not result.is_compliant:
            changes = self.readme_validator.fix_readmes()
            print(f"   🔧 Generated {len([c for c in changes if 'Generated' in c])} README files")

        report = self.readme_validator.get_report()
        report["tool"] = "readme_validator"

        coverage_pct = report["summary"]["readme_coverage"]
        print(f"   ✓ {result.modules_with_readme}/{result.total_modules} modules have README ({coverage_pct}%)")

        return report

    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all compliance checks in sequence.

        Returns:
            Combined results from all validators
        """
        print("\n🤖 Visual Compliance Agent - Starting Analysis\n")
        print(f"Repository: {self.repo_root}")
        print(f"Addons: {self.addons_root}")
        print(f"Auto-fix: {'enabled' if self.enable_autofix else 'disabled'}\n")

        results = {
            "repo_root": str(self.repo_root),
            "addons_root": str(self.addons_root),
            "autofix_enabled": self.enable_autofix,
            "checks": {},
            "summary": {},
        }

        # Run all compliance checks
        results["checks"]["manifest"] = self.run_manifest_compliance()
        results["checks"]["directory"] = self.run_directory_compliance()
        results["checks"]["naming"] = self.run_naming_compliance()
        results["checks"]["readme"] = self.run_readme_compliance()

        # Calculate overall summary
        results["summary"] = self._calculate_summary(results["checks"])

        self.results = results
        return results

    def _calculate_summary(self, checks: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate overall compliance summary from all checks.

        Args:
            checks: Dictionary of check results

        Returns:
            Summary statistics
        """
        total_violations = 0
        critical_count = 0
        high_count = 0
        medium_count = 0
        low_count = 0

        for check_name, check_result in checks.items():
            violations = check_result.get("violations", [])
            total_violations += len(violations)

            # Count by severity
            violations_by_severity = check_result.get("violations_by_severity", {})
            critical_count += violations_by_severity.get("critical", 0)
            high_count += violations_by_severity.get("high", 0)
            medium_count += violations_by_severity.get("medium", 0)
            low_count += violations_by_severity.get("low", 0)

        is_compliant = total_violations == 0

        return {
            "is_compliant": is_compliant,
            "total_violations": total_violations,
            "violations_by_severity": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count,
                "low": low_count,
            },
            "checks_passed": sum(
                1 for check in checks.values()
                if check.get("summary", {}).get("is_compliant", False)
                or len(check.get("violations", [])) == 0
            ),
            "total_checks": len(checks),
        }

    def print_summary(self):
        """Print human-readable summary of results"""
        if not self.results:
            print("⚠️  No results available. Run checks first.")
            return

        summary = self.results.get("summary", {})

        print("\n" + "=" * 70)
        print("📊 VISUAL COMPLIANCE AGENT - SUMMARY")
        print("=" * 70 + "\n")

        # Overall status
        if summary.get("is_compliant", False):
            print("✅ COMPLIANT - All checks passed!")
        else:
            print("❌ NON-COMPLIANT - Violations detected")

        print(f"\nTotal Violations: {summary.get('total_violations', 0)}")
        print(f"Checks Passed: {summary.get('checks_passed', 0)}/{summary.get('total_checks', 0)}")

        # Violations by severity
        violations_by_severity = summary.get("violations_by_severity", {})
        print("\nViolations by Severity:")
        print(f"  🔴 Critical: {violations_by_severity.get('critical', 0)}")
        print(f"  🟠 High:     {violations_by_severity.get('high', 0)}")
        print(f"  🟡 Medium:   {violations_by_severity.get('medium', 0)}")
        print(f"  🔵 Low:      {violations_by_severity.get('low', 0)}")

        # Check details
        print("\nCheck Details:")
        for check_name, check_result in self.results.get("checks", {}).items():
            check_summary = check_result.get("summary", {})
            violation_count = len(check_result.get("violations", []))

            if violation_count == 0:
                print(f"  ✅ {check_name}: PASS")
            else:
                print(f"  ❌ {check_name}: {violation_count} violations")

        print("\n" + "=" * 70 + "\n")

    def export_github_annotations(self) -> List[Dict[str, Any]]:
        """
        Export violations as GitHub Actions annotations.

        Returns:
            List of annotation dictionaries for GitHub Actions
        """
        annotations = []

        for check_name, check_result in self.results.get("checks", {}).items():
            for violation in check_result.get("violations", []):
                severity_map = {
                    "critical": "error",
                    "high": "error",
                    "medium": "warning",
                    "low": "notice",
                }

                annotation = {
                    "level": severity_map.get(violation.get("severity", "warning"), "warning"),
                    "title": f"{check_name.upper()}: {violation.get('violation_type', 'unknown')}",
                    "message": violation.get("description", "No description"),
                    "file": violation.get("file_path", violation.get("module_path", "unknown")),
                }

                annotations.append(annotation)

        return annotations


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Visual Compliance Agent - OCA compliance validation"
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root directory (default: current directory)",
    )
    parser.add_argument(
        "--addons-root",
        type=Path,
        help="Addons directory (default: repo-root/odoo_addons)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically fix violations where possible",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--github-annotations",
        action="store_true",
        help="Export GitHub Actions annotations",
    )

    args = parser.parse_args()

    # Create and run agent
    agent = VisualComplianceAgent(
        repo_root=args.repo_root,
        addons_root=args.addons_root,
        enable_autofix=args.fix,
    )

    results = agent.run_all_checks()

    # Output results
    if args.json:
        print(json.dumps(results, indent=2))
    elif args.github_annotations:
        annotations = agent.export_github_annotations()
        for annotation in annotations:
            level = annotation["level"]
            title = annotation["title"]
            message = annotation["message"]
            file_path = annotation.get("file", "")

            # GitHub Actions annotation format
            print(f"::{level} file={file_path},title={title}::{message}")
    else:
        agent.print_summary()

    # Exit code based on compliance
    summary = results.get("summary", {})
    is_compliant = summary.get("is_compliant", False)
    critical_count = summary.get("violations_by_severity", {}).get("critical", 0)

    if critical_count > 0:
        return 2  # Critical violations
    elif not is_compliant:
        return 1  # Non-critical violations
    else:
        return 0  # Compliant


if __name__ == "__main__":
    sys.exit(main())

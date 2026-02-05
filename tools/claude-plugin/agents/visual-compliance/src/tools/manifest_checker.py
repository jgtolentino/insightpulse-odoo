#!/usr/bin/env python3
"""
Manifest Compliance Checker for Odoo 18.0 + OCA Standards

This tool validates and fixes __manifest__.py files to ensure compliance with:
- Odoo 18.0 version format (18.0.x.y.z)
- LGPL-3 license requirement
- InsightPulseAI author attribution
- Correct website URL

Usage:
    python manifest_checker.py                    # Check only
    python manifest_checker.py --fix              # Check and auto-fix
    python manifest_checker.py --json             # JSON output for agents
"""

import ast
import json
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional


# Configuration (from branding_theme.json)
TARGET_VERSION_PREFIX = "18.0."
TARGET_LICENSE = "LGPL-3"
TARGET_AUTHOR = "InsightPulseAI"
TARGET_WEBSITE = "https://insightpulseai.net"
ADDONS_ROOT = Path("odoo_addons")


class ViolationType(str, Enum):
    """Types of compliance violations"""
    VERSION_MISMATCH = "version_mismatch"
    LICENSE_MISMATCH = "license_mismatch"
    AUTHOR_MISSING = "author_missing"
    WEBSITE_INCORRECT = "website_incorrect"
    MISSING_KEY = "missing_key"
    PARSE_ERROR = "parse_error"


class Severity(str, Enum):
    """Violation severity levels"""
    CRITICAL = "critical"  # Blocks OCA submission
    HIGH = "high"          # Major compliance issue
    MEDIUM = "medium"      # Should be fixed
    LOW = "low"            # Nice to have


@dataclass
class ManifestViolation:
    """Represents a single manifest compliance violation"""
    module_name: str
    file_path: str
    violation_type: ViolationType
    severity: Severity
    current_value: str
    expected_value: str
    description: str
    auto_fixable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class ManifestCheckResult:
    """Result of manifest validation"""
    module_name: str
    file_path: str
    is_compliant: bool
    violations: List[ManifestViolation]
    fixes_applied: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "module_name": self.module_name,
            "file_path": self.file_path,
            "is_compliant": self.is_compliant,
            "violations": [v.to_dict() for v in self.violations],
            "fixes_applied": self.fixes_applied or [],
        }


class ManifestChecker:
    """Validates and fixes Odoo manifest files"""

    def __init__(self, addons_root: Path = ADDONS_ROOT):
        self.addons_root = addons_root
        self.results: List[ManifestCheckResult] = []

    def load_manifest(self, path: Path) -> Dict[str, Any]:
        """
        Safely load __manifest__.py as a dict using ast.literal_eval.

        Raises:
            ValueError: If manifest cannot be parsed
        """
        try:
            text = path.read_text(encoding="utf-8")
            tree = ast.parse(text, filename=str(path))

            # Expect a single dict literal in the file
            for node in tree.body:
                if isinstance(node, ast.Assign):
                    if isinstance(node.value, ast.Dict):
                        return ast.literal_eval(ast.Expression(node.value))
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Dict):
                    return ast.literal_eval(ast.Expression(node.value))

            raise ValueError(f"Could not parse manifest at {path}")
        except Exception as e:
            raise ValueError(f"Failed to load manifest {path}: {e}")

    def dump_manifest(self, path: Path, manifest: Dict[str, Any]) -> None:
        """
        Overwrite manifest file with a pretty-printed dict literal.

        Format matches OCA conventions with proper indentation.
        """
        lines = ["# -*- coding: utf-8 -*-", "{"]

        # Order keys for consistency (OCA convention)
        key_order = [
            "name", "version", "category", "license", "author", "website",
            "depends", "data", "demo", "installable", "application", "auto_install"
        ]

        # Add ordered keys first
        for key in key_order:
            if key in manifest:
                value = manifest[key]
                lines.append(f'    "{key}": {value!r},')

        # Add remaining keys
        for key, value in manifest.items():
            if key not in key_order:
                lines.append(f'    "{key}": {value!r},')

        lines.append("}")
        body = "\n".join(lines) + "\n"
        path.write_text(body, encoding="utf-8")

    def check_manifest(self, path: Path) -> ManifestCheckResult:
        """
        Validate a single manifest file.

        Returns:
            ManifestCheckResult with all violations found
        """
        module_name = path.parent.name
        violations: List[ManifestViolation] = []

        try:
            manifest = self.load_manifest(path)
        except ValueError as e:
            return ManifestCheckResult(
                module_name=module_name,
                file_path=str(path),
                is_compliant=False,
                violations=[
                    ManifestViolation(
                        module_name=module_name,
                        file_path=str(path),
                        violation_type=ViolationType.PARSE_ERROR,
                        severity=Severity.CRITICAL,
                        current_value=str(e),
                        expected_value="Valid Python dict",
                        description=f"Failed to parse manifest: {e}",
                        auto_fixable=False,
                    )
                ],
            )

        # Check version
        version = manifest.get("version", "")
        if not version.startswith(TARGET_VERSION_PREFIX):
            violations.append(
                ManifestViolation(
                    module_name=module_name,
                    file_path=str(path),
                    violation_type=ViolationType.VERSION_MISMATCH,
                    severity=Severity.CRITICAL,
                    current_value=version,
                    expected_value=f"{TARGET_VERSION_PREFIX}x.y.z",
                    description=f'Version "{version}" must start with "{TARGET_VERSION_PREFIX}" for Odoo 18.0',
                    auto_fixable=True,
                )
            )

        # Check license
        license_ = manifest.get("license", "")
        if license_ != TARGET_LICENSE:
            violations.append(
                ManifestViolation(
                    module_name=module_name,
                    file_path=str(path),
                    violation_type=ViolationType.LICENSE_MISMATCH,
                    severity=Severity.CRITICAL,
                    current_value=license_,
                    expected_value=TARGET_LICENSE,
                    description=f'License "{license_}" must be "{TARGET_LICENSE}" for OCA compliance',
                    auto_fixable=True,
                )
            )

        # Check author
        author = manifest.get("author", "")
        if TARGET_AUTHOR not in str(author):
            violations.append(
                ManifestViolation(
                    module_name=module_name,
                    file_path=str(path),
                    violation_type=ViolationType.AUTHOR_MISSING,
                    severity=Severity.HIGH,
                    current_value=author,
                    expected_value=TARGET_AUTHOR,
                    description=f'Author "{author}" should include "{TARGET_AUTHOR}"',
                    auto_fixable=True,
                )
            )

        # Check website
        website = manifest.get("website", "")
        if TARGET_WEBSITE and website != TARGET_WEBSITE:
            violations.append(
                ManifestViolation(
                    module_name=module_name,
                    file_path=str(path),
                    violation_type=ViolationType.WEBSITE_INCORRECT,
                    severity=Severity.MEDIUM,
                    current_value=website,
                    expected_value=TARGET_WEBSITE,
                    description=f'Website "{website}" should be "{TARGET_WEBSITE}"',
                    auto_fixable=True,
                )
            )

        # Check required keys
        required_keys = ["name", "version", "depends", "license", "author"]
        for key in required_keys:
            if key not in manifest:
                violations.append(
                    ManifestViolation(
                        module_name=module_name,
                        file_path=str(path),
                        violation_type=ViolationType.MISSING_KEY,
                        severity=Severity.CRITICAL,
                        current_value="",
                        expected_value=f"'{key}' key present",
                        description=f"Required key '{key}' is missing",
                        auto_fixable=False,  # Can't auto-generate meaningful values
                    )
                )

        return ManifestCheckResult(
            module_name=module_name,
            file_path=str(path),
            is_compliant=len(violations) == 0,
            violations=violations,
        )

    def fix_manifest(self, path: Path) -> List[str]:
        """
        Automatically fix manifest violations.

        Returns:
            List of changes made
        """
        manifest = self.load_manifest(path)
        changes: List[str] = []

        # Fix version
        if not str(manifest.get("version", "")).startswith(TARGET_VERSION_PREFIX):
            old = manifest.get("version", "")
            # Preserve minor version if upgrading from 19.0.x
            if old.startswith("19.0."):
                suffix = old[5:]  # Keep x.y.z part
                manifest["version"] = TARGET_VERSION_PREFIX + suffix
            else:
                manifest["version"] = TARGET_VERSION_PREFIX + "1.0.0"
            changes.append(f'version: "{old}" → "{manifest["version"]}"')

        # Fix license
        if manifest.get("license") != TARGET_LICENSE:
            old = manifest.get("license", "")
            manifest["license"] = TARGET_LICENSE
            changes.append(f'license: "{old}" → "{TARGET_LICENSE}"')

        # Fix author
        if TARGET_AUTHOR not in str(manifest.get("author", "")):
            old = manifest.get("author", "")
            manifest["author"] = TARGET_AUTHOR
            changes.append(f'author: "{old}" → "{TARGET_AUTHOR}"')

        # Fix website
        if TARGET_WEBSITE and manifest.get("website") != TARGET_WEBSITE:
            old = manifest.get("website", "")
            manifest["website"] = TARGET_WEBSITE
            changes.append(f'website: "{old}" → "{TARGET_WEBSITE}"')

        if changes:
            self.dump_manifest(path, manifest)

        return changes

    def check_all(self, fix: bool = False) -> Tuple[int, int]:
        """
        Check all manifests in addons root.

        Args:
            fix: If True, automatically fix violations

        Returns:
            Tuple of (total_manifests, compliant_manifests)
        """
        manifests = list(self.addons_root.glob("*/__manifest__.py"))
        if not manifests:
            print(f"⚠️  No manifests found under {self.addons_root}/", file=sys.stderr)
            return 0, 0

        total = len(manifests)
        compliant = 0

        for manifest_path in sorted(manifests):
            result = self.check_manifest(manifest_path)
            self.results.append(result)

            if result.is_compliant:
                compliant += 1
                print(f"✅ {result.module_name}: OK")
            else:
                print(f"❌ {result.module_name}:")
                for violation in result.violations:
                    severity_emoji = {
                        Severity.CRITICAL: "🔴",
                        Severity.HIGH: "🟠",
                        Severity.MEDIUM: "🟡",
                        Severity.LOW: "🔵",
                    }[violation.severity]
                    print(f"   {severity_emoji} [{violation.severity.value}] {violation.description}")

                if fix and any(v.auto_fixable for v in result.violations):
                    changes = self.fix_manifest(manifest_path)
                    if changes:
                        result.fixes_applied = changes
                        print("   🔧 Applied fixes:")
                        for change in changes:
                            print(f"      • {change}")

        return total, compliant

    def get_report(self) -> Dict[str, Any]:
        """
        Get structured compliance report.

        Returns:
            Dictionary with summary and detailed results
        """
        total = len(self.results)
        compliant = sum(1 for r in self.results if r.is_compliant)

        violations_by_type = {}
        violations_by_severity = {}

        for result in self.results:
            for violation in result.violations:
                vtype = violation.violation_type.value
                violations_by_type[vtype] = violations_by_type.get(vtype, 0) + 1

                sev = violation.severity.value
                violations_by_severity[sev] = violations_by_severity.get(sev, 0) + 1

        return {
            "summary": {
                "total_modules": total,
                "compliant_modules": compliant,
                "non_compliant_modules": total - compliant,
                "compliance_percentage": round(compliant / total * 100, 1) if total > 0 else 0,
            },
            "violations_by_type": violations_by_type,
            "violations_by_severity": violations_by_severity,
            "results": [r.to_dict() for r in self.results],
        }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check (and optionally fix) Odoo manifests for 18.0 + LGPL-3 compliance."
    )
    parser.add_argument("--fix", action="store_true", help="Auto-fix manifests in-place")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--addons-root", type=Path, default=ADDONS_ROOT, help="Path to addons directory")
    args = parser.parse_args()

    checker = ManifestChecker(addons_root=args.addons_root)
    total, compliant = checker.check_all(fix=args.fix)

    if args.json:
        report = checker.get_report()
        print(json.dumps(report, indent=2))
    else:
        print(f"\n📊 Summary: {compliant}/{total} modules compliant ({compliant/total*100:.1f}%)")

    # Exit code: 0 if all compliant, 1 otherwise
    return 0 if total == compliant else 1


if __name__ == "__main__":
    sys.exit(main())

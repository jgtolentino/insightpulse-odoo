#!/usr/bin/env python3
"""
Module Naming Validator for InsightPulseAI Standards

This tool validates and fixes Odoo module naming to ensure compliance with:
- ipai_* prefix for all custom modules
- Lowercase with underscores only (no hyphens, spaces, uppercase)
- Descriptive and consistent naming conventions
- No OCA module conflicts

Addresses issue #394: Standardize all modules to ipai_* prefix
"""

import ast
import json
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional


# Configuration
MODULE_PREFIX = "ipai_"
ADDONS_ROOT = Path("odoo_addons")
MANIFEST_FILES = ["__manifest__.py", "__openerp__.py"]

# OCA modules should NOT be prefixed (exclude from validation)
OCA_PATTERNS = [
    r"^account_.*",
    r"^sale_.*",
    r"^purchase_.*",
    r"^stock_.*",
    r"^hr_.*",
    r"^web_.*",
    r"^base_.*",
]


class ViolationType(str, Enum):
    """Types of naming violations"""
    MISSING_PREFIX = "missing_prefix"
    INVALID_CHARACTERS = "invalid_characters"
    UPPERCASE_NAME = "uppercase_name"
    HYPHEN_SEPARATOR = "hyphen_separator"
    DUPLICATE_NAME = "duplicate_name"
    RESERVED_NAME = "reserved_name"


class Severity(str, Enum):
    """Violation severity levels"""
    CRITICAL = "critical"  # Blocks installation
    HIGH = "high"          # Major compliance issue
    MEDIUM = "medium"      # Should be fixed
    LOW = "low"            # Nice to have


@dataclass
class NamingViolation:
    """Represents a single module naming violation"""
    module_name: str
    module_path: str
    violation_type: ViolationType
    severity: Severity
    description: str
    suggested_name: Optional[str] = None
    auto_fixable: bool = True
    migration_complexity: str = "low"  # low, medium, high
    dependencies_affected: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        if self.dependencies_affected is None:
            result['dependencies_affected'] = []
        return result


@dataclass
class NamingCheckResult:
    """Result of naming validation"""
    is_compliant: bool
    violations: List[NamingViolation]
    total_modules: int
    compliant_modules: int
    modules_to_rename: Dict[str, str]  # old_name -> new_name
    fixes_applied: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "is_compliant": self.is_compliant,
            "violations": [v.to_dict() for v in self.violations],
            "total_modules": self.total_modules,
            "compliant_modules": self.compliant_modules,
            "modules_to_rename": self.modules_to_rename,
            "fixes_applied": self.fixes_applied or [],
        }


class NamingValidator:
    """Validates and fixes Odoo module naming"""

    def __init__(self, addons_root: Path = ADDONS_ROOT):
        self.addons_root = addons_root
        self.results: Optional[NamingCheckResult] = None

    def is_odoo_module(self, path: Path) -> bool:
        """Check if directory is an Odoo module"""
        if not path.is_dir():
            return False
        return any((path / manifest).exists() for manifest in MANIFEST_FILES)

    def is_oca_module(self, module_name: str) -> bool:
        """Check if module appears to be an OCA community module"""
        for pattern in OCA_PATTERNS:
            if re.match(pattern, module_name):
                return True
        return False

    def validate_module_name(self, module_name: str) -> Tuple[bool, List[str]]:
        """
        Validate a single module name against naming standards.

        Args:
            module_name: Name of the module to validate

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Skip OCA modules
        if self.is_oca_module(module_name):
            return True, []

        # Check 1: Must start with ipai_ prefix
        if not module_name.startswith(MODULE_PREFIX):
            issues.append(f"Missing required '{MODULE_PREFIX}' prefix")

        # Check 2: Must be lowercase
        if module_name != module_name.lower():
            issues.append("Contains uppercase letters (use lowercase only)")

        # Check 3: Must use underscores, not hyphens
        if "-" in module_name:
            issues.append("Contains hyphens (use underscores instead)")

        # Check 4: Must contain only valid characters (lowercase, digits, underscores)
        if not re.match(r"^[a-z0-9_]+$", module_name):
            issues.append("Contains invalid characters (use only lowercase, digits, underscores)")

        return len(issues) == 0, issues

    def suggest_module_name(self, module_name: str) -> str:
        """
        Suggest a compliant module name based on the current name.

        Args:
            module_name: Current module name

        Returns:
            Suggested compliant module name
        """
        # Convert to lowercase
        suggested = module_name.lower()

        # Replace hyphens with underscores
        suggested = suggested.replace("-", "_")

        # Remove invalid characters
        suggested = re.sub(r"[^a-z0-9_]", "", suggested)

        # Add prefix if missing
        if not suggested.startswith(MODULE_PREFIX):
            suggested = MODULE_PREFIX + suggested

        # Clean up multiple underscores
        suggested = re.sub(r"_{2,}", "_", suggested)

        # Remove leading/trailing underscores (except prefix)
        suggested = suggested.strip("_")
        if not suggested.startswith(MODULE_PREFIX):
            suggested = MODULE_PREFIX + suggested.lstrip("_")

        return suggested

    def find_module_dependencies(self, module_path: Path) -> List[str]:
        """
        Find modules that depend on this module.

        Args:
            module_path: Path to the module directory

        Returns:
            List of module names that declare this module as a dependency
        """
        dependencies = []
        module_name = module_path.name

        # Search all modules for depends declarations
        if not self.addons_root.exists():
            return dependencies

        for candidate in self.addons_root.iterdir():
            if not self.is_odoo_module(candidate):
                continue

            # Find manifest file
            manifest_path = None
            for manifest_file in MANIFEST_FILES:
                if (candidate / manifest_file).exists():
                    manifest_path = candidate / manifest_file
                    break

            if not manifest_path:
                continue

            try:
                # Parse manifest
                text = manifest_path.read_text(encoding="utf-8")
                tree = ast.parse(text, filename=str(manifest_path))

                for node in tree.body:
                    manifest_dict = None
                    if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
                        manifest_dict = ast.literal_eval(ast.Expression(node.value))
                    elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Dict):
                        manifest_dict = ast.literal_eval(ast.Expression(node.value))

                    if manifest_dict and "depends" in manifest_dict:
                        depends_list = manifest_dict["depends"]
                        if module_name in depends_list:
                            dependencies.append(candidate.name)
                        break

            except (SyntaxError, ValueError):
                # Skip unparseable manifests
                continue

        return dependencies

    def check_naming(self) -> NamingCheckResult:
        """
        Validate naming for all modules in addons root.

        Returns:
            NamingCheckResult with all violations found
        """
        violations: List[NamingViolation] = []
        modules_to_rename: Dict[str, str] = {}
        all_module_names: Set[str] = set()

        if not self.addons_root.exists():
            return NamingCheckResult(
                is_compliant=True,
                violations=[],
                total_modules=0,
                compliant_modules=0,
                modules_to_rename={},
            )

        # Collect all module names first
        for module_path in self.addons_root.iterdir():
            if self.is_odoo_module(module_path):
                all_module_names.add(module_path.name)

        total_modules = len(all_module_names)
        compliant_count = 0

        # Check each module
        for module_path in self.addons_root.iterdir():
            if not self.is_odoo_module(module_path):
                continue

            module_name = module_path.name

            # Skip OCA modules
            if self.is_oca_module(module_name):
                compliant_count += 1
                continue

            is_valid, issues = self.validate_module_name(module_name)

            if is_valid:
                compliant_count += 1
                continue

            # Generate suggested name
            suggested_name = self.suggest_module_name(module_name)

            # Check for conflicts
            if suggested_name in all_module_names and suggested_name != module_name:
                violations.append(
                    NamingViolation(
                        module_name=module_name,
                        module_path=str(module_path),
                        violation_type=ViolationType.DUPLICATE_NAME,
                        severity=Severity.CRITICAL,
                        description=f"Suggested name '{suggested_name}' already exists",
                        suggested_name=None,
                        auto_fixable=False,
                        migration_complexity="high",
                    )
                )
                continue

            # Find dependencies
            dependencies = self.find_module_dependencies(module_path)

            # Determine violation type and severity
            if not module_name.startswith(MODULE_PREFIX):
                violation_type = ViolationType.MISSING_PREFIX
                severity = Severity.HIGH
                complexity = "medium" if dependencies else "low"
            elif "-" in module_name:
                violation_type = ViolationType.HYPHEN_SEPARATOR
                severity = Severity.MEDIUM
                complexity = "low"
            elif module_name != module_name.lower():
                violation_type = ViolationType.UPPERCASE_NAME
                severity = Severity.MEDIUM
                complexity = "low"
            else:
                violation_type = ViolationType.INVALID_CHARACTERS
                severity = Severity.MEDIUM
                complexity = "low"

            violations.append(
                NamingViolation(
                    module_name=module_name,
                    module_path=str(module_path),
                    violation_type=violation_type,
                    severity=severity,
                    description=f"Module '{module_name}' violates naming standards: {', '.join(issues)}",
                    suggested_name=suggested_name,
                    auto_fixable=True,
                    migration_complexity=complexity,
                    dependencies_affected=dependencies,
                )
            )

            modules_to_rename[module_name] = suggested_name

        self.results = NamingCheckResult(
            is_compliant=len(violations) == 0,
            violations=violations,
            total_modules=total_modules,
            compliant_modules=compliant_count,
            modules_to_rename=modules_to_rename,
        )

        return self.results

    def fix_naming(self) -> List[str]:
        """
        Automatically fix naming violations.

        NOTE: This is a DESTRUCTIVE operation that:
        - Renames module directories
        - Updates manifest files
        - Updates dependencies in other modules
        - Should be run in a clean git state with backups

        Returns:
            List of changes made
        """
        if not self.results:
            self.check_naming()

        changes: List[str] = []

        # TODO: Implement auto-fix functionality
        # This is complex because it requires:
        # 1. Renaming directories
        # 2. Updating module's own manifest (name key if present)
        # 3. Updating all dependent modules' manifests
        # 4. Updating any hardcoded references in Python/XML files
        # 5. Updating external references (CI configs, etc.)

        changes.append("⚠️  Auto-fix not yet implemented for naming violations")
        changes.append("   Manual steps required:")

        for old_name, new_name in self.results.modules_to_rename.items():
            changes.append(f"   1. Rename directory: {old_name}/ → {new_name}/")
            changes.append(f"   2. Update dependencies in modules that depend on {old_name}")
            changes.append(f"   3. Search for hardcoded references to '{old_name}'")
            changes.append("")

        return changes

    def get_report(self) -> Dict[str, Any]:
        """
        Get structured naming validation report.

        Returns:
            Dictionary with summary and detailed results
        """
        if not self.results:
            self.check_naming()

        violations_by_type = {}
        violations_by_severity = {}

        for violation in self.results.violations:
            vtype = violation.violation_type.value
            violations_by_type[vtype] = violations_by_type.get(vtype, 0) + 1

            sev = violation.severity.value
            violations_by_severity[sev] = violations_by_severity.get(sev, 0) + 1

        return {
            "summary": {
                "total_modules": self.results.total_modules,
                "compliant_modules": self.results.compliant_modules,
                "non_compliant_modules": self.results.total_modules - self.results.compliant_modules,
                "compliance_percentage": round(
                    self.results.compliant_modules / self.results.total_modules * 100, 1
                ) if self.results.total_modules > 0 else 0,
            },
            "violations_by_type": violations_by_type,
            "violations_by_severity": violations_by_severity,
            "modules_to_rename": self.results.modules_to_rename,
            "violations": [v.to_dict() for v in self.results.violations],
        }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check (and optionally fix) module naming for InsightPulseAI standards."
    )
    parser.add_argument("--fix", action="store_true", help="Auto-fix naming violations (DESTRUCTIVE)")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--addons-root", type=Path, default=ADDONS_ROOT, help="Path to addons directory")
    args = parser.parse_args()

    validator = NamingValidator(addons_root=args.addons_root)
    result = validator.check_naming()

    if args.json:
        report = validator.get_report()
        print(json.dumps(report, indent=2))
    else:
        print(f"📝 Module Naming Validation\n")
        print(f"Addons directory: {validator.addons_root}")
        print(f"Required prefix: {MODULE_PREFIX}\n")

        if result.is_compliant:
            print(f"✅ All {result.total_modules} modules comply with naming standards!")
        else:
            print(f"❌ Found {len(result.violations)} naming violations:\n")
            for violation in result.violations:
                severity_emoji = {
                    Severity.CRITICAL: "🔴",
                    Severity.HIGH: "🟠",
                    Severity.MEDIUM: "🟡",
                    Severity.LOW: "🔵",
                }[violation.severity]
                print(f"{severity_emoji} [{violation.severity.value}] {violation.module_name}")
                print(f"   {violation.description}")

                if violation.suggested_name:
                    print(f"   Suggested: {violation.suggested_name}")

                if violation.dependencies_affected:
                    print(f"   Dependencies: {', '.join(violation.dependencies_affected)}")

                print(f"   Complexity: {violation.migration_complexity}")
                print()

            # Show rename mapping
            if result.modules_to_rename:
                print(f"\n📋 Modules to rename ({len(result.modules_to_rename)}):")
                for old_name, new_name in result.modules_to_rename.items():
                    print(f"   {old_name} → {new_name}")
                print()

            # Apply fixes if requested
            if args.fix:
                print("🔧 Applying fixes...\n")
                changes = validator.fix_naming()
                for change in changes:
                    print(f"   {change}")
                print()

        # Summary
        compliance_pct = (result.compliant_modules / result.total_modules * 100) if result.total_modules > 0 else 0
        print(f"\n📊 Summary: {result.compliant_modules}/{result.total_modules} modules compliant ({compliance_pct:.1f}%)")

    # Exit code: 0 if all compliant, 1 otherwise
    return 0 if result.is_compliant else 1


if __name__ == "__main__":
    sys.exit(main())

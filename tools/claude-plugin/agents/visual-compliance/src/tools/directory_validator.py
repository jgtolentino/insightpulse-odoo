#!/usr/bin/env python3
"""
Directory Structure Validator for OCA Standards

This tool validates and fixes addon directory structure to ensure compliance with:
- Single canonical addons directory (odoo_addons/)
- No scattered addon locations
- Proper module organization
- Clean repository structure

Addresses issue #393: Consolidate three addon directories into single odoo_addons/
"""

import json
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple, Optional


# Configuration
CANONICAL_ADDONS_DIR = "odoo_addons"
KNOWN_ADDON_DIRS = ["odoo_addons", "addons", "custom_addons", "modules"]
MANIFEST_FILES = ["__manifest__.py", "__openerp__.py"]


class ViolationType(str, Enum):
    """Types of directory structure violations"""
    MULTIPLE_ADDON_DIRS = "multiple_addon_dirs"
    NON_CANONICAL_LOCATION = "non_canonical_location"
    MISSING_CANONICAL_DIR = "missing_canonical_dir"
    DUPLICATE_MODULE = "duplicate_module"
    EMPTY_ADDON_DIR = "empty_addon_dir"


class Severity(str, Enum):
    """Violation severity levels"""
    CRITICAL = "critical"  # Blocks OCA submission
    HIGH = "high"          # Major compliance issue
    MEDIUM = "medium"      # Should be fixed
    LOW = "low"            # Nice to have


@dataclass
class DirectoryViolation:
    """Represents a single directory structure violation"""
    violation_type: ViolationType
    severity: Severity
    directory: str
    module_count: int
    modules: List[str]
    description: str
    auto_fixable: bool = True
    migration_plan: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class DirectoryCheckResult:
    """Result of directory structure validation"""
    is_compliant: bool
    violations: List[DirectoryViolation]
    addon_directories: Dict[str, List[str]]  # directory -> module list
    canonical_dir_exists: bool
    total_modules: int
    fixes_applied: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "is_compliant": self.is_compliant,
            "violations": [v.to_dict() for v in self.violations],
            "addon_directories": self.addon_directories,
            "canonical_dir_exists": self.canonical_dir_exists,
            "total_modules": self.total_modules,
            "fixes_applied": self.fixes_applied or [],
        }


class DirectoryValidator:
    """Validates and fixes Odoo addon directory structure"""

    def __init__(self, repo_root: Path = Path(".")):
        self.repo_root = repo_root.resolve()
        self.results: Optional[DirectoryCheckResult] = None

    def is_odoo_module(self, path: Path) -> bool:
        """
        Check if a directory is an Odoo module (contains __manifest__.py).

        Args:
            path: Directory path to check

        Returns:
            True if directory contains a manifest file
        """
        if not path.is_dir():
            return False

        return any((path / manifest).exists() for manifest in MANIFEST_FILES)

    def find_addon_directories(self) -> Dict[str, List[str]]:
        """
        Discover all addon directories in the repository.

        Returns:
            Dictionary mapping directory name to list of module names
        """
        addon_dirs: Dict[str, List[str]] = {}

        # Check known addon directory names
        for addon_dir_name in KNOWN_ADDON_DIRS:
            addon_path = self.repo_root / addon_dir_name
            if addon_path.exists() and addon_path.is_dir():
                modules = self._find_modules_in_directory(addon_path)
                if modules:
                    addon_dirs[addon_dir_name] = modules

        return addon_dirs

    def _find_modules_in_directory(self, directory: Path) -> List[str]:
        """
        Find all Odoo modules in a directory.

        Args:
            directory: Path to addon directory

        Returns:
            List of module names (directory names)
        """
        modules = []

        try:
            for item in directory.iterdir():
                if self.is_odoo_module(item):
                    modules.append(item.name)
        except PermissionError:
            pass

        return sorted(modules)

    def detect_duplicate_modules(self, addon_dirs: Dict[str, List[str]]) -> Dict[str, List[str]]:
        """
        Detect modules that exist in multiple addon directories.

        Args:
            addon_dirs: Dictionary of addon directories and their modules

        Returns:
            Dictionary mapping module name to list of directories containing it
        """
        module_locations: Dict[str, List[str]] = {}

        for dir_name, modules in addon_dirs.items():
            for module in modules:
                if module not in module_locations:
                    module_locations[module] = []
                module_locations[module].append(dir_name)

        # Filter to only duplicates
        return {
            module: locations
            for module, locations in module_locations.items()
            if len(locations) > 1
        }

    def check_structure(self) -> DirectoryCheckResult:
        """
        Validate the addon directory structure.

        Returns:
            DirectoryCheckResult with all violations found
        """
        violations: List[DirectoryViolation] = []

        # Find all addon directories
        addon_dirs = self.find_addon_directories()

        # Check if canonical directory exists
        canonical_exists = CANONICAL_ADDONS_DIR in addon_dirs

        # Calculate total modules
        all_modules: Set[str] = set()
        for modules in addon_dirs.values():
            all_modules.update(modules)
        total_modules = len(all_modules)

        # Violation 1: Missing canonical directory
        if not canonical_exists:
            violations.append(
                DirectoryViolation(
                    violation_type=ViolationType.MISSING_CANONICAL_DIR,
                    severity=Severity.CRITICAL,
                    directory=CANONICAL_ADDONS_DIR,
                    module_count=0,
                    modules=[],
                    description=f"Canonical addon directory '{CANONICAL_ADDONS_DIR}/' does not exist",
                    auto_fixable=True,
                    migration_plan={
                        "action": "create_directory",
                        "target": CANONICAL_ADDONS_DIR,
                    }
                )
            )

        # Violation 2: Multiple addon directories
        if len(addon_dirs) > 1:
            non_canonical = [d for d in addon_dirs.keys() if d != CANONICAL_ADDONS_DIR]
            violations.append(
                DirectoryViolation(
                    violation_type=ViolationType.MULTIPLE_ADDON_DIRS,
                    severity=Severity.CRITICAL,
                    directory=", ".join(addon_dirs.keys()),
                    module_count=sum(len(m) for m in addon_dirs.values()),
                    modules=list(all_modules),
                    description=f"Found {len(addon_dirs)} addon directories. OCA standard requires single '{CANONICAL_ADDONS_DIR}/' directory",
                    auto_fixable=True,
                    migration_plan={
                        "action": "consolidate",
                        "source_directories": non_canonical,
                        "target_directory": CANONICAL_ADDONS_DIR,
                        "total_modules_to_move": sum(len(addon_dirs[d]) for d in non_canonical),
                    }
                )
            )

        # Violation 3: Non-canonical addon directories
        for dir_name, modules in addon_dirs.items():
            if dir_name != CANONICAL_ADDONS_DIR:
                violations.append(
                    DirectoryViolation(
                        violation_type=ViolationType.NON_CANONICAL_LOCATION,
                        severity=Severity.HIGH,
                        directory=dir_name,
                        module_count=len(modules),
                        modules=modules,
                        description=f"Modules in non-canonical directory '{dir_name}/' should be moved to '{CANONICAL_ADDONS_DIR}/'",
                        auto_fixable=True,
                        migration_plan={
                            "action": "move_modules",
                            "source": dir_name,
                            "target": CANONICAL_ADDONS_DIR,
                            "modules": modules,
                        }
                    )
                )

        # Violation 4: Empty addon directories
        for dir_name in KNOWN_ADDON_DIRS:
            dir_path = self.repo_root / dir_name
            if dir_path.exists() and dir_name not in addon_dirs:
                violations.append(
                    DirectoryViolation(
                        violation_type=ViolationType.EMPTY_ADDON_DIR,
                        severity=Severity.LOW,
                        directory=dir_name,
                        module_count=0,
                        modules=[],
                        description=f"Empty addon directory '{dir_name}/' should be removed",
                        auto_fixable=True,
                        migration_plan={
                            "action": "remove_directory",
                            "target": dir_name,
                        }
                    )
                )

        # Violation 5: Duplicate modules across directories
        duplicates = self.detect_duplicate_modules(addon_dirs)
        for module, locations in duplicates.items():
            violations.append(
                DirectoryViolation(
                    violation_type=ViolationType.DUPLICATE_MODULE,
                    severity=Severity.HIGH,
                    directory=", ".join(locations),
                    module_count=len(locations),
                    modules=[module],
                    description=f"Module '{module}' exists in multiple directories: {', '.join(locations)}",
                    auto_fixable=False,  # Requires manual conflict resolution
                    migration_plan={
                        "action": "resolve_duplicate",
                        "module": module,
                        "locations": locations,
                        "recommendation": f"Keep version in '{CANONICAL_ADDONS_DIR}/', remove others",
                    }
                )
            )

        self.results = DirectoryCheckResult(
            is_compliant=len(violations) == 0,
            violations=violations,
            addon_directories=addon_dirs,
            canonical_dir_exists=canonical_exists,
            total_modules=total_modules,
        )

        return self.results

    def fix_structure(self) -> List[str]:
        """
        Automatically fix directory structure violations.

        Returns:
            List of changes made
        """
        if not self.results:
            self.check_structure()

        changes: List[str] = []

        # Create canonical directory if missing
        canonical_path = self.repo_root / CANONICAL_ADDONS_DIR
        if not canonical_path.exists():
            canonical_path.mkdir(parents=True, exist_ok=True)
            changes.append(f"Created canonical directory: {CANONICAL_ADDONS_DIR}/")

        # Move modules from non-canonical directories
        for violation in self.results.violations:
            if violation.violation_type == ViolationType.NON_CANONICAL_LOCATION:
                if violation.migration_plan:
                    source_dir = violation.migration_plan["source"]
                    target_dir = violation.migration_plan["target"]
                    modules = violation.migration_plan["modules"]

                    for module in modules:
                        source_path = self.repo_root / source_dir / module
                        target_path = self.repo_root / target_dir / module

                        # Skip if target already exists (duplicate - manual resolution needed)
                        if target_path.exists():
                            changes.append(f"⚠️  Skipped {module}: already exists in {target_dir}/ (manual resolution required)")
                            continue

                        # Move module
                        source_path.rename(target_path)
                        changes.append(f"Moved {module}: {source_dir}/ → {target_dir}/")

            # Remove empty addon directories
            elif violation.violation_type == ViolationType.EMPTY_ADDON_DIR:
                dir_path = self.repo_root / violation.directory
                if dir_path.exists() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    changes.append(f"Removed empty directory: {violation.directory}/")

        self.results.fixes_applied = changes
        return changes

    def get_report(self) -> Dict[str, Any]:
        """
        Get structured directory structure report.

        Returns:
            Dictionary with summary and detailed results
        """
        if not self.results:
            self.check_structure()

        violations_by_type = {}
        violations_by_severity = {}

        for violation in self.results.violations:
            vtype = violation.violation_type.value
            violations_by_type[vtype] = violations_by_type.get(vtype, 0) + 1

            sev = violation.severity.value
            violations_by_severity[sev] = violations_by_severity.get(sev, 0) + 1

        return {
            "summary": {
                "is_compliant": self.results.is_compliant,
                "total_addon_directories": len(self.results.addon_directories),
                "canonical_dir_exists": self.results.canonical_dir_exists,
                "total_modules": self.results.total_modules,
                "total_violations": len(self.results.violations),
            },
            "violations_by_type": violations_by_type,
            "violations_by_severity": violations_by_severity,
            "addon_directories": self.results.addon_directories,
            "violations": [v.to_dict() for v in self.results.violations],
            "fixes_applied": self.results.fixes_applied or [],
        }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Check (and optionally fix) addon directory structure for OCA compliance."
    )
    parser.add_argument("--fix", action="store_true", help="Auto-fix directory structure in-place")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--repo-root", type=Path, default=Path("."), help="Path to repository root")
    args = parser.parse_args()

    validator = DirectoryValidator(repo_root=args.repo_root)
    result = validator.check_structure()

    if args.json:
        report = validator.get_report()
        print(json.dumps(report, indent=2))
    else:
        print(f"📁 Directory Structure Validation\n")
        print(f"Repository: {validator.repo_root}")
        print(f"Canonical directory: {CANONICAL_ADDONS_DIR}/\n")

        # Show addon directories
        if result.addon_directories:
            print(f"Found {len(result.addon_directories)} addon directories:")
            for dir_name, modules in result.addon_directories.items():
                canonical_marker = "✓" if dir_name == CANONICAL_ADDONS_DIR else "✗"
                print(f"  {canonical_marker} {dir_name}/ ({len(modules)} modules)")
            print()

        # Show violations
        if result.is_compliant:
            print("✅ Directory structure is compliant!")
        else:
            print(f"❌ Found {len(result.violations)} violations:\n")
            for violation in result.violations:
                severity_emoji = {
                    Severity.CRITICAL: "🔴",
                    Severity.HIGH: "🟠",
                    Severity.MEDIUM: "🟡",
                    Severity.LOW: "🔵",
                }[violation.severity]
                print(f"{severity_emoji} [{violation.severity.value}] {violation.description}")

                if violation.migration_plan:
                    print(f"   Migration: {violation.migration_plan.get('action', 'N/A')}")
                    if violation.module_count > 0:
                        print(f"   Modules: {violation.module_count}")
                print()

            # Apply fixes if requested
            if args.fix and any(v.auto_fixable for v in result.violations):
                print("🔧 Applying fixes...\n")
                changes = validator.fix_structure()
                if changes:
                    for change in changes:
                        print(f"   • {change}")
                else:
                    print("   No auto-fixable violations found")
                print()

        # Summary
        print(f"\n📊 Summary:")
        print(f"   Total modules: {result.total_modules}")
        print(f"   Addon directories: {len(result.addon_directories)}")
        print(f"   Violations: {len(result.violations)}")
        if result.is_compliant:
            print(f"   Status: ✅ Compliant")
        else:
            print(f"   Status: ❌ Non-compliant")

    # Exit code: 0 if compliant, 1 otherwise
    return 0 if result.is_compliant else 1


if __name__ == "__main__":
    sys.exit(main())

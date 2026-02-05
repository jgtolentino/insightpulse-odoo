#!/usr/bin/env python3
"""
Directory Validator Skill

Skill wrapper for directory_validator.py with standardized run_skill() interface.
Validates single canonical odoo_addons/ directory (OCA standard).
"""

from pathlib import Path
from typing import Any, Dict

from ..tools.directory_validator import DirectoryValidator


def run_skill(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute directory structure validation skill.

    Args:
        params: Skill parameters
            - repo_path (str): Path to repository root (default: ".")
            - fix (bool): Enable auto-fix (default: False)

    Returns:
        Skill result dictionary:
            - ok (bool): Whether directory structure is compliant
            - addon_directories (dict): Map of directory name to module list
            - violations (list): List of violation objects

    Example:
        >>> result = run_skill({"repo_path": ".", "fix": False})
        >>> print(f"Compliant: {result['ok']}")
        >>> print(f"Directories: {list(result['addon_directories'].keys())}")
    """
    # Extract parameters with defaults
    repo_path = Path(params.get("repo_path", "."))
    enable_fix = params.get("fix", False)

    # Initialize validator
    validator = DirectoryValidator(repo_root=repo_path)

    # Find addon directories
    addon_dirs = validator.find_addon_directories()

    # Detect violations
    violations = []

    # Check for canonical directory
    canonical_path = repo_path / "odoo_addons"
    if not canonical_path.exists():
        violations.append(
            {
                "violation_type": "missing_canonical_directory",
                "severity": "HIGH",
                "description": "Missing canonical odoo_addons/ directory",
                "expected_value": "odoo_addons/",
                "current_value": None,
                "auto_fixable": True,
            }
        )

    # Check for multiple directories
    if len(addon_dirs) > 1:
        other_dirs = [d for d in addon_dirs.keys() if d != "odoo_addons"]
        violations.append(
            {
                "violation_type": "multiple_addon_directories",
                "severity": "HIGH",
                "description": f"Found {len(addon_dirs)} addon directories (expected 1)",
                "expected_value": "odoo_addons/",
                "current_value": ", ".join(addon_dirs.keys()),
                "additional_directories": other_dirs,
                "auto_fixable": True,
            }
        )

    # Detect duplicate modules
    duplicates = validator.detect_duplicate_modules(addon_dirs)
    if duplicates:
        for module_name, locations in duplicates.items():
            violations.append(
                {
                    "violation_type": "duplicate_module",
                    "severity": "CRITICAL",
                    "description": f"Module '{module_name}' exists in multiple directories",
                    "module_name": module_name,
                    "locations": locations,
                    "auto_fixable": False,  # Requires manual resolution
                    "migration_complexity": "HIGH",
                }
            )

    # Apply fixes if enabled
    if enable_fix and violations:
        fixed = validator.fix_structure()
        if fixed:
            # Re-check after fix
            addon_dirs = validator.find_addon_directories()
            duplicates = validator.detect_duplicate_modules(addon_dirs)

            # Recalculate violations
            violations = []
            if not canonical_path.exists():
                violations.append(
                    {
                        "violation_type": "missing_canonical_directory",
                        "severity": "HIGH",
                        "description": "Missing canonical odoo_addons/ directory",
                    }
                )
            if len(addon_dirs) > 1:
                other_dirs = [d for d in addon_dirs.keys() if d != "odoo_addons"]
                violations.append(
                    {
                        "violation_type": "multiple_addon_directories",
                        "severity": "HIGH",
                        "description": f"Found {len(addon_dirs)} addon directories",
                        "additional_directories": other_dirs,
                    }
                )
            if duplicates:
                for module_name, locations in duplicates.items():
                    violations.append(
                        {
                            "violation_type": "duplicate_module",
                            "severity": "CRITICAL",
                            "module_name": module_name,
                            "locations": locations,
                        }
                    )

    # Calculate overall compliance
    is_compliant = len(violations) == 0

    return {
        "ok": is_compliant,
        "addon_directories": addon_dirs,
        "violations": violations,
    }

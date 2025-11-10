#!/usr/bin/env python3
"""
Manifest Validator Skill

Skill wrapper for manifest_checker.py with standardized run_skill() interface.
Validates __manifest__.py files for Odoo 18.0, LGPL-3, and InsightPulseAI metadata.
"""

from pathlib import Path
from typing import Any, Dict

from ..tools.manifest_checker import ManifestChecker


def run_skill(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute manifest validation skill.

    Args:
        params: Skill parameters
            - repo_path (str): Path to repository root (default: ".")
            - fix (bool): Enable auto-fix (default: False)

    Returns:
        Skill result dictionary:
            - ok (bool): Whether all manifests are compliant
            - total_modules (int): Total number of modules checked
            - compliant_modules (int): Number of compliant modules
            - violations (list): List of violation objects

    Example:
        >>> result = run_skill({"repo_path": ".", "fix": False})
        >>> print(f"Compliant: {result['ok']}")
        >>> print(f"Violations: {len(result['violations'])}")
    """
    # Extract parameters with defaults
    repo_path = Path(params.get("repo_path", "."))
    enable_fix = params.get("fix", False)

    # Determine addons path
    # Look for odoo_addons/ directory (canonical location)
    addons_path = repo_path / "odoo_addons"
    if not addons_path.exists():
        # Fallback to repo root if odoo_addons/ doesn't exist
        addons_path = repo_path

    # Initialize checker
    checker = ManifestChecker(addons_path=addons_path)

    # Find all modules
    modules = []
    for item in addons_path.iterdir():
        if item.is_dir() and (item / "__manifest__.py").exists():
            modules.append(item)

    if not modules:
        # No modules found
        return {
            "ok": True,
            "total_modules": 0,
            "compliant_modules": 0,
            "violations": [],
        }

    # Check each module
    all_violations = []
    compliant_count = 0

    for module_path in modules:
        manifest_path = module_path / "__manifest__.py"

        # Check manifest
        result = checker.check_manifest(manifest_path)

        if result.violations:
            # Add module context to violations
            for violation in result.violations:
                violation["module_name"] = module_path.name
                violation["module_path"] = str(module_path)
                all_violations.append(violation)

            # Apply fixes if enabled
            if enable_fix:
                fixed = checker.fix_manifest(manifest_path)
                if fixed:
                    # Re-check after fix
                    result = checker.check_manifest(manifest_path)
                    if not result.violations:
                        compliant_count += 1
        else:
            compliant_count += 1

    # Calculate overall compliance
    is_compliant = len(all_violations) == 0

    return {
        "ok": is_compliant,
        "total_modules": len(modules),
        "compliant_modules": compliant_count,
        "violations": all_violations,
    }

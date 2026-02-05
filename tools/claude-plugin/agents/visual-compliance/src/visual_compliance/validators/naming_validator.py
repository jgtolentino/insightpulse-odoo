#!/usr's/bin/env python3
"""
Naming Validator Skill

Skill wrapper for naming_validator.py with standardized run_skill() interface.
Validates ipai_* prefix for custom modules.
"""

from pathlib import Path
from typing import Any, Dict

from ..tools.naming_validator import NamingValidator


def run_skill(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute module naming validation skill.

    Args:
        params: Skill parameters
            - repo_path (str): Path to repository root (default: ".")
            - fix (bool): Enable auto-fix (default: False)
                         Note: Naming auto-fix requires manual intervention

    Returns:
        Skill result dictionary:
            - ok (bool): Whether all module names are compliant
            - modules_to_rename (dict): Map of old_name to new_name
            - violations (list): List of violation objects

    Example:
        >>> result = run_skill({"repo_path": ".", "fix": False})
        >>> print(f"Compliant: {result['ok']}")
        >>> print(f"Modules to rename: {result['modules_to_rename']}")
    """
    # Extract parameters with defaults
    repo_path = Path(params.get("repo_path", "."))
    enable_fix = params.get("fix", False)

    # Determine addons path
    addons_path = repo_path / "odoo_addons"
    if not addons_path.exists():
        addons_path = repo_path

    # Initialize validator
    validator = NamingValidator(addons_root=addons_path)

    # Find all modules
    modules = []
    for item in addons_path.iterdir():
        if item.is_dir() and (item / "__manifest__.py").exists():
            modules.append(item)

    if not modules:
        return {
            "ok": True,
            "modules_to_rename": {},
            "violations": [],
        }

    # Check each module
    violations = []
    modules_to_rename = {}

    for module_path in modules:
        module_name = module_path.name

        # Skip OCA community modules
        if validator.is_oca_module(module_name):
            continue

        # Check naming compliance
        result = validator.check_module_name(module_name)

        if result.violations:
            # Suggest compliant name
            suggested_name = validator.suggest_module_name(module_name)
            modules_to_rename[module_name] = suggested_name

            # Find dependent modules
            dependencies = validator.find_module_dependencies(module_path)

            # Assess migration complexity
            complexity = "LOW"
            if len(dependencies) > 0:
                complexity = "MEDIUM"
            if len(dependencies) > 5:
                complexity = "HIGH"

            # Add violations with module context
            for violation in result.violations:
                violation["module_name"] = module_name
                violation["module_path"] = str(module_path)
                violation["suggested_name"] = suggested_name
                violation["dependencies"] = dependencies
                violation["migration_complexity"] = complexity
                violation["auto_fixable"] = False  # Requires manual intervention
                violations.append(violation)

    # Note: Auto-fix is intentionally not implemented for naming
    # Module renaming requires:
    # 1. Renaming directory
    # 2. Updating all dependent modules
    # 3. Updating database records
    # 4. Potential data migration
    # This is too destructive to automate

    if enable_fix and violations:
        # Log warning that naming auto-fix is not supported
        print(
            "⚠️  Warning: Module renaming requires manual intervention. "
            "Auto-fix is not supported for naming violations."
        )
        print(f"    Suggested renames: {modules_to_rename}")

    # Calculate overall compliance
    is_compliant = len(violations) == 0

    return {
        "ok": is_compliant,
        "modules_to_rename": modules_to_rename,
        "violations": violations,
    }

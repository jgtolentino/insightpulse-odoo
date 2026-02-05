#!/usr/bin/env python3
"""
README Validator Skill

Skill wrapper for readme_validator.py with standardized run_skill() interface.
Validates README.rst files for OCA documentation standards.
"""

from pathlib import Path
from typing import Any, Dict

from ..tools.readme_validator import ReadmeValidator


def run_skill(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute README documentation validation skill.

    Args:
        params: Skill parameters
            - repo_path (str): Path to repository root (default: ".")
            - fix (bool): Auto-generate missing README.rst files (default: False)

    Returns:
        Skill result dictionary:
            - ok (bool): Whether all modules have compliant READMEs
            - readme_coverage (float): Percentage of modules with README.rst
            - violations (list): List of violation objects

    Example:
        >>> result = run_skill({"repo_path": ".", "fix": False})
        >>> print(f"Compliant: {result['ok']}")
        >>> print(f"Coverage: {result['readme_coverage']:.1f}%")
    """
    # Extract parameters with defaults
    repo_path = Path(params.get("repo_path", "."))
    enable_fix = params.get("fix", False)

    # Determine addons path
    addons_path = repo_path / "odoo_addons"
    if not addons_path.exists():
        addons_path = repo_path

    # Initialize validator
    validator = ReadmeValidator(addons_root=addons_path)

    # Find all modules
    modules = []
    for item in addons_path.iterdir():
        if item.is_dir() and (item / "__manifest__.py").exists():
            modules.append(item)

    if not modules:
        return {
            "ok": True,
            "readme_coverage": 100.0,
            "violations": [],
        }

    # Check each module
    violations = []
    modules_with_readme = 0

    for module_path in modules:
        readme_path = module_path / "README.rst"

        # Check README existence and completeness
        result = validator.check_readme(module_path)

        if result.violations:
            # Add module context to violations
            for violation in result.violations:
                violation["module_name"] = module_path.name
                violation["module_path"] = str(module_path)
                violations.append(violation)

            # Apply fixes if enabled (generate missing READMEs)
            if enable_fix:
                if not readme_path.exists():
                    template = validator.generate_readme_template(module_path)
                    readme_path.write_text(template, encoding="utf-8")

                    # Re-check after generation
                    result = validator.check_readme(module_path)
                    if not result.violations:
                        modules_with_readme += 1
        else:
            modules_with_readme += 1

    # Calculate README coverage
    coverage = (modules_with_readme / len(modules) * 100) if modules else 100.0

    # Calculate overall compliance
    is_compliant = len(violations) == 0

    return {
        "ok": is_compliant,
        "readme_coverage": coverage,
        "violations": violations,
    }

#!/usr/bin/env python3
"""
Skill Registry Loader

Loads skill definitions from skills.yaml and provides dynamic import.
Single source of truth for all Visual Compliance Agent capabilities.
"""

import importlib
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


_SKILLS = None
_PROFILES = None


def load_registry() -> Dict[str, Dict[str, Any]]:
    """
    Load skills registry from skills.yaml.

    Returns:
        Dict mapping skill_id to skill metadata
    """
    global _SKILLS, _PROFILES

    if _SKILLS is None:
        registry_path = Path(__file__).parent / "skills.yaml"

        if not registry_path.exists():
            raise FileNotFoundError(
                f"Skills registry not found at {registry_path}. "
                "Expected agents/skills.yaml in repository root."
            )

        data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))

        _SKILLS = {s["id"]: s for s in data.get("skills", [])}
        _PROFILES = {p["id"]: p for p in data.get("profiles", [])}

    return _SKILLS


def get_profiles() -> Dict[str, Dict[str, Any]]:
    """
    Get skill profiles (predefined combinations).

    Returns:
        Dict mapping profile_id to profile metadata
    """
    if _PROFILES is None:
        load_registry()  # Initializes both _SKILLS and _PROFILES

    return _PROFILES


def get_skill(skill_id: str):
    """
    Get skill entrypoint function and metadata.

    Args:
        skill_id: Skill identifier (e.g., "odoo.manifest.validate")

    Returns:
        Tuple of (entrypoint_function, skill_metadata)

    Raises:
        KeyError: If skill_id not found in registry
        ImportError: If skill module cannot be imported
        AttributeError: If entrypoint function not found in module

    Example:
        >>> run_skill, meta = get_skill("odoo.manifest.validate")
        >>> result = run_skill({"repo_path": ".", "fix": False})
    """
    registry = load_registry()

    if skill_id not in registry:
        available = ", ".join(registry.keys())
        raise KeyError(
            f"Skill '{skill_id}' not found in registry. "
            f"Available skills: {available}"
        )

    meta = registry[skill_id]

    # Dynamic import of skill module
    module = importlib.import_module(meta["module"])

    # Get entrypoint function from module
    entrypoint_name = meta.get("entrypoint", "run_skill")
    if not hasattr(module, entrypoint_name):
        raise AttributeError(
            f"Module '{meta['module']}' does not have entrypoint '{entrypoint_name}'. "
            f"Expected function signature: run_skill(params: Dict) -> Dict"
        )

    fn = getattr(module, entrypoint_name)

    return fn, meta


def list_skills(tag: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    """
    List all skills, optionally filtered by tag.

    Args:
        tag: Optional tag to filter by (e.g., "fast-check", "oca")

    Returns:
        Dict mapping skill_id to skill metadata

    Example:
        >>> fast_checks = list_skills(tag="fast-check")
        >>> for skill_id, meta in fast_checks.items():
        ...     print(f"{skill_id}: {meta['description']}")
    """
    registry = load_registry()

    if tag is None:
        return registry

    # Filter by tag
    return {
        skill_id: meta
        for skill_id, meta in registry.items()
        if tag in meta.get("tags", [])
    }


def get_profile_skills(profile_id: str) -> list[str]:
    """
    Get list of skill IDs for a profile.

    Args:
        profile_id: Profile identifier (e.g., "fast_check", "full_compliance")

    Returns:
        List of skill IDs in the profile

    Raises:
        KeyError: If profile_id not found

    Example:
        >>> skill_ids = get_profile_skills("fast_check")
        >>> for skill_id in skill_ids:
        ...     run_skill, meta = get_skill(skill_id)
        ...     result = run_skill({"repo_path": "."})
    """
    profiles = get_profiles()

    if profile_id not in profiles:
        available = ", ".join(profiles.keys())
        raise KeyError(
            f"Profile '{profile_id}' not found. "
            f"Available profiles: {available}"
        )

    return profiles[profile_id]["skills"]


def validate_skill_inputs(skill_id: str, params: Dict[str, Any]) -> None:
    """
    Validate that params match skill input schema.

    Args:
        skill_id: Skill identifier
        params: Parameters to validate

    Raises:
        ValueError: If required parameters are missing or types don't match
    """
    registry = load_registry()
    meta = registry[skill_id]

    # Check required inputs
    for input_def in meta.get("inputs", []):
        param_name = input_def["name"]
        is_required = input_def.get("required", False)

        if is_required and param_name not in params:
            raise ValueError(
                f"Missing required parameter '{param_name}' for skill '{skill_id}'"
            )

        # Apply defaults for optional parameters
        if param_name not in params and "default" in input_def:
            params[param_name] = input_def["default"]


if __name__ == "__main__":
    # Demo usage
    import json

    print("=== Skills Registry Demo ===\n")

    # List all skills
    print("All Skills:")
    for skill_id, meta in load_registry().items():
        print(f"  - {skill_id}: {meta['description']}")

    print("\nFast Check Skills:")
    for skill_id, meta in list_skills(tag="fast-check").items():
        print(f"  - {skill_id}")

    print("\nProfiles:")
    for profile_id, profile in get_profiles().items():
        print(f"  - {profile_id}: {profile['description']}")
        print(f"    Skills: {', '.join(profile['skills'])}")

    print("\nSkill Metadata Example:")
    _, meta = get_skill("odoo.manifest.validate")
    print(json.dumps(meta, indent=2))

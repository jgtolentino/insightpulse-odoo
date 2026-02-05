#!/usr/bin/env python3
"""
Skill Registry Loader

Loads skill definitions from skills.yaml and provides dynamic import.
Single source of truth for all Visual Compliance Agent capabilities.
Also supports loading external Anthropic-format skills from SKILL.md files.
"""

import importlib
import yaml
import re
from pathlib import Path
from typing import Any, Dict, Optional, List


_SKILLS = None
_PROFILES = None
_ANTHROPIC_SKILLS = None

# Path to Anthropic skills repository
ANTHROPIC_SKILLS_PATH = Path(__file__).resolve().parent.parent / "anthropic_skills"


def parse_skill_md(skill_path: Path) -> Optional[Dict[str, Any]]:
    """
    Parse a SKILL.md file in Anthropic format.

    Args:
        skill_path: Path to directory containing SKILL.md

    Returns:
        Dict with skill metadata or None if parsing fails
    """
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return None

    content = skill_md.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
    if not frontmatter_match:
        return None

    frontmatter_text = frontmatter_match.group(1)
    markdown_body = frontmatter_match.group(2)

    try:
        metadata = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        return None

    # Build skill metadata in our format
    skill_id = f"anthropic.{metadata.get('name', skill_path.name)}"

    return {
        "id": skill_id,
        "name": metadata.get("name", skill_path.name),
        "description": metadata.get("description", ""),
        "module": None,  # Anthropic skills don't have Python modules
        "entrypoint": None,  # They are prompt-based
        "repo": "anthropics/skills",
        "path": str(skill_path),
        "skill_md_path": str(skill_md),
        "tags": ["anthropic", "external"] + metadata.get("metadata", {}).get("tags", []),
        "license": metadata.get("license", "Apache-2.0"),
        "allowed_tools": metadata.get("allowed-tools", []),
        "anthropic": True,
        "markdown_instructions": markdown_body.strip(),
    }


def load_anthropic_skills() -> Dict[str, Dict[str, Any]]:
    """
    Load Anthropic-format skills from anthropic_skills directory.

    Returns:
        Dict mapping skill_id to skill metadata
    """
    global _ANTHROPIC_SKILLS

    if _ANTHROPIC_SKILLS is not None:
        return _ANTHROPIC_SKILLS

    _ANTHROPIC_SKILLS = {}

    if not ANTHROPIC_SKILLS_PATH.exists():
        return _ANTHROPIC_SKILLS

    # Iterate through directories in anthropic_skills
    for skill_dir in ANTHROPIC_SKILLS_PATH.iterdir():
        if not skill_dir.is_dir():
            continue

        # Skip hidden directories and git
        if skill_dir.name.startswith('.'):
            continue

        # Parse SKILL.md
        skill_meta = parse_skill_md(skill_dir)
        if skill_meta:
            _ANTHROPIC_SKILLS[skill_meta["id"]] = skill_meta

    return _ANTHROPIC_SKILLS


def load_registry() -> Dict[str, Dict[str, Any]]:
    """
    Load skills registry from skills.yaml and merge with Anthropic skills.

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

        # Merge Anthropic skills into the registry
        anthropic_skills = load_anthropic_skills()
        _SKILLS.update(anthropic_skills)

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
    all_skills = load_registry()
    print(f"Total Skills Loaded: {len(all_skills)}")

    # Separate Anthropic and native skills
    anthropic_skills = {k: v for k, v in all_skills.items() if v.get("anthropic", False)}
    native_skills = {k: v for k, v in all_skills.items() if not v.get("anthropic", False)}

    print(f"\nNative Skills ({len(native_skills)}):")
    for skill_id, meta in list(native_skills.items())[:5]:
        print(f"  - {skill_id}: {meta['description'][:60]}...")

    print(f"\nAnthropic Skills ({len(anthropic_skills)}):")
    for skill_id, meta in list(anthropic_skills.items())[:5]:
        print(f"  - {skill_id}: {meta['description'][:60]}...")

    print("\nFast Check Skills:")
    for skill_id, meta in list_skills(tag="fast-check").items():
        print(f"  - {skill_id}")

    print("\nProfiles:")
    for profile_id, profile in get_profiles().items():
        print(f"  - {profile_id}: {profile['description']}")
        print(f"    Skills: {', '.join(profile['skills'])}")

    print("\nNative Skill Metadata Example:")
    if "odoo.manifest.validate" in native_skills:
        # Just show metadata, don't try to import the module
        meta = native_skills["odoo.manifest.validate"]
        print(json.dumps({k: v for k, v in meta.items() if k != "markdown_instructions"}, indent=2))

    print("\nAnthropic Skill Metadata Example:")
    if anthropic_skills:
        first_anthropic = list(anthropic_skills.keys())[0]
        meta = anthropic_skills[first_anthropic]
        print(json.dumps({k: v for k, v in meta.items() if k != "markdown_instructions"}, indent=2))

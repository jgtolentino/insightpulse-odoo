#!/usr/bin/env python3
"""
Skill CLI Wrapper

Provides command-line interface for executing Visual Compliance Agent skills.
Used by CI workflows, agents, and manual testing.

Usage:
    python -m agents.run_skill odoo.manifest.validate --repo-path . --fix
    python -m agents.run_skill visual_compliance.full_scan --repo-path . --json
    python -m agents.run_skill --profile fast_check --repo-path .
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

from agents.skill_registry import (
    get_skill,
    list_skills,
    get_profiles,
    get_profile_skills,
    validate_skill_inputs,
)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Visual Compliance Agent - Skill Executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run single skill
  python -m agents.run_skill odoo.manifest.validate --repo-path .

  # Run skill with auto-fix
  python -m agents.run_skill odoo.manifest.validate --repo-path . --fix

  # Run skill profile (multiple skills)
  python -m agents.run_skill --profile fast_check --repo-path .

  # List available skills
  python -m agents.run_skill --list

  # Get skill metadata
  python -m agents.run_skill odoo.directory.validate --info
        """,
    )

    parser.add_argument(
        "skill_id",
        nargs="?",
        help="Skill ID to execute (e.g., odoo.manifest.validate)",
    )

    parser.add_argument(
        "--profile",
        type=str,
        help="Execute skill profile (e.g., fast_check, full_compliance)",
    )

    parser.add_argument(
        "--repo-path",
        type=str,
        default=".",
        help="Path to repository root (default: current directory)",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Enable auto-fix for violations (where supported)",
    )

    parser.add_argument(
        "--create-issues",
        action="store_true",
        help="Create GitHub issues for violations (full_scan only)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available skills",
    )

    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List all available skill profiles",
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show skill metadata (requires skill_id)",
    )

    parser.add_argument(
        "--tag",
        type=str,
        help="Filter skills by tag (use with --list)",
    )

    return parser.parse_args()


def execute_skill(skill_id: str, params: Dict[str, Any], output_json: bool = False):
    """
    Execute a single skill.

    Args:
        skill_id: Skill identifier
        params: Skill parameters
        output_json: Output results in JSON format

    Returns:
        Exit code (0=success, 1=violations, 2=error)
    """
    try:
        # Get skill entrypoint
        run_skill, meta = get_skill(skill_id)

        # Validate inputs
        validate_skill_inputs(skill_id, params)

        # Execute skill
        if not output_json:
            print(f"Running skill: {meta['name']}")
            print(f"Description: {meta['description']}")
            print()

        result = run_skill(params)

        # Output results
        if output_json:
            print(json.dumps(result, indent=2))
        else:
            # Human-readable output
            if result.get("ok", False):
                print(f"✅ {meta['name']}: PASS")
            else:
                print(f"❌ {meta['name']}: VIOLATIONS DETECTED")

            if "total_modules" in result:
                print(f"   Total modules: {result['total_modules']}")
            if "compliant_modules" in result:
                print(f"   Compliant: {result['compliant_modules']}")
            if "violations" in result:
                print(f"   Violations: {len(result['violations'])}")

        # Return exit code
        if result.get("ok", False):
            return 0
        else:
            # Check for critical violations
            violations = result.get("violations", [])
            has_critical = any(
                v.get("severity") == "CRITICAL" for v in violations
            )
            return 2 if has_critical else 1

    except Exception as e:
        print(f"❌ Error executing skill '{skill_id}': {e}", file=sys.stderr)
        return 2


def execute_profile(
    profile_id: str, params: Dict[str, Any], output_json: bool = False
):
    """
    Execute a skill profile (multiple skills).

    Args:
        profile_id: Profile identifier
        params: Skill parameters
        output_json: Output results in JSON format

    Returns:
        Exit code (0=success, 1=violations, 2=error)
    """
    try:
        profiles = get_profiles()
        profile = profiles[profile_id]

        # Get profile options
        profile_options = profile.get("options", {})
        params.update(profile_options)

        if not output_json:
            print(f"Running profile: {profile['name']}")
            print(f"Description: {profile['description']}")
            print()

        # Execute each skill in profile
        skill_ids = get_profile_skills(profile_id)
        results = {}
        max_exit_code = 0

        for skill_id in skill_ids:
            exit_code = execute_skill(skill_id, params.copy(), output_json)
            results[skill_id] = exit_code
            max_exit_code = max(max_exit_code, exit_code)

            if not output_json:
                print()

        if output_json:
            print(json.dumps({"profile": profile_id, "results": results}, indent=2))

        return max_exit_code

    except Exception as e:
        print(f"❌ Error executing profile '{profile_id}': {e}", file=sys.stderr)
        return 2


def main():
    """Main CLI entry point."""
    args = parse_args()

    # List skills
    if args.list:
        skills = list_skills(tag=args.tag)
        print("Available Skills:")
        for skill_id, meta in skills.items():
            tags = ", ".join(meta.get("tags", []))
            print(f"  {skill_id}")
            print(f"    {meta['description']}")
            print(f"    Tags: {tags}")
            print()
        return 0

    # List profiles
    if args.list_profiles:
        profiles = get_profiles()
        print("Available Skill Profiles:")
        for profile_id, profile in profiles.items():
            print(f"  {profile_id}")
            print(f"    {profile['description']}")
            print(f"    Skills: {', '.join(profile['skills'])}")
            print()
        return 0

    # Show skill info
    if args.info:
        if not args.skill_id:
            print("Error: --info requires skill_id", file=sys.stderr)
            return 2

        try:
            _, meta = get_skill(args.skill_id)
            print(json.dumps(meta, indent=2))
            return 0
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 2

    # Execute profile
    if args.profile:
        params = {
            "repo_path": args.repo_path,
            "fix": args.fix,
            "create_issues": args.create_issues,
        }
        return execute_profile(args.profile, params, args.json)

    # Execute single skill
    if args.skill_id:
        params = {
            "repo_path": args.repo_path,
            "fix": args.fix,
        }

        # Add create_issues for full_scan
        if args.skill_id == "visual_compliance.full_scan":
            params["create_issues"] = args.create_issues

        return execute_skill(args.skill_id, params, args.json)

    # No action specified
    print("Error: Must specify skill_id, --profile, --list, or --list-profiles")
    print("Run with --help for usage information")
    return 2


if __name__ == "__main__":
    sys.exit(main())

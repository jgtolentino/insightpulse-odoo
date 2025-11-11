#!/usr/bin/env python3
"""
Import Anthropic Skills to YAML

Scans the anthropic_skills directory and generates YAML entries
for integration into agents/skills.yaml or for documentation.

Usage:
    python3 scripts/import_anthropic_skills.py
    python3 scripts/import_anthropic_skills.py --append  # Append to skills.yaml
    python3 scripts/import_anthropic_skills.py --export anthropic_skills.yaml  # Export to file
"""

import argparse
import sys
from pathlib import Path

import yaml

# Add parent directory to path so we can import skill_registry
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.skill_registry import ANTHROPIC_SKILLS_PATH, load_anthropic_skills


def export_to_yaml(skills: dict, output_path: Path = None, append: bool = False):
    """
    Export Anthropic skills to YAML format.

    Args:
        skills: Dict of skill_id to skill metadata
        output_path: Optional path to write to (default: stdout)
        append: If True, append to existing skills.yaml
    """
    # Convert to YAML-compatible format
    skill_list = []
    for skill_id, meta in skills.items():
        yaml_skill = {
            "id": skill_id,
            "name": meta["name"],
            "description": meta["description"],
            "repo": meta["repo"],
            "path": meta["path"],
            "tags": meta["tags"],
            "license": meta["license"],
            "anthropic": True,
        }

        if meta.get("allowed_tools"):
            yaml_skill["allowed_tools"] = meta["allowed_tools"]

        skill_list.append(yaml_skill)

    # Sort by skill ID for consistency
    skill_list.sort(key=lambda x: x["id"])

    if append and output_path:
        # Load existing skills.yaml and append
        if output_path.exists():
            existing_data = yaml.safe_load(output_path.read_text(encoding="utf-8"))
            existing_skills = existing_data.get("skills", [])

            # Remove any existing Anthropic skills to avoid duplicates
            existing_skills = [
                s for s in existing_skills if not s.get("anthropic", False)
            ]

            # Append new Anthropic skills
            existing_skills.extend(skill_list)
            existing_data["skills"] = existing_skills

            # Write back
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("---\n")
                yaml.dump(existing_data, f, default_flow_style=False, sort_keys=False)

            print(f"✅ Appended {len(skill_list)} Anthropic skills to {output_path}")
        else:
            print(f"❌ Error: {output_path} does not exist")
            sys.exit(1)
    elif output_path:
        # Write to new file
        output_data = {
            "# Anthropic Skills Import": None,
            "# Auto-generated from anthropic_skills directory": None,
            "skills": skill_list,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write("# Anthropic Skills Import\n")
            f.write("# Auto-generated from anthropic_skills directory\n\n")
            yaml.dump(
                {"skills": skill_list}, f, default_flow_style=False, sort_keys=False
            )

        print(f"✅ Exported {len(skill_list)} Anthropic skills to {output_path}")
    else:
        # Print to stdout
        print("---")
        print("# Anthropic Skills Import")
        print("# Auto-generated from anthropic_skills directory\n")
        print(
            yaml.dump({"skills": skill_list}, default_flow_style=False, sort_keys=False)
        )


def main():
    parser = argparse.ArgumentParser(
        description="Import Anthropic skills to YAML format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Print to stdout
  python3 scripts/import_anthropic_skills.py

  # Export to a new file
  python3 scripts/import_anthropic_skills.py --export anthropic_skills.yaml

  # Append to existing skills.yaml
  python3 scripts/import_anthropic_skills.py --append

  # Append to specific file
  python3 scripts/import_anthropic_skills.py --append --file agents/skills_extended.yaml
        """,
    )

    parser.add_argument(
        "--export", type=str, metavar="FILE", help="Export to a new YAML file"
    )

    parser.add_argument(
        "--append", action="store_true", help="Append to existing skills.yaml"
    )

    parser.add_argument(
        "--file",
        type=str,
        default="agents/skills.yaml",
        help="Target file for --append (default: agents/skills.yaml)",
    )

    args = parser.parse_args()

    # Check if anthropic_skills directory exists
    if not ANTHROPIC_SKILLS_PATH.exists():
        print(f"❌ Error: {ANTHROPIC_SKILLS_PATH} does not exist")
        print("Run the following to clone it:")
        print("  git clone https://github.com/anthropics/skills.git anthropic_skills")
        sys.exit(1)

    # Load Anthropic skills
    print(f"Loading Anthropic skills from {ANTHROPIC_SKILLS_PATH}...")
    skills = load_anthropic_skills()

    if not skills:
        print("❌ No Anthropic skills found")
        sys.exit(1)

    print(f"Found {len(skills)} Anthropic skills")

    # Export
    output_path = None
    if args.export:
        output_path = Path(args.export)
    elif args.append:
        output_path = Path(args.file)

    export_to_yaml(skills, output_path, append=args.append)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Skills Consolidation Script
Scans all skills directories and generates:
- skills/REGISTRY.json
- skills/REGISTRY.mcp.json
- docs/claude-code-skills/Section19.generated.md
"""

import json
import pathlib
from datetime import datetime
from typing import Any, Dict, List

# Skill search paths
SKILL_PATHS = ["skills/core", "skills/proposed", "skills/integrations"]

# Output paths
REGISTRY_PATH = "skills/REGISTRY.json"
MCP_REGISTRY_PATH = "skills/REGISTRY.mcp.json"
SECTION19_PATH = "docs/claude-code-skills/Section19.generated.md"


def find_skills() -> List[pathlib.Path]:
    """Find all SKILL.md files in the skill paths"""
    skills = []
    repo_root = pathlib.Path(__file__).parent.parent.parent

    for search_path in SKILL_PATHS:
        skill_dir = repo_root / search_path
        if skill_dir.exists():
            for skill_file in skill_dir.rglob("SKILL.md"):
                skills.append(skill_file)

    return sorted(skills)


def parse_skill_frontmatter(skill_path: pathlib.Path) -> Dict[str, Any]:
    """Extract metadata from SKILL.md file"""
    content = skill_path.read_text()
    lines = content.split("\n")

    metadata = {
        "skill_id": "",
        "version": "1.0.0",
        "category": "",
        "expertise_level": "",
        "path": str(
            skill_path.parent.relative_to(skill_path.parent.parent.parent.parent)
        ),
        "file": str(skill_path.relative_to(skill_path.parent.parent.parent.parent)),
    }

    # Parse frontmatter (simple key: value parsing)
    for line in lines[:20]:  # Check first 20 lines for metadata
        if line.startswith("**Skill ID:**"):
            metadata["skill_id"] = line.split("`")[1] if "`" in line else ""
        elif line.startswith("**Version:**"):
            metadata["version"] = line.split("**Version:**")[1].strip()
        elif line.startswith("**Category:**"):
            metadata["category"] = line.split("**Category:**")[1].strip()
        elif line.startswith("**Expertise Level:**"):
            metadata["expertise_level"] = line.split("**Expertise Level:**")[1].strip()

    # Extract purpose section
    purpose_start = content.find("## 🎯 Purpose")
    if purpose_start != -1:
        purpose_end = content.find("##", purpose_start + 10)
        purpose_section = (
            content[purpose_start:purpose_end]
            if purpose_end != -1
            else content[purpose_start:]
        )
        # Get first paragraph after Purpose heading
        paragraphs = [
            p.strip()
            for p in purpose_section.split("\n\n")
            if p.strip() and not p.strip().startswith("#")
        ]
        metadata["purpose"] = paragraphs[0] if paragraphs else ""

    # Extract key capabilities
    capabilities_start = content.find("### Key Capabilities")
    if capabilities_start != -1:
        capabilities_end = content.find("##", capabilities_start + 10)
        capabilities_section = (
            content[capabilities_start:capabilities_end]
            if capabilities_end != -1
            else content[capabilities_start:]
        )
        capabilities = [
            line.strip("- ").strip()
            for line in capabilities_section.split("\n")
            if line.strip().startswith("-")
        ]
        metadata["capabilities"] = capabilities[:5]  # First 5 capabilities
    else:
        metadata["capabilities"] = []

    return metadata


def generate_registry(skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate main registry JSON"""
    return {
        "version": "0.2.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "skill_count": len(skills),
        "skills": skills,
    }


def generate_mcp_registry(skills: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate MCP usage map"""
    mcp_map = {}

    for skill in skills:
        skill_id = skill["skill_id"]
        # Map skills to MCP services/actions
        if "github" in skill_id.lower():
            mcp_map[skill_id] = {
                "mcp_service": "github",
                "actions": ["api_call", "webhook_handle", "workflow_trigger"],
            }
        elif "odoo" in skill_id.lower() or "automation" in skill_id.lower():
            mcp_map[skill_id] = {
                "mcp_service": "odoo",
                "actions": ["module_install", "api_call", "workflow_execute"],
            }
        elif "git" in skill_id.lower():
            mcp_map[skill_id] = {
                "mcp_service": "git",
                "actions": ["branch_create", "commit", "pr_create"],
            }
        elif "draxlr" in skill_id.lower():
            mcp_map[skill_id] = {
                "mcp_service": "draxlr",
                "actions": ["dataset_create", "chart_create", "dashboard_embed"],
            }
        else:
            mcp_map[skill_id] = {"mcp_service": "generic", "actions": ["execute"]}

    return {
        "version": "0.2.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "mcp_mappings": mcp_map,
    }


def generate_section19_md(skills: List[Dict[str, Any]]) -> str:
    """Generate Section 19 markdown for Claude Code"""
    md_lines = [
        "# Section 19: InsightPulse Skills Registry",
        "",
        f"> Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"> Total Skills: {len(skills)}",
        "",
        "## Available Skills",
        "",
    ]

    # Group by category
    by_category = {}
    for skill in skills:
        cat = skill.get("category", "Uncategorized")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(skill)

    for category in sorted(by_category.keys()):
        md_lines.append(f"### {category}")
        md_lines.append("")

        for skill in sorted(by_category[category], key=lambda s: s["skill_id"]):
            md_lines.append(f"#### `{skill['skill_id']}` (v{skill['version']})")
            md_lines.append("")

            if skill.get("purpose"):
                md_lines.append(skill["purpose"])
                md_lines.append("")

            if skill.get("capabilities"):
                md_lines.append("**Key Capabilities:**")
                for cap in skill["capabilities"]:
                    md_lines.append(f"- {cap}")
                md_lines.append("")

            md_lines.append(f"**Path:** `{skill['path']}`")
            md_lines.append(
                f"**Expertise Level:** {skill.get('expertise_level', 'N/A')}"
            )
            md_lines.append("")
            md_lines.append("---")
            md_lines.append("")

    return "\n".join(md_lines)


def main():
    """Main consolidation process"""
    print("🔍 Scanning for skills...")

    skill_files = find_skills()
    print(f"   Found {len(skill_files)} skill files")

    print("📋 Parsing skill metadata...")
    skills = []
    for skill_file in skill_files:
        try:
            metadata = parse_skill_frontmatter(skill_file)
            if metadata["skill_id"]:
                skills.append(metadata)
                print(f"   ✓ {metadata['skill_id']}")
        except Exception as e:
            print(f"   ✗ Error parsing {skill_file}: {e}")

    print(f"\n✅ Parsed {len(skills)} skills successfully")

    # Generate outputs
    print("\n📝 Generating registry files...")

    # Main registry
    registry = generate_registry(skills)
    registry_path = pathlib.Path(REGISTRY_PATH)
    registry_path.write_text(json.dumps(registry, indent=2))
    print(f"   ✓ {REGISTRY_PATH}")

    # MCP registry
    mcp_registry = generate_mcp_registry(skills)
    mcp_path = pathlib.Path(MCP_REGISTRY_PATH)
    mcp_path.write_text(json.dumps(mcp_registry, indent=2))
    print(f"   ✓ {MCP_REGISTRY_PATH}")

    # Section 19 markdown
    section19_content = generate_section19_md(skills)
    section19_path = pathlib.Path(SECTION19_PATH)
    section19_path.parent.mkdir(parents=True, exist_ok=True)
    section19_path.write_text(section19_content)
    print(f"   ✓ {SECTION19_PATH}")

    print(f"\n✨ Consolidation complete! {len(skills)} skills registered.")


if __name__ == "__main__":
    main()

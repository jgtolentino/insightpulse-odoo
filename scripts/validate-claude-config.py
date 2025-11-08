#!/usr/bin/env python3
"""
validate-claude-config.py - Python-based Claude interface configuration validator

Purpose: Enhanced validation with interface hierarchy consistency checks
Last Updated: 2025-11-08
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ANSI colors for output
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"  # No Color


def log_error(message: str) -> None:
    """Log error message"""
    print(f"{RED}❌ ERROR: {message}{NC}")


def log_warning(message: str) -> None:
    """Log warning message"""
    print(f"{YELLOW}⚠️  WARNING: {message}{NC}")


def log_success(message: str) -> None:
    """Log success message"""
    print(f"{GREEN}✅ {message}{NC}")


def find_project_root() -> Path:
    """Find project root by looking for claude.md"""
    current = Path.cwd()
    while current != current.parent:
        if (current / "claude.md").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root (no claude.md found)")


def parse_claude_md_sections(claude_md_path: Path) -> Dict[int, str]:
    """Parse claude.md into sections"""
    sections = {}
    current_section = None
    current_content = []

    with open(claude_md_path, "r", encoding="utf-8") as f:
        for line in f:
            # Match section headers: ## 0) Title, ## 1) Title, etc.
            match = re.match(r"^## (\d+)\)", line)
            if match:
                # Save previous section
                if current_section is not None:
                    sections[current_section] = "".join(current_content)

                # Start new section
                current_section = int(match.group(1))
                current_content = [line]
            elif current_section is not None:
                current_content.append(line)

        # Save last section
        if current_section is not None:
            sections[current_section] = "".join(current_content)

    return sections


def validate_claude_md_structure(sections: Dict[int, str]) -> List[str]:
    """Validate claude.md structure (sections 0-23)"""
    errors = []

    # Check for all required sections
    required_sections = list(range(24))
    missing_sections = [s for s in required_sections if s not in sections]

    if missing_sections:
        errors.append(f"Missing sections: {missing_sections}")

    return errors


def extract_model_version(sections: Dict[int, str]) -> str:
    """Extract model version from section 22"""
    if 22 not in sections:
        return None

    section_22 = sections[22]
    # Look for claude-* model identifier
    match = re.search(r"claude-[a-z0-9-]+", section_22)
    if match:
        return match.group(0)

    return None


def extract_mcp_servers(sections: Dict[int, str]) -> Set[str]:
    """Extract MCP server names from section 17"""
    if 17 not in sections:
        return set()

    section_17 = sections[17]
    # Extract server names between **name** markers
    servers = set()
    for match in re.finditer(r"\*\*([a-z_-]+)\*\*", section_17):
        servers.add(match.group(1))

    return servers


def extract_agent_names(sections: Dict[int, str]) -> Set[str]:
    """Extract agent names from section 18"""
    if 18 not in sections:
        return set()

    section_18 = sections[18]
    # Extract agent names from ### 1. agent_name format
    agents = set()
    for match in re.finditer(r"### \d+\. ([a-z_]+)", section_18):
        agents.add(match.group(1))

    return agents


def extract_skill_names(sections: Dict[int, str]) -> Set[str]:
    """Extract skill names from section 19"""
    if 19 not in sections:
        return set()

    section_19 = sections[19]
    # Extract skill names between **name** markers
    skills = set()
    for match in re.finditer(r"\*\*([a-z0-9-]+)\*\*", section_19):
        skills.add(match.group(1))

    return skills


def validate_mcp_config(claude_mcp_servers: Set[str], project_root: Path) -> List[str]:
    """Validate MCP configuration against vscode-mcp-config.json"""
    errors = []
    mcp_config_path = project_root / "mcp" / "vscode-mcp-config.json"

    if not mcp_config_path.exists():
        errors.append(f"MCP config file not found: {mcp_config_path}")
        return errors

    try:
        with open(mcp_config_path, "r", encoding="utf-8") as f:
            mcp_config = json.load(f)

        actual_servers = set(mcp_config.get("mcpServers", {}).keys())

        # Compare
        missing_in_config = claude_mcp_servers - actual_servers
        extra_in_config = actual_servers - claude_mcp_servers

        if missing_in_config:
            errors.append(f"MCP servers in claude.md but NOT in config: {missing_in_config}")

        if extra_in_config:
            errors.append(f"MCP servers in config but NOT in claude.md: {extra_in_config}")

    except json.JSONDecodeError as e:
        errors.append(f"Failed to parse MCP config: {e}")

    return errors


def validate_agent_files(claude_agents: Set[str]) -> List[str]:
    """Validate agent files against ~/.claude/superclaude/agents/"""
    errors = []
    agent_dir = Path.home() / ".claude" / "superclaude" / "agents" / "domain"

    if not agent_dir.exists():
        errors.append(f"Agent directory not found: {agent_dir}")
        return errors

    # Find all agent YAML files
    actual_agents = set()
    for agent_file in agent_dir.glob("*.agent.yaml"):
        agent_name = agent_file.stem.replace(".agent", "")
        actual_agents.add(agent_name)

    # Compare
    missing_agents = claude_agents - actual_agents
    extra_agents = actual_agents - claude_agents

    if missing_agents:
        errors.append(f"Agents in claude.md but missing files: {missing_agents}")

    if extra_agents:
        errors.append(f"Agent files exist but not documented in claude.md: {extra_agents}")

    return errors


def validate_skill_directories(claude_skills: Set[str], project_root: Path) -> List[str]:
    """Validate skill directories against docs/claude-code-skills/"""
    errors = []
    skills_dir = project_root / "docs" / "claude-code-skills"

    if not skills_dir.exists():
        errors.append(f"Skills directory not found: {skills_dir}")
        return errors

    # Find all skill directories
    actual_skills = set()
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            actual_skills.add(skill_dir.name)

    # Compare
    missing_skills = claude_skills - actual_skills
    extra_skills = actual_skills - claude_skills

    if missing_skills:
        errors.append(f"Skills in claude.md but missing directories: {missing_skills}")

    if extra_skills:
        errors.append(f"Skill directories exist but not documented in claude.md: {extra_skills}")

    return errors


def validate_interface_hierarchy(project_root: Path) -> List[str]:
    """Validate interface hierarchy consistency"""
    errors = []

    # Check all interface files exist
    interface_files = [
        project_root / "claude.md",
        project_root / ".claude" / "settings.json",
        project_root / ".claude" / "settings.local.json",
        project_root / "mcp" / "vscode-mcp-config.json",
        project_root / "docs" / "SUPERCLAUDE_ARCHITECTURE.md",
    ]

    for file_path in interface_files:
        if not file_path.exists():
            errors.append(f"Missing interface file: {file_path}")

    return errors


def generate_report(
    project_root: Path,
    validation_results: Dict[str, List[str]],
    model_version: str,
) -> None:
    """Generate validation report"""
    report_path = project_root / "docs" / "claude-config-validation.md"

    total_errors = sum(len(errors) for errors in validation_results.values())

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# Claude Configuration Validation Report\n\n")
        f.write(f"**Generated**: {os.popen('date').read().strip()}\n")
        f.write(f"**Repository**: InsightPulse Odoo\n")
        f.write(f"**Canonical Source**: /claude.md\n\n")
        f.write("---\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **Total Errors**: {total_errors}\n")
        f.write(f"- **Model Version**: {model_version or 'NOT FOUND'}\n\n")
        f.write("---\n\n")
        f.write("## Validation Results\n\n")

        for section, errors in validation_results.items():
            f.write(f"### {section}\n\n")
            if errors:
                for error in errors:
                    f.write(f"❌ {error}\n")
            else:
                f.write("✅ No issues found\n")
            f.write("\n")

        f.write("---\n\n")
        f.write("## Recommendations\n\n")

        if total_errors > 0:
            f.write("1. **Fix Configuration Drift**: Sync configurations across interface files\n")
            f.write("2. **Update Documentation**: Ensure all sections are documented in claude.md\n")
            f.write("3. **Validate Files**: Check that all referenced files exist\n")
            f.write("4. **Run Sync Script**: Execute `scripts/sync-claude-configs.sh`\n")
        else:
            f.write("✅ No drift detected. Configuration is synchronized.\n")

    print(f"\n{GREEN}✅ Validation report generated: {report_path}{NC}")


def main():
    """Main validation workflow"""
    parser = argparse.ArgumentParser(description="Validate Claude interface configurations")
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Project root directory (default: auto-detect)",
    )
    args = parser.parse_args()

    # Find project root
    try:
        project_root = args.project_root or find_project_root()
    except RuntimeError as e:
        log_error(str(e))
        sys.exit(1)

    print("=" * 50)
    print("Claude Config Validation - InsightPulse Odoo")
    print("=" * 50)
    print()

    # Step 1: Parse claude.md
    print("1. Parsing /claude.md...")
    claude_md_path = project_root / "claude.md"

    if not claude_md_path.exists():
        log_error(f"claude.md not found at {claude_md_path}")
        sys.exit(1)

    sections = parse_claude_md_sections(claude_md_path)
    log_success(f"Parsed {len(sections)} sections from claude.md")

    # Step 2: Validate structure
    print("\n2. Validating claude.md structure...")
    structure_errors = validate_claude_md_structure(sections)

    if structure_errors:
        for error in structure_errors:
            log_error(error)
    else:
        log_success("All 24 sections (0-23) present in claude.md")

    # Step 3: Extract model version
    print("\n3. Extracting model version from section 22...")
    model_version = extract_model_version(sections)

    if model_version:
        log_success(f"Model version: {model_version}")
    else:
        log_warning("Could not extract model version from section 22")

    # Step 4: Validate MCP servers
    print("\n4. Validating MCP servers...")
    claude_mcp_servers = extract_mcp_servers(sections)
    mcp_errors = validate_mcp_config(claude_mcp_servers, project_root)

    if mcp_errors:
        for error in mcp_errors:
            log_warning(error)
    else:
        log_success("MCP server configuration matches claude.md")

    # Step 5: Validate agents
    print("\n5. Validating agent definitions...")
    claude_agents = extract_agent_names(sections)
    agent_errors = validate_agent_files(claude_agents)

    if agent_errors:
        for error in agent_errors:
            log_warning(error)
    else:
        log_success("Agent definitions match claude.md")

    # Step 6: Validate skills
    print("\n6. Validating skills inventory...")
    claude_skills = extract_skill_names(sections)
    skill_errors = validate_skill_directories(claude_skills, project_root)

    if skill_errors:
        for error in skill_errors:
            log_warning(error)
    else:
        log_success("Skills inventory matches claude.md")

    # Step 7: Validate interface hierarchy
    print("\n7. Validating interface hierarchy...")
    hierarchy_errors = validate_interface_hierarchy(project_root)

    if hierarchy_errors:
        for error in hierarchy_errors:
            log_error(error)
    else:
        log_success("Interface hierarchy complete")

    # Step 8: Generate report
    print("\n8. Generating validation report...")

    validation_results = {
        "Section Structure": structure_errors,
        "MCP Servers": mcp_errors,
        "Agent Definitions": agent_errors,
        "Skills Inventory": skill_errors,
        "Interface Hierarchy": hierarchy_errors,
    }

    generate_report(project_root, validation_results, model_version)

    # Summary
    total_errors = sum(len(errors) for errors in validation_results.values())

    print("\n" + "=" * 50)
    print("Validation Summary")
    print("=" * 50)
    print(f"Total Errors: {total_errors}")
    print()

    if total_errors == 0:
        log_success("Configuration is synchronized!")
        sys.exit(0)
    else:
        log_warning(f"Configuration drift detected. {total_errors} errors found.")
        sys.exit(1)


if __name__ == "__main__":
    main()

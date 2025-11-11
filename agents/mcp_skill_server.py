#!/usr/bin/env python3
"""
MCP Skill Server for InsightPulse AI

Exposes InsightPulse skills (both native and Anthropic) via the Model Context Protocol.
This allows Claude to execute compliance checks and other skills directly.

Usage:
    python3 agents/mcp_skill_server.py

Configuration in claude_desktop_config.json:
    {
      "mcpServers": {
        "insightpulse-skills": {
          "command": "python3",
          "args": ["-m", "agents.mcp_skill_server"],
          "cwd": "/path/to/insightpulse-odoo",
          "env": {
            "PYTHONPATH": "/path/to/insightpulse-odoo"
          }
        }
      }
    }
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.skill_registry import (
    load_registry,
    get_profiles,
    get_skill,
    list_skills,
    get_profile_skills,
)


# MCP Protocol Implementation
# Based on https://spec.modelcontextprotocol.io/specification/2024-11-05/

class MCPSkillServer:
    """MCP Server for InsightPulse AI Skills"""

    def __init__(self):
        self.skills = load_registry()
        self.profiles = get_profiles()

    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Return MCP tools list (skills as tools).

        Returns:
            List of tool definitions in MCP format
        """
        tools = []

        # Add skill execution tool
        tools.append({
            "name": "run_skill",
            "description": "Execute an InsightPulse AI skill (OCA compliance, validation, etc.)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "skill_id": {
                        "type": "string",
                        "description": "Skill identifier (e.g., 'odoo.manifest.validate')",
                        "enum": list(self.skills.keys())
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to repository root",
                        "default": "."
                    },
                    "fix": {
                        "type": "boolean",
                        "description": "Auto-fix violations where possible",
                        "default": False
                    }
                },
                "required": ["skill_id"]
            }
        })

        # Add profile execution tool
        tools.append({
            "name": "run_profile",
            "description": "Execute a skill profile (multiple skills)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "profile_id": {
                        "type": "string",
                        "description": "Profile identifier (e.g., 'fast_check', 'full_compliance')",
                        "enum": list(self.profiles.keys())
                    },
                    "repo_path": {
                        "type": "string",
                        "description": "Path to repository root",
                        "default": "."
                    },
                    "fix": {
                        "type": "boolean",
                        "description": "Auto-fix violations where possible",
                        "default": False
                    }
                },
                "required": ["profile_id"]
            }
        })

        # Add skill listing tool
        tools.append({
            "name": "list_skills",
            "description": "List available InsightPulse AI skills",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tag": {
                        "type": "string",
                        "description": "Filter by tag (e.g., 'rag', 'anthropic', 'odoo')",
                        "enum": ["odoo", "oca", "compliance", "rag", "anthropic", "fast-check"]
                    }
                },
                "required": []
            }
        })

        return tools

    def get_resources(self) -> List[Dict[str, Any]]:
        """
        Return MCP resources (skill metadata).

        Returns:
            List of resource definitions in MCP format
        """
        resources = []

        # Skill registry as a resource
        resources.append({
            "uri": "skill://registry",
            "name": "Skill Registry",
            "description": "Complete registry of InsightPulse AI skills",
            "mimeType": "application/json"
        })

        # Each skill as a resource
        for skill_id, meta in self.skills.items():
            resources.append({
                "uri": f"skill://{skill_id}",
                "name": meta.get("name", skill_id),
                "description": meta.get("description", ""),
                "mimeType": "application/json"
            })

        return resources

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool (skill).

        Args:
            name: Tool name
            arguments: Tool arguments

        Returns:
            Tool result in MCP format
        """
        try:
            if name == "run_skill":
                return await self._run_skill(arguments)
            elif name == "run_profile":
                return await self._run_profile(arguments)
            elif name == "list_skills":
                return await self._list_skills(arguments)
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps({
                                "error": f"Unknown tool: {name}"
                            })
                        }
                    ],
                    "isError": True
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "error": str(e)
                        })
                    }
                ],
                "isError": True
            }

    async def _run_skill(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single skill"""
        skill_id = arguments.get("skill_id")
        repo_path = arguments.get("repo_path", ".")
        fix = arguments.get("fix", False)

        # Get skill
        run_skill_fn, meta = get_skill(skill_id)

        # Check if Anthropic skill (no Python implementation)
        if meta.get("anthropic", False):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "skill_id": skill_id,
                            "type": "anthropic",
                            "instructions": meta.get("markdown_instructions", ""),
                            "note": "This is an Anthropic prompt-based skill. Use the instructions provided."
                        })
                    }
                ]
            }

        # Execute native skill
        result = run_skill_fn({"repo_path": repo_path, "fix": fix})

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "skill_id": skill_id,
                        "result": result
                    }, indent=2)
                }
            ]
        }

    async def _run_profile(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a skill profile"""
        profile_id = arguments.get("profile_id")
        repo_path = arguments.get("repo_path", ".")
        fix = arguments.get("fix", False)

        # Get profile skills
        skill_ids = get_profile_skills(profile_id)
        results = {}

        for skill_id in skill_ids:
            try:
                run_skill_fn, meta = get_skill(skill_id)

                # Skip Anthropic skills in profile execution
                if meta.get("anthropic", False):
                    results[skill_id] = {"skipped": "Anthropic skill"}
                    continue

                result = run_skill_fn({"repo_path": repo_path, "fix": fix})
                results[skill_id] = result
            except Exception as e:
                results[skill_id] = {"error": str(e)}

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "profile_id": profile_id,
                        "results": results
                    }, indent=2)
                }
            ]
        }

    async def _list_skills(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """List available skills"""
        tag = arguments.get("tag")
        skills = list_skills(tag=tag)

        skill_list = []
        for skill_id, meta in skills.items():
            skill_list.append({
                "id": skill_id,
                "name": meta.get("name", skill_id),
                "description": meta.get("description", ""),
                "tags": meta.get("tags", []),
                "anthropic": meta.get("anthropic", False)
            })

        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({
                        "total": len(skill_list),
                        "skills": skill_list
                    }, indent=2)
                }
            ]
        }

    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource (skill metadata).

        Args:
            uri: Resource URI

        Returns:
            Resource content in MCP format
        """
        if uri == "skill://registry":
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps({
                            "skills": self.skills,
                            "profiles": self.profiles
                        }, indent=2, default=str)
                    }
                ]
            }

        # Individual skill
        skill_id = uri.replace("skill://", "")
        if skill_id in self.skills:
            meta = self.skills[skill_id]
            return {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "application/json",
                        "text": json.dumps(meta, indent=2, default=str)
                    }
                ]
            }

        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/plain",
                    "text": f"Resource not found: {uri}"
                }
            ]
        }


async def main():
    """Main MCP server loop"""
    server = MCPSkillServer()

    # MCP protocol implementation (simplified)
    # In a real implementation, this would handle the full MCP protocol
    # including initialize, tools/list, resources/list, etc.

    print("InsightPulse AI MCP Skill Server", file=sys.stderr)
    print(f"Loaded {len(server.skills)} skills", file=sys.stderr)
    print(f"Loaded {len(server.profiles)} profiles", file=sys.stderr)

    # Example: Print capabilities
    capabilities = {
        "tools": server.get_tools(),
        "resources": server.get_resources()
    }

    print(json.dumps(capabilities, indent=2))


if __name__ == "__main__":
    asyncio.run(main())

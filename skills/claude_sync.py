#!/usr/bin/env python3
"""
Claude Skill Syncer: Write Claude-generated skills directly into your registry.

Usage:
    echo '{"id": "my.skill", "description": "...", "path": "skills/my/skill", "tags": ["tag1"]}' | python3 claude_sync.py
"""
import os
import sys
import json
import yaml
from datetime import datetime
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
REGISTRY_PATH = PROJECT_ROOT / "agents" / "skills.yaml"


def validate_payload(payload):
    """Validate the input payload."""
    required_fields = ["id", "path"]
    for field in required_fields:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    # Validate skill ID format
    if not payload["id"].replace(".", "_").replace("-", "_").isidentifier():
        raise ValueError(f"Invalid skill ID format: {payload['id']}")

    return True


def load_registry():
    """Load existing skills registry."""
    if not REGISTRY_PATH.exists():
        return {}

    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in registry: {e}")


def save_registry(registry):
    """Save updated registry."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        yaml.dump(registry, f, default_flow_style=False, sort_keys=False)


def add_skill(payload):
    """Add a new skill to the registry."""
    validate_payload(payload)

    # Load existing registry
    registry = load_registry()

    # Check for duplicates
    if payload["id"] in registry:
        return {
            "status": "warning",
            "message": f"Skill `{payload['id']}` already exists in registry",
            "registry": str(REGISTRY_PATH)
        }

    # Add new skill
    registry[payload["id"]] = {
        "description": payload.get("description", ""),
        "path": payload["path"],
        "tags": payload.get("tags", []),
        "runtime": payload.get("runtime", "python"),
        "anthropic_format": payload.get("anthropic_format", True),
        "added_at": datetime.utcnow().isoformat() + "Z",
        "added_by": "claude_sync"
    }

    # Save registry
    save_registry(registry)

    return {
        "status": "ok",
        "message": f"Skill `{payload['id']}` added to skills.yaml",
        "registry": str(REGISTRY_PATH),
        "skill": registry[payload["id"]]
    }


def run(payload):
    """Main entry point."""
    try:
        return add_skill(payload)
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


if __name__ == "__main__":
    try:
        # Read from stdin
        if sys.stdin.isatty():
            print("Usage: echo '{\"id\": \"...\", \"path\": \"...\"}' | python3 claude_sync.py", file=sys.stderr)
            sys.exit(1)

        payload = json.load(sys.stdin)
        result = run(payload)

        print(json.dumps(result, indent=2))

        # Exit with appropriate code
        sys.exit(0 if result["status"] in ["ok", "warning"] else 1)

    except json.JSONDecodeError as e:
        print(json.dumps({
            "status": "error",
            "message": f"Invalid JSON input: {e}"
        }, indent=2))
        sys.exit(1)
    except Exception as e:
        print(json.dumps({
            "status": "error",
            "message": str(e)
        }, indent=2))
        sys.exit(1)

#!/usr/bin/env python3
"""
PreToolUse Hook for InsightPulse AI Claude Code
Blocks dangerous or unready tools before execution.
"""
import sys
import json


def pre_tool_use(context):
    """Optional: Block dangerous or unready tools."""
    skill_id = context.get("skill_id", "")
    tool_name = context.get("tool", "")

    # Block dangerous skills
    blocked_skills = {"agent.delete", "odoo.drop_db"}
    if skill_id in blocked_skills:
        print(f"❌ Use of skill `{skill_id}` is not allowed in this project.", file=sys.stderr)
        sys.exit(1)

    # Block dangerous operations
    if tool_name == "Bash":
        command = context.get("parameters", {}).get("command", "")
        dangerous_commands = ["rm -rf /", "dd if=", "mkfs", "> /dev/"]
        if any(dangerous in command for dangerous in dangerous_commands):
            print(f"❌ Dangerous command blocked: {command}", file=sys.stderr)
            sys.exit(1)

    return 0


if __name__ == "__main__":
    try:
        # Read context from stdin if provided
        if not sys.stdin.isatty():
            context = json.load(sys.stdin)
        else:
            context = {}

        sys.exit(pre_tool_use(context))
    except Exception as e:
        print(f"⚠️  PreToolUse hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block on hook errors

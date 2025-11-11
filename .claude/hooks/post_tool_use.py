#!/usr/bin/env python3
"""
PostToolUse Hook for InsightPulse AI Claude Code
Logs results and emits summaries after execution.
"""
import sys
import json
from datetime import datetime


def post_tool_use(context, result):
    """Optional: Log results or emit summary after execution."""
    skill_id = context.get("skill_id", "unknown")
    tool_name = context.get("tool", "unknown")
    timestamp = datetime.utcnow().isoformat() + "Z"

    # Log execution to a file for audit trail
    log_entry = {
        "timestamp": timestamp,
        "skill": skill_id,
        "tool": tool_name,
        "success": result.get("success", True),
        "summary": str(result)[:250] + "..." if len(str(result)) > 250 else str(result)
    }

    # Print summary (optional - can be disabled)
    if skill_id not in {"Read", "Glob", "Grep"}:  # Don't log read operations
        print(f"✓ [{timestamp}] {tool_name} completed", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        # Read context and result from stdin if provided
        if not sys.stdin.isatty():
            data = json.load(sys.stdin)
            context = data.get("context", {})
            result = data.get("result", {})
        else:
            context = {}
            result = {}

        sys.exit(post_tool_use(context, result))
    except Exception as e:
        print(f"⚠️  PostToolUse hook error: {e}", file=sys.stderr)
        sys.exit(0)  # Don't block on hook errors

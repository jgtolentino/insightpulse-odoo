# skills/claude_sync.py

"""
Claude Skill Syncer: Write Claude-generated skills directly into your registry.
"""
import os
import yaml
from datetime import datetime

REGISTRY_PATH = "agents/skills.yaml"

def run(payload):
    """
    Payload format expected:
    {
      "id": "my.new_skill",
      "description": "Tool description",
      "path": "skills/my/new_skill",
      "tags": ["tag1", "tag2"]
    }
    """
    if not payload.get("id") or not payload.get("path"):
        raise ValueError("Missing 'id' or 'path' in payload")

    with open(REGISTRY_PATH, "a", encoding="utf-8") as f:
        f.write(f"\n# Added via Claude sync on {datetime.utcnow().isoformat()}Z\n")
        yaml.dump({payload["id"]: {
            "description": payload.get("description", ""),
            "path": payload["path"],
            "tags": payload.get("tags", []),
            "runtime": "python",
            "anthropic_format": True
        }}, f)

    return {
        "status": "ok",
        "message": f"Skill `{payload['id']}` added to skills.yaml",
        "registry": REGISTRY_PATH
    }

if __name__ == "__main__":
    import json
    import sys
    result = run(json.loads(sys.stdin.read()))
    print(json.dumps(result, indent=2))

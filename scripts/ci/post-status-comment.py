#!/usr/bin/env python3
import os
import sys
from textwrap import dedent

# noop friendly; just prints a message to CI logs if not PR
is_pr = os.environ.get("GITHUB_EVENT_NAME") == "pull_request"
msg = "\n".join(sys.argv[1:]) or "Section 19 drift detected."

content = dedent(
    f"""
**Claude Config Sync**
{msg}

**Local fix**
```bash
make claude:sync-write
git add -A && git commit -m "chore(claude): sync Section 19"
```
"""
).strip()

if is_pr:
    try:
        import json
        import subprocess

        pr_number = os.environ.get("PR_NUMBER")
        if not pr_number:
            with open(os.environ["GITHUB_EVENT_PATH"]) as f:
                pr_number = str(json.load(f)["number"])
        subprocess.run(
            ["gh", "pr", "comment", pr_number, "--body", content], check=True
        )
    except Exception as e:
        print(f"NOTE: unable to post PR comment: {e}")
else:
    print(content)

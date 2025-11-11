# skills/ship_ready_skill.py

"""
Claude-accessible skill: Check which PRs are safe to deploy.
Requires GITHUB_TOKEN in env.
"""
import os
import requests
from datetime import datetime

def run(payload=None):
    ORG = "jgtolentino"
    REPO = "insightpulse-odoo"
    TOKEN = os.getenv("GITHUB_TOKEN")
    if not TOKEN:
        return {"error": "GITHUB_TOKEN not set"}

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    r = requests.get(
        f"https://api.github.com/repos/{ORG}/{REPO}/pulls?state=open&per_page=100",
        headers=headers
    )

    if r.status_code != 200:
        return {"error": f"GitHub API error: {r.status_code}"}

    prs = r.json()
    ship_ready = []
    for pr in prs:
        labels = [l["name"] for l in pr.get("labels", [])]
        if "can-deploy" in labels:
            ship_ready.append({
                "id": pr["number"],
                "title": pr["title"],
                "url": pr["html_url"],
                "branch": pr["head"]["ref"],
                "target": pr["base"]["ref"]
            })

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "ship_ready": ship_ready,
        "count": len(ship_ready)
    }

if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))

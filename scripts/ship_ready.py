#!/usr/bin/env python3
"""
Ship Ready Dashboard - Check which PRs are ready for production deployment
"""
import os
from datetime import datetime

import requests

ORG = "jgtolentino"
REPO = "insightpulse-odoo"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("❌ Error: GITHUB_TOKEN environment variable not set")
    print("   Set it with: export GITHUB_TOKEN=your_token_here")
    exit(1)


def get_ready_prs():
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    url = f"https://api.github.com/repos/{ORG}/{REPO}/pulls?state=open&per_page=100"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        prs = response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching PRs: {e}")
        return []

    ready_prs = []
    for pr in prs:
        labels = [label["name"] for label in pr.get("labels", [])]

        # Check if PR is marked as ready
        is_ready = (
            "status:ready" in labels
            or "can-deploy" in labels
            or "[ready]" in pr["title"].lower()
        )

        if is_ready:
            # Get CI status
            status = get_status(pr["statuses_url"], headers)

            ready_prs.append(
                {
                    "id": pr["number"],
                    "title": pr["title"],
                    "branch": pr["head"]["ref"],
                    "target": pr["base"]["ref"],
                    "status": status,
                    "url": pr["html_url"],
                    "labels": labels,
                }
            )

    return ready_prs


def get_status(status_url, headers):
    try:
        response = requests.get(status_url, headers=headers)
        response.raise_for_status()
        statuses = response.json()

        if not statuses:
            return "❓ Unknown"

        # Get the latest status
        latest = sorted(statuses, key=lambda x: x["created_at"], reverse=True)[0]

        state_map = {
            "success": "✅ Passed",
            "failure": "❌ Failed",
            "pending": "⏳ Pending",
            "error": "⚠️  Error",
        }

        return state_map.get(latest["state"], "❓ Unknown")
    except Exception:
        return "❓ Unknown"


def show():
    prs = get_ready_prs()

    print(f"\n🚀 Deployable Candidates as of {datetime.utcnow().isoformat()}Z\n")
    print("=" * 80)

    if not prs:
        print("✨ No PRs ready for deployment at this time.")
        print(
            "\n💡 Tip: Label PRs with 'status:ready' or 'can-deploy' to track them here."
        )
    else:
        print(f"Found {len(prs)} PR(s) ready for review:\n")

        for pr in prs:
            deploy_ready = (
                "🚀 Can Deploy" if "can-deploy" in pr["labels"] else "⏳ Needs Review"
            )

            print(f"#{pr['id']}: {pr['title']}")
            print(f"   Branch: {pr['branch']} → {pr['target']}")
            print(f"   Status: {pr['status']}")
            print(f"   Deploy: {deploy_ready}")
            print(f"   URL:    {pr['url']}")
            print()

    print("=" * 80)


if __name__ == "__main__":
    show()

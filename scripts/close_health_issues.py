#!/usr/bin/env python3
"""
Close all open health check issues using GitHub API
"""

import os
import sys

try:
    import requests
except ImportError:
    print("Installing requests...")
    os.system("pip install -q requests")
    import requests

REPO_OWNER = "jgtolentino"
REPO_NAME = "insightpulse-odoo"


def get_github_token():
    """Get GitHub token from environment or gh CLI"""
    # Try environment variable first
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        return token

    # Try gh CLI
    try:
        import subprocess

        result = subprocess.run(
            ["gh", "auth", "token"], capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except:
        pass

    return None


def close_health_issues(token):
    """Close all open health check issues"""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Get all open health check issues
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues"
    params = {"state": "open", "labels": "health-check", "per_page": 100}

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    issues = response.json()

    if not issues:
        print("✅ No health check issues to close")
        return 0

    print(f"🧹 Closing {len(issues)} health check issue(s)...")

    comment_body = """✅ **Resolved: Health Monitor Updated**

This issue is being closed because:

1. The health monitor has been updated to prevent duplicate issue creation
2. It now automatically closes issues when health is restored
3. Multiple duplicate issues were created during a transient WAF/CDN issue

The root cause was a Cloudflare WAF configuration that temporarily blocked health check requests. The health monitor now handles this gracefully.

**Changes made:**
- Health monitor now checks for existing open issues before creating new ones
- Auto-closes issues when health is restored (fixed dependency bug)
- Added better diagnostics to distinguish between WAF and origin issues

If you continue to see health issues, they will be tracked in a single consolidated issue going forward.

*Auto-closed by health monitor cleanup script*"""

    count = 0
    for issue in issues:
        issue_num = issue["number"]
        print(f"Closing issue #{issue_num}...")

        # Add comment
        comment_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_num}/comments"
        requests.post(comment_url, headers=headers, json={"body": comment_body})

        # Close issue
        issue_url = (
            f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/issues/{issue_num}"
        )
        requests.patch(issue_url, headers=headers, json={"state": "closed"})

        count += 1
        print(f"✓ Closed issue #{issue_num}")

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"✅ Closed {count} health check issue(s)")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    return count


if __name__ == "__main__":
    token = get_github_token()

    if not token:
        print("❌ Error: No GitHub token found")
        print(
            "\nPlease set GITHUB_TOKEN environment variable or authenticate with gh CLI:"
        )
        print("  export GITHUB_TOKEN=your_token_here")
        print("  # or")
        print("  gh auth login")
        sys.exit(1)

    try:
        close_health_issues(token)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

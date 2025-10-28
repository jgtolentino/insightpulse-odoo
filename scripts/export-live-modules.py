#!/usr/bin/env python3
"""
Export live Odoo module inventory via JSON-RPC.

Authenticates to live Odoo instance and exports ir.module.module data
to CSV and Markdown reports for documentation and tracking.

Usage:
    export ODOO_URL="https://insightpulseai.net/odoo"
    export ODOO_DB="odoo_prod"
    export ODOO_LOGIN="admin@example.com"
    export ODOO_PASSWORD="password"
    python3 scripts/export-live-modules.py
"""
import json
import requests
import os
import sys
import csv
import datetime

# Configuration from environment
URL = os.environ.get("ODOO_URL", "").rstrip("/")
DB = os.environ.get("ODOO_DB", "")
USER = os.environ.get("ODOO_LOGIN", "")
PWD = os.environ.get("ODOO_PASSWORD", "")

if not all([URL, DB, USER, PWD]):
    print("ERROR: Missing required environment variables", file=sys.stderr)
    print("Required: ODOO_URL, ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD", file=sys.stderr)
    sys.exit(1)

# Session setup
s = requests.Session()

# 1) Authenticate
print(f"Authenticating to {URL}...", file=sys.stderr)
auth_response = s.post(
    f"{URL}/web/session/authenticate",
    json={
        "jsonrpc": "2.0",
        "params": {
            "db": DB,
            "login": USER,
            "password": PWD
        }
    }
)

try:
    result = auth_response.json()
    uid = result.get("result", {}).get("uid")
    if not uid:
        print(f"ERROR: Authentication failed - {result}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Authenticated as UID {uid}", file=sys.stderr)
except Exception as e:
    print(f"ERROR: Authentication request failed - {e}", file=sys.stderr)
    sys.exit(1)

# 2) Fetch all modules
print("Fetching module inventory...", file=sys.stderr)
payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "model": "ir.module.module",
        "method": "search_read",
        "args": [[("state", "!=", False)]],
        "kwargs": {
            "fields": [
                "name",
                "shortdesc",
                "author",
                "website",
                "latest_version",
                "state",
                "category_id",
                "summary"
            ],
            "limit": 5000
        }
    }
}

try:
    mod_response = s.post(f"{URL}/web/dataset/call_kw", json=payload)
    mods = mod_response.json().get("result", [])
    print(f"✅ Retrieved {len(mods)} modules", file=sys.stderr)
except Exception as e:
    print(f"ERROR: Module fetch failed - {e}", file=sys.stderr)
    sys.exit(1)

# Generate timestamp for filenames
ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%MZ")
csv_path = f"reports/live_modules_{ts}.csv"
md_path = f"reports/live_modules_{ts}.md"

# Ensure reports directory exists
os.makedirs("reports", exist_ok=True)

# 3) Write CSV export
print(f"Writing CSV to {csv_path}...", file=sys.stderr)
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow([
        "technical_name",
        "name",
        "author",
        "website",
        "latest_version",
        "state",
        "category"
    ])
    for m in mods:
        w.writerow([
            m.get("name"),
            m.get("shortdesc"),
            m.get("author"),
            m.get("website"),
            m.get("latest_version"),
            m.get("state"),
            (m.get("category_id") or [None, ""])[1]
        ])

# 4) Write Markdown summary
installed = [m for m in mods if m.get("state") == "installed"]
cats = {}
for m in installed:
    cat = (m.get("category_id") or [None, "Uncategorized"])[1]
    cats[cat] = cats.get(cat, 0) + 1

print(f"Writing Markdown summary to {md_path}...", file=sys.stderr)
lines = [
    f"# Live Module Inventory @ {ts}\n",
    f"**Source**: {URL}",
    f"**Database**: {DB}",
    f"**Timestamp**: {datetime.datetime.utcnow().isoformat()}Z\n",
    "## Summary\n",
    f"- **Total Modules**: {len(mods)}",
    f"- **Installed**: {len(installed)}",
    f"- **Uninstalled**: {len([m for m in mods if m.get('state') == 'uninstalled'])}",
    f"- **To Upgrade**: {len([m for m in mods if m.get('state') == 'to upgrade'])}",
    f"- **To Install**: {len([m for m in mods if m.get('state') == 'to install'])}",
    f"- **To Remove**: {len([m for m in mods if m.get('state') == 'to remove'])}",
    f"- **Uninstallable**: {len([m for m in mods if m.get('state') == 'uninstallable'])}\n",
    "## Installed Modules by Category\n"
]

for k in sorted(cats, key=cats.get, reverse=True):
    lines.append(f"- **{k}**: {cats[k]} modules")

lines.extend([
    "\n## Top 10 Most Recently Updated (Installed)\n"
])

# Sort by latest_version (proxy for recent activity)
recent = sorted(
    [m for m in installed if m.get("latest_version")],
    key=lambda x: x.get("latest_version", ""),
    reverse=True
)[:10]

for m in recent:
    lines.append(
        f"- **{m.get('shortdesc')}** (`{m.get('name')}`) - v{m.get('latest_version')}"
    )

open(md_path, "w", encoding="utf-8").write("\n".join(lines))

# Output paths for shell scripts to capture
print(csv_path)
print(md_path)

print(f"\n✅ Export complete!", file=sys.stderr)
print(f"   CSV: {csv_path}", file=sys.stderr)
print(f"   Markdown: {md_path}", file=sys.stderr)

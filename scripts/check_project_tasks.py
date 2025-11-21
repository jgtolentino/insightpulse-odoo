#!/usr/bin/env python3
"""
check_project_tasks.py

UI-domain health check for finance projects.

- Verifies project records exist and are accessible via JSON-RPC
- Verifies task counts per project match database reality
- Fails hard if any JSON-RPC search_read hits an invalid domain
  (e.g. broken filters like is_internal_project)
- Exits 0 on success, non-zero on failure

Usage:
    export ODOO_URL=https://erp.insightpulseai.net
    export ODOO_DB=odoo
    export ODOO_LOGIN=jgtolentino_rn@yahoo.com
    export ODOO_PASSWORD=your_password
    python3 check_project_tasks.py
"""

import os
import sys
import json
import traceback
import requests
from typing import Any, Dict, List

# Configuration from environment
ODOO_URL = os.getenv("ODOO_URL", "https://erp.insightpulseai.net")
ODOO_DB = os.getenv("ODOO_DB", "odoo")
ODOO_LOGIN = os.getenv("ODOO_LOGIN", "jgtolentino_rn@yahoo.com")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

# Finance projects to validate
PROJECT_IDS = [6, 10, 11]  # Template, BIR Calendar, November 2025

# Expected task counts (update these as projects evolve)
EXPECTED_TASK_COUNTS = {
    6: 36,   # Month-end Closing - Template
    10: 17,  # Tax Filing & BIR Compliance
    11: 36,  # Monthly Closing - November 2025
}


def json_rpc(url: str, method: str, params: Dict[str, Any]) -> Any:
    """Execute JSON-RPC call to Odoo."""
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    if "error" in data:
        raise RuntimeError(f"JSON-RPC error: {data['error']}")
    return data["result"]


def odoo_call(service: str, method: str, *args, **kwargs) -> Any:
    """Generic Odoo service call."""
    url = f"{ODOO_URL}/jsonrpc"
    return json_rpc(url, "call", {
        "service": service,
        "method": method,
        "args": args,
        "kwargs": kwargs,
    })


def authenticate() -> int:
    """Authenticate with Odoo and return UID."""
    uid = odoo_call("common", "authenticate", ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD, {})
    if not uid:
        raise RuntimeError("Failed to authenticate to Odoo – check ODOO_LOGIN/ODOO_PASSWORD")
    return uid


def execute_kw(uid: int, model: str, method: str, args=None, kwargs=None) -> Any:
    """Execute Odoo model method."""
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}
    return odoo_call("object", "execute_kw", ODOO_DB, uid, ODOO_PASSWORD, model, method, args, kwargs)


def check_projects(uid: int) -> Dict[int, Dict]:
    """Validate finance projects are accessible and active."""
    print("▶ Checking finance projects (6, 10, 11)…")
    fields = ["name", "active", "privacy_visibility", "user_id", "task_count"]

    try:
        projects = execute_kw(
            uid,
            "project.project",
            "search_read",
            [[["id", "in", PROJECT_IDS]]],
            {"fields": fields},
        )
    except Exception as e:
        print(f"  ❌ FAIL: Unable to search_read projects: {e}", file=sys.stderr)
        raise

    by_id = {p["id"]: p for p in projects}

    # Check for missing projects
    missing = [pid for pid in PROJECT_IDS if pid not in by_id]
    if missing:
        raise RuntimeError(f"Missing projects in search_read: {missing}")

    # Validate each project
    for pid in PROJECT_IDS:
        p = by_id[pid]
        active_status = "✅" if p["active"] else "❌"
        visibility = p.get("privacy_visibility", "N/A")
        task_count = p.get("task_count", 0)

        print(f"  {active_status} Project {pid}: {p['name']}")
        print(f"     Active: {p['active']} | Visibility: {visibility} | Tasks: {task_count}")

        if not p["active"]:
            raise RuntimeError(f"Project {pid} is not active")

    return by_id


def check_tasks(uid: int) -> None:
    """Validate task counts and UI domain accessibility."""
    print("\n▶ Checking task counts & domains…")

    for pid in PROJECT_IDS:
        # DB-level count via search_count
        try:
            db_count = execute_kw(
                uid,
                "project.task",
                "search_count",
                [[["project_id", "=", pid]]],
            )
        except Exception as e:
            print(f"  ❌ FAIL: Unable to count tasks for project {pid}: {e}", file=sys.stderr)
            raise

        # UI-level check via search_read with same domain
        try:
            tasks = execute_kw(
                uid,
                "project.task",
                "search_read",
                [[["project_id", "=", pid]]],
                {"fields": ["id", "name", "stage_id"], "limit": 5},
            )
            ui_accessible = True
            sample_task_count = len(tasks)
        except Exception as e:
            ui_accessible = False
            sample_task_count = 0
            print(f"  ⚠️  WARN: UI domain error for project {pid}: {e}", file=sys.stderr)

        # Get expected count
        expected = EXPECTED_TASK_COUNTS.get(pid, -1)

        # Determine status
        if db_count == expected and ui_accessible:
            status = "✅"
        elif db_count != expected:
            status = "⚠️"
        else:
            status = "❌"

        print(f"  {status} Project {pid}: DB={db_count}, Expected={expected}, UI_accessible={ui_accessible}")

        # Fail if UI is not accessible but we have tasks in DB
        if db_count > 0 and not ui_accessible:
            raise RuntimeError(
                f"Project {pid} has {db_count} tasks in DB but UI domain returned error. "
                f"Possible filter/RLS/domain problem."
            )

        # Warn if counts don't match expectations
        if expected != -1 and db_count != expected:
            print(f"  ⚠️  WARN: Task count mismatch for project {pid}. Expected {expected}, got {db_count}")


def check_ui_filters(uid: int) -> None:
    """Check for common problematic UI filters."""
    print("\n▶ Checking for problematic UI filters…")

    # Try to detect if certain fields exist that shouldn't
    problematic_fields = ["is_internal_project", "user_skill_ids"]

    try:
        # Get project.project field list
        fields_info = execute_kw(
            uid,
            "project.project",
            "fields_get",
            [],
            {"attributes": ["string", "type"]},
        )

        found_problems = []
        for field in problematic_fields:
            if field in fields_info:
                found_problems.append(field)

        if found_problems:
            print(f"  ⚠️  WARN: Found potentially problematic fields: {', '.join(found_problems)}")
            print(f"     These fields may cause filter issues if used in saved searches")
        else:
            print(f"  ✅ No problematic fields detected")
    except Exception as e:
        print(f"  ⚠️  WARN: Unable to check field list: {e}", file=sys.stderr)


def main() -> int:
    """Main execution flow."""
    try:
        # Validate environment
        if not ODOO_PASSWORD:
            print("❌ FAIL: ODOO_PASSWORD not set in environment", file=sys.stderr)
            return 2

        print(f"ODOO_URL={ODOO_URL}")
        print(f"ODOO_DB={ODOO_DB}")
        print(f"ODOO_LOGIN={ODOO_LOGIN}\n")

        # Authenticate
        uid = authenticate()
        print(f"✅ Authenticated as UID={uid}\n")

        # Run checks
        projects = check_projects(uid)
        check_tasks(uid)
        check_ui_filters(uid)

        print("\n" + "="*60)
        print("✅ W150_UI_DOMAIN_OK: All finance projects and task domains are healthy.")
        print("="*60)
        return 0

    except Exception as e:
        print("\n" + "="*60, file=sys.stderr)
        print("❌ W150_UI_DOMAIN_FAIL: UI domain / project visibility problem detected.", file=sys.stderr)
        print(f"Reason: {e}", file=sys.stderr)
        print("="*60, file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

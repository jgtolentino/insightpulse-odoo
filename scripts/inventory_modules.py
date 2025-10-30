#!/usr/bin/env python3
"""
Odoo Module Inventory Generator

Scans addon directories and generates comprehensive module inventory
in CSV, JSON, and Markdown formats.

Usage:
    python3 scripts/inventory_modules.py [--with-prod-status]

Options:
    --with-prod-status    Query production Odoo for installation status via XML-RPC
"""
import os
import json
import csv
import ast
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDON_ROOTS = [
    ROOT / "addons" / "custom",
    ROOT / "addons" / "insightpulse",
    ROOT / "addons" / "oca",
]

def load_manifest(p):
    """Load and parse __manifest__.py file"""
    try:
        return ast.literal_eval(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Warning: Failed to parse {p}: {e}", file=sys.stderr)
        return {}

def category_for(path: Path):
    """Determine module category from path"""
    parts = str(path)
    if "/custom/" in parts:
        return "ipai_custom"
    if "/insightpulse/" in parts:
        return "insightpulse"
    if "/oca/" in parts:
        return "oca"
    return "unknown"

def scan():
    """Scan all addon directories and extract module metadata"""
    out = []
    for base in ADDON_ROOTS:
        if not base.exists():
            print(f"Warning: {base} does not exist, skipping", file=sys.stderr)
            continue

        for man in base.rglob("__manifest__.py"):
            mod_dir = man.parent
            mod_name = mod_dir.name
            m = load_manifest(man)

            out.append({
                "category": category_for(mod_dir),
                "module_name": mod_name,
                "display_name": m.get("name", mod_name),
                "version": m.get("version", ""),
                "author": m.get("author", ""),
                "license": m.get("license", ""),
                "depends": ",".join(m.get("depends", [])),
                "path": str(mod_dir.relative_to(ROOT)),
                "installed": "",   # filled in by robust path
                "state": "",       # filled in by robust path
            })

    return out

def fetch_installed_states(url, db, user, password):
    """Query Odoo via XML-RPC for module installation states"""
    import xmlrpc.client

    try:
        print(f"Connecting to {url}...", file=sys.stderr)
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
        uid = common.authenticate(db, user, password, {})

        if not uid:
            print("Authentication failed", file=sys.stderr)
            return {}

        print(f"Authenticated as user ID: {uid}", file=sys.stderr)

        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        recs = models.execute_kw(
            db, uid, password,
            'ir.module.module',
            'search_read',
            [[['name', '!=', False]]],
            {'fields': ['name', 'state']}
        )

        states = {r['name']: r['state'] for r in recs}
        print(f"Retrieved {len(states)} module states from production", file=sys.stderr)
        return states

    except Exception as e:
        print(f"Error querying production Odoo: {e}", file=sys.stderr)
        return {}

def emit_csv(rows, fpath):
    """Generate CSV inventory file"""
    with open(fpath, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def emit_json(rows, fpath):
    """Generate JSON inventory file"""
    from datetime import datetime

    # Calculate summary statistics
    summary = {
        "total": len(rows),
        "by_category": {},
        "by_status": {},
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

    for row in rows:
        cat = row["category"]
        summary["by_category"][cat] = summary["by_category"].get(cat, 0) + 1

        if row["installed"]:
            status = "installed" if row["installed"] == "true" else "uninstalled"
            summary["by_status"][status] = summary["by_status"].get(status, 0) + 1

    data = {
        "summary": summary,
        "modules": rows
    }

    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def emit_md(rows, fpath):
    """Generate Markdown inventory file"""
    from datetime import datetime

    rows_sorted = sorted(rows, key=lambda r: (r["category"], r["module_name"]))

    # Calculate summary
    total = len(rows)
    by_cat = {}
    installed_count = 0

    for r in rows:
        by_cat[r["category"]] = by_cat.get(r["category"], 0) + 1
        if r["installed"] == "true":
            installed_count += 1

    with open(fpath, "w", encoding="utf-8") as f:
        f.write("# Odoo Module Inventory\n\n")
        f.write(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n")

        f.write("## Summary\n\n")
        f.write(f"- **Total modules**: {total}\n")
        for cat, count in sorted(by_cat.items()):
            f.write(f"- **{cat}**: {count}\n")
        if installed_count > 0:
            f.write(f"- **Installed**: {installed_count}\n")
            f.write(f"- **Uninstalled**: {total - installed_count}\n")
        f.write("\n")

        # Module tables by category
        cats = ["ipai_custom", "insightpulse", "oca", "unknown"]
        for c in cats:
            subset = [r for r in rows_sorted if r["category"] == c]
            if not subset:
                continue

            f.write(f"## {c.replace('_', ' ').title()}\n\n")
            f.write("| Module | Display Name | Version | Status | State | Dependencies |\n")
            f.write("|--------|--------------|---------|--------|-------|-------------|\n")

            for r in subset:
                status = "✅" if r["installed"] == "true" else "⬜" if r["installed"] == "false" else "❓"
                deps = r["depends"][:50] + "..." if len(r["depends"]) > 50 else r["depends"]

                f.write(
                    f"| {r['module_name']} | {r['display_name']} | {r['version']} | "
                    f"{status} | {r['state']} | {deps} |\n"
                )
            f.write("\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate Odoo module inventory")
    parser.add_argument("--with-prod-status", action="store_true",
                        help="Query production Odoo for installation status")
    parser.add_argument("--url", default="http://localhost:8069",
                        help="Odoo URL (default: http://localhost:8069)")
    parser.add_argument("--db", default="odoo",
                        help="Database name (default: odoo)")
    parser.add_argument("--user", default="admin",
                        help="Admin username (default: admin)")
    parser.add_argument("--password", default="admin",
                        help="Admin password (default: admin)")

    args = parser.parse_args()

    # Scan file system for modules
    print("Scanning addon directories...", file=sys.stderr)
    rows = scan()
    print(f"Found {len(rows)} modules", file=sys.stderr)

    # Optionally fetch production status
    if args.with_prod_status:
        states = fetch_installed_states(args.url, args.db, args.user, args.password)
        for r in rows:
            st = states.get(r["module_name"])
            if st:
                r["installed"] = str(st == "installed").lower()
                r["state"] = st

    # Generate output files
    outdir = ROOT / "docs"
    outdir.mkdir(parents=True, exist_ok=True)

    emit_csv(rows, outdir / "modules_inventory.csv")
    print(f"✅ Generated: docs/modules_inventory.csv")

    emit_json(rows, outdir / "modules_inventory.json")
    print(f"✅ Generated: docs/modules_inventory.json")

    emit_md(rows, outdir / "MODULE_INVENTORY.md")
    print(f"✅ Generated: docs/MODULE_INVENTORY.md")

    print("\n🎉 Inventory generation complete!")

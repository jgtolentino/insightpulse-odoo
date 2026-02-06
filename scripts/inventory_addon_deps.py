#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

MANIFEST_NAMES = ("__manifest__.py", "__openerp__.py")

def read_manifest(path: Path) -> dict:
    src = path.read_text(encoding="utf-8")
    # Manifests are Python dict literals; ast.literal_eval is safe for literals.
    try:
        data = ast.literal_eval(src)
        if not isinstance(data, dict):
            raise ValueError("manifest not a dict")
        return data
    except Exception as e:
        raise RuntimeError(f"Failed to parse manifest: {path} :: {e}") from e

def find_addons(addons_roots: List[Path]) -> Dict[str, Path]:
    addons = {}
    for root in addons_roots:
        if not root.exists():
            continue
        for child in root.iterdir():
            if not child.is_dir():
                continue
            for mf in MANIFEST_NAMES:
                p = child / mf
                if p.exists():
                    addons[child.name] = child
                    break
    return addons

def get_depends(addon_dir: Path) -> List[str]:
    mf = None
    for name in MANIFEST_NAMES:
        p = addon_dir / name
        if p.exists():
            mf = p
            break
    if not mf:
        return []
    data = read_manifest(mf)
    deps = data.get("depends", []) or []
    if not isinstance(deps, list):
        return []
    return [str(x) for x in deps]

def topo(all_addons: Dict[str, Path], selected: List[str]) -> Tuple[List[str], List[str]]:
    # Return (order, missing)
    graph: Dict[str, List[str]] = {}
    missing: Set[str] = set()
    for name, path in all_addons.items():
        graph[name] = get_depends(path)

    visited: Set[str] = set()
    temp: Set[str] = set()
    order: List[str] = []

    def dfs(n: str):
        if n in visited:
            return
        if n in temp:
            raise RuntimeError(f"Cycle detected at {n}")
        temp.add(n)
        if n not in graph:
            missing.add(n)
        else:
            for d in graph[n]:
                if d not in graph:
                    # core Odoo modules (base, mail, web, etc.) may not exist as folders in vendor paths
                    # so treat as missing unless present; we report them separately.
                    missing.add(d)
                else:
                    dfs(d)
        temp.remove(n)
        visited.add(n)
        order.append(n)

    for s in selected:
        dfs(s)

    return order, sorted(missing)

def main():
    repo = Path(__file__).resolve().parents[1]

    # Addon search paths for the InsightPulse Odoo repository.
    # Adjust these paths if your repository layout differs.
    addons_roots = [
        repo / "addons",          # Custom InsightPulse addons
        repo / "custom_addons",   # Alternative custom addon location
        repo / "vendor" / "oca",  # Vendored OCA addons
        repo / "oca",             # Alternative OCA addon location
        repo / "odoo" / "addons", # Core Odoo addons (if vendored)
    ]

    selected = os.environ.get("ODOO_SELECTED_ADDONS", "").strip()
    if not selected:
        print("ERROR: set ODOO_SELECTED_ADDONS to a comma-separated list of addons to install.")
        print("Example: ODOO_SELECTED_ADDONS=ipai_base,mis_builder,dms")
        raise SystemExit(2)

    selected_list = [x.strip() for x in selected.split(",") if x.strip()]

    all_addons = find_addons(addons_roots)
    order, missing = topo(all_addons, selected_list)

    out = {
        "addons_roots": [str(p) for p in addons_roots],
        "selected": selected_list,
        "found_addons_count": len(all_addons),
        "install_order": order,
        "missing_or_core_deps": missing,
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()

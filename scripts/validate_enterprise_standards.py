#!/usr/bin/env python3
from __future__ import annotations

import sys
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "ops/ssot/system_design_map.yaml",
    "docs/architecture/SYSTEM_DESIGN_MAP_2026.md",
    "docs/runbooks/RUNBOOK_Backups_Restore_Drill.md",
    "docs/runbooks/RUNBOOK_Observability_Minimum.md",
    "docs/runbooks/RUNBOOK_Secrets_Management.md",
]

REQUIRED_DOMAINS = [
    "1_system_design_fundamentals",
    "2_service_communication",
    "3_load_balancing_traffic",
    "4_database_storage",
    "5_caching_cdn",
    "6_scalability_fault_tolerance",
    "7_observability_monitoring",
    "8_security_reliability",
    "9_real_world_patterns",
]

def fail(msg: str) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)

def main() -> None:
    # 1) Required files exist
    missing = [p for p in REQUIRED_FILES if not (ROOT / p).exists()]
    if missing:
        fail("Missing required SSOT/runbook files:\n- " + "\n- ".join(missing))

    # 2) SSOT YAML shape validation
    ssot_path = ROOT / "ops/ssot/system_design_map.yaml"
    try:
        data = yaml.safe_load(ssot_path.read_text(encoding="utf-8"))
    except Exception as e:
        fail(f"Cannot parse {ssot_path}: {e}")

    if not isinstance(data, dict):
        fail("SSOT YAML is not a mapping/object.")

    if data.get("version") != 1:
        fail("SSOT YAML version must be 1.")

    domains = data.get("domains")
    if not isinstance(domains, dict):
        fail("SSOT YAML must contain 'domains' mapping.")

    for d in REQUIRED_DOMAINS:
        if d not in domains:
            fail(f"SSOT YAML missing domain: {d}")

        domain_obj = domains[d]
        if not isinstance(domain_obj, dict):
            fail(f"Domain '{d}' must be a mapping/object.")
        if "stack" not in domain_obj or "owners" not in domain_obj:
            fail(f"Domain '{d}' must include 'stack' and 'owners' keys.")

        if not isinstance(domain_obj["stack"], list) or len(domain_obj["stack"]) == 0:
            fail(f"Domain '{d}.stack' must be a non-empty list.")
        if not isinstance(domain_obj["owners"], list) or len(domain_obj["owners"]) == 0:
            fail(f"Domain '{d}.owners' must be a non-empty list.")

    # 3) Minimal enterprise guardrails (file-based, deterministic)
    # NOTE: We keep this conservative to avoid false positives across repos.
    # Add stricter checks later (nginx conf presence, docker-compose, health endpoints) once paths are standardized.

    print("ok: enterprise standards baseline passed")

if __name__ == "__main__":
    main()

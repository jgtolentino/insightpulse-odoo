#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
import yaml
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

def load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}

def main():
    matrix_path = ROOT / "parity" / "ee_parity_matrix.yaml"
    if not matrix_path.exists():
        print(f"ERROR: missing {matrix_path}", file=sys.stderr)
        sys.exit(2)

    m = load_yaml(matrix_path)
    features = m.get("ee_parity", m)
    if not isinstance(features, dict):
        print("ERROR: ee_parity_matrix.yaml has unexpected shape", file=sys.stderr)
        sys.exit(2)

    by_status = Counter()
    by_level = Counter()
    deltas = []
    blockers = []

    for key, spec in features.items():
        if not isinstance(spec, dict):
            continue
        status = str(spec.get("status", spec.get("parity_status", "unknown"))).lower()
        level = str(spec.get("parity_level", spec.get("level", "unknown"))).lower()

        by_status[status] += 1
        by_level[level] += 1

        if status in {"missing", "not_started", "todo", "blocked"} or level in {"none", "partial", "external_service", "custom_adapter"}:
            deltas.append((key, status, level, spec.get("ee_module"), spec.get("oca_equivalent")))

        if status == "blocked" or spec.get("blocker"):
            blockers.append((key, spec.get("blocker")))

    print("=== EE Parity Delta Summary ===")
    print("By status:")
    for k, v in by_status.most_common():
        print(f"  - {k}: {v}")

    print("\nBy parity_level:")
    for k, v in by_level.most_common():
        print(f"  - {k}: {v}")

    print("\n=== Remaining Delta (Top 50) ===")
    for i, (k, status, level, ee_mod, oca_eq) in enumerate(deltas[:50], 1):
        print(f"{i:02d}. {k} | status={status} | level={level} | ee={ee_mod} | oca={oca_eq}")

    if blockers:
        print("\n=== Blockers ===")
        for k, b in blockers:
            print(f"- {k}: {b}")

    sys.exit(0)

if __name__ == "__main__":
    main()

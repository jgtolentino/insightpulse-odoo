#!/usr/bin/env python3
"""
Spec drift detection: fail CI if tracked spec differs from generated.
Detects breaking changes in API contracts.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any


def load_spec(spec_path: Path) -> Dict[str, Any]:
    """Load OpenAPI spec from JSON file."""
    if not spec_path.exists():
        return {}
    return json.loads(spec_path.read_text())


def compare_specs(tracked: Dict[str, Any], generated: Dict[str, Any]) -> bool:
    """
    Compare tracked vs generated spec for breaking changes.
    Returns True if drift detected, False if specs match.
    """
    if not tracked:
        print("📝 No tracked spec found - first run, no drift")
        return False

    drift_detected = False

    # Compare paths
    tracked_paths = set(tracked.get("paths", {}).keys())
    generated_paths = set(generated.get("paths", {}).keys())

    removed_paths = tracked_paths - generated_paths
    added_paths = generated_paths - tracked_paths

    if removed_paths:
        print(f"❌ DRIFT: Removed endpoints: {removed_paths}")
        drift_detected = True

    if added_paths:
        print(f"✅ Added endpoints: {added_paths}")

    # Compare schemas for changed paths
    for path in tracked_paths & generated_paths:
        tracked_methods = set(tracked["paths"][path].keys())
        generated_methods = set(generated["paths"][path].keys())

        removed_methods = tracked_methods - generated_methods
        if removed_methods:
            print(f"❌ DRIFT: {path} removed methods: {removed_methods}")
            drift_detected = True

        # Compare operation schemas
        for method in tracked_methods & generated_methods:
            tracked_op = tracked["paths"][path][method]
            generated_op = generated["paths"][path][method]

            # Check request schema changes
            tracked_req = tracked_op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})
            generated_req = generated_op.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})

            if tracked_req != generated_req:
                print(f"❌ DRIFT: {path} {method} request schema changed")
                drift_detected = True

            # Check response schema changes
            tracked_resp = tracked_op.get("responses", {}).get("200", {}).get("content", {}).get("application/json", {}).get("schema", {})
            generated_resp = generated_op.get("responses", {}).get("200", {}).get("content", {}).get("application/json", {}).get("schema", {})

            if tracked_resp != generated_resp:
                print(f"❌ DRIFT: {path} {method} response schema changed")
                drift_detected = True

            # Check role scope changes
            tracked_scopes = set(tracked_op.get("x-role-scopes", []))
            generated_scopes = set(generated_op.get("x-role-scopes", []))

            if tracked_scopes != generated_scopes:
                print(f"⚠️  WARNING: {path} {method} role scopes changed: {tracked_scopes} → {generated_scopes}")

    return drift_detected


def main():
    """Main execution: compare tracked vs generated spec."""
    print("🔍 Checking for spec drift...\n")

    spec_dir = Path("spec")
    tracked_spec_path = spec_dir / "openapi.json"
    generated_spec_path = spec_dir / "openapi.json"

    # Load specs
    tracked_spec = load_spec(tracked_spec_path)
    generated_spec = load_spec(generated_spec_path)

    # Compare
    drift_detected = compare_specs(tracked_spec, generated_spec)

    if drift_detected:
        print("\n❌ SPEC DRIFT DETECTED - Breaking changes require version bump")
        print("   Fix: Bump major/minor version in affected __manifest__.py files")
        sys.exit(1)
    else:
        print("\n✅ No spec drift detected - specs match")
        sys.exit(0)


if __name__ == "__main__":
    main()

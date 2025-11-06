#!/usr/bin/env python3
"""
Validate spec contracts: x-atomic, x-idempotency, x-role-scopes metadata.
Ensures all endpoints have proper contract metadata defined.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List


def load_openapi_spec() -> Dict[str, Any]:
    """Load generated OpenAPI spec."""
    spec_path = Path("spec/openapi.json")
    if not spec_path.exists():
        print("❌ No OpenAPI spec found at spec/openapi.json")
        sys.exit(1)
    return json.loads(spec_path.read_text())


def validate_endpoint(path: str, method: str, operation: Dict[str, Any]) -> List[str]:
    """
    Validate endpoint contract metadata.
    Returns list of validation errors.
    """
    errors = []

    # Check x-atomic metadata
    if "x-atomic" not in operation:
        errors.append(f"{path} {method}: missing x-atomic metadata")
    elif not isinstance(operation["x-atomic"], bool):
        errors.append(f"{path} {method}: x-atomic must be boolean")

    # Check x-idempotency metadata
    valid_idempotency = ["none", "key-based", "natural"]
    if "x-idempotency" not in operation:
        errors.append(f"{path} {method}: missing x-idempotency metadata")
    elif operation["x-idempotency"] not in valid_idempotency:
        errors.append(f"{path} {method}: x-idempotency must be one of {valid_idempotency}")

    # Check x-role-scopes metadata
    if "x-role-scopes" not in operation:
        errors.append(f"{path} {method}: missing x-role-scopes metadata")
    elif not isinstance(operation["x-role-scopes"], list):
        errors.append(f"{path} {method}: x-role-scopes must be a list")

    # Validate atomic + non-idempotent endpoints
    if operation.get("x-atomic") and operation.get("x-idempotency") == "none":
        errors.append(f"{path} {method}: atomic operations should be idempotent")

    # Validate role scopes format
    if "x-role-scopes" in operation:
        for scope in operation["x-role-scopes"]:
            if not isinstance(scope, str) or ":" not in scope:
                errors.append(f"{path} {method}: invalid role scope format '{scope}' (expected 'role:permission')")

    return errors


def main():
    """Main execution: validate all endpoint contracts."""
    print("🔒 Validating spec contracts...\n")

    spec = load_openapi_spec()
    all_errors = []

    # Validate each endpoint
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            errors = validate_endpoint(path, method, operation)
            all_errors.extend(errors)

            if not errors:
                print(f"✅ {path} {method}")

    # Report results
    if all_errors:
        print(f"\n❌ Contract validation failed with {len(all_errors)} errors:\n")
        for error in all_errors:
            print(f"   - {error}")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(spec.get('paths', {}))} endpoints have valid contracts")
        sys.exit(0)


if __name__ == "__main__":
    main()

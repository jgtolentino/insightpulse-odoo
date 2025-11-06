#!/usr/bin/env python3
"""
Generate OpenAPI 3.1 spec from Pydantic SPEC_REGISTRY.
Reads addons/**/models/spec_registry.py and writes spec/*.json.
"""
import json
import sys
from pathlib import Path
from typing import Any, Dict

def load_spec_registry() -> Dict[str, Any]:
    """
    Load SPEC_REGISTRY from all Odoo addons.
    Expects: addons/<module>/models/spec_registry.py with SPEC_REGISTRY dict.
    """
    registry = {}
    addons_dir = Path("addons")

    if not addons_dir.exists():
        print("⚠️  No addons/ directory found", file=sys.stderr)
        return registry

    for spec_file in addons_dir.rglob("*/models/spec_registry.py"):
        module_name = spec_file.parent.parent.name
        print(f"📦 Loading spec from {module_name}")

        # Execute spec_registry.py to extract SPEC_REGISTRY
        namespace = {}
        try:
            exec(spec_file.read_text(), namespace)
            if "SPEC_REGISTRY" in namespace:
                registry[module_name] = namespace["SPEC_REGISTRY"]
                print(f"   ✅ Loaded {len(namespace['SPEC_REGISTRY'])} endpoints")
        except Exception as e:
            print(f"   ❌ Failed to load: {e}", file=sys.stderr)

    return registry


def pydantic_to_openapi(spec_registry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Pydantic SPEC_REGISTRY to OpenAPI 3.1 spec.
    """
    openapi_spec = {
        "openapi": "3.1.0",
        "info": {
            "title": "InsightPulse Odoo API",
            "version": "1.0.0",
            "description": "Auto-generated from Pydantic models"
        },
        "paths": {},
        "components": {
            "schemas": {}
        }
    }

    for module_name, endpoints in spec_registry.items():
        for endpoint_name, endpoint_spec in endpoints.items():
            # Extract path, method, and schema from Pydantic spec
            path = endpoint_spec.get("path", f"/{module_name}/{endpoint_name}")
            method = endpoint_spec.get("method", "post").lower()

            # Initialize path if not exists
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}

            # Build operation spec
            operation = {
                "operationId": endpoint_name,
                "summary": endpoint_spec.get("summary", f"{endpoint_name} operation"),
                "description": endpoint_spec.get("description", ""),
                "tags": [module_name],
                "x-atomic": endpoint_spec.get("x-atomic", False),
                "x-idempotency": endpoint_spec.get("x-idempotency", "none"),
                "x-role-scopes": endpoint_spec.get("x-role-scopes", [])
            }

            # Add request body schema
            if "request_schema" in endpoint_spec:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": endpoint_spec["request_schema"]
                        }
                    }
                }

                # Add schema to components
                schema_name = f"{endpoint_name}Request"
                openapi_spec["components"]["schemas"][schema_name] = endpoint_spec["request_schema"]

            # Add response schema
            if "response_schema" in endpoint_spec:
                operation["responses"] = {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": endpoint_spec["response_schema"]
                            }
                        }
                    }
                }

                # Add schema to components
                schema_name = f"{endpoint_name}Response"
                openapi_spec["components"]["schemas"][schema_name] = endpoint_spec["response_schema"]

            # Add security if role-scopes defined
            if operation["x-role-scopes"]:
                operation["security"] = [{"bearerAuth": operation["x-role-scopes"]}]

            openapi_spec["paths"][path][method] = operation

    return openapi_spec


def main():
    """Main execution: load specs → convert → write JSON."""
    print("🔧 Generating OpenAPI spec from Pydantic SPEC_REGISTRY...\n")

    # Load spec registry
    spec_registry = load_spec_registry()

    if not spec_registry:
        print("⚠️  No SPEC_REGISTRY found - generating minimal spec", file=sys.stderr)
        spec_registry = {"placeholder": {"health": {"path": "/health", "method": "get"}}}

    # Convert to OpenAPI
    openapi_spec = pydantic_to_openapi(spec_registry)

    # Write to spec/ directory
    spec_dir = Path("spec")
    spec_dir.mkdir(exist_ok=True)

    spec_file = spec_dir / "openapi.json"
    spec_file.write_text(json.dumps(openapi_spec, indent=2))

    print(f"\n✅ OpenAPI spec written to {spec_file}")
    print(f"   Endpoints: {len(openapi_spec['paths'])}")
    print(f"   Schemas: {len(openapi_spec['components']['schemas'])}")


if __name__ == "__main__":
    main()

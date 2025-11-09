#!/usr/bin/env python3
"""
Validate spec/platform_spec.json against spec/platform_spec.schema.json
and ensure all referenced files exist.

Exit codes:
  0 - All validations passed
  1 - Schema validation failed
  2 - Referenced files missing
  3 - JSON parsing error
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema module not installed")
    print("Install with: pip install jsonschema")
    sys.exit(3)


def load_json(file_path):
    """Load and parse JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse {file_path}: {e}")
        sys.exit(3)
    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
        sys.exit(3)


def validate_schema(spec, schema):
    """Validate spec against JSON schema"""
    try:
        jsonschema.validate(instance=spec, schema=schema)
        print("✅ Schema validation passed")
        return True
    except jsonschema.ValidationError as e:
        print(f"❌ Schema validation failed:")
        print(f"   Path: {' -> '.join(str(p) for p in e.path)}")
        print(f"   Message: {e.message}")
        return False
    except jsonschema.SchemaError as e:
        print(f"❌ Invalid schema: {e}")
        return False


def check_file_exists(file_path, description):
    """Check if a file exists and report"""
    repo_root = Path(__file__).parent.parent
    full_path = repo_root / file_path

    if full_path.exists():
        return True
    else:
        print(f"❌ Missing {description}: {file_path}")
        return False


def validate_docs_files(spec):
    """Validate that all docs files referenced in spec exist"""
    all_exist = True

    docs_sections = spec.get('docs_platform', {}).get('sections', [])

    for section in docs_sections:
        section_id = section.get('id', 'unknown')

        # Check pages
        for page in section.get('pages', []):
            if not check_file_exists(page, f"docs page ({section_id})"):
                all_exist = False

        # Check documents
        for doc in section.get('documents', []):
            if not check_file_exists(doc, f"spec-kit document ({section_id})"):
                all_exist = False

        # Check index
        if 'index' in section:
            if not check_file_exists(section['index'], f"index ({section_id})"):
                all_exist = False

    # Check config file
    config_file = spec.get('docs_platform', {}).get('config_file')
    if config_file:
        if not check_file_exists(config_file, "docs config"):
            all_exist = False

    # Check index files
    for index_file in spec.get('docs_platform', {}).get('index_files', []):
        if not check_file_exists(index_file, "docs index"):
            all_exist = False

    return all_exist


def validate_workflow_files(spec):
    """Validate that all CI/CD workflow files exist"""
    all_exist = True

    workflows = spec.get('ci_cd', {}).get('workflows', [])

    for workflow in workflows:
        workflow_id = workflow.get('id', 'unknown')
        workflow_file = workflow.get('file')

        if workflow_file:
            if not check_file_exists(workflow_file, f"workflow ({workflow_id})"):
                all_exist = False

    return all_exist


def main():
    """Main validation routine"""
    repo_root = Path(__file__).parent.parent
    spec_file = repo_root / 'spec' / 'platform_spec.json'
    schema_file = repo_root / 'spec' / 'platform_spec.schema.json'

    print("=" * 60)
    print("Platform Spec Validation")
    print("=" * 60)
    print()

    # Load spec and schema
    print("Loading platform_spec.json...")
    spec = load_json(spec_file)

    print("Loading platform_spec.schema.json...")
    schema = load_json(schema_file)
    print()

    # Validate schema
    print("Step 1: Validating against JSON Schema...")
    schema_valid = validate_schema(spec, schema)
    print()

    # Validate docs files
    print("Step 2: Checking docs files...")
    docs_valid = validate_docs_files(spec)
    if docs_valid:
        print("✅ All docs files exist")
    print()

    # Validate workflow files
    print("Step 3: Checking CI/CD workflow files...")
    workflows_valid = validate_workflow_files(spec)
    if workflows_valid:
        print("✅ All workflow files exist")
    print()

    # Final result
    print("=" * 60)
    if schema_valid and docs_valid and workflows_valid:
        print("✅ Spec validation complete – all guardrails passed")
        print("=" * 60)
        return 0
    else:
        print("❌ Spec validation FAILED")
        print("=" * 60)
        if not schema_valid:
            return 1
        elif not docs_valid or not workflows_valid:
            return 2
        return 1


if __name__ == '__main__':
    sys.exit(main())

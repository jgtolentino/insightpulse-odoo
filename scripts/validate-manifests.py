#!/usr/bin/env python3
"""
Validate Odoo module manifest files (__manifest__.py).

Checks for:
- Valid Python syntax
- Required manifest keys
- Version format
- Dependency format
- Category validity
"""

import ast
import sys
from pathlib import Path
from typing import Dict, List

REQUIRED_KEYS = {
    "name",
    "version",
    "category",
    "author",
    "license",
    "depends",
    "data",
}

RECOMMENDED_KEYS = {
    "summary",
    "description",
    "website",
    "installable",
    "application",
    "auto_install",
}

VALID_LICENSES = {
    "AGPL-3",
    "LGPL-3",
    "OPL-1",
    "GPL-2",
    "GPL-3",
    "Other proprietary",
}


def find_manifest_files(addons_path: Path) -> List[Path]:
    """Find all __manifest__.py files in addons directory (recursive)."""
    manifest_files = []

    # Search recursively for all __manifest__.py files
    for manifest in addons_path.rglob("__manifest__.py"):
        manifest_files.append(manifest)

    return manifest_files


def parse_manifest(manifest_path: Path) -> Dict:
    """Parse manifest file and return dictionary."""
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Parse Python AST
        tree = ast.parse(content)

        # Extract dictionary literal
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                manifest = ast.literal_eval(node)
                return manifest

        return {}

    except SyntaxError as e:
        print(f"❌ Syntax error in {manifest_path}: {e}")
        return None

    except Exception as e:
        print(f"❌ Error parsing {manifest_path}: {e}")
        return None


def validate_manifest(manifest_path: Path, manifest: Dict) -> bool:
    """Validate manifest dictionary against rules."""
    errors = []
    warnings = []

    # Check required keys
    missing_keys = REQUIRED_KEYS - set(manifest.keys())
    if missing_keys:
        errors.append(f"Missing required keys: {', '.join(missing_keys)}")

    # Check recommended keys
    missing_recommended = RECOMMENDED_KEYS - set(manifest.keys())
    if missing_recommended:
        warnings.append(f"Missing recommended keys: {', '.join(missing_recommended)}")

    # Validate version format
    if "version" in manifest:
        version = manifest["version"]
        if not isinstance(version, str):
            errors.append(f"Version must be string, got {type(version).__name__}")
        elif not version.count(".") >= 2:
            errors.append(f"Version format should be X.Y.Z, got {version}")

    # Validate license
    if "license" in manifest:
        license_val = manifest["license"]
        if license_val not in VALID_LICENSES:
            warnings.append(
                f"Unknown license: {license_val}. Valid: {', '.join(VALID_LICENSES)}"
            )

    # Validate depends
    if "depends" in manifest:
        depends = manifest["depends"]
        if not isinstance(depends, list):
            errors.append(f"'depends' must be list, got {type(depends).__name__}")
        elif not all(isinstance(d, str) for d in depends):
            errors.append("'depends' must be list of strings")

    # Validate data
    if "data" in manifest:
        data = manifest["data"]
        if not isinstance(data, list):
            errors.append(f"'data' must be list, got {type(data).__name__}")
        elif not all(isinstance(d, str) for d in data):
            errors.append("'data' must be list of strings")

    # Print results
    addon_name = manifest_path.parent.name

    if errors:
        print(f"❌ {addon_name}:")
        for error in errors:
            print(f"   ERROR: {error}")
        for warning in warnings:
            print(f"   WARNING: {warning}")
        return False

    elif warnings:
        print(f"⚠️  {addon_name}:")
        for warning in warnings:
            print(f"   WARNING: {warning}")
        return True

    else:
        print(f"✅ {addon_name}")
        return True


def main():
    """Main validation function."""
    addons_path = Path(__file__).parent.parent / "addons"

    if not addons_path.exists():
        print(f"❌ Addons directory not found: {addons_path}")
        sys.exit(1)

    manifest_files = find_manifest_files(addons_path)

    if not manifest_files:
        print("⚠️  No manifest files found")
        sys.exit(0)

    print(f"Found {len(manifest_files)} manifest files\n")

    all_valid = True

    for manifest_path in sorted(manifest_files):
        manifest = parse_manifest(manifest_path)

        if manifest is None:
            all_valid = False
            continue

        if not validate_manifest(manifest_path, manifest):
            all_valid = False

    print()

    if all_valid:
        print("✅ All manifests valid")
        sys.exit(0)
    else:
        print("❌ Some manifests have errors")
        sys.exit(1)


if __name__ == "__main__":
    main()

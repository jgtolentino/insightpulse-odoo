"""
Auto-patch: Manifest Validation and Auto-fix
Applies: GR-INSTALL-004
"""
import ast
import re
from pathlib import Path

REQUIRED_FIELDS = ['name', 'version', 'depends', 'data']
VERSION_PATTERN = r'^\d+\.\d+\.\d+\.\d+\.\d+$'  # e.g., 18.0.1.0.0

def validate_manifest(manifest_path):
    """Validate and report issues in __manifest__.py"""
    issues = []

    try:
        with open(manifest_path) as f:
            content = f.read()

        # Parse as Python dict
        manifest_dict = ast.literal_eval(content)

        # Check required fields
        for field in REQUIRED_FIELDS:
            if field not in manifest_dict:
                issues.append(f"Missing required field: '{field}'")

        # Validate version format
        if 'version' in manifest_dict:
            version = manifest_dict['version']
            if not re.match(VERSION_PATTERN, version):
                issues.append(f"Invalid version format: '{version}' (should be like '18.0.1.0.0')")

        # Validate installable
        if 'installable' in manifest_dict and not manifest_dict['installable']:
            issues.append("installable is set to False")

        # Check data files exist
        if 'data' in manifest_dict:
            module_dir = manifest_path.parent
            for data_file in manifest_dict['data']:
                file_path = module_dir / data_file
                if not file_path.exists():
                    issues.append(f"Data file not found: {data_file}")

    except SyntaxError as e:
        issues.append(f"Syntax error in manifest: {e}")
    except Exception as e:
        issues.append(f"Error reading manifest: {e}")

    return issues

def fix_version(manifest_path, odoo_version="18.0"):
    """Auto-fix version to match Odoo server version"""
    with open(manifest_path) as f:
        content = f.read()

    # Replace version
    version_pattern = r"['\"]version['\"]:\s*['\"][\d\.]+"
    new_version = f"'{odoo_version}.1.0.0'"

    fixed_content = re.sub(
        version_pattern,
        f"'version': {new_version}",
        content
    )

    return fixed_content

def apply_patch(module_path, auto_fix=False, odoo_version="18.0"):
    """Validate and optionally fix manifest"""
    module_path = Path(module_path)
    manifest_path = module_path / "__manifest__.py"

    if not manifest_path.exists():
        print(f"   ❌ No __manifest__.py found in {module_path}")
        return False

    print(f"🔍 Validating manifest: {manifest_path}")

    issues = validate_manifest(manifest_path)

    if not issues:
        print("   ✅ Manifest is valid!")
        return True

    print(f"   ⚠️  Found {len(issues)} issues:")
    for issue in issues:
        print(f"      - {issue}")

    if auto_fix:
        print("\n🔧 Applying auto-fixes...")

        # Backup
        backup_path = manifest_path.with_suffix('.py.backup')
        with open(manifest_path) as f:
            original = f.read()
        with open(backup_path, 'w') as f:
            f.write(original)

        # Apply fixes
        fixed_content = fix_version(manifest_path, odoo_version)

        # Ensure installable is True
        if "'installable': False" in fixed_content:
            fixed_content = fixed_content.replace("'installable': False", "'installable': True")

        # Write fixed version
        with open(manifest_path, 'w') as f:
            f.write(fixed_content)

        print(f"   ✅ Fixes applied! Backup saved to: {backup_path}")

        # Re-validate
        remaining_issues = validate_manifest(manifest_path)
        if remaining_issues:
            print(f"\n   ⚠️  {len(remaining_issues)} issues remain (manual fix needed):")
            for issue in remaining_issues:
                print(f"      - {issue}")
        else:
            print("\n   ✅ All issues fixed!")

    return True

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python fix_manifest_validation.py <module_path> [--fix] [--odoo-version=18.0]")
        sys.exit(1)

    module_path = sys.argv[1]
    auto_fix = "--fix" in sys.argv

    odoo_version = "18.0"
    for arg in sys.argv:
        if arg.startswith("--odoo-version="):
            odoo_version = arg.split("=")[1]

    apply_patch(module_path, auto_fix=auto_fix, odoo_version=odoo_version)

"""
Auto-patch: POS Custom Field Export/Import Fix
Applies: GR-POS-001
"""
import ast
import re
from pathlib import Path

def find_pos_model_files(module_path):
    """Find Python files that extend pos.order.line"""
    module_path = Path(module_path)
    candidates = []

    for py_file in module_path.rglob("*.py"):
        try:
            with open(py_file) as f:
                content = f.read()
                if "_inherit = 'pos.order.line'" in content or '_inherit = "pos.order.line"' in content:
                    candidates.append(py_file)
        except:
            continue

    return candidates

def extract_custom_fields(file_path):
    """Extract custom field names from model file"""
    with open(file_path) as f:
        content = f.read()

    # Simple regex to find field definitions
    field_pattern = r'(\w+)\s*=\s*fields\.\w+\('
    fields = re.findall(field_pattern, content)

    # Filter out common Odoo fields
    odoo_fields = {'name', 'create_date', 'write_date', 'create_uid', 'write_uid', 'id'}
    custom_fields = [f for f in fields if f not in odoo_fields]

    return custom_fields

def generate_export_import_methods(custom_fields):
    """Generate export_json and import_json methods"""
    export_lines = ["def export_json(self):"]
    export_lines.append("    res = super().export_json()")

    for field in custom_fields:
        export_lines.append(f"    res['{field}'] = self.{field}")

    export_lines.append("    return res")

    import_lines = ["", "def import_json(self, data):"]
    import_lines.append("    res = super().import_json(data)")

    for field in custom_fields:
        import_lines.append(f"    if '{field}' in data:")
        import_lines.append(f"        self.{field} = data['{field}']")

    import_lines.append("    return res")

    return "\n    ".join(export_lines) + "\n    " + "\n    ".join(import_lines)

def apply_patch(module_path):
    """Apply POS export/import fix to module"""
    print(f"🔧 Applying POS export/import fix to: {module_path}")

    model_files = find_pos_model_files(module_path)

    if not model_files:
        print("   ⚠️  No pos.order.line models found")
        return False

    for model_file in model_files:
        print(f"   📝 Processing: {model_file}")

        custom_fields = extract_custom_fields(model_file)

        if not custom_fields:
            print("      No custom fields found, skipping")
            continue

        print(f"      Found custom fields: {custom_fields}")

        # Read current content
        with open(model_file) as f:
            content = f.read()

        # Check if methods already exist
        if "def export_json" in content and "def import_json" in content:
            print("      ✅ export_json/import_json already exist, skipping")
            continue

        # Generate methods
        methods_code = generate_export_import_methods(custom_fields)

        # Find the class definition and add methods
        class_pattern = r'(class\s+\w+\(models\.Model\):.*?_inherit\s*=\s*["\']pos\.order\.line["\'])'

        def add_methods(match):
            return match.group(1) + "\n\n    " + methods_code

        patched_content = re.sub(class_pattern, add_methods, content, flags=re.DOTALL)

        # Backup original
        backup_file = model_file.with_suffix('.py.backup')
        with open(backup_file, 'w') as f:
            f.write(content)

        # Write patched version
        with open(model_file, 'w') as f:
            f.write(patched_content)

        print(f"      ✅ Patched! Backup saved to: {backup_file}")

    return True

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python apply_pos_export_import_fix.py <module_path>")
        sys.exit(1)

    module_path = sys.argv[1]
    success = apply_patch(module_path)

    if success:
        print("\n✅ Patch applied successfully!")
        print("   Remember to:")
        print("   1. Test in development environment")
        print("   2. Restart Odoo server")
        print("   3. Update the module")
    else:
        print("\n⚠️  No changes made")

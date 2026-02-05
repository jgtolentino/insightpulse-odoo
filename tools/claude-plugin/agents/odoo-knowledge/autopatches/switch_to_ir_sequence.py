"""
Auto-patch: Switch Invoice Numbering to ir.sequence
Applies: GR-ACCT-002
"""
import re
from pathlib import Path

def find_invoice_numbering_issues(module_path):
    """Find hardcoded invoice numbering in Python files"""
    module_path = Path(module_path)
    issues = []

    for py_file in module_path.rglob("*.py"):
        try:
            with open(py_file) as f:
                content = f.read()

            # Look for hardcoded numbering patterns
            patterns = [
                r'\.name\s*=\s*f?["\']INV.*?\{',  # f"INV{...}"
                r'\.name\s*=\s*["\']INV["\'].*?\+',  # "INV" + ...
                r'\.name\s*=\s*str\(.*?\.id\)',  # str(self.id)
            ]

            for pattern in patterns:
                if re.search(pattern, content):
                    issues.append(py_file)
                    break

        except:
            continue

    return issues

def generate_sequence_method():
    """Generate proper ir.sequence usage"""
    return '''
    def _compute_name(self):
        """Override to use ir.sequence for invoice numbering"""
        for move in self:
            if move.move_type in ('out_invoice', 'out_refund') and not move.name:
                # Use ir.sequence instead of hardcoded values
                sequence_code = 'account.move.%s' % move.move_type
                move.name = self.env['ir.sequence'].next_by_code(sequence_code)
            else:
                super()._compute_name()
'''

def create_sequence_data_file(module_path):
    """Create XML data file for sequence definition"""
    sequence_xml = '''<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <!-- Invoice Sequence -->
        <record id="sequence_invoice_custom" model="ir.sequence">
            <field name="name">Customer Invoice Sequence</field>
            <field name="code">account.move.out_invoice</field>
            <field name="prefix">INV/%(range_year)s/</field>
            <field name="padding">5</field>
            <field name="company_id" eval="False"/>
        </record>

        <!-- Refund Sequence -->
        <record id="sequence_refund_custom" model="ir.sequence">
            <field name="name">Customer Refund Sequence</field>
            <field name="code">account.move.out_refund</field>
            <field name="prefix">RINV/%(range_year)s/</field>
            <field name="padding">5</field>
            <field name="company_id" eval="False"/>
        </record>
    </data>
</odoo>
'''

    data_dir = Path(module_path) / "data"
    data_dir.mkdir(exist_ok=True)

    sequence_file = data_dir / "invoice_sequence.xml"

    if not sequence_file.exists():
        with open(sequence_file, 'w') as f:
            f.write(sequence_xml)
        print(f"   ✅ Created sequence data file: {sequence_file}")
        return True
    else:
        print(f"   ℹ️  Sequence data file already exists: {sequence_file}")
        return False

def apply_patch(module_path):
    """Apply ir.sequence fix to module"""
    print(f"🔧 Applying ir.sequence fix to: {module_path}")

    # Find files with hardcoded numbering
    issue_files = find_invoice_numbering_issues(module_path)

    if not issue_files:
        print("   ✅ No hardcoded invoice numbering found")
        return True

    print(f"   ⚠️  Found {len(issue_files)} files with hardcoded numbering:")
    for f in issue_files:
        print(f"      - {f}")

    # Create sequence data file
    sequence_created = create_sequence_data_file(module_path)

    if sequence_created:
        print("\n   📋 Next steps:")
        print("      1. Add 'data/invoice_sequence.xml' to __manifest__.py")
        print("      2. Replace hardcoded numbering with ir.sequence")
        print("      3. Update your module")
        print("\n   Example fix:")
        print(generate_sequence_method())

    return True

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python switch_to_ir_sequence.py <module_path>")
        sys.exit(1)

    module_path = sys.argv[1]
    apply_patch(module_path)

# Module Audit Reference Guide

Comprehensive guide for auditing Odoo modules for structure, compliance, and best practices.

## Table of Contents

1. [Module Structure Validation](#module-structure-validation)
2. [Manifest Validation](#manifest-validation)
3. [Security Rules Audit](#security-rules-audit)
4. [View Structure Audit](#view-structure-audit)
5. [Model Audit](#model-audit)
6. [Performance Audit](#performance-audit)

## Module Structure Validation

### Standard OCA Module Structure

```
my_module/
├── __init__.py                 # Module initialization (required)
├── __manifest__.py             # Module manifest (required)
├── README.rst                  # Module documentation (required for OCA)
├── models/
│   ├── __init__.py
│   └── my_model.py
├── views/
│   ├── my_model_views.xml
│   └── menu.xml
├── security/
│   ├── ir.model.access.csv
│   └── my_module_security.xml
├── data/
│   └── my_module_data.xml
├── demo/
│   └── my_module_demo.xml
├── static/
│   ├── description/
│   │   ├── icon.png
│   │   └── index.html
│   └── src/
│       ├── js/
│       ├── css/
│       └── xml/
├── tests/
│   ├── __init__.py
│   └── test_my_model.py
├── i18n/
│   ├── my_module.pot
│   └── es.po
├── wizards/
│   ├── __init__.py
│   └── my_wizard.py
└── reports/
    ├── __init__.py
    └── my_report.py
```

### Directory Purpose

**Required Directories**:
- `models/`: Business logic and data models
- `views/`: UI definitions (forms, trees, searches)
- `security/`: Access rights and record rules

**Optional Directories**:
- `data/`: Initial data to be loaded
- `demo/`: Demo data for testing
- `static/`: Frontend assets (JS, CSS, images)
- `tests/`: Unit and integration tests
- `i18n/`: Translations
- `wizards/`: Transient models for user interactions
- `reports/`: Report definitions

### Validation Script

```python
#!/usr/bin/env python3
"""
Module structure validator
Checks if module follows OCA guidelines
"""

import os
import sys
from pathlib import Path

class ModuleStructureValidator:
    
    REQUIRED_FILES = ['__init__.py', '__manifest__.py']
    RECOMMENDED_FILES = ['README.rst', 'README.md']
    
    REQUIRED_DIRS = {
        'models': 'has_models',
        'security': 'has_models',
        'views': 'has_views',
    }
    
    def __init__(self, module_path):
        self.module_path = Path(module_path)
        self.errors = []
        self.warnings = []
        self.info = []
    
    def validate(self):
        """Run all validation checks"""
        self.check_required_files()
        self.check_recommended_files()
        self.check_directory_structure()
        self.check_init_files()
        self.check_manifest()
        self.check_security_files()
        
        return self.generate_report()
    
    def check_required_files(self):
        """Check for required files"""
        for filename in self.REQUIRED_FILES:
            file_path = self.module_path / filename
            if not file_path.exists():
                self.errors.append(f"Missing required file: {filename}")
    
    def check_recommended_files(self):
        """Check for recommended files"""
        has_readme = any(
            (self.module_path / f).exists() 
            for f in self.RECOMMENDED_FILES
        )
        if not has_readme:
            self.warnings.append("Missing README file (README.rst or README.md)")
    
    def check_directory_structure(self):
        """Check directory structure"""
        manifest = self.load_manifest()
        
        # Check models directory
        models_dir = self.module_path / 'models'
        if models_dir.exists():
            if not (models_dir / '__init__.py').exists():
                self.errors.append("models/ directory missing __init__.py")
            
            # Should have security rules
            security_dir = self.module_path / 'security'
            if not security_dir.exists():
                self.errors.append("Has models but missing security/ directory")
        
        # Check views directory
        views_dir = self.module_path / 'views'
        if views_dir.exists():
            view_files = list(views_dir.glob('*.xml'))
            if not view_files:
                self.warnings.append("views/ directory is empty")
    
    def check_init_files(self):
        """Check all __init__.py files"""
        for dirpath, dirnames, filenames in os.walk(self.module_path):
            # Skip hidden directories
            dirnames[:] = [d for d in dirnames if not d.startswith('.')]
            
            if '__init__.py' in filenames:
                init_path = Path(dirpath) / '__init__.py'
                
                # Check if __init__.py imports subdirectories
                subdirs = [d for d in dirnames if not d.startswith('_')]
                if subdirs:
                    with open(init_path) as f:
                        content = f.read()
                        for subdir in subdirs:
                            if f'from . import {subdir}' not in content:
                                self.warnings.append(
                                    f"{init_path.relative_to(self.module_path)}: "
                                    f"Missing import for subdirectory '{subdir}'"
                                )
    
    def check_manifest(self):
        """Validate manifest file"""
        manifest = self.load_manifest()
        
        if not manifest:
            self.errors.append("Invalid or missing __manifest__.py")
            return
        
        # Required keys
        required_keys = ['name', 'version', 'category', 'author', 'license', 'depends']
        for key in required_keys:
            if key not in manifest:
                self.errors.append(f"Manifest missing required key: {key}")
        
        # Recommended keys
        recommended_keys = ['summary', 'description', 'website']
        for key in recommended_keys:
            if key not in manifest:
                self.warnings.append(f"Manifest missing recommended key: {key}")
        
        # Version format check
        if 'version' in manifest:
            version = manifest['version']
            parts = version.split('.')
            if len(parts) != 5:
                self.errors.append(
                    f"Version format should be X.0.Y.Z.W (e.g., 19.0.1.0.0), got: {version}"
                )
        
        # License check
        if 'license' in manifest:
            valid_licenses = [
                'AGPL-3', 'GPL-2', 'GPL-3', 'LGPL-3',
                'MIT', 'Apache-2.0', 'BSD-2-Clause'
            ]
            if manifest['license'] not in valid_licenses:
                self.warnings.append(f"Non-standard license: {manifest['license']}")
        
        # Installable check
        if not manifest.get('installable', True):
            self.info.append("Module marked as not installable")
    
    def check_security_files(self):
        """Check security configuration"""
        security_dir = self.module_path / 'security'
        
        if not security_dir.exists():
            return
        
        # Check for ir.model.access.csv
        access_file = security_dir / 'ir.model.access.csv'
        if not access_file.exists():
            self.warnings.append("No ir.model.access.csv file found")
        else:
            # Validate CSV format
            with open(access_file) as f:
                lines = f.readlines()
                if not lines:
                    self.warnings.append("ir.model.access.csv is empty")
                else:
                    # Check header
                    header = lines[0].strip()
                    expected = 'id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink'
                    if header != expected:
                        self.errors.append(
                            f"Invalid CSV header in ir.model.access.csv\n"
                            f"Expected: {expected}\n"
                            f"Got: {header}"
                        )
    
    def load_manifest(self):
        """Load and parse __manifest__.py"""
        manifest_path = self.module_path / '__manifest__.py'
        
        if not manifest_path.exists():
            return None
        
        try:
            import ast
            with open(manifest_path) as f:
                manifest = ast.literal_eval(f.read())
            return manifest
        except Exception as e:
            self.errors.append(f"Failed to parse __manifest__.py: {e}")
            return None
    
    def generate_report(self):
        """Generate validation report"""
        report = {
            'module': self.module_path.name,
            'path': str(self.module_path),
            'errors': self.errors,
            'warnings': self.warnings,
            'info': self.info,
            'passed': len(self.errors) == 0
        }
        
        return report


def validate_all_modules(addons_path):
    """Validate all modules in addons directory"""
    addons_path = Path(addons_path)
    results = []
    
    for module_dir in addons_path.iterdir():
        if not module_dir.is_dir() or module_dir.name.startswith('.'):
            continue
        
        manifest_path = module_dir / '__manifest__.py'
        if manifest_path.exists():
            validator = ModuleStructureValidator(module_dir)
            result = validator.validate()
            results.append(result)
    
    return results


def print_report(results):
    """Print validation report"""
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    print(f"\n{'='*70}")
    print(f"Module Structure Validation Report")
    print(f"{'='*70}")
    print(f"Total modules: {total}")
    print(f"Passed: {passed} ({passed/total*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total*100:.1f}%)")
    print(f"{'='*70}\n")
    
    for result in results:
        if not result['passed']:
            print(f"❌ {result['module']}")
            for error in result['errors']:
                print(f"   ERROR: {error}")
            for warning in result['warnings']:
                print(f"   WARNING: {warning}")
            print()
        else:
            print(f"✅ {result['module']}")
            if result['warnings']:
                for warning in result['warnings']:
                    print(f"   WARNING: {warning}")
            print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python module_structure_validator.py <addons_path>")
        sys.exit(1)
    
    addons_path = sys.argv[1]
    results = validate_all_modules(addons_path)
    print_report(results)
    
    # Exit with error if any module failed
    if any(not r['passed'] for r in results):
        sys.exit(1)
```

## Manifest Validation

### Required Manifest Keys

```python
# __manifest__.py template
{
    # Required
    'name': 'Module Name',
    'version': '19.0.1.0.0',
    'category': 'Category/Subcategory',
    'author': 'Author Name',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    
    # Recommended
    'summary': 'Short one-line description',
    'description': """
        Long description
        Multiple lines
    """,
    'website': 'https://github.com/author/module',
    
    # Optional but useful
    'maintainers': ['github_username'],
    'contributors': ['contributor1', 'contributor2'],
    'images': ['static/description/banner.png'],
    '
': ['keyword1', 'keyword2'],
    
    # Data files
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/my_model_views.xml',
        'data/my_module_data.xml',
    ],
    
    # Demo data
    'demo': [
        'demo/my_module_demo.xml',
    ],
    
    # External dependencies
    'external_dependencies': {
        'python': ['requests', 'pandas'],
        'bin': ['wkhtmltopdf'],
    },
    
    # Flags
    'installable': True,
    'application': False,
    'auto_install': False,
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}
```

### Version Format

**Format**: `{odoo_version}.{major}.{minor}.{patch}`

Examples:
- `19.0.1.0.0` - First version for Odoo 19
- `19.0.1.1.0` - Bug fix
- `19.0.2.0.0` - New feature (breaking changes)

### Category Guidelines

Standard categories:
- `Accounting/Accounting`
- `Sales/Sales`
- `Website/Website`
- `Human Resources`
- `Manufacturing`
- `Inventory/Inventory`
- `Project`
- `Services/Project`
- `Productivity`
- `Administration`
- `Technical`
- `Hidden`

## Security Rules Audit

### Access Rights (ir.model.access)

**Template**:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_my_model_user,my.model.user,model_my_model,base.group_user,1,0,0,0
access_my_model_manager,my.model.manager,model_my_model,base.group_system,1,1,1,1
```

**Validation checks**:
```python
def validate_access_rights(module_path):
    """Validate access rights configuration"""
    issues = []
    
    # Check if CSV file exists
    access_file = module_path / 'security/ir.model.access.csv'
    if not access_file.exists():
        issues.append("Missing ir.model.access.csv")
        return issues
    
    # Parse CSV
    import csv
    with open(access_file) as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Check for each model
    models_path = module_path / 'models'
    if models_path.exists():
        for model_file in models_path.glob('*.py'):
            # Extract model names from Python file
            with open(model_file) as f:
                content = f.read()
                import re
                models = re.findall(r"_name\s*=\s*['\"]([^'\"]+)['\"]", content)
            
            for model in models:
                # Check if model has access rules
                model_rules = [
                    row for row in rows
                    if row.get('model_id:id', '').endswith(model.replace('.', '_'))
                ]
                
                if not model_rules:
                    issues.append(f"Model {model} has no access rules")
                else:
                    # Check for at least user and manager access
                    has_user_access = any('user' in row.get('id', '') for row in model_rules)
                    has_manager_access = any('manager' in row.get('id', '') or 'system' in row.get('group_id:id', '') for row in model_rules)
                    
                    if not has_user_access:
                        issues.append(f"Model {model} has no user access rule")
                    if not has_manager_access:
                        issues.append(f"Model {model} has no manager/system access rule")
    
    return issues
```

### Record Rules (ir.rule)

**Template**:
```xml
<odoo>
    <data noupdate="1">
        
        <!-- Multi-company rule -->
        <record id="my_model_company_rule" model="ir.rule">
            <field name="name">My Model: multi-company</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[
                '|',
                ('company_id', '=', False),
                ('company_id', 'in', company_ids)
            ]</field>
            <field name="global" eval="True"/>
        </record>
        
        <!-- User can only see own records -->
        <record id="my_model_user_rule" model="ir.rule">
            <field name="name">My Model: user can see own records</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[('user_id', '=', user.id)]</field>
            <field name="groups" eval="[(4, ref('base.group_user'))]"/>
        </record>
        
        <!-- Manager can see all -->
        <record id="my_model_manager_rule" model="ir.rule">
            <field name="name">My Model: manager can see all</field>
            <field name="model_id" ref="model_my_model"/>
            <field name="domain_force">[(1, '=', 1)]</field>
            <field name="groups" eval="[(4, ref('base.group_system'))]"/>
        </record>
        
    </data>
</odoo>
```

## View Structure Audit

### View Validation

```python
def validate_views(module_path):
    """Validate XML views"""
    issues = []
    
    views_dir = module_path / 'views'
    if not views_dir.exists():
        return issues
    
    for view_file in views_dir.glob('*.xml'):
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(view_file)
            root = tree.getroot()
            
            # Check for proper structure
            if root.tag != 'odoo':
                issues.append(f"{view_file.name}: Root element should be <odoo>")
            
            # Check for views
            for record in root.findall('.//record'):
                model = record.get('model')
                
                if model == 'ir.ui.view':
                    # Check required fields
                    name = record.find('./field[@name="name"]')
                    model_field = record.find('./field[@name="model"]')
                    arch = record.find('./field[@name="arch"]')
                    
                    if name is None:
                        issues.append(f"{view_file.name}: View missing 'name' field")
                    if model_field is None:
                        issues.append(f"{view_file.name}: View missing 'model' field")
                    if arch is None:
                        issues.append(f"{view_file.name}: View missing 'arch' field")
                    
                    # Check view type
                    if arch is not None:
                        view_type = arch.get('type')
                        if view_type not in ['form', 'tree', 'search', 'kanban', 'calendar', 'graph', 'pivot', 'activity']:
                            issues.append(f"{view_file.name}: Invalid view type: {view_type}")
                
                elif model == 'ir.ui.menu':
                    # Check menu has name
                    name = record.find('./field[@name="name"]')
                    if name is None:
                        issues.append(f"{view_file.name}: Menu missing 'name' field")
        
        except ET.ParseError as e:
            issues.append(f"{view_file.name}: XML parse error: {e}")
    
    return issues
```

## Model Audit

### Model Best Practices

```python
def audit_model(model_file):
    """Audit a model Python file"""
    issues = []
    
    with open(model_file) as f:
        content = f.read()
    
    # Check for proper imports
    required_imports = ['from odoo import models, fields']
    if not any(imp in content for imp in required_imports):
        issues.append("Missing required imports: from odoo import models, fields")
    
    # Check for _name
    if '_name =' not in content and '_inherit =' not in content:
        issues.append("Model must have _name or _inherit")
    
    # Check for _description
    if '_description =' not in content:
        issues.append("Model missing _description (required for accessibility)")
    
    # Check for SQL injection vulnerabilities
    if 'self.env.cr.execute(' in content:
        issues.append("Direct SQL execution found - use ORM instead")
    
    # Check for proper string formatting
    if '% ' in content or '.format(' in content:
        issues.append("Use f-strings instead of % or .format()")
    
    # Check for translatable strings
    import re
    strings = re.findall(r"['\"]([^'\"]+)['\"]", content)
    for string in strings:
        if len(string) > 10 and not re.match(r"^[a-z_]+$", string):
            # Check if it's wrapped in _()
            if f"_('{string}')" not in content and f'_("{string}")' not in content:
                issues.append(f"String '{string}' should be translatable with _()")
    
    return issues
```

## Performance Audit

### Common Performance Issues

1. **N+1 Queries**
```python
# Bad - N+1 queries
for order in orders:
    print(order.partner_id.name)

# Good - Prefetch
orders = orders.with_prefetch(['partner_id'])
for order in orders:
    print(order.partner_id.name)
```

2. **Missing Indexes**
```python
# Bad - No index on frequently searched field
reference = fields.Char(string='Reference')

# Good - Add index
reference = fields.Char(string='Reference', index=True)
```

3. **Inefficient Search Domains**
```python
# Bad - Multiple searches
partners = self.env['res.partner'].search([])
filtered = [p for p in partners if p.country_id.code == 'US']

# Good - Single search with domain
partners = self.env['res.partner'].search([
    ('country_id.code', '=', 'US')
])
```

4. **Unoptimized Computed Fields**
```python
# Bad - Computed without store
total = fields.Float(compute='_compute_total')

# Good - Stored computed field
total = fields.Float(compute='_compute_total', store=True)
```

### Performance Validation Script

```python
def audit_performance(module_path):
    """Audit module for performance issues"""
    issues = []
    
    models_dir = module_path / 'models'
    if not models_dir.exists():
        return issues
    
    for model_file in models_dir.glob('*.py'):
        with open(model_file) as f:
            content = f.read()
        
        # Check for missing indexes on search fields
        import re
        
        # Find all Char/Text fields without index
        char_fields = re.findall(
            r"(\w+)\s*=\s*fields\.(Char|Text)\([^)]*\)",
            content
        )
        for field_name, field_type in char_fields:
            if 'index=True' not in content:
                issues.append(
                    f"{model_file.name}: Consider adding index to {field_name} "
                    f"if frequently used in search domains"
                )
        
        # Check for computed fields without store
        computed_fields = re.findall(
            r"(\w+)\s*=\s*fields\.\w+\([^)]*compute=['\"]([^'\"]+)['\"][^)]*\)",
            content
        )
        for field_name, compute_method in computed_fields:
            field_def = re.search(
                rf"{field_name}\s*=\s*fields\.\w+\([^)]*\)",
                content
            )
            if field_def and 'store=True' not in field_def.group(0):
                issues.append(
                    f"{model_file.name}: Field {field_name} is computed but not stored - "
                    f"consider adding store=True if used in searches"
                )
        
        # Check for search without limit
        if re.search(r"\.search\(\[[^\]]*\]\)(?!\s*\.limit)", content):
            issues.append(
                f"{model_file.name}: Found search() without limit - "
                f"consider adding limit or using search_count()"
            )
    
    return issues
```

---

**Last Updated**: 2025-11-01
**Maintainer**: InsightPulse Team

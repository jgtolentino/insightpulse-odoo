# Module Structure Audit Example

Complete walkthrough of auditing an Odoo module for OCA compliance and best practices.

## Scenario

Audit the `ipai_rate_policy` module to ensure it follows OCA guidelines before submitting to OCA repository.

## Step 1: Initialize Module Audit

```bash
cd /home/runner/work/insightpulse-odoo/insightpulse-odoo
MODULE_PATH="addons/insightpulse/finance/ipai_rate_policy"
MODULE_NAME="ipai_rate_policy"
AUDIT_REPORT="audit-reports/${MODULE_NAME}-structure-$(date +%Y-%m-%d).md"

mkdir -p audit-reports
echo "# Module Structure Audit: $MODULE_NAME" > "$AUDIT_REPORT"
echo "**Date**: $(date)" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"
```

## Step 2: Check Directory Structure

```bash
echo "## Directory Structure Check" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Check for required directories
REQUIRED_DIRS=("models" "views" "security")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$MODULE_PATH/$dir" ]; then
        echo "✅ $dir/" >> "$AUDIT_REPORT"
    else
        echo "❌ $dir/ (MISSING - CRITICAL)" >> "$AUDIT_REPORT"
    fi
done

# Check for recommended directories
RECOMMENDED_DIRS=("tests" "data" "demo" "static/description")
for dir in "${RECOMMENDED_DIRS[@]}"; do
    if [ -d "$MODULE_PATH/$dir" ]; then
        echo "✅ $dir/" >> "$AUDIT_REPORT"
    else
        echo "⚠️  $dir/ (missing - recommended)" >> "$AUDIT_REPORT"
    fi
done

echo "" >> "$AUDIT_REPORT"
```

**Example Output**:
```
## Directory Structure Check

✅ models/
✅ views/
✅ security/
✅ tests/
⚠️  data/ (missing - recommended)
⚠️  demo/ (missing - recommended)
✅ static/description/
```

## Step 3: Validate Required Files

```bash
echo "## Required Files Check" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Check critical files
if [ -f "$MODULE_PATH/__init__.py" ]; then
    echo "✅ __init__.py" >> "$AUDIT_REPORT"
else
    echo "❌ __init__.py (MISSING - CRITICAL)" >> "$AUDIT_REPORT"
fi

if [ -f "$MODULE_PATH/__manifest__.py" ]; then
    echo "✅ __manifest__.py" >> "$AUDIT_REPORT"
else
    echo "❌ __manifest__.py (MISSING - CRITICAL)" >> "$AUDIT_REPORT"
fi

# Check documentation
if [ -f "$MODULE_PATH/README.rst" ]; then
    echo "✅ README.rst" >> "$AUDIT_REPORT"
elif [ -f "$MODULE_PATH/README.md" ]; then
    echo "✅ README.md" >> "$AUDIT_REPORT"
    echo "ℹ️  Note: OCA prefers README.rst over README.md" >> "$AUDIT_REPORT"
else
    echo "⚠️  README (missing - required for OCA)" >> "$AUDIT_REPORT"
fi

# Check security files
if [ -f "$MODULE_PATH/security/ir.model.access.csv" ]; then
    echo "✅ security/ir.model.access.csv" >> "$AUDIT_REPORT"
else
    echo "❌ security/ir.model.access.csv (MISSING - CRITICAL)" >> "$AUDIT_REPORT"
fi

# Check icon
if [ -f "$MODULE_PATH/static/description/icon.png" ]; then
    echo "✅ static/description/icon.png" >> "$AUDIT_REPORT"
else
    echo "⚠️  static/description/icon.png (missing - recommended)" >> "$AUDIT_REPORT"
fi

echo "" >> "$AUDIT_REPORT"
```

## Step 4: Validate Manifest File

```bash
echo "## Manifest Validation" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

python3 << 'PYTHON_SCRIPT'
import ast
import sys

module_path = "addons/insightpulse/finance/ipai_rate_policy"
manifest_file = f"{module_path}/__manifest__.py"

try:
    with open(manifest_file) as f:
        manifest = ast.literal_eval(f.read())
    
    # Check required keys
    required_keys = ['name', 'version', 'category', 'author', 'license', 'depends']
    missing_required = []
    for key in required_keys:
        if key not in manifest:
            missing_required.append(key)
    
    if missing_required:
        print(f"❌ Missing required keys: {', '.join(missing_required)}")
    else:
        print("✅ All required manifest keys present")
    
    # Check recommended keys
    recommended_keys = ['summary', 'description', 'website', 'maintainers']
    missing_recommended = []
    for key in recommended_keys:
        if key not in manifest:
            missing_recommended.append(key)
    
    if missing_recommended:
        print(f"⚠️  Missing recommended keys: {', '.join(missing_recommended)}")
    
    # Validate version format
    if 'version' in manifest:
        version = manifest['version']
        parts = version.split('.')
        if len(parts) != 5:
            print(f"❌ Invalid version format: {version} (should be X.0.Y.Z.W)")
        else:
            print(f"✅ Version format valid: {version}")
    
    # Validate license
    if 'license' in manifest:
        valid_licenses = ['AGPL-3', 'GPL-2', 'GPL-3', 'LGPL-3', 'MIT', 'Apache-2.0']
        if manifest['license'] not in valid_licenses:
            print(f"⚠️  Non-standard license: {manifest['license']}")
        else:
            print(f"✅ License valid: {manifest['license']}")
    
    # Check installable
    if not manifest.get('installable', True):
        print("⚠️  Module marked as not installable")
    
    # Print manifest content
    print(f"\n### Manifest Content:")
    print(f"- **Name**: {manifest.get('name', 'N/A')}")
    print(f"- **Version**: {manifest.get('version', 'N/A')}")
    print(f"- **Category**: {manifest.get('category', 'N/A')}")
    print(f"- **Author**: {manifest.get('author', 'N/A')}")
    print(f"- **License**: {manifest.get('license', 'N/A')}")
    print(f"- **Depends**: {', '.join(manifest.get('depends', []))}")
    print(f"- **Installable**: {manifest.get('installable', True)}")
    print(f"- **Application**: {manifest.get('application', False)}")
    
except FileNotFoundError:
    print(f"❌ Manifest file not found: {manifest_file}")
except Exception as e:
    print(f"❌ Error parsing manifest: {e}")
PYTHON_SCRIPT
```

**Example Output**:
```
## Manifest Validation

✅ All required manifest keys present
⚠️  Missing recommended keys: maintainers
✅ Version format valid: 19.0.1.0.0
✅ License valid: LGPL-3

### Manifest Content:
- **Name**: Rate Policy Automation
- **Version**: 19.0.1.0.0
- **Category**: Accounting/Management
- **Author**: InsightPulse Team
- **License**: LGPL-3
- **Depends**: base, mail, hr, account
- **Installable**: True
- **Application**: False
```

## Step 5: Validate Security Configuration

```bash
echo "## Security Configuration Audit" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Parse access rights CSV
if [ -f "$MODULE_PATH/security/ir.model.access.csv" ]; then
    echo "### Access Rights" >> "$AUDIT_REPORT"
    echo "" >> "$AUDIT_REPORT"
    echo '```csv' >> "$AUDIT_REPORT"
    cat "$MODULE_PATH/security/ir.model.access.csv" >> "$AUDIT_REPORT"
    echo '```' >> "$AUDIT_REPORT"
    echo "" >> "$AUDIT_REPORT"
    
    # Count access rules
    RULE_COUNT=$(tail -n +2 "$MODULE_PATH/security/ir.model.access.csv" | wc -l)
    echo "**Access rules count**: $RULE_COUNT" >> "$AUDIT_REPORT"
    echo "" >> "$AUDIT_REPORT"
    
    # Check for at least 2 rules per model (user + manager)
    if [ $RULE_COUNT -lt 2 ]; then
        echo "⚠️  Warning: Less than 2 access rules (should have at least user and manager access)" >> "$AUDIT_REPORT"
    fi
fi

# Check for record rules
if [ -f "$MODULE_PATH/security/${MODULE_NAME}_security.xml" ]; then
    echo "✅ Record rules file present" >> "$AUDIT_REPORT"
else
    echo "ℹ️  No record rules file (may not be needed)" >> "$AUDIT_REPORT"
fi

echo "" >> "$AUDIT_REPORT"
```

## Step 6: Validate Models

```bash
echo "## Models Validation" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

python3 << 'PYTHON_SCRIPT'
import os
import re
from pathlib import Path

module_path = Path("addons/insightpulse/finance/ipai_rate_policy")
models_path = module_path / "models"

if not models_path.exists():
    print("❌ No models directory found")
    exit()

model_files = list(models_path.glob("*.py"))
model_files = [f for f in model_files if f.name != "__init__.py"]

print(f"**Total model files**: {len(model_files)}\n")

issues = []

for model_file in model_files:
    print(f"### {model_file.name}")
    print()
    
    with open(model_file) as f:
        content = f.read()
    
    # Check for _name
    if '_name =' in content or '_inherit =' in content:
        # Extract model name
        name_match = re.search(r"_name\s*=\s*['\"]([^'\"]+)['\"]", content)
        inherit_match = re.search(r"_inherit\s*=\s*['\"]([^'\"]+)['\"]", content)
        
        if name_match:
            print(f"✅ Model name: `{name_match.group(1)}`")
        elif inherit_match:
            print(f"✅ Inherits: `{inherit_match.group(1)}`")
    else:
        issues.append(f"{model_file.name}: Missing _name or _inherit")
        print("❌ Missing _name or _inherit")
    
    # Check for _description
    if '_description =' in content:
        desc_match = re.search(r"_description\s*=\s*['\"]([^'\"]+)['\"]", content)
        if desc_match:
            print(f"✅ Description: {desc_match.group(1)}")
    else:
        issues.append(f"{model_file.name}: Missing _description")
        print("⚠️  Missing _description (required for accessibility)")
    
    # Check for SQL injection risks
    if 'self.env.cr.execute(' in content or 'self._cr.execute(' in content:
        issues.append(f"{model_file.name}: Direct SQL execution found")
        print("⚠️  Direct SQL execution (prefer ORM)")
    
    # Check for proper imports
    if 'from odoo import models' not in content:
        issues.append(f"{model_file.name}: Missing required imports")
        print("❌ Missing required imports")
    
    print()

if issues:
    print("\n### Issues Summary")
    for issue in issues:
        print(f"- {issue}")
else:
    print("\n✅ All models pass validation")
PYTHON_SCRIPT
```

**Example Output**:
```
## Models Validation

**Total model files**: 3

### rate_policy.py

✅ Model name: `rate.policy`
✅ Description: Rate Policy Configuration
✅ No SQL injection risks
✅ Proper imports

### rate_policy_line.py

✅ Model name: `rate.policy.line`
✅ Description: Rate Policy Lines
✅ No SQL injection risks
✅ Proper imports

### rate_policy_approval.py

✅ Model name: `rate.policy.approval`
⚠️  Missing _description (required for accessibility)
✅ No SQL injection risks
✅ Proper imports

### Issues Summary
- rate_policy_approval.py: Missing _description
```

## Step 7: Validate Views

```bash
echo "## Views Validation" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

python3 << 'PYTHON_SCRIPT'
import xml.etree.ElementTree as ET
from pathlib import Path

module_path = Path("addons/insightpulse/finance/ipai_rate_policy")
views_path = module_path / "views"

if not views_path.exists():
    print("⚠️  No views directory found")
    exit()

view_files = list(views_path.glob("*.xml"))
print(f"**Total view files**: {len(view_files)}\n")

issues = []

for view_file in view_files:
    print(f"### {view_file.name}")
    print()
    
    try:
        tree = ET.parse(view_file)
        root = tree.getroot()
        
        # Check root element
        if root.tag != 'odoo':
            issues.append(f"{view_file.name}: Root element should be <odoo>")
            print(f"❌ Root element is <{root.tag}> (should be <odoo>)")
        else:
            print("✅ Root element is <odoo>")
        
        # Count views and menus
        views = root.findall(".//record[@model='ir.ui.view']")
        menus = root.findall(".//record[@model='ir.ui.menu']")
        actions = root.findall(".//record[@model='ir.actions.act_window']")
        
        print(f"- Views: {len(views)}")
        print(f"- Menus: {len(menus)}")
        print(f"- Actions: {len(actions)}")
        
        # Check each view
        for view in views:
            view_id = view.get('id', 'unknown')
            
            # Check required fields
            name_field = view.find("./field[@name='name']")
            model_field = view.find("./field[@name='model']")
            arch_field = view.find("./field[@name='arch']")
            
            if name_field is None:
                issues.append(f"{view_file.name}: View {view_id} missing 'name' field")
            if model_field is None:
                issues.append(f"{view_file.name}: View {view_id} missing 'model' field")
            if arch_field is None:
                issues.append(f"{view_file.name}: View {view_id} missing 'arch' field")
        
        print()
        
    except ET.ParseError as e:
        issues.append(f"{view_file.name}: XML parse error - {e}")
        print(f"❌ XML parse error: {e}")
        print()

if issues:
    print("\n### Issues Summary")
    for issue in issues:
        print(f"- {issue}")
else:
    print("\n✅ All views pass validation")
PYTHON_SCRIPT
```

## Step 8: Check Tests

```bash
echo "## Tests Validation" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

if [ -d "$MODULE_PATH/tests" ]; then
    TEST_FILES=$(find "$MODULE_PATH/tests" -name "test_*.py" | wc -l)
    echo "✅ Tests directory exists" >> "$AUDIT_REPORT"
    echo "**Test files count**: $TEST_FILES" >> "$AUDIT_REPORT"
    echo "" >> "$AUDIT_REPORT"
    
    if [ $TEST_FILES -eq 0 ]; then
        echo "⚠️  Warning: Tests directory exists but no test files found" >> "$AUDIT_REPORT"
    else
        # List test files
        echo "### Test Files" >> "$AUDIT_REPORT"
        find "$MODULE_PATH/tests" -name "test_*.py" -exec basename {} \; | while read file; do
            echo "- $file" >> "$AUDIT_REPORT"
        done
    fi
else
    echo "⚠️  No tests directory (recommended for OCA modules)" >> "$AUDIT_REPORT"
fi

echo "" >> "$AUDIT_REPORT"
```

## Step 9: Check Code Quality

```bash
echo "## Code Quality Check" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Run flake8 if available
if command -v flake8 &> /dev/null; then
    echo "### Flake8 Results" >> "$AUDIT_REPORT"
    echo '```' >> "$AUDIT_REPORT"
    flake8 "$MODULE_PATH" --config=.flake8 --count 2>&1 >> "$AUDIT_REPORT" || echo "Issues found" >> "$AUDIT_REPORT"
    echo '```' >> "$AUDIT_REPORT"
else
    echo "⚠️  flake8 not installed, skipping code style check" >> "$AUDIT_REPORT"
fi

echo "" >> "$AUDIT_REPORT"

# Run pylint if available
if command -v pylint &> /dev/null; then
    echo "### Pylint Results" >> "$AUDIT_REPORT"
    echo '```' >> "$AUDIT_REPORT"
    pylint "$MODULE_PATH" --rcfile=.pylintrc-mandatory --score=y 2>&1 | tail -20 >> "$AUDIT_REPORT"
    echo '```' >> "$AUDIT_REPORT"
else
    echo "⚠️  pylint not installed, skipping code quality check" >> "$AUDIT_REPORT"
fi

echo "" >> "$AUDIT_REPORT"
```

## Step 10: Generate Summary

```bash
echo "## Audit Summary" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Count issues
CRITICAL_COUNT=$(grep -c "❌" "$AUDIT_REPORT" || echo "0")
WARNING_COUNT=$(grep -c "⚠️" "$AUDIT_REPORT" || echo "0")
PASS_COUNT=$(grep -c "✅" "$AUDIT_REPORT" || echo "0")

echo "### Statistics" >> "$AUDIT_REPORT"
echo "- ✅ Passed: $PASS_COUNT" >> "$AUDIT_REPORT"
echo "- ⚠️  Warnings: $WARNING_COUNT" >> "$AUDIT_REPORT"
echo "- ❌ Critical: $CRITICAL_COUNT" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

# Determine overall status
if [ $CRITICAL_COUNT -eq 0 ]; then
    if [ $WARNING_COUNT -eq 0 ]; then
        echo "**Overall Status**: ✅ EXCELLENT - Ready for OCA submission" >> "$AUDIT_REPORT"
    elif [ $WARNING_COUNT -le 3 ]; then
        echo "**Overall Status**: ✅ GOOD - Minor improvements recommended" >> "$AUDIT_REPORT"
    else
        echo "**Overall Status**: ⚠️  ACCEPTABLE - Address warnings before OCA submission" >> "$AUDIT_REPORT"
    fi
else
    echo "**Overall Status**: ❌ NEEDS WORK - Fix critical issues before submission" >> "$AUDIT_REPORT"
fi

echo "" >> "$AUDIT_REPORT"
echo "### Recommendations" >> "$AUDIT_REPORT"
echo "" >> "$AUDIT_REPORT"

if [ $CRITICAL_COUNT -gt 0 ]; then
    echo "1. **Critical**: Fix all critical issues immediately" >> "$AUDIT_REPORT"
fi

if [ $WARNING_COUNT -gt 0 ]; then
    echo "2. **Warnings**: Address warnings for better code quality" >> "$AUDIT_REPORT"
fi

echo "3. **Documentation**: Ensure README.rst follows OCA template" >> "$AUDIT_REPORT"
echo "4. **Testing**: Add comprehensive unit and integration tests" >> "$AUDIT_REPORT"
echo "5. **Review**: Have another developer review the module" >> "$AUDIT_REPORT"

echo "" >> "$AUDIT_REPORT"
echo "---" >> "$AUDIT_REPORT"
echo "**Audit Completed**: $(date)" >> "$AUDIT_REPORT"
echo "**Auditor**: Module Structure Validator" >> "$AUDIT_REPORT"

# Display report
cat "$AUDIT_REPORT"
```

**Example Output**:
```
## Audit Summary

### Statistics
- ✅ Passed: 18
- ⚠️  Warnings: 3
- ❌ Critical: 0

**Overall Status**: ✅ GOOD - Minor improvements recommended

### Recommendations

2. **Warnings**: Address warnings for better code quality
3. **Documentation**: Ensure README.rst follows OCA template
4. **Testing**: Add comprehensive unit and integration tests
5. **Review**: Have another developer review the module

---
**Audit Completed**: 2025-11-01
**Auditor**: Module Structure Validator
```

## Result

**Module Audit Complete**:
- ✅ Structure follows OCA guidelines
- ✅ Manifest properly configured
- ✅ Security rules defined
- ⚠️  Minor improvements needed
- ✅ Ready for OCA submission after addressing warnings

**Action Items**:
1. Add `_description` to rate_policy_approval.py
2. Add maintainers to __manifest__.py
3. Ensure README.rst follows OCA template
4. Verify test coverage is adequate

---

**Last Updated**: 2025-11-01

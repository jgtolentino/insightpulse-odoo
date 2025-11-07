#!/usr/bin/env bash
# Run OCA Maintainer Quality Tools checks on Odoo modules

set -euo pipefail

echo "🔍 Running OCA MQT quality checks..."

# Find all Odoo modules in addons/
modules=$(find addons -mindepth 1 -maxdepth 1 -type d -not -name "__pycache__" -not -name ".*")

if [ -z "$modules" ]; then
    echo "⚠️  No modules found in addons/"
    exit 0
fi

failed_modules=()

for module_path in $modules; do
    module_name=$(basename "$module_path")

    echo ""
    echo "📦 Checking module: $module_name"

    # Check __manifest__.py exists
    if [ ! -f "$module_path/__manifest__.py" ]; then
        echo "   ❌ Missing __manifest__.py"
        failed_modules+=("$module_name")
        continue
    fi

    # Check __init__.py exists
    if [ ! -f "$module_path/__init__.py" ]; then
        echo "   ⚠️  Missing __init__.py"
    fi

    # Run OCA MQT checks (if installed)
    if command -v odoo-analyse-module &> /dev/null; then
        if odoo-analyse-module "$module_path" --verbose; then
            echo "   ✅ OCA MQT passed"
        else
            echo "   ❌ OCA MQT failed"
            failed_modules+=("$module_name")
        fi
    else
        echo "   ⚠️  odoo-analyse-module not installed, skipping advanced checks"
        echo "   ✅ Basic structure validated"
    fi
done

echo ""
echo "=========================================="
echo "OCA MQT Summary"
echo "=========================================="

if [ ${#failed_modules[@]} -eq 0 ]; then
    echo "✅ All modules passed quality checks"
    exit 0
else
    echo "❌ ${#failed_modules[@]} modules failed:"
    for module in "${failed_modules[@]}"; do
        echo "   - $module"
    done
    exit 1
fi

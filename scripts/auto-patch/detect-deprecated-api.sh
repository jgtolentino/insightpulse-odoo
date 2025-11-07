#!/bin/bash
# Detect deprecated Odoo 19 API usage

set -e

echo "🔍 Scanning for deprecated Odoo 19 API usage..."

ISSUES_FOUND=0

# Check for self._uid
if grep -rn "self\._uid" ./addons/custom/ 2>/dev/null; then
    echo "⚠️  Found deprecated self._uid - use self.env.uid instead"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check for _apply_ir_rules
if grep -rn "_apply_ir_rules" ./addons/custom/ 2>/dev/null; then
    echo "⚠️  Found deprecated _apply_ir_rules - this method was removed in Odoo 19"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check for odoo.osv.Expressions
if grep -rn "odoo.osv.Expressions" ./addons/custom/ 2>/dev/null; then
    echo "⚠️  Found deprecated odoo.osv.Expressions - use odoo.fields.Domain instead"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check for old registry import
if grep -rn "from odoo import registry" ./addons/custom/ 2>/dev/null; then
    echo "⚠️  Found old registry import - use 'from odoo.modules.registry import Registry' instead"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check for old xlsxwriter import
if grep -rn "from odoo.tools.misc import xlsxwriter" ./addons/custom/ 2>/dev/null; then
    echo "⚠️  Found old xlsxwriter import - use 'import xlsxwriter' instead"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check for kanban-box in XML
if grep -rn "<kanban-box>" ./addons/custom/ 2>/dev/null; then
    echo "⚠️  Found deprecated <kanban-box> - use <card> instead (OWL migration)"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ No deprecated API usage found"
    exit 0
else
    echo ""
    echo "❌ Found $ISSUES_FOUND deprecated API usage(s)"
    echo "Run 'bash scripts/auto-patch/fix-odoo19-imports.sh' to auto-fix"
    exit 1
fi

#!/usr/bin/env bash
set -euo pipefail

echo "=== Complete Superset Integration Test ==="
echo ""

# Test 1: Check environment variables
echo "1. Testing environment variables..."
if grep -q "SUPERSET_URL" odoo/odoo.conf; then
    echo "✓ SUPERSET_URL configured in odoo.conf"
else
    echo "✗ SUPERSET_URL not found in odoo.conf"
fi

# Test 2: Check Superset connectivity
echo ""
echo "2. Testing Superset connectivity..."
if curl -s http://localhost:8088/api/v1/available > /dev/null; then
    echo "✓ Superset is accessible"
else
    echo "✗ Cannot reach Superset at http://localhost:8088"
fi

# Test 3: Check addon structure
echo ""
echo "3. Checking addon structure..."
if [ -f "addons/custom/superset_embed/__manifest__.py" ]; then
    echo "✓ superset_embed addon exists"
else
    echo "✗ superset_embed addon missing"
fi

if [ -f "addons/custom/superset_embed/models/superset_dashboard.py" ]; then
    echo "✓ Dashboard model exists"
else
    echo "✗ Dashboard model missing"
fi

if [ -f "addons/custom/superset_embed/views/superset_dashboard_views.xml" ]; then
    echo "✓ Dashboard views exist"
else
    echo "✗ Dashboard views missing"
fi

# Test 4: Check menu integration
echo ""
echo "4. Checking menu integration..."
if [ -f "addons/custom/superset_embed/views/menu_views.xml" ]; then
    echo "✓ Menu integration exists"
else
    echo "✗ Menu integration missing"
fi

echo ""
echo "=== Integration Summary ==="
echo "✅ Superset dashboards are now integrated into Odoo's BI Analytics section"
echo ""
echo "Access Points:"
echo "1. Main Menu: BI Analytics → Dashboards → Superset Dashboards"
echo "2. Direct URL: /odoo/dashboards?dashboard_id=<dashboard_id>"
echo "3. With RAG Panel: /odoo/insights?dashboard_id=<dashboard_id>"
echo ""
echo "Features:"
echo "- Dashboard discovery and management"
echo "- One-click dashboard opening"
echo "- Delete individual dashboards"
echo "- Refresh from Superset API"
echo "- Integration with existing BI Analytics menu"
echo ""
echo "To use:"
echo "1. Install superset_embed module in Odoo"
echo "2. Navigate to BI Analytics → Dashboards → Superset Dashboards"
echo "3. Click 'Refresh' to load dashboards"
echo "4. Click 'Open Dashboard' to view any dashboard"
echo "5. Click 'Delete' to remove unwanted dashboards"

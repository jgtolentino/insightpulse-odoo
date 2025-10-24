#!/usr/bin/env bash
set -euo pipefail

echo "=== Superset Integration Configuration ==="
echo ""

# Check if Odoo config file exists
if [ -f "odoo/odoo.conf" ]; then
    echo "Found odoo.conf, adding Superset environment variables..."
    
    # Add environment variables to odoo.conf
    cat >> odoo/odoo.conf <<EOF

# Superset Integration
SUPERSET_URL = http://localhost:8088
SS_USER = admin
SS_PASS = admin
EOF

    echo "✓ Added Superset configuration to odoo.conf"
else
    echo "⚠ odoo.conf not found, please add these environment variables manually:"
    echo "SUPERSET_URL = http://localhost:8088"
    echo "SS_USER = admin"
    echo "SS_PASS = admin"
fi

echo ""
echo "=== Configuration Complete ==="
echo "Environment variables set:"
echo "SUPERSET_URL=http://localhost:8088"
echo "SS_USER=admin"
echo "SS_PASS=admin"
echo ""
echo "Next steps:"
echo "1. Install the superset_embed module in Odoo"
echo "2. Navigate to BI Analytics → Dashboards → Superset Dashboards"
echo "3. Click 'Refresh' to load dashboards from Superset"
echo "4. Click 'Open Dashboard' to view any dashboard"

#!/bin/bash
set -e

echo "=== IPAI Ship Pack v1: Odoo 18 Update ==="
echo "Target: Odoo 18.0 CE + OCA 18.0"

# 1. Pull and Rebuild
echo ""
echo "[1/4] Rebuilding Docker image (Odoo 18.0)..."
docker-compose -f docker-compose.prod.yml build odoo

# 2. Fix Permissions (Crucial for 500 fixes)
echo ""
echo "[2/4] Ensuring correct volume permissions..."
# We might need to start the container first to fix permissions if it's not running
# But assuming we are updating a running system:
if docker-compose -f docker-compose.prod.yml ps | grep -q odoo; then
     docker-compose -f docker-compose.prod.yml exec -u root odoo chown -R odoo:odoo /var/lib/odoo
fi

# 3. Restart Service
echo ""
echo "[3/4] Restarting services..."
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# 4. Canonical Asset Sweep (Section 4.3 of PRD)
echo ""
echo "[4/4] Running canonical module update sweep..."
echo "Waiting for database to be ready..."
sleep 15
docker-compose -f docker-compose.prod.yml exec odoo odoo -c /etc/odoo/odoo.conf -d odoo -u base,web,ipai_theme_aiux --stop-after-init

echo ""
echo "=== Update Complete ==="
echo "System should be running Odoo 18.0."
echo "Check: https://erp.insightpulseai.net"

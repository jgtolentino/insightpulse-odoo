#!/bin/bash
set -e

# Configuration
COMPOSE_FILE="docker-compose.prod.yml"
SERVICE="odoo"
DB_NAME="odoo"

echo "=== InsightPulse Odoo Fix Tool ==="
echo "Targeting compose file: $COMPOSE_FILE"

# 1. Fix Permissions
echo ""
echo "[1/3] Fixing volume permissions..."
echo "Running chown -R odoo:odoo /var/lib/odoo on container..."
docker-compose -f "$COMPOSE_FILE" exec -u root "$SERVICE" chown -R odoo:odoo /var/lib/odoo
echo "Permissions updated."

# 2. Force Asset Regeneration
echo ""
echo "[2/3] Regenerating web assets..."
echo "Updating 'web' module to force asset rebuild..."
# We use --stop-after-init to just run the update and exit
docker-compose -f "$COMPOSE_FILE" exec "$SERVICE" odoo -c /etc/odoo/odoo.conf -d "$DB_NAME" -u web --stop-after-init
echo "Assets regenerated."

# 3. Restart Service
echo ""
echo "[3/3] Restarting Odoo service..."
docker-compose -f "$COMPOSE_FILE" restart "$SERVICE"
echo "Service restarted."

echo ""
echo "=== Fix Complete ==="
echo "Please wait 30-60 seconds for the server to come back up."
echo "Then check: https://erp.insightpulseai.net/web/database/selector"

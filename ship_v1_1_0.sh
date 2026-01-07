#!/bin/bash
set -euo pipefail

: "${ODOO_DB:=odoo}"
: "${BASE_URL:=https://erp.insightpulseai.net}"
: "${COMPOSE_FILE:=docker-compose.prod.yml}"

echo "=== IPAI Ship Pack v1.1.0: Final Deployment ==="
echo "Target DB: $ODOO_DB"

# 1. Force upgrade of web + ship pack modules (Fast fix pattern)
echo ""
echo "[1/3] Force upgrading web + IPAI modules..."
docker-compose -f "$COMPOSE_FILE" exec odoo odoo -c /etc/odoo/odoo.conf -d "$ODOO_DB" -u web,ipai_theme_aiux,ipai_aiux_chat,ipai_ask_ai,ipai_document_ai,ipai_expense_ocr --stop-after-init

# 2. Restart Odoo
echo ""
echo "[2/3] Restarting Odoo service..."
docker-compose -f "$COMPOSE_FILE" restart odoo || true

# 3. Verification
echo ""
echo "[3/3] Verifying runtime..."
echo "Waiting 10s for startup..."
sleep 10

# Curl checks (if running from a machine with access, otherwise just echo instructions)
if curl -fsS "$BASE_URL/web" >/dev/null 2>&1; then
    echo "✅ /web endpoint reachable"
    curl -fsSI "$BASE_URL/web/assets/" | head -n 1
else
    echo "⚠️  Could not reach $BASE_URL automatically. Please verify manually."
fi

echo ""
echo "✅ Ship v1.1.0 sequence initiated."

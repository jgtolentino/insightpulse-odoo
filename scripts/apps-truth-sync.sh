#!/usr/bin/env bash
set -euo pipefail

# Apps Truth Sync - Force Odoo module registry to match actual deployment state
DB="${1:-odoo_prod}"

echo "🔄 Syncing Apps registry for database: $DB"

echo "📋 Step 1: Refresh module list from disk"
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d "$DB" -i base --stop-after-init

echo "🔄 Step 2: Apply pending upgrades (match DB versions with code)"
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d "$DB" -u all --stop-after-init

echo "🎨 Step 3: Build production assets (clear stale UI badges)"
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d "$DB" --dev=none --stop-after-init

echo "✅ Apps registry and versions synced for $DB"
echo ""
echo "📝 Next steps:"
echo "   1. Go to https://insightpulseai.net/apps"
echo "   2. Enable Developer mode (⋮ menu)"
echo "   3. Click 'Update Apps List'"
echo "   4. Apply any scheduled upgrades if shown"

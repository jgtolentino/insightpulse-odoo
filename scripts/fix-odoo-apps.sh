#!/bin/bash
set -e

# Fix Odoo Apps Configuration - Show Custom Modules
# This script fixes the issue where only official Odoo apps are visible
# and custom modules (ip_expense_mvp, pulser_webhook, ipai_mattermost_bridge) don't appear

echo "🔧 InsightPulse Odoo - Fix Apps Configuration"
echo "=============================================="
echo ""

# Configuration
DROPLET_IP="165.227.10.178"
DROPLET_USER="root"
DEPLOY_DIR="/opt/insightpulse-odoo"

echo "📋 Issue Identified:"
echo "  - URL: https://erp.insightpulseai.net/odoo/settings"
echo "  - Problem: Only showing official Odoo 19.0 apps"
echo "  - Missing: Custom modules (ip_expense_mvp, pulser_webhook, ipai_mattermost_bridge)"
echo ""

echo "🔍 Root Cause:"
echo "  - Odoo addons_path doesn't include /mnt/custom-addons"
echo "  - odoo.conf not mounted in docker-compose.yml"
echo "  - Custom modules not installed/visible in database"
echo ""

echo "✅ Solution:"
echo "  1. Update docker-compose.yml to mount odoo.conf"
echo "  2. Configure addons_path to include custom_addons"
echo "  3. Restart Odoo and update module list"
echo "  4. Install custom modules"
echo ""

read -p "Deploy fix to production? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 1
fi

echo ""
echo "🚀 Deploying fix..."
echo ""

# Step 1: Copy files to droplet
echo "📤 Uploading configuration files..."
scp odoo.conf ${DROPLET_USER}@${DROPLET_IP}:${DEPLOY_DIR}/
scp docker-compose.yml ${DROPLET_USER}@${DROPLET_IP}:${DEPLOY_DIR}/
scp -r custom_addons ${DROPLET_USER}@${DROPLET_IP}:${DEPLOY_DIR}/

# Step 2: Deploy on droplet
echo "🔄 Restarting Odoo with new configuration..."
ssh ${DROPLET_USER}@${DROPLET_IP} << 'ENDSSH'
cd /opt/insightpulse-odoo

# Backup current setup
echo "📦 Backing up current configuration..."
cp docker-compose.yml docker-compose.yml.backup.$(date +%Y%m%d_%H%M%S) || true

# Restart with new config
echo "🔄 Restarting Odoo..."
docker-compose down
docker-compose up -d

# Wait for Odoo to start
echo "⏳ Waiting for Odoo to start (30s)..."
sleep 30

# Update module list
echo "📋 Updating module list..."
docker-compose exec -T odoo odoo-bin -d odoo --update=all --stop-after-init --no-http

# Start Odoo normally
echo "✅ Restarting Odoo in normal mode..."
docker-compose restart odoo

echo "⏳ Waiting for Odoo to be ready (20s)..."
sleep 20

# Check status
echo "🔍 Checking Odoo status..."
docker-compose ps odoo

echo ""
echo "✅ Deployment complete!"
ENDSSH

echo ""
echo "🎯 Verification Steps:"
echo ""
echo "1. Open: https://erp.insightpulseai.net/web#action=base.open_module_tree"
echo "2. Remove any filters in the search bar"
echo "3. Search for: 'InsightPulse'"
echo "4. You should see:"
echo "   ✅ InsightPulse – Expense MVP (Mobile + Dashboard)"
echo "   ✅ Pulser Webhook"
echo "   ✅ IPAI Mattermost Bridge"
echo ""
echo "5. Install the modules:"
echo "   - Click on each module"
echo "   - Click 'Install' button"
echo "   - Wait for installation to complete"
echo ""
echo "📱 After Installation:"
echo "  - Expense MVP: Menu → InsightPulse T&E"
echo "  - Mobile UI: https://erp.insightpulseai.net/ip/mobile/receipt"
echo "  - Admin Dashboard: Menu → InsightPulse T&E → Dashboard"
echo ""
echo "🔧 Troubleshooting:"
echo "  - If modules still not visible: docker-compose exec odoo odoo-bin --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/custom-addons -d odoo --update=all --stop-after-init"
echo "  - Check logs: docker-compose logs odoo"
echo "  - Verify mount: docker-compose exec odoo ls -la /mnt/custom-addons"
echo ""
echo "✅ Fix deployment complete!"

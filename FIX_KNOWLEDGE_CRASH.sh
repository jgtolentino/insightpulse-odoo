#!/bin/bash
# Fix Knowledge Notion Clone missing client action crash
# Issue: JS file has wrong permissions (600 instead of 644)

set -e

echo "🔧 Fixing Knowledge Notion Clone crash..."

# Fix file permissions
echo "📝 Step 1: Fixing file permissions..."
ssh root@188.166.237.231 << 'ENDSSH'
cd /opt/bundle/addons/knowledge_notion_clone

# Fix permissions recursively
find . -type f -exec chmod 644 {} \;
find . -type d -exec chmod 755 {} \;

echo "✅ File permissions fixed"
echo ""
echo "📁 Current permissions:"
ls -la static/src/js/app.js
ls -la static/src/xml/app.xml
ENDSSH

# Clear assets and restart Odoo
echo ""
echo "🗑️  Step 2: Clearing asset cache..."
ssh root@188.166.237.231 << 'ENDSSH'
cd /opt/bundle

# Find and remove cached assets
docker compose exec odoo bash -c "
  find /var/lib/odoo/.local/share/Odoo/filestore -name 'web.assets_*' -delete 2>/dev/null || true
  echo '✅ Asset cache cleared'
"
ENDSSH

# Restart Odoo
echo ""
echo "🔄 Step 3: Restarting Odoo..."
ssh root@188.166.237.231 << 'ENDSSH'
cd /opt/bundle
docker compose restart odoo

# Wait for Odoo to start
echo "⏳ Waiting for Odoo to restart (30 seconds)..."
sleep 30

# Check if Odoo is running
if docker compose ps odoo | grep -q "Up"; then
  echo "✅ Odoo restarted successfully"
else
  echo "❌ Odoo failed to restart"
  docker compose logs odoo --tail=50
  exit 1
fi
ENDSSH

# Verify fix
echo ""
echo "🧪 Step 4: Verification..."
echo ""
echo "✅ Fix complete! Now test:"
echo "1. Open https://insightpulseai.net"
echo "2. Navigate to Knowledge menu"
echo "3. Verify the app loads without errors"
echo ""
echo "If the error persists, run this on the droplet:"
echo "  cd /opt/bundle"
echo "  docker compose exec odoo odoo -d odoo -u knowledge_notion_clone --stop-after-init"
echo "  docker compose restart odoo"

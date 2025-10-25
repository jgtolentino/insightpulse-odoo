#!/usr/bin/env bash
set -euo pipefail

# do-cli API deployment script
# Uses the do-cli API at https://do.chiro.work or https://do-cli.deta.dev

DROPLET_NAME="${1:-insightpulse-odoo}"
DO_CLI_API="${DO_CLI_API:-https://do-cli.deta.dev}"

echo "🚀 Deploying to droplet: $DROPLET_NAME via do-cli API"

# Get droplet information
echo "📡 Getting droplet information..."
DROPLET_INFO=$(curl -fsS "$DO_CLI_API/droplets/$DROPLET_NAME" || echo "{}")

if [ "$DROPLET_INFO" = "{}" ]; then
    echo "❌ Droplet '$DROPLET_NAME' not found or API unavailable"
    exit 1
fi

# Extract IP address from droplet info
DROPLET_IP=$(echo "$DROPLET_INFO" | jq -r '.ip_address // empty')

if [ -z "$DROPLET_IP" ]; then
    echo "❌ Could not extract IP address from droplet info"
    echo "Droplet info: $DROPLET_INFO"
    exit 1
fi

echo "✅ Found droplet at IP: $DROPLET_IP"

# Deploy using SSH (direct Docker registry approach)
echo "📦 Deploying application via Docker registry..."

# SSH deployment commands
ssh -o StrictHostKeyChecking=no root@$DROPLET_IP << 'EOF'
set -e
cd ~/insightpulse-odoo

echo "🐳 Pulling latest Docker images..."
docker compose pull odoo

echo "🚀 Restarting services with new images..."
docker compose up -d --force-recreate odoo

echo "🔄 Updating Odoo modules..."
DB="odoo"
docker compose exec -T odoo odoo shell -d "$DB" << 'PY'
env['ir.module.module'].update_list()
PY

echo "🔄 Upgrading all modules..."
docker compose exec -T odoo odoo -c /etc/odoo/odoo.conf -d "$DB" -u all --stop-after-init

echo "✅ Docker registry deployment completed successfully!"
EOF

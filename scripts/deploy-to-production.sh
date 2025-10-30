#!/usr/bin/env bash
set -euo pipefail

# Production deployment script for insightpulseai.net
DROPLET_HOST="188.166.237.231"
DROPLET_USER="root"
ODOO_DB="odoo"

echo "🚀 Deploying InsightPulse Odoo to production: $DROPLET_HOST"

# Deploy using SSH
ssh -o StrictHostKeyChecking=no $DROPLET_USER@$DROPLET_HOST << 'EOF'
set -e

echo "📁 Setting up insightpulse-odoo directory..."
mkdir -p ~/insightpulse-odoo
cd ~/insightpulse-odoo

# Clone or update repository
if [ ! -d ".git" ]; then
    echo "📦 Cloning repository..."
    git clone https://github.com/jgtolentino/insightpulse-odoo.git .
else
    echo "🔄 Pulling latest changes..."
    git pull origin main
fi

echo "🐳 Setting up Docker services..."
# Stop and remove any existing containers to avoid conflicts
docker compose down 2>/dev/null || true
docker compose pull odoo
docker compose up -d --force-recreate odoo

echo "🔄 Updating Odoo modules..."
DB="odoo"
docker compose exec -T odoo odoo shell -d "$DB" << 'PY'
env['ir.module.module'].update_list()
PY

echo "🔄 Upgrading all modules..."
docker compose exec -T odoo odoo -c /etc/odoo/odoo.conf -d "$DB" -u all --stop-after-init

echo "✅ Production deployment completed successfully!"
echo "🌐 Odoo should be available at: http://$DROPLET_HOST:8069"
EOF

echo "🎉 Deployment to production completed!"
echo "📊 Check services: ssh root@$DROPLET_HOST 'cd ~/insightpulse-odoo && docker compose ps'"
echo "📝 View logs: ssh root@$DROPLET_HOST 'cd ~/insightpulse-odoo && docker compose logs odoo'"

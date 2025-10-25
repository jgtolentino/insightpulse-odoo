#!/bin/bash

# Development server with live reload for Odoo
# This script sets up a development environment with live reload capabilities

set -e

echo "🚀 Starting Odoo Development Server with Live Reload"
echo "=================================================="

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p config

# Create Odoo development configuration
cat > config/odoo.conf << EOF
[options]
addons_path = /mnt/extra-addons
data_dir = /var/lib/odoo
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
http_port = 8069
longpolling_port = 8072
workers = 0
max_cron_threads = 0
dev_mode = all
log_level = debug
logfile = /var/log/odoo/odoo.log
proxy_mode = True
EOF

echo "✅ Configuration created"

# Start development environment
echo "🐳 Starting development containers..."
docker compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check if Odoo is running
if curl -f http://localhost:8069 >/dev/null 2>&1; then
    echo "✅ Odoo is running at http://localhost:8069"
else
    echo "⚠️  Odoo is starting up, please wait a moment..."
fi

# Check if live server is running
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Live reload server is running at http://localhost:3000"
else
    echo "⚠️  Live reload server is starting up..."
fi

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📱 Access points:"
echo "   • Odoo: http://localhost:8069"
echo "   • Live Reload: http://localhost:3000"
echo "   • File Watcher: http://localhost:3001"
echo ""
echo "🔧 Development features:"
echo "   • Auto-reload on file changes"
echo "   • Debug mode enabled"
echo "   • Static file serving with live reload"
echo "   • Hot reload for addons"
echo ""
echo "📝 Useful commands:"
echo "   • View logs: docker compose -f docker-compose.dev.yml logs -f odoo"
echo "   • Stop: docker compose -f docker-compose.dev.yml down"
echo "   • Restart: docker compose -f docker-compose.dev.yml restart odoo"
echo ""
echo "🔄 Live reload is active - changes to your addons will be automatically detected!"

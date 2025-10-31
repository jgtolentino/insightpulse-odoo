#!/bin/bash
set -e

echo "🚀 Starting Superset single container..."

# Wait for Redis to be ready (started by supervisor)
echo "⏳ Waiting for Redis..."
sleep 5

# Initialize Superset database
echo "🔧 Initializing Superset database..."
superset db upgrade

# Create admin user if not exists
echo "👤 Creating admin user..."
superset fab create-admin \
    --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
    --firstname "${SUPERSET_ADMIN_FIRST_NAME:-Admin}" \
    --lastname "${SUPERSET_ADMIN_LAST_NAME:-User}" \
    --email "${SUPERSET_ADMIN_EMAIL:-admin@insightpulseai.net}" \
    --password "${SUPERSET_ADMIN_PASSWORD}" || echo "Admin user already exists"

# Initialize Superset
echo "🎨 Initializing Superset..."
superset init

echo "✅ Initialization complete"
echo "🌐 Starting Supervisor (Redis + Superset)..."

# Start supervisor (which starts Redis and Superset)
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

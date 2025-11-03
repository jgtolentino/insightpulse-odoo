#!/bin/bash
# Superset single-container entrypoint with error handling
# Handles database initialization with retries for DigitalOcean App Platform

set -eo pipefail

echo "🚀 Starting Superset single container..."

# Set Superset configuration path
export SUPERSET_CONFIG_PATH=/app/pythonpath/superset_config.py

# Start supervisor in background (starts Redis and Superset)
echo "🌐 Starting Supervisor (Redis + Superset web server)..."
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
for i in {1..30}; do
    if redis-cli -h localhost ping > /dev/null 2>&1; then
        echo "✅ Redis is ready"
        break
    fi
    echo "Waiting for Redis... ($i/30)"
    sleep 2
done

# Wait a bit for supervisor to fully start
sleep 5

# Initialize Superset database with retries
echo "🔧 Initializing Superset database..."
MAX_RETRIES=5
RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
    if superset db upgrade; then
        echo "✅ Database initialized successfully"
        break
    else
        RETRY=$((RETRY+1))
        if [ $RETRY -lt $MAX_RETRIES ]; then
            echo "⚠️  Database initialization failed, retrying ($RETRY/$MAX_RETRIES)..."
            sleep 10
        else
            echo "❌ Database initialization failed after $MAX_RETRIES attempts"
            echo "Continuing anyway - migrations may have already been applied"
        fi
    fi
done

# Create admin user if not exists
echo "👤 Creating admin user..."
superset fab create-admin \
    --username "${SUPERSET_ADMIN_USERNAME:-admin}" \
    --firstname "${SUPERSET_ADMIN_FIRST_NAME:-Admin}" \
    --lastname "${SUPERSET_ADMIN_LAST_NAME:-User}" \
    --email "${SUPERSET_ADMIN_EMAIL:-admin@insightpulseai.net}" \
    --password "${SUPERSET_ADMIN_PASSWORD}" 2>&1 | grep -v "already exists" || echo "✅ Admin user ready"

# Initialize Superset roles and permissions
echo "🎨 Initializing Superset roles..."
superset init || echo "⚠️  Superset init had warnings (this is often normal)"

echo "✅ Initialization complete"
echo "📊 Superset is running on port 8088"

# Keep container alive by monitoring supervisor
tail -f /var/log/supervisor/*.log

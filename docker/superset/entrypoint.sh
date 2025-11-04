#!/bin/bash
# Apache Superset Production Entrypoint
# Handles database initialization, migrations, and application startup

set -e

echo "========================================="
echo "Apache Superset Production Deployment"
echo "========================================="

# Function to wait for database
wait_for_db() {
    echo "Waiting for PostgreSQL database..."
    until PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -d "$DATABASE_DB" -c '\q' 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    echo "✓ PostgreSQL is ready"
}

# Function to wait for Redis
wait_for_redis() {
    echo "Waiting for Redis..."
    until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null; do
        echo "Redis is unavailable - sleeping"
        sleep 2
    done
    echo "✓ Redis is ready"
}

# Wait for dependencies
wait_for_db
wait_for_redis

echo "========================================="
echo "Database Migration and Initialization"
echo "========================================="

# Verify database connection configuration
echo "Database Configuration Check:"
python3 -c "
import os
db_uri = f\"postgresql+psycopg2://{os.getenv('DATABASE_USER')}:***@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_DB')}\"
print(f'  SQLALCHEMY_DATABASE_URI: {db_uri}')
print(f'  Config file: /app/pythonpath/superset_config.py')
"

# Verify config file exists
if [ ! -f /app/pythonpath/superset_config.py ]; then
    echo "❌ ERROR: superset_config.py not found!"
    exit 1
fi

# Initialize database (if not already initialized)
echo "Running database upgrade..."
if ! superset db upgrade; then
    echo "❌ Database upgrade failed!"
    echo "Attempting to reset metadata database..."

    # Drop all tables and recreate (only safe on first deploy)
    python3 -c "
from superset import db
from superset.app import create_app

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
"

    # Retry upgrade
    superset db upgrade || exit 1
fi

# Create default roles and permissions
superset init

# Create admin user if it doesn't exist
echo "Checking for admin user..."
if ! superset fab list-users | grep -q "$SUPERSET_ADMIN_USERNAME"; then
    echo "Creating admin user: $SUPERSET_ADMIN_USERNAME"
    superset fab create-admin \
        --username "$SUPERSET_ADMIN_USERNAME" \
        --firstname "$SUPERSET_ADMIN_FIRST_NAME" \
        --lastname "$SUPERSET_ADMIN_LAST_NAME" \
        --email "$SUPERSET_ADMIN_EMAIL" \
        --password "$SUPERSET_ADMIN_PASSWORD"
    echo "✓ Admin user created"
else
    echo "✓ Admin user already exists"
fi

# Load examples if enabled (typically disabled in production)
if [ "$SUPERSET_LOAD_EXAMPLES" = "yes" ]; then
    echo "Loading example data..."
    superset load_examples
    echo "✓ Examples loaded"
fi

echo "========================================="
echo "Starting Apache Superset"
echo "========================================="

# Get Gunicorn configuration from environment variables
WORKERS=${SUPERSET_WORKERS:-4}
WORKER_CLASS=${SUPERSET_WORKER_CLASS:-gevent}
WORKER_CONNECTIONS=${SUPERSET_WORKER_CONNECTIONS:-1000}
TIMEOUT=${SUPERSET_TIMEOUT:-120}
MAX_REQUESTS=${SUPERSET_MAX_REQUESTS:-5000}
MAX_REQUESTS_JITTER=${SUPERSET_MAX_REQUESTS_JITTER:-500}

echo "Configuration:"
echo "  Workers: $WORKERS"
echo "  Worker class: $WORKER_CLASS"
echo "  Worker connections: $WORKER_CONNECTIONS"
echo "  Timeout: ${TIMEOUT}s"
echo "  Max requests: $MAX_REQUESTS"
echo "  Max requests jitter: $MAX_REQUESTS_JITTER"
echo "  Application root: $SUPERSET_APP_ROOT"
echo "  Base URL: $SUPERSET_WEBSERVER_PROTOCOL://insightpulseai.net$SUPERSET_APP_ROOT/"

# Start Gunicorn with production settings
exec gunicorn \
    --workers "$WORKERS" \
    --worker-class "$WORKER_CLASS" \
    --worker-connections "$WORKER_CONNECTIONS" \
    --timeout "$TIMEOUT" \
    --bind "0.0.0.0:${SUPERSET_WEBSERVER_PORT}" \
    --max-requests "$MAX_REQUESTS" \
    --max-requests-jitter "$MAX_REQUESTS_JITTER" \
    --access-logfile - \
    --error-logfile - \
    --log-level "${SUPERSET_LOG_LEVEL:-warning}" \
    "superset.app:create_app()"

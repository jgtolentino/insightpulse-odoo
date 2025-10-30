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

# Initialize database (if not already initialized)
superset db upgrade

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

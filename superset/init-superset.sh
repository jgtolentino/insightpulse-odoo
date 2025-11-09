#!/bin/bash
# Superset initialization script
# Runs database migrations, creates admin user, and initializes Superset

set -eo pipefail

echo "🚀 Starting Superset initialization..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until PGPASSWORD=$DATABASE_PASSWORD psql -h "$DATABASE_HOST" -U "$DATABASE_USER" -d "$DATABASE_DB" -c '\q' 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done
echo "✅ PostgreSQL is ready"

# Wait for Redis to be ready
echo "⏳ Waiting for Redis..."
until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" ping 2>/dev/null | grep -q PONG; do
  echo "Redis is unavailable - sleeping"
  sleep 2
done
echo "✅ Redis is ready"

# Run database migrations
echo "🔄 Running Superset database migrations..."
superset db upgrade

# Create admin user if it doesn't exist
echo "👤 Creating admin user..."
superset fab create-admin \
  --username "${ADMIN_USERNAME:-admin}" \
  --firstname "${ADMIN_FIRSTNAME:-Admin}" \
  --lastname "${ADMIN_LASTNAME:-User}" \
  --email "${ADMIN_EMAIL:-admin@insightpulseai.net}" \
  --password "${ADMIN_PASSWORD:-admin}" || echo "Admin user already exists"

# Initialize Superset (creates default roles and permissions)
echo "🔐 Initializing Superset roles and permissions..."
superset init

# Import Odoo datasource if configuration exists
if [ -f "/app/config/odoo-datasource.yaml" ]; then
  echo "📊 Importing Odoo datasource..."
  superset import-datasources -p /app/config/odoo-datasource.yaml || echo "Datasource import failed or already exists"
fi

# Load example dashboards for Finance SSC (optional)
if [ "${LOAD_EXAMPLES:-no}" = "yes" ]; then
  echo "📈 Loading example dashboards..."
  superset load-examples || echo "Examples load failed"
fi

# Create custom Odoo database connection
echo "🔌 Creating Odoo database connection..."
python3 << 'PYEOF'
import os
from superset import db, app
from superset.models.core import Database

# Create application context
application = app.create_app()
with application.app_context():
    # Check if Odoo database already exists
    odoo_db = db.session.query(Database).filter_by(database_name='Odoo Production').first()

    if not odoo_db:
        # Create Odoo datasource
        odoo_uri = os.getenv('ODOO_DATABASE_URI', 'postgresql://postgres:postgres@postgres:5432/odoo')

        odoo_database = Database(
            database_name='Odoo Production',
            sqlalchemy_uri=odoo_uri,
            expose_in_sqllab=True,
            allow_csv_upload=True,
            allow_ctas=True,
            allow_cvas=True,
            allow_dml=False,  # Prevent data modifications
        )

        db.session.add(odoo_database)
        db.session.commit()

        print("✅ Odoo datasource created successfully!")
    else:
        print("ℹ️  Odoo datasource already exists")
PYEOF

echo "✨ Superset initialization complete!"
echo "🌐 Starting Superset on port 8088..."

# Start Superset
exec gunicorn \
  --bind 0.0.0.0:8088 \
  --workers ${SUPERSET_WORKERS:-4} \
  --worker-class gevent \
  --threads ${SUPERSET_THREADS:-4} \
  --timeout ${SUPERSET_TIMEOUT:-120} \
  --limit-request-line 0 \
  --limit-request-field_size 0 \
  --statsd-host localhost:8125 \
  "superset.app:create_app()"

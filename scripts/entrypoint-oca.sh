#!/bin/bash
# Entrypoint script for Odoo 19 with OCA modules
# InsightPulse AI Finance SSC Edition

set -e

# Environment variables with defaults
ODOO_RC=${ODOO_RC:-/etc/odoo/odoo.conf}
DB_ARGS=()

function check_postgres() {
    echo "Waiting for PostgreSQL..."
    until PGPASSWORD="$PGPASSWORD" psql -h "$PGHOST" -U "$PGUSER" -d postgres -c '\q' 2>/dev/null; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 1
    done
    echo "PostgreSQL is up!"
}

function check_redis() {
    echo "Waiting for Redis..."
    until redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" -a "$REDIS_PASSWORD" --no-auth-warning ping 2>/dev/null; do
        echo "Redis is unavailable - sleeping"
        sleep 1
    done
    echo "Redis is up!"
}

function initialize_database() {
    echo "Checking if database needs initialization..."
    if [ "$AUTO_INIT_DB" = "true" ]; then
        DB_EXISTS=$(PGPASSWORD="$PGPASSWORD" psql -h "$PGHOST" -U "$PGUSER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$PGDATABASE'")

        if [ "$DB_EXISTS" != "1" ]; then
            echo "Creating database $PGDATABASE..."
            PGPASSWORD="$PGPASSWORD" psql -h "$PGHOST" -U "$PGUSER" -d postgres -c "CREATE DATABASE $PGDATABASE ENCODING 'UTF8' TEMPLATE template0"

            # Initialize Odoo database
            echo "Initializing Odoo database with base modules..."
            DB_ARGS+=("-i" "base,web")

            # Install OCA core modules if specified
            if [ -n "$OCA_CORE_MODULES" ]; then
                echo "Installing OCA core modules: $OCA_CORE_MODULES"
                DB_ARGS+=("-i" "$OCA_CORE_MODULES")
            fi
        fi
    fi
}

function setup_odoo_config() {
    if [ ! -f "$ODOO_RC" ]; then
        echo "Generating Odoo configuration file..."
        cat > "$ODOO_RC" <<EOF
[options]
; Database configuration
db_host = ${PGHOST:-db}
db_port = ${PGPORT:-5432}
db_user = ${PGUSER:-odoo}
db_password = ${PGPASSWORD}
db_name = ${PGDATABASE:-odoo19}
db_maxconn = ${ODOO_DB_MAXCONN:-128}
db_template = template0

; Server configuration
admin_passwd = ${ODOO_ADMIN_PASSWORD}
http_port = 8069
longpolling_port = 8072
workers = ${ODOO_WORKERS:-8}
max_cron_threads = ${ODOO_MAX_CRON_THREADS:-2}

; Memory limits
limit_memory_hard = ${ODOO_LIMIT_MEMORY_HARD:-4294967296}
limit_memory_soft = ${ODOO_LIMIT_MEMORY_SOFT:-3435973836}
limit_time_cpu = ${ODOO_LIMIT_TIME_CPU:-300}
limit_time_real = ${ODOO_LIMIT_TIME_REAL:-600}
limit_time_real_cron = ${ODOO_LIMIT_TIME_REAL_CRON:-7200}

; Addons path
addons_path = /opt/odoo/addons,/mnt/extra-addons/oca,/mnt/extra-addons/custom,/mnt/extra-addons/insightpulse

; Server-wide modules
server_wide_modules = ${ODOO_SERVER_WIDE_MODULES:-base,web}

; Logging
logfile = /var/log/odoo/odoo.log
log_level = ${ODOO_LOG_LEVEL:-info}

; Security
proxy_mode = ${ODOO_PROXY_MODE:-True}
db_filter = ${ODOO_DB_FILTER:-^%d$}
list_db = ${ODOO_LIST_DB:-False}

; Session store (Redis)
session_store_db = redis
session_store_dbtable = session
session_store_prefix = odoo_session_
session_store_connect_string = redis://:${REDIS_PASSWORD:-}@${REDIS_HOST:-redis}:${REDIS_PORT:-6379}/1

; Gevent mode (for better performance)
gevent_port = 8072

; Email configuration (optional)
; email_from = ${EMAIL_FROM:-odoo@insightpulse.ai}
; smtp_server = ${SMTP_SERVER:-localhost}
; smtp_port = ${SMTP_PORT:-25}
; smtp_user = ${SMTP_USER:-}
; smtp_password = ${SMTP_PASSWORD:-}
; smtp_ssl = ${SMTP_SSL:-False}

; Data directory
data_dir = /var/lib/odoo
EOF
        echo "Configuration file created at $ODOO_RC"
    fi
}

function install_oca_modules() {
    echo "Checking OCA module availability..."

    # List available OCA modules
    if [ -d "/mnt/extra-addons/oca" ]; then
        echo "OCA modules found:"
        ls -1 /mnt/extra-addons/oca | head -10
        echo "..."
    else
        echo "Warning: OCA modules directory not found!"
    fi
}

function main() {
    echo "=== InsightPulse Odoo OCA Entrypoint ==="
    echo "Odoo Version: 19.0"
    echo "Edition: Finance SSC with OCA Modules"

    # Check dependencies
    if [ -n "$PGHOST" ]; then
        check_postgres
    fi

    if [ -n "$REDIS_HOST" ]; then
        check_redis
    fi

    # Setup configuration
    setup_odoo_config

    # Initialize database if needed
    initialize_database

    # Check OCA modules
    install_oca_modules

    echo "=== Starting Odoo ==="
    echo "Command: $@"

    # Execute the command
    if [ "${DB_ARGS[*]}" ]; then
        exec "$@" "${DB_ARGS[@]}"
    else
        exec "$@"
    fi
}

main "$@"

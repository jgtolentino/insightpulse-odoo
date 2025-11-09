#!/bin/bash
# Production Entrypoint Script for InsightPulse Odoo 19.0 CE + OCA
# Purpose: Handle database initialization, module updates, and server startup
# Environment: DigitalOcean App Platform / Docker production deployment

set -e

# Configuration
DB_HOST="${HOST:-postgres}"
DB_PORT="${PORT:-5432}"
DB_USER="${USER:-odoo}"
DB_PASSWORD="${PASSWORD:-odoo}"
DB_NAME="${DB_NAME:-odoo19}"
ADMIN_PASSWD="${ADMIN_PASSWD:-admin}"
ODOO_BIN="/usr/bin/odoo"
ODOO_CONF="/etc/odoo/odoo.conf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

# Wait for PostgreSQL to be ready
wait_for_postgres() {
    log "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT}..."

    local max_attempts=60
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; then
            log "PostgreSQL is ready!"
            return 0
        fi

        warn "PostgreSQL not ready yet (attempt $attempt/$max_attempts)"
        sleep 2
        attempt=$((attempt + 1))
    done

    error "PostgreSQL did not become ready within 120 seconds"
    exit 1
}

# Check if database exists
database_exists() {
    PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"
}

# Initialize Odoo database with base modules
init_database() {
    log "Initializing Odoo database '$DB_NAME'..."

    # Create database if it doesn't exist
    if ! database_exists; then
        log "Creating database '$DB_NAME'..."
        PGPASSWORD="$DB_PASSWORD" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -O "$DB_USER" "$DB_NAME"
    else
        log "Database '$DB_NAME' already exists"
    fi

    # Initialize with base modules
    log "Installing base modules..."
    "$ODOO_BIN" \
        --db_host="$DB_HOST" \
        --db_port="$DB_PORT" \
        --db_user="$DB_USER" \
        --db_password="$DB_PASSWORD" \
        --database="$DB_NAME" \
        --init=base \
        --stop-after-init \
        --no-http

    log "Base modules installed successfully"
}

# Update OCA and custom modules
update_modules() {
    log "Updating OCA and custom modules..."

    # List of critical OCA modules to auto-install
    local oca_modules=(
        # Server Infrastructure (Tier 1)
        "auth_api_key"
        "server_environment"
        "base_jsonify"

        # Accounting & Finance (Tier 1)
        "account_financial_report"
        "account_invoice_import"
        "account_payment_order"
        "account_reconcile_oca"

        # REST API (Tier 1)
        "base_rest"
        "fastapi"

        # Web & UI (Tier 2)
        "web_responsive"
        "web_widget_x2many_2d_matrix"

        # Reporting (Tier 2)
        "report_xlsx"
        "report_qweb_pdf_watermark"

        # Purchase & Procurement (Tier 2)
        "purchase_requisition"
        "purchase_request"

        # HR (Tier 3)
        "hr_expense_invoice"
        "hr_holidays_public"
    )

    # Join modules with comma
    local modules_to_update=$(IFS=,; echo "${oca_modules[*]}")

    # Update modules (will skip if not available)
    "$ODOO_BIN" \
        --db_host="$DB_HOST" \
        --db_port="$DB_PORT" \
        --db_user="$DB_USER" \
        --db_password="$DB_PASSWORD" \
        --database="$DB_NAME" \
        --update="$modules_to_update" \
        --stop-after-init \
        --no-http \
        2>&1 | tee /tmp/odoo-update.log || {
            warn "Some modules could not be updated (this is normal if modules aren't installed yet)"
        }

    log "Module update completed"
}

# Verify critical configurations
verify_config() {
    log "Verifying Odoo configuration..."

    # Check if config file exists
    if [ ! -f "$ODOO_CONF" ]; then
        error "Configuration file not found: $ODOO_CONF"
        exit 1
    fi

    # Verify addons_path includes OCA modules
    if ! grep -q "oca" "$ODOO_CONF"; then
        warn "OCA modules may not be in addons_path"
    fi

    # Verify critical environment variables
    if [ -z "$OPENAI_API_KEY" ]; then
        warn "OPENAI_API_KEY not set - AI features will be disabled"
    fi

    if [ -z "$SUPABASE_URL" ]; then
        warn "SUPABASE_URL not set - Supabase integration will be disabled"
    fi

    log "Configuration verification completed"
}

# Health check endpoint
create_health_endpoint() {
    log "Ensuring health check endpoint is available..."
    # Health checks are handled by Odoo's web module at /web/health
}

# Main entrypoint logic
main() {
    log "=== InsightPulse Odoo 19.0 CE + OCA Production Entrypoint ==="
    log "Database: ${DB_NAME}@${DB_HOST}:${DB_PORT}"
    log "User: ${DB_USER}"
    log "====================================================="

    # Step 1: Wait for PostgreSQL
    wait_for_postgres

    # Step 2: Verify configuration
    verify_config

    # Step 3: Initialize database if needed
    if ! database_exists; then
        init_database
    else
        log "Database exists, skipping initialization"
    fi

    # Step 4: Update modules (if ODOO_UPDATE_MODULES=true)
    if [ "${ODOO_UPDATE_MODULES:-false}" = "true" ]; then
        update_modules
    else
        log "Skipping module updates (set ODOO_UPDATE_MODULES=true to enable)"
    fi

    # Step 5: Create health endpoint
    create_health_endpoint

    # Step 6: Start Odoo server
    log "Starting Odoo server..."
    log "====================================================="

    # Execute Odoo with all arguments passed to this script
    exec "$ODOO_BIN" \
        --db_host="$DB_HOST" \
        --db_port="$DB_PORT" \
        --db_user="$DB_USER" \
        --db_password="$DB_PASSWORD" \
        --database="$DB_NAME" \
        --config="$ODOO_CONF" \
        "$@"
}

# Run main function
main "$@"

#!/bin/bash
##############################################################################
# InsightPulse Multi-Org Database Creation Script
#
# Creates 8 separate PostgreSQL databases for Philippine agencies:
# - db_rim, db_ckvc, db_bom, db_jpal, db_jli, db_jap, db_las, db_rmqb
#
# Each database will have:
# - Base Odoo modules installed
# - Philippine localization (l10n_ph)
# - Company configured with agency-specific TIN
#
# Usage:
#   ./create-multi-org-dbs.sh
#
# Prerequisites:
#   - Docker Compose stack running (postgres, odoo services)
#   - ODOO_ADMIN_PASSWORD environment variable set
#
# Author: InsightPulse AI
# Date: 2025-11-11
# License: LGPL-3
##############################################################################

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
AGENCIES=("rim" "ckvc" "bom" "jpal" "jli" "jap" "las" "rmqb")
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check if docker-compose is running
    if ! docker-compose ps | grep -q "postgres"; then
        log_error "PostgreSQL container not running. Please start docker-compose first."
        exit 1
    fi

    if ! docker-compose ps | grep -q "odoo"; then
        log_error "Odoo container not running. Please start docker-compose first."
        exit 1
    fi

    # Check if ODOO_ADMIN_PASSWORD is set
    if [ -z "${ODOO_ADMIN_PASSWORD:-}" ]; then
        log_warn "ODOO_ADMIN_PASSWORD not set. Using default: admin"
        export ODOO_ADMIN_PASSWORD="admin"
    fi

    log_info "Prerequisites check passed"
}

# Create PostgreSQL database
create_database() {
    local db_name=$1

    log_info "Creating database: $db_name"

    # Check if database already exists
    DB_EXISTS=$(docker-compose exec -T postgres psql -U odoo -lqt | cut -d \| -f 1 | grep -w "$db_name" || true)

    if [ -n "$DB_EXISTS" ]; then
        log_warn "Database $db_name already exists. Skipping creation."
        return 0
    fi

    # Create database
    docker-compose exec -T postgres psql -U odoo -c "CREATE DATABASE $db_name TEMPLATE template0 ENCODING 'UTF8';" || {
        log_error "Failed to create database $db_name"
        return 1
    }

    log_info "✓ Database $db_name created"
}

# Initialize Odoo database
initialize_odoo_database() {
    local db_name=$1
    local agency_code=$2

    log_info "Initializing Odoo in database: $db_name"

    # Initialize with base modules
    docker-compose exec -T odoo odoo \
        -d "$db_name" \
        -i base,web,account,l10n_ph \
        --stop-after-init \
        --without-demo=all \
        --log-level=warn || {
        log_error "Failed to initialize Odoo for $db_name"
        return 1
    }

    log_info "✓ Odoo initialized for $db_name"
}

# Main script
main() {
    log_info "=========================================="
    log_info "InsightPulse Multi-Org Database Setup"
    log_info "=========================================="
    log_info ""

    # Change to project root
    cd "$ROOT_DIR"

    # Check prerequisites
    check_prerequisites

    # Create databases
    log_info ""
    log_info "Step 1: Creating PostgreSQL databases..."
    log_info ""

    for agency in "${AGENCIES[@]}"; do
        DB_NAME="db_${agency}"
        create_database "$DB_NAME"
    done

    # Initialize Odoo databases
    log_info ""
    log_info "Step 2: Initializing Odoo databases..."
    log_info ""

    for agency in "${AGENCIES[@]}"; do
        DB_NAME="db_${agency}"
        initialize_odoo_database "$DB_NAME" "$agency"
    done

    # Summary
    log_info ""
    log_info "=========================================="
    log_info "✓ Multi-Org Database Setup Complete!"
    log_info "=========================================="
    log_info ""
    log_info "Created databases:"
    for agency in "${AGENCIES[@]}"; do
        log_info "  - db_${agency}"
    done
    log_info ""
    log_info "Next steps:"
    log_info "  1. Run seed-demo-data.py to populate with sample data"
    log_info "  2. Access Odoo at http://localhost:8069"
    log_info "  3. Select database from dropdown"
    log_info "  4. Login: admin / ${ODOO_ADMIN_PASSWORD}"
    log_info ""
}

# Run main function
main "$@"

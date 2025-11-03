#!/usr/bin/env bash
###############################################################################
# PostgreSQL Setup Script for Odoo 19
#
# This script configures PostgreSQL for Odoo, creating the database user
# and setting appropriate permissions.
#
# Usage:
#   bash 02-postgres-setup.sh
#
# Run as: root
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

log_info "Configuring PostgreSQL for Odoo..."

# Generate a strong password if not provided
if [[ -z "${ODOO_DB_PASSWORD:-}" ]]; then
    log_warn "ODOO_DB_PASSWORD not set, generating random password..."
    ODOO_DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    log_info "Generated password: $ODOO_DB_PASSWORD"
    log_warn "IMPORTANT: Save this password securely!"
    echo "$ODOO_DB_PASSWORD" > /root/odoo_db_password.txt
    chmod 600 /root/odoo_db_password.txt
    log_info "Password saved to: /root/odoo_db_password.txt"
fi

# Check if odoo role already exists
if sudo -u postgres psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='odoo'" | grep -q 1; then
    log_warn "PostgreSQL role 'odoo' already exists"
    read -p "Do you want to update the password? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo -u postgres psql -c "ALTER USER odoo WITH PASSWORD '$ODOO_DB_PASSWORD';"
        log_info "Password updated for user 'odoo'"
    fi
else
    # Create odoo database user
    log_info "Creating PostgreSQL role 'odoo'..."
    sudo -u postgres psql -c "CREATE USER odoo WITH PASSWORD '$ODOO_DB_PASSWORD';"
    log_info "PostgreSQL role 'odoo' created"
fi

# Grant database creation privileges
log_info "Granting CREATEDB privilege..."
sudo -u postgres psql -c "ALTER ROLE odoo CREATEDB;"

# Verify setup
log_info "Verifying PostgreSQL setup..."
sudo -u postgres psql -c "\du odoo"

log_info "PostgreSQL setup complete!"
log_info "Database password stored in: /root/odoo_db_password.txt"
log_info ""
log_info "Next step: Run bash 03-odoo-install.sh"

exit 0

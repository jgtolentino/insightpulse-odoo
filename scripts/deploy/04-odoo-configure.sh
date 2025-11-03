#!/usr/bin/env bash
###############################################################################
# Odoo 19 Configuration Script
#
# This script creates the Odoo configuration file with production settings.
#
# Usage:
#   bash 04-odoo-configure.sh
#
# Run as: odoo user
# Environment variables:
#   ODOO_DB_PASSWORD - PostgreSQL password for odoo user
#   ODOO_MASTER_PASSWORD - Odoo master/admin password
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

# Check if running as odoo user
if [[ $(whoami) != "odoo" ]]; then
   log_error "This script must be run as the 'odoo' user"
   log_info "Run: sudo su - odoo"
   exit 1
fi

ODOO_HOME="/home/odoo"
CONFIG_FILE="$ODOO_HOME/etc/odoo.conf"

# Read DB password if available
if [[ -f "/root/odoo_db_password.txt" ]] && [[ -z "${ODOO_DB_PASSWORD:-}" ]]; then
    log_warn "Reading database password from /root/odoo_db_password.txt"
    log_warn "Run this script with: sudo -u odoo -E bash 04-odoo-configure.sh"
    exit 1
fi

# Generate master password if not provided
if [[ -z "${ODOO_MASTER_PASSWORD:-}" ]]; then
    log_warn "ODOO_MASTER_PASSWORD not set, generating random password..."
    ODOO_MASTER_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    log_info "Generated master password: $ODOO_MASTER_PASSWORD"
    log_warn "IMPORTANT: Save this password securely!"
    echo "$ODOO_MASTER_PASSWORD" > "$ODOO_HOME/master_password.txt"
    chmod 600 "$ODOO_HOME/master_password.txt"
    log_info "Master password saved to: $ODOO_HOME/master_password.txt"
fi

# Validate DB password
if [[ -z "${ODOO_DB_PASSWORD:-}" ]]; then
    log_error "ODOO_DB_PASSWORD not set"
    log_info "Run: ODOO_DB_PASSWORD=<password> bash 04-odoo-configure.sh"
    exit 1
fi

log_info "Creating Odoo configuration file..."

# Backup existing config if present
if [[ -f "$CONFIG_FILE" ]]; then
    log_warn "Configuration file already exists, creating backup..."
    cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d-%H%M%S)"
fi

# Create configuration file
cat > "$CONFIG_FILE" <<EOF
[options]
# Paths
addons_path = $ODOO_HOME/addons,$ODOO_HOME/src/odoo/addons
data_dir = $ODOO_HOME/data
logfile = $ODOO_HOME/logs/odoo.log

# Database
db_host = 127.0.0.1
db_port = 5432
db_user = odoo
db_password = $ODOO_DB_PASSWORD
db_maxconn = 64
db_template = template0

# Security
admin_passwd = $ODOO_MASTER_PASSWORD
list_db = False

# Performance
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 600
limit_time_real = 1200
limit_time_real_cron = 300

# Longpolling
longpolling_port = 8072

# Proxy mode
proxy_mode = True

# Logging
log_level = info
log_handler = :INFO

# Misc
server_wide_modules = base,web
EOF

# Set proper permissions
chmod 600 "$CONFIG_FILE"

log_info "Configuration file created: $CONFIG_FILE"
log_info "Master password saved to: $ODOO_HOME/master_password.txt"
log_info ""
log_info "Configuration summary:"
log_info "  - Workers: 4"
log_info "  - Max memory: 2.5GB per worker"
log_info "  - Longpolling port: 8072"
log_info "  - Proxy mode: Enabled"
log_info ""
log_info "Next step: Setup systemd service (as root)"
log_info "  sudo bash 05-systemd-setup.sh"

exit 0

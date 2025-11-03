#!/usr/bin/env bash
###############################################################################
# IPAI Modules Database Installation Script
#
# This script installs all IPAI modules into a specified Odoo database.
#
# Usage:
#   bash 08-install-ipai-modules.sh <database_name>
#
# Run as: odoo user
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

# Check if database name provided
if [[ $# -eq 0 ]]; then
    log_error "Database name not provided"
    log_info "Usage: bash 08-install-ipai-modules.sh <database_name>"
    exit 1
fi

DATABASE="$1"
ODOO_HOME="/home/odoo"
ODOO_BIN="$ODOO_HOME/odoo19/bin/python"
ODOO_SCRIPT="$ODOO_HOME/src/odoo/odoo-bin"
CONFIG_FILE="$ODOO_HOME/etc/odoo.conf"

# List of IPAI modules to install
MODULES=(
    "ipai_core"
    "ipai_approvals"
    "ipai_ppm_costsheet"
    "ipai_studio"
    "ipai_rate_policy"
    "ipai_ppm"
    "ipai_subscriptions"
    "ipai_knowledge_ai"
    "superset_connector"
    "ipai_saas_ops"
)

log_info "Installing IPAI modules into database: $DATABASE"
log_info "Modules to install: ${MODULES[*]}"

# Verify database exists
log_info "Checking if database exists..."
if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$DATABASE"; then
    log_error "Database '$DATABASE' does not exist"
    log_info "Please create the database first via the Odoo web interface"
    exit 1
fi

# Activate virtual environment
source "$ODOO_HOME/odoo19/bin/activate"

# Create comma-separated module list
MODULE_LIST=$(IFS=,; echo "${MODULES[*]}")

log_info "Installing modules: $MODULE_LIST"
log_info "This may take several minutes..."

# Install modules
"$ODOO_BIN" "$ODOO_SCRIPT" \
    -c "$CONFIG_FILE" \
    -d "$DATABASE" \
    -i "$MODULE_LIST" \
    --stop-after-init \
    --log-level=info

if [[ $? -eq 0 ]]; then
    log_info ""
    log_info "✓ All IPAI modules installed successfully!"
    log_info ""
    log_info "Installed modules:"
    for module in "${MODULES[@]}"; do
        log_info "  ✓ $module"
    done
    log_info ""
    log_info "Next steps:"
    log_info "  1. Restart Odoo: sudo systemctl restart odoo19"
    log_info "  2. Log in to Odoo at https://your-domain"
    log_info "  3. Configure Superset connector"
    log_info "  4. Configure MCP integration"
else
    log_error "Module installation failed"
    log_info "Check logs: tail -f $ODOO_HOME/logs/odoo.log"
    exit 1
fi

exit 0

#!/usr/bin/env bash
###############################################################################
# Odoo Custom Modules Installation Script
#
# This script clones and installs IPAI custom modules and OCA dependencies.
#
# Usage:
#   bash 07-install-modules.sh
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

ODOO_HOME="/home/odoo"
ADDONS_DIR="$ODOO_HOME/addons"
CONFIG_FILE="$ODOO_HOME/etc/odoo.conf"
ODOO_VERSION="19.0"

log_info "Installing custom modules for Odoo ${ODOO_VERSION}..."

cd "$ADDONS_DIR"

# Clone OCA server-tools
if [[ -d "$ADDONS_DIR/server-tools" ]]; then
    log_warn "OCA server-tools already exists, updating..."
    cd "$ADDONS_DIR/server-tools"
    git pull origin "$ODOO_VERSION"
else
    log_info "Cloning OCA server-tools..."
    git clone --depth=1 --branch "$ODOO_VERSION" https://github.com/OCA/server-tools.git
fi

# Clone OCA server-env
if [[ -d "$ADDONS_DIR/server-env" ]]; then
    log_warn "OCA server-env already exists, updating..."
    cd "$ADDONS_DIR/server-env"
    git pull origin "$ODOO_VERSION"
else
    log_info "Cloning OCA server-env..."
    cd "$ADDONS_DIR"
    git clone --depth=1 --branch "$ODOO_VERSION" https://github.com/OCA/server-env.git
fi

# Clone IPAI modules
IPAI_REPO="${IPAI_REPO:-https://github.com/jgtolentino/insightpulse-odoo.git}"
IPAI_BRANCH="${IPAI_BRANCH:-main}"

if [[ -d "$ADDONS_DIR/ipai_modules" ]]; then
    log_warn "IPAI modules already exist, updating..."
    cd "$ADDONS_DIR/ipai_modules"
    git pull origin "$IPAI_BRANCH"
else
    log_info "Cloning IPAI modules from $IPAI_REPO..."
    cd "$ADDONS_DIR"
    git clone "$IPAI_REPO" ipai_modules
    cd ipai_modules
    git checkout "$IPAI_BRANCH"
fi

# Update Odoo configuration with new addons path
log_info "Updating Odoo configuration..."
NEW_ADDONS_PATH="$ADDONS_DIR,$ADDONS_DIR/server-tools,$ADDONS_DIR/server-env,$ADDONS_DIR/ipai_modules,$ODOO_HOME/src/odoo/addons"

if grep -q "^addons_path" "$CONFIG_FILE"; then
    sed -i "s|^addons_path.*|addons_path = $NEW_ADDONS_PATH|" "$CONFIG_FILE"
    log_info "Addons path updated in configuration"
else
    log_error "Could not find addons_path in configuration file"
    exit 1
fi

log_info ""
log_info "Module directories installed:"
log_info "  ✓ $ADDONS_DIR/server-tools (OCA)"
log_info "  ✓ $ADDONS_DIR/server-env (OCA)"
log_info "  ✓ $ADDONS_DIR/ipai_modules (IPAI)"
log_info ""
log_info "Configuration updated with new addons path"
log_info ""
log_info "Next steps:"
log_info "  1. Restart Odoo: sudo systemctl restart odoo19"
log_info "  2. Create database via web interface at https://your-domain"
log_info "  3. Install modules via CLI or web interface"
log_info ""
log_info "To install all IPAI modules via CLI:"
log_info "  bash 08-install-ipai-modules.sh <database_name>"

exit 0

#!/usr/bin/env bash
###############################################################################
# Odoo 19 Installation Script
#
# This script installs Odoo 19 in a dedicated Python virtual environment
# and configures it for production use.
#
# Usage:
#   bash 03-odoo-install.sh
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
ODOO_VERSION="19.0"

log_info "Installing Odoo ${ODOO_VERSION}..."

# Create Python virtual environment
if [[ -d "$ODOO_HOME/odoo19" ]]; then
    log_warn "Virtual environment already exists at $ODOO_HOME/odoo19"
    read -p "Remove and recreate? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$ODOO_HOME/odoo19"
    else
        log_info "Skipping virtual environment creation"
    fi
fi

if [[ ! -d "$ODOO_HOME/odoo19" ]]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv "$ODOO_HOME/odoo19"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source "$ODOO_HOME/odoo19/bin/activate"

# Upgrade pip and essential packages
log_info "Upgrading pip, wheel, and setuptools..."
pip install --upgrade pip wheel setuptools

# Create directory structure
log_info "Creating directory structure..."
mkdir -p "$ODOO_HOME/src"
mkdir -p "$ODOO_HOME/etc"
mkdir -p "$ODOO_HOME/data"
mkdir -p "$ODOO_HOME/logs"
mkdir -p "$ODOO_HOME/addons"

# Clone Odoo repository
if [[ -d "$ODOO_HOME/src/odoo" ]]; then
    log_warn "Odoo source already exists at $ODOO_HOME/src/odoo"
    read -p "Update existing repository? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$ODOO_HOME/src/odoo"
        git fetch origin
        git checkout "$ODOO_VERSION"
        git pull origin "$ODOO_VERSION"
        log_info "Odoo repository updated"
    fi
else
    log_info "Cloning Odoo ${ODOO_VERSION} from GitHub..."
    cd "$ODOO_HOME/src"
    git clone --depth=1 --branch "$ODOO_VERSION" https://github.com/odoo/odoo.git odoo
    log_info "Odoo repository cloned"
fi

# Install Odoo Python dependencies
log_info "Installing Odoo Python dependencies..."
cd "$ODOO_HOME/src/odoo"
pip install -r requirements.txt

log_info "Odoo ${ODOO_VERSION} installation complete!"
log_info ""
log_info "Next steps:"
log_info "  1. Configure Odoo: bash 04-odoo-configure.sh"
log_info "  2. Setup systemd service (as root): bash 05-systemd-setup.sh"

exit 0

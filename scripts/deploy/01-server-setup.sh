#!/usr/bin/env bash
###############################################################################
# Initial Server Setup Script for Odoo 19 Production
#
# This script performs the initial setup of a fresh DigitalOcean droplet
# for running Odoo 19 in production.
#
# Usage:
#   bash 01-server-setup.sh
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

log_info "Starting Odoo 19 server setup..."

# Create odoo user
log_info "Creating odoo user..."
if id "odoo" &>/dev/null; then
    log_warn "User 'odoo' already exists, skipping creation"
else
    adduser --disabled-password --gecos "" odoo
    log_info "User 'odoo' created"
fi

# Grant sudo access
log_info "Granting sudo access to odoo user..."
usermod -aG sudo odoo

# Configure firewall
log_info "Configuring UFW firewall..."
ufw --force allow OpenSSH
ufw --force allow 80/tcp
ufw --force allow 443/tcp
ufw --force enable

log_info "Firewall configured:"
ufw status

# System updates
log_info "Updating system packages..."
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get -y upgrade

# Install dependencies
log_info "Installing system dependencies..."
DEBIAN_FRONTEND=noninteractive apt-get -y install \
    nginx \
    certbot \
    python3-certbot-nginx \
    postgresql-16 \
    python3-pip \
    python3-venv \
    libpq-dev \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libjpeg-dev \
    zlib1g-dev \
    libldap2-dev \
    libsasl2-dev \
    libffi-dev \
    git \
    curl \
    wget \
    htop \
    net-tools

log_info "System dependencies installed"

# Configure PostgreSQL
log_info "Configuring PostgreSQL..."
systemctl start postgresql
systemctl enable postgresql

log_info "Server setup complete!"
log_info "Next steps:"
log_info "  1. Run: bash 02-postgres-setup.sh"
log_info "  2. Run: bash 03-odoo-install.sh"

exit 0

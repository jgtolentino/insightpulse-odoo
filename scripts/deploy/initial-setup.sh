#!/usr/bin/env bash
###############################################################################
# Master Deployment Script for Odoo 19
#
# This script orchestrates the complete deployment process from a fresh
# Ubuntu droplet to a fully configured Odoo 19 production instance.
#
# Usage:
#   bash deploy-all.sh
#
# Run as: root
###############################################################################

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log_info "============================================"
log_info "  Odoo 19 Production Deployment"
log_info "  InsightPulse AI"
log_info "============================================"
echo ""

# Gather configuration
log_info "Deployment Configuration"
echo ""

read -p "Domain name (e.g., erp.insightpulseai.net): " DOMAIN
read -p "Email for Let's Encrypt: " EMAIL
read -p "IPAI modules repository URL [https://github.com/jgtolentino/insightpulse-odoo.git]: " IPAI_REPO
IPAI_REPO=${IPAI_REPO:-https://github.com/jgtolentino/insightpulse-odoo.git}

echo ""
log_info "Configuration:"
log_info "  Domain: $DOMAIN"
log_info "  Email: $EMAIL"
log_info "  Repository: $IPAI_REPO"
echo ""

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "Deployment cancelled"
    exit 0
fi

echo ""
log_step "Step 1/6: Initial Server Setup"
bash "$SCRIPT_DIR/01-server-setup.sh"

echo ""
log_step "Step 2/6: PostgreSQL Setup"
bash "$SCRIPT_DIR/02-postgres-setup.sh"
ODOO_DB_PASSWORD=$(cat /root/odoo_db_password.txt)

echo ""
log_step "Step 3/6: Odoo Installation (as odoo user)"
sudo -u odoo bash "$SCRIPT_DIR/03-odoo-install.sh"

echo ""
log_step "Step 4/6: Odoo Configuration (as odoo user)"
sudo -u odoo ODOO_DB_PASSWORD="$ODOO_DB_PASSWORD" bash "$SCRIPT_DIR/04-odoo-configure.sh"
ODOO_MASTER_PASSWORD=$(cat /home/odoo/master_password.txt)

echo ""
log_step "Step 5/6: Systemd Service Setup"
bash "$SCRIPT_DIR/05-systemd-setup.sh"

echo ""
log_step "Step 6/6: Nginx and SSL Setup"
DOMAIN="$DOMAIN" EMAIL="$EMAIL" bash "$SCRIPT_DIR/06-nginx-setup.sh"

echo ""
log_info "============================================"
log_info "  Deployment Complete!"
log_info "============================================"
echo ""
log_info "Your Odoo instance is ready at:"
log_info "  URL: https://$DOMAIN"
echo ""
log_info "Important Credentials (save securely):"
log_info "  Database Password: $ODOO_DB_PASSWORD"
log_info "  Master Password: $ODOO_MASTER_PASSWORD"
echo ""
log_info "Password files saved to:"
log_info "  Database: /root/odoo_db_password.txt"
log_info "  Master:   /home/odoo/master_password.txt"
echo ""
log_info "Next Steps:"
log_info "  1. Create database via web interface at https://$DOMAIN"
log_info "  2. Install custom modules:"
log_info "     sudo su - odoo"
log_info "     bash $SCRIPT_DIR/07-install-modules.sh"
log_info "  3. Install IPAI modules (after creating database):"
log_info "     sudo su - odoo"
log_info "     bash $SCRIPT_DIR/08-install-ipai-modules.sh <database_name>"
log_info "  4. Configure backups (add to crontab):"
log_info "     15 2 * * * $SCRIPT_DIR/backup-odoo.sh <database_name> [s3_bucket]"
echo ""
log_info "Service Management:"
log_info "  Status:  systemctl status odoo19"
log_info "  Restart: systemctl restart odoo19"
log_info "  Logs:    journalctl -u odoo19 -f"
echo ""
log_warn "IMPORTANT: Change default passwords before going live!"
echo ""

exit 0

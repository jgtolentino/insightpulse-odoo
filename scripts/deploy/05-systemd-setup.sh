#!/usr/bin/env bash
###############################################################################
# Odoo 19 Systemd Service Setup
#
# This script creates and enables the systemd service for Odoo 19.
#
# Usage:
#   bash 05-systemd-setup.sh
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

SERVICE_FILE="/etc/systemd/system/odoo19.service"

log_info "Creating Odoo 19 systemd service..."

# Stop and disable old Odoo service if exists
if systemctl list-unit-files | grep -q "^odoo.service"; then
    log_warn "Found existing 'odoo' service, stopping and disabling..."
    systemctl stop odoo 2>/dev/null || true
    systemctl disable odoo 2>/dev/null || true
fi

# Create systemd service file
cat > "$SERVICE_FILE" <<'EOF'
[Unit]
Description=Odoo 19 InsightPulse
Requires=postgresql.service
After=network.target postgresql.service

[Service]
Type=simple
SyslogIdentifier=odoo19
PermissionsStartOnly=true
User=odoo
Group=odoo
ExecStart=/home/odoo/odoo19/bin/python /home/odoo/src/odoo/odoo-bin -c /home/odoo/etc/odoo.conf
StandardOutput=journal+console
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

log_info "Systemd service file created: $SERVICE_FILE"

# Reload systemd daemon
log_info "Reloading systemd daemon..."
systemctl daemon-reload

# Enable service
log_info "Enabling odoo19 service..."
systemctl enable odoo19

# Start service
log_info "Starting odoo19 service..."
systemctl start odoo19

# Wait a moment for service to start
sleep 3

# Check status
log_info "Checking service status..."
if systemctl is-active --quiet odoo19; then
    log_info "✓ Odoo 19 service is running!"
else
    log_error "✗ Odoo 19 service failed to start"
    log_info "Check logs with: journalctl -u odoo19 -n 50"
    exit 1
fi

log_info ""
log_info "Service commands:"
log_info "  Status:  systemctl status odoo19"
log_info "  Stop:    systemctl stop odoo19"
log_info "  Start:   systemctl start odoo19"
log_info "  Restart: systemctl restart odoo19"
log_info "  Logs:    journalctl -u odoo19 -f"
log_info ""
log_info "Next step: Setup Nginx reverse proxy"
log_info "  bash 06-nginx-setup.sh"

exit 0

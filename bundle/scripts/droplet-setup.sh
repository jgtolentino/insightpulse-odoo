#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# DigitalOcean Droplet Quick Setup Script
# Run this on your fresh Ubuntu 22.04 droplet
# ============================================================================

echo "═══════════════════════════════════════════════════════════════"
echo "  Odoo 19 - DigitalOcean Droplet Setup"
echo "═══════════════════════════════════════════════════════════════"

# Update system
echo "▶ Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "▶ Installing Docker..."
sudo apt install -y docker.io docker-compose-plugin git curl

# Add user to docker group
echo "▶ Configuring Docker permissions..."
sudo usermod -aG docker $USER

# Configure firewall
echo "▶ Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw default deny incoming
sudo ufw default allow outgoing
echo "y" | sudo ufw enable

# Install fail2ban
echo "▶ Installing fail2ban..."
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Create directories
echo "▶ Creating directories..."
sudo mkdir -p /opt/odoo19
sudo chown $USER:$USER /opt/odoo19

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Setup Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Upload bundle: scp odoo19-bundle.tar.gz root@IP:/opt/odoo19/"
echo "2. Extract: tar xzf /opt/odoo19/odoo19-bundle.tar.gz -C /opt/odoo19"
echo "3. Start: cd /opt/odoo19/bundle && docker compose up -d"
echo ""
echo "Note: You may need to logout and login again for Docker permissions."
echo "═══════════════════════════════════════════════════════════════"

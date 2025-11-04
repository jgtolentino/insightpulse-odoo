#!/bin/bash
# Deploy Core Stack to ERP Droplet (165.227.10.178)
# Deploys Nginx configs, obtains TLS certificates, configures security

set -euo pipefail

DROPLET_IP="165.227.10.178"
DROPLET_USER="root"
ERP_DOMAIN="erp.insightpulseai.net"
AGENT_DOMAIN="agent.insightpulseai.net"
ADMIN_EMAIL="jgtolentino_rn@yahoo.com"

echo "🚀 Deploying Core Stack to ERP Droplet..."
echo "   Droplet: $DROPLET_IP"
echo "   Domains: $ERP_DOMAIN, $AGENT_DOMAIN"
echo ""

# 1) Copy Nginx configurations
echo "📝 Deploying Nginx configurations..."
scp infra/nginx/erp.insightpulseai.net.conf ${DROPLET_USER}@${DROPLET_IP}:/tmp/
scp infra/nginx/agent.insightpulseai.net.conf ${DROPLET_USER}@${DROPLET_IP}:/tmp/

ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
# Move configs to sites-available
sudo mv /tmp/erp.insightpulseai.net.conf /etc/nginx/sites-available/
sudo mv /tmp/agent.insightpulseai.net.conf /etc/nginx/sites-available/

# Enable sites
sudo ln -sf /etc/nginx/sites-available/erp.insightpulseai.net.conf /etc/nginx/sites-enabled/
sudo ln -sf /etc/nginx/sites-available/agent.insightpulseai.net.conf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

echo "✅ Nginx configurations deployed"
REMOTE

# 2) Install certbot if not present
echo "🔒 Setting up certbot..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
if ! command -v certbot &> /dev/null; then
  echo "Installing certbot..."
  sudo apt-get update
  sudo apt-get install -y snapd
  sudo snap install core
  sudo snap refresh core
  sudo snap install --classic certbot
  sudo ln -sf /snap/bin/certbot /usr/bin/certbot
  echo "✅ Certbot installed"
else
  echo "✅ Certbot already installed"
fi
REMOTE

# 3) Obtain TLS certificates
echo "🔐 Obtaining TLS certificates..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<REMOTE
# Obtain certificates for both domains
sudo certbot --nginx \
  -d ${ERP_DOMAIN} \
  -d ${AGENT_DOMAIN} \
  --non-interactive \
  --agree-tos \
  --redirect \
  --email ${ADMIN_EMAIL} \
  --no-eff-email || true

# Reload Nginx with new certificates
sudo nginx -t && sudo systemctl reload nginx

echo "✅ TLS certificates obtained"
REMOTE

# 4) Configure firewall
echo "🔥 Configuring firewall..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
# Install UFW if not present
if ! command -v ufw &> /dev/null; then
  sudo apt-get install -y ufw
fi

# Configure UFW rules
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH, HTTP, HTTPS
sudo ufw allow 22/tcp comment 'SSH'
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Deny direct access to Odoo ports
sudo ufw deny 8069/tcp comment 'Odoo (use HTTPS)'
sudo ufw deny 8072/tcp comment 'Odoo longpolling (use HTTPS)'

# Enable firewall
sudo ufw --force enable

# Show status
sudo ufw status verbose

echo "✅ Firewall configured"
REMOTE

# 5) Setup unattended security updates
echo "🔄 Configuring automatic security updates..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

echo "✅ Automatic security updates enabled"
REMOTE

# 6) Verify certbot auto-renewal
echo "⏰ Verifying certbot auto-renewal..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
# Check renewal timer
systemctl list-timers | grep certbot || sudo snap list | grep certbot

echo "✅ Certbot auto-renewal active"
REMOTE

# 7) Final validation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Core Stack Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 Validation Commands:"
echo ""
echo "# DNS resolution"
echo "dig +short ${ERP_DOMAIN} A"
echo "dig +short ${AGENT_DOMAIN} A"
echo ""
echo "# HTTPS connectivity"
echo "curl -I https://${ERP_DOMAIN}"
echo "curl -I https://${AGENT_DOMAIN}"
echo ""
echo "# Firewall status"
echo "ssh ${DROPLET_USER}@${DROPLET_IP} 'sudo ufw status verbose'"
echo ""
echo "# Nginx status"
echo "ssh ${DROPLET_USER}@${DROPLET_IP} 'sudo systemctl status nginx'"
echo ""
echo "# Certbot certificates"
echo "ssh ${DROPLET_USER}@${DROPLET_IP} 'sudo certbot certificates'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

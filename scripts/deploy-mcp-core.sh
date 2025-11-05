#!/bin/bash
# Deploy MCP Core to Odoo droplet with Nginx + TLS + systemd

set -euo pipefail

DROPLET_IP="165.227.10.178"
DROPLET_USER="root"
DOMAIN="mcp-core.insightpulseai.net"

echo "🚀 Deploying MCP Core to $DROPLET_IP..."

# 1) Create Nginx site configuration
echo "📝 Creating Nginx configuration..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
sudo tee /etc/nginx/sites-available/mcp-core <<'NG'
server {
  listen 80;
  server_name mcp-core.insightpulseai.net;

  location / {
    proxy_pass http://127.0.0.1:8001;
    proxy_set_header Host $host;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_read_timeout 300;
  }
}
NG

# Enable site
sudo ln -sf /etc/nginx/sites-available/mcp-core /etc/nginx/sites-enabled/mcp-core

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx

echo "✅ Nginx configured"
REMOTE

# 2) Install certbot if not present
echo "🔒 Setting up Let's Encrypt..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
# Install certbot if not present
if ! command -v certbot &> /dev/null; then
  sudo snap install core
  sudo snap refresh core
  sudo snap install --classic certbot
  sudo ln -sf /snap/bin/certbot /usr/bin/certbot
fi

# Obtain certificate (non-interactive)
sudo certbot --nginx -d mcp-core.insightpulseai.net --non-interactive --agree-tos --redirect --email jgtolentino_rn@yahoo.com || true

echo "✅ TLS certificate configured"
REMOTE

# 3) Create systemd service
echo "⚙️ Creating systemd service..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
sudo tee /etc/systemd/system/mcp-secure.service <<'UNIT'
[Unit]
Description=MCP Secure API
After=network.target

[Service]
Type=simple
User=odoo
WorkingDirectory=/opt/insightpulse-odoo
Environment="MCP_BEARER=supersecret-bearer-change-me"
Environment="MCP_BASIC_USER=ipai"
Environment="MCP_BASIC_PASS=change-this-password"
Environment="MCP_ALLOW_IPS=127.0.0.1,165.227.10.178"
Environment="CORS_ORIGINS=https://mcp.insightpulseai.net,https://erp.insightpulseai.net"
ExecStart=/usr/bin/uvicorn services.mcp-secure.server:app --host 127.0.0.1 --port 8001
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT

# Reload systemd
sudo systemctl daemon-reload

echo "✅ Systemd service created"
REMOTE

# 4) Deploy code
echo "📦 Deploying MCP Secure code..."
scp -r services/mcp-secure ${DROPLET_USER}@${DROPLET_IP}:/opt/insightpulse-odoo/services/

# 5) Install dependencies
echo "📚 Installing Python dependencies..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
cd /opt/insightpulse-odoo
sudo -u odoo python3 -m pip install fastapi uvicorn pydantic requests || \
  python3 -m pip install fastapi uvicorn pydantic requests

# Fix ownership
sudo chown -R odoo:odoo /opt/insightpulse-odoo/services

echo "✅ Dependencies installed"
REMOTE

# 6) Start service
echo "🔄 Starting MCP Secure service..."
ssh ${DROPLET_USER}@${DROPLET_IP} <<'REMOTE'
sudo systemctl enable mcp-secure
sudo systemctl restart mcp-secure
sleep 3
sudo systemctl status mcp-secure --no-pager

echo "✅ Service started"
REMOTE

# 7) Validation
echo "✅ Deployment complete!"
echo ""
echo "📊 Validation commands:"
echo "  curl -I https://mcp-core.insightpulseai.net/health"
echo "  curl -I --user ipai:change-this-password https://mcp-core.insightpulseai.net/mcp/catalog"
echo "  curl -s https://mcp-core.insightpulseai.net/mcp/catalog -H 'Authorization: Bearer supersecret-bearer-change-me' | jq ."
echo ""
echo "⚠️  IMPORTANT: Update these credentials in systemd service:"
echo "  sudo systemctl edit mcp-secure"
echo "  # Add secure MCP_BEARER and MCP_BASIC_PASS values"

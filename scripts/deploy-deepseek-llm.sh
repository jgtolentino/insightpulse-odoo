#!/bin/bash
# Deploy DeepSeek-R1 7B LLM to New GPU Droplet
# Creates GPU droplet, configures Nginx + TLS, sets up llm.insightpulseai.net

set -euo pipefail

# Configuration
LLM_DOMAIN="llm.insightpulseai.net"
ADMIN_EMAIL="jgtolentino_rn@yahoo.com"
REGION="sgp1"  # Singapore, near existing OCR droplet
DROPLET_SIZE="g-2vcpu-8gb-nvidia-l4"  # GPU droplet with L4
MARKETPLACE_IMAGE_SLUG="deepseek-r1-distill-qwen7b"  # Marketplace 1-Click App

echo "🚀 Deploying DeepSeek-R1 7B LLM Infrastructure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Create GPU Droplet
echo "📦 Creating GPU droplet..."
echo "   Region: $REGION"
echo "   Size: $DROPLET_SIZE"
echo "   Image: DeepSeek R1 Distill Qwen 7B (Marketplace)"
echo ""

# Note: Requires doctl authenticated with DO_ACCESS_TOKEN
# doctl auth init --access-token $DO_ACCESS_TOKEN

DROPLET_JSON=$(doctl compute droplet create llm-deepseek-r1 \
  --region "$REGION" \
  --size "$DROPLET_SIZE" \
  --image "$MARKETPLACE_IMAGE_SLUG" \
  --wait \
  --format ID,PublicIPv4 \
  --output json)

DROPLET_ID=$(echo "$DROPLET_JSON" | jq -r '.[0].id')
DROPLET_IP=$(echo "$DROPLET_JSON" | jq -r '.[0].networks.v4[] | select(.type=="public") | .ip_address')

echo "✅ GPU droplet created"
echo "   Droplet ID: $DROPLET_ID"
echo "   Public IP: $DROPLET_IP"
echo ""

# Wait for SSH to be ready
echo "⏳ Waiting for SSH to be ready (30s)..."
sleep 30

# Step 2: Update DNS (manual action required)
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 DNS Configuration Required"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Add this record to Squarespace DNS:"
echo ""
echo "Host: llm"
echo "Type: A"
echo "Data: $DROPLET_IP"
echo "TTL: 1 hour"
echo ""
echo "Press Enter after DNS is configured to continue..."
read -r

# Step 3: Install Nginx and configure reverse proxy
echo ""
echo "🔧 Configuring Nginx reverse proxy..."

ssh root@"$DROPLET_IP" <<'REMOTE_SCRIPT'
# Install Nginx if not present
if ! command -v nginx &> /dev/null; then
  echo "Installing Nginx..."
  apt-get update
  apt-get install -y nginx
fi

# Create Nginx config for LLM endpoint
cat > /etc/nginx/sites-available/llm.insightpulseai.net.conf <<'NGINX_CONF'
server {
    listen 80;
    server_name llm.insightpulseai.net;

    # LLM API endpoint (DeepSeek runs on port 8000)
    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Streaming support for chat completions
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 3600s;
        proxy_connect_timeout 75s;
    }
}
NGINX_CONF

# Enable site
ln -sf /etc/nginx/sites-available/llm.insightpulseai.net.conf /etc/nginx/sites-enabled/

# Test and reload Nginx
nginx -t
systemctl reload nginx

echo "✅ Nginx configured"
REMOTE_SCRIPT

# Step 4: Install and configure certbot for TLS
echo ""
echo "🔒 Obtaining TLS certificate..."

ssh root@"$DROPLET_IP" <<REMOTE_SCRIPT
# Install certbot via snap if not present
if ! command -v certbot &> /dev/null; then
  echo "Installing certbot..."
  apt-get update
  apt-get install -y snapd
  snap install core
  snap refresh core
  snap install --classic certbot
  ln -sf /snap/bin/certbot /usr/bin/certbot
fi

# Obtain TLS certificate
certbot --nginx \
  -d ${LLM_DOMAIN} \
  --non-interactive \
  --agree-tos \
  --redirect \
  --email ${ADMIN_EMAIL} \
  --no-eff-email

# Reload Nginx with new certificate
nginx -t && systemctl reload nginx

echo "✅ TLS certificate obtained"
REMOTE_SCRIPT

# Step 5: Configure firewall
echo ""
echo "🔥 Configuring firewall..."

ssh root@"$DROPLET_IP" <<'REMOTE_SCRIPT'
# Install UFW if not present
if ! command -v ufw &> /dev/null; then
  apt-get install -y ufw
fi

# Configure UFW rules
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# Allow SSH, HTTP, HTTPS only
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Deny direct access to LLM port
ufw deny 8000/tcp comment 'LLM (use HTTPS)'

# Enable firewall
ufw --force enable
ufw status verbose

echo "✅ Firewall configured"
REMOTE_SCRIPT

# Step 6: Setup automatic security updates
echo ""
echo "🔄 Configuring automatic security updates..."

ssh root@"$DROPLET_IP" <<'REMOTE_SCRIPT'
apt-get install -y unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades

echo "✅ Automatic security updates enabled"
REMOTE_SCRIPT

# Step 7: Verify DeepSeek service is running
echo ""
echo "🔍 Verifying DeepSeek service..."

ssh root@"$DROPLET_IP" <<'REMOTE_SCRIPT'
# Check if DeepSeek service is active
if systemctl is-active --quiet deepseek-r1; then
  echo "✅ DeepSeek R1 service is running"
  systemctl status deepseek-r1 --no-pager
else
  echo "⚠️ DeepSeek R1 service not found or not running"
  echo "   Check Marketplace 1-Click setup instructions"
fi
REMOTE_SCRIPT

# Final validation
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ DeepSeek-R1 7B LLM Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Deployment Summary:"
echo "   Domain: https://${LLM_DOMAIN}"
echo "   Droplet ID: $DROPLET_ID"
echo "   IP Address: $DROPLET_IP"
echo "   Region: $REGION"
echo ""
echo "🔍 Validation Commands:"
echo ""
echo "# DNS resolution"
echo "dig +short ${LLM_DOMAIN} A"
echo ""
echo "# HTTPS connectivity"
echo "curl -I https://${LLM_DOMAIN}"
echo ""
echo "# List available models"
echo "curl -s https://${LLM_DOMAIN}/v1/models | jq"
echo ""
echo "# Test chat completion"
echo "curl -s https://${LLM_DOMAIN}/v1/chat/completions \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"model\": \"deepseek-r1-distill-qwen-7b\", \"messages\": [{\"role\": \"user\", \"content\": \"Hello\"}]}' | jq"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

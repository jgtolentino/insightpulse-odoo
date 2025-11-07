#!/bin/bash
set -euo pipefail

# ============================================================================
# InsightPulse AI Landing Page Deployment Script
# ============================================================================
# Purpose: Deploy unified login landing page to insightpulseai.net
# Target: 165.227.10.178 (Odoo droplet) or separate hosting
# Run as: ./deploy-landing.sh
# ============================================================================

echo "🚀 Deploying InsightPulse AI Landing Page"
echo ""

# Configuration
DROPLET_IP="${DROPLET_IP:-165.227.10.178}"
DROPLET_USER="${DROPLET_USER:-root}"
DOMAIN="insightpulseai.net"
WEB_ROOT="/var/www/${DOMAIN}"

echo "📋 Configuration:"
echo "  Target: ${DROPLET_USER}@${DROPLET_IP}"
echo "  Domain: ${DOMAIN}"
echo "  Web Root: ${WEB_ROOT}"
echo ""

# ============================================================================
# Step 1: Create web directory on droplet
# ============================================================================
echo "📁 Step 1: Creating web directory..."

ssh ${DROPLET_USER}@${DROPLET_IP} "mkdir -p ${WEB_ROOT}"
echo "  ✅ Directory created: ${WEB_ROOT}"
echo ""

# ============================================================================
# Step 2: Upload landing page files
# ============================================================================
echo "📤 Step 2: Uploading landing page..."

scp index.html ${DROPLET_USER}@${DROPLET_IP}:${WEB_ROOT}/
echo "  ✅ index.html uploaded"
echo ""

# ============================================================================
# Step 3: Set proper permissions
# ============================================================================
echo "🔐 Step 3: Setting permissions..."

ssh ${DROPLET_USER}@${DROPLET_IP} "chown -R www-data:www-data ${WEB_ROOT}"
ssh ${DROPLET_USER}@${DROPLET_IP} "chmod -R 755 ${WEB_ROOT}"
echo "  ✅ Permissions set (www-data:www-data, 755)"
echo ""

# ============================================================================
# Step 4: Configure Nginx
# ============================================================================
echo "⚙️  Step 4: Configuring Nginx..."

# Upload Nginx config
scp nginx-landing.conf ${DROPLET_USER}@${DROPLET_IP}:/etc/nginx/sites-available/${DOMAIN}

# Enable site
ssh ${DROPLET_USER}@${DROPLET_IP} "ln -sf /etc/nginx/sites-available/${DOMAIN} /etc/nginx/sites-enabled/${DOMAIN}"

echo "  ✅ Nginx config deployed"
echo ""

# ============================================================================
# Step 5: Obtain SSL certificate
# ============================================================================
echo "🔒 Step 5: Obtaining SSL certificate..."

# Check if certificate already exists
CERT_EXISTS=$(ssh ${DROPLET_USER}@${DROPLET_IP} "test -d /etc/letsencrypt/live/${DOMAIN} && echo 'yes' || echo 'no'")

if [ "$CERT_EXISTS" = "no" ]; then
    echo "  📜 Obtaining new certificate from Let's Encrypt..."

    ssh ${DROPLET_USER}@${DROPLET_IP} "certbot certonly --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email jgtolentino_rn@yahoo.com"

    echo "  ✅ SSL certificate obtained"
else
    echo "  ✅ SSL certificate already exists"
fi
echo ""

# ============================================================================
# Step 6: Test and reload Nginx
# ============================================================================
echo "🧪 Step 6: Testing Nginx configuration..."

ssh ${DROPLET_USER}@${DROPLET_IP} "nginx -t"
echo "  ✅ Nginx configuration valid"

echo "  🔄 Reloading Nginx..."
ssh ${DROPLET_USER}@${DROPLET_IP} "systemctl reload nginx"
echo "  ✅ Nginx reloaded"
echo ""

# ============================================================================
# Step 7: Verify deployment
# ============================================================================
echo "🔍 Step 7: Verifying deployment..."

# Wait for Nginx to start serving
sleep 2

# Test HTTP redirect
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${DOMAIN} || echo "000")
echo "  HTTP redirect: ${HTTP_CODE}"

# Test HTTPS
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://${DOMAIN} || echo "000")
echo "  HTTPS response: ${HTTPS_CODE}"

if [ "$HTTPS_CODE" = "200" ]; then
    echo "  ✅ Landing page is live!"
else
    echo "  ⚠️  Warning: HTTPS returned ${HTTPS_CODE}"
fi
echo ""

# ============================================================================
# Step 8: Test service health checks
# ============================================================================
echo "🏥 Step 8: Testing service endpoints..."

echo "  Testing OCR service..."
OCR_STATUS=$(curl -sf https://ocr.insightpulseai.net/health | jq -r '.status' 2>/dev/null || echo "error")
echo "    OCR: ${OCR_STATUS}"

echo "  Testing Odoo ERP..."
ODOO_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" https://erp.insightpulseai.net || echo "000")
echo "    Odoo: HTTP ${ODOO_STATUS}"

echo ""

# ============================================================================
# Summary
# ============================================================================
echo "════════════════════════════════════════════════════════════════"
echo "🎉 Landing Page Deployment Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "✅ Deployment Status:"
echo "  Landing Page: https://${DOMAIN}"
echo "  Nginx Config: /etc/nginx/sites-available/${DOMAIN}"
echo "  Web Root: ${WEB_ROOT}"
echo "  SSL Certificate: /etc/letsencrypt/live/${DOMAIN}"
echo ""
echo "🔗 Available Services:"
echo "  • Main Portal: https://${DOMAIN}"
echo "  • Odoo ERP: https://erp.insightpulseai.net"
echo "  • OCR Service: https://ocr.insightpulseai.net"
echo "  • Superset BI: https://superset.insightpulseai.net (pending)"
echo ""
echo "🧪 Test Login:"
echo "  1. Visit: https://${DOMAIN}"
echo "  2. Enter Odoo credentials"
echo "  3. Click 'Sign In to All Services'"
echo "  4. Should redirect to Odoo ERP"
echo ""
echo "📊 Health Status:"
echo "  Landing Page: ${HTTPS_CODE}"
echo "  OCR Service: ${OCR_STATUS}"
echo "  Odoo ERP: ${ODOO_STATUS}"
echo ""
echo "════════════════════════════════════════════════════════════════"

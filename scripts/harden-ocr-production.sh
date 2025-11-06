#!/bin/bash
set -euo pipefail

# ============================================================================
# OCR Service Production Hardening Script
# ============================================================================
# Purpose: Apply security hardening, monitoring, and operational best practices
# Target: ocr.insightpulseai.net (188.166.237.231)
# Run as: root on target droplet
# ============================================================================

echo "🔒 Starting OCR Service Production Hardening..."
echo ""

# ============================================================================
# 1. Nginx Security + Performance Patch
# ============================================================================
echo "📝 Step 1: Hardening Nginx configuration..."

# Backup existing config
cp /etc/nginx/sites-available/ocr /etc/nginx/sites-available/ocr.backup-$(date +%Y%m%d-%H%M%S)

# Create hardened config
cat > /etc/nginx/sites-available/ocr <<'EOF'
# Rate limiting zone
limit_req_zone $binary_remote_addr zone=ocr_api:10m rate=5r/s;

server {
    server_name ocr.insightpulseai.net;

    # --- TLS hardening (Certbot handles ssl_protocols, ssl_ciphers, ssl_session_*) ---
    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1 8.8.8.8 valid=300s;
    resolver_timeout 5s;

    # --- Security headers ---
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # CORS - Lock to Odoo domain only
    add_header Access-Control-Allow-Origin "https://erp.insightpulseai.net" always;
    add_header Access-Control-Allow-Methods "POST, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;

    # Handle preflight requests
    if ($request_method = OPTIONS) {
        return 204;
    }

    # --- Rate-limited OCR endpoint ---
    location /v1/ocr/receipt {
        limit_req zone=ocr_api burst=20 nodelay;

        proxy_pass http://127.0.0.1:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        client_max_body_size 10M;
        proxy_connect_timeout 15s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # --- Health probes (no rate limiting) ---
    location ~ ^/(live|health|ready)$ {
        proxy_pass http://127.0.0.1:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Quick timeouts for health checks
        proxy_connect_timeout 5s;
        proxy_send_timeout 10s;
        proxy_read_timeout 10s;
    }

    # --- Legacy endpoints (rate limited) ---
    location ~ ^/v1/(ocr|parse)$ {
        limit_req zone=ocr_api burst=20 nodelay;

        proxy_pass http://127.0.0.1:8100;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        client_max_body_size 10M;
        proxy_connect_timeout 15s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }

    # Block all other paths
    location / {
        return 404;
    }

    # Logging
    access_log /var/log/nginx/ocr.access.log;
    error_log /var/log/nginx/ocr.error.log warn;

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/ocr.insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ocr.insightpulseai.net/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}

# HTTP to HTTPS redirect
server {
    if ($host = ocr.insightpulseai.net) {
        return 301 https://$host$request_uri;
    }

    listen 80;
    server_name ocr.insightpulseai.net;
    return 404;
}
EOF

# Test and reload Nginx
nginx -t
systemctl reload nginx

echo "✅ Nginx hardened and reloaded"
echo ""

# ============================================================================
# 2. Firewall Configuration
# ============================================================================
echo "🔥 Step 2: Configuring UFW firewall..."

# Reset UFW to start fresh
ufw --force reset

# Set default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH (critical - don't lock yourself out!)
ufw allow 22/tcp comment 'SSH'

# Allow HTTP/HTTPS
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Enable firewall
ufw --force enable

echo "✅ Firewall configured (SSH, HTTP, HTTPS allowed)"
echo ""

# ============================================================================
# 3. Fail2Ban Installation
# ============================================================================
echo "🛡️  Step 3: Installing and configuring Fail2Ban..."

apt-get update -qq
apt-get install -y fail2ban

# Create Nginx jail for OCR service
cat > /etc/fail2ban/jail.d/nginx-ocr.conf <<'EOF'
[nginx-ocr]
enabled = true
port = http,https
filter = nginx-ocr
logpath = /var/log/nginx/ocr.access.log
maxretry = 10
findtime = 60
bantime = 3600
EOF

# Create filter for OCR abuse patterns
cat > /etc/fail2ban/filter.d/nginx-ocr.conf <<'EOF'
[Definition]
failregex = ^<HOST> .* "(POST|GET) /v1/ocr/receipt.*" (429|503) .*$
            ^<HOST> .* "(POST|GET) /v1/ocr.*" (500|502|503) .*$
ignoreregex =
EOF

systemctl enable fail2ban
systemctl restart fail2ban

echo "✅ Fail2Ban installed and configured"
echo ""

# ============================================================================
# 4. Log Rotation
# ============================================================================
echo "📊 Step 4: Configuring log rotation..."

cat > /etc/logrotate.d/nginx-ocr <<'EOF'
/var/log/nginx/ocr.*.log {
    weekly
    rotate 8
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        if [ -f /var/run/nginx.pid ]; then
            kill -USR1 `cat /var/run/nginx.pid`
        fi
    endscript
}
EOF

echo "✅ Log rotation configured"
echo ""

# ============================================================================
# 5. Certbot Auto-Renewal Check
# ============================================================================
echo "🔐 Step 5: Verifying SSL auto-renewal..."

systemctl enable certbot.timer
systemctl start certbot.timer

# Dry-run renewal test
certbot renew --dry-run

echo "✅ SSL auto-renewal verified"
echo ""

# ============================================================================
# 6. System Hardening
# ============================================================================
echo "🔧 Step 6: Applying system hardening..."

# Disable SSH password authentication (key-only)
sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
systemctl restart sshd

# Set kernel security parameters
cat >> /etc/sysctl.conf <<'EOF'

# OCR Service Security Hardening
net.ipv4.conf.default.rp_filter=1
net.ipv4.conf.all.rp_filter=1
net.ipv4.tcp_syncookies=1
net.ipv4.conf.all.accept_redirects=0
net.ipv6.conf.all.accept_redirects=0
net.ipv4.conf.all.send_redirects=0
net.ipv4.conf.all.accept_source_route=0
net.ipv6.conf.all.accept_source_route=0
net.ipv4.conf.all.log_martians=1
EOF

sysctl -p

echo "✅ System hardening applied"
echo ""

# ============================================================================
# 7. Monitoring Setup
# ============================================================================
echo "📈 Step 7: Setting up monitoring cron job..."

# Create monitoring script
cat > /usr/local/bin/ocr-health-check.sh <<'EOF'
#!/bin/bash
# OCR Service Health Check Script
# Runs every 5 minutes via cron

LOG="/var/log/ocr-health-check.log"
ALERT_EMAIL="jgtolentino_rn@yahoo.com"

# Check if service is ready
READY=$(curl -sf https://ocr.insightpulseai.net/ready | jq -r '.ready')

if [ "$READY" != "true" ]; then
    echo "$(date): ❌ OCR service NOT READY" >> $LOG
    # Optionally send email alert
    # echo "OCR service health check failed" | mail -s "ALERT: OCR Service Down" $ALERT_EMAIL
    exit 1
fi

echo "$(date): ✅ OCR service healthy" >> $LOG
exit 0
EOF

chmod +x /usr/local/bin/ocr-health-check.sh

# Add to crontab (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/ocr-health-check.sh") | crontab -

echo "✅ Health monitoring cron job configured"
echo ""

# ============================================================================
# 8. Service Status Check
# ============================================================================
echo "🔍 Step 8: Verifying service status..."

# Check systemd service
systemctl status ai-inference-hub --no-pager | head -10

# Check Nginx
systemctl status nginx --no-pager | head -5

# Check UFW
ufw status numbered

# Check Fail2Ban
fail2ban-client status

echo ""
echo "✅ Service status verified"
echo ""

# ============================================================================
# 9. Smoke Tests
# ============================================================================
echo "🧪 Step 9: Running smoke tests..."

echo "  - Testing /live..."
curl -sf https://ocr.insightpulseai.net/live | jq -c

echo "  - Testing /health..."
curl -sf https://ocr.insightpulseai.net/health | jq -c

echo "  - Testing /ready..."
curl -sf https://ocr.insightpulseai.net/ready | jq -c

echo ""
echo "✅ Smoke tests passed"
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "════════════════════════════════════════════════════════════════"
echo "🎉 OCR Service Production Hardening Complete!"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "Applied Hardening:"
echo "  ✅ Nginx: TLS 1.2/1.3, security headers, rate limiting"
echo "  ✅ Firewall: UFW enabled (SSH, HTTP, HTTPS only)"
echo "  ✅ Fail2Ban: Active jail for OCR abuse"
echo "  ✅ Log Rotation: Weekly rotation, 8 weeks retention"
echo "  ✅ SSL: Auto-renewal verified"
echo "  ✅ System: SSH key-only, kernel hardening"
echo "  ✅ Monitoring: Health checks every 5 minutes"
echo ""
echo "Service Endpoints:"
echo "  🔗 Health: https://ocr.insightpulseai.net/health"
echo "  🔗 Ready: https://ocr.insightpulseai.net/ready"
echo "  🔗 OCR: https://ocr.insightpulseai.net/v1/ocr/receipt"
echo ""
echo "Logs:"
echo "  📋 Service: journalctl -u ai-inference-hub -f"
echo "  📋 Nginx: tail -f /var/log/nginx/ocr.access.log"
echo "  📋 Health: tail -f /var/log/ocr-health-check.log"
echo "  📋 Fail2Ban: fail2ban-client status nginx-ocr"
echo ""
echo "Next Steps:"
echo "  1. Configure Odoo: https://ocr.insightpulseai.net/v1/ocr/receipt"
echo "  2. Test mobile upload → OCR → expense creation"
echo "  3. Verify Supabase sync"
echo "  4. Create Superset dashboard"
echo ""
echo "════════════════════════════════════════════════════════════════"

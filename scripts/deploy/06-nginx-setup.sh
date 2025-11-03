#!/usr/bin/env bash
###############################################################################
# Nginx Reverse Proxy Setup for Odoo 19
#
# This script configures Nginx as a reverse proxy for Odoo with SSL/TLS
# support via Let's Encrypt.
#
# Usage:
#   DOMAIN=erp.insightpulseai.net EMAIL=admin@insightpulseai.net bash 06-nginx-setup.sh
#
# Run as: root
# Environment variables:
#   DOMAIN - Domain name for Odoo (e.g., erp.insightpulseai.net)
#   EMAIL  - Email for Let's Encrypt notifications
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

# Validate required environment variables
if [[ -z "${DOMAIN:-}" ]]; then
    log_error "DOMAIN environment variable not set"
    log_info "Usage: DOMAIN=erp.insightpulseai.net EMAIL=admin@insightpulseai.net bash 06-nginx-setup.sh"
    exit 1
fi

if [[ -z "${EMAIL:-}" ]]; then
    log_error "EMAIL environment variable not set"
    log_info "Usage: DOMAIN=erp.insightpulseai.net EMAIL=admin@insightpulseai.net bash 06-nginx-setup.sh"
    exit 1
fi

NGINX_SITE="/etc/nginx/sites-available/odoo"
NGINX_ENABLED="/etc/nginx/sites-enabled/odoo"

log_info "Configuring Nginx for domain: $DOMAIN"

# Remove default site if exists
if [[ -f "/etc/nginx/sites-enabled/default" ]]; then
    log_info "Removing default Nginx site..."
    rm -f /etc/nginx/sites-enabled/default
fi

# Create Nginx configuration
log_info "Creating Nginx configuration..."
cat > "$NGINX_SITE" <<EOF
# Odoo server configuration
upstream odoo {
    server 127.0.0.1:8069;
}

upstream odoochat {
    server 127.0.0.1:8072;
}

map \$http_upgrade \$connection_upgrade {
    default upgrade;
    ''      close;
}

# HTTP server - redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN;

    # Let's Encrypt challenge
    location ~ /.well-known/acme-challenge {
        allow all;
        root /var/www/html;
    }

    # Redirect all HTTP to HTTPS
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}

# HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name $DOMAIN;

    # SSL configuration will be added by certbot
    # ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    # ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Increase buffer size for large requests
    proxy_buffers 16 64k;
    proxy_buffer_size 128k;

    # Increase upload size
    client_max_body_size 100M;

    # Timeouts
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    # Proxy headers
    proxy_set_header X-Forwarded-Host \$host;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header X-Real-IP \$remote_addr;

    # Health check endpoint
    location = /web/health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }

    # Odoo longpolling
    location /longpolling {
        proxy_pass http://odoochat;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$connection_upgrade;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Odoo main
    location / {
        proxy_redirect off;
        proxy_pass http://odoo;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Cache static files
    location ~* /web/static/ {
        proxy_cache_valid 200 90m;
        proxy_buffering on;
        expires 864000;
        proxy_pass http://odoo;
        proxy_set_header Host \$host;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    # Gzip
    gzip on;
    gzip_types text/css text/scss text/plain text/xml application/xml application/json application/javascript;
    gzip_min_length 1000;
}
EOF

# Enable site
log_info "Enabling Nginx site..."
ln -sf "$NGINX_SITE" "$NGINX_ENABLED"

# Test Nginx configuration
log_info "Testing Nginx configuration..."
if nginx -t; then
    log_info "✓ Nginx configuration is valid"
else
    log_error "✗ Nginx configuration test failed"
    exit 1
fi

# Reload Nginx
log_info "Reloading Nginx..."
systemctl reload nginx

# Wait for Nginx to be ready
sleep 2

# Check if domain is accessible
log_info "Checking if domain is accessible..."
if curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" | grep -q "200\|301\|302"; then
    log_info "✓ Domain is accessible"
else
    log_warn "Domain may not be accessible yet. Check DNS configuration."
    log_info "Add this DNS record:"
    log_info "  Type: A"
    log_info "  Name: erp (or your subdomain)"
    log_info "  Value: $(curl -s ifconfig.me)"
    log_info "  TTL: 3600"
    log_info ""
    read -p "Continue with SSL setup? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping SSL setup. Run this script again when DNS is configured."
        exit 0
    fi
fi

# Obtain SSL certificate
log_info "Obtaining SSL certificate from Let's Encrypt..."
certbot --nginx \
    -d "$DOMAIN" \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --redirect

# Test SSL renewal
log_info "Testing SSL certificate renewal..."
certbot renew --dry-run

log_info ""
log_info "✓ Nginx and SSL setup complete!"
log_info ""
log_info "Your Odoo instance is now accessible at:"
log_info "  https://$DOMAIN"
log_info ""
log_info "Health check endpoint:"
log_info "  https://$DOMAIN/web/health"
log_info ""
log_info "Next steps:"
log_info "  1. Create database via web interface"
log_info "  2. Install custom modules: bash 07-install-modules.sh"

exit 0

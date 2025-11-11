#!/bin/bash
# Issue SSL certificates for all InsightPulse Odoo domains
# Prerequisites: DNS records created and propagated

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔐 Issuing SSL certificates for insightpulseai.net${NC}"
echo ""

DOMAIN="insightpulseai.net"
EMAIL="admin@insightpulseai.net"
SERVER_IP="165.227.10.178"

# All subdomains to secure
SUBDOMAINS=(
    "insightpulseai.net"
    "www.insightpulseai.net"
    "erp.insightpulseai.net"
    "superset.insightpulseai.net"
    "mcp.insightpulseai.net"
    "agent.insightpulseai.net"
    "chat.insightpulseai.net"
    "n8n.insightpulseai.net"
    "ocr.insightpulseai.net"
    "gittodoc.insightpulseai.net"
)

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo -e "${RED}❌ Error: certbot not found${NC}"
    echo "Install: sudo apt install certbot python3-certbot-nginx"
    exit 1
fi

# Check if running on the server
CURRENT_IP=$(curl -s ifconfig.me)
if [ "$CURRENT_IP" != "$SERVER_IP" ]; then
    echo -e "${YELLOW}⚠️  Warning: This script should run on the Nginx server (${SERVER_IP})${NC}"
    echo "Current IP: $CURRENT_IP"
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check DNS propagation
echo "🔍 Checking DNS propagation..."
FAILED_DNS=()
for subdomain in "${SUBDOMAINS[@]}"; do
    if ! dig +short "$subdomain" @8.8.8.8 | grep -q .; then
        FAILED_DNS+=("$subdomain")
    fi
done

if [ ${#FAILED_DNS[@]} -gt 0 ]; then
    echo -e "${RED}❌ DNS not yet propagated for:${NC}"
    printf '%s\n' "${FAILED_DNS[@]}"
    echo ""
    echo "Wait 30-60 minutes after creating DNS records, then retry."
    exit 1
fi

echo -e "${GREEN}✅ DNS propagation verified${NC}"
echo ""

# Build domain arguments for certbot
DOMAIN_ARGS=()
for subdomain in "${SUBDOMAINS[@]}"; do
    DOMAIN_ARGS+=("-d" "$subdomain")
done

# Dry run mode
if [ "$1" == "--dry-run" ]; then
    echo -e "${YELLOW}🔍 DRY RUN MODE - Testing certificate issuance${NC}"
    echo ""

    sudo certbot certonly \
        --nginx \
        --dry-run \
        --non-interactive \
        --agree-tos \
        --email "$EMAIL" \
        "${DOMAIN_ARGS[@]}"

    echo ""
    echo -e "${GREEN}✅ Dry run successful${NC}"
    echo "Run without --dry-run to issue real certificates"
    exit 0
fi

# Issue certificates
echo "📜 Issuing SSL certificates..."
echo ""

sudo certbot --nginx \
    --non-interactive \
    --agree-tos \
    --email "$EMAIL" \
    --redirect \
    "${DOMAIN_ARGS[@]}"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ SSL certificates issued successfully${NC}"
    echo ""
    echo "Certificate details:"
    sudo certbot certificates
    echo ""
    echo "Auto-renewal status:"
    sudo systemctl status certbot.timer --no-pager
    echo ""
    echo "Test renewal:"
    echo "  sudo certbot renew --dry-run"
    echo ""
    echo "Next steps:"
    echo "  1. Test HTTPS endpoints: ./scripts/test-dns-endpoints.sh"
    echo "  2. Verify SSL configuration: https://www.ssllabs.com/ssltest/"
else
    echo -e "${RED}❌ Certificate issuance failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check Nginx configs: nginx -t"
    echo "  2. Check DNS records: dig @8.8.8.8 [subdomain]"
    echo "  3. Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
    echo "  4. Manual certbot: sudo certbot --nginx -d [subdomain]"
    exit 1
fi

echo ""

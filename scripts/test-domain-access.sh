#!/bin/bash
# Test domain access for InsightPulse Odoo deployment
# This script verifies DNS, HTTP/HTTPS, and service availability

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default configuration
DOMAIN="${DOMAIN:-localhost}"
ODOO_PATH="${ODOO_PATH:-/odoo}"
SUPERSET_PATH="${SUPERSET_PATH:-/superset}"
ODOO_PORT="${ODOO_PORT:-8069}"
SUPERSET_PORT="${SUPERSET_PORT:-8088}"
USE_HTTPS="${USE_HTTPS:-false}"

# Determine protocol
if [ "$USE_HTTPS" = "true" ]; then
    PROTOCOL="https"
else
    PROTOCOL="http"
fi

echo "============================================"
echo "Domain Access Test for InsightPulse Odoo"
echo "============================================"
echo ""
echo "Configuration:"
echo "  Domain: $DOMAIN"
echo "  Protocol: $PROTOCOL"
echo "  Odoo Path: $ODOO_PATH"
echo "  Superset Path: $SUPERSET_PATH"
echo ""

# Test 1: DNS Resolution
echo "Test 1: DNS Resolution"
echo "----------------------"
if host "$DOMAIN" > /dev/null 2>&1; then
    IP=$(host "$DOMAIN" | grep "has address" | head -n1 | awk '{print $4}')
    echo -e "${GREEN}✓${NC} DNS resolves to: $IP"
else
    echo -e "${RED}✗${NC} DNS resolution failed for $DOMAIN"
    echo "  Please check your DNS configuration"
fi
echo ""

# Test 2: HTTP/HTTPS Connectivity to Domain
echo "Test 2: Domain Connectivity"
echo "---------------------------"
if curl -I -s -f "$PROTOCOL://$DOMAIN" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} $PROTOCOL://$DOMAIN is accessible"
else
    echo -e "${YELLOW}⚠${NC} $PROTOCOL://$DOMAIN is not accessible"
    echo "  This may be expected if using path-based routing"
fi
echo ""

# Test 3: Odoo Service Availability
echo "Test 3: Odoo Service"
echo "--------------------"
ODOO_URL="$PROTOCOL://$DOMAIN$ODOO_PATH"
if curl -I -s -f "$ODOO_URL" > /dev/null 2>&1 || curl -I -s -f "$ODOO_URL/web/login" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Odoo is accessible at: $ODOO_URL"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$ODOO_URL/web/login")
    echo "  HTTP Status Code: $HTTP_CODE"
else
    echo -e "${RED}✗${NC} Odoo is not accessible at: $ODOO_URL"
    echo "  Trying direct port access..."
    if curl -I -s -f "$PROTOCOL://$DOMAIN:$ODOO_PORT" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Odoo is accessible via direct port: $PROTOCOL://$DOMAIN:$ODOO_PORT"
    else
        echo -e "${RED}✗${NC} Odoo is not accessible"
    fi
fi
echo ""

# Test 4: Superset Service Availability
echo "Test 4: Superset Service"
echo "------------------------"
SUPERSET_URL="$PROTOCOL://$DOMAIN$SUPERSET_PATH"
if curl -I -s -f "$SUPERSET_URL" > /dev/null 2>&1 || curl -I -s -f "$SUPERSET_URL/login" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Superset is accessible at: $SUPERSET_URL"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$SUPERSET_URL/login")
    echo "  HTTP Status Code: $HTTP_CODE"
else
    echo -e "${YELLOW}⚠${NC} Superset is not accessible at: $SUPERSET_URL"
    echo "  Trying direct port access..."
    if curl -I -s -f "$PROTOCOL://$DOMAIN:$SUPERSET_PORT/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Superset is accessible via direct port: $PROTOCOL://$DOMAIN:$SUPERSET_PORT"
    else
        echo -e "${YELLOW}⚠${NC} Superset may not be running or configured"
    fi
fi
echo ""

# Test 5: SSL Certificate (if HTTPS)
if [ "$USE_HTTPS" = "true" ]; then
    echo "Test 5: SSL Certificate"
    echo "-----------------------"
    if openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" < /dev/null 2>/dev/null | openssl x509 -noout -dates > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} SSL certificate is valid"
        EXPIRY=$(echo | openssl s_client -connect "$DOMAIN:443" -servername "$DOMAIN" 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
        echo "  Expires: $EXPIRY"
    else
        echo -e "${YELLOW}⚠${NC} SSL certificate validation failed or not available"
    fi
    echo ""
fi

# Test 6: Docker Services (if running locally)
echo "Test 6: Docker Services Status"
echo "-------------------------------"
if command -v docker > /dev/null 2>&1; then
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(odoo|superset)" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Docker services are running:"
        docker ps --format "  {{.Names}}: {{.Status}}" | grep -E "(odoo|superset)"
    else
        echo -e "${YELLOW}⚠${NC} No Docker services found running"
        echo "  Run: docker compose up -d"
    fi
else
    echo -e "${YELLOW}⚠${NC} Docker is not installed or not accessible"
fi
echo ""

# Summary
echo "============================================"
echo "Test Summary"
echo "============================================"
echo ""
echo "Next Steps:"
echo "  1. If tests failed, check:"
echo "     - DNS configuration"
echo "     - Firewall rules"
echo "     - Docker services are running"
echo "     - Caddy reverse proxy configuration"
echo ""
echo "  2. Access your services:"
echo "     - Odoo: $ODOO_URL"
echo "     - Superset: $SUPERSET_URL"
echo ""
echo "  3. For troubleshooting, see:"
echo "     - docs/DOMAIN_CONFIGURATION.md"
echo "     - docs/SUPERSET_DEPLOY.md"
echo ""

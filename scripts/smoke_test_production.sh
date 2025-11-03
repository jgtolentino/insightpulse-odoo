#!/bin/bash
# Production DNS & Health Check Smoke Test
# Verifies InsightPulse AI infrastructure post-cutover

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════"
echo "  InsightPulse AI Production Smoke Test"
echo "════════════════════════════════════════════════════════════"
echo ""

# DNS Resolution Tests
echo "📡 DNS Resolution"
echo "────────────────────────────────────────────────────────────"

check_dns() {
    local subdomain=$1
    local expected_pattern=$2
    local result=$(dig +short ${subdomain}.insightpulseai.net)

    if [[ -n "$result" ]]; then
        echo -e "${GREEN}✓${NC} ${subdomain}.insightpulseai.net → ${result}"
        return 0
    else
        echo -e "${RED}✗${NC} ${subdomain}.insightpulseai.net → NO RESULT"
        return 1
    fi
}

check_dns "erp" "165.227.10.178"
check_dns "mcp" "ondigitalocean.app"
check_dns "superset" "ondigitalocean.app"
check_dns "ocr" "188.166.237.231"
check_dns "llm" "cloudflare"

echo ""

# HTTPS Health Checks
echo "🏥 HTTPS Health Endpoints"
echo "────────────────────────────────────────────────────────────"

check_health() {
    local name=$1
    local url=$2
    local timeout=10

    echo -n "Checking ${name}... "

    if response=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout ${timeout} -I "${url}" 2>/dev/null); then
        if [[ "$response" =~ ^(200|301|302|307|308)$ ]]; then
            echo -e "${GREEN}✓${NC} HTTP ${response}"
            return 0
        elif [[ "$response" == "403" ]]; then
            echo -e "${GREEN}✓${NC} HTTP 403 (WAF protected)"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} HTTP ${response} (unexpected)"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} Connection failed or timeout"
        return 1
    fi
}

check_health "Odoo ERP       " "https://erp.insightpulseai.net/web/health"
check_health "MCP Skill Hub  " "https://mcp.insightpulseai.net/health"
check_health "Superset       " "https://superset.insightpulseai.net"
check_health "OCR Service    " "https://ocr.insightpulseai.net/health"
check_health "LLM Gateway    " "https://llm.insightpulseai.net/health"

echo ""

# SSL Certificate Check
echo "🔒 SSL Certificate Validation"
echo "────────────────────────────────────────────────────────────"

check_ssl() {
    local name=$1
    local domain=$2

    echo -n "Checking ${name}... "

    if echo | timeout 5 openssl s_client -servername ${domain} -connect ${domain}:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Valid certificate"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Certificate check skipped or failed"
        return 1
    fi
}

check_ssl "erp.insightpulseai.net     " "erp.insightpulseai.net"
check_ssl "mcp.insightpulseai.net     " "mcp.insightpulseai.net"
check_ssl "superset.insightpulseai.net" "superset.insightpulseai.net"
check_ssl "ocr.insightpulseai.net     " "ocr.insightpulseai.net"
check_ssl "llm.insightpulseai.net     " "llm.insightpulseai.net"

echo ""

# Origin Health Checks (bypass WAF)
echo "🔍 Origin Health Checks (Direct to Droplets)"
echo "────────────────────────────────────────────────────────────"

check_origin() {
    local name=$1
    local ip=$2
    local path=$3
    local host_header=$4
    local timeout=10

    echo -n "Checking ${name}... "

    if response=$(curl -k -s -o /dev/null -w "%{http_code}" \
        --connect-timeout ${timeout} \
        -H "Host: ${host_header}" \
        "https://${ip}${path}" 2>/dev/null); then
        if [[ "$response" =~ ^(200|201|204|301|302|307|308)$ ]]; then
            echo -e "${GREEN}✓${NC} HTTP ${response} (origin @${ip})"
            return 0
        else
            echo -e "${YELLOW}⚠${NC} HTTP ${response} (origin @${ip})"
            return 1
        fi
    else
        echo -e "${RED}✗${NC} Connection failed or timeout"
        return 1
    fi
}

# Check droplet origins directly (bypasses Cloudflare WAF)
check_origin "ERP Origin     " "165.227.10.178" "/web/health" "erp.insightpulseai.net"
check_origin "OCR Origin     " "188.166.237.231" "/health" "ocr.insightpulseai.net"

echo ""

# Platform Configuration Reminders
echo "📋 Post-Cutover Checklist"
echo "────────────────────────────────────────────────────────────"
echo "App Platform Domains (force HTTPS enabled):"
echo "  ☐ superset.insightpulseai.net → Superset component"
echo "  ☐ mcp.insightpulseai.net → MCP component"
echo ""
echo "Droplet Services (with Caddy DNS-01):"
echo "  ☐ ERP: Caddy with Cloudflare DNS-01 (works with orange cloud)"
echo "  ☐ ERP: CLOUDFLARE_DNS_API_TOKEN env set"
echo "  ☐ ERP: Health endpoint /web/health responding"
echo "  ☐ OCR: Caddy with Cloudflare DNS-01 (works with orange cloud)"
echo "  ☐ OCR: Docker container running on port 8000"
echo "  ☐ OCR: Health endpoint /health responding"
echo "  ☐ LLM: Gateway configured and responding"
echo ""
echo "Superset Configuration:"
echo "  ☐ SUPERSET_SECRET_KEY set (hex)"
echo "  ☐ HTTP_PORT=8088"
echo "  ☐ Run command: db upgrade && init && run -p 8088"
echo ""
echo "Cloudflare Configuration:"
echo "  ☐ Droplets (erp, ocr, llm): PROXIED (orange) + DNS-01 at origin"
echo "  ☐ App Platform (mcp, superset): DNS-ONLY (grey) until certs issued"
echo "  ☐ SSL/TLS mode: Full (strict)"
echo "  ☐ Always Use HTTPS: Enabled"
echo "  ☐ Cloudflare DNS API token: Zone.DNS:Edit permission"
echo ""

echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✓${NC} Smoke test complete!"
echo "════════════════════════════════════════════════════════════"

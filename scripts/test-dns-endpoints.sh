#!/bin/bash
# Test all DNS endpoints for InsightPulse Odoo infrastructure
# Prerequisites: DNS records created, SSL certificates issued

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing DNS endpoints for insightpulseai.net${NC}"
echo ""

# Test results tracking
PASSED=0
FAILED=0
WARNINGS=0

# Function to test HTTP endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=$3
    local check_content=$4

    echo -e "${BLUE}Testing:${NC} $name"
    echo "  URL: $url"

    # HTTP status check
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" -L "$url" --max-time 10 || echo "000")

    if [ "$STATUS" == "$expected_code" ]; then
        echo -e "  ${GREEN}✅ HTTP $STATUS${NC}"

        # Content check if provided
        if [ -n "$check_content" ]; then
            CONTENT=$(curl -s -L "$url" --max-time 10)
            if echo "$CONTENT" | grep -q "$check_content"; then
                echo -e "  ${GREEN}✅ Content verified${NC}"
                ((PASSED++))
            else
                echo -e "  ${YELLOW}⚠️  Content check failed${NC}"
                ((WARNINGS++))
            fi
        else
            ((PASSED++))
        fi
    else
        echo -e "  ${RED}❌ HTTP $STATUS (expected $expected_code)${NC}"
        ((FAILED++))
    fi

    # SSL certificate check
    if [[ "$url" == https://* ]]; then
        SSL_INFO=$(echo | openssl s_client -connect "${url#https://}" -servername "${url#https://}" 2>/dev/null | openssl x509 -noout -dates 2>/dev/null || echo "failed")
        if [ "$SSL_INFO" != "failed" ]; then
            echo -e "  ${GREEN}✅ SSL valid${NC}"
        else
            echo -e "  ${YELLOW}⚠️  SSL check failed${NC}"
            ((WARNINGS++))
        fi
    fi

    echo ""
}

# Function to test DNS resolution
test_dns() {
    local subdomain=$1
    local record_type=$2
    local expected_pattern=$3

    echo -e "${BLUE}DNS Check:${NC} $subdomain ($record_type)"

    RESULT=$(dig +short "$subdomain" "$record_type" @8.8.8.8 || echo "failed")

    if [ "$RESULT" != "failed" ] && [ -n "$RESULT" ]; then
        if [ -n "$expected_pattern" ] && ! echo "$RESULT" | grep -q "$expected_pattern"; then
            echo -e "  ${YELLOW}⚠️  Unexpected result: $RESULT${NC}"
            ((WARNINGS++))
        else
            echo -e "  ${GREEN}✅ Resolved: $RESULT${NC}"
            ((PASSED++))
        fi
    else
        echo -e "  ${RED}❌ Resolution failed${NC}"
        ((FAILED++))
    fi

    echo ""
}

echo "═════════════════════════════════════"
echo "DNS Resolution Tests"
echo "═════════════════════════════════════"
echo ""

# Test DNS records
test_dns "insightpulseai.net" "A" "165.227.10.178"
test_dns "www.insightpulseai.net" "CNAME" "insightpulseai.net"
test_dns "erp.insightpulseai.net" "A" "165.227.10.178"
test_dns "chat.insightpulseai.net" "A" "165.227.10.178"
test_dns "n8n.insightpulseai.net" "A" "165.227.10.178"
test_dns "ocr.insightpulseai.net" "A" "165.227.10.178"
test_dns "gittodoc.insightpulseai.net" "A" "165.227.10.178"
test_dns "superset.insightpulseai.net" "CNAME" "ondigitalocean.app"
test_dns "mcp.insightpulseai.net" "CNAME" "ondigitalocean.app"
test_dns "agent.insightpulseai.net" "CNAME" "agents.do-ai.run"

echo "═════════════════════════════════════"
echo "HTTP/HTTPS Endpoint Tests"
echo "═════════════════════════════════════"
echo ""

# Test HTTPS endpoints
test_endpoint "Root Domain" "https://insightpulseai.net" "200" ""
test_endpoint "WWW Subdomain" "https://www.insightpulseai.net" "200" ""
test_endpoint "Odoo ERP" "https://erp.insightpulseai.net" "200" "Odoo"
test_endpoint "Superset Analytics" "https://superset.insightpulseai.net" "200" ""
test_endpoint "MCP Coordinator" "https://mcp.insightpulseai.net" "200" ""
test_endpoint "DO Gradient Agent" "https://agent.insightpulseai.net" "200" ""
test_endpoint "Mattermost Chat" "https://chat.insightpulseai.net" "200" ""
test_endpoint "n8n Automation" "https://n8n.insightpulseai.net" "200" ""
test_endpoint "OCR Backend" "https://ocr.insightpulseai.net/health" "200" '"status":"ok"'
test_endpoint "GitToDoc Service" "https://gittodoc.insightpulseai.net" "200" ""

echo "═════════════════════════════════════"
echo "Test Summary"
echo "═════════════════════════════════════"
echo ""

TOTAL=$((PASSED + FAILED + WARNINGS))
echo "Total Tests: $TOTAL"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
if [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
fi
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAILED${NC}"
fi

echo ""

if [ $FAILED -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Monitor services with uptime monitoring"
    echo "  2. Setup SSL monitoring for certificate expiry"
    echo "  3. Configure health check alerts"
    exit 0
elif [ $FAILED -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Tests passed with warnings${NC}"
    echo ""
    echo "Review warnings and fix if necessary"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check DNS propagation: dig @8.8.8.8 [subdomain]"
    echo "  2. Check SSL certificates: sudo certbot certificates"
    echo "  3. Check Nginx configs: sudo nginx -t"
    echo "  4. Check Nginx logs: sudo tail -f /var/log/nginx/error.log"
    echo "  5. Check service health: curl https://[subdomain]/health"
    exit 1
fi

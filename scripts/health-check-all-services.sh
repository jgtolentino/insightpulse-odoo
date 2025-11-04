#!/bin/bash
# Comprehensive Health Check for All InsightPulse Services
# Validates DNS, TLS, service endpoints, and infrastructure status

set -euo pipefail

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAINS=(
    "erp.insightpulseai.net"
    "agent.insightpulseai.net"
    "mcp.insightpulseai.net"
    "ocr.insightpulseai.net"
    "superset.insightpulseai.net"
    "llm.insightpulseai.net"
)

DROPLET_IPS=(
    "165.227.10.178"  # ERP droplet
    "188.166.237.231" # OCR droplet
)

# Helper functions
check_mark() {
    echo -e "${GREEN}✅${NC}"
}

x_mark() {
    echo -e "${RED}❌${NC}"
}

warning_mark() {
    echo -e "${YELLOW}⚠️${NC}"
}

print_header() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "$1"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

print_section() {
    echo ""
    echo "─────────────────────────────────────────"
    echo "$1"
    echo "─────────────────────────────────────────"
}

# Main health check
main() {
    print_header "🔍 InsightPulse Infrastructure Health Check"
    echo "Starting comprehensive validation..."
    echo ""

    # Initialize counters
    total_checks=0
    passed_checks=0
    failed_checks=0
    warning_checks=0

    # 1. DNS Resolution Checks
    print_section "1. DNS Resolution"
    for domain in "${DOMAINS[@]}"; do
        total_checks=$((total_checks + 1))
        echo -n "Checking $domain... "

        if dig +short "$domain" A | grep -q .; then
            ip=$(dig +short "$domain" A | head -n1)
            echo -e "$(check_mark) Resolves to: $ip"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "$(x_mark) Failed to resolve"
            failed_checks=$((failed_checks + 1))
        fi
    done

    # 2. HTTPS Connectivity Checks
    print_section "2. HTTPS Connectivity"
    for domain in "${DOMAINS[@]}"; do
        total_checks=$((total_checks + 1))
        echo -n "Checking https://$domain... "

        status_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "https://$domain" 2>/dev/null || echo "000")

        if [[ "$status_code" =~ ^(200|301|302)$ ]]; then
            echo -e "$(check_mark) HTTP $status_code"
            passed_checks=$((passed_checks + 1))
        elif [[ "$status_code" == "000" ]]; then
            echo -e "$(x_mark) Connection failed"
            failed_checks=$((failed_checks + 1))
        else
            echo -e "$(warning_mark) HTTP $status_code"
            warning_checks=$((warning_checks + 1))
        fi
    done

    # 3. TLS Certificate Checks
    print_section "3. TLS Certificate Validation"
    for domain in "${DOMAINS[@]}"; do
        total_checks=$((total_checks + 1))
        echo -n "Checking TLS for $domain... "

        if echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | grep -q "Verify return code: 0"; then
            expiry=$(echo | openssl s_client -servername "$domain" -connect "$domain:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
            echo -e "$(check_mark) Valid until: $expiry"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "$(x_mark) Invalid or expired"
            failed_checks=$((failed_checks + 1))
        fi
    done

    # 4. Service-Specific Endpoint Checks
    print_section "4. Service Endpoint Validation"

    # ERP Odoo
    total_checks=$((total_checks + 1))
    echo -n "ERP (Odoo) web interface... "
    if curl -s -o /dev/null -w "%{http_code}" "https://erp.insightpulseai.net/web" 2>/dev/null | grep -q "200"; then
        echo -e "$(check_mark) Accessible"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "$(x_mark) Not accessible"
        failed_checks=$((failed_checks + 1))
    fi

    # OCR PaddleOCR
    total_checks=$((total_checks + 1))
    echo -n "OCR PaddleOCR health... "
    if curl -s "http://ocr.insightpulseai.net/paddle/health" 2>/dev/null | jq -e '.status == "ok"' >/dev/null 2>&1; then
        echo -e "$(check_mark) Healthy"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "$(x_mark) Unhealthy or unreachable"
        failed_checks=$((failed_checks + 1))
    fi

    # OCR DeepSeek-OCR
    total_checks=$((total_checks + 1))
    echo -n "OCR DeepSeek-OCR health... "
    if curl -s "http://ocr.insightpulseai.net/dsocr/health" 2>/dev/null | jq -e '.status == "ok"' >/dev/null 2>&1; then
        echo -e "$(check_mark) Healthy"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "$(warning_mark) Not deployed or unreachable"
        warning_checks=$((warning_checks + 1))
    fi

    # LLM DeepSeek-R1
    total_checks=$((total_checks + 1))
    echo -n "LLM DeepSeek-R1 models endpoint... "
    if curl -s "https://llm.insightpulseai.net/v1/models" 2>/dev/null | jq -e '.data[0].id' >/dev/null 2>&1; then
        echo -e "$(check_mark) Available"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "$(warning_mark) Not deployed or unreachable"
        warning_checks=$((warning_checks + 1))
    fi

    # Pulse Hub Web UI
    total_checks=$((total_checks + 1))
    echo -n "Pulse Hub Web UI... "
    if curl -s -o /dev/null -w "%{http_code}" "https://mcp.insightpulseai.net" 2>/dev/null | grep -q "200"; then
        echo -e "$(check_mark) Accessible"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "$(x_mark) Not accessible"
        failed_checks=$((failed_checks + 1))
    fi

    # Superset BI
    total_checks=$((total_checks + 1))
    echo -n "Superset BI Dashboard... "
    if curl -s -o /dev/null -w "%{http_code}" "https://superset.insightpulseai.net" 2>/dev/null | grep -q "200"; then
        echo -e "$(check_mark) Accessible"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "$(x_mark) Not accessible"
        failed_checks=$((failed_checks + 1))
    fi

    # AI Agent API
    total_checks=$((total_checks + 1))
    echo -n "AI Agent API... "
    agent_status=$(curl -s -o /dev/null -w "%{http_code}" "https://agent.insightpulseai.net" 2>/dev/null || echo "000")
    if [[ "$agent_status" =~ ^(200|401|403)$ ]]; then
        echo -e "$(check_mark) Reachable (HTTP $agent_status)"
        passed_checks=$((passed_checks + 1))
    else
        echo -e "$(warning_mark) DNS not configured or unreachable"
        warning_checks=$((warning_checks + 1))
    fi

    # 5. Droplet SSH Connectivity
    print_section "5. Droplet SSH Connectivity"
    for ip in "${DROPLET_IPS[@]}"; do
        total_checks=$((total_checks + 1))
        echo -n "Checking SSH to $ip... "

        if timeout 5 ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no root@"$ip" "echo 'SSH OK'" 2>/dev/null | grep -q "SSH OK"; then
            echo -e "$(check_mark) SSH accessible"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "$(x_mark) SSH connection failed"
            failed_checks=$((failed_checks + 1))
        fi
    done

    # 6. Supabase Database Connectivity
    print_section "6. Database Connectivity"
    total_checks=$((total_checks + 1))
    echo -n "Checking Supabase PostgreSQL... "

    if [[ -n "${POSTGRES_URL:-}" ]]; then
        if psql "$POSTGRES_URL" -c "SELECT 1" >/dev/null 2>&1; then
            echo -e "$(check_mark) Connected"
            passed_checks=$((passed_checks + 1))
        else
            echo -e "$(x_mark) Connection failed"
            failed_checks=$((failed_checks + 1))
        fi
    else
        echo -e "$(warning_mark) POSTGRES_URL not set in environment"
        warning_checks=$((warning_checks + 1))
    fi

    # Summary
    print_header "📊 Health Check Summary"

    echo "Total Checks: $total_checks"
    echo -e "$(check_mark) Passed: $passed_checks"
    echo -e "$(x_mark) Failed: $failed_checks"
    echo -e "$(warning_mark) Warnings: $warning_checks"
    echo ""

    success_rate=$((passed_checks * 100 / total_checks))
    echo "Success Rate: ${success_rate}%"
    echo ""

    if [[ $failed_checks -eq 0 && $warning_checks -eq 0 ]]; then
        echo -e "${GREEN}✅ All systems operational!${NC}"
        exit 0
    elif [[ $failed_checks -eq 0 ]]; then
        echo -e "${YELLOW}⚠️ Some services have warnings but core systems are functional${NC}"
        exit 0
    else
        echo -e "${RED}❌ Critical issues detected - $failed_checks services failing${NC}"
        exit 1
    fi
}

# Run main function
main

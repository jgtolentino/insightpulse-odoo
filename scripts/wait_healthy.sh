#!/bin/bash
# Origin health check script for WAF-proxied services
# This script checks the health of services directly at their origin IP,
# bypassing Cloudflare WAF which may return 403 for automated requests.
#
# Usage:
#   ./wait_healthy.sh <base_url> [<path>] [<host_header>] [<max_attempts>] [<retry_delay>]
#
# Examples:
#   # Check ERP droplet directly
#   ./wait_healthy.sh "https://165.227.10.178" "/web/health" "erp.insightpulseai.net"
#
#   # Check OCR droplet directly
#   ./wait_healthy.sh "https://188.166.237.231" "/health" "ocr.insightpulseai.net"
#
#   # Check with custom retries
#   ./wait_healthy.sh "https://165.227.10.178" "/web/health" "erp.insightpulseai.net" 30 10

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Arguments
BASE_URL="${1}"
HEALTH_PATH="${2:-/health}"
HOST_HEADER="${3:-}"
MAX_ATTEMPTS="${4:-30}"
RETRY_DELAY="${5:-5}"

# Validate required arguments
if [[ -z "${BASE_URL}" ]]; then
    echo -e "${RED}Error: BASE_URL is required${NC}"
    echo "Usage: $0 <base_url> [<path>] [<host_header>] [<max_attempts>] [<retry_delay>]"
    exit 1
fi

# Build full URL
FULL_URL="${BASE_URL}${HEALTH_PATH}"

# Build curl command
CURL_CMD="curl -k -s -o /dev/null -w %{http_code}"

# Add Host header if provided
if [[ -n "${HOST_HEADER}" ]]; then
    CURL_CMD="${CURL_CMD} -H \"Host: ${HOST_HEADER}\""
fi

CURL_CMD="${CURL_CMD} \"${FULL_URL}\""

# Display configuration
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Origin Health Check${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "Base URL:      ${BASE_URL}"
echo -e "Health Path:   ${HEALTH_PATH}"
echo -e "Full URL:      ${FULL_URL}"
[[ -n "${HOST_HEADER}" ]] && echo -e "Host Header:   ${HOST_HEADER}"
echo -e "Max Attempts:  ${MAX_ATTEMPTS}"
echo -e "Retry Delay:   ${RETRY_DELAY}s"
echo -e "${BLUE}────────────────────────────────────────────────────────────${NC}"
echo ""

# Health check loop
ATTEMPT=0
while [[ ${ATTEMPT} -lt ${MAX_ATTEMPTS} ]]; do
    ATTEMPT=$((ATTEMPT + 1))

    echo -ne "${YELLOW}[${ATTEMPT}/${MAX_ATTEMPTS}]${NC} Checking health... "

    # Execute curl with optional Host header
    if [[ -n "${HOST_HEADER}" ]]; then
        HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" \
            -H "Host: ${HOST_HEADER}" \
            --connect-timeout 10 \
            --max-time 30 \
            "${FULL_URL}" 2>/dev/null || echo "000")
    else
        HTTP_CODE=$(curl -k -s -o /dev/null -w "%{http_code}" \
            --connect-timeout 10 \
            --max-time 30 \
            "${FULL_URL}" 2>/dev/null || echo "000")
    fi

    # Check if HTTP code indicates success
    if [[ "${HTTP_CODE}" =~ ^(200|201|204|301|302|307|308)$ ]]; then
        echo -e "${GREEN}✓ HTTP ${HTTP_CODE}${NC}"
        echo ""
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  Service is healthy!${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
        exit 0
    elif [[ "${HTTP_CODE}" == "000" ]]; then
        echo -e "${RED}✗ Connection failed${NC}"
    else
        echo -e "${YELLOW}⚠ HTTP ${HTTP_CODE}${NC}"
    fi

    # Don't sleep on last attempt
    if [[ ${ATTEMPT} -lt ${MAX_ATTEMPTS} ]]; then
        echo -e "   Retrying in ${RETRY_DELAY}s..."
        sleep ${RETRY_DELAY}
    fi
done

# Failed after all attempts
echo ""
echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
echo -e "${RED}  Health check failed after ${MAX_ATTEMPTS} attempts${NC}"
echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
exit 1

#!/bin/bash
# Setup DNS record for agent.insightpulseai.net pointing to DO AI Agent
#
# Usage:
#   ./scripts/setup-dns.sh <agent-url>
#
# Example:
#   ./scripts/setup-dns.sh wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run

set -e

AGENT_URL="${1:-wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run}"
DOMAIN="insightpulseai.net"
SUBDOMAIN="agent"
FULL_DOMAIN="${SUBDOMAIN}.${DOMAIN}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== DNS Setup for Multi-Agent Orchestrator ===${NC}"
echo "Domain: $FULL_DOMAIN"
echo "Target: $AGENT_URL"

# Check if doctl is authenticated
if ! doctl account get &>/dev/null; then
    echo -e "${RED}Error: doctl not authenticated. Run 'doctl auth init'${NC}"
    exit 1
fi

# Check if domain exists in DO
if ! doctl compute domain list --format Domain --no-header | grep -q "^$DOMAIN$"; then
    echo -e "${RED}Error: Domain $DOMAIN not found in DigitalOcean${NC}"
    echo "Please add the domain first using: doctl compute domain create $DOMAIN"
    exit 1
fi

echo -e "${YELLOW}Creating CNAME record...${NC}"

# Delete existing record if present
EXISTING_RECORD_ID=$(doctl compute domain records list "$DOMAIN" \
    --format ID,Type,Name --no-header | \
    grep "CNAME.*$SUBDOMAIN" | awk '{print $1}' || true)

if [ -n "$EXISTING_RECORD_ID" ]; then
    echo -e "${YELLOW}Deleting existing CNAME record (ID: $EXISTING_RECORD_ID)...${NC}"
    doctl compute domain records delete "$DOMAIN" "$EXISTING_RECORD_ID" --force
fi

# Create CNAME record
RECORD_ID=$(doctl compute domain records create "$DOMAIN" \
    --record-type CNAME \
    --record-name "$SUBDOMAIN" \
    --record-data "$AGENT_URL." \
    --record-ttl 3600 \
    --format ID --no-header)

echo -e "${GREEN}✓ CNAME record created (ID: $RECORD_ID)${NC}"

# Verify DNS record
echo -e "${YELLOW}Verifying DNS record...${NC}"
doctl compute domain records list "$DOMAIN" --format ID,Type,Name,Data,TTL | grep "$SUBDOMAIN"

echo -e "${GREEN}=== DNS Setup Complete ===${NC}"
echo ""
echo "DNS record created:"
echo "  $FULL_DOMAIN -> $AGENT_URL"
echo ""
echo "⚠️  Note: DNS propagation may take up to 48 hours (typically 5-30 minutes)"
echo ""
echo "Test propagation with:"
echo "  dig $FULL_DOMAIN"
echo "  nslookup $FULL_DOMAIN"
echo ""
echo "Once propagated, test the endpoint:"
echo "  curl https://$FULL_DOMAIN/health"

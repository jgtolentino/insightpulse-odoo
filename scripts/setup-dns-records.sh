#!/bin/bash
# Setup DNS records for InsightPulse Odoo infrastructure

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌐 Setting up DNS records for insightpulseai.net${NC}"
echo ""

# Server IP (Nginx reverse proxy server)
SERVER_IP="165.227.10.178"
DOMAIN="insightpulseai.net"

# Check if doctl is authenticated
if ! doctl account get &> /dev/null; then
    echo -e "${RED}❌ Error: doctl not authenticated${NC}"
    echo "Run: doctl auth init"
    exit 1
fi

# Dry run mode
DRY_RUN=false
if [ "$1" == "--dry-run" ]; then
    DRY_RUN=true
    echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
    echo ""
fi

# Function to create DNS record
create_dns_record() {
    local record_type=$1
    local record_name=$2
    local record_data=$3
    local ttl=${4:-3600}

    if [ "$DRY_RUN" = true ]; then
        echo -e "${YELLOW}[DRY RUN]${NC} Would create: $record_type $record_name.$DOMAIN → $record_data (TTL: $ttl)"
    else
        echo -e "${BLUE}Creating:${NC} $record_type $record_name.$DOMAIN → $record_data"

        if doctl compute domain records create $DOMAIN \
            --record-type $record_type \
            --record-name $record_name \
            --record-data $record_data \
            --record-ttl $ttl 2>/dev/null; then
            echo -e "${GREEN}✅ Created:${NC} $record_name.$DOMAIN"
        else
            echo -e "${YELLOW}⚠️  Record may already exist:${NC} $record_name.$DOMAIN"
        fi
    fi
}

echo "DNS Records to be created:"
echo "=========================="
echo ""

# 1. Root domain (bare domain)
echo "1. Root domain (A record)"
create_dns_record "A" "@" "$SERVER_IP"
sleep 1

# 2. WWW subdomain
echo ""
echo "2. WWW subdomain (CNAME)"
create_dns_record "CNAME" "www" "$DOMAIN"
sleep 1

# 3. Local services (A records pointing to Nginx server)
echo ""
echo "3. Local services (A records)"

LOCAL_SERVICES=(
    "chat:Mattermost Chat"
    "n8n:n8n Workflow Automation"
    "ocr:OCR Backend"
    "gittodoc:Git to Docs"
)

for service in "${LOCAL_SERVICES[@]}"; do
    IFS=':' read -r subdomain description <<< "$service"
    echo ""
    echo "   $description"
    create_dns_record "A" "$subdomain" "$SERVER_IP"
    sleep 1
done

# 4. DigitalOcean App Platform services (CNAME records)
echo ""
echo "4. DigitalOcean App Platform services (CNAME)"

DO_APPS=(
    "superset:superset-nlavf.ondigitalocean.app:Superset Analytics"
    "mcp:pulse-hub-web-an645.ondigitalocean.app:MCP Coordinator"
)

for app in "${DO_APPS[@]}"; do
    IFS=':' read -r subdomain target description <<< "$app"
    echo ""
    echo "   $description"
    create_dns_record "CNAME" "$subdomain" "$target"
    sleep 1
done

# 5. DigitalOcean Gradient AI Agent (CNAME record)
echo ""
echo "5. DigitalOcean Gradient AI Agent (CNAME)"
create_dns_record "CNAME" "agent" "wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run"

echo ""
echo "==============================="

if [ "$DRY_RUN" = true ]; then
    echo -e "${GREEN}✅ Dry run complete${NC}"
    echo "Review the records above and run without --dry-run to create them"
else
    echo -e "${GREEN}✅ DNS records creation complete${NC}"
    echo ""
    echo "⏳ DNS propagation typically takes 30-60 minutes"
    echo ""
    echo "Verify DNS propagation:"
    echo "  dig @8.8.8.8 superset.insightpulseai.net"
    echo "  dig @8.8.8.8 mcp.insightpulseai.net"
    echo ""
    echo "Next steps:"
    echo "  1. Wait for DNS propagation (30-60 minutes)"
    echo "  2. Issue SSL certificates: ./scripts/issue-ssl-certificates.sh"
    echo "  3. Test endpoints: ./scripts/test-dns-endpoints.sh"
fi

echo ""

# List all DNS records
if [ "$DRY_RUN" = false ]; then
    echo "Current DNS records for $DOMAIN:"
    echo "================================="
    doctl compute domain records list $DOMAIN --format Type,Name,Data,TTL
fi

echo ""

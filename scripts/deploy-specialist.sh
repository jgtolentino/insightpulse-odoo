#!/bin/bash
# Deploy or update a specialist agent service on DigitalOcean App Platform
#
# Usage:
#   ./scripts/deploy-specialist.sh odoo-developer-agent
#   ./scripts/deploy-specialist.sh finance-ssc-expert
#   ./scripts/deploy-specialist.sh bi-architect
#   ./scripts/deploy-specialist.sh devops-engineer
#
# Prerequisites:
#   - doctl CLI installed and authenticated
#   - DO_ACCESS_TOKEN environment variable set
#   - App Platform spec files in infra/do/

set -e  # Exit on error
set -u  # Exit on undefined variable

AGENT_NAME="${1:-}"
SPEC_FILE="infra/do/${AGENT_NAME}.yaml"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
RED='\033[0.31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validate arguments
if [ -z "$AGENT_NAME" ]; then
    echo -e "${RED}Error: Agent name required${NC}"
    echo "Usage: $0 <agent-name>"
    echo "Available agents:"
    echo "  - odoo-developer-agent"
    echo "  - finance-ssc-expert"
    echo "  - bi-architect"
    echo "  - devops-engineer"
    exit 1
fi

# Validate spec file exists
if [ ! -f "$PROJECT_ROOT/$SPEC_FILE" ]; then
    echo -e "${RED}Error: Spec file not found: $SPEC_FILE${NC}"
    exit 1
fi

echo -e "${GREEN}=== Deploying Specialist Agent: $AGENT_NAME ===${NC}"

# Validate DO token
if [ -z "${DO_ACCESS_TOKEN:-}" ]; then
    echo -e "${YELLOW}Warning: DO_ACCESS_TOKEN not set. Checking doctl auth...${NC}"
    if ! doctl auth list | grep -q "current context"; then
        echo -e "${RED}Error: Not authenticated with doctl. Run 'doctl auth init'${NC}"
        exit 1
    fi
fi

# Validate spec file
echo -e "${YELLOW}Validating App Platform spec...${NC}"
if ! doctl apps spec validate "$PROJECT_ROOT/$SPEC_FILE"; then
    echo -e "${RED}Error: Invalid App Platform spec${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Spec validation passed${NC}"

# Check if app already exists
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$AGENT_NAME" | awk '{print $1}' || true)

if [ -z "$APP_ID" ]; then
    # Create new app
    echo -e "${YELLOW}Creating new app: $AGENT_NAME...${NC}"
    APP_ID=$(doctl apps create --spec "$PROJECT_ROOT/$SPEC_FILE" --format ID --no-header)
    echo -e "${GREEN}✓ App created with ID: $APP_ID${NC}"
else
    # Update existing app
    echo -e "${YELLOW}Updating existing app ID: $APP_ID...${NC}"
    doctl apps update "$APP_ID" --spec "$PROJECT_ROOT/$SPEC_FILE"
    echo -e "${GREEN}✓ App updated${NC}"
fi

# Trigger deployment
echo -e "${YELLOW}Triggering deployment (force rebuild)...${NC}"
DEPLOYMENT_ID=$(doctl apps create-deployment "$APP_ID" --force-rebuild --format ID --no-header)
echo -e "${GREEN}✓ Deployment triggered with ID: $DEPLOYMENT_ID${NC}"

# Wait for deployment (optional - can be skipped for async deployment)
echo -e "${YELLOW}Waiting for deployment to complete (this may take 3-5 minutes)...${NC}"
while true; do
    STATUS=$(doctl apps get-deployment "$APP_ID" "$DEPLOYMENT_ID" --format Phase --no-header)

    case "$STATUS" in
        "ACTIVE")
            echo -e "${GREEN}✓ Deployment successful!${NC}"
            break
            ;;
        "ERROR"|"CANCELED")
            echo -e "${RED}✗ Deployment failed with status: $STATUS${NC}"
            echo -e "${YELLOW}Fetching deployment logs...${NC}"
            doctl apps logs "$APP_ID" --deployment "$DEPLOYMENT_ID" --type BUILD
            exit 1
            ;;
        *)
            echo -n "."
            sleep 10
            ;;
    esac
done

# Get app URL
APP_URL=$(doctl apps get "$APP_ID" --format DefaultIngress --no-header)
echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo "App ID: $APP_ID"
echo "URL: https://$APP_URL"
echo ""
echo "Next steps:"
echo "1. Test health endpoint: curl https://$APP_URL/health"
echo "2. Test capabilities endpoint: curl https://$APP_URL/capabilities"
echo "3. Add routing tool to DO AI Agent orchestrator"
echo "4. Test multi-agent coordination"

# Optional: Test health endpoint
if command -v curl &> /dev/null; then
    echo -e "${YELLOW}Testing health endpoint...${NC}"
    sleep 5  # Give service time to start
    if curl -sf "https://$APP_URL/health" | jq -r '.status'; then
        echo -e "${GREEN}✓ Health check passed${NC}"
    else
        echo -e "${RED}✗ Health check failed (service may still be starting)${NC}"
    fi
fi

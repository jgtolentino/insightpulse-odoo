#!/bin/bash
# DigitalOcean App Platform Deployment Script
# Leverages the installed DigitalOcean GitHub App

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 DigitalOcean App Platform Deployment${NC}"
echo "========================================="

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}❌ doctl is not installed${NC}"
    echo "Install: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if authenticated
if ! doctl auth list &> /dev/null; then
    echo -e "${RED}❌ Not authenticated with DigitalOcean${NC}"
    echo "Run: doctl auth init"
    exit 1
fi

echo -e "${GREEN}✅ doctl authenticated${NC}"

# Validate spec file
echo ""
echo "Validating app.yaml..."
if doctl apps spec validate "$SCRIPT_DIR/app.yaml"; then
    echo -e "${GREEN}✅ app.yaml is valid${NC}"
else
    echo -e "${RED}❌ app.yaml validation failed${NC}"
    exit 1
fi

# Check if app exists
APP_NAME="insightpulse-odoo"
echo ""
echo "Checking for existing app..."
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}' || echo "")

if [ -z "$APP_ID" ]; then
    echo -e "${YELLOW}⚠️  App not found, creating new app...${NC}"

    # Create new app
    doctl apps create --spec "$SCRIPT_DIR/app.yaml" --wait

    echo -e "${GREEN}✅ App created successfully${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Set secrets in DO dashboard:"
    echo "   - ODOO_ADMIN_PASSWORD"
    echo ""
    echo "2. Configure custom domain DNS:"
    echo "   - Add A record: insightpulseai.net → <app-ip>"
    echo "   - Add CNAME: www → <app-url>"
    echo ""
    echo "3. Enable PR previews:"
    echo "   - Dashboard → Settings → Deploy Pull Request Previews"

else
    echo -e "${GREEN}✅ Found existing app: $APP_ID${NC}"

    # Update existing app
    echo ""
    read -p "Update existing app? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Updating app..."
        doctl apps update "$APP_ID" --spec "$SCRIPT_DIR/app.yaml"
        echo -e "${GREEN}✅ App updated${NC}"
    else
        echo "Skipping update"
    fi
fi

# Show app info
echo ""
echo "App Information:"
doctl apps get "$APP_ID" --format ID,Spec.Name,DefaultIngress,ActiveDeployment.CreatedAt

echo ""
echo -e "${GREEN}🎉 Done!${NC}"
echo ""
echo "View app: https://cloud.digitalocean.com/apps/$APP_ID"
echo "Logs: doctl apps logs $APP_ID --type RUN --follow"

#!/bin/bash
# Skill Hub Deployment Script for DigitalOcean App Platform

set -e

echo "🚀 Deploying Skill Hub to DigitalOcean App Platform..."

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo "❌ doctl CLI not found. Install it first:"
    echo "   brew install doctl"
    echo "   or visit: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi

# Check if logged in
if ! doctl account get &> /dev/null; then
    echo "❌ Not authenticated with DigitalOcean."
    echo "   Run: doctl auth init"
    exit 1
fi

# Set variables
APP_SPEC="../infra/do/skill-hub-app.yaml"
APP_NAME="skill-hub"

echo "📋 Using app spec: $APP_SPEC"

# Check if app exists
APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "$APP_NAME" | awk '{print $1}' || echo "")

if [ -z "$APP_ID" ]; then
    echo "🆕 Creating new app..."
    doctl apps create --spec "$APP_SPEC"
else
    echo "🔄 Updating existing app (ID: $APP_ID)..."
    doctl apps update "$APP_ID" --spec "$APP_SPEC"
fi

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "Next steps:"
echo "1. Set secrets in DigitalOcean App Platform console:"
echo "   - BEARER_TOKEN"
echo "   - ODOO_USERNAME"
echo "   - ODOO_PASSWORD"
echo "   - SUPERSET_USERNAME"
echo "   - SUPERSET_PASSWORD"
echo ""
echo "2. Configure DNS:"
echo "   Add CNAME record: mcp.insightpulseai.net -> <your-app-domain>.ondigitalocean.app"
echo ""
echo "3. Monitor deployment:"
echo "   doctl apps list"
echo "   doctl apps logs $APP_NAME"
echo ""
echo "4. Test endpoints:"
echo "   curl https://mcp.insightpulseai.net/health"
echo ""

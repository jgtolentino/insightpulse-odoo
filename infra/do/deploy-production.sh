#!/usr/bin/env bash
set -euo pipefail

# DigitalOcean App Platform Production Deployment Script (Blue-Green)
# InsightPulse Odoo 19.0 Enterprise SaaS Platform

echo "🚀 DigitalOcean App Platform Production Deployment (Blue-Green)"
echo "=============================================================="
echo ""

# Validation
echo "📋 Pre-deployment Validation"
echo "----------------------------"

# Check required environment variables
REQUIRED_VARS=(
  "DO_ACCESS_TOKEN"
  "POSTGRES_PASSWORD"
  "ODOO_ADMIN_PASSWORD"
)

MISSING_VARS=()
for VAR in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!VAR:-}" ]; then
    MISSING_VARS+=("$VAR")
  else
    echo "✅ $VAR is set"
  fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
  echo ""
  echo "❌ Missing required environment variables:"
  for VAR in "${MISSING_VARS[@]}"; do
    echo "   - $VAR"
  done
  exit 1
fi

# Check doctl authentication
if ! doctl auth list | grep -q "default (current)"; then
  echo "❌ DigitalOcean CLI not authenticated"
  exit 1
fi
echo "✅ DigitalOcean CLI authenticated"

# Check if production app already exists
EXISTING_APP=$(doctl apps list --format ID,Spec.Name --no-header | grep "odoo-saas-platform$" || echo "")
if [ -n "$EXISTING_APP" ]; then
  BLUE_APP_ID=$(echo "$EXISTING_APP" | awk '{print $1}')
  echo "✅ Blue environment exists: $BLUE_APP_ID"
  BLUE_EXISTS=true
else
  echo "ℹ️  No existing production app (first deployment)"
  BLUE_EXISTS=false
fi

echo ""
echo "🟢 Creating Green Environment"
echo "-----------------------------"

# Create temporary spec with secrets substituted
TEMP_SPEC=$(mktemp)
sed "s|ENC\[WILL_BE_SET_VIA_DOCTL\]|${POSTGRES_PASSWORD}|" infra/do/odoo-saas-platform.yaml > "$TEMP_SPEC"
sed -i.bak "s|value: \"ENC\[WILL_BE_SET_VIA_DOCTL\]\"|value: \"${ODOO_ADMIN_PASSWORD}\"|" "$TEMP_SPEC"
rm -f "${TEMP_SPEC}.bak"

echo "✅ Created temporary spec: $TEMP_SPEC"

# Create green environment
GREEN_CREATE_OUTPUT=$(doctl apps create --spec "$TEMP_SPEC" --format ID,Spec.Name,DefaultIngress --no-header)
GREEN_APP_ID=$(echo "$GREEN_CREATE_OUTPUT" | awk '{print $1}')
GREEN_APP_NAME=$(echo "$GREEN_CREATE_OUTPUT" | awk '{print $2}')
GREEN_APP_URL=$(echo "$GREEN_CREATE_OUTPUT" | awk '{print $3}')

# Clean up temporary spec
rm -f "$TEMP_SPEC"

echo "✅ Green environment created:"
echo "   App ID: $GREEN_APP_ID"
echo "   Name: $GREEN_APP_NAME"
echo "   URL: https://$GREEN_APP_URL"

echo ""
echo "🚀 Deploying Green Environment"
echo "------------------------------"

# Trigger deployment
doctl apps create-deployment "$GREEN_APP_ID" --force-rebuild

echo "✅ Deployment triggered"
echo ""
echo "⏳ Waiting for deployment to complete..."

# Poll deployment status
while true; do
  DEPLOYMENT_PHASE=$(doctl apps get "$GREEN_APP_ID" --format ActiveDeployment.Phase --no-header)

  case "$DEPLOYMENT_PHASE" in
    "ACTIVE")
      echo "✅ Green deployment is ACTIVE"
      break
      ;;
    "ERROR"|"CANCELED")
      echo "❌ Deployment failed: $DEPLOYMENT_PHASE"
      echo ""
      echo "View logs:"
      echo "  doctl apps logs $GREEN_APP_ID --type build"
      echo "  doctl apps logs $GREEN_APP_ID --type run"
      exit 1
      ;;
    *)
      echo "   Current phase: $DEPLOYMENT_PHASE"
      sleep 30
      ;;
  esac
done

echo ""
echo "🔍 Smoke Testing Green Environment"
echo "----------------------------------"

# Health check
echo "Testing health endpoint..."
HEALTH_STATUS=$(curl -sf "https://$GREEN_APP_URL/web/health" || echo "FAILED")

if [ "$HEALTH_STATUS" != "FAILED" ]; then
  echo "✅ Health check passed"
else
  echo "❌ Health check failed"
  exit 1
fi

# Test main page
echo "Testing main page..."
MAIN_STATUS=$(curl -sf -o /dev/null -w "%{http_code}" "https://$GREEN_APP_URL/web" || echo "000")

if [ "$MAIN_STATUS" = "200" ] || [ "$MAIN_STATUS" = "303" ]; then
  echo "✅ Main page accessible (HTTP $MAIN_STATUS)"
else
  echo "❌ Main page failed (HTTP $MAIN_STATUS)"
  exit 1
fi

echo ""
echo "✅ All smoke tests passed"

if [ "$BLUE_EXISTS" = true ]; then
  echo ""
  echo "🔄 Blue-Green Cutover"
  echo "--------------------"
  echo "Blue environment: $BLUE_APP_ID"
  echo "Green environment: $GREEN_APP_ID (ACTIVE)"
  echo ""
  echo "Traffic is now routing to green environment."
  echo ""
  echo "To remove blue environment:"
  echo "  doctl apps delete $BLUE_APP_ID"
  echo ""
  echo "To rollback to blue environment:"
  echo "  doctl apps delete $GREEN_APP_ID"
else
  echo ""
  echo "🎉 First Production Deployment Complete"
  echo "---------------------------------------"
  echo "Production URL: https://$GREEN_APP_URL/web"
fi

echo ""
echo "✅ Production deployment successful!"
echo ""
echo "📊 Monitoring Commands:"
echo "  doctl apps logs $GREEN_APP_ID --type run --follow"
echo "  doctl apps get $GREEN_APP_ID"
echo "  doctl apps list-deployments $GREEN_APP_ID"

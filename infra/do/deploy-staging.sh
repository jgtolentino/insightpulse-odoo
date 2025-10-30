#!/usr/bin/env bash
set -euo pipefail

# DigitalOcean App Platform Staging Deployment Script
# InsightPulse Odoo 19.0 Enterprise SaaS Platform

echo "🚀 DigitalOcean App Platform Staging Deployment"
echo "================================================"
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
  echo ""
  echo "Set them with:"
  echo "  export POSTGRES_PASSWORD='your_supabase_postgres_password'"
  echo "  export ODOO_ADMIN_PASSWORD=\"\$(openssl rand -base64 32)\""
  exit 1
fi

# Check doctl authentication
if ! doctl auth list | grep -q "default (current)"; then
  echo "❌ DigitalOcean CLI not authenticated"
  echo "Run: doctl auth init"
  exit 1
fi
echo "✅ DigitalOcean CLI authenticated"

# Check if staging app already exists
EXISTING_APP=$(doctl apps list --format Spec.Name --no-header | grep "odoo-saas-platform-staging" || echo "")
if [ -n "$EXISTING_APP" ]; then
  echo "⚠️  Staging app already exists"
  echo "Delete it first with:"
  echo "  doctl apps delete [app-id]"
  exit 1
fi
echo "✅ No existing staging app found"

echo ""
echo "🔧 Preparing Staging App Spec"
echo "-----------------------------"

# Create temporary spec with secrets substituted
TEMP_SPEC=$(mktemp)
sed "s|ENC\[WILL_BE_SET_VIA_DOCTL\]|${POSTGRES_PASSWORD}|" infra/do/odoo-saas-platform-staging.yaml > "$TEMP_SPEC"
sed -i.bak "s|value: \"ENC\[WILL_BE_SET_VIA_DOCTL\]\"|value: \"${ODOO_ADMIN_PASSWORD}\"|" "$TEMP_SPEC"
rm -f "${TEMP_SPEC}.bak"

echo "✅ Created temporary spec with secrets: $TEMP_SPEC"

echo ""
echo "📦 Creating Staging App"
echo "-----------------------"

# Create app from spec
APP_CREATE_OUTPUT=$(doctl apps create --spec "$TEMP_SPEC" --format ID,Spec.Name,DefaultIngress --no-header)
APP_ID=$(echo "$APP_CREATE_OUTPUT" | awk '{print $1}')
APP_NAME=$(echo "$APP_CREATE_OUTPUT" | awk '{print $2}')
APP_URL=$(echo "$APP_CREATE_OUTPUT" | awk '{print $3}')

# Clean up temporary spec
rm -f "$TEMP_SPEC"

echo "✅ Staging app created:"
echo "   App ID: $APP_ID"
echo "   Name: $APP_NAME"
echo "   URL: https://$APP_URL"

echo ""
echo "🚀 Triggering Initial Deployment"
echo "--------------------------------"

# Trigger deployment
doctl apps create-deployment "$APP_ID" --force-rebuild

echo "✅ Deployment triggered"
echo ""
echo "📊 Monitoring Deployment"
echo "-----------------------"
echo "View logs with:"
echo "  doctl apps logs $APP_ID --type build --follow"
echo "  doctl apps logs $APP_ID --type run --follow"
echo ""
echo "Check deployment status:"
echo "  doctl apps list-deployments $APP_ID --format ID,Phase,Progress"
echo ""
echo "Access app when ready:"
echo "  https://$APP_URL/web"
echo ""
echo "✅ Deployment initiated successfully!"

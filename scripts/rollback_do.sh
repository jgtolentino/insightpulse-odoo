#!/usr/bin/env bash
# DigitalOcean App Platform rollback script
# Usage: ./rollback_do.sh <app_id>

set -euo pipefail

APP_ID="${1:?APP_ID required}"

echo "🔄 Rolling back app: $APP_ID"

# Get previous successful deployment
PREV_DEPLOYMENT=$(doctl apps list-deployments "$APP_ID" \
    --format ID,Phase \
    --no-header | grep ACTIVE | head -2 | tail -1 | awk '{print $1}')

if [ -z "$PREV_DEPLOYMENT" ]; then
    echo "❌ No previous deployment found"
    exit 1
fi

echo "📦 Previous deployment ID: $PREV_DEPLOYMENT"
echo "⏳ Initiating rollback..."

doctl apps create-deployment "$APP_ID" \
    --deployment-id "$PREV_DEPLOYMENT" --wait

echo "✅ Rollback complete"

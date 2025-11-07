#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Rollback DigitalOcean App Platform deployment
# Error: DO-DEPLOY-FAILED

LOG_PREFIX="[heal:rollback_do_app]"
APP_ID=${1:-}

if [ -z "$APP_ID" ]; then
  echo "$LOG_PREFIX ERROR: APP_ID not provided"
  echo "Usage: $0 <app-id>"
  exit 1
fi

echo "$LOG_PREFIX Starting heal for failed deployment"
echo "$LOG_PREFIX App ID: $APP_ID"

# Get last successful deployment
echo "$LOG_PREFIX Finding last successful deployment..."
LAST_SUCCESS=$(doctl apps list-deployments "$APP_ID" \
  --format ID,Phase \
  --no-header | \
  grep "ACTIVE" | \
  head -1 | \
  awk '{print $1}')

if [ -z "$LAST_SUCCESS" ]; then
  echo "$LOG_PREFIX ERROR: No successful deployment found"
  exit 1
fi

echo "$LOG_PREFIX Last successful deployment: $LAST_SUCCESS"

# Trigger rollback by creating deployment from last successful
echo "$LOG_PREFIX Triggering rollback..."
doctl apps create-deployment "$APP_ID" \
  --force-rebuild

echo "$LOG_PREFIX Rollback initiated, monitoring deployment..."

# Monitor deployment
for i in {1..60}; do
  STATUS=$(doctl apps get "$APP_ID" --format Phase --no-header)
  echo "$LOG_PREFIX Deployment status: $STATUS"

  if [ "$STATUS" = "ACTIVE" ]; then
    echo "$LOG_PREFIX Rollback completed successfully"
    exit 0
  elif [ "$STATUS" = "ERROR" ]; then
    echo "$LOG_PREFIX ERROR: Rollback failed"
    exit 1
  fi

  sleep 10
done

echo "$LOG_PREFIX WARNING: Rollback still in progress after 10 minutes"
exit 1

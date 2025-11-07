#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Restart DigitalOcean App Platform app
# Error: DO-APP-HEALTH-CHECK-FAILING

LOG_PREFIX="[heal:restart_do_app]"
APP_ID=${1:-}

if [ -z "$APP_ID" ]; then
  echo "$LOG_PREFIX ERROR: APP_ID not provided"
  echo "Usage: $0 <app-id>"
  exit 1
fi

echo "$LOG_PREFIX Starting heal for health check failure"
echo "$LOG_PREFIX App ID: $APP_ID"

# Trigger new deployment (restart)
echo "$LOG_PREFIX Restarting app..."
doctl apps create-deployment "$APP_ID"

echo "$LOG_PREFIX Restart initiated, monitoring health..."

# Monitor health checks
for i in {1..60}; do
  HEALTH=$(doctl apps get "$APP_ID" --format Health --no-header)
  echo "$LOG_PREFIX Health status: $HEALTH"

  if [ "$HEALTH" = "HEALTHY" ]; then
    echo "$LOG_PREFIX App is healthy"
    exit 0
  fi

  sleep 10
done

echo "$LOG_PREFIX WARNING: App still not healthy after 10 minutes"
exit 1

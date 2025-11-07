#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Warm Superset cache
# Error: SUPERSET-QUERY-TIMEOUT, SUPERSET-CACHE-MISS

LOG_PREFIX="[heal:warm_superset_cache]"
SUPERSET_BASE_URL=${SUPERSET_BASE_URL:-http://localhost:8088}
SUPERSET_API_KEY=${SUPERSET_API_KEY:-}

echo "$LOG_PREFIX Starting heal for Superset cache"

if [ -z "$SUPERSET_API_KEY" ]; then
  echo "$LOG_PREFIX ERROR: SUPERSET_API_KEY not set"
  exit 1
fi

# List of dashboard IDs to warm (customize for your deployment)
DASHBOARDS=${SUPERSET_DASHBOARDS:-"1 2 3"}

echo "$LOG_PREFIX Warming cache for dashboards: $DASHBOARDS"

for dashboard_id in $DASHBOARDS; do
  echo "$LOG_PREFIX Warming dashboard $dashboard_id..."
  curl -X POST \
    -H "Authorization: Bearer $SUPERSET_API_KEY" \
    -H "Content-Type: application/json" \
    "$SUPERSET_BASE_URL/api/v1/dashboard/$dashboard_id/warm_up_cache" \
    -s -o /dev/null -w "HTTP %{http_code}\n" || true
done

echo "$LOG_PREFIX Heal completed successfully"

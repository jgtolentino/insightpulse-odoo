#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Restart Superset
# Error: SUPERSET-METADATA-DB-DEADLOCK

LOG_PREFIX="[heal:restart_superset]"

echo "$LOG_PREFIX Starting heal for Superset metadata deadlock"

# Restart all Superset services
for svc in superset superset-worker superset-beat; do
  if docker compose ps --services | grep -q "^${svc}$"; then
    echo "$LOG_PREFIX Restarting $svc..."
    docker compose restart "$svc"
  fi
done

# Wait for services to be healthy
echo "$LOG_PREFIX Waiting for services to be healthy..."
sleep 10

# Check Superset is responding
if curl -f -s "$SUPERSET_BASE_URL/health" > /dev/null 2>&1; then
  echo "$LOG_PREFIX Superset is healthy"
else
  echo "$LOG_PREFIX WARNING: Superset may not be fully healthy yet"
fi

echo "$LOG_PREFIX Heal completed successfully"

#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Restart Odoo longpoll worker
# Error: ODOO-LONGPOLL-STALL

LOG_PREFIX="[heal:restart_longpoll]"
SVC=${ODOO_SERVICE_NAME:-odoo}

echo "$LOG_PREFIX Starting heal for longpoll stall"
echo "$LOG_PREFIX Service: $SVC"

# Check if service exists
if ! docker compose ps --services | grep -q "^${SVC}$"; then
  echo "$LOG_PREFIX ERROR: Service $SVC not found"
  exit 1
fi

# Restart the service
echo "$LOG_PREFIX Restarting $SVC..."
docker compose restart "$SVC"

# Wait for service to be healthy
echo "$LOG_PREFIX Waiting for service to be healthy..."
for i in {1..30}; do
  if docker compose ps "$SVC" | grep -q "Up"; then
    echo "$LOG_PREFIX Service $SVC is up"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "$LOG_PREFIX ERROR: Service $SVC did not come up in time"
    exit 1
  fi
  sleep 2
done

echo "$LOG_PREFIX Heal completed successfully"

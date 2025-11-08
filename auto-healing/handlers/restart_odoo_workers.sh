#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Restart Odoo workers (memory leak)
# Error: ODOO-MEMORY-LEAK

LOG_PREFIX="[heal:restart_odoo_workers]"
SVC=${ODOO_SERVICE_NAME:-odoo}

echo "$LOG_PREFIX Starting heal for memory leak"
echo "$LOG_PREFIX Service: $SVC"

# Graceful restart to avoid data loss
echo "$LOG_PREFIX Performing graceful restart..."
docker compose exec "$SVC" kill -TERM 1 || true

# Wait for graceful shutdown
sleep 5

# Restart via compose
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

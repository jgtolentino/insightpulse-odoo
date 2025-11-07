#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Scale Superset workers
# Error: SUPERSET-WORKER-OVERLOAD

LOG_PREFIX="[heal:scale_superset_workers]"
TARGET_WORKERS=${SUPERSET_WORKER_COUNT:-4}

echo "$LOG_PREFIX Starting heal for worker overload"
echo "$LOG_PREFIX Scaling to $TARGET_WORKERS workers"

# Scale workers
docker compose up -d --scale superset-worker=$TARGET_WORKERS

# Wait for new workers to be ready
echo "$LOG_PREFIX Waiting for workers to be ready..."
sleep 10

# Check worker count
CURRENT=$(docker compose ps superset-worker --format json | jq -s 'length')
echo "$LOG_PREFIX Current worker count: $CURRENT"

if [ "$CURRENT" -lt "$TARGET_WORKERS" ]; then
  echo "$LOG_PREFIX WARNING: Not all workers started"
  exit 1
fi

echo "$LOG_PREFIX Heal completed successfully"

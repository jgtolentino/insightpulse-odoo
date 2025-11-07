#!/usr/bin/env bash
set -euo pipefail

# Chaos Test: Kill Worker
# Simulate container crash to test restart and recovery

LOG_PREFIX="[chaos:kill_worker]"
TARGET=${1:-odoo}

echo "$LOG_PREFIX Starting kill worker test"
echo "$LOG_PREFIX Target: $TARGET"

# Verify target exists
if ! docker compose ps --services | grep -q "^${TARGET}$"; then
  echo "$LOG_PREFIX ERROR: Service $TARGET not found"
  exit 1
fi

# Get container ID
CONTAINER_ID=$(docker compose ps -q "$TARGET")

if [ -z "$CONTAINER_ID" ]; then
  echo "$LOG_PREFIX ERROR: Container for $TARGET not running"
  exit 1
fi

# Record state before
echo "$LOG_PREFIX Recording state before kill..."
docker compose ps "$TARGET" > /tmp/chaos_before.txt

# Kill the container
echo "$LOG_PREFIX Killing container $CONTAINER_ID (SIGKILL)..."
docker kill -s SIGKILL "$CONTAINER_ID"

echo "$LOG_PREFIX Waiting for restart..."
sleep 5

# Check if restarted
MAX_WAIT=60
for i in $(seq 1 $MAX_WAIT); do
  if docker compose ps "$TARGET" | grep -q "Up"; then
    echo "$LOG_PREFIX ✓ Container restarted after ${i}s"
    docker compose ps "$TARGET"
    break
  fi

  if [ $i -eq $MAX_WAIT ]; then
    echo "$LOG_PREFIX ERROR: Container did not restart within ${MAX_WAIT}s"
    exit 1
  fi

  sleep 1
done

echo "$LOG_PREFIX Kill worker test completed"
echo "$LOG_PREFIX Expected effects:"
echo "$LOG_PREFIX - Service down alert should have fired"
echo "$LOG_PREFIX - Auto-restart should have occurred"
echo "$LOG_PREFIX - Brief service interruption"

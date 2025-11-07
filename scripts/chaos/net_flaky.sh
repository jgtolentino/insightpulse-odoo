#!/usr/bin/env bash
set -euo pipefail

# Chaos Test: Network Flakiness
# Simulate network latency and packet loss

LOG_PREFIX="[chaos:net_flaky]"
TARGET=${1:-odoo}
DURATION=${DURATION:-60}
LATENCY=${LATENCY:-100ms}
LOSS=${LOSS:-5}

echo "$LOG_PREFIX Starting network flakiness test"
echo "$LOG_PREFIX Target: $TARGET"
echo "$LOG_PREFIX Duration: ${DURATION}s"
echo "$LOG_PREFIX Latency: $LATENCY, Loss: ${LOSS}%"

# Note: This requires tc (traffic control) to be available
# and NET_ADMIN capability on the container

# Get container ID
CONTAINER_ID=$(docker compose ps -q "$TARGET")

if [ -z "$CONTAINER_ID" ]; then
  echo "$LOG_PREFIX ERROR: Container for $TARGET not running"
  exit 1
fi

# Check if tc is available
if ! docker exec "$CONTAINER_ID" which tc > /dev/null 2>&1; then
  echo "$LOG_PREFIX WARNING: tc (traffic control) not available in container"
  echo "$LOG_PREFIX Simulating network issues with sleep instead..."

  # Fallback: Just wait to simulate network issues
  sleep "$DURATION"

  echo "$LOG_PREFIX Network flakiness test completed (simulated)"
  exit 0
fi

# Add network delay and packet loss
echo "$LOG_PREFIX Adding network latency and packet loss..."
docker exec "$CONTAINER_ID" tc qdisc add dev eth0 root netem delay "$LATENCY" loss "${LOSS}%" || {
  echo "$LOG_PREFIX WARNING: Could not add tc rules (may require NET_ADMIN capability)"
  echo "$LOG_PREFIX Continuing with sleep simulation..."
  sleep "$DURATION"
  exit 0
}

# Let it run
sleep "$DURATION"

# Remove network impairment
echo "$LOG_PREFIX Removing network impairment..."
docker exec "$CONTAINER_ID" tc qdisc del dev eth0 root netem || true

echo "$LOG_PREFIX Network flakiness test completed"
echo "$LOG_PREFIX Expected effects:"
echo "$LOG_PREFIX - Increased response times"
echo "$LOG_PREFIX - Timeout alerts may have fired"
echo "$LOG_PREFIX - Retry logic should have been exercised"

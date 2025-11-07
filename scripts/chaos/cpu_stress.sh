#!/usr/bin/env bash
set -euo pipefail

# Chaos Test: CPU Stress
# Simulate high CPU load to test alerting and auto-scaling

LOG_PREFIX="[chaos:cpu_stress]"
DURATION=${DURATION:-60}
CPUS=${CPUS:-2}

echo "$LOG_PREFIX Starting CPU stress test"
echo "$LOG_PREFIX Duration: ${DURATION}s, CPUs: $CPUS"

# Run stress container
docker run --rm \
  --name chaos-cpu-stress \
  --cpus="$CPUS" \
  alpine sh -c "
    echo 'Starting CPU stress...'
    # Generate CPU load
    for i in \$(seq 1 $CPUS); do
      yes > /dev/null &
    done
    sleep $DURATION
    killall yes
    echo 'CPU stress completed'
  "

echo "$LOG_PREFIX CPU stress test completed"
echo "$LOG_PREFIX Expected effects:"
echo "$LOG_PREFIX - High CPU alerts should have fired"
echo "$LOG_PREFIX - Auto-scaling may have triggered"
echo "$LOG_PREFIX - Performance degradation should be visible"

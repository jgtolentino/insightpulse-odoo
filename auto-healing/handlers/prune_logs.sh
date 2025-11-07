#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Prune large log files
# Error: DOCKER-DISK-PRESSURE

LOG_PREFIX="[heal:prune_logs]"
LOG_SIZE_LIMIT=${LOG_SIZE_LIMIT:-200M}

echo "$LOG_PREFIX Starting heal for log pressure"
echo "$LOG_PREFIX Truncating logs larger than $LOG_SIZE_LIMIT"

# Find and truncate large log files
if [ -d /var/lib/docker/containers ]; then
  echo "$LOG_PREFIX Searching for large logs in /var/lib/docker/containers..."
  sudo find /var/lib/docker/containers -name '*-json.log' -size +$LOG_SIZE_LIMIT -exec sh -c '
    echo "Truncating: $1 ($(du -h "$1" | cut -f1))"
    truncate -s 0 "$1"
  ' sh {} \;
fi

# Also check local logs directory if exists
if [ -d logs ]; then
  echo "$LOG_PREFIX Searching for large logs in logs/..."
  find logs -name '*.log' -size +$LOG_SIZE_LIMIT -exec sh -c '
    echo "Truncating: $1 ($(du -h "$1" | cut -f1))"
    truncate -s 0 "$1"
  ' sh {} \;
fi

echo "$LOG_PREFIX Heal completed successfully"

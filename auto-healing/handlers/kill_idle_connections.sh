#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Kill idle database connections
# Error: SUPABASE-DB-CONNECTION-SATURATION, DO-DATABASE-CONNECTION-LIMIT

LOG_PREFIX="[heal:kill_idle_connections]"
IDLE_TIMEOUT_MINUTES=${IDLE_TIMEOUT_MINUTES:-10}
POSTGRES_URL=${POSTGRES_URL:-$PGDATABASE}

echo "$LOG_PREFIX Starting heal for connection saturation"
echo "$LOG_PREFIX Will kill connections idle for >${IDLE_TIMEOUT_MINUTES} minutes"

# Kill idle connections
KILLED=$(psql "$POSTGRES_URL" -t -c "
  SELECT count(pg_terminate_backend(pid))
  FROM pg_stat_activity
  WHERE state = 'idle'
    AND state_change < now() - interval '${IDLE_TIMEOUT_MINUTES} minutes'
    AND pid <> pg_backend_pid();
")

echo "$LOG_PREFIX Killed $KILLED idle connections"

# Check current connection count
CURRENT=$(psql "$POSTGRES_URL" -t -c "SELECT count(*) FROM pg_stat_activity;")
MAX=$(psql "$POSTGRES_URL" -t -c "SELECT setting::int FROM pg_settings WHERE name='max_connections';")

echo "$LOG_PREFIX Current connections: $CURRENT / $MAX"

if [ "$CURRENT" -gt $((MAX * 80 / 100)) ]; then
  echo "$LOG_PREFIX WARNING: Still above 80% threshold"
  exit 1
fi

echo "$LOG_PREFIX Heal completed successfully"

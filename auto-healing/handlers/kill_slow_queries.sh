#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Kill slow database queries causing deadlock
# Error: ODOO-DB-DEADLOCK

LOG_PREFIX="[heal:kill_slow_queries]"
TIMEOUT_SECONDS=${QUERY_TIMEOUT_SECONDS:-30}

echo "$LOG_PREFIX Starting heal for database deadlock"
echo "$LOG_PREFIX Will kill queries running longer than ${TIMEOUT_SECONDS}s"

# Get slow queries
SLOW_QUERIES=$(docker compose exec -T odoo psql "$PGDATABASE" -t -c "
  SELECT pid, extract(epoch from (now() - query_start))::int as seconds
  FROM pg_stat_activity
  WHERE state = 'active'
    AND query_start < now() - interval '${TIMEOUT_SECONDS} seconds'
    AND pid <> pg_backend_pid()
    AND query NOT ILIKE '%pg_stat_activity%'
  ORDER BY seconds DESC;
")

if [ -z "$SLOW_QUERIES" ]; then
  echo "$LOG_PREFIX No slow queries found"
  exit 0
fi

echo "$LOG_PREFIX Found slow queries:"
echo "$SLOW_QUERIES"

# Kill each slow query
echo "$SLOW_QUERIES" | while read -r pid seconds; do
  if [ -n "$pid" ] && [ "$pid" != " " ]; then
    echo "$LOG_PREFIX Killing PID $pid (running ${seconds}s)"
    docker compose exec -T odoo psql "$PGDATABASE" -c "SELECT pg_terminate_backend($pid);" || true
  fi
done

echo "$LOG_PREFIX Heal completed successfully"

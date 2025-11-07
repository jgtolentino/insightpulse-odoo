#!/usr/bin/env bash
set -euo pipefail

# Auto-heal handler: Unlock stuck Odoo cron jobs
# Error: ODOO-CRON-JAM

LOG_PREFIX="[heal:unlock_cron]"
DB=${ODOO_DB:-insightpulse}

echo "$LOG_PREFIX Starting heal for cron jam"
echo "$LOG_PREFIX Database: $DB"

# Reset cron via Odoo CLI
echo "$LOG_PREFIX Resetting cron jobs..."
docker compose exec -T odoo odoo \
  -d "$DB" \
  -u base \
  --stop-after-init \
  --log-level=warning || {
    echo "$LOG_PREFIX ERROR: Failed to reset cron"
    exit 1
  }

echo "$LOG_PREFIX Heal completed successfully"

#!/usr/bin/env bash
set -euo pipefail

# Run Odoo module updates for all custom InsightPulse/TBWA modules,
# or for a specific list passed as arguments.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DB_NAME="${ODOO_DB:-odoo}"
ODOO_CONF="${ODOO_CONF:-$REPO_ROOT/deploy/odoo.conf}"

if [ "$#" -gt 0 ]; then
  MODULES_CSV="$(printf "%s," "$@" | sed 's/,$//')"
else
  # Auto-detect ipai_* and tbwa_* modules in addons/
  cd "$REPO_ROOT/addons"
  MODULES_CSV="$(ls -d ipai_* tbwa_* 2>/dev/null | tr '\n' ',' | sed 's/,$//')"
  cd "$REPO_ROOT"
fi

if [ -z "${MODULES_CSV:-}" ]; then
  echo "No ipai_* or tbwa_* modules found to migrate."
  exit 0
fi

echo "Running migrations for DB '$DB_NAME' on modules: $MODULES_CSV"

"$REPO_ROOT/odoo-bin" \
  -c "$ODOO_CONF" \
  -d "$DB_NAME" \
  -u "$MODULES_CSV" \
  --stop-after-init

echo "Migrations completed."

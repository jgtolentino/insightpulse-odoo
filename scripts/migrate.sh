#!/usr/bin/env bash
set -euo pipefail
DB="${1:-odoo}"
MODS="${MODS:-all}"
if command -v docker >/dev/null && docker compose version >/dev/null 2>&1; then DC="docker compose"; else DC="docker-compose"; fi
$DC exec -T odoo odoo -c /etc/odoo/odoo.conf -d "$DB" -u "$MODS" --stop-after-init

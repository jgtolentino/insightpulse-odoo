#!/usr/bin/env bash
set -euo pipefail
DB="${ODOO_DB:-odoboo_prod}"
odoo -c /etc/odoo/odoo.conf -d "$DB" --stop-after-init || createdb "$DB"
odoo -c /etc/odoo/odoo.conf -d "$DB" -i insightpulse_enterprise --stop-after-init

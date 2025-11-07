#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Generating addons_path..."

# Build a comma-separated addons_path from OCA + custom
collect() {
  local root="$1"
  if [ ! -d "$root" ]; then
    echo ""
    return
  fi
  find "$root" -type f -name "__manifest__.py" -printf "%h\n" 2>/dev/null | sort -u || true
}

OCA=$(collect /mnt/oca | tr '\n' ',' | sed 's/,$//')
CUST=$(collect /mnt/addons | tr '\n' ',' | sed 's/,$//')

APPEND=""
[ -n "$OCA" ] && APPEND="${APPEND},${OCA}"
[ -n "$CUST" ] && APPEND="${APPEND},${CUST}"

# Idempotent rewrite: keep first line, replace/add addons_path after it
if ! grep -q "addons_path = " /etc/odoo/odoo.conf; then
  echo "addons_path = /usr/lib/python3/dist-packages/odoo/addons${APPEND}" >> /etc/odoo/odoo.conf
else
  sed -i "s#^addons_path = .*#addons_path = /usr/lib/python3/dist-packages/odoo/addons${APPEND}#g" /etc/odoo/odoo.conf
fi

echo "[entrypoint] addons_path updated successfully."
echo "[entrypoint] Current addons_path:"
grep "addons_path" /etc/odoo/odoo.conf

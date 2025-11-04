#!/usr/bin/env bash
set -euo pipefail
MOD=${1:?module}; OUT=${2:-dist/appstore}
./scripts/odoo/package_addon.sh "$MOD" "$OUT"
[ -d "odoo_addons/${MOD}/store_meta" ] && cp -r "odoo_addons/${MOD}/store_meta" "$OUT/${MOD}_meta" || true

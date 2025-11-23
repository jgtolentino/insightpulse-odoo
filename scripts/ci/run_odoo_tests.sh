#!/usr/bin/env bash
set -euo pipefail

if ! command -v python >/dev/null 2>&1; then
  echo "❌ python not found"
  exit 1
fi

if [ -z "${ODOO_BIN:-}" ]; then
  # Try to discover from default install location
  if [ -f "$HOME/odoo-source-18/odoo-bin" ]; then
    export ODOO_BIN="$HOME/odoo-source-18/odoo-bin"
  fi
fi

if [ ! -f "${ODOO_BIN:-}" ]; then
  echo "❌ ODOO_BIN not set or odoo-bin not found."
  echo "   Make sure scripts/ci/install_odoo_18.sh ran earlier in this job."
  exit 1
fi

echo "▶️ Running Odoo tests via: $ODOO_BIN"
"$ODOO_BIN" "$@"

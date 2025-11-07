#!/usr/bin/env bash
set -euo pipefail

# Install Odoo modules in waves (ordered batches)
# Usage: ./install_waves.sh [database_name]

DB="${1:-${POSTGRES_DB:-odoo18}}"
CONF="${2:-/etc/odoo/odoo.conf}"
WAVES_DIR="${3:-/mnt/waves}"

echo "=== Installing Odoo modules in waves ==="
echo "Database: $DB"
echo "Config: $CONF"
echo "Waves directory: $WAVES_DIR"
echo ""

install_wave() {
  local list="$1"
  local wave_name=$(basename "$list" .txt)

  if [ ! -f "$list" ]; then
    echo "  ✗ Wave file not found: $list"
    return 1
  fi

  # Read modules from file (skip empty lines and comments)
  local mods
  mods=$(grep -E '^[a-zA-Z_][a-zA-Z0-9_]*$' "$list" 2>/dev/null | tr '\n' ',' || true)
  mods="${mods%,}"

  if [ -z "$mods" ]; then
    echo "  ⊘ Skipping empty wave: $wave_name"
    return 0
  fi

  echo ""
  echo "==> Installing wave: $wave_name"
  echo "    Modules: $mods"

  odoo -d "$DB" -i "$mods" -c "$CONF" --stop-after-init --no-http || {
    echo "  ✗ Failed to install wave: $wave_name"
    return 1
  }

  echo "  ✓ Wave $wave_name installed successfully"
}

# Install waves in order
if [ -d "$WAVES_DIR" ]; then
  for w in "$WAVES_DIR"/*.txt; do
    [ -f "$w" ] && install_wave "$w"
  done
else
  echo "✗ Waves directory not found: $WAVES_DIR"
  exit 1
fi

echo ""
echo "=== All waves installed successfully ==="

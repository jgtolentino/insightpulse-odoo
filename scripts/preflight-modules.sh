#!/usr/bin/env bash
set -euo pipefail
DB="${1:-db_ckvc}"
LIST="${2:-}"

if [[ -z "$LIST" ]]; then
  echo "✖ No module list provided"; exit 2
fi

echo "→ Preflight on DB=${DB}"
# Note: apps-update target handles registry refresh

MISSING=()
# Check presence in ir_module_module (means Odoo can see the addon)
IFS=',' read -ra MODS <<< "$LIST"
for m in "${MODS[@]}"; do
  found="$(docker compose exec -T db psql -U odoo -d "$DB" -Atc "select 1 from ir_module_module where name='${m}' limit 1;" || true)"
  if [[ "$found" != "1" ]]; then
    MISSING+=("$m")
  fi
done

if (( ${#MISSING[@]} > 0 )); then
  echo "✖ Missing modules (not visible to Odoo):"
  printf '  - %s\n' "${MISSING[@]}"
  echo "Hints:"
  echo "  • Check addons_path in odoo.conf includes /mnt/addons and /mnt/oca"
  echo "  • Verify folder names match module technical names"
  echo "  • Submodules pulled: git submodule update --init --recursive"
  echo "  • Re-run: make apps-update"
  exit 3
fi

echo "✓ All modules visible to Odoo."

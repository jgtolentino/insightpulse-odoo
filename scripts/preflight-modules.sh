#!/usr/bin/env bash
set -euo pipefail
DB="${1:-insightpulse}"
LIST="${2:-}"
[[ -z "$LIST" ]] && { echo "✖ No module list provided"; exit 2; }

echo "→ Preflight on DB=${DB}"
docker compose exec -T odoo odoo -c /etc/odoo/odoo.conf -d "$DB" -u base --stop-after-init >/dev/null

MISSING=()
IFS=',' read -ra MODS <<< "$LIST"
for m in "${MODS[@]}"; do
  found="$(docker compose exec -T db psql -U odoo -d "$DB" -Atc "select 1 from ir_module_module where name='${m}' limit 1;" || true)"
  [[ "$found" == "1" ]] || MISSING+=("$m")
done

if (( ${#MISSING[@]} > 0 )); then
  echo "✖ Missing modules (not visible to Odoo):"
  printf '  - %s\n' "${MISSING[@]}"
  echo "Hints:"
  echo "  • addons_path includes /mnt/addons and /mnt/oca in odoo.conf"
  echo "  • Folder names match technical names"
  echo "  • Pull submodules: git submodule update --init --recursive"
  echo "  • Re-run: make apps-update"
  exit 3
fi
echo "✓ All modules visible."

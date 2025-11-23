#!/usr/bin/env bash
set -euo pipefail

# Resolve absolute path to this script
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"

# Adjusting default to point to deploy directory where docker-compose.yml lives
ROOT_DIR="${ROOT_DIR:-$HOME/odoo-ce/deploy}"
DB_NAME="${DB_NAME:-odoo}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo}"
DB_SERVICE="${DB_SERVICE:-db}"

cd "$ROOT_DIR"

psql_exec() {
  docker compose exec -T "$DB_SERVICE" psql -U odoo -d "$DB_NAME" "$@"
}

odoo_shell() {
  docker compose exec -T "$ODOO_SERVICE" odoo shell -d "$DB_NAME"
}

case "${1:-}" in
  status)
    echo "🔎 Docker services"
    docker compose ps
    echo

    echo "🔎 ipai*/tbwa* module states"
    psql_exec -c "
      SELECT name, state
      FROM ir_module_module
      WHERE name LIKE 'ipai_%' OR name LIKE 'tbwa_%'
      ORDER BY name;
    "
    echo

    echo "🔎 Legacy modules (should be uninstalled / to remove)"
    psql_exec -c "
      SELECT name, state
      FROM ir_module_module
      WHERE name IN ('ipai_finance_ssc', 'x_cash_advance', 'x_expense_policy');
    "
    ;;

  verify-ppm-2026)
    echo "📅 Checking Finance PPM 2026 engine data (adjust model/field names if needed)..."
    odoo_shell << 'PYCODE'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
# 🔁 Adjust this model to your actual PPM schedule model:
# Added ipai.bir.form.schedule as implemented
Model = env.get('ipai.bir.form.schedule') or env.get('ipai.finance_ppm_schedule') or env.get('ipai.finance_task')

if not Model:
    print("❌ Could not find PPM schedule model (ipai.bir.form.schedule / ipai.finance_ppm_schedule / ipai.finance_task).")
else:
    # Check for 2026 records
    # ipai.bir.form.schedule has 'bir_deadline' field
    total = Model.search_count([])
    print(f"✅ PPM model: {Model._name}")
    print(f"   Total records: {total}")
    
    count_2026 = 0
    if 'bir_deadline' in Model._fields:
        count_2026 = Model.search_count([('bir_deadline', '>=', '2026-01-01'), ('bir_deadline', '<=', '2026-12-31')])
        print(f"   2026 records (via bir_deadline): {count_2026}")
    elif 'year' in Model._fields:
        count_2026 = Model.search_count([('year', '=', 2026)])
        print(f"   2026 records (via year): {count_2026}")
    else:
        # fallback: naive filter by date field
        date_field = None
        for fname in ['planned_date', 'schedule_date', 'date']:
            if fname in Model._fields:
                date_field = fname
                break
        if date_field:
            count_2026 = Model.search_count([(date_field, '>=', '2026-01-01'), (date_field, '<=', '2026-12-31')])
            print(f"   2026 records (via {date_field}): {count_2026}")
        else:
            print("   ⚠️ No year/date field found to filter 2026.")
PYCODE
    ;;

  check-ssl)
    echo "🔒 Checking odoo.conf SSL / proxy settings"
    if docker compose exec -T "$ODOO_SERVICE" test -f /etc/odoo/odoo.conf; then
      docker compose exec -T "$ODOO_SERVICE" grep -E 'proxy_mode|ssl' /etc/odoo/odoo.conf || true
    else
      echo "Could not find /etc/odoo/odoo.conf inside container."
    fi
    ;;

  tail-logs)
    echo "📜 Last 100 lines of Odoo log"
    docker compose logs "$ODOO_SERVICE" --tail=100
    ;;

  restart)
    echo "🔁 Restarting Odoo service"
    docker compose restart "$ODOO_SERVICE"
    ;;

  full-verify)
    echo "✅ 1) Container/Module status"
    "$SCRIPT_PATH" status
    echo
    echo "✅ 2) PPM 2026 engine data"
    "$SCRIPT_PATH" verify-ppm-2026
    echo
    echo "✅ 3) Odoo SSL/proxy config"
    "$SCRIPT_PATH" check-ssl
    echo
    echo "✅ 4) Recent logs"
    "$SCRIPT_PATH" tail-logs
    ;;

  *)
    cat <<EOF
Usage: $(basename "$0") <command>

Commands:
  status          Show docker compose status + ipai*/tbwa* module states + legacy modules
  verify-ppm-2026 Check that the Finance PPM 2026 engine has data (adjust model name inside)
  check-ssl       Show SSL / proxy_mode flags from odoo.conf inside container
  tail-logs       Tail last 100 lines of Odoo logs
  restart         Restart the Odoo service via docker compose
  full-verify     Run status + verify-ppm-2026 + check-ssl + tail-logs

Environment (override as needed):
  ROOT_DIR      (default: \$HOME/odoo-ce/deploy)
  DB_NAME       (default: odoo)
  ODOO_SERVICE  (default: odoo)
  DB_SERVICE    (default: db)
EOF
    ;;
esac

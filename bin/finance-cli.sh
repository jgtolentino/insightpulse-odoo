#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${ROOT_DIR:-$HOME/odoo-ce}"
N8N_URL="${N8N_URL:-http://localhost:5678}"
N8N_API_KEY="${N8N_API_KEY:-CHANGE_ME}"   # set real key in your shell
DB_NAME="${DB_NAME:-odoo}"

cd "$ROOT_DIR"

function odoo_shell() {
  docker exec -i odoo-ce odoo shell -d "$DB_NAME"
}

case "${1:-}" in
  status)
    echo "🔎 Odoo containers:"
    docker ps | grep -E "(odoo|postgres)" || echo "No Odoo containers running"
    echo
    echo "🔎 Finance ipai/tbwa modules:"
    docker exec odoo-db psql -U odoo -d "$DB_NAME" -c \
      "SELECT name, state FROM ir_module_module WHERE name LIKE 'ipai_%' OR name LIKE 'tbwa_%' ORDER BY name;"
    echo
    echo "🔎 BIR schedule count:"
    docker exec odoo-db psql -U odoo -d "$DB_NAME" -c \
      "SELECT count(*) FROM ipai_finance_bir_schedule;"
    ;;

  seed-bir-orm)
    # Run the Python ORM direct-insert script inside odoo shell
    echo "🚀 Seeding BIR schedules via ORM (bypassing noupdate=1)..."
    odoo_shell << 'PYCODE'
from datetime import date
env = odoo.api.Environment(cr, SUPERUSER_ID, {})

# Adjust model & fields to your actual ipai_finance model/table
Model = env['ipai.finance.bir_schedule']

records = [
    # Example: replace with full 128-list you generated
    {
        "name": "1601-C - December 2025",
        "period_covered": "2025-12-01 to 2025-12-31",
        "filing_deadline": date(2026, 1, 10),
        "prep_deadline": date(2026, 1, 5),
        "review_deadline": date(2026, 1, 7),
        "approval_deadline": date(2026, 1, 9),
        "status": "draft",
    },
    # ... Add full 128-record list from generate_bir_seeds.py
]

existing = Model.search([])
print(f"Existing schedule records: {len(existing)}")
if existing:
    print("Keeping existing; inserting only missing combinations.")

for rec in records:
    dom = [
        ('name', '=', rec['name']),
    ]
    if Model.search(dom):
        continue
    Model.create(rec)

cr.commit()
print(f"New total schedule records: {Model.search_count([])}")
PYCODE
    ;;

  gen-2026-calendar)
    echo "📅 Generating 2026 Finance calendar (CSV + JSON)..."
    python scripts/generate_2026_finance_calendar.py
    ls -1 finance_calendar_2026.csv finance_events_2026.json
    ;;

  import-n8n)
    if [ "$N8N_API_KEY" = "CHANGE_ME" ]; then
      echo "❌ Set N8N_API_KEY in your shell first."
      exit 1
    fi

    WF_PATH="${2:-$HOME/n8n/workflows/finance_compliance_engine.json}"
    echo "🚀 Importing n8n workflow from $WF_PATH into $N8N_URL ..."
    curl -fsSL -X POST "$N8N_URL/api/v1/workflows" \
      -H "Content-Type: application/json" \
      -H "X-N8N-API-KEY: $N8N_API_KEY" \
      --data-binary @"$WF_PATH"
    echo
    echo "✅ n8n workflow import attempted; check UI for result."
    ;;

  test-cron)
    echo "⏱  Running BIR Task Sync cron manually in Odoo..."
    odoo_shell << 'PYCODE'
env = odoo.api.Environment(cr, SUPERUSER_ID, {})
cron = env['ir.cron'].search([('cron_name', '=', 'Finance PPM: Sync BIR Tasks')], limit=1)
if not cron:
    print("Cron not found")
else:
    print(f"Running cron: {cron.cron_name}")
    cron.method_direct_trigger()
    cr.commit()
PYCODE
    ;;

  *)
    cat <<EOF
Usage: finance-cli.sh <command>

Commands:
  status             Show Odoo containers, ipai*/tbwa* module states, BIR count
  seed-bir-orm       Insert BIR schedule records via Python ORM (bypass noupdate=1)
  gen-2026-calendar  Generate 2026 Finance calendar CSV + JSON
  import-n8n [path]  Import finance_compliance_engine.json into n8n via API
  test-cron          Manually trigger Finance PPM BIR Task Sync cron

Environment:
  ROOT_DIR   (default: \$HOME/odoo-ce)
  DB_NAME    (default: odoo)
  N8N_URL    (default: http://localhost:5678)
  N8N_API_KEY  n8n API key from your user profile

Examples:
  finance-cli.sh status
  N8N_API_KEY="your-real-key" finance-cli.sh import-n8n
  finance-cli.sh test-cron
EOF
    ;;
esac

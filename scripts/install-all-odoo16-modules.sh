#!/usr/bin/env bash
set -euo pipefail

# ==============================
# Odoo 16 — Tier-3 SaaS Parity
# Staged installer with auto-filter (drops modules not present on disk)
# ==============================

# --- Config (override via env) ---
DB="${DB:-odoo16}"
CONF="${CONF:-config/odoo16.conf}"            # points to your odoo.conf
STRICT="${STRICT:-0}"                         # 1=fatal if module missing, 0=skip missing
USE_DOCKER="${USE_DOCKER:-auto}"              # auto|yes|no
DC_FILE="${DC_FILE:-docker-compose.odoo16.yml}"
ODOO_SERVICE="${ODOO_SERVICE:-odoo}"          # docker service name

# --- Resolve ODOO command (local vs docker) ---
resolve_odoo_cmd() {
  if [[ "${USE_DOCKER}" == "yes" ]] || { [[ "${USE_DOCKER}" == "auto" ]] && [[ -f "${DC_FILE}" ]]; }; then
    echo "docker compose -f ${DC_FILE} exec -T ${ODOO_SERVICE} odoo"
  else
    # Prefer 'odoo' then fallback to 'odoo-bin'
    if command -v odoo >/dev/null 2>&1; then echo "odoo"
    elif command -v odoo-bin >/dev/null 2>&1; then echo "odoo-bin"
    else
      echo "ERROR: no 'odoo' or 'odoo-bin' in PATH and docker not selected." >&2; exit 1
    fi
  fi
}

ODOO_CMD="$(resolve_odoo_cmd)"

# --- Parse addons_path from .conf (comma-separated) ---
if [[ ! -f "${CONF}" ]]; then
  echo "ERROR: Config file not found: ${CONF}" >&2; exit 1
fi
ADDONS_PATH_RAW="$(awk -F= '/^[[:space:]]*addons_path[[:space:]]*=/{print $2}' "${CONF}" | tr -d '[:space:]' || true)"
IFS=',' read -r -a ADDONS_ARR <<< "${ADDONS_PATH_RAW}"

have_module() {
  local mod="$1"
  for p in "${ADDONS_ARR[@]}"; do
    [[ -d "${p}/${mod}" ]] && return 0
  done
  return 1
}

# Filter list to only modules present on disk (unless STRICT=1)
filter_modules() {
  local out=()
  for m in "$@"; do
    if have_module "$m"; then
      out+=("$m")
    else
      if [[ "${STRICT}" == "1" ]]; then
        echo "ERROR: missing module on disk: ${m}" >&2; exit 1
      else
        echo "… skipping missing module: ${m}"
      fi
    fi
  done
  printf "%s\n" "${out[@]}"
}

install_stage() {
  local stage="$1"; shift
  mapfile -t filtered < <(filter_modules "$@")
  if [[ "${#filtered[@]}" -eq 0 ]]; then
    echo "Stage ${stage}: nothing to install (all missing)."
    return 0
  fi
  local csv
  csv="$(IFS=,; echo "${filtered[*]}")"
  echo "Stage ${stage}: installing -> ${csv}"
  ${ODOO_CMD} -c "${CONF}" -d "${DB}" -i "${csv}" --stop-after-init
}

echo "== Odoo 16 Tier-3 SaaS Parity install =="
echo "DB=${DB}  CONF=${CONF}  DOCKER=${USE_DOCKER}  STRICT=${STRICT}"
echo "addons_path=${ADDONS_PATH_RAW}"
echo

# --------------------------
# Stage 1 — Foundation (tech + UI)
# --------------------------
install_stage "1 - Foundation" \
  web_responsive web_environment_ribbon \
  base_automation base_rest component queue_job server_environment \
  auth_oauth auth_totp

# --------------------------
# Stage 2 — Core Apps
# --------------------------
install_stage "2 - Core" \
  contacts crm sale_management purchase stock account account_accountant \
  project hr hr_expense website portal calendar

# --------------------------
# Stage 3 — Accounting Power-ups (OCA)
# --------------------------
install_stage "3 - Accounting OCA" \
  l10n_generic_coa \
  account_bank_statement_import account_bank_statement_import_csv \
  account_bank_statement_import_ofx account_bank_statement_import_qif \
  account_bank_statement_import_camt \
  account_move_base_import account_invoice_import \
  account_fiscal_year account_payment_order account_petty_cash \
  account_financial_report account_tax_balance mis_builder

# --------------------------
# Stage 4 — Ops & Fulfillment
# --------------------------
install_stage "4 - Ops" \
  sale_stock delivery barcode stock_account stock_picking_batch \
  stock_landed_costs fleet

# --------------------------
# Stage 5 — Services / Projects / Field Ops
# (helpdesk is CE-variant dependent; will be auto-skipped if not on disk)
# --------------------------
install_stage "5 - Services" \
  project sale_timesheet helpdesk \
  fieldservice fieldservice_sale fieldservice_account fieldservice_stock

# --------------------------
# Stage 6 — MRP / PLM / Quality / Maintenance
# --------------------------
install_stage "6 - MRP/PLM/Quality" \
  mrp mrp_workorder mrp_subcontracting plm quality quality_control maintenance

# --------------------------
# Stage 7 — HR Suite & OCR MVP
# --------------------------
install_stage "7 - HR & OCR" \
  hr_contract hr_timesheet hr_holidays hr_attendance hr_recruitment hr_skills \
  ip_expense_mvp

# --------------------------
# Stage 8 — Web, Payments, Marketing, Reporting
# --------------------------
install_stage "8 - Web/Pay/Marketing/BI" \
  website website_sale website_form website_livechat appointment \
  payment payment_stripe payment_paypal \
  mass_mailing marketing_automation sms social \
  board report_xlsx

echo
echo "✅ All stages executed."
echo "Tip: to upgrade later, run: ${ODOO_CMD} -c ${CONF} -d ${DB} -u <module_csv> --stop-after-init"

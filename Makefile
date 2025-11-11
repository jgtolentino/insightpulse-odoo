# Makefile
DB ?= insightpulse
ODOO_BIN = docker exec odoo19 odoo -c /etc/odoo/odoo.conf -d $(DB)
PSQL     = docker exec odoo19_db psql -U odoo -d $(DB)

# ── Module sets ────────────────────────────────────────────────────────────────
CORE_MODS = contacts,mail,calendar,account,purchase,sale_management,stock,stock_barcode,hr,hr_holidays,hr_expense,timesheet_grid,project,documents
IPAI_MODS = ipai_branding,ipai_bir_compliance
OCA_MODS  = web_responsive,web_environment_ribbon,module_auto_update,base_user_role,disable_odoo_online,report_xlsx,queue_job,queue_job_cron,account_fiscal_year,account_move_name_sequence,account_bank_statement_import_helper,account_bank_statement_import_qif,account_bank_statement_import_camt,account_bank_statement_import_mt940,account_payment_order,account_payment_mode,account_invoice_constraint_chronology,account_invoice_line_number,mis_builder,mis_builder_budget_oca,account_financial_report,partner_firstname,partner_contact_personal_information_page,sale_exception,sale_order_type,sale_order_line_price_history,purchase_request,purchase_request_to_rfq,purchase_tier_validation,stock_picking_package_preparation,stock_picking_report_delivery_note

ALL_MIN   = $(CORE_MODS),$(IPAI_MODS)
ALL_FULL  = $(CORE_MODS),$(IPAI_MODS),$(OCA_MODS)

# ── Utilities ─────────────────────────────────────────────────────────────────
.PHONY: apps-update preflight verify install-min install-full install-oca help

help: ## Show this help message
	@echo "Usage: make [target] [DB=database_name]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""
	@echo "Default DB: $(DB)"

apps-update: ## Refresh Apps registry (same as Update Apps List)
	$(ODOO_BIN) -u base --stop-after-init

preflight: apps-update ## Ensure modules exist & are visible to Odoo
	bash scripts/preflight-modules.sh "$(DB)" "$(shell echo $(ALL_FULL) | tr -d ' ')"

verify: ## Show availability state of modules
	@echo "=== Module State Check ==="
	@$(PSQL) -c "SELECT name, state FROM ir_module_module WHERE name IN ('$(shell echo $(ALL_FULL) | sed 's/,/'\',\''/g')') ORDER BY name;"

install-min: preflight ## Install CE core + ipai_*
	@echo "=== Installing minimal module set (Core CE + IPAI) ==="
	$(ODOO_BIN) -i $(ALL_MIN) --stop-after-init --without-demo=all

install-oca: preflight ## Install OCA parity set only
	@echo "=== Installing OCA modules ==="
	$(ODOO_BIN) -i $(OCA_MODS) --stop-after-init --without-demo=all

install-full: preflight ## Install everything (CE + ipai_* + OCA)
	@echo "=== Installing full module set (Core CE + IPAI + OCA) ==="
	$(ODOO_BIN) -i $(ALL_FULL) --stop-after-init --without-demo=all

status: ## Check Odoo service status
	@echo "=== Odoo Service Status ==="
	@docker ps --filter name=odoo19 --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
	@echo ""
	@echo "=== Database Status ==="
	@$(PSQL) -c "SELECT COUNT(*) as total_modules, COUNT(*) FILTER (WHERE state='installed') as installed FROM ir_module_module;"

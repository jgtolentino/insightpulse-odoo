#!/usr/bin/env bash
#
# install-enterprise-parity.sh - Install 100+ modules for Enterprise parity
# Orchestrates installation of IPAI custom modules + OCA modules in batches
#
# Usage:
#   ./scripts/install-enterprise-parity.sh [--dry-run] [--skip-ipai] [--category CATEGORY]
#
# Categories: ipai, accounting, sales, purchase, inventory, project, hr, helpdesk,
#             manufacturing, quality, maintenance, website, reporting, tools, all
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✅${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠️${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; }

# Configuration
ODOO_CONTAINER="${ODOO_CONTAINER:-odoo}"
POSTGRES_CONTAINER="${POSTGRES_CONTAINER:-postgres}"
DB_NAME="${ODOO_DB:-odoo}"
DRY_RUN=false
SKIP_IPAI=false
CATEGORY="all"
LOG_FILE="logs/install-enterprise-parity-$(date +%Y%m%d-%H%M%S).log"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN=true; shift ;;
        --skip-ipai) SKIP_IPAI=true; shift ;;
        --category) CATEGORY="$2"; shift 2 ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
done

# Create logs directory
mkdir -p logs

# Installation batches (100+ modules total)
declare -A MODULE_BATCHES=(
    # IPAI Custom Modules (3 modules)
    ["ipai"]="ipai_studio ipai_sign ipai_knowledge"

    # Accounting & Finance (12 modules)
    ["accounting"]="account_financial_report account_move_line_report account_payment_order account_reconcile_oca account_statement_import account_usability mis_builder account_fiscal_year account_asset_management account_invoice_refund_link account_budget account_cost_center"

    # Sales & CRM (8 modules)
    ["sales"]="sale_order_line_date sale_stock_picking_blocking sale_quotation_number sale_automatic_workflow sale_order_type sale_product_set sale_order_invoicing_grouping_criteria sale_order_archive"

    # Purchase & Procurement (7 modules)
    ["purchase"]="purchase_order_type purchase_request purchase_order_approval_block purchase_stock_picking_return_invoicing purchase_work_acceptance purchase_discount purchase_order_line_price_history"

    # Inventory & Logistics (8 modules)
    ["inventory"]="stock_request stock_picking_invoice_link stock_valuation_layer_usage stock_available_unreserved stock_picking_batch_extended stock_putaway_by_route stock_inventory_cost_info stock_move_line_auto_fill"

    # Project Management (6 modules)
    ["project"]="project_task_dependency project_template project_status project_key project_timeline project_timesheet_time_control"

    # HR & Timesheets (7 modules)
    ["hr"]="hr_timesheet_sheet hr_expense_sequence hr_holidays_leave_auto_approve hr_timesheet_task_required hr_expense_invoice hr_employee_service hr_attendance_autoclose"

    # Helpdesk & Support (5 modules)
    ["helpdesk"]="helpdesk_mgmt helpdesk_mgmt_timesheet helpdesk_mgmt_project helpdesk_ticket_type helpdesk_type_team"

    # Field Service (4 modules)
    ["fieldservice"]="fieldservice fieldservice_agreement fieldservice_sale fieldservice_stock"

    # Manufacturing (6 modules)
    ["manufacturing"]="mrp_bom_cost mrp_production_request mrp_production_putaway_strategy mrp_workorder_sequence mrp_subcontracting_purchase_link mrp_unbuild_tracked_raw_material"

    # Quality & Maintenance (5 modules)
    ["quality"]="quality_control quality_control_stock quality_control_issue maintenance_equipment_sequence maintenance_plan"

    # Contracts & Agreements (4 modules)
    ["contracts"]="contract contract_invoice_start_end_dates contract_payment_mode agreement agreement_legal"

    # Website & eCommerce (6 modules)
    ["website"]="website_sale_suggestion website_sale_wishlist website_sale_stock_available website_sale_product_brand website_snippet_country_dropdown website_sale_require_login"

    # eLearning & Knowledge (4 modules)
    ["elearning"]="website_slides_survey website_slides_forum website_slides_tag knowledge"

    # Reporting & BI (6 modules)
    ["reporting"]="report_xlsx report_xlsx_helper kpi kpi_dashboard report_qweb_pdf_watermark report_py3o"

    # Server Tools & Utilities (8 modules)
    ["tools"]="base_import_match base_user_role base_technical_user scheduler_error_mailer auditlog dbfilter_from_header mail_debrand session_db"

    # Web Enhancements (7 modules)
    ["web"]="web_responsive web_domain_field web_timeline web_widget_color web_advanced_search web_pwa_oca web_m2x_options"

    # Document Management (4 modules)
    ["dms"]="dms dms_field dms_storage dms_attachment_link"

    # Queue & Background Jobs (3 modules)
    ["queue"]="queue_job queue_job_cron queue_job_subscribe"
)

# Category descriptions
declare -A CATEGORY_DESCRIPTIONS=(
    ["ipai"]="IPAI Custom Modules (Studio, Sign, Knowledge)"
    ["accounting"]="Accounting & Finance"
    ["sales"]="Sales & CRM"
    ["purchase"]="Purchase & Procurement"
    ["inventory"]="Inventory & Logistics"
    ["project"]="Project Management"
    ["hr"]="HR & Timesheets"
    ["helpdesk"]="Helpdesk & Support"
    ["fieldservice"]="Field Service"
    ["manufacturing"]="Manufacturing"
    ["quality"]="Quality & Maintenance"
    ["contracts"]="Contracts & Agreements"
    ["website"]="Website & eCommerce"
    ["elearning"]="eLearning & Knowledge"
    ["reporting"]="Reporting & BI"
    ["tools"]="Server Tools & Utilities"
    ["web"]="Web Enhancements"
    ["dms"]="Document Management"
    ["queue"]="Queue & Background Jobs"
)

# Function to check if Odoo is running
check_odoo_running() {
    if ! docker ps --format '{{.Names}}' | grep -q "^${ODOO_CONTAINER}$"; then
        log_error "Odoo container '${ODOO_CONTAINER}' is not running"
        log_info "Start it with: docker compose up -d"
        exit 1
    fi
}

# Function to install a module
install_module() {
    local module=$1
    local category=$2

    log_info "Installing: $module (${category})"

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "[DRY RUN] Would install: $module"
        return 0
    fi

    # Install via odoo-bin CLI
    if docker exec "$ODOO_CONTAINER" odoo \
        --database="$DB_NAME" \
        --init="$module" \
        --stop-after-init \
        --no-http \
        --log-level=error 2>&1 | tee -a "$LOG_FILE"; then
        log_success "Installed: $module"
        return 0
    else
        log_error "Failed to install: $module"
        log_warn "Check log: $LOG_FILE"
        return 1
    fi
}

# Function to install a batch of modules
install_batch() {
    local category=$1
    local modules=${MODULE_BATCHES[$category]}
    local success_count=0
    local fail_count=0

    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  Installing: ${CATEGORY_DESCRIPTIONS[$category]}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    for module in $modules; do
        if install_module "$module" "$category"; then
            ((success_count++))
        else
            ((fail_count++))
        fi
    done

    echo ""
    log_info "Batch summary: ${success_count} succeeded, ${fail_count} failed"
    echo ""

    return "$fail_count"
}

# Function to verify installation
verify_installation() {
    log_info "Verifying installation..."

    local installed_count
    installed_count=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_module_module WHERE state = 'installed';")

    log_success "Total installed modules: $installed_count"

    if [[ "$installed_count" -ge 100 ]]; then
        log_success "✓ Target achieved: $installed_count ≥ 100 modules"
        return 0
    else
        log_warn "⚠ Target not met: $installed_count < 100 modules"
        log_info "Consider installing additional categories"
        return 1
    fi
}

# Main installation flow
main() {
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Enterprise Parity Installation (100+ Modules)${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo ""

    if [[ "$DRY_RUN" == "true" ]]; then
        log_warn "DRY RUN MODE - No modules will be installed"
        echo ""
    fi

    # Check prerequisites
    check_odoo_running

    # Install categories
    local total_batches=0
    local failed_batches=0

    if [[ "$CATEGORY" == "all" ]]; then
        # Install all categories in order
        for category in "${!MODULE_BATCHES[@]}"; do
            # Skip IPAI if requested
            if [[ "$category" == "ipai" && "$SKIP_IPAI" == "true" ]]; then
                log_info "Skipping IPAI modules (--skip-ipai)"
                continue
            fi

            ((total_batches++))
            if ! install_batch "$category"; then
                ((failed_batches++))
            fi
        done
    else
        # Install specific category
        if [[ -z "${MODULE_BATCHES[$CATEGORY]:-}" ]]; then
            log_error "Unknown category: $CATEGORY"
            log_info "Available categories: ${!MODULE_BATCHES[*]}"
            exit 1
        fi

        ((total_batches++))
        if ! install_batch "$CATEGORY"; then
            ((failed_batches++))
        fi
    fi

    # Final summary
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Installation Complete${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo ""

    log_info "Batches processed: $total_batches"
    log_info "Batches with failures: $failed_batches"
    echo ""

    if [[ "$DRY_RUN" == "false" ]]; then
        verify_installation
        echo ""
        log_info "Installation log: $LOG_FILE"
    fi

    echo ""
    log_success "Next steps:"
    echo "  1. Verify modules: ./scripts/verify-enterprise-parity.sh"
    echo "  2. Audit modules: ./scripts/audit-modules.sh"
    echo "  3. Check client actions: ./scripts/check-client-actions.sh"

    exit "$failed_batches"
}

main

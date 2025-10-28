#!/usr/bin/env bash
#
# verify-enterprise-parity.sh - Verify Enterprise parity installation
# Validates that 100+ modules are installed and operational
#
# Usage:
#   ./scripts/verify-enterprise-parity.sh [--report FILE] [--strict]
#
# Exit codes:
#   0: All checks passed
#   1: Critical failures (< 100 modules, IPAI modules not installed)
#   2: Non-critical failures (broken modules, workflow issues)
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
REPORT_FILE=""
STRICT_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --report) REPORT_FILE="$2"; shift 2 ;;
        --strict) STRICT_MODE=true; shift ;;
        *) log_error "Unknown option: $1"; exit 1 ;;
    esac
done

# Default report file
if [[ -z "$REPORT_FILE" ]]; then
    REPORT_FILE="logs/verify-enterprise-parity-$(date +%Y%m%d-%H%M%S).txt"
    mkdir -p logs
fi

# Verification results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
CRITICAL_FAILURES=0

# Report output
report() {
    echo "$1" | tee -a "$REPORT_FILE"
}

# Check function
check() {
    local check_name="$1"
    local check_cmd="$2"
    local is_critical="${3:-false}"

    ((TOTAL_CHECKS++))

    log_info "Checking: $check_name"

    if eval "$check_cmd"; then
        ((PASSED_CHECKS++))
        log_success "✓ $check_name"
        report "✓ $check_name"
        return 0
    else
        ((FAILED_CHECKS++))
        if [[ "$is_critical" == "true" ]]; then
            ((CRITICAL_FAILURES++))
            log_error "✗ $check_name (CRITICAL)"
            report "✗ $check_name (CRITICAL)"
        else
            log_warn "✗ $check_name"
            report "✗ $check_name"
        fi
        return 1
    fi
}

# Check if Odoo is running
check_odoo_running() {
    docker ps --format '{{.Names}}' | grep -q "^${ODOO_CONTAINER}$"
}

# Check module count (≥100)
check_module_count() {
    local count
    count=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_module_module WHERE state = 'installed';")

    report "  → Installed modules: $count"

    if [[ "$count" -ge 100 ]]; then
        return 0
    else
        log_error "Expected ≥100 modules, found $count"
        return 1
    fi
}

# Check IPAI modules installed
check_ipai_modules() {
    local missing_modules=()

    for module in ipai_studio ipai_sign ipai_knowledge; do
        local state
        state=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
            "SELECT state FROM ir_module_module WHERE name = '$module';")

        if [[ "$state" == "installed" ]]; then
            report "  → $module: installed"
        else
            missing_modules+=("$module ($state)")
        fi
    done

    if [[ ${#missing_modules[@]} -eq 0 ]]; then
        return 0
    else
        log_error "IPAI modules not installed: ${missing_modules[*]}"
        return 1
    fi
}

# Check for broken modules
check_broken_modules() {
    local broken_count
    broken_count=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_module_module WHERE state = 'uninstallable';")

    report "  → Broken modules: $broken_count"

    if [[ "$broken_count" -eq 0 ]]; then
        return 0
    else
        log_warn "$broken_count broken modules found"

        # List broken modules
        local broken_list
        broken_list=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
            "SELECT name FROM ir_module_module WHERE state = 'uninstallable';")

        report "  → Broken: $broken_list"
        return 1
    fi
}

# Check for modules to upgrade
check_modules_to_upgrade() {
    local upgrade_count
    upgrade_count=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_module_module WHERE state = 'to upgrade';")

    report "  → Modules to upgrade: $upgrade_count"

    if [[ "$upgrade_count" -eq 0 ]]; then
        return 0
    else
        log_warn "$upgrade_count modules pending upgrade"
        return 1
    fi
}

# Check database integrity
check_database_integrity() {
    # Check for missing tables
    local missing_tables
    missing_tables=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'ir_%';")

    report "  → Core tables: $missing_tables"

    if [[ "$missing_tables" -gt 50 ]]; then
        return 0
    else
        log_error "Database integrity check failed: insufficient core tables"
        return 1
    fi
}

# Check client actions (prevent KeyNotFoundError)
check_client_actions() {
    # Use check-client-actions.sh if available
    if [[ -f "scripts/check-client-actions.sh" ]]; then
        if bash scripts/check-client-actions.sh --ci 2>&1 | tee -a "$REPORT_FILE"; then
            return 0
        else
            return 1
        fi
    else
        log_warn "check-client-actions.sh not found, skipping JS validation"
        return 0
    fi
}

# Check module categories coverage
check_category_coverage() {
    local categories
    categories=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT DISTINCT category FROM ir_module_module WHERE state = 'installed' AND category != '';")

    local category_count
    category_count=$(echo "$categories" | wc -l)

    report "  → Module categories: $category_count"
    report "  → Categories: $categories"

    if [[ "$category_count" -ge 10 ]]; then
        return 0
    else
        log_warn "Low category coverage: $category_count categories"
        return 1
    fi
}

# Check OCA modules installed
check_oca_modules() {
    local oca_count
    oca_count=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_module_module WHERE state = 'installed' AND website LIKE '%github.com/OCA%';")

    report "  → OCA modules: $oca_count"

    if [[ "$oca_count" -ge 80 ]]; then
        return 0
    else
        log_warn "Low OCA module count: $oca_count (expected ≥80)"
        return 1
    fi
}

# Check server actions (workflow test)
check_server_actions() {
    local action_count
    action_count=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_actions_server;")

    report "  → Server actions: $action_count"

    if [[ "$action_count" -gt 0 ]]; then
        return 0
    else
        log_warn "No server actions found"
        return 1
    fi
}

# Check menu items (UI availability test)
check_menu_items() {
    local menu_count
    menu_count=$(docker exec "$POSTGRES_CONTAINER" psql -U odoo -d "$DB_NAME" -tAc \
        "SELECT COUNT(*) FROM ir_ui_menu WHERE active = TRUE;")

    report "  → Active menu items: $menu_count"

    if [[ "$menu_count" -gt 100 ]]; then
        return 0
    else
        log_warn "Low menu item count: $menu_count"
        return 1
    fi
}

# Main verification flow
main() {
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Enterprise Parity Verification${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo ""

    report "════════════════════════════════════════════════════"
    report "  Enterprise Parity Verification Report"
    report "  Date: $(date '+%Y-%m-%d %H:%M:%S')"
    report "  Database: $DB_NAME"
    report "════════════════════════════════════════════════════"
    report ""

    # Critical checks
    report "## Critical Checks"
    check "Odoo container running" check_odoo_running true
    check "Module count (≥100)" check_module_count true
    check "IPAI modules installed" check_ipai_modules true
    check "Database integrity" check_database_integrity true

    echo ""
    report ""

    # Important checks
    report "## Important Checks"
    check "No broken modules" check_broken_modules false
    check "No modules to upgrade" check_modules_to_upgrade false
    check "Client actions valid" check_client_actions false

    echo ""
    report ""

    # Coverage checks
    report "## Coverage Checks"
    check "Category coverage (≥10)" check_category_coverage false
    check "OCA modules (≥80)" check_oca_modules false
    check "Server actions present" check_server_actions false
    check "Menu items (≥100)" check_menu_items false

    echo ""
    report ""

    # Final summary
    report "════════════════════════════════════════════════════"
    report "  Verification Summary"
    report "════════════════════════════════════════════════════"
    report "  Total checks: $TOTAL_CHECKS"
    report "  Passed: $PASSED_CHECKS"
    report "  Failed: $FAILED_CHECKS"
    report "  Critical failures: $CRITICAL_FAILURES"
    report "════════════════════════════════════════════════════"

    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  Verification Summary${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════${NC}"
    echo ""
    log_info "Total checks: $TOTAL_CHECKS"
    log_info "Passed: $PASSED_CHECKS"
    log_info "Failed: $FAILED_CHECKS"
    log_info "Critical failures: $CRITICAL_FAILURES"
    echo ""
    log_info "Report saved to: $REPORT_FILE"
    echo ""

    # Exit code logic
    if [[ "$CRITICAL_FAILURES" -gt 0 ]]; then
        log_error "VERIFICATION FAILED: $CRITICAL_FAILURES critical failures"
        echo ""
        log_info "Next steps:"
        echo "  1. Review report: cat $REPORT_FILE"
        echo "  2. Fix critical issues"
        echo "  3. Re-run verification"
        exit 1
    elif [[ "$FAILED_CHECKS" -gt 0 ]]; then
        if [[ "$STRICT_MODE" == "true" ]]; then
            log_error "VERIFICATION FAILED: $FAILED_CHECKS non-critical failures (strict mode)"
            exit 2
        else
            log_warn "VERIFICATION PASSED WITH WARNINGS: $FAILED_CHECKS non-critical failures"
            echo ""
            log_success "Enterprise parity achieved (100+ modules installed)"
            echo ""
            log_info "Optional improvements:"
            echo "  1. Review warnings in: $REPORT_FILE"
            echo "  2. Install additional modules if needed"
            echo "  3. Run audit: ./scripts/audit-modules.sh"
            exit 0
        fi
    else
        log_success "✓ ALL CHECKS PASSED"
        echo ""
        log_success "Enterprise parity fully verified (100+ modules, no issues)"
        echo ""
        log_info "Next steps:"
        echo "  1. Audit modules: ./scripts/audit-modules.sh"
        echo "  2. Check documentation: docs/ENTERPRISE_PARITY.md"
        exit 0
    fi
}

main

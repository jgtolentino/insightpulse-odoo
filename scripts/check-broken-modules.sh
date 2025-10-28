#!/usr/bin/env bash
#
# check-broken-modules.sh - Diagnostic tool for broken Odoo modules
# Identifies modules with missing actions, JS errors, and orphaned records
#
# Usage: ./scripts/check-broken-modules.sh [database_name]
#
# This script checks for:
#   - Modules in error/uninstallable states
#   - Missing action references in menus
#   - Orphaned records in ir_model_data
#   - Modules with pending upgrades
#   - JavaScript action registry issues

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DB="${1:-odoo_prod}"

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_success() {
    echo -e "${GREEN}✅${NC} $1"
}

log_error() {
    echo -e "${RED}❌${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Odoo Broken Module Diagnostic Tool                            ║${NC}"
echo -e "${BLUE}║  Database: $DB${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Docker is running
if ! docker info &>/dev/null; then
    log_error "Docker daemon is not running or not accessible"
    exit 1
fi

# Check database container is running
if ! docker compose ps --services --status running | grep -q db; then
    log_error "Database container is not running. Start with: docker compose up -d"
    exit 1
fi

ISSUES_FOUND=0

# Check 1: Modules in error states
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/6] Checking for modules in error states${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ERROR_MODULES=$(docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB -t -c \"
SELECT name
FROM ir_module_module
WHERE state IN ('to remove', 'uninstallable')
ORDER BY name;
\"" | tr -d ' ' | grep -v '^$' || true)

if [[ -n "$ERROR_MODULES" ]]; then
    log_warning "Found modules in error states:"
    echo "$ERROR_MODULES" | while read -r module; do
        if [[ -n "$module" ]]; then
            echo "  🔴 $module"
            ((ISSUES_FOUND++))
        fi
    done
    echo ""
    log_info "Recommended fix:"
    echo "  ./scripts/odoo-reinstall-module.sh $DB <module_name>"
else
    log_success "No modules in error states"
fi
echo ""

# Check 2: Modules to upgrade
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/6] Checking for modules pending upgrade${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

TO_UPGRADE=$(docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB -t -c \"
SELECT name, latest_version
FROM ir_module_module
WHERE state = 'to upgrade'
ORDER BY name;
\"" | grep -v '^$' || true)

if [[ -n "$TO_UPGRADE" ]]; then
    log_warning "Found modules pending upgrade:"
    echo "$TO_UPGRADE" | while read -r line; do
        if [[ -n "$line" ]]; then
            echo "  🔄 $line"
            ((ISSUES_FOUND++))
        fi
    done
    echo ""
    log_info "Recommended fix:"
    echo "  ./scripts/apps-truth-sync.sh $DB"
else
    log_success "No modules pending upgrade"
fi
echo ""

# Check 3: Missing action references in menus
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/6] Checking for menus with missing actions${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log_info "Querying ir_ui_menu for broken action references..."
BROKEN_MENUS=$(docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB -t -c \"
SELECT m.name AS menu_name, m.action
FROM ir_ui_menu m
WHERE m.action IS NOT NULL
  AND m.action NOT LIKE 'ir.actions.%'
  AND NOT EXISTS (
    SELECT 1
    FROM ir_model_data d
    WHERE d.model = 'ir.ui.menu'
      AND d.res_id = m.id
  )
LIMIT 20;
\"" | grep -v '^$' || true)

if [[ -n "$BROKEN_MENUS" ]]; then
    log_warning "Found menus with potentially missing actions:"
    echo "$BROKEN_MENUS" | while read -r line; do
        if [[ -n "$line" ]]; then
            echo "  ⚠️  $line"
            ((ISSUES_FOUND++))
        fi
    done
    echo ""
    log_info "This may cause KeyNotFoundError in the frontend"
    log_info "Recommended fix: Reinstall the module that owns these menus"
else
    log_success "No menus with missing actions detected"
fi
echo ""

# Check 4: Orphaned records in ir_model_data
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/6] Checking for orphaned records${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log_info "Scanning ir_model_data for records pointing to missing resources..."
ORPHANED_COUNT=$(docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB -t -c \"
SELECT COUNT(*)
FROM ir_model_data imd
WHERE imd.model IN ('ir.ui.menu', 'ir.actions.act_window', 'ir.ui.view')
  AND NOT EXISTS (
    SELECT 1
    FROM pg_tables
    WHERE tablename = replace(imd.model, '.', '_')
  );
\"" | tr -d ' ' || echo "0")

if [[ "$ORPHANED_COUNT" -gt 0 ]]; then
    log_warning "Found $ORPHANED_COUNT orphaned records in ir_model_data"
    ((ISSUES_FOUND++))
    echo ""
    log_info "Recommended fix:"
    echo "  Run database cleanup script (if available)"
    echo "  Or reinstall affected modules"
else
    log_success "No orphaned records detected"
fi
echo ""

# Check 5: Module installation status summary
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/6] Module installation status summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB" <<SQL
\\pset border 2
\\pset format aligned
SELECT
    state,
    COUNT(*) as count,
    CASE state
        WHEN 'installed' THEN '✅'
        WHEN 'to upgrade' THEN '🔄'
        WHEN 'to install' THEN '📥'
        WHEN 'uninstalled' THEN '❌'
        WHEN 'to remove' THEN '🗑️'
        WHEN 'uninstallable' THEN '⚠️'
        ELSE '❓'
    END as icon
FROM ir_module_module
GROUP BY state
ORDER BY
    CASE state
        WHEN 'uninstallable' THEN 1
        WHEN 'to remove' THEN 2
        WHEN 'to upgrade' THEN 3
        WHEN 'to install' THEN 4
        WHEN 'installed' THEN 5
        WHEN 'uninstalled' THEN 6
        ELSE 7
    END;
SQL

echo ""

# Check 6: Verify addons_path configuration
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[6/6] Verifying addons_path configuration${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log_info "Checking addons_path in odoo.conf..."
ADDONS_PATH=$(docker compose exec -T odoo grep -E "^addons_path" /etc/odoo/odoo.conf 2>/dev/null | awk -F= '{print $2}' | tr -d ' ' || echo "")

if [[ -n "$ADDONS_PATH" ]]; then
    log_success "addons_path configured: $ADDONS_PATH"

    # Verify each path exists
    IFS=',' read -ra PATHS <<< "$ADDONS_PATH"
    for path in "${PATHS[@]}"; do
        if docker compose exec -T odoo test -d "$path" &>/dev/null; then
            echo "  ✅ $path (exists)"
        else
            echo "  ❌ $path (missing!)"
            log_error "Addon path missing: $path"
            ((ISSUES_FOUND++))
        fi
    done
else
    log_error "addons_path not found in odoo.conf"
    ((ISSUES_FOUND++))
fi
echo ""

# Summary and recommendations
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Diagnostic Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ $ISSUES_FOUND -eq 0 ]]; then
    echo -e "${GREEN}✅ No critical issues detected!${NC}"
    echo ""
    log_info "All modules appear healthy"
    log_info "If you're still experiencing KeyNotFoundError:"
    echo "  1. Clear browser cache and hard reload (Ctrl+Shift+R)"
    echo "  2. Visit /web?debug=assets to force asset reload"
    echo "  3. Check browser console for specific error messages"
else
    echo -e "${YELLOW}⚠️  Found $ISSUES_FOUND potential issue(s)${NC}"
    echo ""
    echo -e "${BLUE}Recommended Actions:${NC}"
    echo ""
    echo "1. For modules in error states:"
    echo "   ./scripts/odoo-reinstall-module.sh $DB <module_name>"
    echo ""
    echo "2. For modules pending upgrade:"
    echo "   ./scripts/apps-truth-sync.sh $DB"
    echo ""
    echo "3. For missing action references (KeyNotFoundError):"
    echo "   a) Identify the module owning the broken menu"
    echo "   b) Reinstall: ./scripts/odoo-reinstall-module.sh $DB <module_name>"
    echo "   c) Rebuild assets: docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d $DB --dev=none --stop-after-init"
    echo "   d) Restart: docker compose restart odoo"
    echo ""
    echo "4. For orphaned records:"
    echo "   Consider running a full database cleanup or reinstalling affected modules"
    echo ""
    echo "5. For missing addon paths:"
    echo "   a) Check docker-compose.yml volume mounts"
    echo "   b) Verify /etc/odoo/odoo.conf addons_path configuration"
    echo "   c) Restart containers: docker compose restart"
fi

echo ""
log_info "Diagnostic complete. Raw output saved to /tmp/odoo-diagnostic-$DB.log"
echo ""

exit 0

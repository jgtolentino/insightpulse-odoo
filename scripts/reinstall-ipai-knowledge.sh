#!/usr/bin/env bash
#
# reinstall-ipai-knowledge.sh - Reinstall IPAI Knowledge module
#
# Uninstalls and reinstalls the ipai_knowledge module to ensure clean state
# and proper registry updates.
#
# Usage: ./scripts/reinstall-ipai-knowledge.sh [database_name]
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✅${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; exit 1; }
log_warning() { echo -e "${YELLOW}⚠️${NC} $1"; }

DB="${1:-odoo_prod}"
MODULE="ipai_knowledge"

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  IPAI Knowledge Module Reinstall${NC}"
echo -e "${BLUE}  Database: $DB${NC}"
echo -e "${BLUE}  Module: $MODULE${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# Check if Docker is running
if ! docker compose ps odoo &>/dev/null; then
    log_error "Docker Compose not running or Odoo service not found"
fi

log_info "Checking module status..."
CURRENT_STATE=$(docker compose exec -T odoo bash -lc \
    "psql -U \"\$PGUSER\" -d \"$DB\" -tAc \"SELECT state FROM ir_module_module WHERE name = '$MODULE';\"" \
    2>/dev/null | tr -d '\r\n' || echo "not_found")

if [[ "$CURRENT_STATE" == "not_found" ]]; then
    log_warning "Module $MODULE not found in database"
    log_info "Installing from scratch..."

    docker compose exec odoo python odoo-bin \
        -c /etc/odoo/odoo.conf \
        -d "$DB" \
        -i "$MODULE" \
        --stop-after-init \
        || log_error "Installation failed"

    log_success "Module $MODULE installed"
else
    log_info "Current state: $CURRENT_STATE"

    if [[ "$CURRENT_STATE" == "installed" ]]; then
        log_info "Uninstalling module..."
        docker compose exec odoo python odoo-bin \
            -c /etc/odoo/odoo.conf \
            -d "$DB" \
            -u "$MODULE" \
            --stop-after-init \
            || log_error "Uninstall failed"

        log_success "Module uninstalled"
        sleep 2
    fi

    log_info "Reinstalling module..."
    docker compose exec odoo python odoo-bin \
        -c /etc/odoo/odoo.conf \
        -d "$DB" \
        -i "$MODULE" \
        --stop-after-init \
        || log_error "Reinstall failed"

    log_success "Module $MODULE reinstalled"
fi

echo ""
log_info "Building production assets..."
docker compose exec odoo python odoo-bin \
    -c /etc/odoo/odoo.conf \
    -d "$DB" \
    --dev=none \
    --stop-after-init \
    || log_warning "Asset build failed (non-critical)"

echo ""
log_info "Verifying installation..."
FINAL_STATE=$(docker compose exec -T odoo bash -lc \
    "psql -U \"\$PGUSER\" -d \"$DB\" -tAc \"SELECT state FROM ir_module_module WHERE name = '$MODULE';\"" \
    2>/dev/null | tr -d '\r\n')

if [[ "$FINAL_STATE" == "installed" ]]; then
    log_success "Module $MODULE is installed and ready"
else
    log_error "Module in unexpected state: $FINAL_STATE"
fi

echo ""
log_info "Module details:"
docker compose exec -T odoo bash -lc \
    "psql -U \"\$PGUSER\" -d \"$DB\" -c \"SELECT name, shortdesc, latest_version, state FROM ir_module_module WHERE name = '$MODULE';\"" \
    2>/dev/null || log_warning "Could not fetch module details"

echo ""
echo -e "${GREEN}✅ IPAI Knowledge module reinstall complete${NC}"
echo ""
log_info "Next steps:"
echo "  1. Access module: https://insightpulseai.net/web#action=base.open_module_tree"
echo "  2. Verify knowledge pages load"
echo "  3. Test creating new knowledge articles"

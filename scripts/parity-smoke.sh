#!/usr/bin/env bash
#
# parity-smoke.sh - One-shot smoke test for enterprise parity setup
# Validates Docker services, Odoo version, modules, and database state
#
# Usage: ./scripts/parity-smoke.sh [database_name]
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✅${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; exit 1; }

DB="${1:-odoo_prod}"

echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Enterprise Parity Smoke Test${NC}"
echo -e "${BLUE}  Database: $DB${NC}"
echo -e "${BLUE}════════════════════════════════════════════════${NC}"
echo ""

# 1. Check Docker services
log_info "Checking Docker services..."
docker compose ps || log_error "Docker Compose not running"
log_success "Docker services running"
echo ""

# 2. Check Odoo version
log_info "Checking Odoo version..."
docker compose exec odoo python odoo-bin --version || log_error "Odoo version check failed"
log_success "Odoo version confirmed"
echo ""

# 3. Initialize base module
log_info "Initializing base module..."
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d "$DB" -i base --stop-after-init \
  || log_error "Base module initialization failed"
log_success "Base module initialized"
echo ""

# 4. Update all modules
log_info "Updating all modules..."
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d "$DB" -u all --stop-after-init \
  || log_error "Module update failed"
log_success "All modules updated"
echo ""

# 5. Build production assets
log_info "Building production assets..."
docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d "$DB" --dev=none --stop-after-init \
  || log_error "Asset build failed"
log_success "Production assets built"
echo ""

# 6. Query installed modules
log_info "Querying installed modules..."
INSTALLED_MODULES=$(docker compose exec -T odoo bash -lc \
  "psql -U \"\$PGUSER\" -d \"$DB\" -A -F\",\" -c \"SELECT name, state FROM ir_module_module WHERE state IN ('installed', 'to upgrade') ORDER BY name;\"" \
  2>/dev/null) || log_error "Module query failed"

echo "$INSTALLED_MODULES" | head -20
echo ""

# Count installed modules
INSTALLED_COUNT=$(echo "$INSTALLED_MODULES" | grep -c "installed" || echo 0)
log_success "Total installed modules: $INSTALLED_COUNT"
echo ""

# 7. Check for broken modules
BROKEN_COUNT=$(docker compose exec -T odoo bash -lc \
  "psql -U \"\$PGUSER\" -d \"$DB\" -tAc \"SELECT COUNT(*) FROM ir_module_module WHERE state = 'uninstallable';\"" \
  2>/dev/null | tr -d '\r\n' || echo 0)

if [[ "$BROKEN_COUNT" -eq 0 ]]; then
  log_success "No broken modules"
else
  log_error "$BROKEN_COUNT broken modules found"
fi
echo ""

# 8. Check modules to upgrade
UPGRADE_COUNT=$(docker compose exec -T odoo bash -lc \
  "psql -U \"\$PGUSER\" -d \"$DB\" -tAc \"SELECT COUNT(*) FROM ir_module_module WHERE state = 'to upgrade';\"" \
  2>/dev/null | tr -d '\r\n' || echo 0)

if [[ "$UPGRADE_COUNT" -eq 0 ]]; then
  log_success "No pending upgrades"
else
  log_info "$UPGRADE_COUNT modules pending upgrade (re-run smoke test to apply)"
fi
echo ""

echo -e "${GREEN}✅ Parity smoke test complete${NC}"
echo ""
log_info "Next steps:"
echo "  1. Install enterprise parity: ./scripts/install-enterprise-parity.sh"
echo "  2. Verify installation: ./scripts/verify-enterprise-parity.sh"
echo "  3. Audit modules: ./scripts/audit-modules.sh"

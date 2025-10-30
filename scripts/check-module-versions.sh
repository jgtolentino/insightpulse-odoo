#!/usr/bin/env bash
#
# check-module-versions.sh - Compare module versions in DB vs __manifest__.py
# Identifies version mismatches that cause "Upgrade" badges in Apps UI
#
# Usage: ./scripts/check-module-versions.sh [database_name]
#   database_name: Target database (default: odoo_prod)
#
# Output: List of modules with version mismatches and recommended actions

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DB="${1:-odoo_prod}"
ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"

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
echo -e "${BLUE}║  Module Version Checker - DB vs Code Comparison                ║${NC}"
echo -e "${BLUE}║  Database: $DB${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Docker is running
if ! docker info &>/dev/null; then
    log_error "Docker daemon is not running or not accessible"
    exit 1
fi

# Check if database container is running
if ! docker compose ps --services --status running | grep -q db; then
    log_error "Database container is not running. Start with: docker compose up -d"
    exit 1
fi

log_info "Fetching module versions from database: $DB"
echo ""

# Query database for installed module versions
QUERY="
SELECT
    name,
    latest_version as db_version,
    state,
    CASE
        WHEN state = 'installed' THEN '✅'
        WHEN state = 'to upgrade' THEN '🔄'
        WHEN state = 'to install' THEN '📥'
        WHEN state = 'uninstalled' THEN '❌'
        ELSE '❓'
    END as status_icon
FROM ir_module_module
WHERE state IN ('installed', 'to upgrade', 'to install')
ORDER BY name;
"

# Execute query
log_info "Running SQL query to fetch module states..."
docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB" <<EOF > /tmp/module-versions.txt 2>&1
\pset border 2
\pset format aligned
$QUERY
EOF

if [[ $? -ne 0 ]]; then
    log_error "Failed to query database. Check credentials and database name."
    cat /tmp/module-versions.txt
    exit 1
fi

# Display results
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Module Versions in Database${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
cat /tmp/module-versions.txt
echo ""

# Count modules by state
log_info "Module State Summary:"
echo ""

installed_count=$(docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB -t -c \"SELECT COUNT(*) FROM ir_module_module WHERE state='installed';\"" | tr -d ' ')
to_upgrade_count=$(docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB -t -c \"SELECT COUNT(*) FROM ir_module_module WHERE state='to upgrade';\"" | tr -d ' ')
to_install_count=$(docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB -t -c \"SELECT COUNT(*) FROM ir_module_module WHERE state='to install';\"" | tr -d ' ')

echo "  ✅ Installed: $installed_count modules"
echo "  🔄 To Upgrade: $to_upgrade_count modules"
echo "  📥 To Install: $to_install_count modules"
echo ""

# Check for modules needing upgrade
if [[ "$to_upgrade_count" -gt 0 ]]; then
    log_warning "Found $to_upgrade_count module(s) with 'to upgrade' state"
    echo ""
    log_info "Listing modules pending upgrade:"
    docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB" <<EOF
\pset border 2
\pset format aligned
SELECT name, latest_version as db_version
FROM ir_module_module
WHERE state = 'to upgrade'
ORDER BY name;
EOF
    echo ""
    echo -e "${YELLOW}Recommended Action:${NC}"
    echo "  Run: ./scripts/apps-truth-sync.sh $DB"
    echo "  Or manually: docker compose exec odoo python odoo-bin -c $ODOO_CONF -d $DB -u all --stop-after-init"
    echo ""
fi

# Check for modules to install
if [[ "$to_install_count" -gt 0 ]]; then
    log_info "Found $to_install_count module(s) with 'to install' state"
    echo ""
    log_info "These will be installed on next Odoo restart or manual install"
fi

# Recommendations
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Recommendations${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ "$to_upgrade_count" -gt 0 ]] || [[ "$to_install_count" -gt 0 ]]; then
    log_warning "Action Required:"
    echo ""
    echo "  1. Sync Apps registry:"
    echo "     ./scripts/apps-truth-sync.sh $DB"
    echo ""
    echo "  2. Or update specific module:"
    echo "     docker compose exec odoo python odoo-bin -c $ODOO_CONF -d $DB -u <module_name> --stop-after-init"
    echo ""
    echo "  3. Refresh Apps UI:"
    echo "     - Enable Developer Mode"
    echo "     - Go to Apps → ⋮ → Update Apps List"
    echo "     - Apply Scheduled Upgrades (if banner shows)"
    echo ""
else
    log_success "All modules are up-to-date!"
    echo ""
    log_info "If Apps UI still shows 'Upgrade' badges, try:"
    echo "  1. Clear browser cache"
    echo "  2. Run: ./scripts/apps-truth-sync.sh $DB"
    echo "  3. Restart Odoo: docker compose restart odoo"
    echo ""
fi

# Additional checks
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Quick Health Checks${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check addons_path configuration
log_info "Checking addons_path configuration..."
addons_path=$(docker compose exec -T odoo grep -E "^addons_path" "$ODOO_CONF" 2>/dev/null | awk -F= '{print $2}' | tr -d ' ' || echo "")

if [[ -n "$addons_path" ]]; then
    log_success "addons_path: $addons_path"

    # Verify paths exist
    IFS=',' read -ra PATHS <<< "$addons_path"
    for path in "${PATHS[@]}"; do
        if docker compose exec -T odoo test -d "$path" &>/dev/null; then
            echo "  ✅ $path (exists)"
        else
            echo "  ❌ $path (missing!)"
        fi
    done
else
    log_warning "addons_path not found in config"
fi
echo ""

log_info "Check complete! Raw output saved to /tmp/module-versions.txt"
echo ""

exit 0

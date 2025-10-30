#!/usr/bin/env bash
#
# odoo-reinstall-module.sh - Clean module uninstall, reinstall, and asset rebuild
# Fixes KeyNotFoundError and broken module states in Odoo 19
#
# Usage: ./scripts/odoo-reinstall-module.sh DATABASE MODULE [OCA_URL] [OCA_SUBDIR]
#
# Arguments:
#   DATABASE    - Target database name (default: odoo_prod)
#   MODULE      - Module technical name (e.g., knowledge_notion_clone)
#   OCA_URL     - Optional: Git URL for OCA repo (e.g., https://github.com/OCA/knowledge.git)
#   OCA_SUBDIR  - Optional: Subdirectory in repo if module not at root
#
# Examples:
#   # Reinstall custom module already in /mnt/extra-addons
#   ./scripts/odoo-reinstall-module.sh odoo_prod my_custom_module
#
#   # Reinstall from OCA knowledge repo
#   ./scripts/odoo-reinstall-module.sh odoo_prod knowledge_notion_clone \
#     "https://github.com/OCA/knowledge.git"
#
# This script:
#   1. Safely uninstalls the module (if present)
#   2. Optionally clones/updates OCA repo code
#   3. Reinstalls module from disk
#   4. Rebuilds all assets (production mode)
#   5. Purges stale web asset cache
#   6. Restarts Odoo container

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DB="${1:-odoo_prod}"
MODULE="${2:-}"
OCA_URL="${3:-}"
OCA_SUBDIR="${4:-}"
ODOO_CONF="${ODOO_CONF:-/etc/odoo/odoo.conf}"
ADDONS_DIR="${ADDONS_DIR:-/mnt/extra-addons}"

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

# Validate arguments
if [[ -z "$MODULE" ]]; then
    log_error "Module name is required"
    echo ""
    echo "Usage: $0 DATABASE MODULE [OCA_URL] [OCA_SUBDIR]"
    echo ""
    echo "Examples:"
    echo "  $0 odoo_prod my_module"
    echo "  $0 odoo_prod knowledge_notion_clone https://github.com/OCA/knowledge.git"
    exit 1
fi

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Odoo Module Reinstall - Clean Recovery Toolkit                ║${NC}"
echo -e "${BLUE}║  Database: $DB${NC}"
echo -e "${BLUE}║  Module: $MODULE${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Docker is running
if ! docker info &>/dev/null; then
    log_error "Docker daemon is not running or not accessible"
    exit 1
fi

# Check Odoo container is running
if ! docker compose ps --services --status running | grep -q odoo; then
    log_error "Odoo container is not running. Start with: docker compose up -d"
    exit 1
fi

# Verify Odoo version
log_info "Verifying Odoo installation..."
if ! docker compose exec -T odoo python odoo-bin --version &>/dev/null; then
    log_error "Failed to execute odoo-bin. Check container health."
    exit 1
fi
log_success "Odoo container is healthy"
echo ""

# Step 1: Uninstall module if present
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[1/6] Uninstalling module (if present)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log_info "Checking if module '$MODULE' is installed..."

# Use Python to safely uninstall
docker compose exec -T odoo python - <<PYTHON_UNINSTALL 2>&1 | tee /tmp/odoo-uninstall-$MODULE.log || true
import sys
import odoo
from odoo.api import Environment

# Initialize Odoo
odoo.tools.config.parse_config(['-c', '$ODOO_CONF', '-d', '$DB'])
registry = odoo.registry('$DB')

try:
    with registry.cursor() as cr:
        env = Environment(cr, odoo.SUPERUSER_ID, {})

        # Search for module
        module = env['ir.module.module'].search([('name', '=', '$MODULE')], limit=1)

        if not module:
            print("ℹ️  Module '$MODULE' not found in registry")
            sys.exit(0)

        if module.state in ('installed', 'to upgrade', 'to remove'):
            print(f"🗑️  Uninstalling module '$MODULE' (current state: {module.state})...")
            module.button_immediate_uninstall()
            cr.commit()
            print("✅ Module '$MODULE' uninstalled successfully")
        elif module.state == 'uninstalled':
            print("ℹ️  Module '$MODULE' already uninstalled")
        else:
            print(f"ℹ️  Module '$MODULE' in state: {module.state}")

except Exception as e:
    print(f"❌ Error during uninstall: {e}")
    sys.exit(1)
PYTHON_UNINSTALL

if grep -q "Error during uninstall" /tmp/odoo-uninstall-$MODULE.log; then
    log_error "Uninstall failed. Check /tmp/odoo-uninstall-$MODULE.log"
    exit 1
fi

log_success "Uninstall phase complete"
echo ""

# Step 2: Source code sync (optional OCA clone/update)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[2/6] Syncing module code from source${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [[ -n "$OCA_URL" ]]; then
    log_info "Cloning/updating from OCA repo: $OCA_URL"

    docker compose exec -T odoo bash <<EOF_GIT
set -euo pipefail

# Create temp directory for clone
mkdir -p '$ADDONS_DIR/.tmp'
cd '$ADDONS_DIR/.tmp'

# Clone or update repo
if [ -d repo/.git ]; then
    echo "📦 Updating existing repo..."
    cd repo
    git fetch --all
    git reset --hard origin/HEAD
    git pull
else
    echo "📦 Cloning fresh repo..."
    git clone --depth 1 '$OCA_URL' repo
    cd repo
fi

# Navigate to subdirectory if specified
if [ -n '$OCA_SUBDIR' ]; then
    cd '$OCA_SUBDIR'
fi

# Verify module exists
if [ ! -d '$MODULE' ]; then
    echo "❌ Module '$MODULE' not found in repo"
    exit 1
fi

# Copy module to addons directory
echo "📂 Copying module to $ADDONS_DIR/$MODULE..."
rm -rf '$ADDONS_DIR/$MODULE'
cp -R '$MODULE' '$ADDONS_DIR/$MODULE'

echo "✅ Module code synced from OCA"
EOF_GIT

    if [[ $? -ne 0 ]]; then
        log_error "Failed to sync code from OCA repo"
        exit 1
    fi

    log_success "Module code synced from OCA repo"
else
    log_info "No OCA URL provided, expecting module in $ADDONS_DIR/$MODULE"

    # Verify module exists in addons
    if ! docker compose exec -T odoo test -d "$ADDONS_DIR/$MODULE" &>/dev/null; then
        log_error "Module directory not found: $ADDONS_DIR/$MODULE"
        log_info "Either provide OCA_URL or ensure module exists in addons directory"
        exit 1
    fi

    log_success "Module code found in addons directory"
fi
echo ""

# Step 3: Refresh module registry
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[3/6] Refreshing module registry${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log_info "Scanning addons_path for new modules..."
if docker compose exec -T odoo python odoo-bin -c "$ODOO_CONF" -d "$DB" -i base --stop-after-init 2>&1 | tee /tmp/odoo-refresh-registry.log | grep -qiE "(error|ERROR|CRITICAL)"; then
    log_error "Module registry refresh failed. Check /tmp/odoo-refresh-registry.log"
    exit 1
fi

log_success "Module registry refreshed"
echo ""

# Step 4: Install module
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[4/6] Installing module: $MODULE${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log_info "Installing module with full dependency resolution..."
if docker compose exec -T odoo python odoo-bin -c "$ODOO_CONF" -d "$DB" -i "$MODULE" --stop-after-init 2>&1 | tee /tmp/odoo-install-$MODULE.log | grep -qiE "(error|ERROR|CRITICAL)"; then
    log_error "Module installation failed. Check /tmp/odoo-install-$MODULE.log"
    cat /tmp/odoo-install-$MODULE.log
    exit 1
fi

log_success "Module '$MODULE' installed successfully"
echo ""

# Step 5: Update all modules (sync versions)
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[5/6] Syncing all module versions${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log_info "Updating all modules to match code versions..."
log_warning "This may take 1-3 minutes..."
if docker compose exec -T odoo python odoo-bin -c "$ODOO_CONF" -d "$DB" -u all --stop-after-init 2>&1 | tee /tmp/odoo-update-all.log | grep -qiE "(error|ERROR|CRITICAL)"; then
    log_warning "Module update had errors. Check /tmp/odoo-update-all.log"
else
    log_success "All modules updated successfully"
fi
echo ""

# Step 6: Rebuild assets and purge cache
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}[6/6] Rebuilding assets and purging cache${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

log_info "Building production assets (--dev=none)..."
if docker compose exec -T odoo python odoo-bin -c "$ODOO_CONF" -d "$DB" --dev=none --stop-after-init 2>&1 | tee /tmp/odoo-assets-build.log | grep -qiE "(error|ERROR|CRITICAL)"; then
    log_warning "Asset build had warnings. Check /tmp/odoo-assets-build.log"
else
    log_success "Assets rebuilt successfully"
fi

log_info "Purging stale web asset cache..."
docker compose exec -T odoo bash -c 'rm -rf /var/lib/odoo/.local/share/Odoo/filestore/*/web/assets/* 2>/dev/null || true'
log_success "Asset cache purged"

log_info "Restarting Odoo container to apply changes..."
docker compose restart odoo
log_success "Odoo restarted"
echo ""

# Verification
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  ✅ Module Reinstall Complete!                                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

log_info "Verifying module state in database..."
docker compose exec -T db bash -c "PGPASSWORD=\$POSTGRES_PASSWORD psql -U \$POSTGRES_USER -d $DB" <<SQL
\\pset border 2
\\pset format aligned
SELECT name, latest_version, state, demo
FROM ir_module_module
WHERE name = '$MODULE';
SQL

echo ""
log_success "Module '$MODULE' reinstalled successfully on database '$DB'"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo "  1. Open Odoo: https://insightpulseai.net/odoo"
echo "  2. Hard reload browser (Ctrl+Shift+R / Cmd+Shift+R)"
echo "  3. Or visit: /web?debug=assets (forces asset reload)"
echo "  4. Enable Developer Mode and verify module appears correctly"
echo "  5. Test module functionality"
echo ""
log_info "If issues persist, check browser console for JavaScript errors"
echo ""

exit 0

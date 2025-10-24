#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# Odoo 19 - Automatic Module Installation Script
# Scans all OCA and custom addons and installs them automatically
# ============================================================================

COMPOSE_DIR="${COMPOSE_DIR:-$(pwd)}"
DB_NAME="${1:-odoo}"
ADMIN_PASSWD="${ADMIN_PASSWD:-CHANGE_ME}"

echo "═══════════════════════════════════════════════════════════════"
echo "  Odoo 19 - Automatic Module Installation"
echo "═══════════════════════════════════════════════════════════════"
echo "Database:      $DB_NAME"
echo "Compose Dir:   $COMPOSE_DIR"
echo "═══════════════════════════════════════════════════════════════"

# Change to compose directory if specified, otherwise use current directory
if [[ "$COMPOSE_DIR" != "$(pwd)" ]]; then
    cd "$COMPOSE_DIR"
fi

# Function to extract module names from __manifest__.py files
extract_modules() {
    local base_dir="$1"
    local modules=""

    # Find all __manifest__.py files
    while IFS= read -r manifest; do
        # Get directory name (module name)
        module_dir=$(dirname "$manifest")
        module_name=$(basename "$module_dir")

        # Skip if it's a base directory
        if [[ "$module_name" == "addons" ]] || [[ "$module_name" == "oca" ]]; then
            continue
        fi

        # Check if it's installable (default is True in Odoo)
        installable=$(grep -E "'installable'.*False" "$manifest" || echo "")

        if [[ -z "$installable" ]]; then
            modules="$modules,$module_name"
        fi
    done < <(find "$base_dir" -name "__manifest__.py" -o -name "__openerp__.py")

    echo "$modules"
}

echo "▶ Scanning for available modules..."

# Collect modules from OCA directories
OCA_MODULES=""
if [[ -d "addons/oca" ]]; then
    echo "  → Scanning OCA modules..."
    for oca_repo in addons/oca/*/; do
        if [[ -d "$oca_repo" ]]; then
            repo_name=$(basename "$oca_repo")
            echo "    • $repo_name"
            repo_modules=$(extract_modules "$oca_repo")
            OCA_MODULES="$OCA_MODULES$repo_modules"
        fi
    done
fi

# Collect custom modules
CUSTOM_MODULES=""
if [[ -d "addons" ]]; then
    echo "  → Scanning custom modules..."
    for addon_dir in addons/*/; do
        addon_name=$(basename "$addon_dir")
        # Skip OCA directory
        if [[ "$addon_name" != "oca" ]] && [[ -f "${addon_dir}__manifest__.py" ]]; then
            echo "    • $addon_name"
            CUSTOM_MODULES="$CUSTOM_MODULES,$addon_name"
        fi
    done
fi

# Combine all modules
ALL_MODULES="${OCA_MODULES}${CUSTOM_MODULES}"
# Remove leading comma and duplicates
ALL_MODULES=$(echo "$ALL_MODULES" | sed 's/^,//' | tr ',' '\n' | sort -u | paste -sd ',' -)

echo ""
echo "▶ Modules to install:"
echo "$ALL_MODULES" | tr ',' '\n' | sed 's/^/  • /'
echo ""

# Install modules
echo "▶ Installing modules into database: $DB_NAME"
echo "  This may take 5-10 minutes..."

docker compose exec -T odoo odoo \
    -c /etc/odoo/odoo.conf \
    -d "$DB_NAME" \
    --without-demo=all \
    -i "$ALL_MODULES" \
    --stop-after-init \
    2>&1 | tee /tmp/odoo_install.log

# Check for errors
if grep -q "ERROR\|CRITICAL\|Traceback" /tmp/odoo_install.log; then
    echo ""
    echo "⚠️  Some modules failed to install. Check logs above."
    echo "    Common issues:"
    echo "    - Missing Python dependencies"
    echo "    - Module conflicts"
    echo "    - Database constraints"
    echo ""
    echo "    You can retry individual modules with:"
    echo "    docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d $DB_NAME -i MODULE_NAME --stop-after-init"
else
    echo ""
    echo "✅ All modules installed successfully!"
fi

# Restart services
echo ""
echo "▶ Restarting Odoo services..."
docker compose restart odoo odoo-longpoll

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  Installation Complete!"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "Access your Odoo instance:"
echo "  https://insightpulseai.net"
echo ""
echo "Installed modules include:"
echo "  • Authentication: auth_totp, auth_password_policy, auth_session_timeout"
echo "  • UI: web_responsive, web_environment_ribbon"
echo "  • Jobs: queue_job"
echo "  • Reporting: report_xlsx"
echo "  • Knowledge: knowledge_notion_clone (Notion-style workspace)"
echo "  • Plus all other available OCA modules"
echo ""
echo "To access the Notion-style workspace:"
echo "  Apps → Knowledge → Workspace"
echo ""
echo "═══════════════════════════════════════════════════════════════"

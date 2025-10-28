#!/usr/bin/env bash
#
# sync-oca-repos.sh - Clone/update 30+ OCA repositories for 100+ module coverage
# Smart clone: updates if exists, clones fresh if not
#
# Usage: ./scripts/sync-oca-repos.sh [--dry-run]

set -eo pipefail  # Continue on individual repo failures

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Configuration
DRY_RUN="${1:-}"
BASE_DIR="insightpulse_odoo/addons/oca"
OCA_BASE_URL="https://github.com/OCA"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  OCA Repository Sync Tool - 30+ Repos for 100+ Modules        ║${NC}"
echo -e "${BLUE}║  Target: $BASE_DIR${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ "$DRY_RUN" == "--dry-run" ]]; then
    log_warning "DRY RUN MODE - No changes will be made"
    echo ""
fi

# Ensure base directory exists
if [[ "$DRY_RUN" != "--dry-run" ]]; then
    mkdir -p "$BASE_DIR"
    cd "$BASE_DIR"
    log_success "Working directory: $(pwd)"
else
    log_info "Would create/use directory: $BASE_DIR"
fi

echo ""

# OCA Repository List (30+ repos for comprehensive coverage)
declare -A OCA_REPOS=(
    # Accounting & Finance (6 repos)
    ["account-financial-tools"]="Accounting tools, reconciliation, tax balance"
    ["account-invoicing"]="Invoice workflows, refund management"
    ["account-reconcile"]="Bank reconciliation, statement import"
    ["account-payment"]="Payment orders, SEPA, banking"
    ["account-closing"]="Period closing, fiscal year management"
    ["account-budgeting"]="Budget management and control"

    # Sales & CRM (4 repos)
    ["sale-workflow"]="Sale order workflows, tier validation"
    ["crm"]="CRM enhancements, phonecalls, stages"
    ["sale-reporting"]="Sales analytics and reporting"
    ["commission"]="Sales commission calculation"

    # Purchase & Procurement (3 repos)
    ["purchase-workflow"]="Purchase orders, requests, approvals"
    ["purchase-reporting"]="Purchase analytics"
    ["stock-logistics-transport"]="Delivery methods, carriers"

    # Inventory & Logistics (6 repos)
    ["stock-logistics-workflow"]="Stock workflows, picking operations"
    ["stock-logistics-warehouse"]="Warehouse management, putaway"
    ["stock-logistics-barcode"]="Barcode scanning operations"
    ["stock-logistics-reporting"]="Stock analytics and reports"
    ["delivery-carrier"]="Shipping integrations"
    ["stock-logistics-tracking"]="Lot and serial number tracking"

    # Project & Services (4 repos)
    ["project"]="Project enhancements, timelines, status"
    ["project-reporting"]="Project analytics"
    ["hr"]="HR extensions, employee management"
    ["hr-timesheet"]="Timesheet management"

    # Service Management (4 repos)
    ["helpdesk"]="Helpdesk ticket management"
    ["field-service"]="Field service operations"
    ["maintenance"]="Equipment maintenance"
    ["repair"]="Repair orders management"

    # Manufacturing & Quality (4 repos)
    ["manufacturing"]="MRP enhancements, BOMs"
    ["quality-control"]="Quality checks and inspections"
    ["manufacture-reporting"]="Manufacturing analytics"
    ["product-attribute"]="Product variants, attributes"

    # Contracts & Subscriptions (2 repos)
    ["contract"]="Recurring contracts, subscriptions"
    ["account-analytic"]="Analytic accounting"

    # Website & eCommerce (5 repos)
    ["website"]="Website enhancements"
    ["website-cms"]="Content management"
    ["e-commerce"]="E-commerce features"
    ["website-themes"]="Website themes"
    ["product-pack"]="Product bundles and kits"

    # Knowledge & Collaboration (2 repos)
    ["knowledge"]="Knowledge base, wikis"
    ["dms"]="Document management system"

    # Reporting & BI (3 repos)
    ["reporting-engine"]="Report generation (XLSX, PDF, Py3o)"
    ["mis-builder"]="Management information system builder"
    ["bi"]="Business intelligence extensions"

    # Server Tools & Web (5 repos)
    ["server-tools"]="Server utilities, cron, base tools"
    ["web"]="Web UI enhancements, responsive design"
    ["server-ux"]="Server UX improvements"
    ["server-auth"]="Authentication extensions"
    ["queue"]="Job queue system"

    # Partners & Social (3 repos)
    ["partner-contact"]="Partner/contact enhancements"
    ["social"]="Social media integration"
    ["mail-tracking"]="Email tracking"

    # Multi-Company & Localization (2 repos)
    ["multi-company"]="Multi-company features"
    ["server-brand"]="Branding and theming"

    # IoT & Integration (2 repos)
    ["iot"]="IoT device integration"
    ["connector"]="External system connectors"
)

# Statistics
TOTAL_REPOS=${#OCA_REPOS[@]}
UPDATED_COUNT=0
CLONED_COUNT=0
FAILED_COUNT=0

log_info "Syncing $TOTAL_REPOS OCA repositories..."
echo ""

# Clone or update each repository
for repo in "${!OCA_REPOS[@]}"; do
    DESC="${OCA_REPOS[$repo]}"
    REPO_URL="$OCA_BASE_URL/$repo.git"

    if [[ "$DRY_RUN" == "--dry-run" ]]; then
        log_info "Would sync: $repo"
        continue
    fi

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log_info "Processing: $repo"
    log_info "Description: $DESC"

    if [[ -d "$repo/.git" ]]; then
        # Repository exists - update it
        log_info "Updating existing repository..."
        if (cd "$repo" && git fetch --all 2>&1 && git reset --hard origin/HEAD 2>&1); then
            LATEST_COMMIT=$(cd "$repo" && git log -1 --format="%h %s" 2>/dev/null || echo "unknown")
            log_success "Updated: $repo (Latest: $LATEST_COMMIT)"
            ((UPDATED_COUNT++))
        else
            log_error "Failed to update: $repo"
            ((FAILED_COUNT++))
        fi
    else
        # Repository doesn't exist - clone it
        log_info "Cloning fresh repository..."
        if git clone --depth 1 "$REPO_URL" "$repo" 2>&1 | grep -v "^Cloning\|^remote:"; then
            MODULE_COUNT=$(find "$repo" -maxdepth 2 -name "__manifest__.py" 2>/dev/null | wc -l || echo 0)
            log_success "Cloned: $repo (~$MODULE_COUNT modules)"
            ((CLONED_COUNT++))
        else
            log_error "Failed to clone: $repo"
            ((FAILED_COUNT++))
        fi
    fi

    echo ""
done

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Sync Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ "$DRY_RUN" != "--dry-run" ]]; then
    log_success "Sync complete"
    echo "  📦 Total repositories: $TOTAL_REPOS"
    echo "  ✅ Updated: $UPDATED_COUNT"
    echo "  📥 Cloned: $CLONED_COUNT"
    if [[ $FAILED_COUNT -gt 0 ]]; then
        echo "  ❌ Failed: $FAILED_COUNT"
    fi

    # Count total modules
    echo ""
    log_info "Counting available modules..."
    TOTAL_MODULES=$(find . -maxdepth 3 -name "__manifest__.py" 2>/dev/null | wc -l || echo 0)
    log_success "Found $TOTAL_MODULES modules across all OCA repositories"

    echo ""
    log_info "Next steps:"
    echo "  1. Verify modules: ls -la $BASE_DIR/"
    echo "  2. Refresh Odoo registry: docker compose exec odoo python odoo-bin -c /etc/odoo/odoo.conf -d odoo_prod -i base --stop-after-init"
    echo "  3. Install modules: ./scripts/install-enterprise-parity.sh"
else
    echo "  DRY RUN: Would process $TOTAL_REPOS repositories"
    echo ""
    log_info "Run without --dry-run to apply changes"
fi

echo ""
exit 0

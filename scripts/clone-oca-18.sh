#!/usr/bin/env bash
# InsightPulse AI - OCA 18.0 Repository Cloner
# Clones all necessary OCA repositories for Odoo 18 Community Edition
#
# Usage:
#   ./scripts/clone-oca-18.sh [target_directory]
#
# Default target: ./oca (relative to current directory)

set -euo pipefail

# Configuration
TARGET_DIR="${1:-./oca}"
BRANCH="18.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# OCA repositories needed for our modules
# Organized by category for clarity
REPOS=(
    # Web & Server Tools
    "web"
    "server-tools"

    # Sales & Purchase
    "sale-workflow"
    "purchase-workflow"

    # Stock & Logistics
    "stock-logistics-workflow"
    "stock-logistics-reporting"

    # Accounting & Finance
    "account-financial-tools"
    "account-invoicing"
    "bank-statement-import"

    # Reporting
    "reporting-engine"
    "mis-builder"

    # HR & Timesheet
    "hr"
    "hr-attendance"
    "hr-expense"
    "timesheet"

    # Project Management
    "project"

    # Integration
    "connector"
    "queue"
)

# Create target directory
print_info "Creating target directory: ${TARGET_DIR}"
mkdir -p "${TARGET_DIR}"
cd "${TARGET_DIR}"

print_success "Target directory ready: $(pwd)"
echo ""

# Clone each repository
TOTAL=${#REPOS[@]}
CURRENT=0
SKIPPED=0
CLONED=0
FAILED=0

for repo in "${REPOS[@]}"; do
    CURRENT=$((CURRENT + 1))
    print_info "[${CURRENT}/${TOTAL}] Processing: ${repo}"

    if [ -d "${repo}" ]; then
        print_warning "Repository already exists, skipping: ${repo}"
        SKIPPED=$((SKIPPED + 1))
    else
        if git clone --depth 1 -b "${BRANCH}" "https://github.com/OCA/${repo}.git" 2>/dev/null; then
            print_success "Cloned: ${repo}"
            CLONED=$((CLONED + 1))
        else
            print_error "Failed to clone: ${repo}"
            FAILED=$((FAILED + 1))
        fi
    fi
    echo ""
done

# Summary
echo "======================================"
echo "OCA 18.0 Clone Summary"
echo "======================================"
echo ""
echo "Total repositories: ${TOTAL}"
echo "Cloned:             ${CLONED}"
echo "Skipped (existing): ${SKIPPED}"
echo "Failed:             ${FAILED}"
echo ""

if [ ${FAILED} -gt 0 ]; then
    print_warning "Some repositories failed to clone. This may be normal if:"
    print_warning "  - The repository doesn't have an 18.0 branch yet"
    print_warning "  - You don't have internet connectivity"
    print_warning "  - The repository was renamed or archived"
    echo ""
fi

print_success "OCA 18.0 repositories are ready in: ${TARGET_DIR}"
echo ""
echo "Next steps:"
echo "  1. Update your odoo.conf addons_path to include these directories"
echo "  2. Restart Odoo: docker-compose restart odoo"
echo "  3. Update Apps List: Apps → Update Apps List"
echo "  4. Install modules using the wave files in install-waves/"
echo ""

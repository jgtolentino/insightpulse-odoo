#!/usr/bin/env bash
#
# reorganize-oca-addons.sh - Move scattered OCA repos into addons/oca/ subdirectory
# Preserves .git directories for future updates
#
# Usage: ./scripts/reorganize-oca-addons.sh [--dry-run]

set -euo pipefail

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
BASE_DIR="insightpulse_odoo"
OCA_TARGET_DIR="$BASE_DIR/addons/oca"
CUSTOM_DIR="$BASE_DIR/addons/custom"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  OCA Addons Reorganization Tool                                ║${NC}"
echo -e "${BLUE}║  Target: $OCA_TARGET_DIR${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [[ "$DRY_RUN" == "--dry-run" ]]; then
    log_warning "DRY RUN MODE - No changes will be made"
    echo ""
fi

# Check if we're in the right directory
if [[ ! -d "$BASE_DIR" ]]; then
    log_error "Directory $BASE_DIR not found. Run from repository root."
    exit 1
fi

# Create OCA target directory
if [[ "$DRY_RUN" != "--dry-run" ]]; then
    mkdir -p "$OCA_TARGET_DIR"
    log_success "Created $OCA_TARGET_DIR"
else
    log_info "Would create $OCA_TARGET_DIR"
fi

# Find OCA repos in addons directory (exclude custom modules)
log_info "Scanning for OCA repositories in $BASE_DIR/addons..."
echo ""

OCA_REPOS=(
    "account-budgeting"
    "account-financial-reporting"
    "dms"
    "knowledge"
    "mis-builder"
    "project"
    "queue"
    "reporting-engine"
    "server-tools"
    "web"
)

MOVED_COUNT=0
SKIPPED_COUNT=0

for repo in "${OCA_REPOS[@]}"; do
    SOURCE="$BASE_DIR/addons/$repo"
    TARGET="$OCA_TARGET_DIR/$repo"

    if [[ -d "$SOURCE" ]]; then
        if [[ -d "$TARGET" ]]; then
            log_warning "$repo already exists in oca/ - skipping"
            ((SKIPPED_COUNT++))
        else
            if [[ "$DRY_RUN" != "--dry-run" ]]; then
                mv "$SOURCE" "$TARGET"
                log_success "Moved $repo → oca/$repo"
                ((MOVED_COUNT++))
            else
                log_info "Would move $repo → oca/$repo"
                ((MOVED_COUNT++))
            fi
        fi
    else
        log_info "$repo not found in addons/ - will be cloned fresh"
    fi
done

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

if [[ "$DRY_RUN" != "--dry-run" ]]; then
    log_success "Reorganization complete"
    echo "  ✅ Moved: $MOVED_COUNT repositories"
    echo "  ⚠️  Skipped: $SKIPPED_COUNT repositories (already in oca/)"
    echo ""
    log_info "Next steps:"
    echo "  1. Verify structure: ls -la $OCA_TARGET_DIR/"
    echo "  2. Run: ./scripts/sync-oca-repos.sh"
    echo "  3. Update docker-compose.yml if needed (ensure oca/ in addons_path)"
else
    echo "  DRY RUN: Would move $MOVED_COUNT repositories"
    echo "  DRY RUN: Would skip $SKIPPED_COUNT repositories"
    echo ""
    log_info "Run without --dry-run to apply changes"
fi

echo ""
exit 0

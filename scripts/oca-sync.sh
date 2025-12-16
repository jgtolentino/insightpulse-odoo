#!/bin/bash
set -euo pipefail

# OCA Repository Vendoring Script
# Clones/updates OCA repositories to vendor/oca/ at pinned commits from oca.lock.json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOCK_FILE="$PROJECT_ROOT/oca.lock.json"
VENDOR_DIR="$PROJECT_ROOT/vendor/oca"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if jq is available
if ! command -v jq &> /dev/null; then
    log_error "jq is required but not installed. Please install it:"
    log_error "  macOS: brew install jq"
    log_error "  Ubuntu: apt-get install jq"
    exit 1
fi

# Check if lock file exists
if [[ ! -f "$LOCK_FILE" ]]; then
    log_error "Lock file not found: $LOCK_FILE"
    exit 1
fi

# Create vendor directory if it doesn't exist
mkdir -p "$VENDOR_DIR"

# Parse lock file and process each repository
log_info "Reading OCA lock file: $LOCK_FILE"
repos=$(jq -r '.repositories | keys[]' "$LOCK_FILE")

for repo in $repos; do
    log_info "Processing repository: $repo"

    # Extract repository details
    url=$(jq -r ".repositories.\"$repo\".url" "$LOCK_FILE")
    branch=$(jq -r ".repositories.\"$repo\".branch" "$LOCK_FILE")
    commit=$(jq -r ".repositories.\"$repo\".commit" "$LOCK_FILE")

    repo_dir="$VENDOR_DIR/$repo"

    # Clone or update repository
    if [[ -d "$repo_dir/.git" ]]; then
        log_info "  Repository exists, updating..."
        cd "$repo_dir"

        # Fetch latest changes
        git fetch origin "$branch" --quiet

        # Check current commit
        current_commit=$(git rev-parse HEAD)
        if [[ "$current_commit" == "$commit" ]]; then
            log_info "  Already at pinned commit: $commit"
        else
            log_warn "  Current commit ($current_commit) differs from pinned ($commit)"
            log_info "  Checking out pinned commit: $commit"
            git checkout "$commit" --quiet
            log_info "  ✅ Updated to pinned commit"
        fi
    else
        log_info "  Cloning repository..."
        git clone --branch "$branch" --single-branch "$url" "$repo_dir" --quiet
        cd "$repo_dir"
        git checkout "$commit" --quiet
        log_info "  ✅ Cloned and checked out pinned commit: $commit"
    fi

    cd "$PROJECT_ROOT"
done

log_info ""
log_info "✅ OCA vendoring complete!"
log_info ""
log_info "Vendored repositories:"
for repo in $repos; do
    repo_dir="$VENDOR_DIR/$repo"
    if [[ -d "$repo_dir" ]]; then
        cd "$repo_dir"
        current_commit=$(git rev-parse --short HEAD)
        echo "  - $repo @ $current_commit"
    fi
done

cd "$PROJECT_ROOT"
log_info ""
log_info "Next steps:"
log_info "  1. Update odoo.conf addons_path to include vendor/oca repositories"
log_info "  2. Restart Odoo: docker compose restart odoo"
log_info "  3. Install OCA modules via Odoo UI or CLI"

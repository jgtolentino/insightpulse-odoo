#!/usr/bin/env bash
#
# sync-live-to-docs.sh - Append live module inventory to parity documentation
#
# Finds the most recent live module snapshot and appends it to
# docs/ENTERPRISE_PARITY.md for tracking enterprise parity progress.
#
# Usage: ./scripts/sync-live-to-docs.sh
#

set -euo pipefail

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✅${NC} $1"; }

# Find latest snapshot
LATEST_MD="$(ls -t reports/live_modules_*.md 2>/dev/null | head -n1 || echo "")"

if [[ -z "$LATEST_MD" ]]; then
    echo "ERROR: No live module snapshots found in reports/"
    echo "Run scripts/export-live-modules.py first"
    exit 1
fi

DOC="docs/ENTERPRISE_PARITY.md"

if [[ ! -f "$DOC" ]]; then
    echo "ERROR: $DOC not found"
    exit 1
fi

log_info "Found latest snapshot: $LATEST_MD"
log_info "Appending to $DOC..."

# Append to documentation
echo -e "\n\n---\n\n" >> "$DOC"
cat "$LATEST_MD" >> "$DOC"

log_success "Live inventory synced to documentation"
echo ""
echo "Next steps:"
echo "  git add reports/ $DOC"
echo "  git commit -m \"docs(parity): sync live module inventory → $(basename "$LATEST_MD")\""
echo "  git push"

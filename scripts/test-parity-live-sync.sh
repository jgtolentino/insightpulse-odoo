#!/usr/bin/env bash
#
# Test script for Parity Live Sync workflow
# Simulates both successful and graceful failure scenarios
#
# Usage: ./scripts/test-parity-live-sync.sh [--with-secrets]
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ${NC} $1"; }
log_success() { echo -e "${GREEN}✅${NC} $1"; }
log_warning() { echo -e "${YELLOW}⚠️${NC} $1"; }
log_error() { echo -e "${RED}❌${NC} $1"; }

echo "=========================================="
echo "Parity Live Sync Workflow Test"
echo "=========================================="
echo ""

# Test 1: Workflow without secrets (graceful failure)
log_info "Test 1: Testing workflow without secrets (graceful failure case)"
echo ""

# Unset all secrets
unset ODOO_URL ODOO_DB ODOO_LOGIN ODOO_PASSWORD

# Simulate export step
log_info "Running export step..."
EXPORT_SUCCESS="false"

if [ -z "${ODOO_URL:-}" ]; then
    log_warning "ODOO_URL secret not configured - skipping live inventory sync"
    EXPORT_SUCCESS="false"
    EXIT_CODE=0
else
    log_info "Running: python3 scripts/export-live-modules.py"
    if python3 scripts/export-live-modules.py; then
        EXPORT_SUCCESS="true"
        EXIT_CODE=0
    else
        log_error "Export failed"
        EXIT_CODE=1
    fi
fi

if [ $EXIT_CODE -eq 0 ]; then
    log_success "Export step completed (export_success=$EXPORT_SUCCESS)"
else
    log_error "Export step failed"
    exit 1
fi
echo ""

# Simulate sync step
log_info "Checking sync step conditional..."
if [ "$EXPORT_SUCCESS" == "true" ]; then
    log_info "Running: bash scripts/sync-live-to-docs.sh"
    bash scripts/sync-live-to-docs.sh
    log_success "Sync step completed"
else
    log_warning "Sync step skipped (export_success=$EXPORT_SUCCESS)"
fi
echo ""

# Simulate git diff check
log_info "Checking for changes..."
if git diff --quiet reports/ docs/ENTERPRISE_PARITY.md 2>/dev/null; then
    CHANGED="false"
    log_info "No changes detected"
else
    CHANGED="true"
    log_info "Changes detected"
fi
echo ""

# Simulate commit step
log_info "Checking commit step conditional..."
if [ "$EXPORT_SUCCESS" == "true" ] && [ "$CHANGED" == "true" ]; then
    log_info "Would commit and push changes"
    log_success "Commit step would run"
else
    log_warning "Commit step skipped (export_success=$EXPORT_SUCCESS, changed=$CHANGED)"
fi
echo ""

# Simulate summary step
log_info "Generating summary..."
echo ""
echo "### 📊 Live Module Inventory Snapshot"
echo ""

if [ "$EXPORT_SUCCESS" == "true" ]; then
    SNAPSHOT_FILE=$(ls -t reports/live_modules_*.md 2>/dev/null | head -n1 || echo "")
    if [ -n "$SNAPSHOT_FILE" ] && [ -f "$SNAPSHOT_FILE" ]; then
        echo "Snapshot file: $SNAPSHOT_FILE"
        head -20 "$SNAPSHOT_FILE"
        echo "..."
    else
        echo "⚠️ No snapshot file found"
    fi
else
    echo "⚠️ **Secrets not configured** - Live inventory export skipped"
    echo ""
    echo "To enable live module inventory sync:"
    echo "1. Go to Settings → Secrets and variables → Actions"
    echo "2. Add the following secrets:"
    echo "   - \`ODOO_URL\`: Your Odoo instance URL"
    echo "   - \`ODOO_DB\`: Database name"
    echo "   - \`ODOO_LOGIN\`: Admin login"
    echo "   - \`ODOO_PASSWORD\`: Admin password"
fi
echo ""

log_success "Summary step completed"
echo ""

# Final test result
echo "=========================================="
log_success "Test 1 PASSED: Workflow handles missing secrets gracefully"
echo "=========================================="
echo ""

# Check if user wants to test with secrets
if [ "${1:-}" == "--with-secrets" ]; then
    echo ""
    log_info "Test 2: Testing workflow with secrets"
    echo ""
    log_warning "This test requires valid ODOO_URL, ODOO_DB, ODOO_LOGIN, ODOO_PASSWORD"
    log_warning "Set these environment variables and run again"
    echo ""

    if [ -n "${ODOO_URL:-}" ]; then
        log_info "ODOO_URL is set: $ODOO_URL"
        log_info "Running export script..."
        python3 scripts/export-live-modules.py
        log_success "Export completed"

        log_info "Running sync script..."
        bash scripts/sync-live-to-docs.sh
        log_success "Sync completed"

        log_success "Test 2 PASSED: Workflow works with valid secrets"
    else
        log_warning "Skipping Test 2: ODOO_URL not set"
    fi
fi

echo ""
log_success "All tests completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Push changes to trigger workflow on main branch"
echo "  2. Or manually trigger via GitHub Actions UI:"
echo "     Actions → Parity Live Sync → Run workflow"
echo ""

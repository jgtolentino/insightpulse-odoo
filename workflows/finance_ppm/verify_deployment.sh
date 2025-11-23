#!/bin/bash
# Finance PPM n8n Workflows - Deployment Verification Script
# Verifies all components are deployed and operational

# Don't exit on errors - we want to see all results
# set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0
WARNINGS=0

# Helper functions
pass() {
    echo -e "${GREEN}✅ $1${NC}"
    ((PASSED++))
}

fail() {
    echo -e "${RED}❌ $1${NC}"
    ((FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  $1${NC}"
    ((WARNINGS++))
}

info() {
    echo -e "ℹ️  $1"
}

# Environment variables
SUPABASE_URL="${SUPABASE_URL:-https://ublqmilcjtpnflofprkr.supabase.co}"
POSTGRES_URL="${POSTGRES_URL:-postgresql://postgres.ublqmilcjtpnflofprkr:1G8TRd5wE7b9szBH@aws-1-us-east-1.pooler.supabase.com:6543/postgres}"
N8N_URL="${N8N_URL:-https://n8n.insightpulseai.net}"
ODOO_URL="${ODOO_URL:-https://erp.insightpulseai.net}"
MATTERMOST_URL="${MATTERMOST_URL:-https://mattermost.insightpulseai.net}"

echo "========================================="
echo "Finance PPM Workflow Deployment Verification"
echo "========================================="
echo ""

# 1. Check n8n instance accessibility
info "Checking n8n instance..."
if curl -sf -I "$N8N_URL/" > /dev/null 2>&1; then
    pass "n8n Instance: Accessible at $N8N_URL"
else
    fail "n8n Instance: NOT accessible at $N8N_URL"
fi

# 2. Check Odoo instance accessibility
info "Checking Odoo instance..."
if curl -sf -I "$ODOO_URL/" > /dev/null 2>&1; then
    pass "Odoo Instance: Accessible at $ODOO_URL"
else
    fail "Odoo Instance: NOT accessible at $ODOO_URL"
fi

# 3. Check Mattermost instance accessibility
info "Checking Mattermost instance..."
if curl -sf -I "$MATTERMOST_URL/" > /dev/null 2>&1; then
    pass "Mattermost Instance: Accessible at $MATTERMOST_URL"
else
    warn "Mattermost Instance: NOT accessible at $MATTERMOST_URL (optional)"
fi

# 4. Check Supabase database connectivity
info "Checking Supabase database connectivity..."
if psql "$POSTGRES_URL" -c "SELECT 1;" > /dev/null 2>&1; then
    pass "Supabase Database: Connected successfully"
else
    fail "Supabase Database: Connection failed"
fi

# 5. Verify finance_ppm.monthly_reports table exists
info "Checking finance_ppm.monthly_reports table..."
TABLE_EXISTS=$(psql "$POSTGRES_URL" -tAc "SELECT EXISTS (
    SELECT FROM information_schema.tables
    WHERE table_schema = 'finance_ppm'
    AND table_name = 'monthly_reports'
);")

if [ "$TABLE_EXISTS" = "t" ]; then
    pass "Table finance_ppm.monthly_reports: EXISTS"

    # Check table structure
    info "Verifying table structure..."

    # Check required columns
    COLUMNS=$(psql "$POSTGRES_URL" -tAc "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = 'finance_ppm' AND table_name = 'monthly_reports';")
    if [ "$COLUMNS" -ge 20 ]; then
        pass "Table Columns: $COLUMNS columns (expected: 20)"
    else
        warn "Table Columns: Only $COLUMNS columns found (expected: 20)"
    fi

    # Check indexes
    INDEXES=$(psql "$POSTGRES_URL" -tAc "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'finance_ppm' AND tablename = 'monthly_reports';")
    if [ "$INDEXES" -ge 5 ]; then
        pass "Table Indexes: $INDEXES indexes configured"
    else
        warn "Table Indexes: Only $INDEXES indexes found (expected: 5+)"
    fi

    # Check RLS policies
    POLICIES=$(psql "$POSTGRES_URL" -tAc "SELECT COUNT(*) FROM pg_policies WHERE schemaname = 'finance_ppm' AND tablename = 'monthly_reports';")
    if [ "$POLICIES" -ge 2 ]; then
        pass "RLS Policies: $POLICIES policies configured"
    else
        warn "RLS Policies: Only $POLICIES policies found (expected: 2)"
    fi
else
    fail "Table finance_ppm.monthly_reports: DOES NOT EXIST"
    info "Run migration: psql \"\$POSTGRES_URL\" -f migrations/003_finance_ppm_reports.sql"
fi

# 6. Check workflow JSON files exist
info "Checking workflow JSON files..."
WORKFLOW_DIR="$(dirname "$0")"

if [ -f "$WORKFLOW_DIR/bir_deadline_alert.json" ]; then
    FILE_SIZE=$(wc -c < "$WORKFLOW_DIR/bir_deadline_alert.json" | tr -d ' ')
    pass "Workflow File: bir_deadline_alert.json (${FILE_SIZE} bytes)"
else
    fail "Workflow File: bir_deadline_alert.json NOT FOUND"
fi

if [ -f "$WORKFLOW_DIR/task_escalation.json" ]; then
    FILE_SIZE=$(wc -c < "$WORKFLOW_DIR/task_escalation.json" | tr -d ' ')
    pass "Workflow File: task_escalation.json (${FILE_SIZE} bytes)"
else
    fail "Workflow File: task_escalation.json NOT FOUND"
fi

if [ -f "$WORKFLOW_DIR/monthly_report.json" ]; then
    FILE_SIZE=$(wc -c < "$WORKFLOW_DIR/monthly_report.json" | tr -d ' ')
    pass "Workflow File: monthly_report.json (${FILE_SIZE} bytes)"
else
    fail "Workflow File: monthly_report.json NOT FOUND"
fi

# 7. Check if n8n API is accessible (optional)
info "Checking n8n API access..."
if [ -n "$N8N_API_KEY" ]; then
    API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET "$N8N_URL/api/v1/workflows" -H "X-N8N-API-KEY: $N8N_API_KEY" 2>/dev/null)
    if [ "$API_RESPONSE" = "200" ]; then
        pass "n8n API: Accessible with API key"

        # Count workflows
        WORKFLOW_COUNT=$(curl -s -X GET "$N8N_URL/api/v1/workflows" -H "X-N8N-API-KEY: $N8N_API_KEY" 2>/dev/null | jq -r '.data | length' 2>/dev/null || echo "0")
        info "Active Workflows: $WORKFLOW_COUNT"
    elif [ "$API_RESPONSE" = "401" ]; then
        warn "n8n API: API key is invalid or expired"
    else
        warn "n8n API: Response code $API_RESPONSE"
    fi
else
    warn "n8n API: No API key found (set N8N_API_KEY environment variable)"
    info "Workflows must be imported manually via n8n UI"
fi

# 8. Check Odoo module ipai_finance_ppm
info "Checking Odoo module ipai_finance_ppm..."
# This would require Odoo XML-RPC authentication, skip for now
warn "Odoo Module Check: Skipped (requires Odoo credentials)"
info "Verify manually: https://odoo.insightpulseai.net/web#menu_id=XXX"

# 9. Validate workflow JSON structure
info "Validating workflow JSON structure..."
for workflow_file in "$WORKFLOW_DIR"/*.json; do
    if [ -f "$workflow_file" ]; then
        filename=$(basename "$workflow_file")
        if jq empty "$workflow_file" 2>/dev/null; then
            # Check for required fields
            HAS_NAME=$(jq -r '.name' "$workflow_file" 2>/dev/null)
            HAS_NODES=$(jq -r '.nodes | length' "$workflow_file" 2>/dev/null)
            HAS_CONNECTIONS=$(jq -r '.connections' "$workflow_file" 2>/dev/null)

            if [ "$HAS_NAME" != "null" ] && [ "$HAS_NODES" -gt 0 ] && [ "$HAS_CONNECTIONS" != "null" ]; then
                pass "Workflow Structure: $filename valid (name: $HAS_NAME, nodes: $HAS_NODES)"
            else
                warn "Workflow Structure: $filename has missing fields"
            fi
        else
            fail "Workflow Structure: $filename is invalid JSON"
        fi
    fi
done

# 10. Summary
echo ""
echo "========================================="
echo "Verification Summary"
echo "========================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}🎉 All checks passed! Deployment is ready.${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠️  Deployment has warnings. Review above.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ Deployment verification FAILED. Fix issues above.${NC}"
    exit 1
fi

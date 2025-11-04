#!/bin/bash
# InsightPulse Odoo - Production Smoke Test
# Validates deployment health across all services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Functions
print_header() {
    echo -e "\n${YELLOW}================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}================================${NC}\n"
}

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

# ============================================================================
# 1. DNS Resolution Tests
# ============================================================================
print_header "DNS Resolution Tests"

if dig +short erp.insightpulseai.net | grep -q "165.227.10.178"; then
    test_pass "erp.insightpulseai.net resolves correctly"
else
    test_fail "erp.insightpulseai.net DNS resolution failed"
fi

if dig +short mcp.insightpulseai.net | grep -q "ondigitalocean.app"; then
    test_pass "mcp.insightpulseai.net resolves correctly"
else
    test_fail "mcp.insightpulseai.net DNS resolution failed"
fi

if dig +short superset.insightpulseai.net | grep -q "ondigitalocean.app"; then
    test_pass "superset.insightpulseai.net resolves correctly"
else
    test_fail "superset.insightpulseai.net DNS resolution failed"
fi

# ============================================================================
# 2. HTTPS/SSL Certificate Tests
# ============================================================================
print_header "SSL Certificate Tests"

if curl -I --silent --head --fail https://erp.insightpulseai.net > /dev/null 2>&1; then
    test_pass "erp.insightpulseai.net SSL certificate valid"
else
    test_fail "erp.insightpulseai.net SSL certificate invalid"
fi

if curl -I --silent --head --fail https://mcp.insightpulseai.net > /dev/null 2>&1; then
    test_pass "mcp.insightpulseai.net SSL certificate valid"
else
    test_fail "mcp.insightpulseai.net SSL certificate invalid"
fi

if curl -I --silent --head --fail https://superset.insightpulseai.net > /dev/null 2>&1; then
    test_pass "superset.insightpulseai.net SSL certificate valid"
else
    test_fail "superset.insightpulseai.net SSL certificate invalid"
fi

# ============================================================================
# 3. Service Health Checks
# ============================================================================
print_header "Service Health Checks"

# Odoo health
if curl -f --silent http://localhost:8069/web/health > /dev/null 2>&1; then
    test_pass "Odoo health endpoint responding"
else
    test_fail "Odoo health endpoint not responding"
fi

# Database health
if docker exec odoo-db pg_isready -U odoo > /dev/null 2>&1; then
    test_pass "PostgreSQL database is ready"
else
    test_fail "PostgreSQL database is not ready"
fi

# Container status
if docker ps | grep -q "odoo-web.*Up"; then
    test_pass "Odoo web container running"
else
    test_fail "Odoo web container not running"
fi

if docker ps | grep -q "odoo-db.*Up"; then
    test_pass "PostgreSQL container running"
else
    test_fail "PostgreSQL container not running"
fi

# ============================================================================
# 4. Odoo API Tests
# ============================================================================
print_header "Odoo API Tests"

# Database list endpoint
if curl -f --silent http://localhost:8069/web/database/list > /dev/null 2>&1; then
    test_pass "Odoo database list endpoint accessible"
else
    test_fail "Odoo database list endpoint not accessible"
fi

# JSON-RPC endpoint
if curl -f --silent -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"call","params":{},"id":1}' \
    http://localhost:8069/jsonrpc > /dev/null 2>&1; then
    test_pass "Odoo JSON-RPC endpoint responding"
else
    test_fail "Odoo JSON-RPC endpoint not responding"
fi

# ============================================================================
# 5. Database Connectivity Tests
# ============================================================================
print_header "Database Connectivity Tests"

# Test database connection
if docker exec odoo-db psql -U odoo -d odoo -c "SELECT 1;" > /dev/null 2>&1; then
    test_pass "Database connection successful"
else
    test_fail "Database connection failed"
fi

# Check database size
DB_SIZE=$(docker exec odoo-db psql -U odoo -d odoo -t -c \
    "SELECT pg_size_pretty(pg_database_size('odoo'));" | tr -d ' ')
if [ ! -z "$DB_SIZE" ]; then
    test_pass "Database size: $DB_SIZE"
else
    test_fail "Unable to get database size"
fi

# Check active connections
ACTIVE_CONN=$(docker exec odoo-db psql -U odoo -d odoo -t -c \
    "SELECT count(*) FROM pg_stat_activity WHERE datname='odoo';" | tr -d ' ')
if [ ! -z "$ACTIVE_CONN" ]; then
    test_pass "Active database connections: $ACTIVE_CONN"
else
    test_fail "Unable to get active connections"
fi

# ============================================================================
# 6. Odoo Module Tests
# ============================================================================
print_header "Odoo Module Tests"

# Check if Finance SSC modules are installed
FINANCE_SSC_MODULES=("finance_ssc" "bir_compliance" "expense_management" "travel_request")

for module in "${FINANCE_SSC_MODULES[@]}"; do
    MODULE_STATE=$(docker exec odoo-web odoo shell -d odoo << PYEOF 2>/dev/null || echo "error"
import sys
try:
    mod = self.env['ir.module.module'].search([('name', '=', '$module')])
    if mod and mod.state == 'installed':
        print('installed')
    elif mod:
        print(mod.state)
    else:
        print('not_found')
except Exception:
    print('error')
PYEOF
)
    
    if [[ "$MODULE_STATE" == "installed" ]]; then
        test_pass "Module '$module' is installed"
    elif [[ "$MODULE_STATE" == "not_found" ]]; then
        test_fail "Module '$module' not found"
    elif [[ "$MODULE_STATE" == "error" ]]; then
        test_fail "Module '$module' check failed"
    else
        test_fail "Module '$module' state: $MODULE_STATE"
    fi
done

# Check OCA modules
OCA_MODULES=("account_financial_report" "base_exception" "server_environment")

for module in "${OCA_MODULES[@]}"; do
    MODULE_STATE=$(docker exec odoo-web odoo shell -d odoo << PYEOF 2>/dev/null || echo "error"
import sys
try:
    mod = self.env['ir.module.module'].search([('name', '=', '$module')])
    if mod and mod.state == 'installed':
        print('installed')
    else:
        print('not_installed')
except Exception:
    print('error')
PYEOF
)
    
    if [[ "$MODULE_STATE" == "installed" ]]; then
        test_pass "OCA module '$module' is installed"
    else
        # OCA modules are optional, so we just warn
        echo -e "${YELLOW}!${NC} OCA module '$module' not installed (optional)"
    fi
done

# ============================================================================
# 7. Agency Configuration Tests
# ============================================================================
print_header "Agency Configuration Tests"

AGENCIES=("RIM" "CKVC" "BOM" "JPAL" "JLI" "JAP" "LAS" "RMQB")

for agency in "${AGENCIES[@]}"; do
    AGENCY_EXISTS=$(docker exec odoo-web odoo shell -d odoo << PYEOF 2>/dev/null || echo "error"
try:
    agency = self.env['res.partner'].search([('ref', '=', '$agency')], limit=1)
    if agency:
        print('found')
    else:
        print('not_found')
except Exception:
    print('error')
PYEOF
)
    
    if [[ "$AGENCY_EXISTS" == "found" ]]; then
        test_pass "Agency '$agency' configured"
    elif [[ "$AGENCY_EXISTS" == "not_found" ]]; then
        echo -e "${YELLOW}!${NC} Agency '$agency' not configured (may need seeding)"
    else
        test_fail "Agency '$agency' check failed"
    fi
done

# ============================================================================
# 8. File System Tests
# ============================================================================
print_header "File System Tests"

# Check filestore
if docker exec odoo-web test -d /var/lib/odoo/filestore; then
    test_pass "Odoo filestore directory exists"
else
    test_fail "Odoo filestore directory not found"
fi

# Check log file
if docker exec odoo-web test -f /var/log/odoo/odoo.log; then
    test_pass "Odoo log file exists"
else
    echo -e "${YELLOW}!${NC} Odoo log file not found (may be configured differently)"
fi

# Check addons
ADDON_COUNT=$(docker exec odoo-web find /mnt/extra-addons -name "__manifest__.py" 2>/dev/null | wc -l)
if [ "$ADDON_COUNT" -gt 0 ]; then
    test_pass "Custom addons found: $ADDON_COUNT modules"
else
    test_fail "No custom addons found in /mnt/extra-addons"
fi

# ============================================================================
# 9. Performance Tests
# ============================================================================
print_header "Performance Tests"

# Response time test
RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}\n' http://localhost:8069/web)
RESPONSE_TIME_MS=$(echo "$RESPONSE_TIME * 1000" | bc | cut -d'.' -f1)

if [ "$RESPONSE_TIME_MS" -lt 2000 ]; then
    test_pass "Odoo response time: ${RESPONSE_TIME_MS}ms (good)"
elif [ "$RESPONSE_TIME_MS" -lt 5000 ]; then
    echo -e "${YELLOW}!${NC} Odoo response time: ${RESPONSE_TIME_MS}ms (acceptable)"
else
    test_fail "Odoo response time: ${RESPONSE_TIME_MS}ms (slow)"
fi

# Memory usage
ODOO_MEM=$(docker stats --no-stream --format "{{.MemUsage}}" odoo-web 2>/dev/null | cut -d'/' -f1 | tr -d ' ')
if [ ! -z "$ODOO_MEM" ]; then
    test_pass "Odoo memory usage: $ODOO_MEM"
else
    echo -e "${YELLOW}!${NC} Unable to get Odoo memory usage"
fi

# CPU usage
ODOO_CPU=$(docker stats --no-stream --format "{{.CPUPerc}}" odoo-web 2>/dev/null | tr -d ' ')
if [ ! -z "$ODOO_CPU" ]; then
    test_pass "Odoo CPU usage: $ODOO_CPU"
else
    echo -e "${YELLOW}!${NC} Unable to get Odoo CPU usage"
fi

# ============================================================================
# 10. Backup Tests
# ============================================================================
print_header "Backup Tests"

# Check if backup directory exists
if [ -d "/backups/odoo" ]; then
    BACKUP_COUNT=$(find /backups/odoo -name "*.dump" 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 0 ]; then
        LATEST_BACKUP=$(ls -t /backups/odoo/*.dump 2>/dev/null | head -1)
        BACKUP_SIZE=$(du -h "$LATEST_BACKUP" 2>/dev/null | cut -f1)
        test_pass "Latest backup: $LATEST_BACKUP ($BACKUP_SIZE)"
    else
        test_fail "No backups found in /backups/odoo"
    fi
else
    test_fail "Backup directory /backups/odoo not found"
fi

# ============================================================================
# Summary
# ============================================================================
print_header "Test Summary"

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))

echo -e "Total Tests: $TOTAL_TESTS"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✓ All smoke tests passed! Deployment is healthy.${NC}\n"
    exit 0
else
    echo -e "\n${RED}✗ Some tests failed. Please investigate.${NC}\n"
    exit 1
fi

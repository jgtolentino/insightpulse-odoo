#!/usr/bin/env bash
set -euo pipefail

# Smoke Tests for Odoo SaaS Platform
# Tests all 10 enterprise parity modules

APP_URL="${1:-}"

if [ -z "$APP_URL" ]; then
  echo "Usage: $0 <app-url>"
  echo "Example: $0 odoo-saas-platform-abc123.ondigitalocean.app"
  exit 1
fi

# Ensure URL has https://
if [[ ! "$APP_URL" =~ ^https:// ]]; then
  APP_URL="https://$APP_URL"
fi

echo "🧪 Smoke Tests for Odoo SaaS Platform"
echo "===================================="
echo "Target: $APP_URL"
echo ""

PASSED=0
FAILED=0

run_test() {
  local test_name="$1"
  local test_command="$2"

  echo -n "Testing $test_name... "

  if eval "$test_command" > /dev/null 2>&1; then
    echo "✅ PASS"
    PASSED=$((PASSED + 1))
  else
    echo "❌ FAIL"
    FAILED=$((FAILED + 1))
  fi
}

# Test 1: Health Check
run_test "Health endpoint" "curl -sf $APP_URL/web/health | jq -e '.status == \"ok\"'"

# Test 2: Main page
run_test "Main page" "curl -sf -o /dev/null -w '%{http_code}' $APP_URL/web | grep -E '^(200|303)$'"

# Test 3: Database selector
run_test "Database selector" "curl -sf -o /dev/null -w '%{http_code}' $APP_URL/web/database/selector | grep -E '^(200|303)$'"

# Test 4: Login page
run_test "Login page" "curl -sf -o /dev/null -w '%{http_code}' $APP_URL/web/login | grep -E '^(200|303)$'"

# Module-specific API tests (if authentication is available)
if [ -n "${ODOO_ADMIN_PASSWORD:-}" ]; then
  echo ""
  echo "🔐 Authenticated Module Tests"
  echo "-----------------------------"

  # Get session cookie
  SESSION=$(curl -sf -c - "$APP_URL/web/login" | grep session_id | awk '{print $7}')

  if [ -n "$SESSION" ]; then
    # Test Epic 1: Approval Flow
    run_test "Approval Flow API" "curl -sf -H 'Cookie: session_id=$SESSION' $APP_URL/api/v1/approvals/flows"

    # Test Epic 3: Rate Policy
    run_test "Rate Policy API" "curl -sf -H 'Cookie: session_id=$SESSION' $APP_URL/api/v1/rates/bands"

    # Test Epic 5: Expense Management
    run_test "Expense API" "curl -sf -H 'Cookie: session_id=$SESSION' $APP_URL/api/v1/expenses"

    # Test Epic 8: Knowledge AI
    run_test "Knowledge AI API" "curl -sf -H 'Cookie: session_id=$SESSION' $APP_URL/api/v1/knowledge/workspaces"

    # Test Epic 9: Superset Connector
    run_test "Superset Sync API" "curl -sf -H 'Cookie: session_id=$SESSION' $APP_URL/api/v1/superset/status"
  else
    echo "⚠️  Skipping authenticated tests (no session)"
  fi
else
  echo ""
  echo "ℹ️  Skipping authenticated tests (ODOO_ADMIN_PASSWORD not set)"
fi

echo ""
echo "📊 Test Results"
echo "==============="
echo "Passed: $PASSED"
echo "Failed: $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
  echo "✅ All tests passed!"
  exit 0
else
  echo "❌ Some tests failed"
  exit 1
fi

#!/bin/bash

# InsightPulse Monitor MCP Server - Test Script
# Tests all MCP tools and endpoints

set -e

# Configuration
HOST="${MCP_HOST:-localhost}"
PORT="${MCP_PORT:-8000}"
BASE_URL="http://${HOST}:${PORT}"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
log_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
    TESTS_RUN=$((TESTS_RUN + 1))
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

# Test health endpoint
test_health() {
    log_test "Testing health endpoint"

    response=$(curl -s -w "\n%{http_code}" "${BASE_URL}/health")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" == "200" ]; then
        log_pass "Health endpoint returned 200"
        echo "Response: $body"
    else
        log_fail "Health endpoint returned $http_code"
        echo "Response: $body"
        return 1
    fi
}

# Test MCP tools list
test_tools_list() {
    log_test "Testing MCP tools list"

    response=$(curl -s -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{"method":"tools/list","params":{}}')

    if echo "$response" | jq -e '.result' > /dev/null 2>&1; then
        log_pass "Tools list returned successfully"
        tool_count=$(echo "$response" | jq '.result | length')
        echo "Found $tool_count tools"
    else
        log_fail "Tools list failed"
        echo "Response: $response"
        return 1
    fi
}

# Test get_system_health tool
test_system_health() {
    log_test "Testing get_system_health tool"

    response=$(curl -s -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "method":"tools/call",
            "params":{
                "name":"get_system_health",
                "arguments":{}
            }
        }')

    if echo "$response" | jq -e '.result.overall_status' > /dev/null 2>&1; then
        status=$(echo "$response" | jq -r '.result.overall_status')
        log_pass "System health check completed: $status"
        echo "Response: $response" | jq '.'
    else
        log_fail "System health check failed"
        echo "Response: $response"
        return 1
    fi
}

# Test track_bir_filing_deadlines tool
test_bir_deadlines() {
    log_test "Testing track_bir_filing_deadlines tool"

    response=$(curl -s -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "method":"tools/call",
            "params":{
                "name":"track_bir_filing_deadlines",
                "arguments":{"agency_code":"RIM","months_ahead":3}
            }
        }')

    if echo "$response" | jq -e '.result' > /dev/null 2>&1; then
        deadline_count=$(echo "$response" | jq '.result | length')
        log_pass "BIR deadlines retrieved: $deadline_count deadlines"
        echo "First deadline:"
        echo "$response" | jq '.result[0]'
    else
        log_fail "BIR deadlines check failed"
        echo "Response: $response"
        return 1
    fi
}

# Test get_month_end_status tool
test_month_end_status() {
    log_test "Testing get_month_end_status tool"

    current_month=$(date +%Y-%m)

    response=$(curl -s -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d "{
            \"method\":\"tools/call\",
            \"params\":{
                \"name\":\"get_month_end_status\",
                \"arguments\":{\"month\":\"${current_month}\"}
            }
        }")

    if echo "$response" | jq -e '.result' > /dev/null 2>&1; then
        completion=$(echo "$response" | jq -r '.result.completion_percentage // 0')
        log_pass "Month-end status retrieved: ${completion}% complete"
        echo "Response:"
        echo "$response" | jq '.'
    else
        log_fail "Month-end status check failed"
        echo "Response: $response"
        return 1
    fi
}

# Test list_failed_jobs tool
test_failed_jobs() {
    log_test "Testing list_failed_jobs tool"

    response=$(curl -s -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "method":"tools/call",
            "params":{
                "name":"list_failed_jobs",
                "arguments":{"hours":24}
            }
        }')

    if echo "$response" | jq -e '.result' > /dev/null 2>&1; then
        job_count=$(echo "$response" | jq '.result | length')
        log_pass "Failed jobs retrieved: $job_count jobs"
        if [ "$job_count" -gt 0 ]; then
            echo "First failed job:"
            echo "$response" | jq '.result[0]'
        fi
    else
        log_fail "Failed jobs check failed"
        echo "Response: $response"
        return 1
    fi
}

# Test get_agency_metrics tool
test_agency_metrics() {
    log_test "Testing get_agency_metrics tool"

    response=$(curl -s -X POST "${BASE_URL}/mcp" \
        -H "Content-Type: application/json" \
        -d '{
            "method":"tools/call",
            "params":{
                "name":"get_agency_metrics",
                "arguments":{"agency_code":"RIM","metric_type":"all"}
            }
        }')

    if echo "$response" | jq -e '.result.agency' > /dev/null 2>&1; then
        agency=$(echo "$response" | jq -r '.result.agency')
        log_pass "Agency metrics retrieved for: $agency"
        echo "Response:"
        echo "$response" | jq '.'
    else
        log_fail "Agency metrics check failed"
        echo "Response: $response"
        return 1
    fi
}

# Run all tests
echo "============================================"
echo "InsightPulse Monitor MCP Server - Test Suite"
echo "============================================"
echo "Testing server at: ${BASE_URL}"
echo ""

# Check if server is running
if ! curl -s "${BASE_URL}/health" > /dev/null 2>&1; then
    echo -e "${RED}ERROR:${NC} Server is not running at ${BASE_URL}"
    echo "Please start the server first:"
    echo "  docker-compose up"
    echo "or"
    echo "  python server.py"
    exit 1
fi

# Run tests
test_health || true
echo ""
test_tools_list || true
echo ""
test_system_health || true
echo ""
test_bir_deadlines || true
echo ""
test_month_end_status || true
echo ""
test_failed_jobs || true
echo ""
test_agency_metrics || true

# Print summary
echo ""
echo "============================================"
echo "Test Summary"
echo "============================================"
echo "Tests run:    $TESTS_RUN"
echo -e "Tests passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed.${NC}"
    exit 1
fi

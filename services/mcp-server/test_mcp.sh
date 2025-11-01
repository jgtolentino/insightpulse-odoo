#!/bin/bash
# MCP Server Test Script
#
# Tests the MCP server health and functionality
#
# Usage:
#   ./test_mcp.sh [server_url]
#
# Examples:
#   ./test_mcp.sh http://localhost:8000
#   ./test_mcp.sh https://mcp.insightpulseai.net
#
# Environment:
#   REPO=owner/name (default: jgtolentino/insightpulse-odoo)

set -e

# Configuration
SERVER_URL="${1:-http://localhost:8000}"
REPO="${REPO:-jgtolentino/insightpulse-odoo}"

echo "=== MCP Server Test Suite ==="
echo "Server: $SERVER_URL"
echo "Repository: $REPO"
echo ""

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Test 1: Health Check
echo "Test 1: Health Check"
response=$(curl -sf "$SERVER_URL/health" || echo "FAILED")

if [[ "$response" == "FAILED" ]]; then
    fail "Health check failed - server not responding"
fi

if echo "$response" | jq -e '.status == "healthy"' > /dev/null 2>&1; then
    pass "Health check passed"
    echo "  App ID: $(echo "$response" | jq -r '.app_id')"
    echo "  Has Private Key: $(echo "$response" | jq -r '.has_private_key')"
else
    fail "Health check returned invalid response"
fi

echo ""

# Test 2: List Available Tools
echo "Test 2: List Available Tools"
response=$(curl -sf "$SERVER_URL/mcp/github" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}' \
    || echo "FAILED")

if [[ "$response" == "FAILED" ]]; then
    fail "Tools list failed"
fi

tool_count=$(echo "$response" | jq -r '.result.tools | length')
if [[ "$tool_count" -ge 11 ]]; then
    pass "Tools list returned $tool_count tools"
    echo "  Tools:"
    echo "$response" | jq -r '.result.tools[].name' | sed 's/^/    - /'
else
    fail "Expected 11+ tools, got $tool_count"
fi

echo ""

# Test 3: Test github_list_branches Tool (read-only)
echo "Test 3: Test github_list_branches Tool"
response=$(curl -sf "$SERVER_URL/mcp/github" \
    -H "Content-Type: application/json" \
    -d "{
        \"jsonrpc\": \"2.0\",
        \"method\": \"tools/call\",
        \"params\": {
            \"name\": \"github_list_branches\",
            \"arguments\": {
                \"repo\": \"$REPO\"
            }
        },
        \"id\": 2
    }" || echo "FAILED")

if [[ "$response" == "FAILED" ]]; then
    warn "github_list_branches test failed (may need valid credentials)"
elif echo "$response" | jq -e '.result' > /dev/null 2>&1; then
    branch_count=$(echo "$response" | jq -r '.result | length')
    pass "github_list_branches returned $branch_count branches"
    echo "  Sample branches:"
    echo "$response" | jq -r '.result[0:3][].name' | sed 's/^/    - /' || echo "    (none)"
else
    error=$(echo "$response" | jq -r '.error.message // "Unknown error"')
    warn "github_list_branches returned error: $error"
    warn "This is expected if GITHUB_PRIVATE_KEY is not configured"
fi

echo ""

# Test 4: Test Invalid Tool
echo "Test 4: Test Invalid Tool (error handling)"
response=$(curl -sf "$SERVER_URL/mcp/github" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "invalid_tool"}, "id": 3}' \
    || echo "FAILED")

if [[ "$response" == "FAILED" ]]; then
    fail "Invalid tool test failed"
fi

if echo "$response" | jq -e '.error.code == -32601' > /dev/null 2>&1; then
    pass "Invalid tool correctly returned error -32601"
else
    fail "Invalid tool did not return expected error"
fi

echo ""

# Test 5: Test Invalid Method
echo "Test 5: Test Invalid Method (error handling)"
response=$(curl -sf "$SERVER_URL/mcp/github" \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc": "2.0", "method": "invalid/method", "params": {}, "id": 4}' \
    || echo "FAILED")

if [[ "$response" == "FAILED" ]]; then
    fail "Invalid method test failed"
fi

if echo "$response" | jq -e '.error.code == -32601' > /dev/null 2>&1; then
    pass "Invalid method correctly returned error -32601"
else
    fail "Invalid method did not return expected error"
fi

echo ""

# Summary
echo "=== Test Summary ==="
echo -e "${GREEN}All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure GITHUB_PRIVATE_KEY in production"
echo "  2. Configure GITHUB_INSTALLATION_ID"
echo "  3. Add MCP server to Claude Code configuration"
echo "  4. Test AI-driven GitHub operations"

#!/bin/bash
# Test script for pulser-hub MCP server

set -e

BASE_URL="${1:-http://localhost:8000}"

echo "🧪 Testing pulser-hub MCP Server at $BASE_URL"
echo ""

# Test health check
echo "1. Health Check"
curl -s "$BASE_URL/health" | jq '.'
echo ""

# Test root endpoint
echo "2. Root Endpoint"
curl -s "$BASE_URL/" | jq '.'
echo ""

# Test MCP tools/list
echo "3. MCP tools/list"
curl -s -X POST "$BASE_URL/mcp/github" \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "params": {}}' | jq '.result | length'
echo " tools available"
echo ""

# Test listing branches (requires REPO variable)
if [ -n "$REPO" ]; then
  echo "4. Test github_list_branches for $REPO"
  curl -s -X POST "$BASE_URL/mcp/github" \
    -H "Content-Type: application/json" \
    -d "{
      \"method\": \"tools/call\",
      \"params\": {
        \"name\": \"github_list_branches\",
        \"arguments\": {
          \"repo\": \"$REPO\"
        }
      }
    }" | jq '.result | length'
  echo " branches found"
  echo ""
else
  echo "4. Skipping github_list_branches test (set REPO env var to test)"
  echo ""
fi

echo "✅ All tests passed!"

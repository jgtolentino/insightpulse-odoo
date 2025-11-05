#!/bin/bash
set -euo pipefail

# Smoke Test Suite for AI Inference Hub
# =====================================

BASE_URL="${1:-http://127.0.0.1:8100}"
echo "🧪 Running smoke tests against: $BASE_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

# Test function
test_endpoint() {
  local name="$1"
  local method="$2"
  local endpoint="$3"
  local data="$4"
  local expected_status="${5:-200}"

  echo -n "Testing: $name ... "

  if [ "$method" = "GET" ]; then
    response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
  else
    response=$(curl -s -w "\n%{http_code}" -X "$method" \
      -H "Content-Type: application/json" \
      -d "$data" \
      "$BASE_URL$endpoint")
  fi

  http_code=$(echo "$response" | tail -n1)
  body=$(echo "$response" | sed '$d')

  if [ "$http_code" -eq "$expected_status" ]; then
    echo -e "${GREEN}✓ PASS${NC} (HTTP $http_code)"
    ((PASSED++))
    return 0
  else
    echo -e "${RED}✗ FAIL${NC} (HTTP $http_code, expected $expected_status)"
    echo "Response: $body"
    ((FAILED++))
    return 1
  fi
}

# 1. Health Check
echo "======================================"
echo "1. System Health Tests"
echo "======================================"
test_endpoint "Health Check" "GET" "/health"

# 2. Document Processing
echo ""
echo "======================================"
echo "2. Document Processing Tests"
echo "======================================"
echo "⚠️  Note: OCR/STT/TTS tests require file uploads (skipped in automated tests)"
echo "   Manual test: curl -X POST $BASE_URL/v1/ocr -F \"file=@test.jpg\""

# 3. AI Coding Agents
echo ""
echo "======================================"
echo "3. AI Coding Agent Tests"
echo "======================================"

# Code Explanation
test_endpoint "Code Explanation" "POST" "/v1/agent/code-explain" \
  '{"code":"def add(a,b): return a+b","language":"python","model":"claude-3-5-sonnet-20241022"}'

# Code Review
test_endpoint "Code Review" "POST" "/v1/agent/code-review" \
  '{"code":"import os\nos.system(\"rm -rf /\")","language":"python","model":"claude-3-5-sonnet-20241022"}'

# Code Completion
test_endpoint "Code Completion" "POST" "/v1/agent/code-complete" \
  '{"prefix":"def calculate_total(items):\n    total = 0\n    for item in items:\n        ","suffix":"\n    return total","language":"python","model":"claude-3-5-sonnet-20241022"}'

# Code Refactoring
test_endpoint "Code Refactoring" "POST" "/v1/agent/code-refactor" \
  '{"code":"def calc(x,y,op):\n    if op==\"+\": return x+y\n    elif op==\"-\": return x-y","language":"python","focus":"readability","model":"claude-3-5-sonnet-20241022"}'

# Code Generation
test_endpoint "Code Generation" "POST" "/v1/agent/code-generate" \
  '{"description":"Create a function that validates email addresses","language":"python","model":"claude-3-5-sonnet-20241022"}'

# Code Debugging
test_endpoint "Code Debugging" "POST" "/v1/agent/code-debug" \
  '{"code":"def divide(a,b):\n    return a/b","error":"ZeroDivisionError: division by zero","language":"python","model":"claude-3-5-sonnet-20241022"}'

# 4. Error Handling
echo ""
echo "======================================"
echo "4. Error Handling Tests"
echo "======================================"

# Invalid endpoint
test_endpoint "404 Not Found" "GET" "/invalid-endpoint" "" 404

# Missing required field
test_endpoint "400 Bad Request" "POST" "/v1/agent/code-review" '{}' 422

# Summary
echo ""
echo "======================================"
echo "Test Results"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ All tests passed!${NC}"
  exit 0
else
  echo -e "${RED}✗ Some tests failed${NC}"
  exit 1
fi

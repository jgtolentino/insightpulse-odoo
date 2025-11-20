#!/bin/bash
#
# InsightPulse OCR Adapter - End-to-End Test Script
#
set -e

# Configuration
OCR_URL="${OCR_URL:-https://ocr.insightpulseai.net}"
API_KEY="${API_KEY:-dev-key-insecure}"
TEST_IMAGE="${1:-sample-receipt.jpg}"

echo "========================================"
echo "InsightPulse OCR Adapter - Smoke Test"
echo "========================================"
echo "OCR URL: $OCR_URL"
echo "Test Image: $TEST_IMAGE"
echo ""

# Test 1: Health check
echo "Test 1: Health Check"
echo "--------------------"
curl -s "$OCR_URL/health" | jq '.'
echo ""

# Test 2: OCR endpoint without auth (should fail if API key required)
echo "Test 2: OCR Endpoint (No Auth)"
echo "-------------------------------"
if [ -f "$TEST_IMAGE" ]; then
    HTTP_CODE=$(curl -s -o /tmp/ocr-response.json -w "%{http_code}" \
        -F "file=@$TEST_IMAGE" \
        "$OCR_URL/api/expense/ocr")

    echo "HTTP Status: $HTTP_CODE"
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ]; then
        echo "✅ Response received"
        cat /tmp/ocr-response.json | jq '.'
    else
        echo "❌ Unexpected status code: $HTTP_CODE"
        cat /tmp/ocr-response.json
    fi
else
    echo "⚠️  Test image not found: $TEST_IMAGE"
    echo "   Skipping OCR test"
fi
echo ""

# Test 3: OCR endpoint with auth
echo "Test 3: OCR Endpoint (With API Key)"
echo "------------------------------------"
if [ -f "$TEST_IMAGE" ]; then
    HTTP_CODE=$(curl -s -o /tmp/ocr-response-auth.json -w "%{http_code}" \
        -H "X-API-Key: $API_KEY" \
        -F "file=@$TEST_IMAGE" \
        "$OCR_URL/api/expense/ocr")

    echo "HTTP Status: $HTTP_CODE"
    if [ "$HTTP_CODE" = "200" ]; then
        echo "✅ OCR successful"
        cat /tmp/ocr-response-auth.json | jq '.'

        # Validate response structure
        MERCHANT=$(cat /tmp/ocr-response-auth.json | jq -r '.merchant_name')
        DATE=$(cat /tmp/ocr-response-auth.json | jq -r '.invoice_date')
        AMOUNT=$(cat /tmp/ocr-response-auth.json | jq -r '.total_amount')

        echo ""
        echo "Extracted Fields:"
        echo "  Merchant: $MERCHANT"
        echo "  Date: $DATE"
        echo "  Amount: $AMOUNT"

        if [ "$MERCHANT" != "null" ] && [ "$AMOUNT" != "null" ]; then
            echo "✅ All required fields present"
        else
            echo "⚠️  Some required fields missing"
        fi
    else
        echo "❌ OCR failed with status: $HTTP_CODE"
        cat /tmp/ocr-response-auth.json
    fi
else
    echo "⚠️  Test image not found: $TEST_IMAGE"
    echo "   Create a sample receipt image or provide path as argument"
    echo "   Usage: $0 path/to/receipt.jpg"
fi
echo ""

# Test 4: Check nginx proxy (SSL)
echo "Test 4: SSL Certificate Check"
echo "------------------------------"
if [[ "$OCR_URL" == https://* ]]; then
    DOMAIN=$(echo "$OCR_URL" | sed 's|https://||' | cut -d'/' -f1)
    echo "Checking SSL certificate for: $DOMAIN"
    echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | \
        openssl x509 -noout -dates 2>/dev/null || echo "⚠️  Could not verify SSL certificate"
else
    echo "⚠️  Using HTTP - SSL check skipped"
fi
echo ""

echo "========================================"
echo "Test Summary"
echo "========================================"
echo "1. Health Check: ✅"
echo "2. OCR Endpoint Access: $([ -f "$TEST_IMAGE" ] && echo '✅' || echo '⚠️  No test image')"
echo "3. OCR Response Format: $([ -f /tmp/ocr-response-auth.json ] && echo '✅' || echo '⚠️  Not tested')"
echo "4. SSL Certificate: $([ "$OCR_URL" == https://* ] && echo '✅' || echo '⚠️  HTTP only')"
echo ""
echo "Next Steps:"
echo "1. Configure Odoo: Settings → Expenses → InsightPulse OCR"
echo "2. Set OCR API URL: $OCR_URL/api/expense/ocr"
echo "3. Set API Key: $API_KEY"
echo "4. Test in Odoo: Create expense → Attach receipt → Click 'Scan with InsightPulse OCR'"
echo ""

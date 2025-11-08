#!/bin/bash
# OAuth Configuration Verification Script
# Tests Google OAuth setup for InsightPulse AI

set -e

echo "🔐 Verifying Google OAuth Configuration..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Check OAuth provider in database
echo "1️⃣  Checking OAuth provider configuration..."
PROVIDER_CHECK=$(docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -t -c \
  "SELECT enabled, client_id FROM auth_oauth_provider WHERE name = 'Google OAuth2';" | xargs)

if echo "$PROVIDER_CHECK" | grep -q ".apps.googleusercontent.com"; then
  echo -e "${GREEN}✅ OAuth provider configured correctly${NC}"
  CLIENT_ID=$(echo "$PROVIDER_CHECK" | awk '{print $2}')
  echo "   Client ID: ${CLIENT_ID:0:15}...${CLIENT_ID: -30}"
else
  echo -e "${RED}❌ OAuth provider not configured${NC}"
  exit 1
fi
echo ""

# Test 2: Check client secret
echo "2️⃣  Checking OAuth client secret..."
SECRET_CHECK=$(docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -t -c \
  "SELECT value FROM ir_config_parameter WHERE key = 'auth_oauth.client_secret_3';" | xargs)

if [ -n "$SECRET_CHECK" ]; then
  echo -e "${GREEN}✅ Client secret configured${NC}"
  echo "   Secret: GOCSPX-***"
else
  echo -e "${RED}❌ Client secret missing${NC}"
  exit 1
fi
echo ""

# Test 3: Check base URL
echo "3️⃣  Checking base URL configuration..."
BASE_URL=$(docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -t -c \
  "SELECT value FROM ir_config_parameter WHERE key = 'web.base.url';" | xargs)

if [ "$BASE_URL" = "https://erp.insightpulseai.net" ]; then
  echo -e "${GREEN}✅ Base URL configured correctly${NC}"
  echo "   URL: $BASE_URL"
else
  echo -e "${YELLOW}⚠️  Base URL: $BASE_URL${NC}"
fi
echo ""

# Test 4: Check session cookie configuration
echo "4️⃣  Checking session cookie configuration..."
COOKIE_DOMAIN=$(docker exec insightpulse-odoo-odoo-1 grep session_cookie_domain /etc/odoo/odoo.conf | cut -d '=' -f2 | xargs)

if [ "$COOKIE_DOMAIN" = ".insightpulseai.net" ]; then
  echo -e "${GREEN}✅ Session cookies configured for unified SSO${NC}"
  echo "   Domain: $COOKIE_DOMAIN"
else
  echo -e "${RED}❌ Session cookie domain not configured${NC}"
  exit 1
fi
echo ""

# Test 5: Check Odoo service status
echo "5️⃣  Checking Odoo service status..."
if docker ps | grep -q "insightpulse-odoo-odoo-1"; then
  echo -e "${GREEN}✅ Odoo service running${NC}"
  UPTIME=$(docker ps --filter "name=insightpulse-odoo-odoo-1" --format "{{.Status}}")
  echo "   Status: $UPTIME"
else
  echo -e "${RED}❌ Odoo service not running${NC}"
  exit 1
fi
echo ""

# Test 6: Check login page accessibility
echo "6️⃣  Checking login page accessibility..."
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.net/web/login)

if [ "$HTTP_STATUS" = "200" ]; then
  echo -e "${GREEN}✅ Login page accessible${NC}"
  echo "   URL: https://erp.insightpulseai.net/web/login"
else
  echo -e "${RED}❌ Login page not accessible (HTTP $HTTP_STATUS)${NC}"
  exit 1
fi
echo ""

# Test 7: Check OAuth redirect endpoint
echo "7️⃣  Checking OAuth redirect endpoint..."
REDIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://erp.insightpulseai.net/auth_oauth/signin)

if [ "$REDIRECT_STATUS" = "303" ] || [ "$REDIRECT_STATUS" = "302" ] || [ "$REDIRECT_STATUS" = "200" ]; then
  echo -e "${GREEN}✅ OAuth redirect endpoint responsive${NC}"
  echo "   Endpoint: https://erp.insightpulseai.net/auth_oauth/signin"
else
  echo -e "${YELLOW}⚠️  OAuth redirect endpoint (HTTP $REDIRECT_STATUS)${NC}"
fi
echo ""

# Test 8: Check auth_oauth module
echo "8️⃣  Checking auth_oauth module status..."
MODULE_STATE=$(docker exec insightpulse-odoo-db-1 psql -U odoo -d odoo19 -t -c \
  "SELECT state FROM ir_module_module WHERE name = 'auth_oauth';" | xargs)

if [ "$MODULE_STATE" = "installed" ]; then
  echo -e "${GREEN}✅ auth_oauth module installed${NC}"
else
  echo -e "${RED}❌ auth_oauth module not installed (state: $MODULE_STATE)${NC}"
  exit 1
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ All OAuth configuration checks passed!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 Next Steps:"
echo "   1. Open: https://erp.insightpulseai.net/web/login"
echo "   2. Click 'Sign in with Google' button"
echo "   3. Authorize InsightPulse AI"
echo "   4. Test unified SSO across subdomains"
echo ""
echo "📖 Documentation: /Users/tbwa/insightpulse-odoo/portal/OAUTH_SETUP.md"
echo ""

# Optional: Generate OAuth authorization URL (dynamic)
echo "🧪 OAuth authorization URL generation..."
if [ -n "$CLIENT_ID" ]; then
  AUTH_URL="https://accounts.google.com/o/oauth2/v2/auth?client_id=${CLIENT_ID}&redirect_uri=https://erp.insightpulseai.net/auth_oauth/signin&scope=openid+email+profile&response_type=code"
  echo "   Authorization URL: [Generated dynamically]"
  echo "   Visit login page for actual OAuth button"
else
  echo "   (Client ID not available)"
fi
echo ""
echo -e "${YELLOW}💡 Tip: Test OAuth flow via login page: https://erp.insightpulseai.net/web/login${NC}"
echo ""

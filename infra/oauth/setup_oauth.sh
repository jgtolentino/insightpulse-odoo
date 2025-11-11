#!/usr/bin/env bash
set -euo pipefail

# Google OAuth Setup for InsightPulse AI - Odoo Droplet (165.227.10.178)
# Purpose: Configure unified Google OAuth SSO across all services
# Last Updated: 2025-11-09

# Environment variables (set these before running)
POSTGRES_HOST="${POSTGRES_HOST:-db.spdtwktxdalcfigzeqrz.supabase.co}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres.spdtwktxdalcfigzeqrz}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-SHWYXDMFAwXI1drT}"
POSTGRES_DB="${POSTGRES_DB:-postgres}"

# Google OAuth Credentials (REQUIRED - set before running)
GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID:-}"
GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET:-}"

# Odoo Configuration
ODOO_ADMIN_EMAIL="${ODOO_ADMIN_EMAIL:-jgtolentino_rn@yahoo.com}"
SESSION_COOKIE_DOMAIN="${SESSION_COOKIE_DOMAIN:-.insightpulseai.net}"

echo "=== Google OAuth Setup for InsightPulse AI ==="
echo ""

# Validation
if [[ -z "$GOOGLE_CLIENT_ID" ]] || [[ -z "$GOOGLE_CLIENT_SECRET" ]]; then
  echo "❌ ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set"
  echo ""
  echo "Please create OAuth credentials in Google Cloud Console first:"
  echo "1. Go to https://console.cloud.google.com/apis/credentials"
  echo "2. Create OAuth 2.0 Client ID (Web application)"
  echo "3. Add authorized redirect URIs:"
  echo "   - https://erp.insightpulseai.net/auth_oauth/signin"
  echo "   - https://superset.insightpulseai.net/oauth-authorized/google"
  echo "   - https://mcp.insightpulseai.net/api/auth/callback/google"
  echo "   - https://n8n.insightpulseai.net/rest/oauth2-credential/callback"
  echo "   - https://chat.insightpulseai.net/oauth/google/complete"
  echo ""
  echo "Then export credentials:"
  echo "  export GOOGLE_CLIENT_ID='your-client-id'"
  echo "  export GOOGLE_CLIENT_SECRET='your-client-secret'"
  exit 1
fi

# Build PostgreSQL connection string
POSTGRES_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}?sslmode=require"

echo "✅ Configuration validated"
echo ""
echo "Postgres Host: $POSTGRES_HOST"
echo "Postgres DB: $POSTGRES_DB"
echo "Google Client ID: ${GOOGLE_CLIENT_ID:0:20}..."
echo "Session Cookie Domain: $SESSION_COOKIE_DOMAIN"
echo ""

# Step 1: Enable auth_oauth module in Odoo
echo "📦 Step 1: Enabling auth_oauth module..."
psql "$POSTGRES_URL" <<SQL
-- Enable auth_oauth module
UPDATE ir_module_module
SET state = 'to install'
WHERE name = 'auth_oauth' AND state = 'uninstalled';

-- Mark for immediate installation
UPDATE ir_module_module
SET state = 'installed'
WHERE name = 'auth_oauth' AND state = 'to install';
SQL

echo "✅ auth_oauth module enabled"
echo ""

# Step 2: Configure Google OAuth provider
echo "🔐 Step 2: Configuring Google OAuth provider..."
psql "$POSTGRES_URL" < /Users/tbwa/Documents/GitHub/insightpulse-odoo/infra/oauth/odoo_oauth_setup.sql

echo "✅ Google OAuth provider configured"
echo ""

# Step 3: Configure system parameters
echo "⚙️  Step 3: Configuring system parameters..."
psql "$POSTGRES_URL" <<SQL
-- Set base URL
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('web.base.url', 'https://erp.insightpulseai.net', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();

-- Configure OAuth authorization header
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('auth_oauth.authorization_header', 'true', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();

-- Set session cookie domain for cross-subdomain SSO
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('session_cookie_domain', '$SESSION_COOKIE_DOMAIN', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();

-- Set session cookie secure flag
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('session_cookie_secure', 'true', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();

-- Set session cookie SameSite policy
INSERT INTO ir_config_parameter (key, value, create_uid, create_date, write_uid, write_date)
VALUES ('session_cookie_samesite', 'None', 1, NOW(), 1, NOW())
ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, write_date = NOW();
SQL

echo "✅ System parameters configured"
echo ""

# Step 4: Verification
echo "🔍 Step 4: Verifying configuration..."
PROVIDER_COUNT=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM auth_oauth_provider WHERE name = 'Google';")
PARAM_COUNT=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM ir_config_parameter WHERE key IN ('web.base.url', 'session_cookie_domain', 'session_cookie_secure');")

if [[ "$PROVIDER_COUNT" -ge 1 ]] && [[ "$PARAM_COUNT" -ge 3 ]]; then
  echo "✅ OAuth configuration verified successfully"
  echo ""
  echo "Next steps:"
  echo "1. Restart Odoo service: sudo systemctl restart odoo"
  echo "2. Update Nginx configuration: sudo cp infra/oauth/nginx_oauth.conf /etc/nginx/conf.d/"
  echo "3. Reload Nginx: sudo nginx -t && sudo systemctl reload nginx"
  echo "4. Test OAuth login at: https://erp.insightpulseai.net/web/login"
  echo ""
  echo "For other services (Superset, MCP, n8n, Mattermost), see:"
  echo "  docs/OAUTH_SETUP_GUIDE.md"
else
  echo "⚠️  WARNING: Configuration verification failed"
  echo "  OAuth providers found: $PROVIDER_COUNT (expected: ≥1)"
  echo "  System parameters found: $PARAM_COUNT (expected: ≥3)"
  echo ""
  echo "Please check database connection and rerun script."
  exit 1
fi

echo ""
echo "=== OAuth Setup Complete ==="

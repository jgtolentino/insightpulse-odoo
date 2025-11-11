#!/usr/bin/env bash
set -euo pipefail

# Supabase Magic Link Setup Script
# Purpose: Configure passwordless email authentication
# Project: spdtwktxdalcfigzeqrz (InsightPulse AI)
# Last Updated: 2025-11-09

# Supabase Configuration
SUPABASE_URL="${SUPABASE_URL:-https://spdtwktxdalcfigzeqrz.supabase.co}"
SUPABASE_SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"
POSTGRES_URL="${POSTGRES_URL:-postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@db.spdtwktxdalcfigzeqrz.supabase.co:5432/postgres}"

# Email Configuration (for SMTP setup)
SMTP_HOST="${SMTP_HOST:-smtp.gmail.com}"
SMTP_PORT="${SMTP_PORT:-587}"
SMTP_USER="${SMTP_USER:-}"
SMTP_PASSWORD="${SMTP_PASSWORD:-}"
SMTP_FROM="${SMTP_FROM:-noreply@insightpulseai.net}"

echo "=== Supabase Magic Link Setup ==="
echo ""

# Validation
if [[ -z "$SUPABASE_SERVICE_ROLE_KEY" ]]; then
  echo "❌ ERROR: SUPABASE_SERVICE_ROLE_KEY must be set"
  echo ""
  echo "Export service role key:"
  echo "  export SUPABASE_SERVICE_ROLE_KEY='your-service-role-key'"
  exit 1
fi

echo "✅ Configuration validated"
echo ""
echo "Supabase URL: $SUPABASE_URL"
echo "Postgres URL: ${POSTGRES_URL%%@*}@***"
echo "SMTP Host: $SMTP_HOST"
echo "SMTP From: $SMTP_FROM"
echo ""

# Step 1: Create database schema for auth sync
echo "📦 Step 1: Creating auth sync tables..."
psql "$POSTGRES_URL" < /Users/tbwa/Documents/GitHub/insightpulse-odoo/infra/auth/supabase_magic_link_setup.sql

echo "✅ Auth sync tables created"
echo ""

# Step 2: Configure Supabase Auth via Management API
echo "🔐 Step 2: Configuring Supabase Auth settings..."

# Enable magic link via Supabase Management API
curl -X PATCH "${SUPABASE_URL}/auth/v1/admin/config" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "MAILER_AUTOCONFIRM": false,
    "MAILER_SECURE_EMAIL_CHANGE_ENABLED": true,
    "MAILER_OTP_EXP": 3600,
    "SITE_URL": "https://erp.insightpulseai.net",
    "EXTERNAL_EMAIL_ENABLED": true
  }'

echo ""
echo "✅ Auth settings configured"
echo ""

# Step 3: Configure SMTP (if credentials provided)
if [[ -n "$SMTP_USER" ]] && [[ -n "$SMTP_PASSWORD" ]]; then
  echo "📧 Step 3: Configuring SMTP settings..."

  curl -X PATCH "${SUPABASE_URL}/auth/v1/admin/config" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -d '{
      "SMTP_HOST": "'"$SMTP_HOST"'",
      "SMTP_PORT": '"$SMTP_PORT"',
      "SMTP_USER": "'"$SMTP_USER"'",
      "SMTP_PASS": "'"$SMTP_PASSWORD"'",
      "SMTP_SENDER_NAME": "InsightPulse AI",
      "SMTP_ADMIN_EMAIL": "'"$SMTP_FROM"'"
    }'

  echo ""
  echo "✅ SMTP configured"
else
  echo "⚠️  Step 3: SMTP credentials not provided, skipping SMTP setup"
  echo "   To configure SMTP later, set SMTP_USER and SMTP_PASSWORD and rerun this script"
fi
echo ""

# Step 4: Test magic link functionality
echo "🧪 Step 4: Testing magic link setup..."

TEST_EMAIL="${TEST_EMAIL:-jgtolentino_rn@yahoo.com}"

echo "Sending test magic link to: $TEST_EMAIL"
curl -X POST "${SUPABASE_URL}/auth/v1/magiclink" \
  -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "'"$TEST_EMAIL"'"
  }'

echo ""
echo "✅ Test magic link sent (check inbox)"
echo ""

# Step 5: Verification
echo "🔍 Step 5: Verifying configuration..."

# Check auth sync table exists
TABLE_COUNT=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM pg_tables WHERE tablename = 'auth_sync';")

if [[ "$TABLE_COUNT" -ge 1 ]]; then
  echo "✅ auth_sync table exists"
else
  echo "⚠️  WARNING: auth_sync table not found"
  exit 1
fi

# Check RLS policies exist
POLICY_COUNT=$(psql "$POSTGRES_URL" -t -c "SELECT COUNT(*) FROM pg_policies WHERE tablename = 'auth_sync';")

if [[ "$POLICY_COUNT" -ge 2 ]]; then
  echo "✅ RLS policies configured (count: $POLICY_COUNT)"
else
  echo "⚠️  WARNING: Expected ≥2 RLS policies, found: $POLICY_COUNT"
fi

echo ""
echo "=== Magic Link Setup Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure email templates in Supabase Dashboard:"
echo "   https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/auth/templates"
echo ""
echo "2. Test magic link login:"
echo "   - Go to: https://erp.insightpulseai.net/web/login"
echo "   - Click 'Sign in with email' (implement this UI)"
echo "   - Enter email and click 'Send magic link'"
echo "   - Check inbox for magic link"
echo ""
echo "3. Integrate with Odoo login page:"
echo "   - Add magic link input field to /web/login template"
echo "   - Call Supabase Auth API: POST /auth/v1/magiclink"
echo "   - On confirmation, sync with Odoo via auth_sync table"
echo ""
echo "For troubleshooting, see: docs/OAUTH_SETUP_GUIDE.md"

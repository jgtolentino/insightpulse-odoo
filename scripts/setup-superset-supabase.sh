#!/bin/bash
# Setup Superset with Supabase database connection

set -e

echo "🔧 Setting up Superset database connection to Supabase..."

# Supabase credentials from environment
SUPABASE_PROJECT_REF="${SUPABASE_PROJECT_REF:-xkxyvboeubffxxbebsll}"
SUPABASE_URL="${SUPABASE_URL:-https://xkxyvboeubffxxbebsll.supabase.co}"
SUPABASE_PASSWORD="${SUPABASE_DB_PASSWORD:-SHWYXDMFAwXI1drT}"

echo "📋 Supabase Connection Details:"
echo "   Project: $SUPABASE_PROJECT_REF"
echo "   URL: $SUPABASE_URL"

# Get the correct connection details from Supabase
echo ""
echo "🔍 To get the correct database password:"
echo "   1. Go to: https://supabase.com/dashboard/project/$SUPABASE_PROJECT_REF/settings/database"
echo "   2. Copy the 'Database Password' (not the Connection Pooler password)"
echo "   3. Note the 'Host' and 'Port' for direct connection"
echo ""

# Generate connection strings for different scenarios
echo "📝 Connection String Options:"
echo ""
echo "1️⃣  Direct Connection (Transaction Mode):"
echo "   postgresql://postgres.${SUPABASE_PROJECT_REF}:[YOUR-PASSWORD]@db.${SUPABASE_PROJECT_REF}.supabase.co:5432/postgres"
echo ""
echo "2️⃣  Connection Pooler (Session Mode):"
echo "   postgresql://postgres.${SUPABASE_PROJECT_REF}:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres?pgbouncer=true"
echo ""

# For Superset specifically
echo "🎯 For Superset Database Connection:"
echo ""
echo "Host: db.${SUPABASE_PROJECT_REF}.supabase.co"
echo "Port: 5432 (direct) or 6543 (pooler)"
echo "Database: postgres"
echo "Username: postgres"
echo "Password: [YOUR-DATABASE-PASSWORD]"
echo ""

# Test connection
echo "🧪 Testing connection..."
echo "Please enter your Supabase database password:"
read -s DB_PASSWORD

TEST_URL="postgresql://postgres:${DB_PASSWORD}@db.${SUPABASE_PROJECT_REF}.supabase.co:5432/postgres"

if psql "$TEST_URL" -c "SELECT version();" >/dev/null 2>&1; then
    echo "✅ Connection successful!"
    echo ""
    echo "📝 Update your Superset app spec with:"
    echo ""
    echo "DATABASE_HOST=db.${SUPABASE_PROJECT_REF}.supabase.co"
    echo "DATABASE_PORT=5432"
    echo "DATABASE_DB=postgres"
    echo "DATABASE_USER=postgres"
    echo "DATABASE_PASSWORD=$DB_PASSWORD"
else
    echo "❌ Connection failed"
    echo ""
    echo "⚠️  Please check:"
    echo "   1. Password is correct (from Supabase Settings → Database)"
    echo "   2. IP allowlist includes your location (or set to 0.0.0.0/0)"
    echo "   3. Database is active and not paused"
fi

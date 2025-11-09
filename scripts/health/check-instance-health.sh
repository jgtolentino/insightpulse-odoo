#!/usr/bin/env bash
set -euo pipefail

# Instance Health Check Script
# Purpose: Verify Odoo, Supabase, and Superset instance health per environment
# Usage: ./check-instance-health.sh [local|staging|production]
# Last Updated: 2025-11-09

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "${ROOT_DIR}"

ENVIRONMENT="${1:-local}"
CONFIG_FILE="config/instance-matrix.yaml"

echo "========================================="
echo "Instance Health Check"
echo "Environment: ${ENVIRONMENT}"
echo "========================================="
echo ""

# Validate config file exists
if [[ ! -f "${CONFIG_FILE}" ]]; then
  echo "❌ ERROR: Missing ${CONFIG_FILE}"
  exit 1
fi

# Simple YAML parsing (avoids external dependencies)
# For production use, consider installing yq
get_yaml_value() {
  local key="$1"
  local env="$2"
  grep -A20 "  ${env}:" "${CONFIG_FILE}" \
    | grep "${key}:" \
    | head -n1 \
    | sed -E 's/.*'"${key}"': "([^"]*)".*/\1/'
}

# Extract configuration for environment
echo "📋 Loading configuration from ${CONFIG_FILE}..."

# Odoo configuration
ODOO_URL=$(get_yaml_value "url" "${ENVIRONMENT}" | grep -A5 "odoo:" | grep "url:" | sed -E 's/.*url: "([^"]*)".*/\1/')
ODOO_DB_ENV=$(get_yaml_value "db_url_env" "${ENVIRONMENT}" | grep -A5 "odoo:" | grep "db_url_env:" | sed -E 's/.*db_url_env: "([^"]*)".*/\1/')

# Supabase configuration
SUPABASE_DB_ENV=$(get_yaml_value "db_url_env" "${ENVIRONMENT}" | grep -A5 "supabase:" | grep "db_url_env:" | sed -E 's/.*db_url_env: "([^"]*)".*/\1/')

# Superset configuration
SUPERSET_URL=$(get_yaml_value "url" "${ENVIRONMENT}" | grep -A5 "superset:" | grep "url:" | sed -E 's/.*url: "([^"]*)".*/\1/')
SUPERSET_META_DB_ENV=$(get_yaml_value "metadata_db_url_env" "${ENVIRONMENT}" | grep -A5 "superset:" | grep "metadata_db_url_env:" | sed -E 's/.*metadata_db_url_env: "([^"]*)".*/\1/')

echo "✅ Configuration loaded"
echo ""

# Get actual environment variable values
eval "ODOO_DB_URL=\${${ODOO_DB_ENV}:-}"
eval "SUPABASE_DB_URL=\${${SUPABASE_DB_ENV}:-}"
eval "SUPERSET_META_DB_URL=\${${SUPERSET_META_DB_ENV}:-}"

# Display configuration (without secrets)
echo "📊 Instance Configuration:"
echo "  Odoo URL: ${ODOO_URL}"
echo "  Odoo DB Env Var: ${ODOO_DB_ENV}"
echo "  Odoo DB URL: ${ODOO_DB_URL:+[SET]}${ODOO_DB_URL:-[NOT SET]}"
echo ""
echo "  Supabase DB Env Var: ${SUPABASE_DB_ENV}"
echo "  Supabase DB URL: ${SUPABASE_DB_URL:+[SET]}${SUPABASE_DB_URL:-[NOT SET]}"
echo ""
echo "  Superset URL: ${SUPERSET_URL}"
echo "  Superset Meta DB Env Var: ${SUPERSET_META_DB_ENV}"
echo "  Superset Meta DB URL: ${SUPERSET_META_DB_URL:+[SET]}${SUPERSET_META_DB_URL:-[NOT SET]}"
echo ""

# Health check functions
check_odoo_http() {
  echo "========================================="
  echo "1️⃣  Checking Odoo HTTP Health"
  echo "========================================="

  if ! command -v curl >/dev/null 2>&1; then
    echo "⚠️  curl not installed, skipping HTTP check"
    return 0
  fi

  echo "🔍 Testing: ${ODOO_URL}/web/login"

  if curl -fsS --max-time 30 "${ODOO_URL}/web/login" >/dev/null 2>&1; then
    echo "✅ Odoo HTTP: HEALTHY"
    return 0
  else
    echo "❌ Odoo HTTP: FAILED"
    echo "   URL: ${ODOO_URL}/web/login"
    echo "   This could mean:"
    echo "   - Odoo service is down"
    echo "   - Network connectivity issue"
    echo "   - SSL certificate problem"
    return 1
  fi
}

check_supabase_db() {
  echo ""
  echo "========================================="
  echo "2️⃣  Checking Supabase Database Health"
  echo "========================================="

  if [[ -z "${SUPABASE_DB_URL}" ]]; then
    echo "⚠️  ${SUPABASE_DB_ENV} not set, skipping DB check"
    return 0
  fi

  if ! command -v psql >/dev/null 2>&1; then
    echo "⚠️  psql not installed, skipping DB check"
    return 0
  fi

  echo "🔍 Testing: Supabase PostgreSQL connection"
  echo "   Connection: ${SUPABASE_DB_URL%%@*}@***"

  if psql "${SUPABASE_DB_URL}" -c "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ Supabase Database: HEALTHY"

    # Additional checks
    echo ""
    echo "📊 Supabase Database Stats:"

    # Count tables
    TABLE_COUNT=$(psql "${SUPABASE_DB_URL}" -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema');" 2>/dev/null | tr -d ' ')
    echo "   Tables: ${TABLE_COUNT}"

    # Count active connections
    CONN_COUNT=$(psql "${SUPABASE_DB_URL}" -t -c "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = current_database();" 2>/dev/null | tr -d ' ')
    echo "   Active Connections: ${CONN_COUNT}"

    # Check auth_sync table (magic link integration)
    if psql "${SUPABASE_DB_URL}" -t -c "SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'auth_sync');" 2>/dev/null | grep -q "t"; then
      AUTH_SYNC_COUNT=$(psql "${SUPABASE_DB_URL}" -t -c "SELECT COUNT(*) FROM auth_sync;" 2>/dev/null | tr -d ' ')
      echo "   Auth Sync Records: ${AUTH_SYNC_COUNT}"
    fi

    return 0
  else
    echo "❌ Supabase Database: FAILED"
    echo "   This could mean:"
    echo "   - Database server is down"
    echo "   - Incorrect credentials in ${SUPABASE_DB_ENV}"
    echo "   - Network connectivity issue"
    echo "   - Connection limit reached"
    return 1
  fi
}

check_superset_http() {
  echo ""
  echo "========================================="
  echo "3️⃣  Checking Superset HTTP Health"
  echo "========================================="

  if ! command -v curl >/dev/null 2>&1; then
    echo "⚠️  curl not installed, skipping HTTP check"
    return 0
  fi

  echo "🔍 Testing: ${SUPERSET_URL}/health"

  # Try /health endpoint first
  if curl -fsS --max-time 30 "${SUPERSET_URL}/health" >/dev/null 2>&1; then
    echo "✅ Superset HTTP: HEALTHY"
    return 0
  fi

  # Fallback to /login/ endpoint
  echo "   /health endpoint failed, trying /login/"
  if curl -fsS --max-time 30 "${SUPERSET_URL}/login/" >/dev/null 2>&1; then
    echo "✅ Superset HTTP: HEALTHY (via /login/)"
    return 0
  fi

  echo "❌ Superset HTTP: FAILED"
  echo "   URL: ${SUPERSET_URL}"
  echo "   This could mean:"
  echo "   - Superset service is down"
  echo "   - Network connectivity issue"
  echo "   - SSL certificate problem"
  return 1
}

check_superset_metadata_db() {
  echo ""
  echo "========================================="
  echo "4️⃣  Checking Superset Metadata Database"
  echo "========================================="

  if [[ -z "${SUPERSET_META_DB_URL}" ]]; then
    echo "⚠️  ${SUPERSET_META_DB_ENV} not set, skipping metadata DB check"
    return 0
  fi

  if ! command -v psql >/dev/null 2>&1; then
    echo "⚠️  psql not installed, skipping metadata DB check"
    return 0
  fi

  echo "🔍 Testing: Superset Metadata PostgreSQL connection"
  echo "   Connection: ${SUPERSET_META_DB_URL%%@*}@***"

  if psql "${SUPERSET_META_DB_URL}" -c "SELECT 1;" >/dev/null 2>&1; then
    echo "✅ Superset Metadata Database: HEALTHY"

    # Additional checks
    echo ""
    echo "📊 Superset Metadata Stats:"

    # Count dashboards
    if psql "${SUPERSET_META_DB_URL}" -t -c "SELECT EXISTS (SELECT FROM pg_tables WHERE tablename = 'dashboards');" 2>/dev/null | grep -q "t"; then
      DASHBOARD_COUNT=$(psql "${SUPERSET_META_DB_URL}" -t -c "SELECT COUNT(*) FROM dashboards;" 2>/dev/null | tr -d ' ')
      echo "   Dashboards: ${DASHBOARD_COUNT}"

      # Count charts
      CHART_COUNT=$(psql "${SUPERSET_META_DB_URL}" -t -c "SELECT COUNT(*) FROM slices;" 2>/dev/null | tr -d ' ')
      echo "   Charts: ${CHART_COUNT}"

      # Count datasets
      DATASET_COUNT=$(psql "${SUPERSET_META_DB_URL}" -t -c "SELECT COUNT(*) FROM tables;" 2>/dev/null | tr -d ' ')
      echo "   Datasets: ${DATASET_COUNT}"
    fi

    return 0
  else
    echo "❌ Superset Metadata Database: FAILED"
    echo "   This could mean:"
    echo "   - Metadata database server is down"
    echo "   - Incorrect credentials in ${SUPERSET_META_DB_ENV}"
    echo "   - Network connectivity issue"
    return 1
  fi
}

# Run all health checks
FAILED_CHECKS=0

check_odoo_http || FAILED_CHECKS=$((FAILED_CHECKS + 1))
check_supabase_db || FAILED_CHECKS=$((FAILED_CHECKS + 1))
check_superset_http || FAILED_CHECKS=$((FAILED_CHECKS + 1))
check_superset_metadata_db || FAILED_CHECKS=$((FAILED_CHECKS + 1))

# Summary
echo ""
echo "========================================="
echo "Summary"
echo "========================================="

if [[ $FAILED_CHECKS -eq 0 ]]; then
  echo "✅ All instance health checks PASSED"
  echo "   Environment: ${ENVIRONMENT}"
  echo "   Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
  exit 0
else
  echo "❌ ${FAILED_CHECKS} health check(s) FAILED"
  echo "   Environment: ${ENVIRONMENT}"
  echo "   Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
  echo ""
  echo "Troubleshooting steps:"
  echo "1. Verify environment variables are set:"
  echo "   echo \$${ODOO_DB_ENV}"
  echo "   echo \$${SUPABASE_DB_ENV}"
  echo "   echo \$${SUPERSET_META_DB_ENV}"
  echo ""
  echo "2. Check service status:"
  if [[ "${ENVIRONMENT}" == "local" ]]; then
    echo "   docker-compose ps"
  else
    echo "   ssh root@<server-ip> systemctl status odoo"
  fi
  echo ""
  echo "3. Review logs:"
  echo "   make logs"
  echo ""
  echo "4. See docs/INSTANCE_MAP_SUPABASE_SUPERSET_ODOO.md for details"
  exit 1
fi

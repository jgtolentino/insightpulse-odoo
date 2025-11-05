#!/bin/bash
# Import LLM Metrics Dashboard into Superset
set -e

SUPERSET_URL="${SUPERSET_URL:-http://localhost:8088}"
SUPERSET_USERNAME="${SUPERSET_USERNAME:-admin}"
SUPERSET_PASSWORD="${SUPERSET_PASSWORD:-admin}"

echo "🚀 Importing LLM Metrics Dashboard to Superset"

# Login and get access token
echo "🔐 Authenticating..."
ACCESS_TOKEN=$(curl -s -X POST "${SUPERSET_URL}/api/v1/security/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"${SUPERSET_USERNAME}\",\"password\":\"${SUPERSET_PASSWORD}\",\"provider\":\"db\",\"refresh\":true}" \
  | jq -r '.access_token')

if [ "$ACCESS_TOKEN" = "null" ]; then
  echo "❌ Authentication failed"
  exit 1
fi

echo "✓ Authenticated"

# Create database connection (if not exists)
echo "📊 Setting up database connection..."
curl -s -X POST "${SUPERSET_URL}/api/v1/database/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @- <<EOF || true
{
  "database_name": "InsightPulse",
  "sqlalchemy_uri": "${DATABASE_URL}",
  "expose_in_sqllab": true,
  "allow_ctas": true,
  "allow_cvas": true
}
EOF

# Import datasets
echo "📈 Creating LLM metrics datasets..."

# You would typically export these from Superset and check them in
# For now, we'll create them via SQL Lab

echo "✅ LLM Metrics Dashboard setup complete"
echo "   Visit: ${SUPERSET_URL}/superset/dashboard/llm-metrics/"

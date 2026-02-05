#!/bin/bash
# ETL Health Check Script
# Purpose: Validate all ETL components (Airbyte, dbt, Supabase sync, outbox queue)
# Exit code: 0 = healthy, non-zero = issues detected

set -o pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Initialize counters
CHECKS_PASSED=0
CHECKS_FAILED=0
CHECKS_WARNING=0

# Helper functions
check_passed() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

check_failed() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

check_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((CHECKS_WARNING++))
}

echo "=========================================="
echo "ETL Health Check - InsightPulse Odoo"
echo "=========================================="
echo "Date: $(date)"
echo ""

# ==========================================
# 1. Check Airbyte Configuration
# ==========================================
echo "1. Airbyte Configuration Checks"
echo "------------------------------------------"

if [ -f "$REPO_ROOT/airbyte/odoo-to-supabase.yml" ]; then
    check_passed "Airbyte config file exists"
    
    # Parse YAML and check for required fields (basic validation)
    if grep -q "odoo_source:" "$REPO_ROOT/airbyte/odoo-to-supabase.yml"; then
        check_passed "Odoo source configured"
    else
        check_failed "Odoo source not configured"
    fi
    
    if grep -q "supabase_destination:" "$REPO_ROOT/airbyte/odoo-to-supabase.yml"; then
        check_passed "Supabase destination configured"
    else
        check_failed "Supabase destination not configured"
    fi
    
    # Count configured streams
    STREAM_COUNT=$(grep -c "name:" "$REPO_ROOT/airbyte/odoo-to-supabase.yml" || echo 0)
    if [ "$STREAM_COUNT" -gt 0 ]; then
        check_passed "$STREAM_COUNT data streams configured"
    else
        check_failed "No data streams configured"
    fi
else
    check_failed "Airbyte config file missing"
fi

# Check if Airbyte is running (optional - only if docker available)
if command -v docker &> /dev/null; then
    if docker ps | grep -q airbyte; then
        check_passed "Airbyte containers running"
    else
        check_warning "Airbyte containers not detected (may not be deployed locally)"
    fi
fi

echo ""

# ==========================================
# 2. Check dbt Project
# ==========================================
echo "2. dbt Project Checks"
echo "------------------------------------------"

if [ -f "$REPO_ROOT/dbt/project.yml" ]; then
    check_passed "dbt project file exists"
    
    # Check for dbt models
    if [ -d "$REPO_ROOT/dbt/models" ]; then
        MODEL_COUNT=$(find "$REPO_ROOT/dbt/models" -name "*.sql" | wc -l)
        if [ "$MODEL_COUNT" -gt 0 ]; then
            check_passed "$MODEL_COUNT dbt models found"
        else
            check_warning "No dbt models implemented yet"
        fi
    else
        check_warning "dbt models directory missing"
    fi
    
    # Check for profiles.yml (local or example)
    if [ -f "$REPO_ROOT/dbt/profiles.yml" ] || [ -f "$HOME/.dbt/profiles.yml" ]; then
        check_passed "dbt profiles configured"
    else
        check_warning "dbt profiles not configured (check ~/.dbt/profiles.yml)"
    fi
else
    check_failed "dbt project file missing"
fi

echo ""

# ==========================================
# 3. Check Supabase Sync Infrastructure
# ==========================================
echo "3. Supabase Sync Checks"
echo "------------------------------------------"

if [ -f "$REPO_ROOT/supabase/migrations/20260205152220_odoo_sync.sql" ]; then
    check_passed "Supabase sync migration exists"
else
    check_failed "Supabase sync migration missing"
fi

if [ -f "$REPO_ROOT/supabase/migrations/010_knowledge_pipeline.sql" ]; then
    check_passed "Knowledge pipeline migration exists"
else
    check_warning "Knowledge pipeline migration missing"
fi

# Check Supabase connectivity (if credentials available)
if [ -n "$SUPABASE_PROJECT_URL" ] && [ -n "$SUPABASE_ANON_KEY" ]; then
    if curl -s -o /dev/null -w "%{http_code}" \
        -H "apikey: $SUPABASE_ANON_KEY" \
        "$SUPABASE_PROJECT_URL/rest/v1/" | grep -q "200"; then
        check_passed "Supabase API accessible"
    else
        check_failed "Supabase API not accessible"
    fi
else
    check_warning "Supabase credentials not set (SUPABASE_PROJECT_URL, SUPABASE_ANON_KEY)"
fi

# Check if PostgreSQL client is available for database checks
if command -v psql &> /dev/null; then
    if [ -n "$SUPABASE_DB_URL" ]; then
        # Try to check outbox queue depth
        if QUEUE_DEPTH=$(psql "$SUPABASE_DB_URL" -t -c "SELECT COUNT(*) FROM ops.odoo_outbox WHERE status = 'queued';" 2>/dev/null); then
            QUEUE_DEPTH=$(echo "$QUEUE_DEPTH" | xargs) # trim whitespace
            check_passed "Outbox queue accessible (depth: $QUEUE_DEPTH)"
            
            if [ "$QUEUE_DEPTH" -gt 1000 ]; then
                check_warning "High outbox queue depth ($QUEUE_DEPTH records) - worker may be stalled"
            fi
        else
            check_warning "Cannot query outbox queue (check SUPABASE_DB_URL or table existence)"
        fi
    else
        check_warning "SUPABASE_DB_URL not set - cannot check database"
    fi
else
    check_warning "psql not installed - skipping database checks"
fi

echo ""

# ==========================================
# 4. Check Data Warehouse
# ==========================================
echo "4. Data Warehouse Checks"
echo "------------------------------------------"

if [ -d "$REPO_ROOT/warehouse" ]; then
    check_passed "Warehouse directory exists"
    
    if [ -f "$REPO_ROOT/warehouse/views.sql" ]; then
        check_passed "Warehouse views defined"
    else
        check_warning "Warehouse views.sql missing"
    fi
    
    if [ -f "$REPO_ROOT/warehouse/rollback.sql" ]; then
        check_passed "Rollback procedures documented"
    else
        check_warning "Rollback procedures missing"
    fi
else
    check_failed "Warehouse directory missing"
fi

echo ""

# ==========================================
# 5. Check Docker Compose Configurations
# ==========================================
echo "5. Docker Compose Checks"
echo "------------------------------------------"

if [ -f "$REPO_ROOT/docker-compose.yml" ]; then
    check_passed "Main docker-compose.yml exists"
    
    # Check for ETL-related services
    if grep -q "airbyte" "$REPO_ROOT/docker-compose.yml"; then
        check_passed "Airbyte service defined in docker-compose"
    else
        check_warning "Airbyte not in docker-compose (may be separate deployment)"
    fi
    
    if grep -q "postgres" "$REPO_ROOT/docker-compose.yml"; then
        check_passed "PostgreSQL service defined"
    else
        check_warning "PostgreSQL not in docker-compose"
    fi
else
    check_failed "docker-compose.yml missing"
fi

echo ""

# ==========================================
# 6. Check Environment Variables
# ==========================================
echo "6. Environment Variables Checks"
echo "------------------------------------------"

# Check for .env.example
if [ -f "$REPO_ROOT/.env.example" ]; then
    check_passed ".env.example exists"
else
    check_warning ".env.example missing"
fi

# Check critical environment variables
ENV_VARS=(
    "ODOO_DB_HOST"
    "ODOO_DB_NAME"
    "ODOO_DB_USER"
    "SUPABASE_PROJECT_URL"
    "SUPABASE_DB_HOST"
)

MISSING_VARS=()
for var in "${ENV_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -eq 0 ]; then
    check_passed "All critical environment variables set"
else
    check_warning "Missing environment variables: ${MISSING_VARS[*]}"
fi

echo ""

# ==========================================
# 7. Check ETL Scripts
# ==========================================
echo "7. ETL Scripts Checks"
echo "------------------------------------------"

EXPECTED_SCRIPTS=(
    "outbox-worker.py"
    "validate-airbyte-sync.sh"
    "ingest-knowledge.py"
)

for script in "${EXPECTED_SCRIPTS[@]}"; do
    if [ -f "$REPO_ROOT/scripts/$script" ]; then
        check_passed "Script exists: $script"
    else
        check_warning "Script missing: $script (planned for future implementation)"
    fi
done

echo ""

# ==========================================
# Summary
# ==========================================
echo "=========================================="
echo "Health Check Summary"
echo "=========================================="
echo -e "${GREEN}Passed:${NC}  $CHECKS_PASSED"
echo -e "${YELLOW}Warnings:${NC} $CHECKS_WARNING"
echo -e "${RED}Failed:${NC}  $CHECKS_FAILED"
echo ""

if [ "$CHECKS_FAILED" -gt 0 ]; then
    echo -e "${RED}❌ ETL Health Check FAILED${NC}"
    echo "Review the failed checks above and consult ETL_BLOCKERS_REPORT.md"
    exit 1
elif [ "$CHECKS_WARNING" -gt 5 ]; then
    echo -e "${YELLOW}⚠️  ETL Health Check PASSED WITH WARNINGS${NC}"
    echo "Some components are not configured yet - see ETL_BLOCKERS_REPORT.md"
    exit 0
else
    echo -e "${GREEN}✅ ETL Health Check PASSED${NC}"
    echo "All critical components are properly configured"
    exit 0
fi

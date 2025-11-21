#!/bin/bash
###############################################################################
# apply-supabase-schema.sh - Apply Supabase health check schema
#
# Usage:
#   ./scripts/apply-supabase-schema.sh [--project-ref PROJECT_REF]
#
# Requirements:
#   - SUPABASE_SERVICE_ROLE_KEY environment variable
#   - SUPABASE_PROJECT_REF environment variable (or --project-ref flag)
#   - psql command available
#
# What this script does:
#   1. Validates Supabase connection
#   2. Applies health_check table schema
#   3. Creates helper views and functions
#   4. Validates schema application
###############################################################################

set -euo pipefail

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_REF="${SUPABASE_PROJECT_REF:-}"
SERVICE_ROLE_KEY="${SUPABASE_SERVICE_ROLE_KEY:-}"
SQL_FILE="packages/db/sql/02_health_check_table.sql"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --project-ref)
            PROJECT_REF="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Function to print colored messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."

    # Check if PROJECT_REF is set
    if [ -z "$PROJECT_REF" ]; then
        log_error "SUPABASE_PROJECT_REF is not set"
        log_error "Please set the environment variable or use --project-ref flag"
        exit 1
    fi

    # Check if SERVICE_ROLE_KEY is set
    if [ -z "$SERVICE_ROLE_KEY" ]; then
        log_error "SUPABASE_SERVICE_ROLE_KEY is not set"
        log_error "Please set the environment variable"
        exit 1
    fi

    # Check if SQL file exists
    if [ ! -f "$SQL_FILE" ]; then
        log_error "SQL file not found: $SQL_FILE"
        exit 1
    fi

    # Check if psql is available
    if ! command -v psql &> /dev/null; then
        log_error "psql command not found"
        log_error "Please install PostgreSQL client tools"
        exit 1
    fi

    log_success "Prerequisites validated"
}

# Function to construct Postgres URL
get_postgres_url() {
    echo "postgres://postgres.${PROJECT_REF}:${SERVICE_ROLE_KEY}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
}

# Function to test Supabase connection
test_connection() {
    log_info "Testing Supabase connection..."

    local POSTGRES_URL=$(get_postgres_url)

    if psql "$POSTGRES_URL" -c "SELECT 1;" &>/dev/null; then
        log_success "Supabase connection successful"
        return 0
    else
        log_error "Cannot connect to Supabase"
        log_error "Please verify:"
        log_error "  1. PROJECT_REF is correct: $PROJECT_REF"
        log_error "  2. SERVICE_ROLE_KEY is valid"
        log_error "  3. Network connectivity to Supabase"
        exit 1
    fi
}

# Function to apply schema
apply_schema() {
    log_info "Applying health check schema..."

    local POSTGRES_URL=$(get_postgres_url)

    if psql "$POSTGRES_URL" -f "$SQL_FILE" > /tmp/supabase_schema_apply.log 2>&1; then
        log_success "Schema applied successfully"

        # Display relevant output
        if grep -q "CREATE TABLE\|CREATE VIEW\|CREATE FUNCTION" /tmp/supabase_schema_apply.log; then
            log_info "Changes applied:"
            grep "CREATE TABLE\|CREATE VIEW\|CREATE FUNCTION\|CREATE POLICY\|CREATE INDEX" /tmp/supabase_schema_apply.log | sed 's/^/  /'
        fi

        return 0
    else
        log_error "Failed to apply schema"
        log_error "Error log:"
        cat /tmp/supabase_schema_apply.log | sed 's/^/  /'
        exit 1
    fi
}

# Function to validate schema
validate_schema() {
    log_info "Validating schema..."

    local POSTGRES_URL=$(get_postgres_url)
    local validation_failed=0

    # Check if health_check table exists
    log_info "  → Checking health_check table"
    if psql "$POSTGRES_URL" -t -c "SELECT EXISTS (SELECT FROM pg_tables WHERE schemaname = 'public' AND tablename = 'health_check');" | grep -q "t"; then
        log_success "    health_check table exists"
    else
        log_error "    health_check table not found"
        validation_failed=1
    fi

    # Check if views exist
    log_info "  → Checking helper views"
    local views=("health_check_latest" "health_check_summary" "health_check_recent_failures")
    for view in "${views[@]}"; do
        if psql "$POSTGRES_URL" -t -c "SELECT EXISTS (SELECT FROM pg_views WHERE schemaname = 'public' AND viewname = '$view');" | grep -q "t"; then
            log_success "    $view view exists"
        else
            log_error "    $view view not found"
            validation_failed=1
        fi
    done

    # Check if functions exist
    log_info "  → Checking helper functions"
    local functions=("get_environment_health" "mark_health_check_fixed" "clean_old_health_checks")
    for func in "${functions[@]}"; do
        if psql "$POSTGRES_URL" -t -c "SELECT EXISTS (SELECT FROM pg_proc WHERE proname = '$func');" | grep -q "t"; then
            log_success "    $func function exists"
        else
            log_error "    $func function not found"
            validation_failed=1
        fi
    done

    # Check RLS is enabled
    log_info "  → Checking Row Level Security"
    if psql "$POSTGRES_URL" -t -c "SELECT relrowsecurity FROM pg_class WHERE relname = 'health_check';" | grep -q "t"; then
        log_success "    RLS is enabled on health_check table"
    else
        log_error "    RLS is not enabled on health_check table"
        validation_failed=1
    fi

    if [ $validation_failed -eq 0 ]; then
        log_success "Schema validation passed"
    else
        log_error "Schema validation failed"
        exit 1
    fi
}

# Function to insert test record
insert_test_record() {
    log_info "Inserting test health check record..."

    local POSTGRES_URL=$(get_postgres_url)

    local test_sql="
        INSERT INTO public.health_check (environment, gate_name, status, duration_ms, details)
        VALUES ('dev', 'schema_validation', 'PASS', 100, '{\"message\": \"Schema application test\"}'::jsonb)
        RETURNING id, check_time;
    "

    if psql "$POSTGRES_URL" -t -c "$test_sql" > /tmp/test_record.log 2>&1; then
        local record_id=$(cat /tmp/test_record.log | awk '{print $1}' | tr -d ' ')
        log_success "Test record inserted: $record_id"

        # Query the record back
        local query_sql="SELECT * FROM public.health_check WHERE id = '$record_id'::uuid;"
        log_info "Querying test record..."
        psql "$POSTGRES_URL" -c "$query_sql"

        return 0
    else
        log_error "Failed to insert test record"
        cat /tmp/test_record.log | sed 's/^/  /'
        exit 1
    fi
}

# Function to display next steps
display_next_steps() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log_success "Supabase schema applied successfully!"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📋 Next Steps:"
    echo ""
    echo "1. View health check data in Supabase:"
    echo "   ${BLUE}https://supabase.com/dashboard/project/$PROJECT_REF/editor/29274?sort=created_at%3Adesc${NC}"
    echo ""
    echo "2. Test helper functions:"
    echo "   ${BLUE}SELECT * FROM public.get_environment_health('prod');${NC}"
    echo "   ${BLUE}SELECT * FROM public.health_check_summary;${NC}"
    echo ""
    echo "3. Continue with server deployment:"
    echo "   ${BLUE}./scripts/deploy-to-server.sh${NC}"
    echo ""
    echo "📚 Documentation:"
    echo "   - ${BLUE}docs/HEALTH_CHECK.md${NC} - Health check system documentation"
    echo ""
}

# Main execution
main() {
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  Supabase Health Check Schema Application"
    echo "  Project: $PROJECT_REF"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    validate_prerequisites
    test_connection
    apply_schema
    validate_schema
    insert_test_record
    display_next_steps
}

# Run main function
main

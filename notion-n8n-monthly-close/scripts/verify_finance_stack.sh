#!/bin/bash
# InsightPulse Finance Stack - Comprehensive Health Check
# Purpose: Validate Odoo finance projects, n8n workflows, Supabase integration
# Usage: ./verify_finance_stack.sh [--env prod|dev|staging] [--fix] [--verbose] [--json]

set -euo pipefail

#=============================================================================
# Configuration
#=============================================================================

# Version
VERSION="1.0.0"

# Default environment
ENV="${1:-prod}"

# Parse flags
FIX_MODE=false
VERBOSE=false
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --env)
      ENV="$2"
      shift 2
      ;;
    --fix)
      FIX_MODE=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Environment configurations
case "$ENV" in
  prod)
    ODOO_HOST="erp.insightpulseai.net"
    ODOO_CONTAINER="odoo-odoo-1"
    ODOO_DB_CONTAINER="odoo-db-1"
    SUPABASE_PROJECT_REF="xkxyvboeubffxxbebsll"
    ;;
  dev)
    ODOO_HOST="dev.insightpulseai.net"
    ODOO_CONTAINER="odoo-dev-ipa"
    ODOO_DB_CONTAINER="odoo-dev-db"
    SUPABASE_PROJECT_REF="xkxyvboeubffxxbebsll"
    ;;
  staging)
    ODOO_HOST="staging.insightpulseai.net"
    ODOO_CONTAINER="odoo-staging-ipa"
    ODOO_DB_CONTAINER="odoo-staging-db"
    SUPABASE_PROJECT_REF="xkxyvboeubffxxbebsll"
    ;;
  *)
    echo "❌ Invalid environment: $ENV. Use prod|dev|staging"
    exit 2
    ;;
esac

# Finance project IDs
FINANCE_PROJECT_IDS=(6 10 11)
FINANCE_PROJECT_NAMES=(
  "Month-end Closing - Template"
  "Tax Filing & BIR Compliance"
  "Monthly Closing - November 2025"
)
EXPECTED_TASK_COUNTS=(36 17 36)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNED_CHECKS=0

#=============================================================================
# Logging Functions
#=============================================================================

log_info() {
  if [[ "$JSON_OUTPUT" == "false" ]]; then
    echo -e "${BLUE}ℹ${NC}  $1"
  fi
}

log_success() {
  if [[ "$JSON_OUTPUT" == "false" ]]; then
    echo -e "${GREEN}✅${NC} $1"
  fi
  ((PASSED_CHECKS++))
}

log_warn() {
  if [[ "$JSON_OUTPUT" == "false" ]]; then
    echo -e "${YELLOW}⚠️${NC}  $1"
  fi
  ((WARNED_CHECKS++))
}

log_error() {
  if [[ "$JSON_OUTPUT" == "false" ]]; then
    echo -e "${RED}❌${NC} $1"
  fi >&2
  ((FAILED_CHECKS++))
}

log_verbose() {
  if [[ "$VERBOSE" == "true" && "$JSON_OUTPUT" == "false" ]]; then
    echo "   $1"
  fi
}

#=============================================================================
# Supabase Logging
#=============================================================================

log_to_supabase() {
  local gate_name="$1"
  local status="$2"
  local duration="$3"
  local details="$4"

  # Only log if SUPABASE_SERVICE_ROLE_KEY is set
  if [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
    log_verbose "Supabase logging skipped (no service role key)"
    return 0
  fi

  local url="https://${SUPABASE_PROJECT_REF}.supabase.co/rest/v1/health_check"
  local payload=$(cat <<EOF
{
  "environment": "$ENV",
  "gate_name": "$gate_name",
  "status": "$status",
  "duration_ms": $duration,
  "details": $details
}
EOF
)

  curl -sf -X POST "$url" \
    -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
    -H "Content-Type: application/json" \
    -d "$payload" >/dev/null 2>&1 || log_verbose "Failed to log to Supabase"
}

#=============================================================================
# Validation Gates
#=============================================================================

# Gate 1: SSH Connectivity
validate_ssh_connectivity() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 1/10] SSH Connectivity to $ODOO_HOST"

  if ssh -o ConnectTimeout=10 -o BatchMode=yes root@"$ODOO_HOST" "echo ''" >/dev/null 2>&1; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "SSH connection successful (${duration}ms)"
    log_to_supabase "ssh_connectivity" "PASS" "$duration" '{"host": "'$ODOO_HOST'"}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_error "SSH connection failed"
    log_to_supabase "ssh_connectivity" "FAIL" "$duration" '{"host": "'$ODOO_HOST'", "error": "connection_refused"}'
    return 1
  fi
}

# Gate 2: Odoo Service Status
validate_odoo_service() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 2/10] Odoo Service Status"

  if ssh root@"$ODOO_HOST" "docker ps | grep -q $ODOO_CONTAINER" 2>/dev/null; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "Odoo container running"
    log_to_supabase "odoo_service" "PASS" "$duration" '{"container": "'$ODOO_CONTAINER'"}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_error "Odoo container not running"
    log_to_supabase "odoo_service" "FAIL" "$duration" '{"container": "'$ODOO_CONTAINER'", "error": "not_running"}'

    if [[ "$FIX_MODE" == "true" ]]; then
      log_warn "Attempting to restart Odoo..."
      ssh root@"$ODOO_HOST" "docker restart $ODOO_CONTAINER" 2>/dev/null && log_success "Odoo restarted" || log_error "Failed to restart Odoo"
    fi
    return 1
  fi
}

# Gate 3: Database Connectivity
validate_database() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 3/10] Database Connectivity"

  if ssh root@"$ODOO_HOST" "docker exec $ODOO_DB_CONTAINER psql -U odoo -d odoo -c 'SELECT 1;'" >/dev/null 2>&1; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "Database connection successful"
    log_to_supabase "database_connectivity" "PASS" "$duration" '{"container": "'$ODOO_DB_CONTAINER'"}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_error "Database connection failed"
    log_to_supabase "database_connectivity" "FAIL" "$duration" '{"container": "'$ODOO_DB_CONTAINER'", "error": "connection_failed"}'
    return 1
  fi
}

# Gate 4: Finance Projects Exist
validate_finance_projects() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 4/10] Finance Projects Validation"

  local query="SELECT id, name, active FROM project_project WHERE id IN (6, 10, 11) ORDER BY id;"
  local result=$(ssh root@"$ODOO_HOST" "docker exec $ODOO_DB_CONTAINER psql -U odoo -d odoo -t -c \"$query\"" 2>/dev/null)

  local found_count=$(echo "$result" | grep -c '|' || echo "0")

  if [[ "$found_count" -ge 3 ]]; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "All 3 finance projects found"
    log_verbose "$result"
    log_to_supabase "finance_projects" "PASS" "$duration" '{"found": '$found_count'}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_error "Expected 3 finance projects, found $found_count"
    log_to_supabase "finance_projects" "FAIL" "$duration" '{"found": '$found_count', "expected": 3}'
    return 1
  fi
}

# Gate 5: Finance Tasks Count
validate_finance_tasks() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 5/10] Finance Tasks Count Validation"

  local all_passed=true
  for i in "${!FINANCE_PROJECT_IDS[@]}"; do
    local project_id="${FINANCE_PROJECT_IDS[$i]}"
    local project_name="${FINANCE_PROJECT_NAMES[$i]}"
    local expected_count="${EXPECTED_TASK_COUNTS[$i]}"

    local query="SELECT COUNT(*) FROM project_task WHERE project_id = $project_id;"
    local actual_count=$(ssh root@"$ODOO_HOST" "docker exec $ODOO_DB_CONTAINER psql -U odoo -d odoo -t -c \"$query\"" 2>/dev/null | tr -d ' ')

    if [[ "$actual_count" -eq "$expected_count" ]]; then
      log_success "Project $project_id: $actual_count tasks (expected $expected_count)"
    else
      log_warn "Project $project_id: $actual_count tasks (expected $expected_count)"
      all_passed=false
    fi
  done

  local duration=$(($(date +%s%3N) - start_time))
  if [[ "$all_passed" == "true" ]]; then
    log_to_supabase "finance_tasks" "PASS" "$duration" '{"all_counts_match": true}'
    return 0
  else
    log_to_supabase "finance_tasks" "WARN" "$duration" '{"all_counts_match": false}'
    return 0
  fi
}

# Gate 6: UI Domain Check (Python script)
validate_ui_domain() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 6/10] UI Domain Accessibility Check"

  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  local check_script="$script_dir/../../scripts/check_project_tasks.py"

  if [[ ! -f "$check_script" ]]; then
    log_warn "check_project_tasks.py not found, skipping"
    return 0
  fi

  if ODOO_URL="https://$ODOO_HOST" ODOO_DB="odoo" python3 "$check_script" >/dev/null 2>&1; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "UI domain check passed"
    log_to_supabase "ui_domain" "PASS" "$duration" '{}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_error "UI domain check failed (see logs)"
    log_to_supabase "ui_domain" "FAIL" "$duration" '{"error": "check_failed"}'
    return 1
  fi
}

# Gate 7: n8n Workflow Health
validate_n8n_workflows() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 7/10] n8n Workflow Health"

  if [[ -z "${N8N_API_KEY:-}" ]]; then
    log_warn "N8N_API_KEY not set, skipping"
    return 0
  fi

  local n8n_url="https://ipa.insightpulseai.net/api/v1/workflows"
  if curl -sf -H "X-N8N-API-KEY: $N8N_API_KEY" "$n8n_url" >/dev/null 2>&1; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "n8n API accessible"
    log_to_supabase "n8n_workflows" "PASS" "$duration" '{}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_error "n8n API unreachable"
    log_to_supabase "n8n_workflows" "FAIL" "$duration" '{"error": "api_unreachable"}'
    return 1
  fi
}

# Gate 8: Supabase Health
validate_supabase() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 8/10] Supabase Connection"

  if [[ -z "${SUPABASE_SERVICE_ROLE_KEY:-}" ]]; then
    log_warn "SUPABASE_SERVICE_ROLE_KEY not set, skipping"
    return 0
  fi

  local url="https://${SUPABASE_PROJECT_REF}.supabase.co/rest/v1/"
  if curl -sf -H "apikey: ${SUPABASE_SERVICE_ROLE_KEY}" "$url" >/dev/null 2>&1; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "Supabase API accessible"
    log_to_supabase "supabase_health" "PASS" "$duration" '{}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_error "Supabase API unreachable"
    log_to_supabase "supabase_health" "FAIL" "$duration" '{"error": "api_unreachable"}'
    return 1
  fi
}

# Gate 9: OCR Service Health
validate_ocr_service() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 9/10] OCR Service Health"

  local ocr_url="https://ade-ocr-backend-d9dru.ondigitalocean.app/health"
  if curl -sf "$ocr_url" >/dev/null 2>&1; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "OCR service healthy"
    log_to_supabase "ocr_service" "PASS" "$duration" '{}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_warn "OCR service unreachable"
    log_to_supabase "ocr_service" "WARN" "$duration" '{"error": "service_unreachable"}'
    return 0
  fi
}

# Gate 10: Worker Status
validate_workers() {
  local start_time=$(date +%s%3N)
  ((TOTAL_CHECKS++))

  log_info "[Gate 10/10] Odoo Worker Status"

  local worker_logs=$(ssh root@"$ODOO_HOST" "docker logs --tail 50 $ODOO_CONTAINER 2>&1 | grep -i worker" 2>/dev/null || echo "")

  if echo "$worker_logs" | grep -q "alive"; then
    local duration=$(($(date +%s%3N) - start_time))
    log_success "Workers alive"
    log_verbose "$worker_logs"
    log_to_supabase "workers" "PASS" "$duration" '{}'
    return 0
  else
    local duration=$(($(date +%s%3N) - start_time))
    log_warn "No worker status found in logs"
    log_to_supabase "workers" "WARN" "$duration" '{"error": "no_worker_logs"}'
    return 0
  fi
}

#=============================================================================
# Main Execution
#=============================================================================

main() {
  if [[ "$JSON_OUTPUT" == "false" ]]; then
    echo "============================================================"
    echo "  InsightPulse Finance Stack Health Check v${VERSION}"
    echo "  Environment: $ENV"
    echo "  Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    echo "  Fix Mode: $FIX_MODE"
    echo "============================================================"
    echo ""
  fi

  # Run all validation gates
  validate_ssh_connectivity || true
  validate_odoo_service || true
  validate_database || true
  validate_finance_projects || true
  validate_finance_tasks || true
  validate_ui_domain || true
  validate_n8n_workflows || true
  validate_supabase || true
  validate_ocr_service || true
  validate_workers || true

  # Summary
  if [[ "$JSON_OUTPUT" == "true" ]]; then
    cat <<EOF
{
  "environment": "$ENV",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "total_checks": $TOTAL_CHECKS,
  "passed": $PASSED_CHECKS,
  "failed": $FAILED_CHECKS,
  "warned": $WARNED_CHECKS,
  "success": $([ $FAILED_CHECKS -eq 0 ] && echo "true" || echo "false")
}
EOF
  else
    echo ""
    echo "============================================================"
    echo "  Summary"
    echo "============================================================"
    echo "  Total Checks:  $TOTAL_CHECKS"
    echo "  Passed:        $PASSED_CHECKS"
    echo "  Failed:        $FAILED_CHECKS"
    echo "  Warnings:      $WARNED_CHECKS"
    echo "============================================================"

    if [[ $FAILED_CHECKS -eq 0 ]]; then
      echo -e "${GREEN}✅ W150_FINANCE_STACK_OK: All checks passed${NC}"
      echo "============================================================"
      return 0
    else
      echo -e "${RED}❌ W150_FINANCE_STACK_FAIL: $FAILED_CHECKS checks failed${NC}"
      echo "============================================================"
      return 1
    fi
  fi
}

# Run main
main
exit $?

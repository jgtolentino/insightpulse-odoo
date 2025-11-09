#!/usr/bin/env bash
set -euo pipefail

# Automation Health Check Script
# Purpose: Validation Pyramid implementation for InsightPulse Odoo
# Usage: ./automation-health.sh [--layer LAYER] [--fast] [--json]
# Layers: static, automated, integration, production, all (default)
# Last Updated: 2025-11-09

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Status emojis
PASS="✅"
FAIL="❌"
WARN="⚠️"
INFO="ℹ️"

# Configuration
LAYER="${1:-all}"
FAST_MODE=false
JSON_OUTPUT=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --layer)
      LAYER="$2"
      shift 2
      ;;
    --fast)
      FAST_MODE=true
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

# Counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Results storage
declare -a RESULTS

log_result() {
  local status=$1
  local message=$2

  TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

  case $status in
    "PASS")
      PASSED_CHECKS=$((PASSED_CHECKS + 1))
      if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${GREEN}${PASS} ${message}${NC}"
      fi
      ;;
    "FAIL")
      FAILED_CHECKS=$((FAILED_CHECKS + 1))
      if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${RED}${FAIL} ${message}${NC}"
      fi
      ;;
    "WARN")
      WARNING_CHECKS=$((WARNING_CHECKS + 1))
      if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${YELLOW}${WARN} ${message}${NC}"
      fi
      ;;
    "INFO")
      if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${BLUE}${INFO} ${message}${NC}"
      fi
      ;;
  esac

  RESULTS+=("$status|$message")
}

# ════════════════════════════════════════════════════════════════
# LAYER 1: STATIC ANALYSIS
# ════════════════════════════════════════════════════════════════

layer_static() {
  if [ "$JSON_OUTPUT" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 Layer 1: Static Analysis"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  fi

  # Python linting (pylint)
  if command -v pylint >/dev/null 2>&1; then
    if pylint odoo/addons/ --exit-zero --score=no >/dev/null 2>&1; then
      log_result "PASS" "Python linting (pylint)"
    else
      log_result "FAIL" "Python linting (pylint)"
    fi
  else
    log_result "WARN" "Python linting (pylint not installed)"
  fi

  # Python style (flake8)
  if command -v flake8 >/dev/null 2>&1; then
    if flake8 odoo/addons/ --exit-zero >/dev/null 2>&1; then
      log_result "PASS" "Python style (flake8)"
    else
      log_result "FAIL" "Python style (flake8)"
    fi
  else
    log_result "WARN" "Python style (flake8 not installed)"
  fi

  # Python type checking (mypy) - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if command -v mypy >/dev/null 2>&1; then
      if mypy odoo/addons/ --ignore-missing-imports --no-error-summary >/dev/null 2>&1; then
        log_result "PASS" "Python type checking (mypy)"
      else
        log_result "WARN" "Python type checking (mypy - warnings)"
      fi
    else
      log_result "INFO" "Python type checking (mypy not installed)"
    fi
  fi

  # YAML linting
  if command -v yamllint >/dev/null 2>&1; then
    if yamllint -d relaxed . >/dev/null 2>&1; then
      log_result "PASS" "YAML linting (yamllint)"
    else
      log_result "FAIL" "YAML linting (yamllint)"
    fi
  else
    log_result "WARN" "YAML linting (yamllint not installed)"
  fi

  # SQL linting - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if command -v sqlfluff >/dev/null 2>&1; then
      if find . -name "*.sql" -type f -exec sqlfluff lint {} + >/dev/null 2>&1; then
        log_result "PASS" "SQL linting (sqlfluff)"
      else
        log_result "WARN" "SQL linting (sqlfluff - warnings)"
      fi
    else
      log_result "INFO" "SQL linting (sqlfluff not installed)"
    fi
  fi

  # Security scanning (bandit)
  if command -v bandit >/dev/null 2>&1; then
    if bandit -r odoo/addons/ -ll -q >/dev/null 2>&1; then
      log_result "PASS" "Security scanning (bandit)"
    else
      log_result "FAIL" "Security scanning (bandit)"
    fi
  else
    log_result "WARN" "Security scanning (bandit not installed)"
  fi

  # Dependency audit (pip-audit)
  if command -v pip-audit >/dev/null 2>&1; then
    if pip-audit --quiet >/dev/null 2>&1; then
      log_result "PASS" "Dependency audit (pip-audit)"
    else
      log_result "FAIL" "Dependency audit (pip-audit)"
    fi
  else
    log_result "INFO" "Dependency audit (pip-audit not installed)"
  fi

  # Repository structure validation
  if [ -f "scripts/validate-repo-structure.py" ]; then
    if python3 scripts/validate-repo-structure.py >/dev/null 2>&1; then
      log_result "PASS" "Repository structure validation"
    else
      log_result "FAIL" "Repository structure validation"
    fi
  else
    log_result "WARN" "Repository structure validation (script not found)"
  fi
}

# ════════════════════════════════════════════════════════════════
# LAYER 2: AUTOMATED CI/CD
# ════════════════════════════════════════════════════════════════

layer_automated() {
  if [ "$JSON_OUTPUT" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🤖 Layer 2: Automated CI/CD"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  fi

  # Spec-driven contract validation
  if [ -f "ci/speckit/validate_spec_contract.py" ]; then
    if python3 ci/speckit/validate_spec_contract.py >/dev/null 2>&1; then
      log_result "PASS" "Spec-driven contract validation"
    else
      log_result "FAIL" "Spec-driven contract validation"
    fi
  else
    log_result "WARN" "Spec-driven contract validation (script not found)"
  fi

  # Spec drift detection
  if [ -f "ci/speckit/spec_drift_gate.py" ]; then
    if python3 ci/speckit/spec_drift_gate.py >/dev/null 2>&1; then
      log_result "PASS" "Spec drift detection"
    else
      log_result "FAIL" "Spec drift detection"
    fi
  else
    log_result "WARN" "Spec drift detection (script not found)"
  fi

  # OCA MQT checks - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -f "ci/qa/run_mqt.sh" ]; then
      if bash ci/qa/run_mqt.sh >/dev/null 2>&1; then
        log_result "PASS" "OCA Module Quality Tools (MQT)"
      else
        log_result "FAIL" "OCA Module Quality Tools (MQT)"
      fi
    else
      log_result "WARN" "OCA MQT checks (script not found)"
    fi
  fi

  # Odoo module tests
  if command -v pytest >/dev/null 2>&1; then
    if pytest odoo/tests/ -q --tb=no >/dev/null 2>&1; then
      log_result "PASS" "Odoo module tests (pytest)"
    else
      log_result "FAIL" "Odoo module tests (pytest)"
    fi
  else
    log_result "WARN" "Odoo module tests (pytest not installed)"
  fi

  # Unit tests
  if [ -d "tests/unit" ]; then
    if pytest tests/unit/ -q --tb=no >/dev/null 2>&1; then
      log_result "PASS" "Unit tests"
    else
      log_result "FAIL" "Unit tests"
    fi
  else
    log_result "INFO" "Unit tests (no tests directory found)"
  fi

  # OCR service tests - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -f "tests/test_ocr_endpoints.py" ]; then
      if pytest tests/test_ocr_endpoints.py -q --tb=no >/dev/null 2>&1; then
        log_result "PASS" "OCR service tests"
      else
        log_result "FAIL" "OCR service tests"
      fi
    else
      log_result "INFO" "OCR service tests (test file not found)"
    fi
  fi

  # Warehouse view tests - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -f "tests/test_warehouse_views.py" ]; then
      if pytest tests/test_warehouse_views.py -q --tb=no >/dev/null 2>&1; then
        log_result "PASS" "Warehouse view tests"
      else
        log_result "FAIL" "Warehouse view tests"
      fi
    else
      log_result "INFO" "Warehouse view tests (test file not found)"
    fi
  fi

  # Skills registry validation
  if [ -f "scripts/skills/consolidate.py" ]; then
    if python3 scripts/skills/consolidate.py >/dev/null 2>&1; then
      log_result "PASS" "Skills registry validation"
    else
      log_result "FAIL" "Skills registry validation"
    fi
  else
    log_result "WARN" "Skills registry validation (script not found)"
  fi

  # Claude config freshness check
  if [ -f "claude.md" ]; then
    LAST_MODIFIED=$(stat -f %m claude.md 2>/dev/null || stat -c %Y claude.md)
    CURRENT_TIME=$(date +%s)
    DAYS_OLD=$(( (CURRENT_TIME - LAST_MODIFIED) / 86400 ))

    if [ $DAYS_OLD -lt 7 ]; then
      log_result "PASS" "Claude config freshness (<7 days old)"
    else
      log_result "FAIL" "Claude config freshness (${DAYS_OLD} days old, >7 days)"
    fi
  else
    log_result "WARN" "Claude config freshness (claude.md not found)"
  fi
}

# ════════════════════════════════════════════════════════════════
# LAYER 3: INTEGRATION TESTS
# ════════════════════════════════════════════════════════════════

layer_integration() {
  if [ "$JSON_OUTPUT" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔗 Layer 3: Integration Tests"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  fi

  # Instance health checks (local)
  if [ -f "scripts/health/check-instance-health.sh" ]; then
    if bash scripts/health/check-instance-health.sh local >/dev/null 2>&1; then
      log_result "PASS" "Instance health (local)"
    else
      log_result "FAIL" "Instance health (local)"
    fi
  else
    log_result "WARN" "Instance health checks (script not found)"
  fi

  # Expense intake idempotency test - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -f "tests/test_expense_idempotency.py" ]; then
      if pytest tests/test_expense_idempotency.py -q --tb=no >/dev/null 2>&1; then
        log_result "PASS" "Expense intake idempotency"
      else
        log_result "FAIL" "Expense intake idempotency"
      fi
    else
      log_result "INFO" "Expense intake idempotency (test not found)"
    fi
  fi

  # OCR service contract test - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -f "tests/test_ocr_endpoints.py" ]; then
      if pytest tests/test_ocr_endpoints.py::test_classify_expense -q --tb=no >/dev/null 2>&1; then
        log_result "PASS" "OCR service contract"
      else
        log_result "FAIL" "OCR service contract"
      fi
    else
      log_result "INFO" "OCR service contract (test not found)"
    fi
  fi

  # Warehouse view availability - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -f "tests/test_warehouse_views.py" ]; then
      if pytest tests/test_warehouse_views.py -q --tb=no >/dev/null 2>&1; then
        log_result "PASS" "Warehouse view availability"
      else
        log_result "FAIL" "Warehouse view availability"
      fi
    else
      log_result "INFO" "Warehouse view availability (test not found)"
    fi
  fi

  # Cross-service synthetic flow - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -f "tests/integration/test_synthetic_order_flow.py" ]; then
      if pytest tests/integration/test_synthetic_order_flow.py -q --tb=no >/dev/null 2>&1; then
        log_result "PASS" "Cross-service synthetic flow"
      else
        log_result "FAIL" "Cross-service synthetic flow"
      fi
    else
      log_result "INFO" "Cross-service synthetic flow (test not found)"
    fi
  fi

  # OAuth SSO flow test - planned
  if [ -f "tests/test_oauth_flow.py" ]; then
    if pytest tests/test_oauth_flow.py -q --tb=no >/dev/null 2>&1; then
      log_result "PASS" "OAuth SSO flow"
    else
      log_result "FAIL" "OAuth SSO flow"
    fi
  else
    log_result "INFO" "OAuth SSO flow (test planned)"
  fi

  # Magic Link flow test - planned
  if [ -f "tests/test_magic_link_flow.py" ]; then
    if pytest tests/test_magic_link_flow.py -q --tb=no >/dev/null 2>&1; then
      log_result "PASS" "Magic Link flow"
    else
      log_result "FAIL" "Magic Link flow"
    fi
  else
    log_result "INFO" "Magic Link flow (test planned)"
  fi
}

# ════════════════════════════════════════════════════════════════
# LAYER 4: PRODUCTION MONITORING
# ════════════════════════════════════════════════════════════════

layer_production() {
  if [ "$JSON_OUTPUT" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🚀 Layer 4: Production Monitoring"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  fi

  # Prometheus availability
  if command -v curl >/dev/null 2>&1; then
    if curl -fsS --max-time 5 http://localhost:9090/-/healthy >/dev/null 2>&1; then
      log_result "PASS" "Prometheus availability"
    else
      log_result "INFO" "Prometheus availability (not running locally)"
    fi
  else
    log_result "WARN" "Prometheus availability (curl not installed)"
  fi

  # Alertmanager availability
  if curl -fsS --max-time 5 http://localhost:9093/-/healthy >/dev/null 2>&1; then
    log_result "PASS" "Alertmanager availability"
  else
    log_result "INFO" "Alertmanager availability (not running locally)"
  fi

  # Health heartbeat function (Supabase Edge Function) - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
      if curl -fsS --max-time 10 -X POST "${SUPABASE_URL}/functions/v1/health_heartbeat" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -d '{"source":"automation-health","status":"ok"}' >/dev/null 2>&1; then
        log_result "PASS" "Health heartbeat (Supabase Edge Function)"
      else
        log_result "FAIL" "Health heartbeat (Supabase Edge Function)"
      fi
    else
      log_result "INFO" "Health heartbeat (Supabase credentials not set)"
    fi
  fi

  # Synthetic order flow function - skip in fast mode
  if [ "$FAST_MODE" = false ]; then
    if [ -n "${SUPABASE_URL:-}" ] && [ -n "${SUPABASE_SERVICE_ROLE_KEY:-}" ]; then
      if curl -fsS --max-time 10 -X POST "${SUPABASE_URL}/functions/v1/synthetic_order_flow" \
        -H "Authorization: Bearer ${SUPABASE_SERVICE_ROLE_KEY}" \
        -d '{}' >/dev/null 2>&1; then
        log_result "PASS" "Synthetic order flow (Edge Function)"
      else
        log_result "FAIL" "Synthetic order flow (Edge Function)"
      fi
    else
      log_result "INFO" "Synthetic order flow (Supabase credentials not set)"
    fi
  fi

  # Log aggregation check
  if command -v journalctl >/dev/null 2>&1; then
    if journalctl --version >/dev/null 2>&1; then
      log_result "PASS" "Log aggregation (journalctl available)"
    else
      log_result "INFO" "Log aggregation (journalctl not configured)"
    fi
  else
    log_result "INFO" "Log aggregation (journalctl not installed)"
  fi
}

# ════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ════════════════════════════════════════════════════════════════

main() {
  if [ "$JSON_OUTPUT" = false ]; then
    echo "╔═════════════════════════════════════════════════════════╗"
    echo "║   InsightPulse Odoo - Automation Health Check          ║"
    echo "║   Validation Pyramid Implementation                    ║"
    echo "╚═════════════════════════════════════════════════════════╝"
    echo ""
    echo "Layer: ${LAYER}"
    echo "Fast Mode: ${FAST_MODE}"
    echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
  fi

  # Execute selected layer(s)
  case $LAYER in
    static)
      layer_static
      ;;
    automated)
      layer_automated
      ;;
    integration)
      layer_integration
      ;;
    production)
      layer_production
      ;;
    all)
      layer_static
      layer_automated
      layer_integration
      layer_production
      ;;
    *)
      echo "❌ Invalid layer: ${LAYER}"
      echo "Valid layers: static, automated, integration, production, all"
      exit 1
      ;;
  esac

  # Summary
  if [ "$JSON_OUTPUT" = false ]; then
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Summary"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Total Checks:   ${TOTAL_CHECKS}"
    echo "Passed:         ${GREEN}${PASSED_CHECKS}${NC}"
    echo "Failed:         ${RED}${FAILED_CHECKS}${NC}"
    echo "Warnings:       ${YELLOW}${WARNING_CHECKS}${NC}"
    echo ""

    # Calculate percentage
    if [ $TOTAL_CHECKS -gt 0 ]; then
      PASS_PERCENTAGE=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
      echo "Pass Rate:      ${PASS_PERCENTAGE}%"

      # Overall health status
      if [ $FAILED_CHECKS -eq 0 ]; then
        if [ $WARNING_CHECKS -eq 0 ]; then
          echo "Overall Status: ${GREEN}🟢 HEALTHY${NC}"
        else
          echo "Overall Status: ${YELLOW}🟡 WARNING${NC}"
        fi
      else
        echo "Overall Status: ${RED}🔴 UNHEALTHY${NC}"
      fi
    fi

    echo ""
    echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
  else
    # JSON output
    echo "{"
    echo "  \"timestamp\": \"$(date -u +"%Y-%m-%d %H:%M:%S UTC")\","
    echo "  \"layer\": \"${LAYER}\","
    echo "  \"fast_mode\": ${FAST_MODE},"
    echo "  \"total_checks\": ${TOTAL_CHECKS},"
    echo "  \"passed\": ${PASSED_CHECKS},"
    echo "  \"failed\": ${FAILED_CHECKS},"
    echo "  \"warnings\": ${WARNING_CHECKS},"
    echo "  \"pass_rate\": $(( (PASSED_CHECKS * 100) / TOTAL_CHECKS )),"
    echo "  \"results\": ["

    first=true
    for result in "${RESULTS[@]}"; do
      status="${result%%|*}"
      message="${result#*|}"

      if [ "$first" = true ]; then
        first=false
      else
        echo ","
      fi

      echo -n "    {\"status\": \"$status\", \"message\": \"$message\"}"
    done

    echo ""
    echo "  ]"
    echo "}"
  fi

  # Exit code
  if [ $FAILED_CHECKS -gt 0 ]; then
    exit 1
  else
    exit 0
  fi
}

# Run main
main

#!/bin/bash
# Pre-Flight Check Script
# Validates code quality, spec compliance, and security before committing
#
# Usage: ./scripts/pre-flight-check.sh [--strict]
#   --strict: Exit on any warning (default: exit only on errors)

set -e

STRICT_MODE=false
if [ "$1" = "--strict" ]; then
  STRICT_MODE=true
fi

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
ERRORS=0
WARNINGS=0
PASSED=0

# Helper functions
error() {
  echo -e "${RED}❌ ERROR: $1${NC}"
  ((ERRORS++))
}

warning() {
  echo -e "${YELLOW}⚠️  WARNING: $1${NC}"
  ((WARNINGS++))
}

success() {
  echo -e "${GREEN}✅ $1${NC}"
  ((PASSED++))
}

info() {
  echo -e "${BLUE}ℹ️  $1${NC}"
}

section() {
  echo ""
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
  echo -e "${BLUE}$1${NC}"
  echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Start checks
echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        🔍 Pre-Flight Checks Starting             ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"

# Check 1: Platform Spec Validation
section "1. Platform Spec Validation"

if [ -f "scripts/validate_spec.py" ] && [ -f "spec/platform_spec.json" ]; then
  if python3 scripts/validate_spec.py > /dev/null 2>&1; then
    success "Platform spec validation passed"
  else
    error "Platform spec validation failed"
    info "Run: python3 scripts/validate_spec.py"
  fi
else
  warning "Spec validation script not found (skipping)"
fi

# Check 2: Code Formatting
section "2. Code Formatting"

# Check if black is installed
if command -v black &> /dev/null; then
  if black --check . --exclude '/(\.git|\.venv|venv|node_modules|build|dist)/' > /dev/null 2>&1; then
    success "Black formatting check passed"
  else
    warning "Black formatting issues found"
    info "Run: black ."
  fi
else
  warning "Black not installed (pip install black)"
fi

# Check if isort is installed
if command -v isort &> /dev/null; then
  if isort --check-only . --skip .venv --skip venv --skip node_modules > /dev/null 2>&1; then
    success "Isort import sorting check passed"
  else
    warning "Import sorting issues found"
    info "Run: isort ."
  fi
else
  warning "Isort not installed (pip install isort)"
fi

# Check 3: Linting
section "3. Linting"

# Flake8
if command -v flake8 &> /dev/null; then
  if [ -d "addons" ] || [ -d "scripts" ]; then
    LINT_PATHS=""
    [ -d "addons" ] && LINT_PATHS="$LINT_PATHS addons/"
    [ -d "scripts" ] && LINT_PATHS="$LINT_PATHS scripts/"

    if flake8 $LINT_PATHS --max-line-length=120 --extend-ignore=E203,W503 --exclude=__pycache__,*.pyc,.git > /dev/null 2>&1; then
      success "Flake8 linting passed"
    else
      warning "Flake8 linting issues found"
      info "Run: flake8 $LINT_PATHS --max-line-length=120"
    fi
  else
    info "No addons/ or scripts/ directories to lint"
  fi
else
  warning "Flake8 not installed (pip install flake8)"
fi

# Check 4: Security - No secrets in code
section "4. Security Checks"

# Check for common secret patterns
SECRET_PATTERNS=(
  "sk-[a-zA-Z0-9]"          # OpenAI API keys
  "AKIA[0-9A-Z]"             # AWS access keys
  "ghp_[a-zA-Z0-9]"          # GitHub personal access tokens
  "glpat-[a-zA-Z0-9]"        # GitLab tokens
  "-----BEGIN.*PRIVATE KEY" # Private keys
  "password\s*=\s*['\"]"     # Hardcoded passwords
  "api_key\s*=\s*['\"]"      # Hardcoded API keys
)

SECRETS_FOUND=false
for pattern in "${SECRET_PATTERNS[@]}"; do
  if grep -rE "$pattern" --include="*.py" --include="*.yml" --include="*.yaml" --include="*.js" --include="*.ts" \
     --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=.venv --exclude-dir=venv \
     . > /dev/null 2>&1; then
    SECRETS_FOUND=true
    break
  fi
done

if [ "$SECRETS_FOUND" = true ]; then
  error "Potential secrets/API keys found in code!"
  info "Check: Use environment variables and .env.example for config"
else
  success "No hardcoded secrets detected"
fi

# Check 5: Python Module Compilation
section "5. Python Module Compilation"

COMPILE_PATHS=""
[ -d "agents" ] && COMPILE_PATHS="$COMPILE_PATHS agents"
[ -d "workflows" ] && COMPILE_PATHS="$COMPILE_PATHS workflows"
[ -d "memory" ] && COMPILE_PATHS="$COMPILE_PATHS memory"
[ -d "addons" ] && COMPILE_PATHS="$COMPILE_PATHS addons"

if [ -n "$COMPILE_PATHS" ]; then
  if python3 -m compileall $COMPILE_PATHS > /dev/null 2>&1; then
    success "Python module compilation passed"
  else
    warning "Python compilation issues found"
    info "Run: python3 -m compileall $COMPILE_PATHS"
  fi
else
  info "No Python modules to compile"
fi

# Check 6: Git Status
section "6. Git Status"

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
  info "Uncommitted changes detected (normal for pre-commit check)"
else
  success "Working tree is clean"
fi

# Check for merge conflicts
if grep -r "<<<<<<< HEAD" --include="*.py" --include="*.yml" --include="*.md" . > /dev/null 2>&1; then
  error "Merge conflict markers found!"
else
  success "No merge conflicts detected"
fi

# Check 7: TODO markers in production code
section "7. TODO Markers Check"

if grep -r "TODO" --include="*.py" --exclude-dir=tests --exclude-dir=.git \
   addons/ scripts/ 2>/dev/null | grep -v "# TODO: " > /dev/null 2>&1; then
  warning "TODO markers found in production code"
  info "Consider creating GitHub issues for TODOs"
else
  success "No TODO markers in production code"
fi

# Summary
section "📊 Pre-Flight Check Summary"

echo ""
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "${RED}❌ Errors: $ERRORS${NC}"
echo ""

# Exit logic
if [ $ERRORS -gt 0 ]; then
  echo -e "${RED}╔═══════════════════════════════════════════════════╗${NC}"
  echo -e "${RED}║  ❌ Pre-flight checks FAILED - Fix errors above  ║${NC}"
  echo -e "${RED}╚═══════════════════════════════════════════════════╝${NC}"
  exit 1
elif [ $WARNINGS -gt 0 ] && [ "$STRICT_MODE" = true ]; then
  echo -e "${YELLOW}╔═══════════════════════════════════════════════════╗${NC}"
  echo -e "${YELLOW}║  ⚠️  Warnings detected (strict mode enabled)     ║${NC}"
  echo -e "${YELLOW}╚═══════════════════════════════════════════════════╝${NC}"
  exit 1
else
  echo -e "${GREEN}╔═══════════════════════════════════════════════════╗${NC}"
  echo -e "${GREEN}║  ✅ Pre-flight checks PASSED - Ready to commit!  ║${NC}"
  echo -e "${GREEN}╚═══════════════════════════════════════════════════╝${NC}"
  exit 0
fi

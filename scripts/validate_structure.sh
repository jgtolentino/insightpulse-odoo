#!/usr/bin/env bash
# Comprehensive validation script for Supabase-first monorepo structure
set -euo pipefail

echo "🔍 Validating Supabase-first Monorepo Structure..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Counter for checks
PASSED=0
WARNINGS=0
FAILED=0

# Function to check directory exists
check_dir() {
    local dir=$1
    local required=${2:-true}
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} Directory exists: $dir"
        PASSED=$((PASSED + 1))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} REQUIRED directory missing: $dir"
            FAILED=$((FAILED + 1))
            return 1
        else
            echo -e "${YELLOW}⚠${NC} Optional directory missing: $dir"
            WARNINGS=$((WARNINGS + 1))
            return 0
        fi
    fi
}

# Function to check file exists
check_file() {
    local file=$1
    local required=${2:-true}
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} File exists: $file"
        PASSED=$((PASSED + 1))
        return 0
    else
        if [ "$required" = "true" ]; then
            echo -e "${RED}✗${NC} REQUIRED file missing: $file"
            FAILED=$((FAILED + 1))
            return 1
        else
            echo -e "${YELLOW}⚠${NC} Optional file missing: $file"
            WARNINGS=$((WARNINGS + 1))
            return 0
        fi
    fi
}

# Function to check file is executable
check_executable() {
    local file=$1
    
    if [ -x "$file" ]; then
        echo -e "${GREEN}✓${NC} File is executable: $file"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗${NC} File is NOT executable: $file"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. CANONICAL DEPLOY SURFACE (supabase/)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_dir "supabase" true
check_dir "supabase/migrations" true
check_dir "supabase/functions" true
check_file "supabase/config.toml" false

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. RUNTIME EXECUTION (runtime/)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_dir "runtime" true
check_dir "runtime/odoo" true
check_file "runtime/odoo/docker-compose.yml" true
check_file "runtime/odoo/odoo.conf" true
check_file "runtime/README.md" false

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. EXTERNAL DEPENDENCIES (vendor/)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_dir "vendor" true
check_dir "vendor/odoo" false
# OCA can be in vendor/oca OR at root oca/ for legacy compatibility
if [ -d "vendor/oca" ] || [ -d "oca" ]; then
    echo -e "${GREEN}✓${NC} OCA modules found (vendor/oca or oca/)"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}✗${NC} REQUIRED: OCA modules directory missing"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. CUSTOM MODULES (addons/)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_dir "addons" true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. CLAUDE TOOLING (tools/claude-plugin/)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_dir "tools/claude-plugin" true
check_dir "tools/claude-plugin/.claude-plugin" false
check_dir "tools/claude-plugin/agents" true
check_dir "tools/claude-plugin/skills" true
check_file "tools/claude-plugin/README.md" false

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. UTILITY SCRIPTS (scripts/)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_file "scripts/repo_check.sh" true
check_file "scripts/odoo_up.sh" true
check_file "scripts/odoo_down.sh" true
check_file "scripts/supabase_up.sh" true

check_executable "scripts/repo_check.sh"
check_executable "scripts/odoo_up.sh"
check_executable "scripts/odoo_down.sh"
check_executable "scripts/supabase_up.sh"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. CI/CD (github/workflows/)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_file ".github/workflows/ci.yml" true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. DOCUMENTATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
check_file "MONOREPO_STRUCTURE.md" true
check_file "README.md" true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "9. DOCKER COMPOSE VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
    cd runtime/odoo
    if docker compose config --quiet 2>&1; then
        echo -e "${GREEN}✓${NC} Docker Compose file is valid"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} Docker Compose file has syntax errors"
        FAILED=$((FAILED + 1))
    fi
    cd ../..
else
    echo -e "${YELLOW}⚠${NC} Docker not available, skipping validation"
    WARNINGS=$((WARNINGS + 1))
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "10. SHELL SCRIPT SYNTAX"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
for script in scripts/repo_check.sh scripts/odoo_up.sh scripts/odoo_down.sh scripts/supabase_up.sh; do
    if bash -n "$script" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Valid bash syntax: $script"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗${NC} Invalid bash syntax: $script"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed:${NC}   $PASSED"
echo -e "${YELLOW}Warnings:${NC} $WARNINGS"
echo -e "${RED}Failed:${NC}   $FAILED"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "✅ VALIDATION PASSED"
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 0
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "❌ VALIDATION FAILED"
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    exit 1
fi

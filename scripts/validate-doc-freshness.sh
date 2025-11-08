#!/usr/bin/env bash
#
# validate-doc-freshness.sh
# Validates documentation freshness and completeness
#
# Exit codes:
#   0 - All checks passed
#   1 - Errors found (CI fails)
#   0 - Warnings only (CI passes)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 Validating Documentation Freshness..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 1. Check claude.md freshness (<7 days)
echo "1️⃣  Checking claude.md freshness..."
if [[ -f "claude.md" ]]; then
    CLAUDE_AGE=$(( ($(date +%s) - $(stat -c %Y claude.md 2>/dev/null || stat -f %m claude.md)) / 86400 ))
    echo "   📅 claude.md is $CLAUDE_AGE days old"

    if [[ $CLAUDE_AGE -gt 7 ]]; then
        echo -e "   ${RED}❌ FAIL: claude.md is stale (>7 days old)${NC}"
        ((ERRORS++))
    elif [[ $CLAUDE_AGE -gt 5 ]]; then
        echo -e "   ${YELLOW}⚠️  WARN: claude.md is getting old ($CLAUDE_AGE days)${NC}"
        ((WARNINGS++))
    else
        echo -e "   ${GREEN}✅ PASS: claude.md is fresh ($CLAUDE_AGE days old)${NC}"
    fi

    # Check required sections
    if ! grep -q "## Section 0: Repository Overview" claude.md; then
        echo -e "   ${RED}❌ FAIL: Missing Section 0${NC}"
        ((ERRORS++))
    fi

    if ! grep -q "## Section 10: Code Generation Guidelines" claude.md; then
        echo -e "   ${RED}❌ FAIL: Missing Section 10${NC}"
        ((ERRORS++))
    fi

    if ! grep -q "## Section 11: Conditional Deployment Mode" claude.md; then
        echo -e "   ${RED}❌ FAIL: Missing Section 11${NC}"
        ((ERRORS++))
    fi
else
    echo -e "   ${RED}❌ FAIL: claude.md not found${NC}"
    ((ERRORS++))
fi
echo ""

# 2. Check README.md completeness
echo "2️⃣  Checking README.md completeness..."
if [[ -f "README.md" ]]; then
    # Check for essential sections
    MISSING_SECTIONS=0

    if ! grep -qi "## Quick Start\|## Installation" README.md; then
        echo -e "   ${YELLOW}⚠️  WARN: Missing Quick Start/Installation section${NC}"
        ((WARNINGS++))
    fi

    if ! grep -qiE "Features|What.*Included" README.md; then
        echo -e "   ${YELLOW}⚠️  WARN: Missing Features section${NC}"
        ((WARNINGS++))
    fi

    if [[ $WARNINGS -eq 0 ]]; then
        echo -e "   ${GREEN}✅ PASS: All required sections present${NC}"
    fi
else
    echo -e "   ${RED}❌ FAIL: README.md not found${NC}"
    ((ERRORS++))
fi
echo ""

# 3. Check PLANNING.md freshness (<30 days)
echo "3️⃣  Checking PLANNING.md freshness..."
if [[ -f ".github/PLANNING.md" ]]; then
    PLANNING_AGE=$(( ($(date +%s) - $(stat -c %Y .github/PLANNING.md 2>/dev/null || stat -f %m .github/PLANNING.md)) / 86400 ))
    echo "   📅 PLANNING.md is $PLANNING_AGE days old"

    if [[ $PLANNING_AGE -gt 30 ]]; then
        echo -e "   ${YELLOW}⚠️  WARN: PLANNING.md is stale (>30 days old)${NC}"
        ((WARNINGS++))
    else
        echo -e "   ${GREEN}✅ PASS: PLANNING.md is fresh ($PLANNING_AGE days old)${NC}"
    fi
else
    echo -e "   ${YELLOW}⚠️  WARN: .github/PLANNING.md not found${NC}"
    ((WARNINGS++))
fi
echo ""

# 4. Validate cross-references
echo "4️⃣  Validating cross-references..."
BROKEN_REFS=0

# Check if claude.md references README.md
if [[ -f "claude.md" ]]; then
    if grep -q "README.md" claude.md; then
        echo -e "   ${GREEN}✅ claude.md → README.md${NC}"
    else
        echo -e "   ${YELLOW}⚠️  claude.md should reference README.md${NC}"
        ((WARNINGS++))
    fi
fi

# Check if README.md references claude.md
if [[ -f "README.md" ]]; then
    if grep -q "claude.md" README.md; then
        echo -e "   ${GREEN}✅ README.md → claude.md${NC}"
    else
        echo -e "   ${YELLOW}⚠️  README.md should reference claude.md${NC}"
        ((WARNINGS++))
    fi
fi

if [[ $BROKEN_REFS -eq 0 ]] && [[ $WARNINGS -eq 0 ]]; then
    echo -e "   ${GREEN}✅ PASS: All cross-references valid${NC}"
fi
echo ""

# 5. Check module documentation coverage
echo "5️⃣  Checking module documentation..."
if [[ -d "odoo/addons" ]]; then
    TOTAL_MODULES=0
    DOCUMENTED_MODULES=0

    for module in odoo/addons/*; do
        if [[ -d "$module" ]] && [[ -f "$module/__manifest__.py" ]]; then
            ((TOTAL_MODULES++))
            if [[ -f "$module/README.md" ]]; then
                ((DOCUMENTED_MODULES++))
            fi
        fi
    done

    if [[ $TOTAL_MODULES -gt 0 ]]; then
        COVERAGE=$(( DOCUMENTED_MODULES * 100 / TOTAL_MODULES ))
        echo "   📊 Documentation coverage: $DOCUMENTED_MODULES/$TOTAL_MODULES modules ($COVERAGE%)"

        if [[ $COVERAGE -lt 80 ]]; then
            echo -e "   ${YELLOW}⚠️  WARN: Documentation coverage <80%${NC}"
            ((WARNINGS++))
        else
            echo -e "   ${GREEN}✅ PASS: Documentation coverage ≥80%${NC}"
        fi
    else
        echo "   ℹ️  No modules found (repository just initialized)"
    fi
else
    echo "   ℹ️  odoo/addons directory not found"
fi
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Documentation Validation Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Errors:   $ERRORS"
echo "Warnings: $WARNINGS"
echo ""

if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}❌ FAIL: $ERRORS error(s) found${NC}"
    echo ""
    echo "Fix errors and run again:"
    echo "  ./scripts/update-auto-sections.sh"
    echo "  git add . && git commit -m 'docs: update documentation'"
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}⚠️  WARN: $WARNINGS warning(s) found${NC}"
    echo ""
    echo "Consider addressing warnings:"
    echo "  ./scripts/update-auto-sections.sh"
    exit 0
else
    echo -e "${GREEN}✅ PASS: All documentation is fresh and valid${NC}"
    exit 0
fi

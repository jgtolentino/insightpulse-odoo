#!/bin/bash
# Local quality checks for InsightPulse Odoo
# Runs linting and formatting checks before committing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "InsightPulse Odoo - Local Quality Checks"
echo "============================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -d "addons" ]; then
    echo -e "${RED}✗${NC} Error: Must be run from repository root"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check for Python
if ! command_exists python3; then
    echo -e "${RED}✗${NC} Python 3 is not installed"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"
echo ""

# Install/check dependencies
echo "Checking dependencies..."
echo "------------------------"

PACKAGES="pre-commit black isort flake8 pylint bandit"
MISSING_PACKAGES=""

for package in $PACKAGES; do
    if ! python3 -m pip show "$package" > /dev/null 2>&1; then
        MISSING_PACKAGES="$MISSING_PACKAGES $package"
    fi
done

if [ -n "$MISSING_PACKAGES" ]; then
    echo -e "${YELLOW}⚠${NC} Missing packages:$MISSING_PACKAGES"
    echo "Installing missing packages..."
    python3 -m pip install --user $MISSING_PACKAGES
    echo ""
fi

echo -e "${GREEN}✓${NC} All required packages are installed"
echo ""

# Test 1: Run pre-commit hooks
echo "Test 1: Pre-commit Hooks"
echo "------------------------"
if command_exists pre-commit; then
    if pre-commit run --all-files; then
        echo -e "${GREEN}✓${NC} Pre-commit checks passed"
    else
        echo -e "${YELLOW}⚠${NC} Pre-commit checks found issues (some may be auto-fixed)"
    fi
else
    echo -e "${YELLOW}⚠${NC} pre-commit not available"
fi
echo ""

# Test 2: Black formatting check
echo "Test 2: Black Formatting"
echo "------------------------"
if command_exists black; then
    if find addons -name '*.py' -type f | xargs black --check --line-length=88 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Code is properly formatted"
    else
        echo -e "${YELLOW}⚠${NC} Code formatting issues found"
        echo "  Run: black addons --line-length=88"
    fi
else
    echo -e "${YELLOW}⚠${NC} black not available"
fi
echo ""

# Test 3: isort import sorting
echo "Test 3: Import Sorting (isort)"
echo "-------------------------------"
if command_exists isort; then
    if find addons -name '*.py' -type f | xargs isort --check-only --profile=black 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Imports are properly sorted"
    else
        echo -e "${YELLOW}⚠${NC} Import sorting issues found"
        echo "  Run: isort addons --profile=black"
    fi
else
    echo -e "${YELLOW}⚠${NC} isort not available"
fi
echo ""

# Test 4: Flake8 linting
echo "Test 4: Flake8 Linting"
echo "----------------------"
if command_exists flake8; then
    if find addons -name '*.py' -type f | xargs flake8 --max-line-length=88 --extend-ignore=E203,E501,W503 2>/dev/null; then
        echo -e "${GREEN}✓${NC} No flake8 issues found"
    else
        echo -e "${YELLOW}⚠${NC} Flake8 found some issues"
    fi
else
    echo -e "${YELLOW}⚠${NC} flake8 not available"
fi
echo ""

# Test 5: Pylint for Odoo
echo "Test 5: Pylint-Odoo"
echo "-------------------"
if python3 -m pip show pylint-odoo > /dev/null 2>&1; then
    if find addons -name '*.py' -not -path '*/tests/*' -type f | head -10 | xargs pylint --load-plugins=pylint_odoo -d all -e odoolint 2>/dev/null; then
        echo -e "${GREEN}✓${NC} No pylint-odoo issues found (sample check)"
    else
        echo -e "${YELLOW}⚠${NC} Pylint-odoo found some issues"
    fi
else
    echo -e "${YELLOW}⚠${NC} pylint-odoo not available"
    echo "  Install: pip install pylint-odoo"
fi
echo ""

# Test 6: Bandit security scan
echo "Test 6: Security Scan (Bandit)"
echo "------------------------------"
if command_exists bandit; then
    if find addons -name '*.py' -not -path '*/tests/*' -type f | head -20 | xargs bandit -ll 2>/dev/null; then
        echo -e "${GREEN}✓${NC} No security issues found (sample check)"
    else
        echo -e "${YELLOW}⚠${NC} Bandit found potential security issues"
    fi
else
    echo -e "${YELLOW}⚠${NC} bandit not available"
fi
echo ""

# Test 7: Check for common issues
echo "Test 7: Common Issues Check"
echo "---------------------------"

# Check for TODO/FIXME comments
TODO_COUNT=$(find addons -name '*.py' -type f -exec grep -l "TODO\|FIXME" {} \; 2>/dev/null | wc -l)
if [ "$TODO_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Found $TODO_COUNT files with TODO/FIXME comments"
else
    echo -e "${GREEN}✓${NC} No TODO/FIXME comments found"
fi

# Check for print statements (should use logger)
PRINT_COUNT=$(find addons -name '*.py' -not -path '*/tests/*' -type f -exec grep -l "print(" {} \; 2>/dev/null | wc -l)
if [ "$PRINT_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} Found $PRINT_COUNT files with print() statements (use logger instead)"
else
    echo -e "${GREEN}✓${NC} No print() statements found"
fi

# Check for hardcoded credentials
if find addons -name '*.py' -type f -exec grep -i "password\s*=\s*['\"]" {} \; 2>/dev/null | grep -v "TODO\|EXAMPLE" > /dev/null; then
    echo -e "${RED}✗${NC} Potential hardcoded credentials found!"
    echo "  Please review and use environment variables"
else
    echo -e "${GREEN}✓${NC} No obvious hardcoded credentials found"
fi

echo ""

# Summary
echo "============================================"
echo "Quality Check Summary"
echo "============================================"
echo ""
echo "Auto-fix commands:"
echo "  black addons --line-length=88"
echo "  isort addons --profile=black"
echo ""
echo "Full check commands:"
echo "  pre-commit run --all-files"
echo "  flake8 addons --max-line-length=88"
echo "  pylint --load-plugins=pylint_odoo -d all -e odoolint addons"
echo ""
echo "For CI/CD integration, see:"
echo "  .github/workflows/quality.yml"
echo ""

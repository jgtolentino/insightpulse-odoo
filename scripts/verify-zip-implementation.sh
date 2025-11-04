#!/bin/bash
# Verification script for zip file implementation
# Generated: 2025-11-04
# Purpose: Verify that all content from zip files has been properly implemented

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "================================================"
echo "Zip Files Implementation Verification"
echo "================================================"
echo ""

# Change to repository root
cd "$(dirname "$0")/.."

total_checks=0
passed_checks=0
failed_checks=0

# Function to check if file/directory exists
check_exists() {
    local path="$1"
    local description="$2"
    
    total_checks=$((total_checks + 1))
    
    if [ -e "$path" ]; then
        echo -e "${GREEN}✓${NC} $description"
        echo "  Location: $path"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $description"
        echo "  Expected: $path"
        failed_checks=$((failed_checks + 1))
        return 1
    fi
}

# Function to check symlink
check_symlink() {
    local link="$1"
    local description="$2"
    
    total_checks=$((total_checks + 1))
    
    if [ -L "$link" ] && [ -e "$link" ]; then
        target=$(readlink "$link")
        echo -e "${GREEN}✓${NC} $description"
        echo "  Link: $link -> $target"
        passed_checks=$((passed_checks + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $description"
        echo "  Expected symlink: $link"
        failed_checks=$((failed_checks + 1))
        return 1
    fi
}

echo "=== Claude Skills (from files 48, 49, odoomate.zip) ==="
echo ""

# Check key skills
key_skills=(
    "reddit-product-viability"
    "odoo-knowledge-agent"
    "firecrawl-data-extraction"
    "bir-tax-filing"
    "odoo-app-automator-final"
    "insightpulse_connection_manager"
    "odoo-finance-automation"
    "superset-dashboard-automation"
)

for skill in "${key_skills[@]}"; do
    check_symlink ".claude/skills/$skill" "Skill: $skill"
done

echo ""
echo "=== Skills Documentation ==="
echo ""

check_exists "docs/skills-reference/INDEX.md" "Skills index"
check_exists "docs/skills-reference/WHAT-YOU-GOT.md" "Skills overview"
check_exists "docs/skills-reference/INSTALL.md" "Skills installation guide"
check_exists "docs/skills-reference/FIRECRAWL-INTEGRATION-GUIDE.md" "Firecrawl guide"
check_exists "docs/skills-reference/WHATS-NEW-V1.1.md" "Version 1.1 changelog"

echo ""
echo "=== CI/CD Workflows (from files 53.zip) ==="
echo ""

workflows=(
    "backup-scheduler.yml"
    "deploy-mcp.yml"
    "deploy-ocr.yml"
    "deploy-odoo.yml"
    "deploy-superset.yml"
    "health-monitor.yml"
    "integration-tests.yml"
)

for workflow in "${workflows[@]}"; do
    check_exists ".github/workflows/$workflow" "Workflow: $workflow"
done

echo ""
echo "=== Scripts (from files 53.zip) ==="
echo ""

scripts=(
    "backup.sh"
    "health-check.sh"
    "restore.sh"
    "rollback.sh"
    "quick-setup.sh"
)

for script in "${scripts[@]}"; do
    if check_exists "scripts/$script" "Script: $script"; then
        # Check if executable
        if [ -x "scripts/$script" ]; then
            echo -e "  ${GREEN}Executable: Yes${NC}"
        else
            echo -e "  ${YELLOW}Executable: No${NC}"
        fi
    fi
done

echo ""
echo "=== Superset Documentation ==="
echo ""

check_exists "docs/claude-code-skills/community/superset-dashboard-automation/SKILL.md" "Superset automation skill"

echo ""
echo "================================================"
echo "Verification Summary"
echo "================================================"
echo ""
echo "Total checks: $total_checks"
echo -e "${GREEN}Passed: $passed_checks${NC}"
echo -e "${RED}Failed: $failed_checks${NC}"

if [ $failed_checks -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "All content from zip files has been successfully implemented."
    echo "You can safely remove the zip files using: ./scripts/cleanup-zip-files.sh"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some checks failed${NC}"
    echo ""
    echo "Some expected files are missing. Please review the failures above."
    echo "Refer to ZIP_FILES_IMPLEMENTATION_REPORT.md for expected locations."
    exit 1
fi

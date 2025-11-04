#!/bin/bash
# Cleanup script for implemented zip files
# Generated: 2025-11-04
# Purpose: Remove zip files whose contents are already implemented in the repository

set -e  # Exit on error

echo "================================================"
echo "Zip Files Cleanup Script"
echo "================================================"
echo ""
echo "This script will remove zip files that have been"
echo "successfully extracted and implemented in the repository."
echo ""
echo "Refer to ZIP_FILES_IMPLEMENTATION_REPORT.md for details."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to safely remove a file
safe_remove() {
    local file="$1"
    local reason="$2"
    
    if [ -f "$file" ]; then
        echo -e "${YELLOW}Checking: $file${NC}"
        echo "  Reason: $reason"
        echo -n "  Remove? (y/N): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            rm "$file"
            echo -e "  ${GREEN}✓ Removed${NC}"
        else
            echo -e "  ${RED}✗ Skipped${NC}"
        fi
        echo ""
    else
        echo -e "${RED}File not found: $file${NC}"
        echo ""
    fi
}

# Change to repository root
cd "$(dirname "$0")/.."

echo "Current directory: $(pwd)"
echo ""
echo "Files to be reviewed:"
echo "---------------------"

# List all zip files
echo ""
echo "Zip files in repository:"
find . -maxdepth 1 -name "*.zip" -type f | while read -r file; do
    size=$(du -h "$file" | cut -f1)
    echo "  - $file ($size)"
done
echo ""

echo "================================================"
echo "Starting cleanup process..."
echo "================================================"
echo ""

# Remove implemented zip files
echo "=== IMPLEMENTED FILES (Safe to Remove) ==="
echo ""

safe_remove "files (48).zip" "Skills and documentation already in docs/skills-reference/"
safe_remove "files (49).zip" "Skills already installed in .claude/skills/"
safe_remove "odoomate.zip" "Duplicate of files (49).zip - same content"
safe_remove "files (53).zip" "CI/CD workflows and scripts already in .github/ and scripts/"
safe_remove "superset-dashboard-automation-v2-droplets.zip" "Core SKILL.md already installed"

echo "=== FILES REQUIRING DECISION ==="
echo ""

# Files that need a decision
echo -e "${YELLOW}files (50).zip${NC} - SAP Integration Templates (26 KB)"
echo "  Status: NOT YET IMPLEMENTED"
echo "  Options:"
echo "    1. Extract to docs/integrations/sap/ if SAP integration is planned"
echo "    2. Remove if SAP integration is not in scope"
echo -n "  Action (extract/remove/skip): "
read -r sap_action

case "$sap_action" in
    extract)
        echo "  Extracting to docs/integrations/sap/"
        mkdir -p docs/integrations/sap
        unzip -q "files (50).zip" -d docs/integrations/sap/
        rm "files (50).zip"
        echo -e "  ${GREEN}✓ Extracted and removed${NC}"
        ;;
    remove)
        rm "files (50).zip"
        echo -e "  ${GREEN}✓ Removed${NC}"
        ;;
    *)
        echo -e "  ${RED}✗ Skipped${NC}"
        ;;
esac
echo ""

echo -e "${YELLOW}odoomation-saas-parity-scaffold.zip${NC} - Scaffold Template (9 KB)"
echo "  Status: REFERENCE TEMPLATE"
echo "  Options:"
echo "    1. Extract to docs/templates/ for reference"
echo "    2. Remove if not needed"
echo -n "  Action (extract/remove/skip): "
read -r scaffold_action

case "$scaffold_action" in
    extract)
        echo "  Extracting to docs/templates/"
        mkdir -p docs/templates
        unzip -q "odoomation-saas-parity-scaffold.zip" -d docs/templates/
        rm "odoomation-saas-parity-scaffold.zip"
        echo -e "  ${GREEN}✓ Extracted and removed${NC}"
        ;;
    remove)
        rm "odoomation-saas-parity-scaffold.zip"
        echo -e "  ${GREEN}✓ Removed${NC}"
        ;;
    *)
        echo -e "  ${RED}✗ Skipped${NC}"
        ;;
esac
echo ""

echo "================================================"
echo "Cleanup Summary"
echo "================================================"
echo ""

# Show remaining zip files
remaining=$(find . -maxdepth 1 -name "*.zip" -type f | wc -l)
if [ "$remaining" -eq 0 ]; then
    echo -e "${GREEN}✓ No zip files remaining in root directory${NC}"
else
    echo -e "${YELLOW}⚠ $remaining zip file(s) remaining:${NC}"
    find . -maxdepth 1 -name "*.zip" -type f
fi

echo ""
echo "================================================"
echo "Next Steps:"
echo "================================================"
echo "1. Review ZIP_FILES_IMPLEMENTATION_REPORT.md for details"
echo "2. Update .gitignore to prevent future zip commits"
echo "3. Commit changes to repository"
echo ""
echo "To prevent future zip commits, add to .gitignore:"
echo "  *.zip"
echo "  !addons/**/*.zip  # Allow test data zips"
echo ""

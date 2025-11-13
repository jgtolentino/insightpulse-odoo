#!/bin/bash
# scripts/detect_conflicts.sh
# Safe merge conflict detection - reports but does NOT auto-delete

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔍 Scanning for merge conflict markers..."
echo ""

CONFLICT_FOUND=0
CONFLICT_FILES=()

# Search common file types
FILE_PATTERNS=(
    "*.py"
    "*.xml"
    "*.js"
    "*.ts"
    "*.jsx"
    "*.tsx"
    "*.yaml"
    "*.yml"
    "*.json"
    "*.md"
    "*.rst"
    "*.txt"
    "*.sh"
)

for pattern in "${FILE_PATTERNS[@]}"; do
    while IFS= read -r -d '' file; do
        # Skip node_modules, .git, and other common directories
        if [[ "$file" =~ (node_modules|\.git|__pycache__|\.venv|venv|build|dist) ]]; then
            continue
        fi

        if grep -q "^<<<<<<< " "$file" 2>/dev/null; then
            CONFLICT_FOUND=1
            CONFLICT_FILES+=("$file")

            echo -e "${RED}❌ Merge conflict found in: $file${NC}"

            # Show the conflict context
            echo -e "${YELLOW}Context:${NC}"
            grep -n -A2 -B2 "^<<<<<<< " "$file" | head -20
            echo ""
        fi
    done < <(find . -type f -name "$pattern" -print0 2>/dev/null)
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $CONFLICT_FOUND -eq 1 ]; then
    echo -e "${RED}❌ CONFLICT DETECTION FAILED${NC}"
    echo ""
    echo "Found unresolved merge conflicts in ${#CONFLICT_FILES[@]} file(s):"
    for file in "${CONFLICT_FILES[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "⚠️  Please resolve these conflicts manually before committing."
    echo ""
    echo "To resolve:"
    echo "  1. Open each file"
    echo "  2. Search for <<<<<<< markers"
    echo "  3. Choose the correct version"
    echo "  4. Remove all conflict markers (<<<<<<< =======  >>>>>>>)"
    echo "  5. Test your changes"
    echo "  6. Commit"
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ No merge conflicts detected${NC}"
    echo ""
    exit 0
fi

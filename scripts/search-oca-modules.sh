#!/bin/bash
# OCA Module Search Tool
# Search OCA repositories for relevant modules

set -euo pipefail

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

KEYWORDS=""
VERSION="19.0"
OUTPUT_FORMAT="table"
TOKEN="${GITHUB_TOKEN:-}"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --keywords)
            KEYWORDS="$2"
            shift 2
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --format)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 --keywords KEYWORDS [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --keywords KEYWORDS  Search keywords, comma-separated"
            echo "  --version VERSION    Odoo version (default: 19.0)"
            echo "  --format FORMAT      Output format: table|json|csv (default: table)"
            echo ""
            echo "Environment:"
            echo "  GITHUB_TOKEN         GitHub token (optional, increases rate limits)"
            echo ""
            echo "Example:"
            echo "  $0 --keywords \"expense,approval,travel\" --format table"
            echo "  GITHUB_TOKEN=ghp_xxx $0 --keywords \"expense\" --format json"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$KEYWORDS" ]; then
    echo "Error: --keywords is required"
    exit 1
fi

echo -e "${GREEN}🔍 Searching OCA modules for: $KEYWORDS${NC}"
echo "=========================================="

# Convert keywords to array
IFS=',' read -ra KEYWORD_ARRAY <<< "$KEYWORDS"

# OCA repositories to search
OCA_REPOS=(
    "account-financial-reporting"
    "account-financial-tools"
    "account-invoicing"
    "bank-payment"
    "connector"
    "hr"
    "l10n-spain"
    "l10n-brazil"
    "manufacturing"
    "mis-builder"
    "reporting-engine"
    "sale-workflow"
    "server-backend"
    "server-tools"
    "stock-logistics-workflow"
)

echo -e "${BLUE}📦 Searching OCA repositories...${NC}"
echo ""

# Create temporary file for results
RESULTS=$(mktemp)

# Search GitHub API
for repo in "${OCA_REPOS[@]}"; do
    url="https://api.github.com/repos/OCA/${repo}/contents"
    auth_args=()
    [[ -n "$TOKEN" ]] && auth_args=(-H "Authorization: Bearer $TOKEN")

    # List top-level directories
    dirs=$(curl -sSL "${auth_args[@]}" "${url}" 2>/dev/null | jq -r '.[] | select(.type=="dir") | .name' 2>/dev/null || echo "")

    [[ -z "$dirs" ]] && continue

    while IFS= read -r module; do
        [[ -z "$module" ]] && continue

        # Get manifest
        manifest_url="https://raw.githubusercontent.com/OCA/${repo}/${VERSION}/${module}/__manifest__.py"
        manifest=$(curl -sSL "$manifest_url" 2>/dev/null || true)

        [[ -z "$manifest" ]] && continue

        # Parse with Python for accuracy
        name=$(python3 - <<PY 2>/dev/null
import ast, sys
s=sys.stdin.read()
try:
 d=ast.literal_eval(s)
 print(d.get('name',''))
except Exception:
 pass
PY
 <<<"$manifest")

        summary=$(python3 - <<PY 2>/dev/null
import ast, sys
s=sys.stdin.read()
try:
 d=ast.literal_eval(s)
 print(d.get('summary','').replace(',', ';'))
except Exception:
 pass
PY
 <<<"$manifest")

        installable=$(python3 - <<PY 2>/dev/null
import ast, sys
s=sys.stdin.read()
try:
 d=ast.literal_eval(s)
 print(str(d.get('installable',True)))
except Exception:
 print('True')
PY
 <<<"$manifest")

        # Filter by keywords
        match=false
        for keyword in "${KEYWORD_ARRAY[@]}"; do
            keyword=$(echo "$keyword" | tr -d ' ')
            if [[ "$name" =~ $keyword ]] || [[ "$summary" =~ $keyword ]] || [[ "$module" =~ $keyword ]]; then
                match=true
                break
            fi
        done

        if [[ "$match" == true ]] && [[ "$installable" == "True" ]]; then
            [ -z "$summary" ] && summary="No summary"
            echo "${repo}|${module}|${summary}|https://github.com/OCA/${repo}/tree/${VERSION}/${module}" >> "$RESULTS"
        fi
    done <<< "$dirs"
done

# Display results
if [ ! -s "$RESULTS" ]; then
    echo -e "${YELLOW}⚠️  No modules found${NC}"
    rm "$RESULTS"
    exit 0
fi

# Remove duplicates
sort -u "$RESULTS" -o "$RESULTS"

echo -e "${GREEN}✅ Found $(wc -l < "$RESULTS") modules${NC}"
echo ""

# Output based on format
case "$OUTPUT_FORMAT" in
    table)
        echo -e "${BLUE}Repository          | Module                      | Summary${NC}"
        echo "-------------------|-----------------------------|---------------------------------"
        while IFS='|' read -r repo module summary url; do
            printf "%-18s | %-27s | %-50s\n" "$repo" "$module" "$summary"
        done < "$RESULTS"
        ;;

    json)
        echo "["
        first=true
        while IFS='|' read -r repo module summary url; do
            if [ "$first" = true ]; then
                first=false
            else
                echo ","
            fi
            cat << EOF
  {
    "repository": "$repo",
    "module": "$module",
    "summary": "$summary",
    "url": "$url",
    "version": "$VERSION"
  }
EOF
        done < "$RESULTS"
        echo ""
        echo "]"
        ;;

    csv)
        echo "Repository,Module,Summary,URL,Version"
        while IFS='|' read -r repo module summary url; do
            echo "\"$repo\",\"$module\",\"$summary\",\"$url\",\"$VERSION\""
        done < "$RESULTS"
        ;;
esac

echo ""
echo -e "${BLUE}💡 To install OCA modules:${NC}"
echo "  1. Add to requirements.txt: git+https://github.com/OCA/[repo]@${VERSION}#subdirectory=[module]"
echo "  2. Or clone: git clone -b ${VERSION} https://github.com/OCA/[repo] addons/oca/[repo]"

rm "$RESULTS"

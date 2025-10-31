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
            echo "Example:"
            echo "  $0 --keywords \"expense,approval,travel\""
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
    "account-financial-tools"
    "account-invoicing"
    "bank-payment"
    "hr"
    "project"
    "sale-workflow"
    "purchase-workflow"
    "web"
    "server-tools"
    "reporting-engine"
)

echo -e "${BLUE}📦 Searching OCA repositories...${NC}"
echo ""

# Create temporary file for results
RESULTS=$(mktemp)

# Search GitHub API
for repo in "${OCA_REPOS[@]}"; do
    for keyword in "${KEYWORD_ARRAY[@]}"; do
        keyword=$(echo "$keyword" | tr -d ' ')

        # Search GitHub API
        response=$(curl -s "https://api.github.com/search/code?q=${keyword}+repo:OCA/${repo}+filename:__manifest__.py" 2>/dev/null || echo "")

        if [ -n "$response" ]; then
            # Parse JSON and extract module names
            modules=$(echo "$response" | jq -r '.items[]? | .path' 2>/dev/null | sed 's|/__manifest__.py||' || echo "")

            if [ -n "$modules" ]; then
                while IFS= read -r module; do
                    # Get manifest content to check version
                    manifest_url="https://raw.githubusercontent.com/OCA/${repo}/${VERSION}/${module}/__manifest__.py"
                    manifest=$(curl -s "$manifest_url" 2>/dev/null || echo "")

                    if [[ "$manifest" == *"'version'"* ]] || [[ "$manifest" == *'"version"'* ]]; then
                        installable=$(echo "$manifest" | grep -i "installable" | grep -i "true" || echo "")

                        if [ -n "$installable" ]; then
                            # Extract summary
                            summary=$(echo "$manifest" | grep -i "summary" | sed "s/.*['\"]\(.*\)['\"]/\1/" | head -1)
                            [ -z "$summary" ] && summary="No summary"

                            # Save result
                            echo "${repo}|${module}|${summary}|https://github.com/OCA/${repo}/tree/${VERSION}/${module}" >> "$RESULTS"
                        fi
                    fi
                done <<< "$modules"
            fi
        fi
    done
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

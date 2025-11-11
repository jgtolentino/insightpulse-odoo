#!/bin/bash
# CI/CD Skill Runner
# Executes skill profiles with proper error handling and exit codes

set -e

# Configuration
REPO_PATH="${REPO_PATH:-.}"
PROFILE="${SKILL_PROFILE:-fast_check}"
OUTPUT_FORMAT="${OUTPUT_FORMAT:-json}"
FAIL_ON_VIOLATIONS="${FAIL_ON_VIOLATIONS:-true}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "============================================"
echo "InsightPulse AI - Skills CI Runner"
echo "============================================"
echo "Profile: $PROFILE"
echo "Repo Path: $REPO_PATH"
echo "Output Format: $OUTPUT_FORMAT"
echo "============================================"
echo ""

# Run skill profile
if [ "$OUTPUT_FORMAT" = "json" ]; then
    python3 -m agents.run_skill \
        --profile "$PROFILE" \
        --repo-path "$REPO_PATH" \
        --json > skill_results.json

    # Check if results exist
    if [ ! -f "skill_results.json" ]; then
        echo -e "${RED}❌ Error: skill_results.json not found${NC}"
        exit 2
    fi

    # Display results
    echo "Results saved to skill_results.json"
    cat skill_results.json

    # Parse results for violations (if jq is available)
    if command -v jq &> /dev/null; then
        violations=$(jq '.results | to_entries[] | select(.value != 0) | length' skill_results.json 2>/dev/null || echo "0")

        if [ "$violations" -gt 0 ] && [ "$FAIL_ON_VIOLATIONS" = "true" ]; then
            echo -e "${RED}❌ Found violations. Exiting with code 1${NC}"
            exit 1
        else
            echo -e "${GREEN}✅ All checks passed${NC}"
            exit 0
        fi
    else
        echo "⚠️  jq not found, skipping result parsing"
        exit 0
    fi
else
    # Human-readable output
    python3 -m agents.run_skill \
        --profile "$PROFILE" \
        --repo-path "$REPO_PATH"

    exit_code=$?

    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ All checks passed${NC}"
    elif [ $exit_code -eq 1 ]; then
        echo -e "${YELLOW}⚠️  Violations found${NC}"
    else
        echo -e "${RED}❌ Critical errors detected${NC}"
    fi

    exit $exit_code
fi

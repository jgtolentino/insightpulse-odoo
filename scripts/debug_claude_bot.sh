#!/bin/bash
#
# Claude Bot Diagnostic Script
# Identifies why @claude failed on PR #64
#

set -e

echo "========================================="
echo "  Claude Bot Diagnostics for PR #64"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check 1: Workflow file exists
echo "Check 1: Workflow file exists"
if [ -f .github/workflows/claude-autofix-bot.yml ]; then
    echo -e "${GREEN}✓${NC} Workflow file found"
else
    echo -e "${RED}✗${NC} Workflow file NOT found"
    exit 1
fi
echo ""

# Check 2: API Key Secret
echo "Check 2: ANTHROPIC_API_KEY secret"
if gh secret list | grep -q ANTHROPIC_API_KEY; then
    echo -e "${GREEN}✓${NC} ANTHROPIC_API_KEY secret is set"
else
    echo -e "${RED}✗${NC} ANTHROPIC_API_KEY secret NOT found"
    echo ""
    echo "FIX: Run the following command:"
    echo "  gh secret set ANTHROPIC_API_KEY"
    echo ""
    echo "Get your API key from: https://console.anthropic.com/settings/keys"
    echo ""
    exit 1
fi
echo ""

# Check 3: Workflow permissions
echo "Check 3: Workflow permissions"
PERMS=$(gh api repos/jgtolentino/insightpulse-odoo/actions/permissions 2>/dev/null | jq -r '.default_workflow_permissions' || echo "unknown")
if [ "$PERMS" = "write" ]; then
    echo -e "${GREEN}✓${NC} Workflow has write permissions"
elif [ "$PERMS" = "read" ]; then
    echo -e "${RED}✗${NC} Workflow only has read permissions"
    echo ""
    echo "FIX:"
    echo "1. Go to: https://github.com/jgtolentino/insightpulse-odoo/settings/actions"
    echo "2. Under 'Workflow permissions', select: 'Read and write permissions'"
    echo "3. Check: 'Allow GitHub Actions to create and approve pull requests'"
    echo "4. Click 'Save'"
    echo ""
else
    echo -e "${YELLOW}?${NC} Could not determine permissions (might need manual check)"
fi
echo ""

# Check 4: Recent workflow runs
echo "Check 4: Recent workflow runs"
echo ""
gh run list --workflow=claude-autofix-bot.yml --limit 5 --json conclusion,createdAt,event,displayTitle,databaseId 2>/dev/null | \
    jq -r '.[] | "\(.conclusion // "in_progress") | \(.createdAt) | \(.displayTitle) | Run ID: \(.databaseId)"' || \
    echo -e "${YELLOW}Could not fetch recent runs${NC}"
echo ""

# Check 5: Get last failed run details
echo "Check 5: Last failed run (if any)"
echo ""
LAST_FAILED=$(gh run list --workflow=claude-autofix-bot.yml --status failure --limit 1 --json databaseId -q '.[0].databaseId' 2>/dev/null || echo "")

if [ -n "$LAST_FAILED" ]; then
    echo -e "${YELLOW}Found failed run: $LAST_FAILED${NC}"
    echo ""
    echo "View full logs with:"
    echo "  gh run view $LAST_FAILED --log-failed"
    echo ""
    echo "Fetching error summary..."
    gh run view $LAST_FAILED --log-failed 2>/dev/null | tail -50 || echo "Could not fetch logs"
else
    echo -e "${GREEN}No failed runs found (or bot never triggered)${NC}"
fi
echo ""

# Check 6: PR #64 details
echo "Check 6: PR #64 details"
echo ""
gh pr view 64 --json title,number,changedFiles,additions,deletions 2>/dev/null | \
    jq -r '"Title: \(.title)\nFiles changed: \(.changedFiles)\nAdditions: +\(.additions)\nDeletions: -\(.deletions)"' || \
    echo -e "${YELLOW}Could not fetch PR details${NC}"
echo ""

# Check 7: PR comments for @claude mentions
echo "Check 7: Recent comments on PR #64"
echo ""
gh pr view 64 --json comments 2>/dev/null | \
    jq -r '.comments[-3:] | .[] | "[\(.createdAt)] @\(.author.login): \(.body | split("\n")[0])"' || \
    echo -e "${YELLOW}Could not fetch PR comments${NC}"
echo ""

echo "========================================="
echo "  Diagnostics Complete"
echo "========================================="
echo ""
echo "SUMMARY:"
echo ""
echo "If ANTHROPIC_API_KEY is missing, fix with:"
echo "  gh secret set ANTHROPIC_API_KEY"
echo ""
echo "If permissions are wrong, visit:"
echo "  https://github.com/jgtolentino/insightpulse-odoo/settings/actions"
echo ""
echo "Once fixed, test on PR #64 by commenting:"
echo "  @claude review"
echo ""

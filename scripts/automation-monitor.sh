#!/bin/bash
#
# Automation Monitoring Script
# Tracks automation statistics and Notion sync status
#
# Usage: ./scripts/automation-monitor.sh
#

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ADDONS_PATH="$PROJECT_ROOT/addons"
LOG_FILE="$PROJECT_ROOT/automation.log"
TIMESTAMP_FILE="$PROJECT_ROOT/.last_automation_run"

# Header
echo ""
echo "========================================="
echo "📊 Automation Statistics"
echo "========================================="
echo ""

# Count generated modules
echo -e "${BLUE}📦 Module Statistics:${NC}"
if [ -d "$ADDONS_PATH" ]; then
    MODULE_COUNT=$(find "$ADDONS_PATH" -maxdepth 1 -type d -name "ipai_*" | wc -l)
    echo "  Total InsightPulse Modules: $MODULE_COUNT"

    # Count by category
    FINANCE_COUNT=$(find "$ADDONS_PATH" -maxdepth 1 -type d -name "ipai_*" -exec grep -l "Accounting/Finance" {}/__ manifest__.py \; 2>/dev/null | wc -l)
    OPS_COUNT=$(find "$ADDONS_PATH" -maxdepth 1 -type d -name "ipai_*" -exec grep -l "Operations" {}/__ manifest__.py \; 2>/dev/null | wc -l)

    echo "  Finance modules: $FINANCE_COUNT"
    echo "  Operations modules: $OPS_COUNT"
else
    echo "  Addons directory not found"
fi

echo ""

# Last run timestamp
echo -e "${BLUE}⏰ Last Run Information:${NC}"
if [ -f "$TIMESTAMP_FILE" ]; then
    LAST_RUN=$(cat "$TIMESTAMP_FILE")
    echo "  Last automation run: $LAST_RUN"

    # Calculate time since last run
    LAST_RUN_EPOCH=$(date -d "$LAST_RUN" +%s 2>/dev/null || echo 0)
    NOW_EPOCH=$(date +%s)
    DIFF_HOURS=$(( (NOW_EPOCH - LAST_RUN_EPOCH) / 3600 ))

    echo "  Hours since last run: $DIFF_HOURS"
else
    echo "  No automation runs recorded yet"
fi

# Update timestamp
date > "$TIMESTAMP_FILE"

echo ""

# Notion sync status
echo -e "${BLUE}🔄 Notion Sync Status:${NC}"
echo "  Querying Notion database..."

if command -v cn &> /dev/null; then
    # Query Notion for status counts
    cn << 'EOF' 2>/dev/null || echo "  Failed to connect to Notion"
Query my Notion Feature Requests database and provide counts by status:
- To Do
- Ready for Development
- In Development
- Testing
- Done

Output format:
Status | Count
-------|------
To Do  | X
Ready  | X
In Dev | X
...
EOF
else
    echo "  Continue CLI not installed"
    echo "  Install with: npm i -g @continuedev/cli"
fi

echo ""

# Recent log entries
echo -e "${BLUE}📝 Recent Activity:${NC}"
if [ -f "$LOG_FILE" ]; then
    echo "  Last 5 log entries:"
    tail -5 "$LOG_FILE" | sed 's/^/    /'
else
    echo "  No log file found"
fi

echo ""

# Git status
echo -e "${BLUE}📂 Git Status:${NC}"
cd "$PROJECT_ROOT"
if git rev-parse --git-dir > /dev/null 2>&1; then
    # Count uncommitted changes
    CHANGED_FILES=$(git status --porcelain | wc -l)
    echo "  Uncommitted changes: $CHANGED_FILES files"

    if [ $CHANGED_FILES -gt 0 ]; then
        echo ""
        echo "  Modified files:"
        git status --short | head -10 | sed 's/^/    /'

        if [ $CHANGED_FILES -gt 10 ]; then
            echo "    ... and $((CHANGED_FILES - 10)) more"
        fi
    fi

    # Recent commits
    echo ""
    echo "  Recent commits:"
    git log --oneline -5 | sed 's/^/    /'
else
    echo "  Not a git repository"
fi

echo ""

# System resources
echo -e "${BLUE}💻 System Resources:${NC}"
if command -v free &> /dev/null; then
    MEMORY_USAGE=$(free -h | awk '/^Mem:/ {print $3 "/" $2}')
    echo "  Memory usage: $MEMORY_USAGE"
fi

if command -v df &> /dev/null; then
    DISK_USAGE=$(df -h "$PROJECT_ROOT" | awk 'NR==2 {print $3 "/" $2 " (" $5 ")"}')
    echo "  Disk usage: $DISK_USAGE"
fi

echo ""

# Health checks
echo -e "${BLUE}🏥 Health Checks:${NC}"

# Check Continue CLI config
if [ -f "$HOME/.continue/config.json" ]; then
    echo "  ✅ Continue CLI configured"
else
    echo "  ❌ Continue CLI not configured"
fi

# Check environment variables
ENV_VARS=("NOTION_API_KEY" "ANTHROPIC_API_KEY" "SUPABASE_URL")
for var in "${ENV_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        echo "  ✅ $var is set"
    else
        echo "  ⚠️  $var not set"
    fi
done

echo ""

# Recommendations
echo -e "${YELLOW}💡 Recommendations:${NC}"

if [ $CHANGED_FILES -gt 0 ]; then
    echo "  • Commit and push your changes"
fi

if ! command -v cn &> /dev/null; then
    echo "  • Install Continue CLI: npm i -g @continuedev/cli"
fi

if [ ! -f "$HOME/.continue/config.json" ]; then
    echo "  • Configure Continue CLI with your API keys"
fi

# Calculate modules generated per week
if [ -f "$TIMESTAMP_FILE" ]; then
    WEEKS_ACTIVE=$(( DIFF_HOURS / 168 + 1 ))
    MODULES_PER_WEEK=$(( MODULE_COUNT / WEEKS_ACTIVE ))
    echo "  • Average: $MODULES_PER_WEEK modules per week"
fi

echo ""
echo "========================================="
echo "Monitor complete: $(date)"
echo "========================================="
echo ""

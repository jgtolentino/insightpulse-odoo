#!/bin/bash
# Archive old InsightPulse repositories that have been consolidated into insightpulse-odoo

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🗂️  Repository Archiving Script"
echo "================================"
echo ""

# List of repositories to archive (old InsightPulse-related repos)
REPOS_TO_ARCHIVE=(
  # Old Odoo projects (consolidated into insightpulse-odoo)
  "ipai-odoo"
  "finance-automation"
  "odoobo-fin-ops"
  "odoo-erp"
  "odoobo-backend-repo"
  "odoobo-ocean"
  "odoboo-workspace"

  # Old Notion experiments
  "next-notion-supabase"
  "react-notion-x"
  "nextjs-notion-starter-kit"
  "notion-clone"
  "notion"

  # Forks no longer needed
  "oca"

  # Old tools/generators
  "odoo-spark-generator"

  # Old rate card systems
  "rate-inquiry---approval-system"
  "rate-card"
  "rate-card-729"

  # Inactive infrastructure
  "scout-analytics-prod"
  "ai-aas-hardened-lakehouse"
  "Scout-Dashboard"
  "render-mcp-bridge"
  "openai-ui"

  # Old Scout experiments
  "scout-agentic-analytics"
  "apps-scout-dashboard"
  "scout-dashboard-clean"
  "scout-v7"
  "scout-analytics-clean"
  "tbwa-scout-dashboard"

  # Old SpendFlow/Expense systems
  "concur-ui-revive"
  "app-expense"
  "tbwa-concur-expense-app"
  "ios-expense"
  "SpendFlow-Web"
  "spendflow-db"
  "concur-buddy"
  "mobile-expense---ca-app"

  # Old SUQI experiments
  "suqi-agentic-ai"
  "suqi-public"
  "suqi-analytics"
  "suqi-agentic-db"
  "agentic-suqi"
  "ai-agentic-analytics"
  "suqi-ai"
  "scout-suqi-ship"
  "Scout-Analytics-Dashboard-Suqi"
  "edge-suqi-pie"
  "suqi-face"
  "chartvision"
  "Suqi-Supa-db"
  "supa-love"
  "supa-love-db"
  "gen-bi-nw"
  "tab-ai"
  "suqi-gen-bi"
  "tableau-insight-ai"
  "pulser-ai-bi"
  "suqi-ai-db"
  "suqi-ai-dashboard-"
  "geographic-dashboard"

  # Old agency projects
  "tbwa-agency-databank"
  "tbwa-lions-palette-forge"
  "amazing-awards"

  # Other experimental/inactive
  "chatgpt-plugin-server"
  "expenseflow-claudescribe"
  "builderio-shopify-commerce-headless"
  "specflow"
  "onelink"
  "v0-i-os-on-the-web"
  # "dataintelligence-ph"  # KEEP ACTIVE - Active project
  "my-site-4"
  "ios-design-essence"
  "insightpulse-app"
  "w9-studios-landing-page"
  "w9-coming-soon"
  "W9-landing"
  "w9studio"
  "ai-studios-landing-page"
  "auto-brand"
  "standalone-dashboard"
  "test-coke"
  "Suki-intel-scout-platform-v5"
  "scout-databank-isolated"
  "neural-docs"
  "mockify-creator"
  "webapp_pulse"
  "scout-analytics-blueprint-doc"
  "map"
)

# Dry run by default
DRY_RUN=true

if [ "$1" == "--execute" ]; then
  DRY_RUN=false
  echo -e "${RED}⚠️  EXECUTION MODE ENABLED - Will actually archive repositories${NC}"
  echo ""
  read -p "Are you sure you want to proceed? (yes/no): " confirm
  if [ "$confirm" != "yes" ]; then
    echo "Aborted."
    exit 0
  fi
else
  echo -e "${YELLOW}🔍 DRY RUN MODE - No changes will be made${NC}"
  echo "Run with --execute to actually archive repositories"
  echo ""
fi

# Function to archive a repository
archive_repo() {
  local repo=$1
  local owner="jgtolentino"

  if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}[DRY RUN]${NC} Would archive: $owner/$repo"
  else
    echo -e "${GREEN}Archiving:${NC} $owner/$repo"
    if gh repo archive "$owner/$repo" --yes; then
      echo -e "${GREEN}✅ Successfully archived:${NC} $repo"
    else
      echo -e "${RED}❌ Failed to archive:${NC} $repo"
    fi
  fi
}

# Archive each repository
echo "Repositories to archive:"
echo "========================"
for repo in "${REPOS_TO_ARCHIVE[@]}"; do
  echo "  - $repo"
done
echo ""

for repo in "${REPOS_TO_ARCHIVE[@]}"; do
  archive_repo "$repo"
  sleep 1  # Rate limiting
done

echo ""
echo "================================"
if [ "$DRY_RUN" = true ]; then
  echo -e "${GREEN}✅ Dry run complete${NC}"
  echo "Review the list above and run with --execute to proceed"
else
  echo -e "${GREEN}✅ Archiving complete${NC}"
  echo "Archived repositories are now read-only"
fi

#!/bin/bash
# Workflow Consolidation Script
# Consolidates 73 workflows down to 8 essential ones
# Date: 2025-11-09

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "GitHub Workflows Consolidation"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Essential workflows to keep
ESSENTIAL=(
  "ci-unified.yml"
  "odoo-deploy.yml"
  "deploy-superset.yml"
  "superset-postgres-guard.yml"
  "deploy-ocr.yml"
  "infrastructure-validation.yml"
  "feature-inventory.yml"
  "oca-pre-commit.yml"
)

cd "$(dirname "$0")/.."

# Count current workflows
CURRENT_COUNT=$(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)
echo "📊 Current workflows: $CURRENT_COUNT"
echo "🎯 Target workflows: ${#ESSENTIAL[@]}"
echo ""

# Create archive directory
mkdir -p .github/workflows-archive
echo "✅ Created archive directory"

# Move all workflows to archive first
echo "📦 Archiving all workflows..."
mv .github/workflows/*.yml .github/workflows-archive/ 2>/dev/null || true

# Restore essential workflows
echo "♻️  Restoring essential workflows..."
for workflow in "${ESSENTIAL[@]}"; do
  if [ -f ".github/workflows-archive/$workflow" ]; then
    mv ".github/workflows-archive/$workflow" .github/workflows/
    echo "  ✅ $workflow"
  else
    echo "  ⚠️  $workflow (not found in archive)"
  fi
done

# Count archived workflows
ARCHIVED_COUNT=$(ls -1 .github/workflows-archive/*.yml 2>/dev/null | wc -l)
ACTIVE_COUNT=$(ls -1 .github/workflows/*.yml 2>/dev/null | wc -l)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Consolidation Complete"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Active workflows: $ACTIVE_COUNT"
echo "Archived workflows: $ARCHIVED_COUNT"
echo "Reduction: $(( $CURRENT_COUNT - $ACTIVE_COUNT )) workflows removed"
echo ""
echo "Next steps:"
echo "1. Review changes: git status"
echo "2. Commit: git add .github/ && git commit -m 'ci: consolidate to 8 essential workflows'"
echo "3. Push: git push -u origin claude/review-github-workflows-011CUwdUXBoLLMnTETfQLaiS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

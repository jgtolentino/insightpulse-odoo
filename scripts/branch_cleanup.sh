#!/usr/bin/env bash
# Branch consolidation and cleanup automation for Insightpulseai/odoo
# Safe, idempotent, re-runnable GitOps script
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Insightpulseai/odoo.git}"
REPO_DIR="${REPO_DIR:-odoo}"
DRY_RUN="${DRY_RUN:-false}"
MAIN_BRANCH="${MAIN_BRANCH:-main}"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Branch Consolidation & Cleanup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Repo: $REPO_URL"
echo "Dry Run: $DRY_RUN"
echo ""

# Clone or update repo
if [ ! -d "$REPO_DIR" ]; then
  echo "📥 Cloning repository..."
  git clone "$REPO_URL" "$REPO_DIR"
fi

cd "$REPO_DIR"

# Ensure clean state
echo "🔄 Fetching all branches..."
git fetch --all --prune
git checkout "$MAIN_BRANCH"
git pull origin "$MAIN_BRANCH"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 1: Classify Branches"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# List all remote branches (excluding main and HEAD)
ALL_BRANCHES=$(git branch -r | grep -vE "origin/$MAIN_BRANCH|origin/HEAD" | sed 's|origin/||' | tr -d ' ')

if [ -z "$ALL_BRANCHES" ]; then
  echo "✅ No branches to process (only $MAIN_BRANCH exists)"
  exit 0
fi

# Temporary files for classification
MERGED_FILE=$(mktemp)
REDUNDANT_FILE=$(mktemp)
DIVERGENT_FILE=$(mktemp)
PRIORITY_MERGE_FILE=$(mktemp)

trap "rm -f $MERGED_FILE $REDUNDANT_FILE $DIVERGENT_FILE $PRIORITY_MERGE_FILE" EXIT

echo "📋 Classifying branches..."

for branch in $ALL_BRANCHES; do
  # Check if already merged
  if git branch -r --merged "origin/$MAIN_BRANCH" | grep -q "origin/$branch"; then
    echo "  ✓ Merged: $branch"
    echo "$branch" >> "$MERGED_FILE"
    continue
  fi

  # Check if redundant (no diff from main)
  if git diff --quiet "origin/$MAIN_BRANCH...origin/$branch" 2>/dev/null; then
    echo "  ≈ Redundant (no diff): $branch"
    echo "$branch" >> "$REDUNDANT_FILE"
    continue
  fi

  # Check if priority merge candidate (chore/, fix/, refactor/)
  if echo "$branch" | grep -qE '^(chore/|fix/|refactor/)'; then
    echo "  → Priority merge: $branch"
    echo "$branch" >> "$PRIORITY_MERGE_FILE"
    continue
  fi

  # Divergent (needs manual review)
  echo "  ⚠ Divergent (manual review): $branch"
  echo "$branch" >> "$DIVERGENT_FILE"
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 2: Merge Priority Branches"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -s "$PRIORITY_MERGE_FILE" ]; then
  while read -r branch; do
    echo "🔀 Merging: $branch"
    if [ "$DRY_RUN" = "false" ]; then
      git checkout "$MAIN_BRANCH"
      if git merge --no-ff "origin/$branch" -m "merge($branch): consolidate into $MAIN_BRANCH" 2>&1; then
        echo "  ✅ Merged successfully"
      else
        echo "  ⚠️  Merge conflict or error - skipping"
        git merge --abort 2>/dev/null || true
      fi
    else
      echo "  [DRY RUN] Would merge $branch"
    fi
  done < "$PRIORITY_MERGE_FILE"

  if [ "$DRY_RUN" = "false" ]; then
    echo "📤 Pushing merged changes..."
    git push origin "$MAIN_BRANCH"
  else
    echo "[DRY RUN] Would push to $MAIN_BRANCH"
  fi
else
  echo "ℹ️  No priority branches to merge"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Phase 3: Delete Redundant Branches"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Combine merged + redundant
cat "$MERGED_FILE" "$REDUNDANT_FILE" 2>/dev/null | sort -u > /tmp/delete_branches.txt || true

if [ -s /tmp/delete_branches.txt ]; then
  echo "🗑️  Deleting $(wc -l < /tmp/delete_branches.txt) branches..."
  
  while read -r branch; do
    echo "  Deleting: $branch"
    if [ "$DRY_RUN" = "false" ]; then
      if git push origin --delete "$branch" 2>&1; then
        echo "    ✅ Deleted"
      else
        echo "    ⚠️  Failed to delete (may not exist or protected)"
      fi
    else
      echo "    [DRY RUN] Would delete $branch"
    fi
  done < /tmp/delete_branches.txt

  if [ "$DRY_RUN" = "false" ]; then
    echo "🧹 Cleaning local refs..."
    git fetch --prune
  fi
else
  echo "ℹ️  No branches to delete"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Merged branches:    $(wc -l < "$MERGED_FILE" 2>/dev/null || echo 0)"
echo "Redundant branches: $(wc -l < "$REDUNDANT_FILE" 2>/dev/null || echo 0)"
echo "Priority merges:    $(wc -l < "$PRIORITY_MERGE_FILE" 2>/dev/null || echo 0)"
echo "Divergent (review): $(wc -l < "$DIVERGENT_FILE" 2>/dev/null || echo 0)"
echo ""

if [ -s "$DIVERGENT_FILE" ]; then
  echo "⚠️  Divergent branches requiring manual review:"
  cat "$DIVERGENT_FILE" | sed 's/^/  - /'
  echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Verification"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

echo "📊 Remaining remote branches:"
git branch -r | grep -vE "origin/HEAD" | wc -l

echo ""
echo "📝 Recent commits on $MAIN_BRANCH:"
git log --oneline --decorate -5

echo ""
echo "🔍 Unmerged branches (excluding divergent):"
UNMERGED=$(git branch -r --no-merged "origin/$MAIN_BRANCH" | grep -vE "origin/HEAD|origin/$MAIN_BRANCH" | wc -l)
echo "  Count: $UNMERGED"

if [ $UNMERGED -gt 0 ]; then
  git branch -r --no-merged "origin/$MAIN_BRANCH" | grep -vE "origin/HEAD|origin/$MAIN_BRANCH" | sed 's/^/  - /'
fi

echo ""
if [ "$DRY_RUN" = "true" ]; then
  echo "✅ DRY RUN COMPLETE - No changes were made"
  echo "   Re-run with DRY_RUN=false to apply changes"
else
  echo "✅ CLEANUP COMPLETE"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

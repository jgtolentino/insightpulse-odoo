#!/bin/bash
#
# Configure Git Merge Strategies
#
# This script sets up intelligent merge strategies for different file types
# to reduce conflicts and enable better automatic resolution.
#
# Features:
# - Rerere (Reuse Recorded Resolution)
# - File-type specific merge drivers
# - Conflict style configuration
# - YAML semantic merge
#
# Usage:
#   ./scripts/setup/configure-git-merge-strategies.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "🔧 Configuring Git merge strategies for repository..."
echo "Repository: $REPO_ROOT"
echo ""

cd "$REPO_ROOT"

# ============================================================================
# 1. Enable rerere (Reuse Recorded Resolution)
# ============================================================================
echo "📝 Enabling rerere (Reuse Recorded Resolution)..."

git config rerere.enabled true
git config rerere.autoupdate true

echo "   ✅ rerere enabled"
echo "   Git will remember how you resolved conflicts and reuse solutions"
echo ""

# ============================================================================
# 2. Set conflict style to diff3
# ============================================================================
echo "📝 Setting conflict style to diff3..."

git config merge.conflictstyle diff3

echo "   ✅ Conflict style set to diff3"
echo "   Conflicts will show: ours | base | theirs"
echo ""

# ============================================================================
# 3. Configure merge drivers
# ============================================================================
echo "📝 Configuring merge drivers..."

# YAML merge driver
git config merge.yaml.name "YAML semantic merge"
git config merge.yaml.driver "python .github/scripts/yaml-merge.py %O %A %B"

# Keep ours driver
git config merge.ours.name "Keep our version"
git config merge.ours.driver true

# Keep theirs driver
git config merge.theirs.name "Keep their version"
git config merge.theirs.driver "git merge-file --theirs %O %A %B"

# Union merge (combine both)
git config merge.union.name "Union merge (combine both)"
git config merge.union.driver "git merge-file --union %O %A %B"

echo "   ✅ Merge drivers configured:"
echo "      - yaml: Semantic YAML merge"
echo "      - ours: Keep our version"
echo "      - theirs: Keep their version"
echo "      - union: Combine both versions"
echo ""

# ============================================================================
# 4. Create/Update .gitattributes
# ============================================================================
echo "📝 Creating .gitattributes with merge strategies..."

cat > "$REPO_ROOT/.gitattributes" << 'EOF'
# Git Attributes - Merge Strategies
# ==================================

# YAML files - use semantic merge
*.yml merge=yaml
*.yaml merge=yaml

# Package lock files - prefer theirs (usually updated by dependency managers)
package-lock.json merge=theirs
yarn.lock merge=theirs
Pipfile.lock merge=theirs
poetry.lock merge=theirs
pnpm-lock.yaml merge=theirs

# Environment files - prefer ours (local configurations)
.env merge=ours
.env.* merge=ours
*.local merge=ours

# Configuration files - prefer ours
config/*.conf merge=ours
odoo.conf merge=ours

# Generated files - prefer theirs (should be regenerated)
**/dist/** merge=theirs
**/build/** merge=theirs
**/__pycache__/** merge=theirs
*.pyc merge=theirs

# Database dumps - binary, no merge
*.sql.gz binary
*.dump binary

# Images and binary files
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.pdf binary

# Documentation - use standard merge with rerere
*.md merge=union
README* merge=union

# Source code - use standard merge
*.py merge
*.js merge
*.ts merge
*.tsx merge
*.jsx merge

# XML/Data files - line-based merge
*.xml merge
*.json merge

# Shell scripts
*.sh merge
EOF

echo "   ✅ .gitattributes created with merge strategies"
echo ""

# ============================================================================
# 5. Additional Git configuration for better merging
# ============================================================================
echo "📝 Configuring additional Git settings..."

# Use patience diff algorithm (better for code)
git config diff.algorithm patience

# Show renames in diffs
git config diff.renames true

# Detect copies as well as renames
git config diff.renameLimit 999999

# Auto-stash before rebase/pull
git config rebase.autoStash true

# Prune deleted branches on fetch
git config fetch.prune true

# Use --ff-only for pulls by default (safer)
# Comment out if you prefer merge commits
# git config pull.ff only

echo "   ✅ Additional Git settings configured"
echo ""

# ============================================================================
# 6. Make scripts executable
# ============================================================================
echo "📝 Making merge scripts executable..."

chmod +x "$REPO_ROOT/.github/scripts/ai-conflict-resolver.py" 2>/dev/null || true
chmod +x "$REPO_ROOT/.github/scripts/yaml-merge.py" 2>/dev/null || true
chmod +x "$REPO_ROOT/scripts/resolve-conflicts.sh" 2>/dev/null || true

echo "   ✅ Scripts are executable"
echo ""

# ============================================================================
# 7. Create rerere directory if it doesn't exist
# ============================================================================
echo "📝 Initializing rerere..."

mkdir -p "$REPO_ROOT/.git/rr-cache"

echo "   ✅ rerere initialized"
echo ""

# ============================================================================
# Summary
# ============================================================================
echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ✅ Git Merge Strategies Configured Successfully!         ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Configuration Summary:"
echo "   • rerere enabled - Git will remember conflict resolutions"
echo "   • diff3 conflict style - Shows base, ours, and theirs"
echo "   • YAML semantic merge - Intelligent YAML merging"
echo "   • File-specific strategies - Lock files, configs, etc."
echo "   • Patience diff algorithm - Better code diffs"
echo ""
echo "🎯 Next Steps:"
echo "   1. Test YAML merge:"
echo "      git checkout -b test-yaml-merge"
echo "      # Make changes to a .yml file"
echo "      git merge main"
echo ""
echo "   2. View current config:"
echo "      git config --list | grep -E '(merge|diff|rerere)'"
echo ""
echo "   3. Manually resolve a conflict to teach rerere:"
echo "      git rerere status"
echo "      git rerere diff"
echo ""
echo "   4. Use the auto-resolver for complex conflicts:"
echo "      ./scripts/resolve-conflicts.sh <branch-name>"
echo ""
echo "📚 Documentation:"
echo "   • Rerere: https://git-scm.com/docs/git-rerere"
echo "   • Merge drivers: https://git-scm.com/docs/gitattributes#_defining_a_custom_merge_driver"
echo "   • Conflict resolution guide: ./docs/CONFLICT_RESOLUTION.md"
echo ""

# Check if running in CI
if [ -n "$CI" ]; then
    echo "ℹ️  Running in CI - configuration applied to current repository only"
else
    echo "ℹ️  Configuration applied to current repository (.git/config)"
    echo "   To apply globally, add --global flag to git config commands"
fi

echo ""
echo "Done! 🎉"

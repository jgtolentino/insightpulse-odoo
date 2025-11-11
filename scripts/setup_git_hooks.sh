#!/bin/bash
# scripts/setup_git_hooks.sh
# Install git hooks for conflict detection

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || echo ".")
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "🔧 Installing git hooks..."

# Create pre-commit hook
cat > "$HOOKS_DIR/pre-commit" <<'EOF'
#!/bin/bash
# Pre-commit hook: Prevents committing files with unresolved merge conflicts

echo "🔍 Pre-commit: Checking for merge conflicts..."

CONFLICT_FOUND=0

# Check staged files only
for file in $(git diff --cached --name-only); do
    if [ -f "$file" ] && grep -q "^<<<<<<< " "$file" 2>/dev/null; then
        echo "❌ Merge conflict found in: $file"
        CONFLICT_FOUND=1
    fi
done

if [ $CONFLICT_FOUND -eq 1 ]; then
    echo ""
    echo "❌ COMMIT BLOCKED: Unresolved merge conflicts detected"
    echo ""
    echo "Please resolve all conflicts before committing."
    echo "Run: ./scripts/detect_conflicts.sh for details"
    echo ""
    exit 1
fi

echo "✅ No conflicts detected"
exit 0
EOF

chmod +x "$HOOKS_DIR/pre-commit"

echo "✅ Git hooks installed successfully"
echo ""
echo "Installed hooks:"
echo "  - pre-commit (conflict detection)"
echo ""
echo "To bypass hooks (not recommended):"
echo "  git commit --no-verify"

#!/usr/bin/env bash
# Install git hooks for auto-regenerating repo tree
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
HOOK_DIR="${ROOT_DIR}/.git/hooks"
PRE_COMMIT_HOOK="${HOOK_DIR}/pre-commit"

echo "Installing git pre-commit hook..."

cat > "${PRE_COMMIT_HOOK}" << 'EOF'
#!/usr/bin/env bash
# Auto-regenerate repo tree before commit
# Installed by scripts/install-git-hooks.sh

set -euo pipefail

echo "🔄 Regenerating repo tree..."
./scripts/gen_repo_tree.sh

# Add the updated spec.md to staging if it changed
if ! git diff --quiet spec.md; then
  echo "📝 Adding updated spec.md to commit"
  git add spec.md
fi

exit 0
EOF

chmod +x "${PRE_COMMIT_HOOK}"

echo "✅ Git hooks installed successfully!"
echo ""
echo "Pre-commit hook will now auto-regenerate repo tree in spec.md"
echo "To disable: rm .git/hooks/pre-commit"

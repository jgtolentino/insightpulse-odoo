#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"

TARGET_FILE="${ROOT_DIR}/spec.md"
TMP_TREE="$(mktemp)"

cd "${ROOT_DIR}"

# Generate the actual tree (depth 2, adjust as needed)
# Exclude common build/cache directories
# Use LC_ALL=C for consistent sorting across macOS and Linux
LC_ALL=C tree -a -L 2 \
  --dirsfirst \
  --noreport \
  -I 'node_modules|.git|__pycache__|*.pyc|.DS_Store|venv|env' \
  . > "${TMP_TREE}"

# Escape backticks for safe insertion
ESCAPED_TREE=$(sed 's/`/\\`/g' "${TMP_TREE}")

# Replace the section between markers in TARGET_FILE
perl -0pi -e "s/<!-- REPO_TREE_START -->.*?<!-- REPO_TREE_END -->/<!-- REPO_TREE_START -->\n\`\`\`text\n${ESCAPED_TREE}\n\`\`\`\n<!-- REPO_TREE_END -->/s" "${TARGET_FILE}"

rm -f "${TMP_TREE}"

echo "✅ Updated repo tree in ${TARGET_FILE}"

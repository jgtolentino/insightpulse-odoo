#!/usr/bin/env bash
set -euo pipefail

# Clone OCA repositories for Odoo 18.0
# Usage: ./clone_oca.sh [target_directory]

BASE="${1:-./oca}"
BRANCH="${2:-18.0}"

mkdir -p "$BASE"
cd "$BASE"

echo "=== Cloning OCA repositories (branch: $BRANCH) to $BASE ==="

REPOS=(
  web
  server-tools
  server-ux
  sale-workflow
  purchase-workflow
  stock-logistics-workflow
  stock-logistics-reporting
  account-financial-tools
  account-invoicing
  reporting-engine
  hr
  hr-attendance
  hr-expense
  timesheet
  project
  mis-builder
  connector
  queue
)

for r in "${REPOS[@]}"; do
  if [ -d "$r" ]; then
    echo "  ✓ $r already exists, skipping..."
  else
    echo "  → Cloning $r..."
    git clone --depth 1 -b "$BRANCH" "https://github.com/OCA/$r.git" || {
      echo "  ✗ Failed to clone $r (branch $BRANCH may not exist)"
    }
  fi
done

echo ""
echo "=== OCA $BRANCH repositories cloned successfully ==="
echo "Total directories: $(ls -1 | wc -l)"

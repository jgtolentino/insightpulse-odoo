#!/usr/bin/env bash
set -euo pipefail
mkdir -p addons/oca
cd addons/oca

clone_repo() {
  local repo="$1"; shift
  if [ ! -d "$(basename "$repo" .git)" ]; then
    git clone --depth=1 "https://github.com/OCA/${repo}.git"
  fi
}

# Core repos
clone_repo server-tools
clone_repo server-auth
clone_repo web
clone_repo queue
clone_repo account-financial-tools
clone_repo reporting-engine
clone_repo hr
clone_repo purchase-workflow

echo "Fetched OCA repos. Enable needed modules in Apps."

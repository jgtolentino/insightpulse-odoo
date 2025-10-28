#!/bin/bash
# List all installations for this app
# Usage: ./scripts/gh-app-list-installations.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JWT=$("$SCRIPT_DIR/gh-app-jwt.sh")

curl -s \
  -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github+json" \
  https://api.github.com/app/installations | \
  jq -r '.[] | "\(.id)\t\(.account.login)\t\(.repository_selection)"'

#!/bin/bash
# Get installation access token
# Usage: ./scripts/gh-app-install-token.sh <installation_id>

set -euo pipefail

INSTALLATION_ID="${1:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "$INSTALLATION_ID" ]; then
  echo "Usage: $0 <installation_id>" >&2
  echo "Get installation ID with: $SCRIPT_DIR/gh-app-list-installations.sh" >&2
  exit 1
fi

JWT=$("$SCRIPT_DIR/gh-app-jwt.sh")

curl -s -X POST \
  -H "Authorization: Bearer ${JWT}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens" | \
  jq -r '.token'

#!/bin/bash
# Generate GitHub App JWT
# Usage: ./scripts/gh-app-jwt.sh

set -euo pipefail

GITHUB_APP_ID="${GITHUB_APP_ID:-2191216}"
PEM_PATH="${GITHUB_APP_PEM_PATH:-$HOME/.github/apps/pulser-hub.pem}"

if [ ! -f "$PEM_PATH" ]; then
  echo "Error: PEM file not found at $PEM_PATH" >&2
  exit 1
fi

NOW=$(date +%s)
IAT=$((NOW - 60))
EXP=$((NOW + 600))

HEADER='{"alg":"RS256","typ":"JWT"}'
PAYLOAD="{\"iat\":${IAT},\"exp\":${EXP},\"iss\":\"${GITHUB_APP_ID}\"}"

HEADER_B64=$(echo -n "$HEADER" | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')
PAYLOAD_B64=$(echo -n "$PAYLOAD" | openssl base64 -e -A | tr '+/' '-_' | tr -d '=')

SIGNATURE=$(echo -n "${HEADER_B64}.${PAYLOAD_B64}" | \
  openssl dgst -sha256 -sign "$PEM_PATH" | \
  openssl base64 -e -A | tr '+/' '-_' | tr -d '=')

JWT="${HEADER_B64}.${PAYLOAD_B64}.${SIGNATURE}"
echo "$JWT"

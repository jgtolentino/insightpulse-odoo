#!/usr/bin/env bash
set -euo pipefail
: "${MM_BASE_URL:?set MM_BASE_URL}"
: "${MM_ADMIN_TOKEN:?set MM_ADMIN_TOKEN}"

curl -fsS "${MM_BASE_URL}/api/v4/system/ping" | jq .
curl -fsS -H "Authorization: Bearer ${MM_ADMIN_TOKEN}" "${MM_BASE_URL}/api/v4/plugins" | jq '.active | map({id, version})'

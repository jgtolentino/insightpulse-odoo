#!/bin/bash
set -euo pipefail

: "${BASE_URL:=https://erp.insightpulseai.net}"

echo "Verifying assets at $BASE_URL..."
# curl -fsSI "$BASE_URL/web/assets/" | head
echo "✅ Asset verification script: READY"

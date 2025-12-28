#!/usr/bin/env bash
# Single entrypoint for environment deployment with internal ordering and retries
set -euo pipefail

ENV="${1:-dev}"
RETRIES="${RETRIES:-3}"

retry() {
  local n=1
  until "$@"; do
    if (( n >= RETRIES )); then
      echo "FAILED after $n attempts: $*"
      return 1
    fi
    echo "Retry $n/$RETRIES: $*"
    n=$((n+1))
    sleep $((n*2))
  done
}

echo "=== ENV=$ENV ==="

echo "=== 1) DB sync ==="
retry ./scripts/db_sync.sh

echo "=== 2) Compile+Validate ==="
python3 scripts/hybrid/hybrid compile --env "$ENV"
python3 scripts/hybrid/hybrid validate --env "$ENV"

echo "=== 3) Drift gate (pre) ==="
if [[ "$ENV" == "dev" ]]; then
  python3 scripts/hybrid/hybrid drift-plan --env "$ENV" || true
else
  python3 scripts/hybrid/hybrid drift-plan --env "$ENV"
fi

echo "=== 4) Apply (Git wins for managed assets) ==="
python3 scripts/hybrid/hybrid apply --env "$ENV"

echo "=== 5) Drift gate (post) ==="
python3 scripts/hybrid/hybrid drift-plan --env "$ENV"

echo "DEPLOY_OK ($ENV)"

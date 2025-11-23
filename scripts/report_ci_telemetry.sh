#!/usr/bin/env bash
set -euo pipefail

# Usage: report_ci_telemetry.sh <status>
# status: success | failure | cancelled (use ${{ job.status }} in GH Actions)

STATUS="${1:-unknown}"
WEBHOOK_URL="${N8N_CI_WEBHOOK_URL:-}"

# If no webhook configured, exit gracefully (no-op)
if [ -z "$WEBHOOK_URL" ]; then
  echo "N8N_CI_WEBHOOK_URL not set, skipping CI telemetry."
  exit 0
fi

# Build JSON payload via Python to avoid brittle shell escaping
python3 - << 'PY' "$STATUS"
import json, os, sys
status = sys.argv[1]

payload = {
    "status": status,
    "repo": os.environ.get("GITHUB_REPOSITORY"),
    "workflow": os.environ.get("GITHUB_WORKFLOW"),
    "job": os.environ.get("GITHUB_JOB"),
    "run_id": os.environ.get("GITHUB_RUN_ID"),
    "run_number": os.environ.get("GITHUB_RUN_NUMBER"),
    "branch": os.environ.get("GITHUB_REF_NAME"),
    "sha": os.environ.get("GITHUB_SHA"),
}

print(json.dumps(payload))
PY | curl -sS -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d @-

echo "CI telemetry sent with status: $STATUS"

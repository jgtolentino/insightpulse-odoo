#!/usr/bin/env bash
set -euo pipefail

: "${N8N_BASE_URL:?set N8N_BASE_URL (e.g., https://n8n.insightpulseai.net)}"

AUTH_HEADER=()
if [[ -n "${N8N_API_KEY:-}" ]]; then
  AUTH_HEADER=(-H "X-N8N-API-KEY: ${N8N_API_KEY}")
elif [[ -n "${N8N_BASIC_AUTH_USER:-}" && -n "${N8N_BASIC_AUTH_PASSWORD:-}" ]]; then
  AUTH_HEADER=(-u "${N8N_BASIC_AUTH_USER}:${N8N_BASIC_AUTH_PASSWORD}")
else
  echo "Provide N8N_API_KEY or N8N_BASIC_AUTH_USER/N8N_BASIC_AUTH_PASSWORD"; exit 1
fi

echo "== n8n: health =="
curl -fsS "${N8N_BASE_URL}/rest/ping" "${AUTH_HEADER[@]}" || {
  echo "n8n not reachable at ${N8N_BASE_URL}"; exit 1; }

echo "== n8n: importing hello_webhook workflow =="
curl -fsS -X POST "${N8N_BASE_URL}/rest/workflows" \
  -H 'Content-Type: application/json' \
  "${AUTH_HEADER[@]}" \
  --data-binary @workflows/n8n/hello_webhook.json \
  | jq -r '.id' || true

echo "== n8n: list workflows (sanity) =="
curl -fsS "${N8N_BASE_URL}/rest/workflows" "${AUTH_HEADER[@]}" | jq '.data | length' || true

echo "n8n seed complete."

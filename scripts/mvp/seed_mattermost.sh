#!/usr/bin/env bash
set -euo pipefail

: "${MM_BASE_URL:?set MM_BASE_URL (e.g., https://chat.insightpulseai.net)}"
: "${MM_ADMIN_TOKEN:?set MM_ADMIN_TOKEN (Mattermost personal access token)}"

auth=(-H "Authorization: Bearer ${MM_ADMIN_TOKEN}")

# Create "insightpulse" team if not exists
TEAM_NAME=insightpulse
TEAM_DISPLAY_NAME="InsightPulse"
TEAM_ID=$(curl -fsS -H "Content-Type: application/json" "${auth[@]}" \
  "${MM_BASE_URL}/api/v4/teams/name/${TEAM_NAME}" | jq -r '.id' 2>/dev/null || true)

if [[ -z "${TEAM_ID}" || "${TEAM_ID}" == "null" ]]; then
  echo "== create team =="
  TEAM_ID=$(curl -fsS -X POST -H "Content-Type: application/json" "${auth[@]}" \
    "${MM_BASE_URL}/api/v4/teams" \
    -d "{\"name\":\"${TEAM_NAME}\",\"display_name\":\"${TEAM_DISPLAY_NAME}\",\"type\":\"I\"}" | jq -r '.id')
fi

# Create "ops" channel
CHANNEL_NAME=ops
CHANNEL_ID=$(curl -fsS -H "Content-Type: application/json" "${auth[@]}" \
  "${MM_BASE_URL}/api/v4/teams/${TEAM_ID}/channels/name/${CHANNEL_NAME}" | jq -r '.id' 2>/dev/null || true)

if [[ -z "${CHANNEL_ID}" || "${CHANNEL_ID}" == "null" ]]; then
  echo "== create channel =="
  CHANNEL_ID=$(curl -fsS -X POST -H "Content-Type: application/json" "${auth[@]}" \
    "${MM_BASE_URL}/api/v4/channels" \
    -d "{\"team_id\":\"${TEAM_ID}\",\"name\":\"${CHANNEL_NAME}\",\"display_name\":\"Ops\",\"type\":\"O\"}" | jq -r '.id')
fi

# Post hello message
echo "== post hello =="
curl -fsS -X POST -H "Content-Type: application/json" "${auth[@]}" \
  "${MM_BASE_URL}/api/v4/posts" \
  -d "{\"channel_id\":\"${CHANNEL_ID}\",\"message\":\"✅ InsightPulse MVP online. n8n + Mattermost ready.\"}" >/dev/null

echo "Mattermost seed complete."

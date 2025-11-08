#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   DOMAIN_BASE=insightpulseai.net ERP_HOST=165.227.10.178 make mvp-quickstart
# Or:
#   DOMAIN_BASE=... ERP_HOST=... scripts/mvp/quickstart.sh

# --- Inputs (required) ---
DOMAIN_BASE="${DOMAIN_BASE:-${1:-}}"
ERP_HOST="${ERP_HOST:-${2:-}}"

if [[ -z "${DOMAIN_BASE}" || -z "${ERP_HOST}" ]]; then
  echo "❌ Missing DOMAIN_BASE or ERP_HOST."
  echo "   Example: DOMAIN_BASE=insightpulseai.net ERP_HOST=165.227.10.178 make mvp-quickstart"
  exit 1
fi

# --- Derived URLs ---
N8N_BASE_URL="${N8N_BASE_URL:-https://n8n.${DOMAIN_BASE}}"
MM_BASE_URL="${MM_BASE_URL:-https://chat.${DOMAIN_BASE}}"

# --- Random secret generator (prefers openssl; falls back to Python) ---
rand() {
  if command -v openssl >/dev/null 2>&1; then
    openssl rand -base64 32 | tr -d '\n' | tr -d '=/+' | cut -c1-32
  else
    python3 - <<'PY' 2>/dev/null || true
import secrets, string
alphabet = string.ascii_letters + string.digits
print(''.join(secrets.choice(alphabet) for _ in range(32)))
PY
  fi
}

# Existing .env.mvp? Keep user-edited values; fill gaps only.
ENV_FILE=".env.mvp"
touch "${ENV_FILE}"

# Helper to upsert a key=value line idempotently
put() {
  local key="$1" val="$2"
  if grep -qE "^${key}=" "${ENV_FILE}"; then
    # keep existing value
    true
  else
    echo "${key}=${val}" >> "${ENV_FILE}"
  fi
}

echo "📝 Generating ${ENV_FILE} (non-destructive)…"
put DOMAIN_BASE "${DOMAIN_BASE}"
put ERP_HOST "${ERP_HOST}"

put N8N_BASE_URL "${N8N_BASE_URL}"
put N8N_HOST "n8n.${DOMAIN_BASE}"
put N8N_BASIC_AUTH_ACTIVE "true"
put N8N_BASIC_AUTH_USER "${N8N_BASIC_AUTH_USER:-admin}"
put N8N_BASIC_AUTH_PASSWORD "${N8N_BASIC_AUTH_PASSWORD:-$(rand)}"
put N8N_API_KEY "${N8N_API_KEY:-}"               # optional alternative auth
put N8N_POSTGRES_PASSWORD "${N8N_POSTGRES_PASSWORD:-$(rand)}"

put MM_BASE_URL "${MM_BASE_URL}"
put MM_ADMIN_TOKEN "${MM_ADMIN_TOKEN:-}"         # required later for seeding
put MM_POSTGRES_PASSWORD "${MM_POSTGRES_PASSWORD:-$(rand)}"

put CERTBOT_EMAIL "${CERTBOT_EMAIL:-admin@${DOMAIN_BASE}}"

# Show a safe summary (no secrets)
echo "╭───────────────────────────────╮"
echo "│ MVP Environment Ready         │"
echo "╰───────────────────────────────╯"
echo "DOMAIN_BASE         = ${DOMAIN_BASE}"
echo "ERP_HOST            = ${ERP_HOST}"
echo "N8N_BASE_URL        = ${N8N_BASE_URL}"
echo "MM_BASE_URL         = ${MM_BASE_URL}"
echo "N8N auth            = basic (user: admin)  # password written to .env.mvp"
echo "Mattermost token    = $( [[ -n ${MM_ADMIN_TOKEN} ]] && echo 'present' || echo 'NOT SET' )"
echo

# Export env for current session
set -a
source "${ENV_FILE}"
set +a

echo "🚀 Starting services (Mattermost + n8n)…"
make mvp-up

# Optional TLS step (skippable). Set MVP_TLS=1 to enable.
if [[ "${MVP_TLS:-0}" == "1" ]]; then
  echo "🔐 Issuing TLS certs via certbot (--nginx)…"
  make mvp-tls || echo "⚠️ TLS step failed or skipped; continue without"
else
  echo "ℹ️ TLS step skipped (set MVP_TLS=1 to enable)"
fi

echo "⏳ Waiting for services to stabilize…"
sleep "${MVP_SLEEP:-60}"

# Seed if we already have a Mattermost PAT
if [[ -n "${MM_ADMIN_TOKEN}" ]]; then
  echo "🌱 Seeding automations (n8n workflow + Mattermost bootstrap)…"
  make mvp-seed || echo "⚠️ Seeding had warnings; check logs"
else
  echo "ℹ️ Skipping seeding (no MM_ADMIN_TOKEN)."
  echo "   After you generate a Mattermost Personal Access Token:"
  echo "     export MM_ADMIN_TOKEN='your_token_here'"
  echo "     make mvp-seed"
fi

echo "🔎 Running verification…"
make mvp-verify || true

echo
echo "✅ MVP quickstart complete."
echo "Next:"
echo "  1) Open: ${MM_BASE_URL} and ${N8N_BASE_URL}"
echo "  2) Create a Mattermost Personal Access Token"
echo "  3) export MM_ADMIN_TOKEN=... && make mvp-seed && make mvp-verify"

#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; NC='\033[0m'
ok(){ echo -e "${GREEN}✓${NC} $*"; }
err(){ echo -e "${RED}✗${NC} $*"; exit 1; }

echo "== OAuth Provider Validation"

# Check Keycloak SSO provider
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -tAc "SELECT COUNT(*) FROM auth_oauth_provider WHERE name = '\''Keycloak SSO'\'' AND enabled = true"' | grep -q "1" \
  && ok "Keycloak SSO provider enabled" || err "Keycloak SSO provider missing"

# Check Google provider
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -tAc "SELECT COUNT(*) FROM auth_oauth_provider WHERE name = '\''Google'\'' AND enabled = true"' | grep -q "1" \
  && ok "Google provider enabled" || err "Google provider missing"

# Check OAuth button text
curl -s https://erp.insightpulseai.net/web/login | grep -q "Sign in with Keycloak SSO" \
  && ok "Keycloak SSO button text correct" || err "Keycloak button text missing"

curl -s https://erp.insightpulseai.net/web/login | grep -q "Sign in with Google" \
  && ok "Google button text correct" || err "Google button text missing"

# Check Keycloak redirect URIs
echo "== Keycloak redirect URIs configured"
ssh root@165.227.10.178 'source /opt/insightpulse-sso/sso-credentials.sh && \
  TOKEN=$(curl -s -X POST "$KEYCLOAK_URL/realms/master/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=$KEYCLOAK_ADMIN_USER" \
    -d "password=$KEYCLOAK_ADMIN_PASSWORD" \
    -d "grant_type=password" \
    -d "client_id=admin-cli" | jq -r ".access_token") && \
  curl -s "$KEYCLOAK_URL/admin/realms/$KEYCLOAK_REALM/clients" \
    -H "Authorization: Bearer $TOKEN" | jq -r ".[] | select(.clientId == \"odoo-erp\") | .redirectUris[]"' | tee /tmp/redirects.txt

grep -q "https://erp.insightpulseai.net" /tmp/redirects.txt && ok "HTTPS redirect URI configured" || err "HTTPS redirect missing"
grep -q "http://erp.insightpulseai.net" /tmp/redirects.txt && ok "HTTP redirect URI configured" || err "HTTP redirect missing"

ok "OAuth validation passed."

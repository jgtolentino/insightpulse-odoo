#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; NC='\033[0m'
ok(){ echo -e "${GREEN}✓${NC} $*"; }
err(){ echo -e "${RED}✗${NC} $*"; exit 1; }

echo "== Containers"
ssh root@165.227.10.178 'docker ps --format "table {{.Names}}\t{{.Status}}"' || err "docker ps failed"

echo ""
echo "== Ports"
ssh root@165.227.10.178 'nc -z localhost 8069' && ok "Odoo on :8069" || err "Odoo not listening :8069"
ssh root@165.227.10.178 'nc -z localhost 80' && ok "Nginx on :80" || err "Nginx not listening :80"

echo ""
echo "== HTTP smoke via domain"
curl -fsS https://erp.insightpulseai.net/ -o /dev/null && ok "GET / (Odoo)" || err "Odoo not reachable"

echo ""
echo "== DBs"
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -lqt | cut -d \| -f 1 | grep -qw insightpulse' \
  && ok "DB insightpulse exists" || err "DB insightpulse missing"

echo ""
echo "== OAuth Providers"
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -tAc "SELECT name FROM auth_oauth_provider WHERE enabled = true ORDER BY id"' | while read provider; do
  ok "Provider: $provider"
done

echo ""
echo "== Company Branding"
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -tAc "SELECT name FROM res_company WHERE id = 1"' | grep -q "InsightPulse AI" \
  && ok "Company 1 branded as InsightPulse AI" || err "Company 1 branding missing"

echo ""
echo "== Base URL"
ssh root@165.227.10.178 'docker exec odoo19_db psql -U odoo -d insightpulse -tAc "SELECT value FROM ir_config_parameter WHERE key = '\''web.base.url'\''"' | grep -q "https://erp.insightpulseai.net" \
  && ok "Base URL is HTTPS" || err "Base URL not HTTPS"

echo ""
echo "== Logs readable"
ssh root@165.227.10.178 'docker logs odoo19 --tail=10' >/dev/null && ok "Odoo logs accessible"

echo ""
ok "Healthcheck passed."

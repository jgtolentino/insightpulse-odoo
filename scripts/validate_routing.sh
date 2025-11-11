#!/usr/bin/env bash
set -euo pipefail
set -x
echo "== Testing Odoo routing"
curl -I https://erp.insightpulseai.net/ | head -n1
curl -I https://erp.insightpulseai.net/web/login | head -n1

echo "== Testing OAuth endpoints"
curl -s https://erp.insightpulseai.net/web/login | grep -o "Sign in with [^<]*" | head -3

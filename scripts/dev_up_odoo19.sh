#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Ensure pins exist
"${ROOT}/scripts/pin_images.sh"

# Set proper permissions (avoid 777)
chmod -R u+rwX,go+rX "${ROOT}/config" "${ROOT}/addons" 2>/dev/null || true

cd "${ROOT}/runtime/dev"
docker compose --env-file .env.odoo19 -f compose.odoo19.yml up -d

echo "OK: started. Waiting for Odoo to be ready..."
sleep 5

# Probe
if curl -fsS http://localhost:8069/web/login >/dev/null 2>&1; then
  echo "✅ OK: Odoo reachable on http://localhost:8069"
else
  echo "⚠️  Warning: Odoo not yet ready. Check logs with:"
  echo "   cd runtime/dev && docker compose --env-file .env.odoo19 -f compose.odoo19.yml logs --tail=50 web"
fi

echo ""
echo "Access points:"
echo "  Odoo:    http://localhost:8069"
echo "  pgAdmin: http://localhost:5050 (admin@admin.com / admin)"

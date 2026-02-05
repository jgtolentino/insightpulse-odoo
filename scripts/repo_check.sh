#!/usr/bin/env bash
set -euo pipefail

test -d supabase/migrations || { echo "missing supabase/migrations"; exit 2; }
test -d supabase/functions  || { echo "missing supabase/functions"; exit 2; }
test -f supabase/config.toml || echo "WARN: supabase/config.toml not found (ok if remote-only)"

test -d runtime/odoo || { echo "missing runtime/odoo"; exit 2; }
test -f runtime/odoo/docker-compose.yml || { echo "missing runtime/odoo/docker-compose.yml"; exit 2; }

test -d tools/claude-plugin/.claude-plugin || echo "WARN: tools/claude-plugin/.claude-plugin missing"

echo "✅ repo_check OK"

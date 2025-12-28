#!/usr/bin/env bash
# Database migration and seed orchestrator
# Applies migrations and seed data in order
set -euo pipefail

MIGRATIONS_DIR="${MIGRATIONS_DIR:-db/migrations}"
SEED_DIR="${SEED_DIR:-db/seed}"
POSTGRES_URL="${POSTGRES_URL:-${DATABASE_URL}}"

if [[ -z "$POSTGRES_URL" ]]; then
  echo "❌ ERROR: POSTGRES_URL or DATABASE_URL must be set"
  exit 1
fi

echo "=== Database Sync ==="
echo "  Migrations: $MIGRATIONS_DIR"
echo "  Seed: $SEED_DIR"
echo ""

# Apply migrations in order
echo "=== 1) Applying migrations ==="
if [[ -d "$MIGRATIONS_DIR" ]]; then
  for migration in "$MIGRATIONS_DIR"/*.sql; do
    if [[ -f "$migration" ]]; then
      echo "  → $(basename "$migration")"
      psql "$POSTGRES_URL" -f "$migration" -v ON_ERROR_STOP=1
    fi
  done
  echo "✅ Migrations complete"
else
  echo "⚠️  No migrations directory found"
fi

echo ""

# Apply seed data
echo "=== 2) Applying seed data ==="
if [[ -d "$SEED_DIR" ]]; then
  for seed in "$SEED_DIR"/*.sql; do
    if [[ -f "$seed" ]]; then
      echo "  → $(basename "$seed")"
      psql "$POSTGRES_URL" -f "$seed" -v ON_ERROR_STOP=1
    fi
  done
  echo "✅ Seed data complete"
else
  echo "⚠️  No seed directory found"
fi

echo ""
echo "✅ DB_SYNC_OK"

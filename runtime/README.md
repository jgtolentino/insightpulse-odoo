# Runtime

This directory contains execution scaffolding for the InsightPulse platform.

## Structure

- `odoo/` - Odoo 19 runtime configuration
  - `docker-compose.yml` - Odoo and PostgreSQL services
  - `odoo.conf` - Odoo configuration (env-substituted, no secrets)
  - `entrypoint.d/` - Custom entrypoint scripts (if needed)
  - `scripts/` - Runtime utility scripts (if needed)
- `supabase/` - Local Supabase development wrappers (optional)
  - `start.sh` - Local supabase start wrapper (if needed)

## Key Principle

The `supabase/` directory at the root remains the canonical deploy surface for DB + Edge Functions. This `runtime/` directory is purely for local development and execution scaffolding.

## Usage

### Start Odoo Runtime

```bash
bash scripts/odoo_up.sh
# or directly:
cd runtime/odoo
docker compose up -d
```

### Stop Odoo Runtime

```bash
bash scripts/odoo_down.sh
# or directly:
cd runtime/odoo
docker compose down
```

### Check Status

```bash
cd runtime/odoo
docker compose ps
```

## Configuration

Odoo configuration uses environment variables:
- `ODOO_DB_NAME` (default: odoo)
- `ODOO_DB_USER` (default: odoo)
- `ODOO_DB_PASSWORD` (default: odoo)

Set these in your `.env` file at the repository root.

## Volumes

- `odoo_pgdata` - PostgreSQL data
- `odoo_webdata` - Odoo data directory
- `../../addons` - Custom addons (mounted read-only)
- `../../vendor/oca` - OCA modules (mounted read-only)

## Odoo Source Strategy

Current strategy uses the official `odoo:19.0` Docker image. For more control, you can:
1. Pin to a specific version: `odoo:19.0.20240101`
2. Build from source in `vendor/odoo/` (requires updating docker-compose.yml)
3. Use a custom Dockerfile in this directory

See the main README for deployment strategies.

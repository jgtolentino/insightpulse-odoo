# Odoo 19 Dev Runtime (Digest-Pinned)

Production-grade, deterministic Odoo 19 development environment using pinned container digests.

## Quick Start

```bash
./scripts/dev_up_odoo19.sh
```

This will:
1. Pull and compute digests for pinned image tags
2. Generate `.env.odoo19` with digest-pinned images
3. Start the stack with Docker Compose

## Access

- **Odoo**: http://localhost:8069
- **pgAdmin**: http://localhost:5050 (admin@admin.com / admin)

## Stop

```bash
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml down
```

## Clean (removes volumes)

```bash
cd runtime/dev
docker compose --env-file .env.odoo19 -f compose.odoo19.yml down -v
```

## Architecture

### Pinned Images

Images are pinned by digest via `scripts/pin_images.sh` using tags in `ops/pins/*`:

- `ops/pins/odoo_19.tag.txt` - Odoo 19 dated tag (e.g., `odoo:19.0-20260119`)
- `ops/pins/postgres_16.tag.txt` - PostgreSQL 16 Alpine
- `ops/pins/pgadmin.tag.txt` - pgAdmin 4

### Environment Variables

The compose file uses `${ODOO_IMAGE}`, `${PG_IMAGE}`, and `${PGADMIN_IMAGE}` to prevent tag drift. These are resolved from `.env.odoo19` which contains digest-pinned references.

### Colima (Apple Silicon)

For fast performance on Apple Silicon:

```bash
colima stop --force || true
colima delete || true
colima start --cpu 4 --memory 8 --disk 60 --vm-type=vz --mount-type=virtiofs
```

## CI Guards

Two CI guards enforce determinism:

1. **No Floating Images** (`guards/ci_guard_no_floating_images.sh`)
   - Blocks `:latest`, `:19`, `:18`, etc.
   - Allows `${VAR}` and `@sha256:...`

2. **No Version Branching** (`guards/ci_guard_no_version_branching.sh`)
   - Prevents version-specific code (`if odoo >= 19`)
   - Enforces "version as env config" pattern

## Notes

* Images are deterministic - same digest across all environments
* No `chmod 777` - proper permissions via `u+rwX,go+rX`
* `--dev=xml,qweb,assets` for development only
* PostgreSQL 16 aligns with Supabase baseline
* Version switching is configuration, not code branching

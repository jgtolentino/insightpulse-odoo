# Release Notes (Template)

## Summary
- Image: Docker Hub `jgtolentino/insightpulse-odoo:main`
- Compose: two-service (odoo, db)
- Superset embedding via `superset_embed`

## Feature Inventory
See `docs/feature-inventory.md` (auto-generated).

## Changes since last release
- Merged PRs: fill via GitHub release notes.
- Breaking: none known.

## Upgrade steps
1. Pull image and `docker compose up -d`.
2. Run DB migrations: `-u all --stop-after-init`.
3. Restart Odoo.

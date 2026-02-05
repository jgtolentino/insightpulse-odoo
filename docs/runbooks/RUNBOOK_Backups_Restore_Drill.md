# Runbook: Backups + Restore Drill (Odoo DB + Supabase)

## Scope
- Odoo DB on DO Managed Postgres: `odoo-db-sgp1`
- Supabase Postgres + Storage artifacts (control plane / apps)

## Objectives
- Ensure backups exist and are restorable (RPO/RTO confidence)
- Ensure restore drill is repeatable and logged

## Odoo DB (DO Managed Postgres) — Restore Drill (logical)
**Inputs**
- Postgres endpoint/port/user/db provided via secrets/env
- A known dump path in CI runner or ops box

**Procedure (logical restore)**
1) Create a scratch database (or use a scratch cluster if you have one).
2) Restore using `pg_restore` (custom-format dumps) or `psql` (plain dumps).
3) Run smoke queries (table counts + critical tables exist).

**Smoke Queries**
- `SELECT 1;`
- `\dt` contains core Odoo tables (e.g., res_partner, account_move) — adjust per version
- `SELECT count(*) FROM ir_model;`

## Supabase — Restore Drill (logical)
1) Confirm nightly backups or PITR policy exists (plan-dependent)
2) Export schema + data snapshot for critical schemas (ops/app schemas)
3) Validate: apply to scratch project and run smoke RPCs

## Logging
- Record drill date, operator/agent, outputs, and pass/fail in:
  - `ops/ssot/restore_drills.log` (or equivalent)

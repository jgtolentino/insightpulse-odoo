# Superset Hybrid Control Plane Agent — Skills Spec

This agent owns the Git-first reconciliation loop for Superset/Preset dashboards and database connections.

## Core Capabilities

### A. Runtime Management
- [x] Boot Superset (Docker) and verify health
- [x] Initialize admin + roles
- [x] Load official examples (`superset load_examples`)
- [ ] Execute SQL Lab queries via API

### B. Asset Operations (Dashboards as Code)
- [ ] Author templated native assets: databases/datasets/charts/dashboards
- [ ] Compile env bundles from templates
- [ ] Validate YAML structure and required fields
- [ ] Apply bundles via CLI (Superset/Preset)

### C. Drift & Reconciliation
- [ ] Export runtime assets to repo snapshot
- [ ] Normalize exports for deterministic diff
- [ ] Drift-plan: runtime vs bundle diff
- [ ] Translate exports to templates and retarget via env vars
- [ ] Promote dev→staging→prod sequentially

### D. Database Sync
- [ ] Migrations-as-code in `db/migrations/`
- [ ] Schema dump snapshots in `db/schema_dump/`
- [ ] Drift check: runtime schema vs snapshot
- [x] Generate Superset DB connection assets (Supabase Postgres / SQLite)

### E. CI/CD Enforcement
- [ ] Compile/validate on PR
- [ ] Docs regeneration + fail if uncommitted
- [ ] Drift gate on deploy
- [ ] Secrets gating (skip if missing, no false failures)

### F. Observability & Audit
- [ ] Write deployment manifests (env, git_sha, bundle_hash, migration_version)
- [ ] Persist export artifacts and diffs
- [ ] Provide reproducible verification commands

## Required Commands (must work)
- `hybrid compile --env dev`
- `hybrid validate --env dev`
- `hybrid plan --env dev`
- `hybrid drift-plan --env dev`
- `hybrid apply --env dev`
- `hybrid export --env dev`
- `hybrid translate --env dev`
- `hybrid promote --chain dev,staging,prod --drift`

## Definition of Done
- All workflows green
- Drift-plan clean for target env(s)
- Exports and templates converge (UI-first PR roundtrip works)
- Docs auto-generated and committed

## Current Implementation Status

### Completed (Session: 2025-12-28)
- ✅ Superset Docker deployment (localhost:8089)
- ✅ Admin user creation and authentication
- ✅ Official example dashboards loaded (11 dashboards, multiple datasets)
- ✅ SQLite sample database created and connected
- ✅ API authentication working

### In Progress
- 🔄 Hybrid CLI tool implementation
- 🔄 Asset template system
- 🔄 Export/normalize/translate workflows

### Pending
- ⏳ Drift detection and reconciliation
- ⏳ CI/CD workflows
- ⏳ Machine-checkable skill tests

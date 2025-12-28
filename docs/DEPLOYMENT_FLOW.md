# Superset GitOps Deployment Flow

## Overview

This document describes the policy-driven GitOps deployment system for Apache Superset, implementing a hybrid control plane with drift detection and environment-specific apply strategies.

## Architecture

```
Git (Source of Truth)
  ↓
DB Migrations + Seed Data
  ↓
Superset Assets (YAML)
  ↓
Drift Detection Gates
  ↓
Deployed Environment
```

## Deployment Order

1. **DB Migrations + Seed** - Recreate database schema and sample data
2. **Compile** - Transform Jinja2 templates into environment-specific YAML bundles
3. **Validate** - Verify YAML structure and required fields
4. **Drift Gate (Pre)** - Check for divergence from Git state
5. **Apply** - Deploy assets to Superset workspace
6. **Drift Gate (Post)** - Verify deployment matches Git state

## Policy Configuration

File: `policy.yaml`

```yaml
db:
  mode: migrations_and_seed
  migrations_dir: db/migrations
  seed_dir: db/seed

apply:
  dev:
    mode: overwrite_git_wins      # Git wins, overwrites runtime changes
    drift_gate: warn              # Warn on drift but continue
  staging:
    mode: strict_fail_on_drift    # Fail on any drift
    drift_gate: fail
  prod:
    mode: strict_fail_on_drift    # Fail on any drift
    drift_gate: fail

export:
  format: superset_cli_yaml       # Use superset-cli for full YAML export

deploy:
  mode: script_with_retry
  steps:
    - db_sync
    - apply_assets
    - drift_check
```

## Scripts

### `scripts/deploy_env.sh` - Main Deployment Entrypoint

Single command deployment with retry logic:

```bash
export POSTGRES_URL="postgres://..."
./scripts/deploy_env.sh dev
```

**Features**:
- Environment-aware drift handling (warn for dev, fail for staging/prod)
- Retry logic with exponential backoff (3 attempts)
- Internal ordering enforcement (DB → Compile → Validate → Apply → Drift)

### `scripts/db_sync.sh` - Database Migration Orchestrator

Applies SQL migrations and seed data in order:

```bash
export POSTGRES_URL="postgres://..."
./scripts/db_sync.sh
```

**Behavior**:
- Applies all `*.sql` files in `db/migrations/` (alphabetical order)
- Applies all `*.sql` files in `db/seed/` (alphabetical order)
- Uses `psql` with `-v ON_ERROR_STOP=1` for transaction safety

### `scripts/export_runtime.sh` - Export from Running Superset

Exports complete asset definitions using superset-cli:

```bash
export BASE_URL="http://localhost:8088"
export SUPERSET_ADMIN_USER="admin"
export SUPERSET_ADMIN_PASS="admin"
./scripts/export_runtime.sh superset_assets
```

**Output**: Full YAML definitions (not REST API metadata)

### `scripts/hybrid/hybrid` - Hybrid Control Plane CLI

Main CLI for asset management:

```bash
# Compile templates to bundles
python3 scripts/hybrid/hybrid compile --env dev

# Validate bundle structure
python3 scripts/hybrid/hybrid validate --env dev

# Check drift
python3 scripts/hybrid/hybrid drift-plan --env dev

# Apply bundle to workspace
python3 scripts/hybrid/hybrid apply --env dev

# Export runtime assets
python3 scripts/hybrid/hybrid export --env dev

# Translate exports to templates
python3 scripts/hybrid/hybrid translate --env dev
```

## Database Schema

### Migrations

**File**: `db/migrations/001_create_examples_schema.sql`

Creates:
- `examples` schema for Superset sample data
- `public.schema_migrations` tracking table

### Seed Data

**File**: `db/seed/001_birth_names_sample.sql`

Creates:
- `examples.birth_names` table with sample data (10 rows)
- Indexes on `year` and `state` columns

## CI/CD Workflow

**File**: `.github/workflows/deploy.yml`

```yaml
on:
  pull_request:
  push:
    branches: [ main ]

jobs:
  dev:
    # Deploy to dev on all branches (drift warn)
    ./scripts/deploy_env.sh dev

  staging_prod:
    # Deploy to staging/prod on main only (strict drift enforcement)
    ./scripts/deploy_env.sh staging
    ./scripts/deploy_env.sh prod
```

## Implementation Status

### ✅ Completed

1. **Policy Configuration** - `policy.yaml` with environment-specific modes
2. **Deployment Orchestrator** - `scripts/deploy_env.sh` with retry logic
3. **Database Management** - Migrations + seed orchestrator
4. **Export Pipeline** - `scripts/export_runtime.sh` using superset-cli
5. **Hybrid CLI** - Skeleton with policy-aware stubs
6. **CI/CD Workflow** - Simplified GitHub Actions workflow
7. **Database Schema** - Examples schema + tracking tables

### ⏳ Stub Implementations (Policy-Aware)

1. **`hybrid compile`** - Gracefully handles missing templates
2. **`hybrid validate`** - Gracefully handles missing bundles
3. **`hybrid apply`** - Reads policy, acknowledges apply mode
4. **`hybrid drift-plan`** - Reads policy, acknowledges drift gate

### 📝 Future Work

1. **Full `apply` Implementation** - Deploy assets in order (databases → datasets → charts → dashboards)
2. **Full `drift-plan` Implementation** - Export runtime state, compare with Git bundle, report differences
3. **`translate` Implementation** - Convert exports to Jinja2 templates
4. **Asset Templates** - Create Jinja2 templates for databases, datasets, charts, dashboards

## Testing Local Deployment

```bash
# Set database connection
export POSTGRES_URL="postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:5432/postgres?sslmode=require"

# Run deployment
./scripts/deploy_env.sh dev

# Expected output:
# === ENV=dev ===
# === 1) DB sync ===
# ✅ DB_SYNC_OK
# === 2) Compile+Validate ===
# ✅ Compilation complete
# ✅ Validation complete
# === 3) Drift gate (pre) ===
# ✅ No drift detected (policy: warn)
# === 4) Apply (Git wins for managed assets) ===
# ✅ Apply complete
# === 5) Drift gate (post) ===
# ✅ No drift detected (policy: warn)
# DEPLOY_OK (dev)
```

## Key Design Decisions

1. **Separation of Concerns**: DB schema/seed managed separately from Superset assets (YAML)
2. **Policy-Driven**: Environment-specific apply modes and drift gates
3. **Deterministic Diffs**: Git is single source of truth, reproducible deployments
4. **Script-Based Ordering**: Single entrypoint enforces correct deployment order
5. **Graceful Degradation**: Stubs handle missing templates/bundles without failing
6. **Retry Logic**: Exponential backoff for transient failures

## References

- **Policy File**: `/Users/tbwa/insightpulse-devops-dashboard/policy.yaml`
- **Main Deployment Script**: `/Users/tbwa/insightpulse-devops-dashboard/scripts/deploy_env.sh`
- **Hybrid CLI**: `/Users/tbwa/insightpulse-devops-dashboard/scripts/hybrid/hybrid`
- **Database Migrations**: `/Users/tbwa/insightpulse-devops-dashboard/db/migrations/`
- **Seed Data**: `/Users/tbwa/insightpulse-devops-dashboard/db/seed/`

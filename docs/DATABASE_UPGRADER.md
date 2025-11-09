# InsightPulse Database Upgrader

Comprehensive database migration system for InsightPulse Odoo 19 + Supabase + Superset stack.

## Overview

The Database Upgrader provides:

- **Schema Migrations**: Track and apply Supabase schema changes
- **Superset Integration**: Initialize Superset dashboards and datasets
- **Sample Data**: Install test/demo data for development
- **App Installation**: Coordinate Odoo module installation
- **Version Tracking**: Flyway/Liquibase-style migration tracking
- **Idempotency**: Safe to run multiple times

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DB Upgrader System                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  Migration   │  │  Superset    │  │  Sample      │    │
│  │  Tracker     │  │  Importer    │  │  Data        │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
│         │                 │                 │             │
│         ▼                 ▼                 ▼             │
│  ┌──────────────────────────────────────────────────┐    │
│  │          Supabase PostgreSQL Database            │    │
│  │                                                  │    │
│  │  ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌─────┐ │    │
│  │  │superset │ │   ops   │ │analytics │ │ ai  │ │    │
│  │  │ schema  │ │ schema  │ │  schema  │ │ ... │ │    │
│  │  └─────────┘ └─────────┘ └──────────┘ └─────┘ │    │
│  └──────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install psycopg2-binary requests pyyaml

# Set database connection
export POSTGRES_URL="postgresql://user:pass@host:port/dbname"

# Or use Supabase URL
export SUPABASE_DB_URL="postgresql://postgres.xxx:pass@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
```

### Basic Usage

```bash
# Check current migration status
python3 scripts/db_upgrader.py status

# Run all pending migrations
python3 scripts/db_upgrader.py upgrade

# Full setup (migrations + Superset + sample data)
python3 scripts/db_upgrader.py full-setup

# Dry run (see what would be executed)
python3 scripts/db_upgrader.py upgrade --dry-run
```

## Commands

### `status`

Show current migration status and pending migrations.

```bash
python3 scripts/db_upgrader.py status
```

Output:
```
======================================================================
DATABASE MIGRATION STATUS
======================================================================

Applied migrations: 9

VERSION      DESCRIPTION                    DATE         STATUS
----------------------------------------------------------------------
001          Ipai Medallion                 2025-11-01   ✅
002          Schema Separation              2025-11-02   ✅
003          Saas Core Schema               2025-11-03   ✅
004          Enable Extensions              2025-11-04   ✅
005          Training Infrastructure        2025-11-05   ✅

✅ All migrations are up to date
======================================================================
```

### `upgrade`

Apply all pending migrations.

```bash
# Development environment
python3 scripts/db_upgrader.py upgrade --env development

# Production environment (adds SSL mode)
python3 scripts/db_upgrader.py upgrade --env production

# Dry run (preview only)
python3 scripts/db_upgrader.py upgrade --dry-run
```

### `init-superset`

Initialize Superset metadata tables and analytics views.

```bash
python3 scripts/db_upgrader.py init-superset
```

This will:
1. Run `superset db upgrade` to create Superset metadata tables
2. Create analytics views from `superset/datasets/*.sql`
3. Set up materialized views for dashboard queries

### `install-sample-data`

Install sample data for testing and development.

```bash
# Install all sample data
python3 scripts/db_upgrader.py install-sample-data --schema all

# Install specific schema
python3 scripts/db_upgrader.py install-sample-data --schema ops
python3 scripts/db_upgrader.py install-sample-data --schema analytics
```

Sample data includes:
- `ops.task_queue`: Deployment and build tasks
- `ops.workflow_runs`: CI/CD workflow history
- `analytics.*`: Sales, customer, product demo data

### `full-setup`

Complete database setup in one command.

```bash
python3 scripts/db_upgrader.py full-setup --env development
```

Execution order:
1. Create all schemas (superset, ops, analytics, ai, scout_*)
2. Apply all pending migrations
3. Initialize Superset metadata
4. Create analytics views
5. Install sample data

## Migration Files

### Naming Convention

Migrations follow this naming pattern:

```
{version}_{description}.sql

Examples:
  001_ipai_medallion.sql
  002_schema_separation.sql
  20251105_github_installations.sql
```

Supported version formats:
- `001`, `002`, `003` (three-digit sequential)
- `20251105` (date-based YYYYMMDD)
- Any numeric prefix followed by underscore

### Creating New Migrations

1. Create a new SQL file in `supabase/migrations/`:

```bash
touch supabase/migrations/011_add_billing_tables.sql
```

2. Write idempotent SQL:

```sql
-- Migration: Add billing tables
-- Purpose: Support subscription billing

-- Create billing schema
CREATE SCHEMA IF NOT EXISTS billing;

-- Create subscription table
CREATE TABLE IF NOT EXISTS billing.subscriptions (
    id BIGSERIAL PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    plan TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_subscriptions_customer
    ON billing.subscriptions(customer_id);

-- Permissions
GRANT USAGE ON SCHEMA billing TO postgres, service_role;
GRANT ALL ON billing.subscriptions TO postgres, service_role;
```

3. Test the migration:

```bash
# Dry run first
python3 scripts/db_upgrader.py upgrade --dry-run

# Apply
python3 scripts/db_upgrader.py upgrade
```

### Migration Best Practices

**✅ DO:**
- Use `IF NOT EXISTS` clauses
- Add comments explaining purpose
- Include rollback instructions in comments
- Test on development database first
- Keep migrations small and focused

**❌ DON'T:**
- Modify existing migration files after they've been applied
- Include data that changes frequently
- Use hardcoded IDs or timestamps
- Run destructive operations without backups

## Superset Integration

### Dashboard Import/Export

The system includes a Superset dashboard importer for managing dashboards as code.

```bash
# Bootstrap CI/CD dashboard
python3 scripts/superset_dashboard_importer.py bootstrap

# Import a dashboard
python3 scripts/superset_dashboard_importer.py import --file dashboards/ci-cd-metrics.yaml

# Export a dashboard
python3 scripts/superset_dashboard_importer.py export --dashboard-id 1 --output backup.yaml

# List all dashboards
python3 scripts/superset_dashboard_importer.py list
```

### Analytics Views

Analytics views for Superset dashboards are defined in `superset/datasets/*.sql`:

```
superset/datasets/
├── 01_mv_sales_kpi_daily.sql
├── 02_mv_product_performance.sql
├── 03_fact_sales.sql
├── 04_mv_customer_ltv.sql
├── 05_fact_purchase.sql
├── 06_fact_invoice.sql
├── 07_fact_expense.sql
├── 08_mv_expense_compliance.sql
├── 09_dim_customer.sql
└── 10_dim_employee.sql
```

These views are automatically created when running:
```bash
python3 scripts/db_upgrader.py init-superset
```

## Sample Data

### Available Datasets

Sample data is organized by schema:

```
scripts/sample_data/
├── ops/
│   ├── workflow_runs.json       # 25 CI/CD workflow executions
│   └── task_queue.json          # Deployment and build tasks
├── analytics/
│   └── (populated from Odoo exports)
└── ai/
    └── training_runs.json       # Model training history
```

### Custom Sample Data

Generate custom sample data:

```bash
# Generate 100 workflow runs
python3 scripts/generate_sample_data.py --schema ops --rows 100

# Generate 365 days of analytics data
python3 scripts/generate_sample_data.py --schema analytics --days 365
```

### Resetting Sample Data

To remove all sample data:

```bash
# Truncate all sample data tables
python3 scripts/db_upgrader.py reset-sample-data
```

This preserves schema structure and migrations.

## Version Tracking

### Schema Version Table

The upgrader tracks migrations in `public.schema_version`:

```sql
CREATE TABLE public.schema_version (
    version TEXT PRIMARY KEY,
    description TEXT,
    migration_file TEXT NOT NULL,
    checksum TEXT NOT NULL,              -- SHA256 hash
    installed_by TEXT DEFAULT CURRENT_USER,
    installed_at TIMESTAMPTZ DEFAULT NOW(),
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE
);
```

### Checksum Verification

Each migration's checksum is stored and verified on subsequent runs.

If a migration file is modified after being applied:
```
⚠️  Migration 002 checksum mismatch!
   Applied: abc12345...
   Current: def67890...
   This migration was modified after being applied.
```

This prevents silent corruption of applied migrations.

## Testing

### Running Tests

```bash
# Run all tests
python3 scripts/test_db_upgrader.py

# Run with verbose output
python3 scripts/test_db_upgrader.py -v

# Run specific test
python3 scripts/test_db_upgrader.py TestMigrations.test_migration_tracking
```

### Test Database Setup

Configure a test database for integration tests:

```bash
export TEST_POSTGRES_URL="postgresql://postgres:password@localhost:5432/insightpulse_test"
```

### Test Coverage

The test suite includes:

- **Unit Tests**
  - Migration filename parsing
  - Checksum calculation
  - Version comparison

- **Integration Tests**
  - Schema creation
  - Migration execution
  - Version tracking
  - Idempotency verification

- **Verification Tests**
  - Migration file naming conventions
  - SQL syntax validation
  - Checksum integrity

## Environments

The upgrader supports multiple environments:

```bash
# Development (no SSL)
python3 scripts/db_upgrader.py upgrade --env development

# Staging
python3 scripts/db_upgrader.py upgrade --env staging

# Production (SSL required)
python3 scripts/db_upgrader.py upgrade --env production
```

### Environment Configuration

Set environment variables for each environment:

**Development:**
```bash
export POSTGRES_URL="postgresql://postgres:password@localhost:5432/postgres"
```

**Staging:**
```bash
export POSTGRES_URL="postgresql://postgres:pass@staging-db:5432/postgres?sslmode=prefer"
```

**Production:**
```bash
export POSTGRES_URL="postgresql://postgres.spdtwktxdalcfigzeqrz:${DB_PASSWORD}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
```

## Troubleshooting

### Connection Issues

```
❌ Failed to connect to database: connection refused
```

**Solution:**
1. Verify database is running
2. Check connection string
3. Verify network access
4. Test with `psql`:
   ```bash
   psql "$POSTGRES_URL"
   ```

### Migration Failures

```
❌ Failed: relation "xyz" already exists
```

**Solution:**
1. Ensure migration uses `IF NOT EXISTS`
2. Check for partially applied migrations
3. Review database state:
   ```bash
   python3 scripts/db_upgrader.py status
   ```

### Checksum Mismatch

```
⚠️  Migration 002 checksum mismatch!
```

**Solution:**
1. Don't modify applied migrations
2. Create a new migration to fix issues
3. Document why checksum changed

### Superset Connection

```
⚠️  Superset command not found
```

**Solution:**
1. Install Superset: `pip install apache-superset`
2. Or run manually: `superset db upgrade`
3. Skip Superset init: use `upgrade` instead of `full-setup`

## CI/CD Integration

### GitHub Actions

```yaml
name: Database Migration

on:
  push:
    branches: [main]
    paths:
      - 'supabase/migrations/**'

jobs:
  migrate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install psycopg2-binary

      - name: Run migrations
        env:
          POSTGRES_URL: ${{ secrets.PRODUCTION_DB_URL }}
        run: |
          python3 scripts/db_upgrader.py upgrade --env production
```

### Pre-deployment Checks

Before deploying to production:

```bash
# 1. Test on staging
python3 scripts/db_upgrader.py upgrade --env staging --dry-run

# 2. Verify migrations
python3 scripts/test_db_upgrader.py

# 3. Backup production database
pg_dump "$PROD_DB_URL" > backup_$(date +%Y%m%d).sql

# 4. Apply to production
python3 scripts/db_upgrader.py upgrade --env production
```

## Rollback Strategy

### Current Status

Full automated rollback is not yet implemented.

For now, use manual rollback:

```bash
# 1. Restore from backup
psql "$POSTGRES_URL" < backup_20251109.sql

# 2. Or manually revert changes
psql "$POSTGRES_URL" -f migrations/rollback/011_rollback.sql
```

### Planned Rollback

Future versions will support:

```bash
# Rollback to specific version
python3 scripts/db_upgrader.py rollback --to-version 010

# Rollback last migration
python3 scripts/db_upgrader.py rollback --steps 1
```

## Best Practices

### Development Workflow

1. **Create migration locally**
   ```bash
   touch supabase/migrations/011_new_feature.sql
   ```

2. **Test on local database**
   ```bash
   python3 scripts/db_upgrader.py upgrade --env development --dry-run
   python3 scripts/db_upgrader.py upgrade --env development
   ```

3. **Verify changes**
   ```bash
   psql $DEV_DB_URL -c "\d+ analytics.new_table"
   ```

4. **Commit and push**
   ```bash
   git add supabase/migrations/011_new_feature.sql
   git commit -m "feat: add new_feature tables"
   git push
   ```

5. **Deploy to staging**
   ```bash
   python3 scripts/db_upgrader.py upgrade --env staging
   ```

6. **Deploy to production**
   ```bash
   python3 scripts/db_upgrader.py upgrade --env production
   ```

### Safety Checklist

Before running migrations in production:

- [ ] Tested on local development database
- [ ] Tested on staging environment
- [ ] Backup created and verified
- [ ] Migration is idempotent (uses `IF NOT EXISTS`)
- [ ] Team notified of planned changes
- [ ] Rollback plan documented
- [ ] Monitoring in place to detect issues

## Advanced Usage

### Custom Migration Directories

Override the default migrations directory:

```python
import os
os.environ["MIGRATIONS_DIR"] = "/path/to/custom/migrations"
```

### Programmatic Usage

Use the upgrader in Python scripts:

```python
from db_upgrader import (
    get_db_connection,
    init_version_table,
    get_pending_migrations,
    execute_migration
)

# Connect
conn = get_db_connection("production")

# Initialize
init_version_table(conn)

# Get pending migrations
pending = get_pending_migrations(conn)

# Apply migrations
for version, file_path in pending:
    execute_migration(conn, version, file_path, dry_run=False)

conn.close()
```

### Integration with Odoo

The upgrader can coordinate with Odoo module installation:

```python
from db_upgrader import install_odoo_apps

# After migrations complete
install_odoo_apps(
    app_list=["sale_management", "account", "purchase"],
    odoo_url="https://erp.insightpulseai.net",
    api_key=os.getenv("ODOO_API_KEY")
)
```

## Support

### Documentation

- Database Upgrader: `docs/DATABASE_UPGRADER.md` (this file)
- Sample Data: `scripts/sample_data/README.md`
- Superset Integration: `docs/SUPERSET_INTEGRATION.md`

### Troubleshooting

If you encounter issues:

1. Check status: `python3 scripts/db_upgrader.py status`
2. Review logs: check script output for errors
3. Verify database connection: `psql "$POSTGRES_URL"`
4. Run tests: `python3 scripts/test_db_upgrader.py`

### Getting Help

- Open an issue: [GitHub Issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- Check docs: `docs/` directory
- Review migration history: `SELECT * FROM public.schema_version;`

---

**Related Documentation:**
- [Supabase Migrations](../supabase/migrations/README.md)
- [Superset Datasets](../superset/datasets/README.md)
- [Sample Data](../scripts/sample_data/README.md)

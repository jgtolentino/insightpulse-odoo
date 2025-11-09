# Database Upgrader - Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install psycopg2-binary requests pyyaml
```

### 2. Set Database Connection

```bash
# Using Supabase
export POSTGRES_URL="postgresql://postgres.xxx:password@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Or local database
export POSTGRES_URL="postgresql://postgres:password@localhost:5432/postgres"
```

### 3. Run Full Setup

```bash
cd /home/user/insightpulse-odoo

# See what will be executed
python3 scripts/db_upgrader.py status

# Run all migrations + Superset + sample data
python3 scripts/db_upgrader.py full-setup
```

## Common Commands

```bash
# Check migration status
python3 scripts/db_upgrader.py status

# Apply pending migrations only
python3 scripts/db_upgrader.py upgrade

# Initialize Superset dashboards
python3 scripts/db_upgrader.py init-superset

# Install sample data
python3 scripts/db_upgrader.py install-sample-data --schema all

# Run tests
python3 scripts/test_db_upgrader.py
```

## What Gets Created

### Schemas

- **superset** - Apache Superset metadata (dashboards, charts)
- **ops** - Operations data (tasks, workflows, CI/CD metrics)
- **analytics** - Data warehouse (sales, customers, products)
- **ai** - AI training data and embeddings
- **scout_bronze/silver/gold** - ELT data layers

### Sample Data

- **ops.workflow_runs** - 25 CI/CD workflow executions
- **ops.task_queue** - Deployment and build tasks
- **analytics.*** - Sales and customer demo data

### Superset Dashboards

- **CI/CD Metrics** - Workflow success rates, deployment frequency
- **Sales KPIs** - Daily sales, revenue, customer metrics
- **Finance Compliance** - Expense tracking, BIR compliance

## Verify Installation

```bash
# Check that all schemas exist
psql "$POSTGRES_URL" -c "\dn"

# Check that migrations are tracked
psql "$POSTGRES_URL" -c "SELECT version, description, installed_at FROM public.schema_version ORDER BY installed_at;"

# Check sample data
psql "$POSTGRES_URL" -c "SELECT COUNT(*) FROM ops.workflow_runs;"

# List Superset dashboards
python3 scripts/superset_dashboard_importer.py list
```

## Next Steps

1. **Configure Superset**
   - Access Superset at http://localhost:8088
   - Login with admin/admin
   - View CI/CD Metrics dashboard

2. **Connect Odoo**
   - Configure Odoo to write to analytics schema
   - Set up Supabase sync module
   - Enable real-time data feeds

3. **Customize Dashboards**
   - Create custom analytics views
   - Build business-specific dashboards
   - Set up alerts and subscriptions

## Troubleshooting

**Connection failed?**
```bash
# Test database connection
psql "$POSTGRES_URL" -c "SELECT version();"
```

**Migration failed?**
```bash
# Check status to see which migration failed
python3 scripts/db_upgrader.py status

# Review the failed migration file
cat supabase/migrations/XXX_failed_migration.sql
```

**Superset not found?**
```bash
# Skip Superset initialization
python3 scripts/db_upgrader.py upgrade  # migrations only

# Or install Superset
pip install apache-superset
```

## Full Documentation

See `docs/DATABASE_UPGRADER.md` for complete documentation.

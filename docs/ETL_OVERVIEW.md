# ETL Infrastructure Overview

This document provides a high-level overview of the ETL (Extract, Transform, Load) infrastructure for InsightPulse Odoo.

## Quick Links

- 📊 **[ETL Blockers Report](../ETL_BLOCKERS_REPORT.md)** - Comprehensive analysis of issues and remediation
- 🔧 **[CLI Reference](ETL_CLI_REFERENCE.md)** - All ETL commands and operations
- 📁 **[dbt Models](../dbt/models/)** - Data transformation models
- 🔄 **[Airbyte Config](../airbyte/odoo-to-supabase.yml)** - CDC sync configuration

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Odoo PostgreSQL                         │
│              (Source of Truth - Production)                 │
│   Tables: res_partner, account_move, sale_order, etc.      │
└────────────┬────────────────────────────────────────────────┘
             │
             │ CDC Sync (Airbyte)
             │ • 17 tables, 5-minute intervals
             │ • Incremental with write_date cursor
             │
             ↓
┌─────────────────────────────────────────────────────────────┐
│                   Supabase PostgreSQL                       │
│                  (Analytics Warehouse)                      │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  odoo_raw schema                                     │  │
│  │  • Raw synced data (mirror of Odoo)                 │  │
│  │  • 17+ tables updated every 5 minutes               │  │
│  └──────────────────────────────────────────────────────┘  │
│                      │                                      │
│                      │ dbt transformations                  │
│                      │ (staging → intermediate → semantic)  │
│                      ↓                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  staging schema                                      │  │
│  │  • Cleaned, typed, business-friendly                │  │
│  │  • stg_partners, stg_invoices, stg_sales_orders     │  │
│  └──────────────────────────────────────────────────────┘  │
│                      │                                      │
│                      ↓                                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  intermediate / semantic / metrics schemas           │  │
│  │  • Business aggregations                            │  │
│  │  • KPI calculations                                 │  │
│  │  • Wide tables for BI tools                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────┬───────────────────────────────────────────────┘
              │
              │ SQL queries
              ↓
┌─────────────────────────────────────────────────────────────┐
│                  Apache Superset                            │
│              (Business Intelligence Layer)                   │
│  • Dashboards, charts, SQL Lab                             │
│  • Finance, procurement, sales analytics                   │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Extract (Airbyte)
- **Source**: Odoo PostgreSQL (`ODOO_DB_HOST`)
- **Destination**: Supabase PostgreSQL (`SUPABASE_DB_HOST`)
- **Method**: CDC (Change Data Capture) using `write_date` cursor
- **Frequency**: Every 5 minutes
- **Tables**: 17 tables (see [Airbyte config](../airbyte/odoo-to-supabase.yml))

**Status**: ✅ Configured, ⚠️ Runtime not validated

### 2. Transform (dbt)
- **Input**: `odoo_raw` schema
- **Output**: `staging`, `intermediate`, `semantic`, `metrics` schemas
- **Tool**: dbt (Data Build Tool)
- **Models**: 3 staging models (partners, invoices, sales orders)
- **Schedule**: Daily (recommended)

**Status**: ⚠️ Models created, needs deployment

### 3. Load (Superset)
- **Input**: Transformed tables in Supabase
- **Tool**: Apache Superset
- **Features**: Dashboards, SQL Lab, alerts
- **Access**: Row-level security (RLS) by company_id

**Status**: ✅ Deployed and running

## Bidirectional Sync (Supabase → Odoo)

For write-back scenarios (e.g., approvals from BI tool):

```
Supabase Change → ops.odoo_outbox → Outbox Worker → Odoo API
```

- **Queue**: `ops.odoo_outbox` table
- **Worker**: `scripts/outbox-worker.py`
- **Method**: Idempotent upserts via Odoo XML-RPC

**Status**: ⚠️ Schema created, worker skeleton exists

## Components

| Component | Purpose | Status | Location |
|-----------|---------|--------|----------|
| **Airbyte** | CDC sync Odoo → Supabase | ⚠️ Configured | `airbyte/` |
| **dbt** | Data transformations | ⚠️ Partial | `dbt/` |
| **Outbox Worker** | Supabase → Odoo sync | ⚠️ Skeleton | `scripts/outbox-worker.py` |
| **Superset** | BI dashboards | ✅ Deployed | `services/superset/` |
| **Health Check** | ETL monitoring | ✅ Working | `scripts/check-etl-health.sh` |

## Getting Started

### Prerequisites
```bash
# Environment variables
export ODOO_DB_HOST="odoo-db.internal"
export ODOO_DB_NAME="odoo"
export ODOO_DB_USER="odoo"
export ODOO_DB_PASSWORD="***"
export SUPABASE_DB_URL="postgresql://..."
export SUPABASE_PROJECT_URL="https://xxx.supabase.co"
```

### 1. Check ETL Health
```bash
./scripts/check-etl-health.sh
```

### 2. Deploy Airbyte (if not already running)
```bash
# See Airbyte documentation for deployment
# https://docs.airbyte.com/deploying-airbyte
```

### 3. Configure dbt
```bash
# Copy profiles example
cp dbt/profiles.yml.example ~/.dbt/profiles.yml

# Edit with your credentials
vim ~/.dbt/profiles.yml

# Test connection
cd dbt && dbt debug

# Run models
dbt run --target dev
```

### 4. Start Outbox Worker (when ready)
```bash
# Dry-run first
python scripts/outbox-worker.py --once --dry-run

# Production mode
python scripts/outbox-worker.py --daemon
```

### 5. Access Superset
```bash
# URL: http://localhost:8088 (or production URL)
# Login with configured credentials
```

## Monitoring

### Health Checks
```bash
# Run health check
./scripts/check-etl-health.sh

# Check outbox queue depth
psql "$SUPABASE_DB_URL" -c "SELECT COUNT(*) FROM ops.odoo_outbox WHERE status = 'queued';"

# View failed syncs
psql "$SUPABASE_DB_URL" -c "SELECT * FROM ops.odoo_sync_runs WHERE status = 'failed' ORDER BY created_at DESC LIMIT 10;"
```

### Scheduled Jobs (Recommended)
```cron
# Daily dbt run (3 AM)
0 3 * * * cd /path/to/dbt && dbt run --target prod

# Hourly health check
0 * * * * /path/to/scripts/check-etl-health.sh

# Every 5 minutes: outbox processing (if not running as daemon)
*/5 * * * * python /path/to/scripts/outbox-worker.py --once
```

## Data Quality

### dbt Tests
```bash
# Run all tests
cd dbt && dbt test

# Test specific model
dbt test --models staging.stg_partners
```

### Row Count Validation
```sql
-- Compare row counts: Odoo vs Supabase
SELECT 
  'odoo' AS source,
  relname AS table_name,
  n_live_tup AS row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
  AND relname IN ('res_partner', 'account_move', 'sale_order')

UNION ALL

SELECT 
  'supabase' AS source,
  table_name,
  -- Query row count from odoo_raw schema
FROM odoo_raw.table_name;
```

## Troubleshooting

### Sync Lag
```bash
# Check last sync time for each stream
# TODO: Implement in validate-airbyte-sync.sh
```

### Outbox Queue Growing
```bash
# Check worker status
ps aux | grep outbox-worker

# Check for errors
tail -f /tmp/outbox-worker.log

# Manually process queue
python scripts/outbox-worker.py --once --batch-size 50
```

### dbt Errors
```bash
# Check dbt logs
cat ~/.dbt/logs/dbt.log

# Test connection
dbt debug

# Compile without running
dbt compile --models staging.stg_partners
```

## Security

### Credentials
- **Never** commit credentials to git
- Use environment variables or secrets manager
- Rotate passwords regularly (quarterly)

### Access Control
- Supabase: Use Row-Level Security (RLS)
- Superset: Configure role-based access
- Airbyte: Restrict API access

### Audit Logging
```sql
-- Enable PostgreSQL query logging
ALTER DATABASE postgres SET log_statement = 'all';

-- View access logs
SELECT * FROM pg_stat_activity WHERE usename = 'superset';
```

## Performance Optimization

### Indexes
```sql
-- Add indexes for common queries
CREATE INDEX idx_partners_customer ON staging.stg_partners(is_company, customer_rank);
CREATE INDEX idx_invoices_overdue ON staging.stg_invoices(is_overdue, due_date);
CREATE INDEX idx_orders_pending ON staging.stg_sales_orders(is_confirmed, invoice_status);
```

### Materialized Views
```sql
-- For frequently accessed aggregations
CREATE MATERIALIZED VIEW metrics.monthly_revenue AS
SELECT 
  DATE_TRUNC('month', invoice_date) AS month,
  SUM(amount_total) AS total_revenue
FROM staging.stg_invoices
WHERE move_category = 'customer'
  AND is_posted = true
GROUP BY 1;

-- Refresh daily
REFRESH MATERIALIZED VIEW metrics.monthly_revenue;
```

## Roadmap

### Immediate (Current PR)
- [x] ETL blockers report
- [x] Health check script
- [x] CLI reference documentation
- [x] Outbox worker skeleton
- [x] Basic dbt models (3 staging models)

### Short-term (Next Sprint)
- [ ] Complete outbox worker Odoo integration
- [ ] Add Airbyte sync validator
- [ ] Implement knowledge ingestion
- [ ] Add intermediate/semantic models
- [ ] Set up monitoring dashboard

### Medium-term (Q1 2026)
- [ ] Automated data quality checks
- [ ] Advanced transformations (metrics layer)
- [ ] End-to-end integration tests
- [ ] Data catalog/lineage documentation
- [ ] Performance optimization (indexes, MVs)

## Support

- **Documentation**: [ETL Blockers Report](../ETL_BLOCKERS_REPORT.md)
- **CLI Reference**: [ETL CLI Reference](ETL_CLI_REFERENCE.md)
- **Issues**: Open GitHub issue with `etl` label
- **Slack**: #data-engineering (if available)

## Contributing

When making changes to ETL infrastructure:
1. Update documentation (this file, blockers report, CLI reference)
2. Run health checks before/after
3. Test in staging environment first
4. Document rollback procedure
5. Update CHANGELOG

---

**Last Updated**: 2026-02-05  
**Maintainer**: DevOps & Data Engineering Teams

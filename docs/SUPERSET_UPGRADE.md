# Superset 4.1.1 Upgrade Guide

## Overview

This guide covers the upgrade from Superset 3.1.0 to 4.1.1 with pre-configured Finance SSC dashboards for InsightPulse Odoo.

## What's New in 4.1.1

- **Enhanced Performance**: Improved query caching and dashboard load times
- **Better Security**: Updated dependencies and security patches
- **New Chart Types**: Additional visualization options
- **Improved UX**: Streamlined dashboard creation and editing
- **Bug Fixes**: Resolved issues from 3.x series

## Pre-Deployment Checklist

### 1. Backup Existing Data

```bash
# Backup Superset metadata database
docker-compose -f deploy/superset.compose.yml exec superset-db \
  pg_dump -U superset superset > superset_backup_$(date +%Y%m%d).sql

# Backup Superset home directory
docker cp superset:/app/superset_home ./superset_home_backup_$(date +%Y%m%d)
```

### 2. Review Configuration

Ensure the following are configured in `deploy/superset.env`:

```env
# Required
SUPERSET_SECRET_KEY=<your-secret-key>
SQLALCHEMY_DATABASE_URI=postgresql://...
REDIS_URL=redis://superset-redis:6379/0

# Optional
SUPERSET_POSTGRES_DB=superset
SUPERSET_POSTGRES_USER=superset
SUPERSET_POSTGRES_PASSWORD=<secure-password>
```

### 3. Database Prerequisites

Create the required views in your Odoo/Supabase database:

```bash
psql "$POSTGRES_URL" -f deploy/sql/superset_views.sql
```

## Deployment Steps

### Option 1: Local Docker Deployment

```bash
# Run the deployment script
./scripts/deploy-superset.sh
```

This script will:
1. ✅ Check prerequisites (Docker, Docker Compose)
2. ✅ Pull Superset 4.1.1 image
3. ✅ Stop existing containers
4. ✅ Start upgraded services
5. ✅ Initialize example dashboards
6. ✅ Verify health

### Option 2: DigitalOcean App Platform

```bash
# Update DigitalOcean app spec
doctl apps update bc1764a5-b48e-4bec-aa72-8a22cab141bc \
  --spec infra/do/superset.yaml

# Trigger deployment
doctl apps create-deployment bc1764a5-b48e-4bec-aa72-8a22cab141bc --force-rebuild

# Monitor logs
doctl apps logs bc1764a5-b48e-4bec-aa72-8a22cab141bc --follow
```

### Option 3: Manual Deployment

```bash
# Navigate to deploy directory
cd deploy

# Pull new image
docker-compose -f superset.compose.yml pull

# Stop existing services
docker-compose -f superset.compose.yml down

# Start with new image
docker-compose -f superset.compose.yml up -d

# Check logs
docker-compose -f superset.compose.yml logs -f superset
```

## Post-Deployment Verification

### 1. Health Check

```bash
# Local
curl http://localhost:8088/health

# Production
curl https://superset.insightpulseai.net/health

# Expected response
{"ok": true}
```

### 2. Access Dashboard

- **Local**: http://localhost:8088
- **Production**: https://superset.insightpulseai.net

Default credentials:
- Username: `admin`
- Password: `admin` (change immediately!)

### 3. Verify Example Dashboard

Navigate to: `/superset/dashboard/finance-ssc-executive/`

Expected charts:
1. ✅ Expense by Agency - Current Month (Pie Chart)
2. ✅ BIR Forms Submitted - This Quarter (Big Number)
3. ✅ Expense Approvals - Last 30 Days (Line Chart)
4. ✅ Top 10 Expense Categories (Bar Chart)

### 4. Test Database Connection

```bash
# Using Superset CLI
docker-compose -f deploy/superset.compose.yml exec superset \
  superset test-db

# Or via UI
# Navigate to: Data > Databases > Test Connection
```

## Example Dashboards

### Finance SSC Executive Dashboard

**Purpose**: Multi-agency Finance Shared Service Center overview with BIR compliance metrics

**Metrics**:
- Total expenses by agency (current month)
- BIR forms submitted (current quarter)
- Expense approval timeline (last 30 days)
- Top expense categories

**Data Sources**:
- `superset_expense_summary` view
- `superset_bir_compliance` view
- `superset_agency_metrics` view

**Refresh Frequency**: 5 minutes (300 seconds)

### Customization

To customize the example dashboard:

1. Navigate to dashboard: `/superset/dashboard/finance-ssc-executive/`
2. Click **Edit Dashboard**
3. Modify charts, add filters, adjust layout
4. Click **Save**

To create new charts:

1. Navigate to: **Charts > + Chart**
2. Select dataset (e.g., `superset_expense_summary`)
3. Choose visualization type
4. Configure metrics and dimensions
5. Click **Save**

## Database Connection Details

### Supabase (SpendFlow)

```yaml
Database Name: InsightPulse Odoo
SQLAlchemy URI: postgresql://postgres.spdtwktxdalcfigzeqrz:${PASSWORD}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
Expose in SQL Lab: Yes
Allow Run Async: Yes
Allow DML: No (read-only for safety)
```

### Available Views

1. **superset_expense_summary**
   - Fields: expense_name, date_submitted, total_amount, company_name, employee_name, status_label
   - Filters: year, month, quarter, state

2. **superset_bir_compliance**
   - Fields: form_type, submission_date, status, tax_amount, company_name, form_description
   - Filters: year, quarter, status, form_type

3. **superset_agency_metrics**
   - Fields: company_name, total_expenses, total_expense_amount, avg_expense_amount, approved_count
   - Aggregated metrics for performance tracking

## Troubleshooting

### Issue: Container fails to start

```bash
# Check logs
docker-compose -f deploy/superset.compose.yml logs superset

# Common causes:
# 1. Database connection issues
# 2. Invalid SECRET_KEY
# 3. Port 8088 already in use
```

**Solution**:
```bash
# Check database connectivity
psql "$SQLALCHEMY_DATABASE_URI" -c "SELECT 1"

# Generate new SECRET_KEY
openssl rand -base64 42

# Check port availability
lsof -i :8088
```

### Issue: Dashboards not loading

**Solution**:
```bash
# Clear Superset cache
docker-compose -f deploy/superset.compose.yml exec superset \
  superset fab reset-cache

# Rebuild dashboard
docker-compose -f deploy/superset.compose.yml exec superset \
  python3 /app/pythonpath/init-dashboards.py
```

### Issue: Database connection timeout

**Solution**:
```bash
# Check Supabase connection pooler status
psql "$SQLALCHEMY_DATABASE_URI" -c "SELECT version()"

# Verify network connectivity
curl -I https://aws-1-us-east-1.pooler.supabase.com:6543

# Update connection string with timeout
postgresql://...?connect_timeout=30&sslmode=require
```

### Issue: Charts showing no data

**Solution**:
```bash
# Verify views exist
psql "$POSTGRES_URL" -c "\dv superset_*"

# Check view permissions
psql "$POSTGRES_URL" -c "\dp superset_*"

# Re-run view creation script
psql "$POSTGRES_URL" -f deploy/sql/superset_views.sql
```

## Rollback Procedure

If the upgrade fails:

```bash
# Stop current version
docker-compose -f deploy/superset.compose.yml down

# Edit superset.compose.yml and change image back to 3.1.0
sed -i 's/4.1.1/3.1.0/g' deploy/superset.compose.yml

# Restore backup
docker-compose -f deploy/superset.compose.yml up -d
docker-compose -f deploy/superset.compose.yml exec -T superset-db \
  psql -U superset superset < superset_backup_YYYYMMDD.sql

# Restart services
docker-compose -f deploy/superset.compose.yml restart
```

## Security Recommendations

### 1. Change Default Credentials

```bash
# Connect to Superset container
docker-compose -f deploy/superset.compose.yml exec superset bash

# Update admin password
superset fab create-admin \
  --username admin \
  --firstname Admin \
  --lastname User \
  --email admin@insightpulseai.net \
  --password <new-secure-password>
```

### 2. Configure SSL/TLS

For production deployments, ensure:
- ✅ Use HTTPS (Nginx reverse proxy)
- ✅ Valid SSL certificate
- ✅ Secure cookie settings
- ✅ CORS policies configured

### 3. Database Security

```yaml
# Use read-only connection for Superset
Allow DML: No
Allow CSV Upload: No
Expose in SQL Lab: Yes (limited users only)
```

### 4. Row-Level Security (RLS)

Implement RLS in Superset:

1. Navigate to: **Security > Row Level Security**
2. Add filter: `company_id = {{ current_user_company_id() }}`
3. Apply to: `superset_expense_summary`, `superset_bir_compliance`, `superset_agency_metrics`

## Performance Optimization

### 1. Query Caching

```python
# In superset_config.py
CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL')
}
```

### 2. Metadata Caching

```python
# Cache table metadata for 12 hours
TABLE_NAMES_CACHE_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_DEFAULT_TIMEOUT': 43200
}
```

### 3. Async Query Execution

Enable for long-running queries:

```yaml
Allow Run Async: Yes
Async Query Timeout: 300  # 5 minutes
```

### 4. Database Connection Pool

```python
# In database connection extra JSON
{
    "engine_params": {
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": true,
        "pool_recycle": 3600
    }
}
```

## Monitoring

### Health Endpoint

```bash
# Check Superset health
curl http://localhost:8088/health

# Expected response
{
  "ok": true,
  "metastore": "ok",
  "cache": "ok"
}
```

### Logs

```bash
# View logs
docker-compose -f deploy/superset.compose.yml logs -f superset

# Export logs
docker-compose -f deploy/superset.compose.yml logs superset \
  > superset_logs_$(date +%Y%m%d).log
```

### Metrics

Monitor these key metrics:
- Dashboard load time (target: <3 seconds)
- Query execution time (target: <5 seconds)
- Cache hit rate (target: >80%)
- Error rate (target: <1%)

## Maintenance Tasks

### Weekly

```bash
# Clean up old logs
docker-compose -f deploy/superset.compose.yml exec superset \
  find /app/superset_home/logs -type f -mtime +7 -delete

# Vacuum database
docker-compose -f deploy/superset.compose.yml exec superset-db \
  vacuumdb -U superset -d superset -z
```

### Monthly

```bash
# Backup metadata
docker-compose -f deploy/superset.compose.yml exec superset-db \
  pg_dump -U superset superset > superset_backup_monthly_$(date +%Y%m).sql

# Update dependencies
docker-compose -f deploy/superset.compose.yml pull
docker-compose -f deploy/superset.compose.yml up -d
```

## Support

For issues or questions:

1. **Documentation**: https://superset.apache.org/docs/
2. **GitHub Issues**: https://github.com/apache/superset/issues
3. **InsightPulse Support**: Create issue in insightpulse-odoo repo

## Changelog

### 4.1.1 (2025-11-11)
- ✅ Upgraded from 3.1.0 to 4.1.1
- ✅ Added Finance SSC Executive Dashboard
- ✅ Created Odoo database views (expense, BIR, agency metrics)
- ✅ Configured Supabase connection
- ✅ Automated deployment script
- ✅ Added health checks and monitoring

### 3.1.0 (Previous)
- Initial deployment
- Basic configuration

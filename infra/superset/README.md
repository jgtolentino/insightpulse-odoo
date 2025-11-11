# Superset 4.1.1 - InsightPulse Odoo Integration

## Overview

Apache Superset 4.1.1 configured for InsightPulse Odoo Finance Shared Service Center (SSC) with pre-built dashboards and visualizations.

## Quick Start

### Local Development

```bash
# Deploy Superset with example dashboards
./scripts/deploy-superset.sh

# Access at http://localhost:8088
# Default: admin/admin (will prompt to reset)
```

### Production Deployment (DigitalOcean)

```bash
# Deploy to DigitalOcean App Platform
doctl apps update bc1764a5-b48e-4bec-aa72-8a22cab141bc \
  --spec infra/do/superset.yaml

# Trigger deployment
doctl apps create-deployment bc1764a5-b48e-4bec-aa72-8a22cab141bc --force-rebuild

# Access at https://superset.insightpulseai.net
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Superset 4.1.1                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │          Finance SSC Dashboard                  │   │
│  │  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │  Expense by  │  │ BIR Forms    │            │   │
│  │  │  Agency      │  │ Submitted    │            │   │
│  │  └──────────────┘  └──────────────┘            │   │
│  │  ┌──────────────┐  ┌──────────────┐            │   │
│  │  │  Approval    │  │ Top Expense  │            │   │
│  │  │  Timeline    │  │ Categories   │            │   │
│  │  └──────────────┘  └──────────────┘            │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              Supabase PostgreSQL                        │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Views:                                         │   │
│  │  - superset_expense_summary                     │   │
│  │  - superset_bir_compliance                      │   │
│  │  - superset_agency_metrics                      │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Tables:                                        │   │
│  │  - expense_report (Odoo)                        │   │
│  │  - bir_form (Odoo)                              │   │
│  │  - res_company (Odoo)                           │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Pre-Built Dashboards

### 1. Finance SSC Executive Dashboard

**URL**: `/superset/dashboard/finance-ssc-executive/`

**Charts**:
1. **Expense by Agency - Current Month** (Pie Chart)
   - Metric: Total expense amount
   - Dimension: Company/Agency name
   - Filter: Current month only

2. **BIR Forms Submitted - This Quarter** (Big Number)
   - Metric: Count of submitted forms
   - Filter: Current quarter, status = submitted

3. **Expense Approvals - Last 30 Days** (Line Chart)
   - Metric: Count of expenses
   - Dimension: Date submitted
   - Time range: Last 30 days

4. **Top 10 Expense Categories** (Bar Chart)
   - Metric: Total amount
   - Dimension: Expense category
   - Limit: Top 10

**Refresh Frequency**: 5 minutes (300 seconds)

## Database Configuration

### Supabase Connection

```yaml
Database Name: InsightPulse Odoo
Connection String: postgresql://postgres.spdtwktxdalcfigzeqrz:${PASSWORD}@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require
SSL Mode: Require
Expose in SQL Lab: Yes
Allow Run Async: Yes
Allow DML: No
```

### Available Views

#### superset_expense_summary
Aggregated expense data for reporting.

**Fields**:
- `id` - Expense ID
- `expense_name` - Expense report name
- `date_submitted` - Submission date
- `date_approved` - Approval date
- `total_amount` - Expense amount
- `state` - Workflow state
- `category` - Expense category
- `company_name` - Agency/company name
- `employee_name` - Employee name
- `year`, `month`, `quarter` - Time dimensions
- `status_label` - Human-readable status

**Sample Query**:
```sql
SELECT
    company_name,
    SUM(total_amount) as total_expense,
    COUNT(*) as expense_count
FROM superset_expense_summary
WHERE year = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY company_name
ORDER BY total_expense DESC;
```

#### superset_bir_compliance
BIR form submission tracking.

**Fields**:
- `id` - Form ID
- `form_type` - Form type (2307, 2316, 1601C, etc.)
- `submission_date` - Date submitted to BIR
- `status` - Form status
- `tax_amount` - Tax amount
- `company_name` - Agency/company name
- `year`, `quarter`, `month` - Time dimensions
- `form_description` - Human-readable form name

**Sample Query**:
```sql
SELECT
    form_type,
    form_description,
    COUNT(*) as form_count,
    SUM(tax_amount) as total_tax
FROM superset_bir_compliance
WHERE status = 'submitted'
    AND year = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY form_type, form_description;
```

#### superset_agency_metrics
Performance metrics by agency.

**Fields**:
- `company_id` - Company ID
- `company_name` - Agency/company name
- `total_expenses` - Count of expense reports
- `total_expense_amount` - Sum of expense amounts
- `avg_expense_amount` - Average expense amount
- `approved_count` - Count of approved expenses
- `pending_count` - Count of pending expenses
- `rejected_count` - Count of rejected expenses
- `total_bir_forms` - Count of BIR forms
- `submitted_bir_forms` - Count of submitted BIR forms

**Sample Query**:
```sql
SELECT
    company_name,
    total_expenses,
    total_expense_amount,
    approved_count,
    pending_count,
    ROUND(100.0 * approved_count / NULLIF(total_expenses, 0), 2) as approval_rate
FROM superset_agency_metrics
WHERE current_year = EXTRACT(YEAR FROM CURRENT_DATE)
ORDER BY total_expense_amount DESC;
```

## Common Tasks

### Create New Chart

1. Navigate to **Charts** → **+ Chart**
2. Select dataset: `superset_expense_summary`
3. Choose visualization type (e.g., Bar Chart)
4. Configure:
   - **Metrics**: `SUM(total_amount)`
   - **Dimensions**: `category`
   - **Filters**: `year = 2025`
5. Click **Run Query**
6. Click **Save** and add to dashboard

### Create Custom SQL Chart

1. Navigate to **SQL Lab** → **SQL Editor**
2. Write query:
```sql
SELECT
    DATE_TRUNC('month', date_submitted) as month,
    company_name,
    SUM(total_amount) as total
FROM superset_expense_summary
WHERE year = 2025
GROUP BY 1, 2
ORDER BY 1, 2;
```
3. Click **Run**
4. Click **Explore** → Choose visualization
5. Configure chart and save

### Export Dashboard

```bash
# Export dashboard to JSON
docker-compose -f deploy/superset.compose.yml exec superset \
  superset export-dashboards -d finance-ssc-executive -f /tmp/dashboard.json

# Copy to host
docker cp superset:/tmp/dashboard.json ./dashboard_backup.json
```

### Import Dashboard

```bash
# Copy to container
docker cp dashboard_backup.json superset:/tmp/dashboard.json

# Import
docker-compose -f deploy/superset.compose.yml exec superset \
  superset import-dashboards -p /tmp/dashboard.json
```

## Administration

### Reset Admin Password

```bash
./scripts/reset-superset-admin.sh
```

### Create New User

```bash
docker-compose -f deploy/superset.compose.yml exec superset \
  superset fab create-user \
    --role Admin \
    --username jdoe \
    --firstname John \
    --lastname Doe \
    --email jdoe@insightpulseai.net \
    --password secure_password
```

### Backup Metadata

```bash
# Backup Superset metadata database
docker-compose -f deploy/superset.compose.yml exec superset-db \
  pg_dump -U superset superset > superset_backup_$(date +%Y%m%d).sql
```

### Restore Metadata

```bash
# Restore from backup
docker-compose -f deploy/superset.compose.yml exec -T superset-db \
  psql -U superset superset < superset_backup_20251111.sql
```

## Monitoring

### Health Check

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

### View Logs

```bash
# Real-time logs
docker-compose -f deploy/superset.compose.yml logs -f superset

# Last 100 lines
docker-compose -f deploy/superset.compose.yml logs --tail=100 superset
```

### Performance Metrics

Monitor these metrics in Superset UI (**Settings** → **List Logs**):

- Dashboard load time (target: <3 seconds)
- Query execution time (target: <5 seconds)
- Cache hit rate (target: >80%)
- Error rate (target: <1%)

## Security

### Row-Level Security (RLS)

Implement company-based RLS:

1. Navigate to **Security** → **Row Level Security**
2. Add filter:
   - **Name**: Company Isolation
   - **Table**: `superset_expense_summary`
   - **Filter**: `company_id = {{ current_user.company_id }}`
   - **Group**: Finance Managers

### SSL/TLS Configuration

Production Nginx configuration:

```nginx
server {
    listen 443 ssl http2;
    server_name superset.insightpulseai.net;

    ssl_certificate /etc/letsencrypt/live/insightpulseai.net/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/insightpulseai.net/privkey.pem;

    location / {
        proxy_pass http://superset:8088;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

See [SUPERSET_UPGRADE.md](../../docs/SUPERSET_UPGRADE.md#troubleshooting) for detailed troubleshooting guide.

### Quick Fixes

**Issue**: Container won't start
```bash
docker-compose -f deploy/superset.compose.yml logs superset
```

**Issue**: Can't connect to database
```bash
psql "$SQLALCHEMY_DATABASE_URI" -c "SELECT 1"
```

**Issue**: Dashboards not loading
```bash
docker-compose -f deploy/superset.compose.yml exec superset \
  superset fab reset-cache
```

## Resources

- **Official Docs**: https://superset.apache.org/docs/
- **GitHub**: https://github.com/apache/superset
- **Upgrade Guide**: [docs/SUPERSET_UPGRADE.md](../../docs/SUPERSET_UPGRADE.md)
- **InsightPulse Docs**: [docs/](../../docs/)

## Version History

- **4.1.1** (2025-11-11): Upgraded from 3.1.0, added Finance SSC dashboard
- **3.1.0** (Previous): Initial deployment

# Superset Dashboards - InsightPulse Odoo Analytics

This directory contains production-ready Apache Superset dashboard configurations for the InsightPulse Odoo analytics platform.

## Overview

**5 Production-Ready Dashboards**:
1. **Executive Overview** - Strategic insights for C-suite
2. **Procurement Analytics** - Vendor management and cost optimization
3. **Finance Performance** - Financial metrics and cash flow
4. **Sales Performance** - Pipeline tracking and revenue forecasting
5. **Operational Efficiency** - Process metrics and bottleneck analysis

## Directory Structure

```
superset/
├── dashboards/           # Dashboard JSON export files
│   ├── 00_executive_overview.json
│   ├── 01_procurement_analytics.json
│   ├── 02_finance_performance.json
│   ├── 03_sales_performance.json
│   └── 04_operational_efficiency.json
├── datasets/            # SQL files for data sources
│   ├── 01_mv_sales_kpi_daily.sql
│   ├── 02_mv_product_performance.sql
│   ├── 03_fact_sales.sql
│   ├── 04_mv_customer_ltv.sql
│   ├── 05_fact_purchase.sql
│   ├── 06_fact_invoice.sql
│   ├── 07_fact_expense.sql
│   ├── 08_mv_expense_compliance.sql
│   ├── 09_dim_customer.sql
│   ├── 10_dim_employee.sql
│   └── README.md
├── import_dashboards.sh # Automated import script
└── README.md            # This file
```

## Quick Start

### Prerequisites

1. **Apache Superset** installed and running
2. **Supabase** database with analytics schema
3. **Database connection** configured in Superset
4. **CLI tools**: `curl`, `jq`, `superset`

### Installation Steps

#### 1. Configure Database Connection

In Superset UI:
- Navigate to: **Data > Databases > + Database**
- Database Name: `Supabase Analytics`
- SQLAlchemy URI: `postgresql://user:password@host:port/database`
- Test Connection
- Click **Connect**

#### 2. Create Datasets

Option A - Using Web UI:
```bash
# Navigate to: Data > Datasets > + Dataset
# Select:
#   - Database: Supabase Analytics
#   - Schema: analytics
#   - Table: [select from list]
# Repeat for all tables in datasets/ directory
```

Option B - Using CLI:
```bash
# From the superset directory
cd datasets/
# Create datasets from SQL files
# (Manual creation recommended for first-time setup)
```

#### 3. Import Dashboards

Using the automated script:
```bash
# Set environment variables (optional)
export SUPERSET_HOST="http://localhost:8088"
export SUPERSET_USERNAME="admin"
export SUPERSET_PASSWORD="admin"

# Run import script
./import_dashboards.sh
```

Manual import via UI:
```bash
# Navigate to: Dashboards > Import Dashboard
# Upload each JSON file from dashboards/ directory
```

## Dashboard Specifications

### 1. Executive Overview
**Purpose**: Strategic insights for C-suite executives

**Target Audience**: CEO, CFO, COO, Board Members

**Key Metrics**:
- Revenue: $2.4M (↑12%)
- Orders: 1,247 (↑8%)
- Customers: 342 (↑15%)
- Margin: 34% (↓2%)
- ARR: $12M

**Charts**:
- Revenue KPI Card
- Orders KPI Card
- Customers KPI Card
- Margin KPI Card
- ARR KPI Card
- Revenue Trend (12 months)
- Top 10 Products by Revenue
- Revenue by Customer Segment
- MRR/ARR Trend
- Customer Acquisition

**Refresh**: Every 5 minutes

### 2. Procurement Analytics
**Purpose**: Procurement performance and vendor management

**Target Audience**: Procurement Managers, Supply Chain Analysts

**Key Metrics**:
- PO Value: $1.8M (↑5%)
- PO Count: 423 (↑12%)
- Active Vendors: 67 (↑3)
- Avg Lead Time: 14.2 days
- On-Time Delivery: 87%

**Charts**:
- Purchase Orders by Status (Funnel)
- Top 10 Vendors by Spend
- Procurement Cycle Time Trend
- Vendor Performance Scorecard
- Purchase by Category (Treemap)

**Refresh**: Every 30 minutes

### 3. Finance Performance
**Purpose**: Financial metrics and cash flow monitoring

**Target Audience**: CFO, Finance Managers, Accounting Team

**Key Metrics**:
- Revenue: $2.4M
- Expenses: $1.6M
- Net Income: $800K
- AR Balance: $450K
- AP Balance: $320K

**Charts**:
- Cash Flow Trend
- P&L Summary
- Accounts Receivable Aging
- Accounts Payable Aging
- Outstanding Invoices (Top 20)

**Refresh**: Every 15 minutes

### 4. Sales Performance
**Purpose**: Sales pipeline and performance tracking

**Target Audience**: Sales Managers, Sales Representatives

**Key Metrics**:
- Pipeline: $3.2M
- Closed Won: $890K
- Win Rate: 28%
- Avg Deal Size: $24.5K
- Quota Attainment: 92%

**Charts**:
- Sales Funnel
- Revenue by Salesperson
- Monthly Sales Trend vs Target
- Top Customers by LTV
- Sales Cycle Analysis

**Refresh**: Every 10 minutes

### 5. Operational Efficiency
**Purpose**: Process efficiency and bottleneck analysis

**Target Audience**: COO, Operations Managers, Process Analysts

**Key Metrics**:
- Order Cycle: 5.2 days
- Procurement Cycle: 14.3 days
- Expense Approval: 3.1 days
- Compliance Rate: 94%
- Active Issues: 12

**Charts**:
- Order Fulfillment Cycle Time (Box Plot)
- Procurement Cycle Time (Box Plot)
- Expense Compliance Trend
- Top Process Bottlenecks
- Department Performance Heatmap

**Refresh**: Every 30 minutes

## Configuration

### Color Scheme
All dashboards use a consistent color palette:
- **Primary** (#1976D2): Blue - Neutral metrics
- **Success** (#43A047): Green - Positive trends, revenue
- **Warning** (#FFA000): Amber - Attention needed
- **Danger** (#D32F2F): Red - Negative trends, issues
- **Info** (#00ACC1): Cyan - Information, insights

### Native Filters
Each dashboard includes:
- **Date Range**: Time period selector
- **Company Filter**: Multi-company selection (RLS-enabled)
- **Domain-specific filters**: Based on dashboard purpose

### Cross-Filtering
Cross-filtering is enabled on all dashboards for interactive exploration.

### Caching Strategy
| Dashboard | Cache TTL | Refresh Schedule |
|-----------|-----------|------------------|
| Executive Overview | 5 min | */5 * * * * |
| Procurement Analytics | 30 min | */30 * * * * |
| Finance Performance | 15 min | */15 * * * * |
| Sales Performance | 10 min | */10 * * * * |
| Operational Efficiency | 30 min | */30 * * * * |

## Row-Level Security (RLS)

All dashboards support multi-tenancy through RLS policies:

```sql
-- Example RLS policy for company-based access
WHERE company_key IN (
    SELECT company_id
    FROM user_company_access
    WHERE user_id = {{ current_user_id() }}
)
```

Configure RLS in Superset:
1. Navigate to: **Data > Datasets > [Dataset] > Edit**
2. Go to **Advanced** tab
3. Add RLS filter in **Row Level Security** section

## Export Capabilities

All dashboards support:
- **PDF Export**: Full dashboard export
- **PNG Export**: Individual chart export
- **CSV Export**: Data table export
- **Email Scheduling**: Automated email reports
- **Slack Integration**: Real-time alerts

## Permissions

### Role-Based Access
| Role | Dashboards | Access Level |
|------|-----------|-------------|
| Executive | All | Full (with RLS) |
| Finance Team | Executive, Finance | Company-specific + consolidation |
| Sales Team | Executive, Sales | Team-specific (own + team deals) |
| Procurement Team | Executive, Procurement | Company-specific |
| Operations Team | All | Company-specific |

### Configure Permissions
1. Navigate to: **Settings > List Roles**
2. Select role (e.g., "Finance Team")
3. Click **Edit**
4. Add dashboard permissions under **Permissions** tab

## Performance Optimization

### Query Optimization
- Use materialized views for complex aggregations
- Implement indexes on fact tables
- Leverage query result caching
- Partition large tables by date

### Dashboard Loading
- Lazy-load charts (visible first)
- Use progressive rendering
- Implement chart-level caching
- Minimize cross-chart dependencies

### Performance Benchmarks
- **Page Load**: < 3 seconds
- **Chart Render**: < 2 seconds
- **Filter Response**: < 1 second
- **Export Generation**: < 10 seconds
- **Concurrent Users**: 50+ supported

## Troubleshooting

### Common Issues

**Issue**: Dashboard charts not loading
```bash
# Solution: Check database connection
superset db upgrade
superset init
```

**Issue**: "Dataset not found" error
```bash
# Solution: Verify datasets exist
# Navigate to: Data > Datasets
# Create missing datasets from datasets/ directory
```

**Issue**: Slow query performance
```bash
# Solution: Check materialized view refresh
# Verify indexes on fact tables
# Review query execution plan with EXPLAIN ANALYZE
```

**Issue**: RLS not filtering data
```bash
# Solution: Verify RLS policies
# Check user-company mappings in database
# Test RLS filter in SQL Lab before applying
```

## Monitoring and Alerts

### Set Up Alerts
1. Navigate to: **Alerts & Reports > Alerts**
2. Click **+ Alert**
3. Configure:
   - Dashboard/Chart
   - Condition (threshold)
   - Recipients
   - Schedule

### Example Alert
```yaml
Alert Name: "High AR Balance"
Dashboard: Finance Performance
Chart: AR Balance KPI
Condition: Value > $500,000
Recipients: finance@company.com
Schedule: Daily at 9:00 AM
```

## Maintenance

### Regular Tasks
- **Daily**: Review dashboard performance metrics
- **Weekly**: Check query execution times
- **Monthly**: Update RLS policies for new users
- **Quarterly**: Review and optimize slow queries

### Backup
```bash
# Export all dashboards
superset export-dashboards -f dashboards_backup.zip

# Export specific dashboard
superset export-dashboards -d 1 -f dashboard_1_backup.zip
```

### Upgrade
```bash
# Upgrade Superset
pip install --upgrade apache-superset

# Run database migrations
superset db upgrade

# Re-import dashboards if needed
./import_dashboards.sh
```

## Support and Documentation

- **Main Documentation**: `/docs/SUPERSET_DASHBOARDS.md`
- **BI Architecture**: `/docs/BI_ARCHITECTURE.md`
- **Superset Official Docs**: https://superset.apache.org/docs/intro

## Version History

- **v1.0.0** (2025-11-03): Initial release with 5 production dashboards

## License

Internal use only - InsightPulse Odoo Analytics Platform

---

**Created by**: SuperClaude - bi-designer agent
**Last Updated**: 2025-11-03
**Status**: Production Ready

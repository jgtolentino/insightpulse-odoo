# Superset Dataset SQL Files

This directory contains SQL queries and documentation for all datasets used in Superset dashboards.

## Overview

These SQL files define the data sources for the 5 Superset dashboards:
1. Executive Overview
2. Procurement Analytics
3. Finance Performance
4. Sales Performance
5. Operational Efficiency

## Dataset Files

### Fact Tables (Real-time via CDC)
- `03_fact_sales.sql` - Sales order transactions
- `05_fact_purchase.sql` - Purchase order transactions
- `06_fact_invoice.sql` - Invoice and payment records
- `07_fact_expense.sql` - Expense records with approval workflow

### Materialized Views (Hourly refresh)
- `01_mv_sales_kpi_daily.sql` - Daily sales KPI aggregations
- `02_mv_product_performance.sql` - Product performance metrics
- `04_mv_customer_ltv.sql` - Customer lifetime value metrics
- `08_mv_expense_compliance.sql` - Expense compliance metrics

### Dimension Tables (Daily refresh)
- `09_dim_customer.sql` - Customer master data
- `10_dim_employee.sql` - Employee master data

## Usage Instructions

### 1. Create Datasets in Superset

For each SQL file, create a corresponding dataset in Superset:

```bash
# Using Superset CLI
superset import-datasets -p /path/to/datasets/

# Or via Web UI:
# 1. Navigate to Data > Datasets
# 2. Click "+ Dataset"
# 3. Select Database: "Supabase Analytics"
# 4. Select Schema: "analytics"
# 5. Select Table: [table name from SQL file]
# 6. Click "Create Dataset and Create Chart"
```

### 2. Configure Dataset Properties

For each dataset, configure:
- **Cache Timeout**: Set based on refresh frequency
  - Fact tables: 300 seconds (5 minutes)
  - Materialized views: 3600 seconds (1 hour)
  - Dimension tables: 86400 seconds (24 hours)

- **Calculated Columns**: Add custom calculations as needed
- **Metrics**: Define default metrics for charts
- **Filters**: Configure default filters

### 3. Set Up RLS (Row-Level Security)

Apply RLS policies to ensure users only see their authorized data:

```sql
-- Example RLS filter for company-based access
-- Add to dataset's SQL Lab > Advanced > Row Level Security
WHERE company_key IN (
    SELECT company_id
    FROM user_company_access
    WHERE user_id = {{ current_user_id() }}
)
```

## Dataset ID Mapping

The dashboard JSON files reference datasets by ID:
- Dataset 1: `mv_sales_kpi_daily`
- Dataset 2: `mv_product_performance`
- Dataset 3: `fact_sales`
- Dataset 4: `mv_customer_ltv`
- Dataset 5: `fact_purchase`
- Dataset 6: `fact_invoice`
- Dataset 7: `fact_sales` (Sales Performance specific)
- Dataset 8: `mv_customer_ltv` (Sales Performance specific)
- Dataset 9: `fact_expense`
- Dataset 10: `dim_employee`
- Dataset 11: `mv_expense_compliance`
- Dataset 12: Process metrics (custom query)

## Data Refresh Schedule

| Dataset Type | Refresh Method | Frequency | Cache TTL |
|-------------|----------------|-----------|-----------|
| Fact Tables | CDC (Real-time) | Continuous | 5 min |
| Materialized Views | Scheduled refresh | Hourly | 1 hour |
| Dimension Tables | CDC + Daily refresh | Daily | 24 hours |

## Schema References

All datasets are in the `analytics` schema in Supabase:
- Database: Supabase PostgreSQL
- Schema: `analytics`
- Connection: Configure in Superset > Data > Databases

## Custom SQL Queries

For complex visualizations requiring custom SQL, use SQL Lab:
1. Navigate to SQL Lab > SQL Editor
2. Write custom query combining multiple datasets
3. Save as "Virtual Dataset"
4. Use in dashboard charts

## Troubleshooting

### Dataset Not Found
- Verify schema exists in Supabase
- Check database connection in Superset
- Ensure user has SELECT permissions

### Slow Query Performance
- Check materialized view refresh status
- Verify indexes exist on fact tables
- Review query execution plan
- Adjust cache timeout settings

### RLS Not Working
- Verify RLS policies are enabled in Superset
- Check user-company mappings
- Test with SQL Lab before applying to datasets

## Additional Resources

- [Superset Documentation](https://superset.apache.org/docs/intro)
- [Analytics Schema Documentation](../../docs/BI_ARCHITECTURE.md)
- [Dashboard Specifications](../../docs/SUPERSET_DASHBOARDS.md)

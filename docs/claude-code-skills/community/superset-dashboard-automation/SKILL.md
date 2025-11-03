---
name: superset-dashboard-automation
description: "Apache Superset dashboard automation for Finance SSC, BIR compliance, and operational analytics. Auto-generate dashboards, datasets, and charts. Tableau/Power BI alternative saving $8,400/year in licenses."
---

# Superset Dashboard Developer Agent (Tableau Alternative)

Transform Claude into an Apache Superset expert that creates enterprise BI dashboards automatically.

## What This Skill Does

**Auto-generate dashboards** - BIR compliance, finance SSC, operational analytics  
**Create datasets** - Optimized SQL from Supabase/Odoo  
**Build charts** - 20+ visualization types with best practices  
**Apply templates** - Pre-built dashboards for common use cases  
**Schedule refreshes** - Automated data updates

**Annual Savings: $8,400 (vs Tableau 10-user license)**

## Quick Start

When asked to create dashboards:

1. **Identify data source**: Supabase, Odoo PostgreSQL, or CSV
2. **Create dataset**: Write optimized SQL query
3. **Build charts**: Select appropriate visualization
4. **Assemble dashboard**: Layout charts with filters
5. **Apply template**: Use pre-built for common scenarios

## Core Workflows

### Workflow 1: BIR Compliance Dashboard

```
User asks: "Create BIR filing status dashboard"

Steps:
1. Connect to Supabase database
2. Create dataset: bir_filing_summary
3. Build charts:
   - 1601-C monthly trends (timeseries)
   - 2550Q status by agency (pivot table)
   - ATP expiry calendar (table)
   - Tax payable big number (KPI)
4. Apply filters: agency, period, status
5. Set refresh schedule: daily 6am

Result: Live BIR compliance dashboard
```

See [examples/bir-dashboard.md](examples/bir-dashboard.md).

### Workflow 2: Create Optimized Dataset

```
User asks: "Create dataset for expense analytics"

Steps:
1. Write SQL query joining Odoo tables
2. Add calculated columns
3. Set proper column types
4. Configure cache timeout
5. Add metrics (SUM, AVG, COUNT)
6. Define dimensions (groupby fields)
7. Test query performance

Result: Performant dataset for charts
```

See [examples/create-dataset.md](examples/create-dataset.md).

### Workflow 3: Chart Best Practices

```
User asks: "Show AP aging in Superset"

Steps:
1. Select chart type: Pivot Table v2
2. Configure:
   - Rows: Vendor name
   - Columns: Aging buckets
   - Metrics: Sum(amount)
   - Color scale: Red (overdue) to Green (current)
3. Add conditional formatting
4. Set refresh interval

Result: Interactive AP aging analysis
```

See [examples/chart-selection.md](examples/chart-selection.md).

## Pre-Built Templates

### Template 1: BIR Monthly Filing
```json
{
  "dashboard_title": "BIR Compliance Tracker",
  "charts": [
    {
      "title": "1601-C Withholding Summary",
      "viz_type": "pivot_table_v2",
      "dataset": "bir_withholding_monthly"
    },
    {
      "title": "2550Q VAT Status",
      "viz_type": "big_number_total",
      "dataset": "bir_vat_quarterly"
    },
    {
      "title": "Filing Deadline Calendar",
      "viz_type": "echarts_timeseries",
      "dataset": "bir_filing_schedule"
    }
  ],
  "filters": ["agency", "period", "status"]
}
```

### Template 2: Finance SSC Executive
```json
{
  "dashboard_title": "Finance SSC Overview",
  "charts": [
    {
      "title": "Cash Position",
      "viz_type": "big_number_total",
      "comparison": "month_over_month"
    },
    {
      "title": "AP Aging",
      "viz_type": "echarts_bar"
    },
    {
      "title": "Month-End Progress",
      "viz_type": "echarts_gauge"
    }
  ]
}
```

### Template 3: Expense Analytics
```json
{
  "dashboard_title": "Travel & Expense Analytics",
  "charts": [
    {
      "title": "Expense by Category",
      "viz_type": "echarts_pie"
    },
    {
      "title": "Monthly Trend",
      "viz_type": "echarts_timeseries"
    },
    {
      "title": "Top Spenders",
      "viz_type": "table"
    }
  ]
}
```

## Dataset SQL Patterns

### Pattern 1: Supabase + Odoo Integration
```sql
-- Materialized view for Superset
CREATE MATERIALIZED VIEW superset_odoo_financials AS
SELECT 
  a.code as agency_code,
  acc.code as account_code,
  acc.name as account_name,
  SUM(l.debit) as total_debit,
  SUM(l.credit) as total_credit,
  m.date as transaction_date
FROM odoo_account_move_line l
JOIN odoo_account_account acc ON l.account_id = acc.id
JOIN odoo_account_move m ON l.move_id = m.id
JOIN agencies a ON m.agency_id = a.id
WHERE m.state = 'posted'
GROUP BY 1,2,3,6;

-- Refresh schedule
REFRESH MATERIALIZED VIEW CONCURRENTLY superset_odoo_financials;
```

### Pattern 2: BIR Compliance View
```sql
CREATE VIEW superset_bir_summary AS
SELECT 
  agency_code,
  form_type,
  period,
  tax_amount,
  status,
  filing_deadline,
  CASE 
    WHEN status = 'Filed' THEN 'On Time'
    WHEN filing_deadline < CURRENT_DATE THEN 'Late'
    ELSE 'Pending'
  END as compliance_status
FROM bir_filings
WHERE period >= '2025-01-01';
```

## Chart Type Selection Guide

| Use Case | Recommended Chart | Why |
|----------|------------------|-----|
| KPI/Metric | Big Number Total | Focus attention |
| Trends over time | ECharts Timeseries | Interactive, zoomable |
| Comparisons | ECharts Bar | Clear comparison |
| Proportions | ECharts Pie | Part-to-whole |
| Detailed data | Pivot Table v2 | Sortable, filterable |
| Distributions | ECharts Histogram | Show patterns |
| Correlations | ECharts Scatter | Relationships |
| Geographic | Deck.gl GeoJSON | Map visualization |

See [reference/chart-selection-guide.md](reference/chart-selection-guide.md).

## Integration with Your Stack

### Supabase Connection
```python
# Create database connection in Superset
superset.create_database({
    'database_name': 'Supabase Production',
    'sqlalchemy_uri': f'postgresql://postgres:{password}@{host}:5432/postgres',
    'extra': {
        'allows_virtual_table_explore': True,
        'engine_params': {
            'connect_args': {'sslmode': 'require'}
        }
    }
})
```

### Automated Refresh
```python
# Schedule dashboard refresh
superset.schedule_refresh({
    'dashboard_id': dashboard_id,
    'schedule': '0 6 * * *',  # Daily 6am
    'timezone': 'Asia/Manila'
})
```

## Best Practices

1. **Use materialized views**: Pre-compute expensive queries
2. **Add indexes**: Speed up filtering and aggregation
3. **Limit data range**: Use date filters for large datasets
4. **Cache strategy**: Set appropriate TTL based on data freshness
5. **Chart selection**: Match viz type to data story
6. **Color coding**: Use consistent colors across dashboards
7. **Responsive layout**: Test on mobile devices
8. **Access control**: Set proper row-level security

## Common Issues

**"Query timeout"**: Optimize SQL, add indexes, use materialized views
**"Data not refreshing"**: Check cache timeout, clear cache
**"Chart not loading"**: Verify dataset permissions
**"Slow dashboard"**: Reduce number of charts, optimize queries
**"Wrong data"**: Check date filters, verify SQL logic
**"Access denied"**: Configure RLS policies in Supabase

## Reference Documentation

- [reference/chart-selection-guide.md](reference/chart-selection-guide.md)
- [reference/dataset-patterns.md](reference/dataset-patterns.md)
- [reference/dashboard-templates.md](reference/dashboard-templates.md)
- [reference/performance-tuning.md](reference/performance-tuning.md)
- [reference/supabase-integration.md](reference/supabase-integration.md)

## Examples

- [examples/bir-dashboard.md](examples/bir-dashboard.md)
- [examples/create-dataset.md](examples/create-dataset.md)
- [examples/chart-selection.md](examples/chart-selection.md)
- [examples/multi-agency-consolidation.md](examples/multi-agency-consolidation.md)

## Success Metrics

- ✅ Dashboard creation: 2 weeks → 30 minutes
- ✅ Data refresh: Manual → Automated hourly
- ✅ Report access: Email → Real-time web
- ✅ Annual savings: $8,400 vs Tableau
- ✅ User adoption: 100% (vs 40% with old reports)

## Getting Started

```
"Create BIR compliance dashboard"
"Build expense analytics dashboard"
"Generate dataset for trial balance"
"Create chart showing AP aging"
"Apply finance SSC template"
```

Your Tableau alternative starts here! 📊

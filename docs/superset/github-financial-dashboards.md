# Superset CFO Dashboards - GitHub Financial Tracking

**Complete SQL queries and dashboard configurations for CFO-level visibility into development costs, budgets, and ROI.**

---

## Overview

This guide provides ready-to-use Superset dashboard queries that integrate GitHub Projects with Odoo timesheet data to provide:

- **Project burn rate** (budget vs. actual spend)
- **CapEx vs OpEx split** (for financial reporting)
- **Feature ROI** (development cost vs. revenue)
- **Developer productivity** (hours, output, cost per feature)
- **Budget forecasting** (runway, completion estimates)

**Prerequisites:**
- `ipai_github_timesheets` Odoo module installed
- GitHub Projects synced to Odoo
- Employee hourly rates configured
- Timesheets being logged regularly

---

## Dashboard 1: Project Burn Rate

**Purpose**: Track budget utilization and spending pace across all active projects

### Chart 1.1: Budget vs. Actual Spend (Bar Chart)

```sql
-- Budget vs Actual Spend by Project
SELECT
    gp.title AS project_name,
    gp.project_budget AS budget,
    gp.project_spend AS actual_spend,
    gp.remaining_budget,
    gp.budget_utilization_pct AS utilization_pct,
    CASE
        WHEN gp.budget_utilization_pct > 100 THEN 'Over Budget'
        WHEN gp.budget_utilization_pct > 80 THEN 'At Risk'
        WHEN gp.budget_utilization_pct > 50 THEN 'On Track'
        ELSE 'Under Budget'
    END AS budget_status
FROM github_project gp
WHERE gp.github_state = 'open'
  AND gp.active = true
ORDER BY gp.budget_utilization_pct DESC;
```

**Superset Config:**
- **Chart Type**: Bar Chart (Horizontal)
- **X-axis**: `budget`, `actual_spend`, `remaining_budget`
- **Y-axis**: `project_name`
- **Color**: `budget_status` (conditional formatting)
- **Sort**: Budget Utilization % (descending)

### Chart 1.2: Budget Utilization Gauge

```sql
-- Overall Budget Utilization
SELECT
    SUM(gp.project_budget) AS total_budget,
    SUM(gp.project_spend) AS total_spend,
    SUM(gp.remaining_budget) AS total_remaining,
    ROUND(
        (SUM(gp.project_spend) / NULLIF(SUM(gp.project_budget), 0)) * 100,
        2
    ) AS overall_utilization_pct
FROM github_project gp
WHERE gp.github_state = 'open'
  AND gp.active = true;
```

**Superset Config:**
- **Chart Type**: Gauge
- **Metric**: `overall_utilization_pct`
- **Min**: 0
- **Max**: 150
- **Color Zones**:
  - 0-50: Green
  - 50-80: Yellow
  - 80-100: Orange
  - 100+: Red

### Chart 1.3: Burn Rate Trend (Time Series)

```sql
-- Monthly burn rate (cumulative spend over time)
SELECT
    DATE_TRUNC('month', aal.date) AS month,
    gp.title AS project_name,
    SUM(ABS(aal.amount)) AS monthly_spend,
    SUM(SUM(ABS(aal.amount))) OVER (
        PARTITION BY gp.id
        ORDER BY DATE_TRUNC('month', aal.date)
    ) AS cumulative_spend,
    MAX(gp.project_budget) AS project_budget
FROM github_project gp
INNER JOIN project_project pp ON pp.id = gp.odoo_project_id
INNER JOIN account_analytic_line aal ON aal.project_id = pp.id
WHERE aal.amount < 0  -- Costs are negative in Odoo
  AND gp.github_state = 'open'
GROUP BY DATE_TRUNC('month', aal.date), gp.id, gp.title
ORDER BY month, project_name;
```

**Superset Config:**
- **Chart Type**: Line Chart
- **X-axis**: `month` (time)
- **Y-axis**: `cumulative_spend`, `project_budget` (dual axis)
- **Group By**: `project_name`
- **Line Type**: `cumulative_spend` (solid), `project_budget` (dashed)

---

## Dashboard 2: CapEx vs OpEx Split

**Purpose**: Classify development costs for financial reporting (capitalize assets vs. expense immediately)

### Chart 2.1: CapEx vs OpEx Breakdown (Pie Chart)

```sql
-- Total spend by expense type
SELECT
    gp.expense_type,
    SUM(gp.project_spend) AS total_cost,
    COUNT(DISTINCT gp.id) AS project_count,
    ROUND(
        SUM(gp.project_spend) / NULLIF(
            (SELECT SUM(project_spend) FROM github_project WHERE active = true),
            0
        ) * 100,
        2
    ) AS percentage_of_total
FROM github_project gp
WHERE gp.active = true
  AND gp.project_spend > 0
GROUP BY gp.expense_type
ORDER BY total_cost DESC;
```

**Superset Config:**
- **Chart Type**: Pie Chart
- **Label**: `expense_type`
- **Value**: `total_cost`
- **Show Percentage**: Yes
- **Color Scheme**:
  - CapEx: Blue
  - R&D (OpEx): Orange
  - Maintenance (OpEx): Gray
  - Bug Fix (OpEx): Red

### Chart 2.2: CapEx vs OpEx Trend (Area Chart)

```sql
-- Monthly CapEx vs OpEx trend
SELECT
    DATE_TRUNC('month', aal.date) AS month,
    gp.expense_type,
    SUM(ABS(aal.amount)) AS monthly_cost
FROM github_project gp
INNER JOIN project_project pp ON pp.id = gp.odoo_project_id
INNER JOIN account_analytic_line aal ON aal.project_id = pp.id
WHERE aal.amount < 0  -- Costs
GROUP BY DATE_TRUNC('month', aal.date), gp.expense_type
ORDER BY month, gp.expense_type;
```

**Superset Config:**
- **Chart Type**: Area Chart (Stacked)
- **X-axis**: `month`
- **Y-axis**: `monthly_cost`
- **Stack By**: `expense_type`

### Chart 2.3: Project Classification Table

```sql
-- Detailed project classification for accounting
SELECT
    gp.title AS project_name,
    gp.expense_type,
    gp.project_budget AS budget,
    gp.project_spend AS actual_cost,
    gp.github_state AS status,
    pp.name AS odoo_project,
    COUNT(DISTINCT pt.id) AS task_count,
    SUM(aal.unit_amount) AS total_hours
FROM github_project gp
INNER JOIN project_project pp ON pp.id = gp.odoo_project_id
LEFT JOIN project_task pt ON pt.project_id = pp.id
LEFT JOIN account_analytic_line aal ON aal.project_id = pp.id AND aal.amount < 0
WHERE gp.active = true
GROUP BY gp.id, gp.title, gp.expense_type, gp.project_budget, gp.project_spend, gp.github_state, pp.name
ORDER BY gp.project_spend DESC;
```

**Superset Config:**
- **Chart Type**: Table
- **Columns**: All
- **Conditional Formatting**:
  - CapEx rows: Blue background
  - OpEx rows: Orange background

---

## Dashboard 3: Feature ROI Analysis

**Purpose**: Calculate return on investment for features (if tracking revenue per feature)

### Chart 3.1: Feature ROI Ranking

```sql
-- Feature ROI calculation (requires sale_order_line linkage)
SELECT
    gp.title AS feature_name,
    gp.project_spend AS development_cost,
    COALESCE(SUM(sol.price_subtotal), 0) AS revenue_generated,
    COALESCE(SUM(sol.price_subtotal), 0) - gp.project_spend AS net_roi,
    CASE
        WHEN gp.project_spend > 0 THEN
            ROUND(
                (COALESCE(SUM(sol.price_subtotal), 0) - gp.project_spend) /
                NULLIF(gp.project_spend, 0) * 100,
                2
            )
        ELSE 0
    END AS roi_percentage,
    COUNT(DISTINCT sol.id) AS sales_count
FROM github_project gp
LEFT JOIN sale_order_line sol ON sol.name ILIKE '%' || gp.title || '%'  -- Match by feature name
WHERE gp.expense_type = 'capex_feature'  -- Only capitalizable features
  AND gp.github_state = 'closed'  -- Completed features
GROUP BY gp.id, gp.title, gp.project_spend
HAVING SUM(sol.price_subtotal) > 0  -- Only features with revenue
ORDER BY net_roi DESC;
```

**Superset Config:**
- **Chart Type**: Bar Chart (Horizontal)
- **X-axis**: `net_roi`
- **Y-axis**: `feature_name`
- **Color**: `roi_percentage` (green = positive, red = negative)

### Chart 3.2: ROI Scatter Plot

```sql
-- Development cost vs revenue scatter
SELECT
    gp.title AS feature_name,
    gp.project_spend AS development_cost,
    COALESCE(SUM(sol.price_subtotal), 0) AS revenue,
    COALESCE(SUM(sol.price_subtotal), 0) - gp.project_spend AS profit
FROM github_project gp
LEFT JOIN sale_order_line sol ON sol.name ILIKE '%' || gp.title || '%'
WHERE gp.expense_type = 'capex_feature'
GROUP BY gp.id, gp.title, gp.project_spend
HAVING SUM(sol.price_subtotal) > 0;
```

**Superset Config:**
- **Chart Type**: Scatter Plot
- **X-axis**: `development_cost`
- **Y-axis**: `revenue`
- **Bubble Size**: `profit`
- **Trend Line**: Linear regression

---

## Dashboard 4: Developer Productivity

**Purpose**: Track developer output, cost, and efficiency

### Chart 4.1: Developer Cost Summary

```sql
-- Cost per developer (from timesheets)
SELECT
    he.name AS developer_name,
    SUM(aal.unit_amount) AS total_hours,
    SUM(ABS(aal.amount)) AS total_cost,
    ROUND(SUM(ABS(aal.amount)) / NULLIF(SUM(aal.unit_amount), 0), 2) AS avg_hourly_rate,
    COUNT(DISTINCT gpr.id) AS prs_completed,
    COUNT(DISTINCT gp.id) AS projects_worked_on
FROM hr_employee he
INNER JOIN account_analytic_line aal ON aal.employee_id = he.id
LEFT JOIN github_pull_request gpr ON gpr.id = aal.github_pr_id
LEFT JOIN github_project gp ON gp.id = aal.github_project_id
WHERE aal.amount < 0  -- Costs
  AND aal.date >= CURRENT_DATE - INTERVAL '90 days'  -- Last 90 days
GROUP BY he.id, he.name
ORDER BY total_cost DESC;
```

**Superset Config:**
- **Chart Type**: Table with sparklines
- **Metrics**: All columns
- **Sort**: Total Cost (descending)

### Chart 4.2: Hours Logged per Developer (Bar Chart)

```sql
-- Developer hours breakdown by project
SELECT
    he.name AS developer,
    gp.title AS project,
    SUM(aal.unit_amount) AS hours_logged,
    SUM(ABS(aal.amount)) AS cost
FROM hr_employee he
INNER JOIN account_analytic_line aal ON aal.employee_id = he.id
INNER JOIN github_project gp ON gp.id = aal.github_project_id
WHERE aal.amount < 0
  AND aal.date >= CURRENT_DATE - INTERVAL '30 days'  -- Last 30 days
GROUP BY he.name, gp.title
ORDER BY hours_logged DESC;
```

**Superset Config:**
- **Chart Type**: Bar Chart (Stacked)
- **X-axis**: `developer`
- **Y-axis**: `hours_logged`
- **Stack By**: `project`

### Chart 4.3: PRs Merged per Developer (Time Series)

```sql
-- Developer velocity: PRs merged over time
SELECT
    DATE_TRUNC('week', gpr.github_merged_at) AS week,
    he.name AS developer,
    COUNT(DISTINCT gpr.id) AS prs_merged,
    SUM(gpr.timesheet_hours) AS total_hours,
    SUM(gpr.timesheet_cost) AS total_cost
FROM github_pull_request gpr
INNER JOIN hr_employee he ON he.id = gpr.employee_id
WHERE gpr.github_state = 'merged'
  AND gpr.github_merged_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY week, he.name
ORDER BY week, prs_merged DESC;
```

**Superset Config:**
- **Chart Type**: Line Chart
- **X-axis**: `week`
- **Y-axis**: `prs_merged`
- **Group By**: `developer`

---

## Dashboard 5: Budget Forecasting

**Purpose**: Predict project completion dates and budget runway

### Chart 5.1: Project Runway (Days to Budget Exhaustion)

```sql
-- Calculate runway based on burn rate
WITH monthly_burn AS (
    SELECT
        gp.id,
        gp.title,
        gp.remaining_budget,
        AVG(
            SUM(ABS(aal.amount)) OVER (
                PARTITION BY gp.id
                ORDER BY DATE_TRUNC('month', aal.date)
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            )
        ) AS avg_monthly_burn  -- 3-month rolling average
    FROM github_project gp
    INNER JOIN project_project pp ON pp.id = gp.odoo_project_id
    INNER JOIN account_analytic_line aal ON aal.project_id = pp.id
    WHERE aal.amount < 0
      AND gp.github_state = 'open'
    GROUP BY gp.id, gp.title, gp.remaining_budget, DATE_TRUNC('month', aal.date)
)
SELECT
    title AS project_name,
    remaining_budget,
    avg_monthly_burn,
    CASE
        WHEN avg_monthly_burn > 0 THEN
            ROUND((remaining_budget / avg_monthly_burn) * 30, 0)  -- Days
        ELSE NULL
    END AS days_to_exhaustion,
    CASE
        WHEN avg_monthly_burn > 0 AND (remaining_budget / avg_monthly_burn) < 2 THEN 'Critical'
        WHEN avg_monthly_burn > 0 AND (remaining_budget / avg_monthly_burn) < 4 THEN 'Warning'
        ELSE 'Healthy'
    END AS runway_status
FROM monthly_burn
WHERE avg_monthly_burn > 0
ORDER BY days_to_exhaustion NULLS LAST;
```

**Superset Config:**
- **Chart Type**: Table with conditional formatting
- **Highlight Rules**:
  - Critical: Red
  - Warning: Yellow
  - Healthy: Green

### Chart 5.2: Projected Completion Date

```sql
-- Estimate project completion based on velocity
WITH task_velocity AS (
    SELECT
        gp.id AS project_id,
        gp.title,
        COUNT(DISTINCT pt.id) AS total_tasks,
        COUNT(DISTINCT CASE WHEN pt.stage_id IN (SELECT id FROM project_task_type WHERE name = 'Done') THEN pt.id END) AS completed_tasks,
        AVG(
            COUNT(DISTINCT CASE WHEN pt.stage_id IN (SELECT id FROM project_task_type WHERE name = 'Done') THEN pt.id END)
        ) OVER (
            PARTITION BY gp.id
            ORDER BY DATE_TRUNC('week', pt.write_date)
            ROWS BETWEEN 3 PRECEDING AND CURRENT ROW
        ) AS avg_weekly_velocity
    FROM github_project gp
    INNER JOIN project_project pp ON pp.id = gp.odoo_project_id
    INNER JOIN project_task pt ON pt.project_id = pp.id
    WHERE gp.github_state = 'open'
    GROUP BY gp.id, gp.title, DATE_TRUNC('week', pt.write_date)
)
SELECT
    title AS project_name,
    total_tasks,
    completed_tasks,
    total_tasks - completed_tasks AS remaining_tasks,
    avg_weekly_velocity AS tasks_per_week,
    CASE
        WHEN avg_weekly_velocity > 0 THEN
            CURRENT_DATE + INTERVAL '1 week' * ((total_tasks - completed_tasks) / avg_weekly_velocity)
        ELSE NULL
    END AS projected_completion_date
FROM task_velocity
WHERE avg_weekly_velocity > 0
ORDER BY projected_completion_date;
```

**Superset Config:**
- **Chart Type**: Timeline / Gantt Chart
- **Start**: Current Date
- **End**: `projected_completion_date`
- **Label**: `project_name`

---

## Setup Instructions

### 1. Create Superset Database Connection

```bash
# In Superset: Data → Databases → + Database

# Connection String (Supabase)
postgresql://postgres:[PASSWORD]@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require

# Or direct Odoo PostgreSQL
postgresql://odoo:[PASSWORD]@localhost:5432/odoo_db
```

### 2. Create Datasets

For each SQL query above:

1. Go to **SQL Lab → SQL Editor**
2. Paste the SQL query
3. Click **Save → Save as Dataset**
4. Name the dataset: `github_project_burn_rate`, `capex_opex_split`, etc.

### 3. Create Dashboard

1. Go to **Dashboards → + Dashboard**
2. Name: **CFO Financial Tracking - GitHub Projects**
3. Add charts from datasets created above
4. Arrange in logical sections:
   - **Section 1**: Project Burn Rate
   - **Section 2**: CapEx vs OpEx
   - **Section 3**: Feature ROI
   - **Section 4**: Developer Productivity
   - **Section 5**: Forecasting

### 4. Configure Filters

Add dashboard-level filters:

```yaml
filters:
  - name: Date Range
    type: time_range
    default: "Last 90 days"

  - name: Expense Type
    type: select
    options: [All, CapEx, OpEx (R&D), OpEx (Maintenance), OpEx (Bug Fix)]

  - name: Project Status
    type: select
    options: [All, Open, Closed]

  - name: Developer
    type: select
    datasource: hr_employee
```

### 5. Set Refresh Schedule

```bash
# In Superset: Dashboard → Edit → Refresh Interval

# Recommended schedules:
# - Burn Rate charts: Every 1 hour
# - CapEx/OpEx: Daily at 2 AM
# - ROI analysis: Weekly on Monday
# - Developer productivity: Daily at 8 AM
```

---

## Troubleshooting

### No Data Showing

**Check Odoo sync:**
```sql
SELECT COUNT(*) FROM github_project;  -- Should return > 0
SELECT COUNT(*) FROM account_analytic_line WHERE github_pr_id IS NOT NULL;  -- Should return > 0
```

**Verify timesheet costs:**
```sql
SELECT * FROM account_analytic_line WHERE amount >= 0;  -- Costs should be negative
```

### Incorrect Cost Calculations

**Check employee hourly rates:**
```sql
SELECT name, hourly_cost FROM hr_employee WHERE hourly_cost = 0 OR hourly_cost IS NULL;
```

**Recalculate project spend:**
```sql
-- Manual recalculation
UPDATE github_project gp
SET project_spend = (
    SELECT SUM(ABS(aal.amount))
    FROM account_analytic_line aal
    WHERE aal.project_id = gp.odoo_project_id
      AND aal.amount < 0
);
```

---

## Export to Excel

All dashboards can be exported:

```bash
# From Superset UI
Dashboard → ... → Download → Excel
```

Or via API:

```bash
curl -X GET "https://your-superset.com/api/v1/chart/export/?q=(ids:!(1,2,3))" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o dashboard_export.zip
```

---

## Next Steps

1. **Automate reporting**: Schedule email delivery of dashboards (Superset → Reports)
2. **Add alerts**: Set up budget threshold alerts (e.g., >80% utilization)
3. **Integrate with BI tools**: Connect Power BI, Tableau, or Looker to same datasource
4. **Track more metrics**: Add code quality metrics, bug rates, deployment frequency

---

## Support

- **Superset Docs**: https://superset.apache.org/docs/intro
- **SQL Troubleshooting**: Check `docs/troubleshooting/superset-sql.md`
- **Contact**: support@insightpulseai.net

---

**Last Updated**: 2025-11-11
**Author**: InsightPulse AI Platform Team
**Version**: 1.0.0

# Superset Dashboard Best Practices & Configuration Guide

## Overview

This guide provides comprehensive instructions for creating professional Apache Superset dashboards for Odoo data, including best practices for visualization design, row-level security, and multi-company analytics.

---

## Table of Contents

1. [Dashboard Design Principles](#dashboard-design-principles)
2. [Sample Dashboard Configurations](#sample-dashboard-configurations)
3. [Row-Level Security Setup](#row-level-security-setup)
4. [Multi-Company Analytics](#multi-company-analytics)
5. [Chart Library](#chart-library)
6. [Performance Optimization](#performance-optimization)
7. [Deployment & Embedding](#deployment--embedding)

---

## Dashboard Design Principles

### 1. Visual Hierarchy

**Priority Levels:**
- **Primary**: KPI cards at the top - most important metrics
- **Secondary**: Trend charts - show patterns over time
- **Tertiary**: Detailed tables and drill-down charts

**Example Layout:**
```
┌─────────────────────────────────────────────────┐
│  [Revenue]  [Orders]  [Avg Value]  [Conv Rate] │  ← KPI Cards
├─────────────────────────────────────────────────┤
│                                                 │
│         Revenue Trend (Line Chart)              │  ← Primary Chart
│                                                 │
├──────────────────────┬──────────────────────────┤
│  Top Products        │  Sales by Region        │  ← Secondary Charts
│  (Bar Chart)         │  (Map/Pie Chart)        │
├──────────────────────┴──────────────────────────┤
│        Recent Orders (Table)                    │  ← Detail View
└─────────────────────────────────────────────────┘
```

### 2. Color Psychology

**Recommended Color Schemes:**

- **Revenue/Profit**: Green tones (#28a745, #20c997)
- **Loss/Negative**: Red tones (#dc3545, #e74c3c)
- **Neutral/Info**: Blue tones (#007bff, #17a2b8)
- **Warning**: Orange/Yellow (#ffc107, #fd7e14)

**Color Blindness Considerations:**
- Avoid red-green combinations
- Use patterns or labels in addition to colors
- Test with colorblind simulators

### 3. Data-Ink Ratio

**Maximize:**
- Actual data representation
- Clear labels
- Meaningful gridlines

**Minimize:**
- Decorative elements
- Unnecessary borders
- Redundant legends

### 4. Chart Selection Guide

| Data Type | Best Chart | Use Case |
|-----------|-----------|----------|
| Time series | Line chart | Revenue trends, user growth |
| Comparison | Bar chart | Product comparison, regional sales |
| Parts of whole | Pie/Donut chart | Market share, category breakdown |
| Distribution | Histogram | Order values, customer segments |
| Relationship | Scatter plot | Price vs. quantity, correlation |
| Geographic | Map | Sales by country, store locations |
| Hierarchical | Sunburst | Category drill-down |
| Process flow | Sankey | Customer journey, fund allocation |

---

## Sample Dashboard Configurations

### Dashboard 1: Sales Executive Overview

**Purpose**: High-level sales metrics for executives

**Target Audience**: C-suite, Sales Directors

**Filters:**
- Date Range (last 30 days default)
- Company (multi-select)
- Sales Team (multi-select)

**Charts:**

#### 1. KPI Cards (Row 1)
```yaml
chart_type: big_number_with_trendline
charts:
  - name: "Total Revenue"
    metric: SUM(amount_total)
    comparison: previous_period
    format: currency
    
  - name: "Order Count"
    metric: COUNT(DISTINCT id)
    comparison: previous_period
    format: number
    
  - name: "Avg Order Value"
    metric: AVG(amount_total)
    comparison: previous_period
    format: currency
    
  - name: "Conversion Rate"
    metric: |
      COUNT(DISTINCT CASE WHEN state IN ('sale','done') THEN id END) /
      NULLIF(COUNT(DISTINCT id), 0) * 100
    comparison: previous_period
    format: percentage
```

**SQL for Revenue KPI:**
```sql
SELECT 
    SUM(amount_total) as metric,
    SUM(amount_total) FILTER (
        WHERE date_order >= CURRENT_DATE - INTERVAL '60 days' 
          AND date_order < CURRENT_DATE - INTERVAL '30 days'
    ) as metric__previous
FROM sale_order
WHERE state IN ('sale', 'done')
  AND date_order >= CURRENT_DATE - INTERVAL '30 days'
  AND company_id = {{ company_filter }}
```

#### 2. Revenue Trend (Row 2)
```yaml
chart_type: line
dataset: vw_sales_kpi_day
x_axis: sale_date
metrics:
  - total_revenue
  - confirmed_revenue
  - delivered_revenue
time_grain: day
rolling_window: 7  # 7-day moving average
```

**Custom SQL:**
```sql
SELECT 
    sale_date,
    SUM(total_revenue) OVER (
        ORDER BY sale_date 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) / 7.0 as rolling_avg_revenue,
    total_revenue
FROM vw_sales_kpi_day
WHERE sale_date >= {{ date_filter.start }}
  AND sale_date <= {{ date_filter.end }}
  AND company_id IN ({{ company_filter }})
ORDER BY sale_date
```

#### 3. Top 10 Products (Row 3, Left)
```yaml
chart_type: bar
dataset: vw_product_performance
metrics:
  - total_revenue
dimensions:
  - product_name
sort: total_revenue DESC
limit: 10
color_scheme: supersetColors
```

#### 4. Sales by Region (Row 3, Right)
```yaml
chart_type: country_map
dataset: vw_customer_ltv
metric: SUM(lifetime_value)
dimension: country_name
color_scheme: blue_shades
```

#### 5. Recent Orders (Row 4)
```yaml
chart_type: table
dataset: sale_order
columns:
  - name
  - partner_id.name
  - date_order
  - amount_total
  - state
sort: date_order DESC
limit: 20
conditional_formatting:
  - column: state
    operator: "="
    value: "done"
    color: green
  - column: amount_total
    operator: ">"
    value: 10000
    color: gold
```

**Export Configuration:**
```json
{
  "dashboard_title": "Sales Executive Overview",
  "slug": "sales-executive-overview",
  "position_json": {
    "CHART-1": {"col": 0, "row": 0, "size_x": 3, "size_y": 4},
    "CHART-2": {"col": 3, "row": 0, "size_x": 3, "size_y": 4},
    "CHART-3": {"col": 6, "row": 0, "size_x": 3, "size_y": 4},
    "CHART-4": {"col": 9, "row": 0, "size_x": 3, "size_y": 4},
    "CHART-5": {"col": 0, "row": 4, "size_x": 12, "size_y": 8},
    "CHART-6": {"col": 0, "row": 12, "size_x": 6, "size_y": 8},
    "CHART-7": {"col": 6, "row": 12, "size_x": 6, "size_y": 8},
    "CHART-8": {"col": 0, "row": 20, "size_x": 12, "size_y": 8}
  },
  "css": "",
  "json_metadata": {
    "timed_refresh_immune_slices": [],
    "refresh_frequency": 300,
    "default_filters": "{}",
    "color_scheme": "supersetColors"
  }
}
```

### Dashboard 2: Financial Performance

**Purpose**: Financial metrics and P&L tracking

**Charts:**

#### Cash Flow Statement
```yaml
chart_type: waterfall
dataset: account_move_line
dimensions:
  - account_id.name
metrics:
  - SUM(CASE WHEN debit > 0 THEN debit ELSE -credit END)
filters:
  - account_id.internal_type IN ('receivable', 'payable', 'liquidity')
```

#### Accounts Receivable Aging
```yaml
chart_type: stacked_bar
custom_sql: |
  SELECT 
    CASE 
      WHEN CURRENT_DATE - date_maturity <= 30 THEN '0-30 days'
      WHEN CURRENT_DATE - date_maturity <= 60 THEN '31-60 days'
      WHEN CURRENT_DATE - date_maturity <= 90 THEN '61-90 days'
      ELSE '90+ days'
    END as aging_bucket,
    SUM(amount_residual) as amount
  FROM account_move_line
  WHERE account_id.internal_type = 'receivable'
    AND reconciled = false
  GROUP BY aging_bucket
  ORDER BY aging_bucket
```

### Dashboard 3: Inventory & Operations

**Purpose**: Warehouse operations and inventory levels

**Charts:**

#### Stock Level Heatmap
```yaml
chart_type: heatmap
dataset: stock_quant
x_axis: location_id.name
y_axis: product_id.name
metric: SUM(quantity)
normalize_across: heatmap
```

#### Turnover Rate
```yaml
chart_type: line
custom_sql: |
  SELECT 
    date_trunc('month', sm.date) as month,
    pt.name as product,
    COUNT(*) / NULLIF(AVG(sq.quantity), 0) as turnover_rate
  FROM stock_move sm
  JOIN product_product pp ON sm.product_id = pp.id
  JOIN product_template pt ON pp.product_tmpl_id = pt.id
  LEFT JOIN stock_quant sq ON sq.product_id = pp.id
  WHERE sm.state = 'done'
  GROUP BY month, pt.name
  ORDER BY month
```

---

## Row-Level Security Setup

### Overview

Row-Level Security (RLS) ensures users only see data they're authorized to access, critical for multi-tenant Superset deployments.

### Implementation Steps

#### 1. Create RLS Filter in Superset

Navigate to: **Data > Row Level Security**

**Filter Name**: `Multi-Company Filter`

**Filter Type**: `Regular`

**Tables**: `vw_sales_kpi_day`, `sale_order`, `purchase_order`, etc.

**SQL WHERE Clause:**
```sql
company_id IN (
    SELECT company_id 
    FROM user_company_access 
    WHERE user_email = '{{ current_username() }}'
)
```

#### 2. Create User-Company Mapping Table

In Odoo PostgreSQL:
```sql
CREATE TABLE user_company_access (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    company_id INTEGER NOT NULL,
    FOREIGN KEY (company_id) REFERENCES res_company(id),
    UNIQUE(user_email, company_id)
);

CREATE INDEX idx_user_company_email ON user_company_access(user_email);

-- Populate from Odoo data
INSERT INTO user_company_access (user_email, company_id)
SELECT 
    u.login as user_email,
    rc.company_id
FROM res_users u
JOIN res_company_users_rel rc ON u.id = rc.user_id
WHERE u.active = true;

-- Keep table in sync with Odoo
CREATE OR REPLACE FUNCTION sync_user_company_access()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO user_company_access (user_email, company_id)
        SELECT login, NEW.company_id
        FROM res_users
        WHERE id = NEW.user_id
        ON CONFLICT (user_email, company_id) DO NOTHING;
    ELSIF TG_OP = 'DELETE' THEN
        DELETE FROM user_company_access
        WHERE user_email = (SELECT login FROM res_users WHERE id = OLD.user_id)
          AND company_id = OLD.company_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_sync_user_company
AFTER INSERT OR DELETE ON res_company_users_rel
FOR EACH ROW
EXECUTE FUNCTION sync_user_company_access();
```

#### 3. Test RLS

**Test Query:**
```sql
-- Login as user@company1.com
SELECT * FROM vw_sales_kpi_day;
-- Should only return Company 1 data

-- Login as admin@multicompany.com (access to all)
SELECT * FROM vw_sales_kpi_day;
-- Should return all companies data
```

#### 4. RLS for Specific Use Cases

**Department-Level Access:**
```sql
-- RLS filter for department managers
department_id IN (
    SELECT department_id 
    FROM user_department_access 
    WHERE user_email = '{{ current_username() }}'
)
```

**Time-Based Access:**
```sql
-- RLS filter for time-restricted data
date_order >= (
    SELECT access_start_date 
    FROM user_access_periods 
    WHERE user_email = '{{ current_username() }}'
)
AND date_order <= (
    SELECT access_end_date 
    FROM user_access_periods 
    WHERE user_email = '{{ current_username() }}'
)
```

### Advanced RLS Patterns

#### Dynamic Role-Based Filtering
```sql
-- Different filters based on user role
CASE 
    WHEN '{{ current_username() }}' IN (
        SELECT email FROM users WHERE role = 'admin'
    ) THEN TRUE
    WHEN '{{ current_username() }}' IN (
        SELECT email FROM users WHERE role = 'manager'
    ) THEN team_id IN (
        SELECT team_id FROM user_teams WHERE email = '{{ current_username() }}'
    )
    ELSE user_id = (
        SELECT id FROM res_users WHERE login = '{{ current_username() }}'
    )
END
```

---

## Multi-Company Analytics

### Challenge

Odoo's multi-company feature requires careful handling in Superset to:
1. Prevent data leakage between companies
2. Enable cross-company reporting for authorized users
3. Maintain performance with large datasets

### Solution Architecture

```
┌─────────────────────────────────────────┐
│          Superset Dashboard             │
├─────────────────────────────────────────┤
│  Company Filter: [Company A] [Company B]│
│                  (Multi-select)         │
├─────────────────────────────────────────┤
│              RLS Layer                  │
│  (Filters based on user permissions)   │
├─────────────────────────────────────────┤
│          PostgreSQL Views               │
│  (Include company_id in all queries)   │
├─────────────────────────────────────────┤
│           Odoo Database                 │
└─────────────────────────────────────────┘
```

### Implementation

#### 1. Create Multi-Company Views

```sql
-- Consolidated sales view across companies
CREATE OR REPLACE VIEW vw_multi_company_sales AS
SELECT 
    so.id,
    so.name as order_number,
    so.company_id,
    c.name as company_name,
    so.partner_id,
    p.name as customer_name,
    so.date_order,
    so.amount_total,
    so.state,
    -- Add company currency handling
    so.amount_total * COALESCE(
        (SELECT rate FROM res_currency_rate 
         WHERE currency_id = c.currency_id 
         AND name <= so.date_order 
         ORDER BY name DESC LIMIT 1), 
        1.0
    ) as amount_total_base_currency
FROM sale_order so
JOIN res_company c ON so.company_id = c.id
JOIN res_partner p ON so.partner_id = p.id
WHERE so.state IN ('sale', 'done');
```

#### 2. Cross-Company Comparison Dashboard

**Chart: Revenue by Company**
```yaml
chart_type: bar
dataset: vw_multi_company_sales
x_axis: company_name
metric: SUM(amount_total_base_currency)
sort: metric DESC
```

**Chart: Inter-Company Transactions**
```sql
SELECT 
    c1.name as from_company,
    c2.name as to_company,
    COUNT(*) as transaction_count,
    SUM(so.amount_total) as total_value
FROM sale_order so
JOIN res_company c1 ON so.company_id = c1.id
JOIN res_partner p ON so.partner_id = p.id
JOIN res_company c2 ON p.company_id = c2.id
WHERE c1.id != c2.id
  AND so.state IN ('sale', 'done')
GROUP BY c1.name, c2.name
```

#### 3. Company-Specific KPIs with Benchmarking

```sql
WITH company_metrics AS (
    SELECT 
        company_id,
        company_name,
        SUM(total_revenue) as revenue,
        COUNT(DISTINCT partner_id) as customer_count,
        AVG(amount_total) as avg_order_value
    FROM vw_sales_kpi_day
    WHERE sale_date >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY company_id, company_name
),
overall_metrics AS (
    SELECT 
        AVG(revenue) as avg_revenue,
        AVG(customer_count) as avg_customers,
        AVG(avg_order_value) as avg_aov
    FROM company_metrics
)
SELECT 
    cm.*,
    om.avg_revenue as benchmark_revenue,
    (cm.revenue - om.avg_revenue) / NULLIF(om.avg_revenue, 0) * 100 as revenue_vs_avg_pct
FROM company_metrics cm
CROSS JOIN overall_metrics om
ORDER BY cm.revenue DESC;
```

---

## Chart Library

### Pre-built Chart Configurations

All chart configurations are available as JSON exports in `examples/superset/charts/`.

To import:
1. Go to Charts > Import Charts
2. Upload the JSON file
3. Map to your datasets

### Chart Types Reference

See `docs/KNOWLEDGE.md` for detailed chart type selection guide.

---

## Performance Optimization

### 1. Caching Strategy

**Redis Cache Configuration:**
```python
# superset_config.py
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 300,  # 5 minutes
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0'
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',
    'CACHE_DEFAULT_TIMEOUT': 3600,  # 1 hour for data
    'CACHE_KEY_PREFIX': 'superset_data_',
    'CACHE_REDIS_URL': 'redis://localhost:6379/1'
}
```

### 2. Query Optimization

**Use EXPLAIN ANALYZE:**
```sql
EXPLAIN ANALYZE
SELECT * FROM vw_sales_kpi_day
WHERE sale_date >= '2025-01-01';
```

**Add Appropriate Indexes:**
```sql
CREATE INDEX idx_sale_order_date_company 
ON sale_order(date_order, company_id) 
WHERE state IN ('sale', 'done');
```

### 3. Materialized Views

For expensive aggregations:
```sql
CREATE MATERIALIZED VIEW mv_monthly_sales AS
SELECT 
    date_trunc('month', date_order) as month,
    company_id,
    SUM(amount_total) as total_revenue,
    COUNT(*) as order_count
FROM sale_order
WHERE state IN ('sale', 'done')
GROUP BY month, company_id;

CREATE UNIQUE INDEX ON mv_monthly_sales (month, company_id);

-- Refresh via cron
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_monthly_sales;
```

---

## Deployment & Embedding

### Embedded Dashboard Configuration

```python
# Generate guest token for embedding
from superset import app, security_manager

guest_user = {
    'username': 'guest',
    'first_name': 'Guest',
    'last_name': 'User'
}

embedded_config = {
    'dashboard_id': 1,
    'rls': [
        {'clause': f"company_id = {company_id}"}
    ],
    'user': guest_user
}

guest_token = security_manager.get_guest_token(embedded_config)
```

**Iframe Embed:**
```html
<iframe
  src="https://superset.example.com/superset/dashboard/1/?standalone=true&guest_token={guest_token}"
  width="100%"
  height="800"
  frameborder="0"
></iframe>
```

### Odoo Integration Module

See `examples/odoo_modules/superset_embed/` for complete Odoo module.

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Slow dashboard load | Large datasets, no caching | Enable caching, use materialized views |
| RLS not working | Incorrect SQL syntax | Test RLS clause directly in SQL Lab |
| Charts not updating | Stale cache | Clear cache or reduce cache timeout |
| Permission denied | Missing database grants | Grant SELECT on tables to Superset user |

---

**Last Updated**: 2025-10-26  
**Superset Version**: 3.0+  
**Odoo Version**: 19.0

# Draxlr Integration

**Skill ID:** `draxlr_integration`
**Version:** 1.0.0
**Category:** Analytics, Business Intelligence
**Expertise Level:** Intermediate

---

## 🎯 Purpose

This skill enables low-lift analytics and BI integration using Draxlr, a lightweight alternative to traditional BI tools like Tableau or Power BI. Draxlr provides instant SQL-to-dashboard capabilities with minimal setup.

### Key Capabilities
- Quick dataset configuration from PostgreSQL/Supabase
- SQL-based chart and dashboard creation
- Embedded analytics for web applications
- Real-time data visualization
- Shareable dashboards and reports
- Role-based access control

---

## 🧠 Core Competencies

### 1. Database Connection Setup

#### Supabase/PostgreSQL Connection
```json
{
  "type": "postgres",
  "host": "aws-1-us-east-1.pooler.supabase.com",
  "port": 6543,
  "database": "postgres",
  "username": "postgres.PROJECT_REF",
  "password": "YOUR_PASSWORD",
  "ssl": true,
  "schema": "public"
}
```

#### Connection Configuration
```python
# scripts/draxlr/configure_connection.py
import os
import requests
from typing import Dict, Any

DRAXLR_API_KEY = os.getenv('DRAXLR_API_KEY')
DRAXLR_BASE_URL = 'https://api.draxlr.com/v1'

def create_connection(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a new database connection in Draxlr"""
    response = requests.post(
        f'{DRAXLR_BASE_URL}/connections',
        headers={
            'Authorization': f'Bearer {DRAXLR_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'name': config['name'],
            'type': config['type'],
            'config': {
                'host': config['host'],
                'port': config['port'],
                'database': config['database'],
                'username': config['username'],
                'password': config['password'],
                'ssl': config.get('ssl', True)
            }
        }
    )
    response.raise_for_status()
    return response.json()

# Example usage
connection = create_connection({
    'name': 'InsightPulse Supabase',
    'type': 'postgres',
    'host': os.getenv('SUPABASE_DB_HOST'),
    'port': int(os.getenv('SUPABASE_DB_PORT', 6543)),
    'database': os.getenv('SUPABASE_DB_NAME'),
    'username': os.getenv('SUPABASE_DB_USER'),
    'password': os.getenv('SUPABASE_DB_PASSWORD'),
    'ssl': True
})

print(f"✅ Connection created: {connection['id']}")
```

### 2. Dataset Configuration

#### Analytics View Setup
```sql
-- warehouse/draxlr/expense_analytics.sql
-- View optimized for Draxlr dashboards

CREATE OR REPLACE VIEW draxlr.vw_expense_analytics AS
SELECT
    e.id,
    e.name AS expense_name,
    e.employee_id,
    emp.name AS employee_name,
    emp.department_id,
    dept.name AS department_name,
    e.total_amount,
    e.date AS expense_date,
    DATE_TRUNC('month', e.date) AS expense_month,
    DATE_TRUNC('week', e.date) AS expense_week,
    e.state AS approval_status,
    e.x_category AS category,
    e.x_merchant AS merchant,
    e.x_policy_breach AS has_policy_breach,
    e.x_ocr_confidence AS ocr_confidence,
    e.x_approval_latency_days AS approval_latency_days,
    CASE
        WHEN e.x_approval_latency_days <= 1 THEN 'Fast'
        WHEN e.x_approval_latency_days <= 3 THEN 'Normal'
        ELSE 'Slow'
    END AS approval_speed,
    CASE
        WHEN e.total_amount < 50 THEN 'Small'
        WHEN e.total_amount < 200 THEN 'Medium'
        WHEN e.total_amount < 500 THEN 'Large'
        ELSE 'Very Large'
    END AS expense_size_category
FROM staging_odoo.hr_expense e
LEFT JOIN staging_odoo.hr_employee emp ON e.employee_id = emp.id
LEFT JOIN staging_odoo.hr_department dept ON emp.department_id = dept.id
WHERE e.date >= CURRENT_DATE - INTERVAL '90 days';

-- Grant access
GRANT SELECT ON draxlr.vw_expense_analytics TO draxlr_viewer;
```

#### Dataset Registration
```json
{
  "name": "Expense Analytics",
  "connection_id": "conn_123abc",
  "type": "view",
  "schema": "draxlr",
  "table": "vw_expense_analytics",
  "refresh_schedule": "0 */6 * * *",
  "description": "90-day expense analytics with employee and department context",
  "columns": [
    {"name": "id", "type": "integer", "description": "Expense ID"},
    {"name": "expense_name", "type": "text", "description": "Expense description"},
    {"name": "employee_name", "type": "text", "description": "Employee name"},
    {"name": "department_name", "type": "text", "description": "Department"},
    {"name": "total_amount", "type": "numeric", "description": "Expense amount", "format": "currency"},
    {"name": "expense_date", "type": "date", "description": "Expense date"},
    {"name": "expense_month", "type": "date", "description": "Month bucket"},
    {"name": "category", "type": "text", "description": "Expense category"},
    {"name": "approval_status", "type": "text", "description": "Current status"},
    {"name": "has_policy_breach", "type": "boolean", "description": "Policy violation flag"}
  ]
}
```

### 3. Chart Creation

#### SQL-Based Chart Definitions
```yaml
# draxlr/charts/expense_by_month.yml
name: "Monthly Expense Trends"
type: "line"
dataset: "expense_analytics"
query: |
  SELECT
    expense_month AS month,
    SUM(total_amount) AS total_expenses,
    COUNT(*) AS expense_count,
    AVG(total_amount) AS avg_expense
  FROM draxlr.vw_expense_analytics
  WHERE expense_month >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY expense_month
  ORDER BY expense_month

x_axis: "month"
y_axes:
  - column: "total_expenses"
    label: "Total Amount"
    format: "currency"
  - column: "expense_count"
    label: "Count"
    format: "number"

filters:
  - column: "department_name"
    type: "multi-select"
    label: "Department"
  - column: "expense_month"
    type: "date-range"
    label: "Date Range"
```

#### Python Chart Builder
```python
# scripts/draxlr/create_chart.py
def create_chart(config: Dict[str, Any]) -> Dict[str, Any]:
    """Create a chart in Draxlr"""
    response = requests.post(
        f'{DRAXLR_BASE_URL}/charts',
        headers={
            'Authorization': f'Bearer {DRAXLR_API_KEY}',
            'Content-Type': 'application/json'
        },
        json={
            'name': config['name'],
            'type': config['type'],
            'dataset_id': config['dataset_id'],
            'query': config['query'],
            'config': {
                'x_axis': config.get('x_axis'),
                'y_axes': config.get('y_axes', []),
                'filters': config.get('filters', []),
                'colors': config.get('colors', ['#3B82F6', '#10B981', '#F59E0B'])
            }
        }
    )
    response.raise_for_status()
    return response.json()

# Example: Top 10 merchants by spend
chart = create_chart({
    'name': 'Top Merchants by Spend',
    'type': 'bar',
    'dataset_id': 'ds_expense_analytics',
    'query': '''
        SELECT merchant, SUM(total_amount) AS total_spend
        FROM draxlr.vw_expense_analytics
        WHERE merchant IS NOT NULL
        GROUP BY merchant
        ORDER BY total_spend DESC
        LIMIT 10
    ''',
    'x_axis': 'merchant',
    'y_axes': [{'column': 'total_spend', 'label': 'Total Spend', 'format': 'currency'}]
})
```

### 4. Dashboard Assembly

#### Dashboard Configuration
```json
{
  "name": "T&E Executive Dashboard",
  "description": "Real-time travel and expense analytics",
  "layout": {
    "type": "grid",
    "columns": 12,
    "widgets": [
      {
        "chart_id": "chart_monthly_trends",
        "position": {"x": 0, "y": 0, "w": 8, "h": 4}
      },
      {
        "chart_id": "chart_top_merchants",
        "position": {"x": 8, "y": 0, "w": 4, "h": 4}
      },
      {
        "chart_id": "chart_policy_violations",
        "position": {"x": 0, "y": 4, "w": 6, "h": 3}
      },
      {
        "chart_id": "chart_approval_latency",
        "position": {"x": 6, "y": 4, "w": 6, "h": 3}
      }
    ]
  },
  "filters": [
    {"type": "date-range", "default": "last_90_days"},
    {"type": "department", "default": "all"}
  ],
  "refresh_interval": 300
}
```

### 5. Embedded Analytics

#### Embed Code Generation
```html
<!-- Example: Embed Draxlr dashboard in Odoo web module -->
<template id="draxlr_dashboard_embed" name="Draxlr Dashboard">
  <t t-name="draxlr.dashboard">
    <div class="o_draxlr_dashboard">
      <iframe
        src="https://app.draxlr.com/embed/dashboard/DASHBOARD_ID?token=EMBED_TOKEN"
        width="100%"
        height="800px"
        frameborder="0"
        allowfullscreen
      ></iframe>
    </div>
  </t>
</template>
```

#### Dynamic Embed with Filters
```javascript
// odoo/modules/ip_expense_ocr/static/src/js/draxlr_embed.js
odoo.define('ip_expense_ocr.draxlr_embed', function (require) {
    "use strict";

    const AbstractField = require('web.AbstractField');
    const fieldRegistry = require('web.field_registry');

    const DraxlrDashboard = AbstractField.extend({
        template: 'DraxlrDashboardWidget',

        start: function () {
            this._super.apply(this, arguments);
            this._renderDashboard();
        },

        _renderDashboard: function () {
            const dashboardId = this.recordData.dashboard_id || 'default';
            const embedToken = this.recordData.embed_token;
            const department = this.recordData.department_id;

            const iframeUrl = `https://app.draxlr.com/embed/dashboard/${dashboardId}` +
                `?token=${embedToken}` +
                `&filter_department=${department}`;

            this.$el.html(`
                <iframe src="${iframeUrl}"
                        width="100%"
                        height="600px"
                        frameborder="0"
                        allowfullscreen>
                </iframe>
            `);
        }
    });

    fieldRegistry.add('draxlr_dashboard', DraxlrDashboard);
});
```

---

## ✅ Validation Criteria

### Integration Quality
- ✅ Connection established with <2s latency
- ✅ Datasets refresh on schedule (every 6 hours)
- ✅ Charts render in <3s
- ✅ Dashboards support 100+ concurrent viewers
- ✅ Embed tokens have expiry and rotation

### Data Accuracy
- ✅ SQL views match Odoo source data
- ✅ Aggregations validated against source
- ✅ Filters work correctly with parameters
- ✅ Real-time data sync lag <5 minutes

---

## 🎯 Usage Examples

### Example 1: Quick Dashboard Setup
```bash
# Create analytics views
psql $SUPABASE_DB_URL -f warehouse/draxlr/expense_analytics.sql

# Configure connection (via Draxlr UI or API)
python3 scripts/draxlr/configure_connection.py

# Create dataset and charts
python3 scripts/draxlr/setup_dashboard.py
```

### Example 2: Embedded Report in Odoo
```xml
<!-- Add to Odoo expense form view -->
<page string="Analytics" name="analytics">
  <field name="draxlr_dashboard" widget="draxlr_dashboard"/>
</page>
```

### Example 3: Automated Report Distribution
```python
# scripts/draxlr/scheduled_report.py
def email_dashboard_snapshot(dashboard_id: str, recipients: list):
    """Email dashboard snapshot via Draxlr API"""
    response = requests.post(
        f'{DRAXLR_BASE_URL}/dashboards/{dashboard_id}/snapshot',
        headers={'Authorization': f'Bearer {DRAXLR_API_KEY}'},
        json={
            'format': 'pdf',
            'recipients': recipients,
            'subject': 'Weekly Expense Report',
            'filters': {'date_range': 'last_7_days'}
        }
    )
    return response.json()

# Schedule with cron or pg_cron
email_dashboard_snapshot('dash_tne_exec', ['finance@company.com'])
```

---

## 📊 Success Metrics

### Adoption Metrics
- **Dashboard Views**: 100+ per day
- **Unique Users**: 20+ per week
- **Report Exports**: 10+ per week
- **Embed Usage**: 50+ views per day

### Performance Metrics
- **Query Response Time**: <2s p95
- **Dashboard Load Time**: <3s
- **Data Freshness**: <5min lag
- **Uptime**: >99.5%

---

## 🔗 Related Skills
- `superset-dashboard-automation` - Apache Superset alternative
- `superset-chart-builder` - Advanced BI charting
- `odoo-finance-automation` - Source data for analytics

---

## 📚 References

- [Draxlr Documentation](https://docs.draxlr.com/)
- [Draxlr API Reference](https://api.draxlr.com/docs)
- [Draxlr vs Superset Comparison](https://draxlr.com/vs/superset)
- [Embedded Analytics Guide](https://docs.draxlr.com/embedding)

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
**Integration Type:** Optional - Analytics Enhancement

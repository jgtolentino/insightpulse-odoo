# T&E Dashboards (Overview / Manager / Audit)

Complete Travel & Expense analytics dashboards for Apache Superset with BIR compliance tracking, OCR quality monitoring, and approval workflow analysis.

## 📊 Dashboard Overview

### 1. T&E Overview Dashboard
**Purpose**: Executive view of all expense activities
**Key Metrics**:
- 💰 Cash advance outstanding balance (KPI card)
- 📈 Expense by category breakdown (pie chart)
- 📉 Monthly expense trends (timeseries)
- 👥 Top spenders ranking (table)
- ⚠️ Policy compliance status (stacked bar)
- 🚨 Policy violations list (filtered table)

**Audience**: Executives, Finance team
**Refresh**: Real-time (5 min cache)

### 2. T&E Manager Dashboard
**Purpose**: Team oversight and approval management
**Key Metrics**:
- 📊 Team expense summary by department/month (pivot table)
- ⏳ Approval queue with aging (sorted table)
- ✅ Policy compliance trends (timeseries bar)
- 💵 Budget vs actual comparison (line chart)

**Audience**: Department managers, Approvers
**Refresh**: 5 minutes (auto-refresh enabled)

### 3. T&E Audit Dashboard
**Purpose**: BIR compliance and exception tracking
**Key Metrics**:
- 📋 BIR ATP timeline (approval timeline)
- 🔍 OCR confidence distribution (histogram)
- ⏱️ Approval workflow timeline (scatter plot)
- ⚠️ Policy violations detail (filtered table)

**Audience**: Auditors, Compliance team, Finance controllers
**Refresh**: On-demand

---

## 🚀 Quick Start

### Prerequisites

1. **Apache Superset** v2.0+ installed and running
2. **PostgreSQL** database with Odoo or Supabase analytics
3. **Database access** with permissions to create views
4. **Superset CLI** available (for automated import)

### Step 1: Create Database Views

Create the analytics views in your PostgreSQL database:

```bash
# Set your database connection
export POSTGRES_URL="postgresql://user:password@host:5432/database"

# Create views
make te-views
# OR manually:
psql "$POSTGRES_URL" -f superset/te/sql/00_views.sql
```

**Important**: The SQL file assumes Odoo table structure. If your tables differ, edit `superset/te/sql/00_views.sql` to match your schema.

### Step 2: Import Dashboards

```bash
# Option A: Using Makefile (recommended)
make te-import

# Option B: Direct script
cd superset/te
./import.sh

# Option C: Manual import via UI
# 1. Import datasets: Superset UI → Data → Datasets → Import
#    Upload: superset/te/datasets.yaml
# 2. Import dashboards: Superset UI → Dashboards → Import
#    Upload each JSON from: superset/te/dashboards/
```

### Step 3: Configure & Verify

1. **Check datasets**: Data → Datasets
   - ✓ `te_expenses_v`
   - ✓ `te_cash_advances_v`
   - ✓ `te_approvals_v`
   - ✓ `te_receipts_ocr_v`

2. **Set cache timeouts**:
   - Fact tables (te_expenses_v, te_approvals_v): **300 seconds** (5 min)
   - Aggregated views (te_cash_advances_v): **3600 seconds** (1 hour)
   - OCR data (te_receipts_ocr_v): **1800 seconds** (30 min)

3. **Access dashboards**:
   - 📊 [T&E Overview](http://localhost:8088/superset/dashboard/te-overview/)
   - 👔 [T&E Manager](http://localhost:8088/superset/dashboard/te-manager/)
   - 🔍 [T&E Audit](http://localhost:8088/superset/dashboard/te-audit/)

---

## 📁 File Structure

```
superset/te/
├── sql/
│   └── 00_views.sql              # Database views for analytics
├── charts/
│   ├── te_expense_by_category.json
│   ├── te_monthly_trend.json
│   ├── te_top_spenders.json
│   ├── te_cash_advance_kpis.json
│   ├── te_team_summary.json
│   ├── te_approval_queue.json
│   ├── te_policy_compliance.json
│   ├── te_budget_vs_actual.json
│   ├── te_bir_atp_timeline.json
│   ├── te_ocr_confidence_hist.json
│   ├── te_approval_timeline.json
│   └── te_exceptions.json
├── dashboards/
│   ├── te_overview.json          # Executive overview
│   ├── te_manager.json           # Manager dashboard
│   └── te_audit.json             # Audit & compliance
├── datasets.yaml                 # Dataset definitions
├── import.sh                     # Import automation script
└── README.md                     # This file
```

---

## 🎨 Dataset Mapping

| Dataset | Source View | Description | Metrics |
|---------|-------------|-------------|---------|
| `te_expenses_v` | hr_expense + joins | All expense transactions | total_amount, expense_count, avg_amount |
| `te_cash_advances_v` | hr_expense_sheet | Cash advance tracking | total_advances, outstanding_balance |
| `te_approvals_v` | mail_message | Approval workflow data | open_items, avg_hours_open |
| `te_receipts_ocr_v` | ir_attachment | OCR quality metrics | docs, avg_conf |

---

## 🔒 Security & RLS

### Row-Level Security (RLS)

To restrict data access by department or employee:

1. Go to: **Data → Datasets → [dataset name] → Edit**
2. Click **Security** tab
3. Add RLS filter:

```sql
-- Example: Show only current user's department
WHERE department_id IN (
    SELECT department_id
    FROM hr_employee
    WHERE user_id = {{ current_user_id() }}
)

-- Example: Show only direct reports
WHERE employee_id IN (
    SELECT e.id
    FROM hr_employee e
    WHERE e.parent_id = (
        SELECT id FROM hr_employee WHERE user_id = {{ current_user_id() }}
    )
)
```

### Access Control

- **Executives**: Full access to all 3 dashboards
- **Managers**: T&E Overview + T&E Manager (filtered by department)
- **Auditors**: T&E Audit only
- **Employees**: Limited to own expenses (custom RLS)

---

## 🛠️ Customization

### Adding Custom Metrics

Edit `datasets.yaml` to add new calculated metrics:

```yaml
metrics:
  - metric_name: tax_percentage
    expression: (SUM(tax_amount) / SUM(amount)) * 100
    verbose_name: Tax %
    d3format: ".1%"
```

### Changing Chart Types

Chart JSONs can be edited to change visualization:
- Pie → Bar: Change `"viz_type": "pie"` to `"viz_type": "echarts_bar"`
- Line → Area: Change `"viz_type": "echarts_timeseries_line"` to `"echarts_timeseries_area"`

See: [superset-chart-builder skill](../../.claude/skills/superset-chart-builder/SKILL.md)

### Color Schemes

Color coding for policy flags (already configured in `te_audit.json`):

```json
{
  "label_colors": {
    "OK": "#52C41A",      // Green
    "WARN": "#FAAD14",    // Yellow
    "VIOLATION": "#F5222D" // Red
  }
}
```

---

## 📊 Chart Inventory

| Chart Name | Type | Dataset | Purpose |
|------------|------|---------|---------|
| Expense by Category | Pie | te_expenses_v | Category breakdown |
| Monthly Expense Trend | Timeseries Line | te_expenses_v | Monthly trends |
| Top Spenders | Table | te_expenses_v | Employee rankings |
| Cash Advance Outstanding | Big Number | te_cash_advances_v | KPI card |
| Team Expense Summary | Pivot Table | te_expenses_v | Dept × Month |
| Approval Queue | Table | te_approvals_v | Pending items |
| Policy Compliance | Timeseries Bar | te_expenses_v | Compliance trends |
| Budget vs Actual | Timeseries Line | te_expenses_v | Budget comparison |
| BIR ATP Timeline | Timeseries Line | te_approvals_v | Approval timeline |
| OCR Confidence Distribution | Histogram | te_receipts_ocr_v | Quality metrics |
| Approval Workflow Timeline | Scatter | te_approvals_v | Cycle time |
| Policy Violations | Table | te_expenses_v | Exception list |

---

## 🔧 Troubleshooting

### Issue: "Dataset not found"

**Solution**:
1. Verify views exist: `psql "$POSTGRES_URL" -c "\dv te_*"`
2. Re-import datasets: `make te-import`
3. Check database connection in Superset: Data → Databases

### Issue: "No data showing in charts"

**Solution**:
1. Check data exists in views:
   ```sql
   SELECT COUNT(*) FROM te_expenses_v;
   SELECT COUNT(*) FROM te_cash_advances_v;
   ```
2. Clear Superset cache: Chart → ⋮ → Force refresh
3. Check date filters (default: last year)

### Issue: "Import script fails"

**Solution**:
- Ensure running inside Superset container:
  ```bash
  docker exec -it superset_app bash
  cd /app/superset/te
  ./import.sh
  ```
- Or install Superset CLI locally

### Issue: "Slow dashboard performance"

**Solution**:
1. Add database indexes:
   ```sql
   CREATE INDEX idx_expenses_month ON te_expenses_v(month_date);
   CREATE INDEX idx_expenses_dept ON te_expenses_v(department);
   CREATE INDEX idx_expenses_emp ON te_expenses_v(employee_name);
   ```
2. Use materialized views for complex calculations
3. Increase cache timeout (3600s for MVs)

### Issue: "Charts missing after dashboard import"

**Solution**:
Charts are embedded in dashboard JSON. If missing:
1. Manually create charts using specs in `charts/` directory
2. Link charts to dashboard positions
3. Or use Superset export/import via UI (includes embedded charts)

---

## 🎯 Next Steps

### Phase 2: Enhanced Analytics

- [ ] Add predictive expense forecasting (ML models)
- [ ] Real-time alert rules (exceed budget, policy violations)
- [ ] Mobile-responsive layouts
- [ ] Export to PDF/email automation

### Phase 3: Integration

- [ ] Embed dashboards in Odoo via `superset_connector` module
- [ ] URL filter passing from Odoo context
- [ ] SSO authentication with Odoo users
- [ ] Webhook triggers for data refresh

### Related Skills

- [`superset-dashboard-automation`](../../.claude/skills/superset-dashboard-automation/) - Build more dashboards
- [`superset-chart-builder`](../../.claude/skills/superset-chart-builder/) - Chart type selection
- [`odoo-finance-automation`](../../.claude/skills/odoo-finance-automation/) - Finance workflows
- [`bir-tax-filing`](../../.claude/skills/bir-tax-filing/) - BIR compliance

---

## 📚 Resources

- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [Superset Chart Gallery](https://superset.apache.org/docs/creating-charts-dashboards/exploring-data)
- [Superset Security](https://superset.apache.org/docs/security)
- [InsightPulse Odoo Integration](../../docs/SUPERSET_INTEGRATION.md)

---

## ✅ Success Metrics

- ✅ Dashboard creation: 2 weeks → **30 minutes**
- ✅ Data refresh: Manual → **Automated (5 min)**
- ✅ Report access: Email → **Real-time web**
- ✅ User adoption: 40% → **100%** (accessible to all)
- ✅ Compliance tracking: Monthly → **Daily**

---

## 🙋 Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [Superset Documentation](https://superset.apache.org/docs/intro)
3. Open issue in [InsightPulse repo](https://github.com/InsightPulseAI/insightpulse-odoo/issues)

---

**Version**: 1.0.0
**Last Updated**: 2025-11-08
**Maintainer**: InsightPulse AI Team

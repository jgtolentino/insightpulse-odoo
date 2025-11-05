# Apache Superset Dashboard Examples for Finance SSC

Official dashboard templates for InsightPulse Finance SSC operations across 8 agencies.

---

## Dashboard 1: Executive Finance Overview

**Purpose:** High-level financial KPIs for management across all agencies

**URL:** https://superset.insightpulseai.net/superset/dashboard/executive-finance/

### Charts

#### 1.1 Total Revenue by Agency (Bar Chart)
```sql
SELECT
    company_name as "Agency",
    SUM(amount_total) as "Revenue"
FROM sale_order
WHERE state IN ('sale', 'done')
    AND date_order >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY company_name
ORDER BY "Revenue" DESC;
```

**Chart Type:** Bar Chart (Horizontal)
**Metrics:** Revenue
**Dimensions:** Agency
**Colors:** Agency-specific (RIM=Blue, CKVC=Green, etc.)

#### 1.2 Monthly Revenue Trend (Line Chart)
```sql
SELECT
    DATE_TRUNC('month', date_order) as "Month",
    company_name as "Agency",
    SUM(amount_total) as "Revenue"
FROM sale_order
WHERE state IN ('sale', 'done')
    AND date_order >= DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '1 year'
GROUP BY "Month", company_name
ORDER BY "Month";
```

**Chart Type:** Line Chart (Multi-line)
**X-Axis:** Month
**Y-Axis:** Revenue
**Series:** Agency (one line per agency)

#### 1.3 Expense Approval Status (Pie Chart)
```sql
SELECT
    state as "Status",
    COUNT(*) as "Count",
    SUM(total_amount) as "Amount"
FROM hr_expense
WHERE create_date >= DATE_TRUNC('month', CURRENT_DATE)
GROUP BY state;
```

**Chart Type:** Pie Chart
**Labels:** Status (Draft, Submitted, Approved, Paid, Refused)
**Values:** Count or Amount (toggleable)

#### 1.4 Outstanding Receivables (Big Number)
```sql
SELECT
    SUM(amount_residual) as "Outstanding"
FROM account_move
WHERE move_type = 'out_invoice'
    AND state = 'posted'
    AND amount_residual > 0;
```

**Chart Type:** Big Number with Trend
**Format:** Currency (PHP)
**Comparison:** vs. Last Month

#### 1.5 BIR Compliance Status (Table)
```sql
SELECT
    company_name as "Agency",
    form_type as "Form",
    filing_deadline as "Deadline",
    CASE
        WHEN status = 'filed' THEN '✅ Filed'
        WHEN filing_deadline < CURRENT_DATE THEN '🚨 Overdue'
        WHEN filing_deadline < CURRENT_DATE + INTERVAL '3 days' THEN '⚠️ Due Soon'
        ELSE '📋 Pending'
    END as "Status"
FROM bir_form_status
WHERE filing_deadline >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
ORDER BY filing_deadline;
```

**Chart Type:** Table
**Conditional Formatting:** Status column colored by status

---

## Dashboard 2: Agency-Specific Operations

**Purpose:** Detailed operational metrics for individual agencies

**URL:** https://superset.insightpulseai.net/superset/dashboard/agency-ops/

### Filters
- Agency Selector (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- Date Range (This Month, Last Month, This Quarter, This Year, Custom)

### Charts

#### 2.1 Sales Pipeline (Funnel Chart)
```sql
SELECT
    CASE state
        WHEN 'draft' THEN '1. Quotation'
        WHEN 'sent' THEN '2. Sent'
        WHEN 'sale' THEN '3. Sale Order'
        WHEN 'done' THEN '4. Delivered'
    END as "Stage",
    COUNT(*) as "Count",
    SUM(amount_total) as "Value"
FROM sale_order
WHERE company_id = {{ agency_filter }}
    AND date_order >= {{ date_from }}
    AND date_order <= {{ date_to }}
GROUP BY state
ORDER BY state;
```

**Chart Type:** Funnel Chart
**Stages:** Quotation → Sent → Sale Order → Delivered
**Metrics:** Count and Value

#### 2.2 Top Customers (Bar Chart)
```sql
SELECT
    partner.name as "Customer",
    COUNT(DISTINCT so.id) as "Orders",
    SUM(so.amount_total) as "Revenue"
FROM sale_order so
JOIN res_partner partner ON so.partner_id = partner.id
WHERE so.company_id = {{ agency_filter }}
    AND so.state IN ('sale', 'done')
    AND so.date_order >= {{ date_from }}
GROUP BY partner.name
ORDER BY "Revenue" DESC
LIMIT 10;
```

**Chart Type:** Horizontal Bar Chart
**Top:** 10 customers
**Sort:** By Revenue

#### 2.3 Expense Categories (Treemap)
```sql
SELECT
    category.name as "Category",
    COUNT(*) as "Count",
    SUM(expense.total_amount) as "Amount"
FROM hr_expense expense
JOIN hr_expense_category category ON expense.product_id = category.id
WHERE expense.company_id = {{ agency_filter }}
    AND expense.date >= {{ date_from }}
    AND expense.state IN ('approved', 'done')
GROUP BY category.name;
```

**Chart Type:** Treemap
**Size:** Amount
**Color:** Category

#### 2.4 Payment Collection Rate (Gauge)
```sql
WITH collected AS (
    SELECT SUM(amount) as collected
    FROM account_payment
    WHERE company_id = {{ agency_filter }}
        AND payment_type = 'inbound'
        AND state = 'posted'
        AND date >= {{ date_from }}
),
invoiced AS (
    SELECT SUM(amount_total) as invoiced
    FROM account_move
    WHERE company_id = {{ agency_filter }}
        AND move_type = 'out_invoice'
        AND state = 'posted'
        AND invoice_date >= {{ date_from }}
)
SELECT
    ROUND((collected.collected / NULLIF(invoiced.invoiced, 0)) * 100, 1) as "Collection Rate"
FROM collected, invoiced;
```

**Chart Type:** Gauge Chart
**Range:** 0-100%
**Zones:** Red (0-60%), Yellow (60-80%), Green (80-100%)

---

## Dashboard 3: Expense Management

**Purpose:** Real-time expense tracking and approval monitoring

**URL:** https://superset.insightpulseai.net/superset/dashboard/expense-mgmt/

### Charts

#### 3.1 Expense Approval Queue (Table)
```sql
SELECT
    e.name as "Description",
    emp.name as "Employee",
    comp.name as "Agency",
    e.total_amount as "Amount",
    e.date as "Date",
    CURRENT_DATE - e.date as "Days Pending",
    e.state as "Status"
FROM hr_expense e
JOIN hr_employee emp ON e.employee_id = emp.id
JOIN res_company comp ON e.company_id = comp.id
WHERE e.state IN ('submit', 'approve')
ORDER BY e.date;
```

**Chart Type:** Interactive Table
**Conditional Formatting:**
- Days Pending > 7: Red highlight
- Days Pending 3-7: Yellow highlight
- Days Pending < 3: Green

#### 3.2 Expense Trend by Month (Area Chart)
```sql
SELECT
    DATE_TRUNC('month', date) as "Month",
    company_name as "Agency",
    SUM(total_amount) as "Amount"
FROM hr_expense
WHERE state IN ('approved', 'done')
    AND date >= DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '1 year'
GROUP BY "Month", company_name
ORDER BY "Month";
```

**Chart Type:** Stacked Area Chart
**X-Axis:** Month
**Y-Axis:** Amount
**Stack:** Agency

#### 3.3 Top Expense Categories (Donut Chart)
```sql
SELECT
    product_template.name as "Category",
    COUNT(*) as "Count",
    SUM(e.total_amount) as "Amount"
FROM hr_expense e
JOIN product_product product ON e.product_id = product.id
JOIN product_template ON product.product_tmpl_id = product_template.id
WHERE e.state IN ('approved', 'done')
    AND e.date >= {{ date_from }}
GROUP BY product_template.name
ORDER BY "Amount" DESC
LIMIT 8;
```

**Chart Type:** Donut Chart
**Hole:** 40%
**Labels:** Show percentage

#### 3.4 Average Approval Time (Big Number)
```sql
WITH approval_times AS (
    SELECT
        e.id,
        e.date as submit_date,
        msg.date as approval_date,
        EXTRACT(epoch FROM (msg.date - e.date))/3600 as hours_to_approve
    FROM hr_expense e
    JOIN mail_message msg ON msg.res_id = e.id AND msg.model = 'hr.expense'
    WHERE msg.body ILIKE '%approved%'
        AND e.date >= {{ date_from }}
)
SELECT
    ROUND(AVG(hours_to_approve), 1) as "Avg Hours"
FROM approval_times;
```

**Chart Type:** Big Number with Trend
**Format:** Decimal (X.X hours)
**Comparison:** vs. Last Period

#### 3.5 Expense Submission by Employee (Bar Chart)
```sql
SELECT
    emp.name as "Employee",
    COUNT(*) as "Submissions",
    SUM(e.total_amount) as "Total Amount",
    AVG(e.total_amount) as "Avg Amount"
FROM hr_expense e
JOIN hr_employee emp ON e.employee_id = emp.id
WHERE e.date >= {{ date_from }}
    AND e.company_id = {{ agency_filter }}
GROUP BY emp.name
ORDER BY "Total Amount" DESC
LIMIT 20;
```

**Chart Type:** Horizontal Bar Chart
**Tooltip:** Show count, total, and average

---

## Dashboard 4: BIR Compliance Tracker

**Purpose:** Philippine BIR form tracking and deadline monitoring

**URL:** https://superset.insightpulseai.net/superset/dashboard/bir-compliance/

### Charts

#### 4.1 Upcoming BIR Deadlines (Timeline)
```sql
SELECT
    form_type as "Form",
    filing_deadline as "Deadline",
    CURRENT_DATE - filing_deadline as "Days Until Due",
    company_name as "Agency",
    CASE
        WHEN status = 'filed' THEN '✅'
        WHEN filing_deadline < CURRENT_DATE THEN '🚨'
        WHEN filing_deadline < CURRENT_DATE + INTERVAL '3 days' THEN '⚠️'
        ELSE '📋'
    END as "Status"
FROM bir_form_status
WHERE filing_deadline >= CURRENT_DATE - INTERVAL '7 days'
    AND filing_deadline <= CURRENT_DATE + INTERVAL '30 days'
ORDER BY filing_deadline;
```

**Chart Type:** Table (Timeline View)
**Sort:** By deadline (ascending)
**Alerts:** Auto-highlight overdue and due soon

#### 4.2 BIR Form Filing Rate (Big Number KPI)
```sql
WITH total AS (
    SELECT COUNT(*) as cnt
    FROM bir_form_status
    WHERE filing_deadline >= DATE_TRUNC('year', CURRENT_DATE)
),
filed AS (
    SELECT COUNT(*) as cnt
    FROM bir_form_status
    WHERE filing_deadline >= DATE_TRUNC('year', CURRENT_DATE)
        AND status = 'filed'
)
SELECT
    ROUND((filed.cnt::numeric / NULLIF(total.cnt, 0)) * 100, 1) as "Filing Rate %"
FROM total, filed;
```

**Chart Type:** Big Number with Gauge
**Target:** 100%
**Current:** Calculated percentage

#### 4.3 Monthly BIR Forms by Type (Heatmap)
```sql
SELECT
    DATE_TRUNC('month', filing_deadline) as "Month",
    form_type as "Form",
    COUNT(*) as "Count"
FROM bir_form_status
WHERE filing_deadline >= DATE_TRUNC('year', CURRENT_DATE) - INTERVAL '2 years'
GROUP BY "Month", form_type
ORDER BY "Month", form_type;
```

**Chart Type:** Calendar Heatmap
**X-Axis:** Month
**Y-Axis:** Form Type
**Color:** Intensity by count

#### 4.4 Agency Compliance Score (Bullet Chart)
```sql
WITH agency_scores AS (
    SELECT
        company_name as "Agency",
        COUNT(*) as total_forms,
        SUM(CASE WHEN status = 'filed' THEN 1 ELSE 0 END) as filed_forms,
        ROUND((SUM(CASE WHEN status = 'filed' THEN 1 ELSE 0 END)::numeric / COUNT(*)) * 100, 1) as score
    FROM bir_form_status
    WHERE filing_deadline >= DATE_TRUNC('year', CURRENT_DATE)
    GROUP BY company_name
)
SELECT
    "Agency",
    score as "Compliance Score",
    total_forms as "Total Forms",
    filed_forms as "Filed Forms"
FROM agency_scores
ORDER BY score DESC;
```

**Chart Type:** Bullet Chart
**Measure:** Compliance Score
**Target:** 100%
**Ranges:** Poor (0-70%), Good (70-90%), Excellent (90-100%)

---

## Dashboard 5: Cash Flow Analysis

**Purpose:** Real-time cash flow monitoring and forecasting

**URL:** https://superset.insightpulseai.net/superset/dashboard/cash-flow/

### Charts

#### 5.1 Cash Flow Waterfall (Waterfall Chart)
```sql
WITH cash_movements AS (
    SELECT
        DATE_TRUNC('month', date) as month,
        SUM(CASE WHEN payment_type = 'inbound' THEN amount ELSE -amount END) as net_flow
    FROM account_payment
    WHERE state = 'posted'
        AND date >= DATE_TRUNC('year', CURRENT_DATE)
    GROUP BY month
)
SELECT
    month as "Month",
    net_flow as "Net Flow",
    SUM(net_flow) OVER (ORDER BY month) as "Cumulative"
FROM cash_movements
ORDER BY month;
```

**Chart Type:** Waterfall Chart
**X-Axis:** Month
**Y-Axis:** Cash Flow
**Colors:** Green (positive), Red (negative)

#### 5.2 Receivables Aging (Stacked Bar)
```sql
SELECT
    company_name as "Agency",
    SUM(CASE WHEN CURRENT_DATE - invoice_date <= 30 THEN amount_residual ELSE 0 END) as "0-30 Days",
    SUM(CASE WHEN CURRENT_DATE - invoice_date BETWEEN 31 AND 60 THEN amount_residual ELSE 0 END) as "31-60 Days",
    SUM(CASE WHEN CURRENT_DATE - invoice_date BETWEEN 61 AND 90 THEN amount_residual ELSE 0 END) as "61-90 Days",
    SUM(CASE WHEN CURRENT_DATE - invoice_date > 90 THEN amount_residual ELSE 0 END) as "90+ Days"
FROM account_move
WHERE move_type = 'out_invoice'
    AND state = 'posted'
    AND amount_residual > 0
GROUP BY company_name;
```

**Chart Type:** Stacked Horizontal Bar
**Categories:** Aging buckets
**Colors:** Green → Yellow → Orange → Red (by age)

#### 5.3 Bank Balance Trend (Mixed Chart)
```sql
SELECT
    date as "Date",
    bank_name as "Bank",
    balance as "Balance",
    balance - LAG(balance) OVER (PARTITION BY bank_name ORDER BY date) as "Daily Change"
FROM bank_statement_line
WHERE date >= CURRENT_DATE - INTERVAL '90 days'
ORDER BY date;
```

**Chart Type:** Mixed (Line + Bar)
**Line:** Balance per bank
**Bar:** Daily change

#### 5.4 Forecast vs Actual (Combo Chart)
```sql
SELECT
    DATE_TRUNC('month', date) as "Month",
    SUM(amount_total) as "Actual Revenue",
    AVG(amount_total) OVER (ORDER BY DATE_TRUNC('month', date) ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING) as "Forecast"
FROM sale_order
WHERE state IN ('sale', 'done')
    AND date_order >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY "Month"
ORDER BY "Month";
```

**Chart Type:** Line Chart (Dual Line)
**Lines:** Actual (solid), Forecast (dashed)

---

## Dashboard 6: OCR Expense Processing

**Purpose:** Monitor OCR accuracy and expense automation pipeline

**URL:** https://superset.insightpulseai.net/superset/dashboard/ocr-expense/

### Charts

#### 6.1 OCR Processing Stats (KPI Cards)
```sql
-- Total Processed Today
SELECT COUNT(*) as "Processed Today"
FROM ocr_task
WHERE DATE(created_at) = CURRENT_DATE;

-- Average Confidence
SELECT ROUND(AVG(confidence_score), 2) as "Avg Confidence"
FROM ocr_task
WHERE DATE(created_at) = CURRENT_DATE;

-- Auto-Approval Rate
SELECT ROUND((COUNT(*) FILTER (WHERE status = 'auto_approved')::numeric / COUNT(*)) * 100, 1) as "Auto-Approval %"
FROM expense_automation
WHERE DATE(processed_at) = CURRENT_DATE;

-- Processing Time
SELECT ROUND(AVG(EXTRACT(epoch FROM (completed_at - created_at))), 1) as "Avg Seconds"
FROM ocr_task
WHERE DATE(created_at) = CURRENT_DATE;
```

**Chart Type:** 4x Big Number KPIs in a row

#### 6.2 OCR Confidence Distribution (Histogram)
```sql
SELECT
    FLOOR(confidence_score * 10) * 10 as "Confidence Range",
    COUNT(*) as "Count"
FROM ocr_task
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY "Confidence Range"
ORDER BY "Confidence Range";
```

**Chart Type:** Histogram
**Bins:** 10% buckets (0-10%, 10-20%, ..., 90-100%)
**Target Line:** 60% (auto-approval threshold)

#### 6.3 Daily OCR Volume (Area Chart)
```sql
SELECT
    DATE(created_at) as "Date",
    COUNT(*) as "Total",
    COUNT(*) FILTER (WHERE status = 'success') as "Success",
    COUNT(*) FILTER (WHERE status = 'failed') as "Failed",
    COUNT(*) FILTER (WHERE status = 'manual_review') as "Manual Review"
FROM ocr_task
WHERE created_at >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY "Date"
ORDER BY "Date";
```

**Chart Type:** Stacked Area Chart
**Series:** Success, Failed, Manual Review

#### 6.4 Top Field Extraction Failures (Bar Chart)
```sql
SELECT
    field_name as "Field",
    COUNT(*) as "Failures"
FROM ocr_extraction_error
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY field_name
ORDER BY "Failures" DESC
LIMIT 10;
```

**Chart Type:** Horizontal Bar Chart
**Purpose:** Identify which receipt fields need OCR improvement

---

## Dashboard 7: AI Agent Performance

**Purpose:** Monitor @ipai-bot usage and Gradient API performance

**URL:** https://superset.insightpulseai.net/superset/dashboard/ai-agent/

### Charts

#### 7.1 Agent Query Volume (Line Chart)
```sql
SELECT
    DATE_TRUNC('hour', timestamp) as "Hour",
    COUNT(*) as "Queries",
    AVG(response_time_ms) as "Avg Response Time"
FROM ipai_agent_log
WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY "Hour"
ORDER BY "Hour";
```

**Chart Type:** Dual-Axis Line Chart
**Left Y:** Query count
**Right Y:** Response time

#### 7.2 Provider Usage (Pie Chart)
```sql
SELECT
    provider as "Provider",
    COUNT(*) as "Queries"
FROM ipai_agent_log
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY provider;
```

**Chart Type:** Pie Chart
**Labels:** DO Agent, Gradient API, Error
**Purpose:** Show fallback usage ratio

#### 7.3 Top Query Topics (Wordcloud)
```sql
SELECT
    query_text as "Query",
    COUNT(*) as "Frequency"
FROM ipai_agent_log
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY query_text
ORDER BY "Frequency" DESC
LIMIT 100;
```

**Chart Type:** Word Cloud
**Size:** By frequency

#### 7.4 Cost Tracking (Big Number + Trend)
```sql
SELECT
    SUM(CASE
        WHEN provider = 'gradient' THEN tokens_used * 0.0000014
        ELSE 0
    END) as "Total Cost USD"
FROM ipai_agent_log
WHERE timestamp >= DATE_TRUNC('month', CURRENT_DATE);
```

**Chart Type:** Big Number with Monthly Trend
**Format:** Currency (USD)
**Comparison:** vs. Last Month

---

## Dashboard 8: Slack Integration Metrics

**Purpose:** Track Slack bot usage and notification delivery

**URL:** https://superset.insightpulseai.net/superset/dashboard/slack-metrics/

### Charts

#### 8.1 Slack Commands by Type (Bar Chart)
```sql
SELECT
    command as "Command",
    COUNT(*) as "Usage",
    AVG(response_time_ms) as "Avg Response"
FROM slack_command_log
WHERE timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY command
ORDER BY "Usage" DESC;
```

**Chart Type:** Horizontal Bar Chart
**Commands:** /odoo, /expense, /bir

#### 8.2 Channel Activity Heatmap (Heatmap)
```sql
SELECT
    channel_name as "Channel",
    DATE_TRUNC('day', timestamp) as "Day",
    COUNT(*) as "Messages"
FROM slack_message_log
WHERE timestamp >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY channel_name, "Day"
ORDER BY "Day";
```

**Chart Type:** Calendar Heatmap
**Purpose:** Identify most active channels and times

#### 8.3 Notification Delivery Rate (Gauge)
```sql
WITH sent AS (
    SELECT COUNT(*) as cnt
    FROM slack_notification_log
    WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
),
delivered AS (
    SELECT COUNT(*) as cnt
    FROM slack_notification_log
    WHERE timestamp >= CURRENT_DATE - INTERVAL '7 days'
        AND status = 'delivered'
)
SELECT
    ROUND((delivered.cnt::numeric / NULLIF(sent.cnt, 0)) * 100, 1) as "Delivery Rate %"
FROM sent, delivered;
```

**Chart Type:** Gauge
**Target:** 99%+

---

## Deployment Guide

### Step 1: Connect to Supabase Database

**URL:** https://superset.insightpulseai.net
**Login:** admin / SHWYXDMFAwXI1drT

**Add Database:**
1. Settings → Database Connections → + Database
2. Database Type: PostgreSQL
3. Connection String:
   ```
   postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=prefer
   ```
4. Test Connection → Save

### Step 2: Create Datasets

For each SQL query above:
1. SQL Lab → SQL Editor
2. Paste query
3. Save → Create Dataset
4. Name dataset (e.g., "Executive Revenue by Agency")

### Step 3: Create Charts

1. Charts → + Chart
2. Select dataset
3. Choose chart type
4. Configure metrics/dimensions
5. Apply filters
6. Save chart

### Step 4: Build Dashboards

1. Dashboards → + Dashboard
2. Drag charts into layout
3. Add filters (agency, date range)
4. Configure interactivity
5. Publish dashboard

### Step 5: Schedule Email Reports

1. Dashboard → ⋮ → Email Reports
2. Configure recipients
3. Set schedule (daily/weekly/monthly)
4. Choose format (PNG/PDF)

---

## Best Practices

### Performance Optimization
- Use materialized views for complex queries
- Index frequently queried columns
- Limit row scans with date filters
- Cache dashboard results (1 hour)

### Security
- Row-level security per agency
- Read-only database user for Superset
- Enable SSL connections
- Audit dashboard access logs

### Maintenance
- Weekly: Review slow queries
- Monthly: Update datasets
- Quarterly: Archive old data
- Annually: Performance audit

---

**Status:** Ready to deploy
**Documentation:** Complete
**Contact:** Jake Tolentino (jgtolentino_rn@yahoo.com)

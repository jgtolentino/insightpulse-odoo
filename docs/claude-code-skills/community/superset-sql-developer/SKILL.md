---
name: superset-sql-developer
description: Expert guidance for writing optimized SQL queries for Apache Superset datasets, virtual datasets, and SQL Lab. This skill helps you create performant queries, design efficient datasets, and leverage PostgreSQL features - with specific patterns for Finance SSC, BIR compliance, and Odoo integration.
license: MIT
---

# Superset SQL Developer Skill

## Purpose
Expert guidance for writing optimized SQL queries for Apache Superset datasets, virtual datasets, and SQL Lab. This skill helps you create performant queries, design efficient datasets, and leverage PostgreSQL features - with specific patterns for Finance SSC, BIR compliance, and Odoo integration.

## When to Use This Skill
- Creating new Superset datasets
- Writing SQL for charts and dashboards
- Optimizing slow queries
- Designing virtual datasets
- Building metrics and calculated columns
- Querying Odoo database via Supabase
- Implementing row-level security

## SQL Development Workflow

### 1. Develop in SQL Lab
```
SQL Lab → Test Query → Verify Results → Save as Dataset
```

**SQL Lab Best Practices:**
- Start with `LIMIT 10` to test quickly
- Use `EXPLAIN ANALYZE` to check performance
- Save query history for reuse
- Add comments to document logic

### 2. Create Dataset
```
Datasets → + Dataset → SQL Query or Table
```

**Dataset Types:**
- **Physical Table:** Direct table reference (fastest)
- **Virtual Dataset:** SQL query (flexible)
- **Jinja Template:** Dynamic SQL (advanced)

### 3. Define Metrics
```
Dataset → Edit → Metrics Tab → + Add Metric
```

**Metric Examples:**
```sql
-- Sum of amounts
SUM(amount)

-- Count distinct
COUNT(DISTINCT agency_id)

-- Percentage
SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)

-- Average with filter
AVG(CASE WHEN processing_time_seconds > 0 THEN processing_time_seconds END)
```

---

## Query Optimization Fundamentals

### Performance Targets
```yaml
Fast Query:    < 1 second
Good Query:    1-5 seconds
Acceptable:    5-10 seconds
Needs Work:    10-30 seconds
Too Slow:      > 30 seconds (optimize or async)
```

### Query Optimization Checklist

**1. Use WHERE Clauses Wisely**
```sql
-- ✅ GOOD: Filter on indexed columns
SELECT * FROM bir_filing_tracker
WHERE agency_id = 5
  AND filing_date >= '2025-10-01'

-- ❌ BAD: No filters, scans entire table
SELECT * FROM bir_filing_tracker

-- ❌ BAD: Function on column prevents index use
SELECT * FROM bir_filing_tracker
WHERE EXTRACT(YEAR FROM filing_date) = 2025

-- ✅ GOOD: Filter allows index use
SELECT * FROM bir_filing_tracker
WHERE filing_date >= '2025-01-01'
  AND filing_date < '2026-01-01'
```

**2. Optimize Aggregations**
```sql
-- ✅ GOOD: Group by indexed columns
SELECT 
  agency_id,
  COUNT(*) as filing_count
FROM bir_filing_tracker
WHERE filing_date >= '2025-01-01'
GROUP BY agency_id

-- ❌ BAD: Group by non-indexed computed value
SELECT 
  TO_CHAR(filing_date, 'Month YYYY'),
  COUNT(*)
FROM bir_filing_tracker
GROUP BY TO_CHAR(filing_date, 'Month YYYY')

-- ✅ BETTER: Group by date-truncated column (can be indexed)
SELECT 
  DATE_TRUNC('month', filing_date) as month,
  COUNT(*)
FROM bir_filing_tracker
GROUP BY DATE_TRUNC('month', filing_date)
```

**3. Join Efficiently**
```sql
-- ✅ GOOD: Join on indexed foreign keys
SELECT 
  t.task_name,
  a.agency_name,
  COUNT(*) as count
FROM month_end_closing_tasks t
INNER JOIN agencies a ON t.agency_id = a.agency_id
WHERE t.closing_period = '2025-10'
GROUP BY t.task_name, a.agency_name

-- ❌ BAD: Cartesian product (missing join condition)
SELECT t.task_name, a.agency_name
FROM month_end_closing_tasks t, agencies a

-- ⚠️ CAUTION: LEFT JOIN might be slower
-- Only use if you need NULL results
SELECT t.*, a.agency_name
FROM month_end_closing_tasks t
LEFT JOIN agencies a ON t.agency_id = a.agency_id
```

**4. Limit Result Sets**
```sql
-- ✅ GOOD: Use LIMIT for large results
SELECT * FROM document_processing_logs
WHERE processed_at >= CURRENT_DATE
ORDER BY processed_at DESC
LIMIT 1000

-- ✅ GOOD: Use TOP N with window functions
SELECT * FROM (
  SELECT 
    *,
    ROW_NUMBER() OVER (PARTITION BY agency_id ORDER BY filing_date DESC) as rn
  FROM bir_filing_tracker
) sub
WHERE rn <= 10  -- Top 10 per agency

-- ❌ BAD: No limit, returns millions of rows
SELECT * FROM document_processing_logs
```

**5. Use Appropriate Data Types**
```sql
-- ✅ GOOD: Specific data types
SELECT 
  amount::NUMERIC(10,2),          -- For money
  filing_date::DATE,               -- For dates
  agency_id::INTEGER               -- For IDs

-- ❌ BAD: Casting everything as text
SELECT 
  amount::TEXT,
  filing_date::TEXT,
  agency_id::TEXT
```

---

## PostgreSQL Optimization Features

### 1. Indexes
```sql
-- Check if index exists
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'bir_filing_tracker';

-- Suggest indexes based on common queries
-- Index on frequently filtered columns
CREATE INDEX idx_bir_filing_agency_date 
ON bir_filing_tracker(agency_id, filing_date);

-- Index for status queries
CREATE INDEX idx_bir_filing_status 
ON bir_filing_tracker(filing_status)
WHERE filing_status IN ('Pending', 'Overdue');  -- Partial index

-- Composite index for joins
CREATE INDEX idx_closing_tasks_lookup
ON month_end_closing_tasks(agency_id, closing_period, task_status);
```

### 2. Materialized Views
```sql
-- Create materialized view for expensive aggregations
CREATE MATERIALIZED VIEW mv_bir_filing_summary AS
SELECT 
  agency_id,
  filing_period,
  form_type,
  COUNT(*) as total_filings,
  SUM(CASE WHEN filing_status = 'Completed' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN filing_status = 'Overdue' THEN 1 ELSE 0 END) as overdue,
  MAX(filing_date) as last_filing_date
FROM bir_filing_tracker
GROUP BY agency_id, filing_period, form_type;

-- Create indexes on materialized view
CREATE INDEX idx_mv_bir_agency ON mv_bir_filing_summary(agency_id);
CREATE INDEX idx_mv_bir_period ON mv_bir_filing_summary(filing_period);

-- Refresh strategy
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_bir_filing_summary;
-- Schedule: Every 15 minutes or on-demand
```

### 3. Window Functions
```sql
-- Running totals
SELECT 
  filing_date,
  COUNT(*) as daily_count,
  SUM(COUNT(*)) OVER (ORDER BY filing_date) as cumulative_count
FROM bir_filing_tracker
WHERE filing_period = '2025-Q4'
GROUP BY filing_date
ORDER BY filing_date;

-- Ranking
SELECT 
  agency_name,
  completion_rate,
  RANK() OVER (ORDER BY completion_rate DESC) as ranking
FROM agency_performance;

-- Previous period comparison
SELECT 
  month,
  revenue,
  LAG(revenue, 1) OVER (ORDER BY month) as prev_month_revenue,
  revenue - LAG(revenue, 1) OVER (ORDER BY month) as month_over_month_change
FROM monthly_revenue;
```

### 4. Common Table Expressions (CTEs)
```sql
-- Break complex queries into readable steps
WITH completed_tasks AS (
  SELECT 
    agency_id,
    closing_period,
    COUNT(*) as completed_count
  FROM month_end_closing_tasks
  WHERE task_status = 'Done'
  GROUP BY agency_id, closing_period
),
total_tasks AS (
  SELECT 
    agency_id,
    closing_period,
    COUNT(*) as total_count
  FROM month_end_closing_tasks
  GROUP BY agency_id, closing_period
)
SELECT 
  a.agency_name,
  c.closing_period,
  c.completed_count,
  t.total_count,
  (c.completed_count::FLOAT / t.total_count::FLOAT * 100) as completion_percentage
FROM completed_tasks c
JOIN total_tasks t ON c.agency_id = t.agency_id AND c.closing_period = t.closing_period
JOIN agencies a ON c.agency_id = a.agency_id
ORDER BY completion_percentage DESC;
```

---

## Finance SSC SQL Patterns

### Pattern 1: BIR Filing Status Query
```sql
-- Virtual Dataset: BIR Filing Status Dashboard
SELECT 
  bft.filing_id,
  bft.filing_period,
  bft.form_type,
  bft.filing_date,
  bft.due_date,
  bft.filing_status,
  bft.filing_amount,
  a.agency_id,
  a.agency_code,
  a.agency_name,
  u.full_name as assignee_name,
  -- Calculated Fields
  CASE 
    WHEN bft.filing_status = 'Completed' THEN 'Completed'
    WHEN bft.filing_status = 'Pending' AND bft.due_date >= CURRENT_DATE THEN 'Pending'
    WHEN bft.filing_status = 'Pending' AND bft.due_date < CURRENT_DATE THEN 'Overdue'
    ELSE bft.filing_status
  END as display_status,
  -- Days variance
  CASE 
    WHEN bft.filing_date IS NOT NULL 
    THEN DATE_PART('day', bft.filing_date - bft.due_date)
    ELSE DATE_PART('day', CURRENT_DATE - bft.due_date)
  END as days_variance,
  -- Quarter helper
  'Q' || DATE_PART('quarter', bft.filing_date) || ' ' || DATE_PART('year', bft.filing_date) as filing_quarter
FROM bir_filing_tracker bft
JOIN agencies a ON bft.agency_id = a.agency_id
LEFT JOIN users u ON bft.assignee_id = u.user_id
WHERE bft.filing_date >= '2024-01-01'  -- Last 2 years
ORDER BY bft.filing_date DESC;
```

**Metrics to Define:**
```yaml
Total Filings: COUNT(*)
Completed: SUM(CASE WHEN filing_status = 'Completed' THEN 1 ELSE 0 END)
Overdue: SUM(CASE WHEN display_status = 'Overdue' THEN 1 ELSE 0 END)
Completion Rate: SUM(CASE WHEN filing_status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
Total Amount Filed: SUM(filing_amount)
```

### Pattern 2: Month-End Closing Progress
```sql
-- Virtual Dataset: Month-End Closing Tracker
SELECT 
  mect.task_id,
  mect.closing_period,
  mect.task_category,
  mect.task_name,
  mect.task_description,
  mect.due_date,
  mect.completion_date,
  mect.task_status,
  mect.priority_level,
  a.agency_id,
  a.agency_code,
  a.agency_name,
  u.full_name as assignee_name,
  -- Calculated Fields
  EXTRACT(EPOCH FROM (mect.completion_date - mect.due_date)) / 86400 as days_variance,
  CASE 
    WHEN mect.task_status = 'Done' THEN 'Completed'
    WHEN mect.task_status IN ('In Progress', 'Started') THEN 'In Progress'
    WHEN mect.due_date < CURRENT_DATE THEN 'Overdue'
    WHEN mect.due_date <= CURRENT_DATE + INTERVAL '3 days' THEN 'Due Soon'
    ELSE 'On Track'
  END as task_health,
  -- Aging
  CASE 
    WHEN mect.task_status != 'Done' 
    THEN DATE_PART('day', CURRENT_DATE - mect.due_date)
    ELSE NULL
  END as days_overdue
FROM month_end_closing_tasks mect
JOIN agencies a ON mect.agency_id = a.agency_id
LEFT JOIN users u ON mect.assignee_id = u.user_id
WHERE mect.closing_period >= TO_CHAR(CURRENT_DATE - INTERVAL '6 months', 'YYYY-MM')
ORDER BY mect.due_date;
```

**Metrics to Define:**
```yaml
Total Tasks: COUNT(*)
Tasks Completed: SUM(CASE WHEN task_status = 'Done' THEN 1 ELSE 0 END)
Tasks Overdue: SUM(CASE WHEN task_health = 'Overdue' THEN 1 ELSE 0 END)
Completion Percentage: SUM(CASE WHEN task_status = 'Done' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
Avg Days to Complete: AVG(days_variance) FILTER (WHERE task_status = 'Done')
```

### Pattern 3: InsightPulse AI Processing Metrics
```sql
-- Virtual Dataset: Document Processing Analytics
SELECT 
  dpl.log_id,
  dpl.document_id,
  dpl.document_type,
  dpl.processing_status,
  dpl.processed_at,
  dpl.processing_time_seconds,
  dpl.ocr_confidence_score,
  dpl.page_count,
  dpl.file_size_bytes,
  dpl.error_message,
  -- Calculated Fields
  DATE_TRUNC('hour', dpl.processed_at) as processing_hour,
  DATE_TRUNC('day', dpl.processed_at) as processing_date,
  CASE 
    WHEN dpl.processing_status = 'Completed' AND dpl.ocr_confidence_score >= 0.95 THEN 'High Quality'
    WHEN dpl.processing_status = 'Completed' AND dpl.ocr_confidence_score >= 0.85 THEN 'Good Quality'
    WHEN dpl.processing_status = 'Completed' THEN 'Review Needed'
    WHEN dpl.processing_status = 'Failed' THEN 'Failed'
    ELSE 'Processing'
  END as quality_status,
  -- Speed category
  CASE 
    WHEN dpl.processing_time_seconds <= 2 THEN 'Fast'
    WHEN dpl.processing_time_seconds <= 5 THEN 'Normal'
    ELSE 'Slow'
  END as processing_speed_category,
  -- File size category
  CASE 
    WHEN dpl.file_size_bytes < 1000000 THEN 'Small (<1MB)'
    WHEN dpl.file_size_bytes < 5000000 THEN 'Medium (1-5MB)'
    ELSE 'Large (>5MB)'
  END as file_size_category
FROM document_processing_logs dpl
WHERE dpl.processed_at >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY dpl.processed_at DESC;
```

**Metrics to Define:**
```yaml
Documents Processed: COUNT(*)
Success Rate: SUM(CASE WHEN processing_status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
Avg Processing Time: AVG(processing_time_seconds)
Avg OCR Confidence: AVG(ocr_confidence_score) FILTER (WHERE ocr_confidence_score > 0)
Error Rate: SUM(CASE WHEN processing_status = 'Failed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*)
```

---

## Time-Series Query Patterns

### Daily/Weekly/Monthly Aggregation
```sql
-- Pattern: Flexible time grain aggregation
SELECT 
  DATE_TRUNC('day', filing_date) as period,      -- Change to 'week', 'month', 'quarter'
  agency_id,
  COUNT(*) as filing_count,
  SUM(filing_amount) as total_amount
FROM bir_filing_tracker
WHERE filing_date >= '2025-01-01'
GROUP BY DATE_TRUNC('day', filing_date), agency_id
ORDER BY period, agency_id;
```

### Period-over-Period Comparison
```sql
-- Compare current period to previous
WITH current_period AS (
  SELECT 
    agency_id,
    COUNT(*) as current_filings,
    SUM(filing_amount) as current_amount
  FROM bir_filing_tracker
  WHERE filing_period = '2025-Q4'
  GROUP BY agency_id
),
previous_period AS (
  SELECT 
    agency_id,
    COUNT(*) as previous_filings,
    SUM(filing_amount) as previous_amount
  FROM bir_filing_tracker
  WHERE filing_period = '2025-Q3'
  GROUP BY agency_id
)
SELECT 
  a.agency_name,
  c.current_filings,
  p.previous_filings,
  c.current_filings - p.previous_filings as filing_change,
  ROUND(((c.current_filings::FLOAT - p.previous_filings::FLOAT) / 
         p.previous_filings::FLOAT * 100), 2) as percent_change,
  c.current_amount,
  p.previous_amount,
  c.current_amount - p.previous_amount as amount_change
FROM current_period c
LEFT JOIN previous_period p ON c.agency_id = p.agency_id
JOIN agencies a ON c.agency_id = a.agency_id
ORDER BY percent_change DESC;
```

### Moving Average
```sql
-- 7-day moving average of processing volume
SELECT 
  processing_date,
  daily_count,
  AVG(daily_count) OVER (
    ORDER BY processing_date 
    ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
  ) as seven_day_avg
FROM (
  SELECT 
    DATE_TRUNC('day', processed_at) as processing_date,
    COUNT(*) as daily_count
  FROM document_processing_logs
  WHERE processed_at >= CURRENT_DATE - INTERVAL '60 days'
  GROUP BY DATE_TRUNC('day', processed_at)
) daily_counts
ORDER BY processing_date;
```

### Year-over-Year Comparison
```sql
SELECT 
  DATE_PART('month', filing_date) as month,
  DATE_PART('year', filing_date) as year,
  COUNT(*) as filing_count
FROM bir_filing_tracker
WHERE filing_date >= CURRENT_DATE - INTERVAL '2 years'
GROUP BY DATE_PART('month', filing_date), DATE_PART('year', filing_date)
ORDER BY year, month;
```

---

## Odoo Database Queries

### Querying Odoo Tables
```sql
-- Invoice data from Odoo account_move
SELECT 
  am.id as move_id,
  am.name as invoice_number,
  am.date as invoice_date,
  am.invoice_date,
  am.amount_total,
  am.amount_tax,
  am.state as invoice_state,
  am.move_type,
  rp.id as partner_id,
  rp.name as partner_name,
  rp.vat as partner_tin,
  rc.name as company_name
FROM account_move am
JOIN res_partner rp ON am.partner_id = rp.id
JOIN res_company rc ON am.company_id = rc.id
WHERE am.move_type IN ('out_invoice', 'out_refund')  -- Customer invoices
  AND am.state = 'posted'
  AND am.invoice_date >= '2025-01-01'
ORDER BY am.invoice_date DESC;
```

### Odoo Accounting Reports
```sql
-- General Ledger Summary
SELECT 
  aa.code as account_code,
  aa.name as account_name,
  SUM(aml.debit) as total_debit,
  SUM(aml.credit) as total_credit,
  SUM(aml.debit - aml.credit) as balance
FROM account_move_line aml
JOIN account_account aa ON aml.account_id = aa.id
JOIN account_move am ON aml.move_id = am.id
WHERE am.state = 'posted'
  AND am.date >= '2025-01-01'
  AND am.date <= '2025-12-31'
GROUP BY aa.code, aa.name
ORDER BY aa.code;
```

### Odoo Inventory Queries
```sql
-- Stock Movement Summary
SELECT 
  pt.name as product_name,
  pt.default_code as product_code,
  sm.date as movement_date,
  spt.code as operation_type,
  sl_source.complete_name as source_location,
  sl_dest.complete_name as dest_location,
  sm.product_uom_qty as quantity,
  sm.state
FROM stock_move sm
JOIN product_product pp ON sm.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
JOIN stock_picking_type spt ON sm.picking_type_id = spt.id
JOIN stock_location sl_source ON sm.location_id = sl_source.id
JOIN stock_location sl_dest ON sm.location_dest_id = sl_dest.id
WHERE sm.date >= '2025-10-01'
  AND sm.state = 'done'
ORDER BY sm.date DESC;
```

---

## Calculated Metrics & Columns

### Superset Metric SQL
```sql
-- In Superset: Dataset → Edit → Metrics Tab

-- Metric Name: Completion Rate
-- SQL Expression:
SUM(CASE WHEN filing_status = 'Completed' THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)

-- Metric Name: Avg Days to Complete
-- SQL Expression:
AVG(EXTRACT(EPOCH FROM (completion_date - due_date)) / 86400)

-- Metric Name: On-Time Completion Rate
-- SQL Expression:
SUM(CASE WHEN completion_date <= due_date THEN 1 ELSE 0 END) * 100.0 / 
  NULLIF(SUM(CASE WHEN completion_date IS NOT NULL THEN 1 ELSE 0 END), 0)

-- Metric Name: Overdue Amount
-- SQL Expression:
SUM(CASE WHEN filing_status = 'Overdue' THEN filing_amount ELSE 0 END)
```

### Calculated Columns
```sql
-- In Dataset SQL (better performance than calculated metrics)

-- Status with color indicator
CASE 
  WHEN filing_status = 'Completed' THEN '🟢 Completed'
  WHEN filing_status = 'Overdue' THEN '🔴 Overdue'
  WHEN filing_status = 'Pending' THEN '🟡 Pending'
  ELSE filing_status
END as status_display

-- Aging bucket
CASE 
  WHEN task_status = 'Done' THEN 'Completed'
  WHEN days_overdue <= 0 THEN 'On Time'
  WHEN days_overdue <= 5 THEN '1-5 Days'
  WHEN days_overdue <= 10 THEN '6-10 Days'
  ELSE '10+ Days'
END as aging_bucket

-- Performance rating
CASE 
  WHEN completion_percentage >= 95 THEN 'Excellent'
  WHEN completion_percentage >= 85 THEN 'Good'
  WHEN completion_percentage >= 70 THEN 'Needs Improvement'
  ELSE 'Poor'
END as performance_rating
```

---

## Row-Level Security

### Implementing RLS in Superset
```sql
-- Create SQL dataset with user-based filtering

-- Pattern 1: Agency-level access
SELECT *
FROM bir_filing_tracker
WHERE agency_id IN (
  SELECT agency_id
  FROM user_agency_access
  WHERE user_email = '{{ current_user_email() }}'
)

-- Pattern 2: Role-based access
SELECT *
FROM month_end_closing_tasks
WHERE 
  CASE 
    WHEN '{{ current_user_role() }}' = 'Admin' THEN TRUE
    WHEN '{{ current_user_role() }}' = 'Agency_Lead' THEN 
      agency_id = (SELECT agency_id FROM users WHERE email = '{{ current_user_email() }}')
    WHEN '{{ current_user_role() }}' = 'Viewer' THEN 
      task_status = 'Done'  -- Only completed tasks
    ELSE FALSE
  END
```

### Using Jinja Templates for Dynamic Filtering
```sql
-- Dataset with dynamic date range based on user preference
SELECT *
FROM document_processing_logs
WHERE processed_at >= CURRENT_DATE - INTERVAL '{{ user_date_range_days|default(30) }} days'
  {% if current_user_department() != 'Admin' %}
    AND department_id = '{{ current_user_department() }}'
  {% endif %}
ORDER BY processed_at DESC
```

---

## Query Performance Monitoring

### Check Query Execution Plan
```sql
-- Use EXPLAIN ANALYZE to see actual performance
EXPLAIN (ANALYZE, BUFFERS, TIMING) 
SELECT 
  agency_name,
  COUNT(*) as filing_count
FROM bir_filing_tracker bft
JOIN agencies a ON bft.agency_id = a.agency_id
WHERE filing_date >= '2025-01-01'
GROUP BY agency_name;
```

**Key Metrics to Watch:**
- **Execution Time:** < 1s ideal, < 10s acceptable
- **Planning Time:** Should be < 10ms
- **Buffers:** High shared/temp buffers → need more memory
- **Seq Scan:** Large table sequential scans → add indexes

### Common Performance Issues

**Issue 1: Sequential Scan on Large Table**
```
Seq Scan on bir_filing_tracker (cost=0.00..1500.00 rows=50000)
  Filter: (filing_date >= '2025-01-01'::date)
```
**Solution:** Add index on `filing_date`

**Issue 2: Nested Loop Join**
```
Nested Loop (cost=0.00..5000.00)
  -> Seq Scan on agencies
  -> Index Scan on bir_filing_tracker
```
**Solution:** Ensure join columns are indexed

**Issue 3: Large Sort Operation**
```
Sort (cost=3000.00..3500.00)
  Sort Key: filing_date DESC
  Sort Method: external merge Disk: 50000kB
```
**Solution:** Add index on sort column or limit result set

---

## Dataset Design Best Practices

### Physical Table vs Virtual Dataset

**Use Physical Table When:**
- Query is simple (SELECT * FROM table)
- Performance is critical
- Data doesn't need transformation
- Table is already optimized

**Use Virtual Dataset When:**
- Need to join multiple tables
- Require calculated fields
- Need complex aggregations
- Want to hide sensitive columns
- Implementing row-level security

### Dataset Naming Convention
```
Format: {domain}_{entity}_{purpose}

Examples:
  bir_filing_status_dashboard
  month_end_closing_tracker
  insightpulse_processing_metrics
  odoo_invoice_analysis
  agency_performance_summary
```

### Column Naming
```yaml
Be Descriptive:
  ❌ dt, amt, sts
  ✅ filing_date, filing_amount, filing_status

Use Consistent Suffixes:
  - _date: Date fields
  - _amount: Money fields
  - _count: Count aggregations
  - _rate: Percentage values
  - _id: Primary/foreign keys
  - _name: Display names
```

---

## Testing & Validation

### Data Quality Checks
```sql
-- Check for NULL values in critical fields
SELECT 
  COUNT(*) as total_rows,
  COUNT(agency_id) as non_null_agency,
  COUNT(filing_date) as non_null_date,
  COUNT(*) - COUNT(agency_id) as null_agency_count
FROM bir_filing_tracker;

-- Check for duplicates
SELECT 
  agency_id,
  filing_period,
  form_type,
  COUNT(*) as duplicate_count
FROM bir_filing_tracker
GROUP BY agency_id, filing_period, form_type
HAVING COUNT(*) > 1;

-- Validate date ranges
SELECT 
  MIN(filing_date) as earliest_date,
  MAX(filing_date) as latest_date,
  COUNT(CASE WHEN filing_date > CURRENT_DATE THEN 1 END) as future_dates
FROM bir_filing_tracker;
```

### Query Result Validation
```sql
-- Compare aggregation results
SELECT 
  'Direct Count' as method,
  COUNT(*) as result
FROM bir_filing_tracker
WHERE filing_status = 'Completed'

UNION ALL

SELECT 
  'SUM(CASE WHEN)' as method,
  SUM(CASE WHEN filing_status = 'Completed' THEN 1 ELSE 0 END) as result
FROM bir_filing_tracker;
```

---

## Quick Reference: Common SQL Patterns

### Pivot Table in SQL
```sql
SELECT 
  agency_name,
  SUM(CASE WHEN form_type = '1601-C' THEN 1 ELSE 0 END) as form_1601c,
  SUM(CASE WHEN form_type = '2550Q' THEN 1 ELSE 0 END) as form_2550q,
  SUM(CASE WHEN form_type = '1702-RT' THEN 1 ELSE 0 END) as form_1702rt
FROM bir_filing_tracker bft
JOIN agencies a ON bft.agency_id = a.agency_id
GROUP BY agency_name;
```

### Running Total
```sql
SELECT 
  filing_date,
  filing_count,
  SUM(filing_count) OVER (ORDER BY filing_date) as cumulative_total
FROM daily_filing_counts
ORDER BY filing_date;
```

### Rank & Dense Rank
```sql
SELECT 
  agency_name,
  completion_rate,
  RANK() OVER (ORDER BY completion_rate DESC) as rank,
  DENSE_RANK() OVER (ORDER BY completion_rate DESC) as dense_rank
FROM agency_performance;
```

### First/Last Value
```sql
SELECT DISTINCT
  agency_id,
  FIRST_VALUE(filing_date) OVER (
    PARTITION BY agency_id 
    ORDER BY filing_date
  ) as first_filing,
  LAST_VALUE(filing_date) OVER (
    PARTITION BY agency_id 
    ORDER BY filing_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  ) as last_filing
FROM bir_filing_tracker;
```

---

## Integration with Your Stack

### Supabase PostgreSQL Context
```yaml
Database: PostgreSQL 15+
Connection: Direct connection to Supabase
Extensions: pgvector (for InsightPulse), pg_stat_statements
Features: Row-level security, realtime subscriptions

Performance:
  - Connection pooling enabled
  - Read replicas available
  - Automated backups
```

### Odoo Integration
```sql
-- Odoo tables synced to Supabase
-- Query Supabase instead of Odoo directly for better performance

-- Common Odoo-Superset pattern
WITH odoo_invoices AS (
  SELECT * FROM account_move  -- Supabase copy of Odoo table
  WHERE state = 'posted'
)
SELECT 
  invoice_date,
  SUM(amount_total) as total_revenue
FROM odoo_invoices
GROUP BY invoice_date
ORDER BY invoice_date;
```

---

## Next Steps

After creating your SQL dataset:
1. **Test in SQL Lab** - Verify results and performance
2. **Save as Dataset** - Create reusable dataset
3. **Define Metrics** - Add calculated metrics
4. **Build Charts** - Use `superset-chart-builder` skill
5. **Create Dashboard** - Use `superset-dashboard-designer` skill

**Related Skills:**
- `superset-chart-builder` - Visualize your data
- `superset-dashboard-designer` - Build dashboards
- `odoo19-oca-devops` - Odoo data integration

---

## Support

For PostgreSQL/Superset SQL:
```bash
# Check database version
SELECT version();

# View slow queries
SELECT * FROM pg_stat_statements 
ORDER BY total_exec_time DESC 
LIMIT 10;

# Check table sizes
SELECT 
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Your Context:**
- Supabase PostgreSQL (spdtwktxdalcfigzeqrz)
- Odoo 18/19 tables synced to Supabase
- Finance SSC multi-agency data
- BIR compliance tracking
- InsightPulse AI document processing
- Employee codes: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

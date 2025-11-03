---
name: superset-chart-builder
description: Expert guidance for selecting, configuring, and optimizing Apache Superset charts. This skill helps you choose the right visualization, configure it properly, and avoid common mistakes - with specific examples for Finance SSC, BIR compliance, and business intelligence use cases.
license: MIT
---

# Superset Chart Builder Skill

## Purpose
Expert guidance for selecting, configuring, and optimizing Apache Superset charts. This skill helps you choose the right visualization, configure it properly, and avoid common mistakes - with specific examples for Finance SSC, BIR compliance, and business intelligence use cases.

## When to Use This Skill
- Selecting the right chart type for your data story
- Configuring chart properties and customizations
- Optimizing chart performance and interactivity
- Building dashboards for Finance Shared Service Centers
- Creating BIR compliance visualizations
- Designing analytics for InsightPulse AI or business operations

## Chart Selection Decision Tree

### Start Here: What's Your Primary Goal?

**1. COMPARE VALUES ACROSS CATEGORIES**
- Few categories (2-7): **Bar Chart** (horizontal or vertical)
- Many categories (8+): **Table** or **Horizontal Bar Chart**
- Need to show change over time: **Line Chart** or **Area Chart**
- Need to show parts of whole: **Stacked Bar Chart**

**2. SHOW TRENDS OVER TIME**
- Continuous time series: **Line Chart**
- Multiple metrics: **Multi-Line Chart** or **Mixed Chart**
- Show volume + trend: **Area Chart**
- Compare periods: **Bar Chart** with time grouping
- Cumulative values: **Stacked Area Chart**

**3. DISPLAY SINGLE KEY METRIC (KPI)**
- Just the number: **Big Number**
- Number + trend: **Big Number with Trendline**
- Progress to goal: **Gauge Chart**
- Multiple related KPIs: **Big Number** cards in grid layout

**4. SHOW COMPOSITION/PARTS OF WHOLE**
- 2-5 categories: **Pie Chart** or **Donut Chart**
- 6+ categories: **Bar Chart** (easier to read)
- Hierarchical data: **Treemap** or **Sunburst**
- Over time: **Stacked Area Chart** or **100% Stacked Bar**

**5. COMPARE MANY ITEMS WITH DETAIL**
- Tabular data with sorting: **Table**
- Cross-tabulation: **Pivot Table**
- Heatmap of values: **Heatmap**

**6. SHOW RELATIONSHIPS/DISTRIBUTION**
- Correlation between two metrics: **Scatter Plot**
- Distribution: **Histogram** or **Box Plot**
- Network/flow: **Sankey Diagram**

**7. GEOGRAPHIC DATA**
- Points on map: **Deck.gl Scatterplot**
- Regions/choropleth: **Country Map** or **Deck.gl Polygon**

## Chart Type Configuration Guide

### Bar Charts
**Best For:** Comparing values across categories, rankings, showing magnitude differences

**Configuration Essentials:**
```yaml
Chart Type: Bar Chart / Horizontal Bar Chart

Key Settings:
  Metrics: [sum(amount), avg(value)]
  Dimensions: [agency_name, month, category]
  Orientation: Horizontal (for long labels) | Vertical (for time series)
  
Formatting:
  Show Legend: Yes (for multiple metrics)
  Show Values: Yes (for exact numbers)
  Sort Bars: Descending (for rankings)
  Color Scheme: Use categorical colors
  
Performance:
  Row Limit: 50 (default) | 100 (for comprehensive views)
  Server Pagination: Enable for 1000+ rows
```

**Finance SSC Example:**
```sql
-- BIR Filing Status by Agency
SELECT 
  agency_code,
  agency_name,
  COUNT(CASE WHEN filing_status = 'Completed' THEN 1 END) as completed_filings,
  COUNT(CASE WHEN filing_status = 'Pending' THEN 1 END) as pending_filings,
  COUNT(CASE WHEN filing_status = 'Overdue' THEN 1 END) as overdue_filings
FROM bir_filing_tracker
WHERE filing_period = '2025-Q4'
GROUP BY agency_code, agency_name
ORDER BY overdue_filings DESC
```

Chart: Horizontal Bar Chart, Stacked, showing status breakdown per agency

**Common Mistakes:**
- ❌ Too many bars (20+) - hard to read
- ❌ Using pie chart instead for 5+ categories
- ❌ Not sorting bars meaningfully
- ✅ Use color to highlight key insights (red for overdue)

---

### Line Charts
**Best For:** Time series trends, continuous data, showing patterns over time

**Configuration Essentials:**
```yaml
Chart Type: Line Chart / Time-series Line Chart

Key Settings:
  Metrics: [sum(revenue), avg(processing_time)]
  Time Column: filing_date, closing_date, processed_at
  Time Grain: Day | Week | Month | Quarter
  
Formatting:
  Line Style: Solid (for primary) | Dashed (for comparison)
  Markers: Show on hover only
  Y-Axis: Start at zero (for volume) | Auto (for percentages)
  Rolling Window: 7-day moving average (for smoothing)
  
Annotations:
  Reference Lines: Budget targets, deadlines
  Event Markers: BIR filing due dates, month-end close
```

**Finance SSC Example:**
```sql
-- Monthly Closing Task Completion Trend
SELECT 
  DATE_TRUNC('day', completed_at) as date,
  COUNT(*) as tasks_completed,
  AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/3600) as avg_hours_to_complete
FROM month_end_closing_tasks
WHERE completed_at >= '2025-01-01'
  AND task_status = 'Done'
GROUP BY DATE_TRUNC('day', completed_at)
ORDER BY date
```

Chart: Line Chart with 2 Y-axes (count left, hours right), annotations for month-end dates

**Common Mistakes:**
- ❌ Not using time-series chart type (loses time features)
- ❌ Too many lines (5+) - confusing
- ❌ Jagged lines without smoothing for daily data
- ✅ Use area chart to emphasize volume

---

### Big Number (KPI Cards)
**Best For:** Executive dashboards, highlighting key metrics, status at-a-glance

**Configuration Essentials:**
```yaml
Chart Type: Big Number / Big Number with Trendline

Key Settings:
  Metric: COUNT(*), SUM(amount), MAX(date)
  Subheader: Comparison text or time period
  
Formatting:
  Number Format: 
    - ",.0f" for whole numbers (1,234)
    - ",.2f" for decimals (1,234.56)
    - ".1%" for percentages (45.2%)
    - "₱,.0f" for Philippine Peso
  Font Size: Large (for primary KPIs)
  
Comparison:
  Show Trend: Yes (with comparison period)
  Comparison Type: Values | Percentage | Change
  Time Comparison: Previous period, year-over-year
  
Conditional Formatting:
  Color Rules: Green (good) | Yellow (warning) | Red (critical)
```

**Finance SSC Example:**
```sql
-- Overdue BIR Filings (Critical KPI)
SELECT COUNT(*) as overdue_count
FROM bir_filing_tracker
WHERE filing_status = 'Overdue'
  AND due_date < CURRENT_DATE
```

Big Number Config:
- Metric: `overdue_count`
- Subheader: "BIR Filings Past Due"
- Number Format: "0"
- Color: Red if > 0, Green if = 0

**InsightPulse AI Example:**
```sql
-- Daily Document Processing Volume
SELECT 
  COUNT(*) as documents_processed,
  AVG(ocr_confidence_score) as avg_confidence
FROM document_processing_logs
WHERE processed_at >= CURRENT_DATE
  AND processing_status = 'Completed'
```

Two Big Number cards side-by-side with trendlines (7-day comparison)

---

### Tables & Pivot Tables
**Best For:** Detailed data exploration, drilldown views, multi-dimensional analysis

**Configuration Essentials:**
```yaml
Chart Type: Table / Pivot Table

Key Settings:
  Columns: Dimensions and metrics to display
  Row Limit: 50-500 depending on use case
  
Formatting:
  Column Formatting:
    - Align Right: Numbers and dates
    - Align Left: Text and categories
  Conditional Formatting: Highlight cells based on rules
  
Features:
  Sorting: Enable column header sorting
  Filtering: Enable search box
  Pagination: Server-side for large datasets
  
Pivot Table Specific:
  Rows: Primary grouping (Agency, Month)
  Columns: Secondary dimension (Filing Status)
  Aggregation: SUM, AVG, COUNT
```

**Finance SSC Example:**
```sql
-- Month-End Closing Task Status Matrix
SELECT 
  agency_name,
  task_category,
  task_name,
  assignee_name,
  due_date,
  completion_date,
  CASE 
    WHEN completion_date IS NULL AND due_date < CURRENT_DATE THEN 'Overdue'
    WHEN completion_date IS NULL THEN 'In Progress'
    ELSE 'Completed'
  END as status,
  CASE 
    WHEN completion_date IS NOT NULL 
    THEN EXTRACT(EPOCH FROM (completion_date - due_date))/86400 
  END as days_variance
FROM month_end_closing_tasks
WHERE closing_period = '2025-10'
ORDER BY agency_name, task_category, due_date
```

Table Config:
- Conditional formatting: Red for overdue, green for early completion
- Sortable columns
- Search box enabled

---

### Pie & Donut Charts
**Best For:** Showing composition of a whole, 2-5 categories maximum

**Configuration Essentials:**
```yaml
Chart Type: Pie Chart / Donut Chart

Key Settings:
  Dimension: Category column (status, type)
  Metric: SUM, COUNT, or percentage
  
Formatting:
  Show Labels: Yes (with percentages)
  Show Legend: Yes (for more than 3 categories)
  Donut Radius: 50-70% (for donut charts)
  Color Scheme: Categorical or custom
  
Best Practices:
  Max Categories: 5 (use bar chart for 6+)
  Sort: By size (largest first)
```

**Finance SSC Example:**
```sql
-- BIR Form Types Distribution
SELECT 
  form_type,
  COUNT(*) as filing_count
FROM bir_filing_tracker
WHERE filing_period = '2025-Q4'
GROUP BY form_type
```

Donut Chart:
- Center Text: Total filings count
- Labels: Form type with percentage
- Colors: Distinctive categorical palette

**When NOT to Use:**
- ❌ More than 5 categories
- ❌ Values are similar (hard to distinguish)
- ❌ Comparing multiple pie charts side-by-side
- ✅ Use bar chart instead for better comparison

---

### Gauge Charts
**Best For:** Progress toward goal, performance metrics, completion percentages

**Configuration Essentials:**
```yaml
Chart Type: Gauge Chart

Key Settings:
  Metric: Percentage or completion value
  Min Value: 0 or baseline
  Max Value: 100 or target
  
Formatting:
  Color Ranges:
    - 0-33%: Red (critical)
    - 34-66%: Yellow (warning)
    - 67-100%: Green (good)
  Show Needle: Yes
  Show Values: Current and target
```

**Finance SSC Example:**
```sql
-- Month-End Closing Progress
SELECT 
  (COUNT(CASE WHEN task_status = 'Done' THEN 1 END)::FLOAT / 
   COUNT(*)::FLOAT * 100) as completion_percentage
FROM month_end_closing_tasks
WHERE closing_period = '2025-10'
```

Gauge: 0-100%, color thresholds at 33% and 67%

---

## Advanced Chart Types

### Heatmap
**Best For:** Correlation matrices, time-based patterns, intensity visualization

**Finance SSC Example:**
```sql
-- Task Completion by Agency and Day
SELECT 
  agency_code,
  TO_CHAR(completed_at, 'Day') as day_of_week,
  COUNT(*) as task_count
FROM month_end_closing_tasks
WHERE completed_at IS NOT NULL
GROUP BY agency_code, TO_CHAR(completed_at, 'Day')
```

---

### Treemap
**Best For:** Hierarchical data, proportional comparison, space-efficient visualization

**InsightPulse AI Example:**
```sql
-- Document Processing Volume by Type and Status
SELECT 
  document_type,
  processing_status,
  COUNT(*) as document_count
FROM document_processing_logs
GROUP BY document_type, processing_status
```

---

## Performance Optimization

### Query Performance
1. **Use indexed columns** in WHERE clauses and GROUP BY
2. **Aggregate at database level** rather than post-processing
3. **Limit row counts** appropriately (50-500 for tables, 10-20 for charts)
4. **Use materialized views** for complex calculations
5. **Cache query results** for frequently accessed dashboards

### Chart Rendering Performance
1. **Reduce data points** for line charts (use time grain: day → week → month)
2. **Paginate tables** server-side for large datasets
3. **Async queries** for slow-running reports
4. **Progressive loading** for multi-chart dashboards

### Your Database Context
For Odoo 18/19 + Supabase PostgreSQL:
```sql
-- Use Odoo's optimized views
FROM account_move_line_view  -- Pre-joined accounting data
FROM stock_move_stats         -- Aggregated inventory data

-- Leverage PostgreSQL features
WITH RECURSIVE           -- Hierarchical queries
WINDOW FUNCTIONS         -- Running totals, rankings
MATERIALIZED VIEW        -- Pre-computed aggregations
```

---

## Common Patterns for Finance SSC

### BIR Compliance Dashboard Charts

**1. Filing Status Overview (Big Number Cards)**
- Total filings this period
- Completed count (green)
- Pending count (yellow)
- Overdue count (red)

**2. ATP Expiration Timeline (Line Chart)**
```sql
SELECT 
  agency_name,
  atp_expiry_date,
  CASE 
    WHEN atp_expiry_date < CURRENT_DATE THEN 'Expired'
    WHEN atp_expiry_date < CURRENT_DATE + INTERVAL '30 days' THEN 'Expiring Soon'
    ELSE 'Valid'
  END as status
FROM bir_atp_registry
WHERE atp_status = 'Active'
```

**3. Form Submission by Agency (Stacked Bar)**
- X-axis: Agency names
- Y-axis: Filing count
- Stack: Form types (1601-C, 2550Q, 1702-RT)

**4. Compliance Rate Trend (Line + Area)**
```sql
SELECT 
  DATE_TRUNC('month', filing_date) as month,
  (COUNT(CASE WHEN filing_status = 'Completed' THEN 1 END)::FLOAT / 
   COUNT(*)::FLOAT * 100) as compliance_rate
FROM bir_filing_tracker
GROUP BY DATE_TRUNC('month', filing_date)
ORDER BY month
```

### Month-End Closing Dashboard Charts

**1. Progress Gauge**
- Overall completion percentage
- Color thresholds: <70% red, 70-90% yellow, >90% green

**2. Task Status Breakdown (Donut)**
- Done
- In Progress  
- Blocked
- Not Started

**3. Tasks by Agency (Horizontal Bar)**
- Sorted by completion rate
- Stacked by status

**4. Timeline View (Gantt Alternative)**
```sql
SELECT 
  task_name,
  due_date,
  completion_date,
  assignee_name,
  EXTRACT(EPOCH FROM (completion_date - due_date))/86400 as days_variance
FROM month_end_closing_tasks
WHERE closing_period = CURRENT_PERIOD
ORDER BY due_date
```

Use Table with conditional formatting for variance

---

## Chart Configuration Checklist

Before finalizing any chart:

**Data Quality:**
- [ ] No NULL values breaking visualizations
- [ ] Date formats consistent
- [ ] Number formats appropriate (decimals, currency)
- [ ] Categories are complete (no missing groups)

**Visual Design:**
- [ ] Chart type matches data story
- [ ] Colors are meaningful (not just default)
- [ ] Labels are clear and readable
- [ ] Legend is necessary and placed well
- [ ] Axes have appropriate scales

**Performance:**
- [ ] Query executes in < 30 seconds
- [ ] Row limit is appropriate
- [ ] Caching is enabled
- [ ] No unnecessary calculations

**Accessibility:**
- [ ] Color-blind friendly palette
- [ ] Text is legible (font size 12+)
- [ ] Tooltip provides full context
- [ ] Alternative text/description for screen readers

**Interactivity:**
- [ ] Filters apply correctly
- [ ] Cross-filtering configured (if needed)
- [ ] Drill-down enabled (if multi-level data)
- [ ] Export options available

---

## Color Schemes for Finance SSC

### Status Colors (Universal)
- **Green (#52C41A):** Completed, On-time, Good
- **Yellow (#FAAD14):** In Progress, Warning, Pending
- **Red (#F5222D):** Overdue, Critical, Failed
- **Blue (#1890FF):** Informational, Neutral
- **Gray (#8C8C8C):** Not Started, Inactive

### BIR Form Types
- **1601-C** (Monthly Withholding): #1890FF (Blue)
- **2550Q** (Quarterly VAT): #52C41A (Green)
- **1702-RT/EX** (Annual ITR): #FA8C16 (Orange)
- **ATP Renewals:** #722ED1 (Purple)

### Agency Differentiation
Use distinct categorical colors:
```
RIM:  #1890FF
CKVC: #52C41A
BOM:  #FA8C16
JPAL: #722ED1
JLI:  #13C2C2
JAP:  #F5222D
LAS:  #FADB14
RMQB: #EB2F96
```

---

## Integration with Your Stack

### Odoo Database Queries
```sql
-- Connect to Odoo PostgreSQL through Supabase
SELECT 
  move.name as invoice_number,
  partner.name as partner_name,
  move.amount_total,
  move.state
FROM account_move move
JOIN res_partner partner ON move.partner_id = partner.id
WHERE move.move_type = 'out_invoice'
  AND move.state IN ('posted', 'paid')
```

### Supabase Realtime Data
```sql
-- Query Supabase tables directly
SELECT * FROM month_end_closing_tasks
WHERE assignee_id = current_user_id()
  AND task_status != 'Done'
ORDER BY due_date
```

### InsightPulse AI Metrics
```sql
-- Document processing analytics
SELECT 
  DATE_TRUNC('hour', processed_at) as hour,
  COUNT(*) as documents_processed,
  AVG(processing_time_seconds) as avg_processing_time,
  AVG(ocr_confidence_score) as avg_confidence,
  SUM(CASE WHEN processing_status = 'Failed' THEN 1 ELSE 0 END) as failed_count
FROM document_processing_logs
WHERE processed_at >= NOW() - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', processed_at)
ORDER BY hour DESC
```

---

## Quick Reference: Chart Selection

| Your Goal | Best Chart | Alternative |
|-----------|-----------|-------------|
| Show KPI | Big Number | Gauge |
| Compare categories | Bar Chart | Table |
| Show trend | Line Chart | Area Chart |
| Parts of whole | Donut Chart | Stacked Bar |
| Detailed data | Table | Pivot Table |
| Time series | Line Chart | Bar Chart (grouped) |
| Progress | Gauge | Big Number |
| Distribution | Histogram | Box Plot |
| Correlation | Scatter Plot | Heatmap |
| Geographic | Deck.gl Map | Country Map |

---

## Next Steps

After building your chart:
1. **Test with real data** - Ensure query performs well
2. **Add to dashboard** - Position with related charts
3. **Configure filters** - Enable user interactivity
4. **Set up alerts** - For critical metrics
5. **Document** - Add description for other users

**Related Skills:**
- `superset-dashboard-designer` - Layout and composition
- `superset-sql-developer` - Query optimization
- `odoo19-oca-devops` - Data source integration

---

## Support

For Superset-specific features, check:
```bash
# View available chart types
http://your-superset-url/chart/list/

# Check your Superset version
SELECT version FROM superset_version;
```

**Your Context:**
- Odoo 18/19 database
- Supabase PostgreSQL (spdtwktxdalcfigzeqrz)
- Finance SSC multi-agency environment
- BIR compliance requirements
- InsightPulse AI document processing

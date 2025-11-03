# BIR Compliance SQL Templates

## Template 1: Filing Status by Agency
```sql
-- Purpose: Show filing completion status for all agencies
-- Use in: Dashboard overview, agency comparison charts

SELECT 
  a.agency_code,
  a.agency_name,
  COUNT(*) as total_filings,
  SUM(CASE WHEN bft.filing_status = 'Completed' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN bft.filing_status = 'Pending' THEN 1 ELSE 0 END) as pending,
  SUM(CASE WHEN bft.filing_status = 'Overdue' THEN 1 ELSE 0 END) as overdue,
  ROUND(
    SUM(CASE WHEN bft.filing_status = 'Completed' THEN 1 ELSE 0 END)::NUMERIC / 
    COUNT(*)::NUMERIC * 100, 2
  ) as completion_rate
FROM bir_filing_tracker bft
JOIN agencies a ON bft.agency_id = a.agency_id
WHERE bft.filing_period = '2025-Q4'  -- ← Parameterize this
GROUP BY a.agency_code, a.agency_name
ORDER BY completion_rate DESC;
```

## Template 2: Overdue Filings Detail
```sql
-- Purpose: List all overdue filings with details
-- Use in: Action items table, alerts

SELECT 
  bft.filing_id,
  a.agency_name,
  bft.form_type,
  bft.filing_period,
  bft.due_date,
  DATE_PART('day', CURRENT_DATE - bft.due_date) as days_overdue,
  u.full_name as assignee,
  u.email as assignee_email,
  bft.filing_amount,
  bft.notes
FROM bir_filing_tracker bft
JOIN agencies a ON bft.agency_id = a.agency_id
LEFT JOIN users u ON bft.assignee_id = u.user_id
WHERE bft.filing_status != 'Completed'
  AND bft.due_date < CURRENT_DATE
ORDER BY days_overdue DESC, bft.filing_amount DESC;
```

## Template 3: ATP Expiration Tracking
```sql
-- Purpose: Track Authorization to Print certificate expirations
-- Use in: Compliance monitoring, renewal alerts

SELECT 
  atp.atp_id,
  a.agency_name,
  atp.receipt_type,
  atp.atp_number,
  atp.issue_date,
  atp.expiry_date,
  DATE_PART('day', atp.expiry_date - CURRENT_DATE) as days_until_expiry,
  CASE 
    WHEN atp.expiry_date < CURRENT_DATE THEN '🔴 Expired'
    WHEN atp.expiry_date <= CURRENT_DATE + INTERVAL '30 days' THEN '🟡 Expiring Soon'
    WHEN atp.expiry_date <= CURRENT_DATE + INTERVAL '90 days' THEN '🟠 Renewal Due'
    ELSE '🟢 Valid'
  END as status,
  atp.last_series_used,
  atp.series_limit
FROM bir_atp_registry atp
JOIN agencies a ON atp.agency_id = a.agency_id
WHERE atp.atp_status = 'Active'
ORDER BY days_until_expiry;
```

## Template 4: Form Type Distribution
```sql
-- Purpose: Breakdown of filing types across agencies
-- Use in: Donut/pie charts, stacked bar charts

SELECT 
  bft.form_type,
  COUNT(*) as filing_count,
  SUM(bft.filing_amount) as total_amount,
  ROUND(
    COUNT(*)::NUMERIC / 
    (SELECT COUNT(*) FROM bir_filing_tracker WHERE filing_period = '2025-Q4')::NUMERIC * 100, 
    2
  ) as percentage_of_total
FROM bir_filing_tracker bft
WHERE bft.filing_period = '2025-Q4'
GROUP BY bft.form_type
ORDER BY filing_count DESC;
```

## Template 5: Compliance Trend Over Time
```sql
-- Purpose: Monthly compliance rate trend
-- Use in: Line chart showing improvement/decline

SELECT 
  bft.filing_period,
  COUNT(*) as total_filings,
  SUM(CASE WHEN bft.filing_status = 'Completed' THEN 1 ELSE 0 END) as completed,
  ROUND(
    SUM(CASE WHEN bft.filing_status = 'Completed' THEN 1 ELSE 0 END)::NUMERIC / 
    COUNT(*)::NUMERIC * 100, 2
  ) as compliance_rate,
  SUM(bft.filing_amount) as total_amount
FROM bir_filing_tracker bft
WHERE bft.filing_date >= '2024-01-01'
GROUP BY bft.filing_period
ORDER BY bft.filing_period;
```

## Template 6: Agency Performance Scorecard
```sql
-- Purpose: Comprehensive agency performance metrics
-- Use in: Executive dashboard, agency comparison

WITH agency_stats AS (
  SELECT 
    a.agency_id,
    a.agency_name,
    COUNT(*) as total_filings,
    SUM(CASE WHEN bft.filing_status = 'Completed' THEN 1 ELSE 0 END) as completed,
    SUM(CASE WHEN bft.filing_status = 'Overdue' THEN 1 ELSE 0 END) as overdue,
    AVG(
      CASE 
        WHEN bft.filing_date IS NOT NULL 
        THEN DATE_PART('day', bft.filing_date - bft.due_date)
      END
    ) as avg_days_variance
  FROM bir_filing_tracker bft
  JOIN agencies a ON bft.agency_id = a.agency_id
  WHERE bft.filing_period = '2025-Q4'
  GROUP BY a.agency_id, a.agency_name
)
SELECT 
  agency_name,
  total_filings,
  completed,
  overdue,
  ROUND((completed::NUMERIC / total_filings::NUMERIC * 100), 2) as completion_rate,
  ROUND(avg_days_variance, 1) as avg_days_variance,
  CASE 
    WHEN (completed::NUMERIC / total_filings::NUMERIC) >= 0.95 THEN 'Excellent'
    WHEN (completed::NUMERIC / total_filings::NUMERIC) >= 0.85 THEN 'Good'
    WHEN (completed::NUMERIC / total_filings::NUMERIC) >= 0.70 THEN 'Needs Improvement'
    ELSE 'Poor'
  END as performance_rating,
  RANK() OVER (ORDER BY (completed::NUMERIC / total_filings::NUMERIC) DESC) as ranking
FROM agency_stats
ORDER BY completion_rate DESC;
```

## Template 7: Quarterly Summary Report
```sql
-- Purpose: Complete quarterly BIR filing summary
-- Use in: Executive report, quarterly review

SELECT 
  '2025-Q4' as quarter,
  COUNT(*) as total_filings,
  SUM(CASE WHEN filing_status = 'Completed' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN filing_status = 'Pending' THEN 1 ELSE 0 END) as pending,
  SUM(CASE WHEN filing_status = 'Overdue' THEN 1 ELSE 0 END) as overdue,
  SUM(filing_amount) as total_amount,
  COUNT(DISTINCT agency_id) as agencies_involved,
  COUNT(DISTINCT form_type) as form_types_filed,
  MIN(filing_date) as first_filing,
  MAX(filing_date) as last_filing,
  ROUND(AVG(
    CASE WHEN filing_date IS NOT NULL 
    THEN DATE_PART('day', filing_date - due_date)
    END
  ), 1) as avg_days_from_due_date
FROM bir_filing_tracker
WHERE filing_period = '2025-Q4';
```

## Template 8: Weekly Filing Activity
```sql
-- Purpose: Week-by-week filing activity for trend analysis
-- Use in: Line chart, weekly planning

SELECT 
  DATE_TRUNC('week', bft.filing_date) as week_start,
  COUNT(*) as filings_completed,
  COUNT(DISTINCT bft.agency_id) as agencies_active,
  SUM(bft.filing_amount) as total_amount,
  STRING_AGG(DISTINCT bft.form_type, ', ') as forms_filed
FROM bir_filing_tracker bft
WHERE bft.filing_date >= CURRENT_DATE - INTERVAL '12 weeks'
  AND bft.filing_status = 'Completed'
GROUP BY DATE_TRUNC('week', bft.filing_date)
ORDER BY week_start DESC;
```

## Template 9: Assignee Workload
```sql
-- Purpose: Track filing assignments and workload per person
-- Use in: Team management, workload balancing

SELECT 
  u.full_name as assignee,
  COUNT(*) as assigned_filings,
  SUM(CASE WHEN bft.filing_status = 'Completed' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN bft.filing_status = 'Pending' THEN 1 ELSE 0 END) as pending,
  SUM(CASE WHEN bft.filing_status = 'Overdue' THEN 1 ELSE 0 END) as overdue,
  ROUND(
    SUM(CASE WHEN bft.filing_status = 'Completed' THEN 1 ELSE 0 END)::NUMERIC / 
    COUNT(*)::NUMERIC * 100, 2
  ) as completion_rate,
  STRING_AGG(DISTINCT a.agency_code, ', ' ORDER BY a.agency_code) as agencies
FROM bir_filing_tracker bft
JOIN users u ON bft.assignee_id = u.user_id
LEFT JOIN agencies a ON bft.agency_id = a.agency_id
WHERE bft.filing_period = '2025-Q4'
GROUP BY u.user_id, u.full_name
ORDER BY assigned_filings DESC;
```

## Template 10: Penalty Risk Assessment
```sql
-- Purpose: Calculate potential penalties for late filings
-- Use in: Risk management, financial impact analysis

SELECT 
  a.agency_name,
  bft.form_type,
  bft.filing_amount,
  bft.due_date,
  DATE_PART('day', CURRENT_DATE - bft.due_date) as days_late,
  -- BIR penalty calculation (simplified - verify actual rates)
  CASE 
    WHEN DATE_PART('day', CURRENT_DATE - bft.due_date) <= 30 THEN bft.filing_amount * 0.25
    ELSE bft.filing_amount * 0.25 + (bft.filing_amount * 0.02 * FLOOR(DATE_PART('day', CURRENT_DATE - bft.due_date) / 30))
  END as estimated_penalty,
  bft.notes
FROM bir_filing_tracker bft
JOIN agencies a ON bft.agency_id = a.agency_id
WHERE bft.filing_status = 'Overdue'
  AND bft.filing_amount > 0
ORDER BY estimated_penalty DESC;
```

## Usage Notes

**Parameterization:**
Replace hard-coded values with Superset parameters:
- `'2025-Q4'` → `{{ filing_period }}` (filter)
- `CURRENT_DATE` → Keep as-is (dynamic)
- `a.agency_id = 5` → `{{ agency_filter }}` (filter)

**Performance Tips:**
1. Always include WHERE clause with indexed columns
2. Use DATE_TRUNC for time grouping
3. Limit results for large tables (LIMIT 1000)
4. Consider materialized views for expensive aggregations

**Customization:**
- Add your specific agency codes (RIM, CKVC, BOM, etc.)
- Adjust form types (1601-C, 2550Q, 1702-RT, etc.)
- Modify penalty calculations per BIR regulations
- Add company-specific fields as needed

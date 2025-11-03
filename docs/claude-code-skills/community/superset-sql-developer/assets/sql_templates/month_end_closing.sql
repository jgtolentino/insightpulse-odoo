# Month-End Closing SQL Templates

## Template 1: Overall Closing Progress
```sql
-- Purpose: High-level progress for current closing period
-- Use in: Big number cards, gauge charts

SELECT 
  '2025-10' as closing_period,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN task_status = 'Done' THEN 1 ELSE 0 END) as completed_tasks,
  SUM(CASE WHEN task_status IN ('In Progress', 'Started') THEN 1 ELSE 0 END) as in_progress,
  SUM(CASE WHEN task_status = 'Not Started' THEN 1 ELSE 0 END) as not_started,
  SUM(CASE WHEN due_date < CURRENT_DATE AND task_status != 'Done' THEN 1 ELSE 0 END) as overdue,
  ROUND(
    SUM(CASE WHEN task_status = 'Done' THEN 1 ELSE 0 END)::NUMERIC / 
    COUNT(*)::NUMERIC * 100, 2
  ) as completion_percentage,
  MIN(due_date) as earliest_due_date,
  MAX(due_date) as latest_due_date
FROM month_end_closing_tasks
WHERE closing_period = '2025-10';
```

## Template 2: Tasks by Agency
```sql
-- Purpose: Compare progress across agencies
-- Use in: Horizontal bar chart (stacked by status)

SELECT 
  a.agency_code,
  a.agency_name,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN mect.task_status = 'Done' THEN 1 ELSE 0 END) as done,
  SUM(CASE WHEN mect.task_status IN ('In Progress', 'Started') THEN 1 ELSE 0 END) as in_progress,
  SUM(CASE WHEN mect.task_status = 'Blocked' THEN 1 ELSE 0 END) as blocked,
  SUM(CASE WHEN mect.task_status = 'Not Started' THEN 1 ELSE 0 END) as not_started,
  ROUND(
    SUM(CASE WHEN mect.task_status = 'Done' THEN 1 ELSE 0 END)::NUMERIC / 
    COUNT(*)::NUMERIC * 100, 2
  ) as completion_rate
FROM month_end_closing_tasks mect
JOIN agencies a ON mect.agency_id = a.agency_id
WHERE mect.closing_period = '2025-10'
GROUP BY a.agency_code, a.agency_name
ORDER BY completion_rate DESC;
```

## Template 3: Task Detail with Variance
```sql
-- Purpose: Detailed task list with completion timing
-- Use in: Table with conditional formatting

SELECT 
  mect.task_id,
  a.agency_name,
  mect.task_category,
  mect.task_name,
  mect.due_date,
  mect.completion_date,
  mect.task_status,
  u.full_name as assignee,
  mect.priority_level,
  -- Calculate variance
  CASE 
    WHEN mect.completion_date IS NOT NULL 
    THEN DATE_PART('day', mect.completion_date - mect.due_date)
    WHEN mect.due_date < CURRENT_DATE AND mect.task_status != 'Done'
    THEN DATE_PART('day', CURRENT_DATE - mect.due_date)
    ELSE NULL
  END as days_variance,
  -- Status indicator
  CASE 
    WHEN mect.task_status = 'Done' AND mect.completion_date <= mect.due_date THEN '🟢 On Time'
    WHEN mect.task_status = 'Done' AND mect.completion_date > mect.due_date THEN '🟡 Late'
    WHEN mect.task_status = 'Blocked' THEN '🔴 Blocked'
    WHEN mect.due_date < CURRENT_DATE AND mect.task_status != 'Done' THEN '🔴 Overdue'
    WHEN mect.due_date <= CURRENT_DATE + INTERVAL '3 days' THEN '🟠 Due Soon'
    ELSE '🟢 On Track'
  END as health_status,
  mect.notes
FROM month_end_closing_tasks mect
JOIN agencies a ON mect.agency_id = a.agency_id
LEFT JOIN users u ON mect.assignee_id = u.user_id
WHERE mect.closing_period = '2025-10'
ORDER BY 
  CASE WHEN mect.task_status != 'Done' AND mect.due_date < CURRENT_DATE THEN 0 ELSE 1 END,
  mect.due_date,
  a.agency_name;
```

## Template 4: Daily Completion Trend
```sql
-- Purpose: Show task completion velocity
-- Use in: Area chart showing cumulative completion

SELECT 
  completion_date::DATE as date,
  COUNT(*) as tasks_completed_on_day,
  SUM(COUNT(*)) OVER (ORDER BY completion_date::DATE) as cumulative_completed
FROM month_end_closing_tasks
WHERE closing_period = '2025-10'
  AND task_status = 'Done'
  AND completion_date IS NOT NULL
GROUP BY completion_date::DATE
ORDER BY date;
```

## Template 5: Tasks by Category
```sql
-- Purpose: Breakdown by task category (AP, AR, GL, etc.)
-- Use in: Donut chart or stacked bar chart

SELECT 
  mect.task_category,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN mect.task_status = 'Done' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN mect.task_status != 'Done' THEN 1 ELSE 0 END) as remaining,
  ROUND(
    SUM(CASE WHEN mect.task_status = 'Done' THEN 1 ELSE 0 END)::NUMERIC / 
    COUNT(*)::NUMERIC * 100, 2
  ) as completion_rate
FROM month_end_closing_tasks mect
WHERE mect.closing_period = '2025-10'
GROUP BY mect.task_category
ORDER BY completion_rate ASC;  -- Show lowest completion first
```

## Template 6: Blocked Tasks Analysis
```sql
-- Purpose: Identify and analyze bottlenecks
-- Use in: Action items table, blocking analysis

SELECT 
  mect.task_id,
  a.agency_name,
  mect.task_name,
  mect.task_category,
  mect.due_date,
  DATE_PART('day', CURRENT_DATE - mect.blocked_date) as days_blocked,
  mect.blocking_reason,
  mect.blocked_by_task_id,
  bt.task_name as blocking_task_name,
  bt.task_status as blocking_task_status,
  u.full_name as assignee,
  mect.notes
FROM month_end_closing_tasks mect
JOIN agencies a ON mect.agency_id = a.agency_id
LEFT JOIN users u ON mect.assignee_id = u.user_id
LEFT JOIN month_end_closing_tasks bt ON mect.blocked_by_task_id = bt.task_id
WHERE mect.closing_period = '2025-10'
  AND mect.task_status = 'Blocked'
ORDER BY days_blocked DESC, mect.due_date;
```

## Template 7: Historical Performance
```sql
-- Purpose: Compare current closing to previous periods
-- Use in: Line chart showing trend over time

SELECT 
  mect.closing_period,
  COUNT(*) as total_tasks,
  SUM(CASE WHEN mect.task_status = 'Done' THEN 1 ELSE 0 END) as completed,
  ROUND(
    SUM(CASE WHEN mect.task_status = 'Done' THEN 1 ELSE 0 END)::NUMERIC / 
    COUNT(*)::NUMERIC * 100, 2
  ) as completion_rate,
  AVG(
    CASE WHEN mect.completion_date IS NOT NULL 
    THEN DATE_PART('day', mect.completion_date - mect.due_date)
    END
  ) as avg_days_variance,
  MIN(mect.completion_date) as first_task_completed,
  MAX(mect.completion_date) as last_task_completed
FROM month_end_closing_tasks mect
WHERE mect.closing_period >= TO_CHAR(CURRENT_DATE - INTERVAL '12 months', 'YYYY-MM')
GROUP BY mect.closing_period
ORDER BY mect.closing_period;
```

## Template 8: Assignee Workload
```sql
-- Purpose: Track individual workload and performance
-- Use in: Team management, resource allocation

SELECT 
  u.full_name as assignee,
  COUNT(*) as assigned_tasks,
  SUM(CASE WHEN mect.task_status = 'Done' THEN 1 ELSE 0 END) as completed,
  SUM(CASE WHEN mect.task_status IN ('In Progress', 'Started') THEN 1 ELSE 0 END) as in_progress,
  SUM(CASE WHEN mect.task_status = 'Blocked' THEN 1 ELSE 0 END) as blocked,
  SUM(CASE WHEN mect.due_date < CURRENT_DATE AND mect.task_status != 'Done' THEN 1 ELSE 0 END) as overdue,
  ROUND(
    AVG(
      CASE WHEN mect.completion_date IS NOT NULL 
      THEN DATE_PART('day', mect.completion_date - mect.due_date)
      END
    ), 1
  ) as avg_days_variance,
  STRING_AGG(DISTINCT a.agency_code, ', ' ORDER BY a.agency_code) as agencies
FROM month_end_closing_tasks mect
JOIN users u ON mect.assignee_id = u.user_id
LEFT JOIN agencies a ON mect.agency_id = a.agency_id
WHERE mect.closing_period = '2025-10'
GROUP BY u.user_id, u.full_name
ORDER BY overdue DESC, assigned_tasks DESC;
```

## Template 9: Critical Path Analysis
```sql
-- Purpose: Identify tasks on critical path
-- Use in: Priority planning, bottleneck identification

WITH task_dependencies AS (
  SELECT 
    mect.task_id,
    mect.task_name,
    mect.due_date,
    mect.task_status,
    COUNT(dep.task_id) as dependent_task_count,
    STRING_AGG(dep.task_name, ', ') as dependent_tasks
  FROM month_end_closing_tasks mect
  LEFT JOIN month_end_closing_tasks dep 
    ON mect.task_id = dep.blocked_by_task_id
    AND dep.closing_period = mect.closing_period
  WHERE mect.closing_period = '2025-10'
  GROUP BY mect.task_id, mect.task_name, mect.due_date, mect.task_status
)
SELECT 
  td.task_name,
  td.due_date,
  td.task_status,
  td.dependent_task_count,
  td.dependent_tasks,
  CASE 
    WHEN td.dependent_task_count > 0 AND td.task_status != 'Done' THEN '🔴 Critical'
    WHEN td.dependent_task_count > 0 THEN '🟡 Important'
    ELSE '🟢 Normal'
  END as criticality
FROM task_dependencies td
WHERE td.dependent_task_count > 0
ORDER BY td.dependent_task_count DESC, td.due_date;
```

## Template 10: Late Completion Analysis
```sql
-- Purpose: Analyze patterns in late task completion
-- Use in: Process improvement, root cause analysis

SELECT 
  a.agency_name,
  mect.task_category,
  COUNT(*) as total_late_tasks,
  AVG(DATE_PART('day', mect.completion_date - mect.due_date)) as avg_days_late,
  MIN(DATE_PART('day', mect.completion_date - mect.due_date)) as min_days_late,
  MAX(DATE_PART('day', mect.completion_date - mect.due_date)) as max_days_late,
  STRING_AGG(DISTINCT mect.task_name, '; ') as frequently_late_tasks
FROM month_end_closing_tasks mect
JOIN agencies a ON mect.agency_id = a.agency_id
WHERE mect.task_status = 'Done'
  AND mect.completion_date > mect.due_date
  AND mect.closing_period >= TO_CHAR(CURRENT_DATE - INTERVAL '6 months', 'YYYY-MM')
GROUP BY a.agency_name, mect.task_category
HAVING COUNT(*) >= 3  -- At least 3 late completions
ORDER BY avg_days_late DESC;
```

## Template 11: Task Completion Forecast
```sql
-- Purpose: Predict closing date based on current velocity
-- Use in: Planning, risk assessment

WITH completion_velocity AS (
  SELECT 
    DATE_PART('day', CURRENT_DATE - MIN(completion_date)) as days_elapsed,
    COUNT(*) as tasks_completed,
    COUNT(*) / NULLIF(DATE_PART('day', CURRENT_DATE - MIN(completion_date)), 0) as tasks_per_day
  FROM month_end_closing_tasks
  WHERE closing_period = '2025-10'
    AND task_status = 'Done'
    AND completion_date IS NOT NULL
),
remaining_tasks AS (
  SELECT COUNT(*) as tasks_remaining
  FROM month_end_closing_tasks
  WHERE closing_period = '2025-10'
    AND task_status != 'Done'
)
SELECT 
  cv.tasks_completed,
  cv.days_elapsed,
  ROUND(cv.tasks_per_day, 2) as avg_tasks_per_day,
  rt.tasks_remaining,
  CASE 
    WHEN cv.tasks_per_day > 0 
    THEN ROUND(rt.tasks_remaining / cv.tasks_per_day, 0)
    ELSE NULL
  END as estimated_days_to_complete,
  CASE 
    WHEN cv.tasks_per_day > 0 
    THEN CURRENT_DATE + (ROUND(rt.tasks_remaining / cv.tasks_per_day, 0) || ' days')::INTERVAL
    ELSE NULL
  END as forecast_completion_date
FROM completion_velocity cv
CROSS JOIN remaining_tasks rt;
```

## Template 12: Period-over-Period Comparison
```sql
-- Purpose: Compare current month performance to previous
-- Use in: Executive summary, trend analysis

WITH current_month AS (
  SELECT 
    COUNT(*) as total_tasks,
    SUM(CASE WHEN task_status = 'Done' THEN 1 ELSE 0 END) as completed,
    AVG(CASE WHEN completion_date IS NOT NULL 
        THEN DATE_PART('day', completion_date - due_date) END) as avg_variance
  FROM month_end_closing_tasks
  WHERE closing_period = '2025-10'
),
previous_month AS (
  SELECT 
    COUNT(*) as total_tasks,
    SUM(CASE WHEN task_status = 'Done' THEN 1 ELSE 0 END) as completed,
    AVG(CASE WHEN completion_date IS NOT NULL 
        THEN DATE_PART('day', completion_date - due_date) END) as avg_variance
  FROM month_end_closing_tasks
  WHERE closing_period = '2025-09'
)
SELECT 
  'Current Month (2025-10)' as period,
  cm.total_tasks,
  cm.completed,
  ROUND((cm.completed::NUMERIC / cm.total_tasks::NUMERIC * 100), 2) as completion_rate,
  ROUND(cm.avg_variance, 1) as avg_days_variance,
  -- Comparison
  cm.total_tasks - pm.total_tasks as task_count_change,
  ROUND((cm.completed::NUMERIC / cm.total_tasks::NUMERIC * 100) - 
        (pm.completed::NUMERIC / pm.total_tasks::NUMERIC * 100), 2) as completion_rate_change,
  ROUND(cm.avg_variance - pm.avg_variance, 1) as variance_improvement
FROM current_month cm
CROSS JOIN previous_month pm;
```

## Usage Notes

**Task Categories:**
Common month-end closing categories:
- Accounts Payable (AP)
- Accounts Receivable (AR)
- General Ledger (GL)
- Fixed Assets (FA)
- Inventory (INV)
- Payroll (PR)
- Bank Reconciliation (BR)

**Task Status Values:**
- Not Started
- Started / In Progress
- Blocked
- Done / Completed

**Priority Levels:**
- Critical / High
- Normal / Medium
- Low

**Parameterization:**
Replace with Superset filters:
- `'2025-10'` → `{{ closing_period }}`
- `a.agency_id = 5` → `{{ agency_filter }}`
- `u.user_id = 10` → `{{ assignee_filter }}`

**Performance Tips:**
1. Index on: closing_period, agency_id, task_status, due_date
2. Materialize view for historical performance queries
3. Cache results during active closing period
4. Use date filters to limit data range

-- Dataset: mv_expense_compliance
-- Description: Expense compliance metrics by fiscal period
-- Schema: analytics
-- Refresh: Hourly via materialized view

SELECT
    fiscal_period,
    company_key,
    company_name,
    total_expenses,
    compliant_expenses,
    non_compliant_expenses,
    compliance_rate,
    avg_approval_time,
    refused_expenses,
    pending_expenses
FROM analytics.mv_expense_compliance
WHERE fiscal_period >= TO_CHAR(CURRENT_DATE - INTERVAL '24 months', 'YYYY-MM')
ORDER BY fiscal_period DESC;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.mv_expense_compliance
-- Type: Materialized View
-- Columns:
--   - fiscal_period (VARCHAR): Fiscal period (YYYY-MM)
--   - company_key (INTEGER): Company foreign key
--   - company_name (VARCHAR): Company name
--   - total_expenses (INTEGER): Total number of expenses
--   - compliant_expenses (INTEGER): Number of compliant expenses
--   - non_compliant_expenses (INTEGER): Number of non-compliant expenses
--   - compliance_rate (DECIMAL): Compliance rate (0-1)
--   - avg_approval_time (DECIMAL): Average approval time in days
--   - refused_expenses (INTEGER): Number of refused expenses
--   - pending_expenses (INTEGER): Number of pending expenses

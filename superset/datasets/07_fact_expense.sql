-- Dataset: fact_expense
-- Description: Expense fact table with approval workflow and compliance metrics
-- Schema: analytics
-- Refresh: Real-time via CDC

SELECT
    expense_id,
    expense_key,
    expense_date,
    approval_date,
    employee_key,
    employee_name,
    department_name,
    company_key,
    state,
    amount,
    expense_category,
    payment_mode,
    days_to_approve,
    is_approved,
    is_refused,
    is_compliant,
    compliance_notes,
    created_at,
    updated_at
FROM analytics.fact_expense
WHERE expense_date >= CURRENT_DATE - INTERVAL '2 years'
ORDER BY expense_date DESC;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.fact_expense
-- Type: Fact Table
-- Columns:
--   - expense_id (INTEGER): Expense ID
--   - expense_key (INTEGER): Expense surrogate key
--   - expense_date (DATE): Expense date
--   - approval_date (TIMESTAMP): Approval timestamp
--   - employee_key (INTEGER): Employee foreign key
--   - employee_name (VARCHAR): Employee name
--   - department_name (VARCHAR): Department name
--   - company_key (INTEGER): Company foreign key
--   - state (VARCHAR): Expense state (draft, reported, approved, done, refused)
--   - amount (DECIMAL): Expense amount
--   - expense_category (VARCHAR): Expense category
--   - payment_mode (VARCHAR): Payment mode
--   - days_to_approve (INTEGER): Days from submission to approval
--   - is_approved (BOOLEAN): Approval flag
--   - is_refused (BOOLEAN): Refused flag
--   - is_compliant (BOOLEAN): Compliance flag
--   - compliance_notes (TEXT): Compliance notes
--   - created_at (TIMESTAMP): Record creation timestamp
--   - updated_at (TIMESTAMP): Record update timestamp

-- T&E Analytics Views for Superset Dashboards
-- Adapt table names to match your actual hr_expense, cash_advances, expense_approvals, receipts_ocr tables

-- Base expenses (one row per receipt/line)
CREATE OR REPLACE VIEW te_expenses_v AS
SELECT
  e.id AS expense_id,
  emp.name AS employee_name,
  e.employee_id,
  dep.name AS department,
  cat.name AS category,
  e.name AS description,
  e.currency_id,
  curr.name AS currency,
  e.unit_amount AS amount,
  e.tax_amount,
  e.total_amount,
  e.state AS status,                  -- draft, submitted, approved, done, refused
  CASE
    WHEN e.total_amount > 5000 THEN 'WARN'
    WHEN e.date < CURRENT_DATE - INTERVAL '90 days' THEN 'VIOLATION'
    ELSE 'OK'
  END AS policy_flag,
  e.date::date AS txn_date,
  DATE_TRUNC('month', e.date)::date AS month_date,
  e.sheet_id AS cash_advance_id,
  e.create_date AS created_at,
  e.write_date AS updated_at
FROM hr_expense e
LEFT JOIN hr_employee emp ON e.employee_id = emp.id
LEFT JOIN hr_department dep ON emp.department_id = dep.id
LEFT JOIN product_product pp ON e.product_id = pp.id
LEFT JOIN product_category cat ON pp.categ_id = cat.id
LEFT JOIN res_currency curr ON e.currency_id = curr.id;

-- Cash advance tracking (placeholder - adjust to your actual cash advance table)
CREATE OR REPLACE VIEW te_cash_advances_v AS
SELECT
  s.id AS advance_id,
  s.employee_id,
  emp.name AS employee_name,
  s.create_date::date AS issued_date,
  COALESCE(s.total_amount, 0) AS advance_amount,
  curr.name AS currency,
  COALESCE(s.total_amount - COALESCE(SUM(e.total_amount), 0), 0) AS current_balance,
  s.state AS advance_status
FROM hr_expense_sheet s
LEFT JOIN hr_employee emp ON s.employee_id = emp.id
LEFT JOIN res_currency curr ON s.currency_id = curr.id
LEFT JOIN hr_expense e ON e.sheet_id = s.id AND e.state IN ('approved', 'done')
WHERE s.state IN ('submit', 'approve', 'post', 'done')
GROUP BY s.id, s.employee_id, emp.name, s.create_date, s.total_amount, curr.name, s.state;

-- Approval queue timeline (using state transitions or activity tracking)
CREATE OR REPLACE VIEW te_approvals_v AS
SELECT
  m.id AS approval_id,
  e.id AS expense_id,
  e.employee_id,
  u.login AS approver_name,
  m.subtype_id AS state,
  m.date AS entered_at,
  CASE WHEN e.state IN ('approve', 'done') THEN e.write_date ELSE NULL END AS decided_at,
  EXTRACT(EPOCH FROM (
    COALESCE(
      CASE WHEN e.state IN ('approve', 'done') THEN e.write_date ELSE CURRENT_TIMESTAMP END,
      CURRENT_TIMESTAMP
    ) - m.date
  ))/3600.0 AS hours_open
FROM mail_message m
JOIN hr_expense e ON m.res_id = e.id AND m.model = 'hr.expense'
LEFT JOIN res_users u ON m.author_id = u.partner_id
WHERE m.message_type = 'notification'
  AND m.subtype_id IS NOT NULL;

-- OCR receipts quality (placeholder - adapt to your OCR processing table)
CREATE OR REPLACE VIEW te_receipts_ocr_v AS
SELECT
  a.id AS receipt_id,
  a.res_id AS expense_id,
  1 AS page_count,
  'paddleocr' AS ocr_engine,
  RANDOM() * 0.3 + 0.7 AS ocr_confidence,        -- Mock confidence 0.7-1.0
  0 AS parse_errors,
  a.create_date AS processed_at
FROM ir_attachment a
WHERE a.res_model = 'hr.expense'
  AND a.mimetype LIKE 'image/%'
LIMIT 1000;

-- Grant permissions (adjust role as needed)
GRANT SELECT ON te_expenses_v TO superset_user;
GRANT SELECT ON te_cash_advances_v TO superset_user;
GRANT SELECT ON te_approvals_v TO superset_user;
GRANT SELECT ON te_receipts_ocr_v TO superset_user;

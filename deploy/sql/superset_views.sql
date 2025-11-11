-- Superset Dashboard Views for InsightPulse Odoo
-- These views provide aggregated data for Superset dashboards

-- Drop existing views
DROP VIEW IF EXISTS superset_expense_summary CASCADE;
DROP VIEW IF EXISTS superset_bir_compliance CASCADE;
DROP VIEW IF EXISTS superset_agency_metrics CASCADE;

-- 1. Expense Summary View
CREATE OR REPLACE VIEW superset_expense_summary AS
SELECT
    er.id,
    er.name AS expense_name,
    er.date_submitted,
    er.date_approved,
    er.total_amount,
    er.state,
    er.category,
    rc.name AS company_name,
    rc.id AS company_id,
    ru.name AS employee_name,
    ru.id AS employee_id,
    EXTRACT(YEAR FROM er.date_submitted) AS year,
    EXTRACT(MONTH FROM er.date_submitted) AS month,
    EXTRACT(QUARTER FROM er.date_submitted) AS quarter,
    CASE
        WHEN er.state = 'approved' THEN 'Approved'
        WHEN er.state = 'pending' THEN 'Pending'
        WHEN er.state = 'rejected' THEN 'Rejected'
        ELSE 'Draft'
    END AS status_label
FROM
    expense_report er
    JOIN res_company rc ON er.company_id = rc.id
    JOIN res_users ru ON er.employee_id = ru.id
WHERE
    er.active = true;

COMMENT ON VIEW superset_expense_summary IS 'Aggregated expense data for Superset dashboards';

-- 2. BIR Compliance View
CREATE OR REPLACE VIEW superset_bir_compliance AS
SELECT
    bf.id,
    bf.form_type,
    bf.submission_date,
    bf.status,
    bf.tax_amount,
    bf.period_covered,
    rc.name AS company_name,
    rc.id AS company_id,
    EXTRACT(YEAR FROM bf.submission_date) AS year,
    EXTRACT(QUARTER FROM bf.submission_date) AS quarter,
    EXTRACT(MONTH FROM bf.submission_date) AS month,
    CASE
        WHEN bf.status = 'submitted' THEN 'Submitted'
        WHEN bf.status = 'draft' THEN 'Draft'
        WHEN bf.status = 'cancelled' THEN 'Cancelled'
        ELSE 'Unknown'
    END AS status_label,
    CASE
        WHEN bf.form_type = '2307' THEN 'Withholding Tax Certificate'
        WHEN bf.form_type = '2316' THEN 'Annual Information Return'
        WHEN bf.form_type = '1601C' THEN 'Monthly Remittance Return'
        WHEN bf.form_type = '1702RT' THEN 'Annual Income Tax Return'
        ELSE bf.form_type
    END AS form_description
FROM
    bir_form bf
    JOIN res_company rc ON bf.company_id = rc.id
WHERE
    bf.active = true;

COMMENT ON VIEW superset_bir_compliance IS 'BIR form compliance data for Superset dashboards';

-- 3. Agency Performance Metrics
CREATE OR REPLACE VIEW superset_agency_metrics AS
SELECT
    rc.id AS company_id,
    rc.name AS company_name,
    COUNT(DISTINCT er.id) AS total_expenses,
    SUM(er.total_amount) AS total_expense_amount,
    AVG(er.total_amount) AS avg_expense_amount,
    COUNT(DISTINCT CASE WHEN er.state = 'approved' THEN er.id END) AS approved_count,
    COUNT(DISTINCT CASE WHEN er.state = 'pending' THEN er.id END) AS pending_count,
    COUNT(DISTINCT CASE WHEN er.state = 'rejected' THEN er.id END) AS rejected_count,
    COUNT(DISTINCT bf.id) AS total_bir_forms,
    COUNT(DISTINCT CASE WHEN bf.status = 'submitted' THEN bf.id END) AS submitted_bir_forms,
    EXTRACT(YEAR FROM CURRENT_DATE) AS current_year,
    EXTRACT(MONTH FROM CURRENT_DATE) AS current_month
FROM
    res_company rc
    LEFT JOIN expense_report er ON rc.id = er.company_id
        AND er.active = true
        AND EXTRACT(YEAR FROM er.date_submitted) = EXTRACT(YEAR FROM CURRENT_DATE)
    LEFT JOIN bir_form bf ON rc.id = bf.company_id
        AND bf.active = true
        AND EXTRACT(YEAR FROM bf.submission_date) = EXTRACT(YEAR FROM CURRENT_DATE)
WHERE
    rc.active = true
GROUP BY
    rc.id, rc.name;

COMMENT ON VIEW superset_agency_metrics IS 'Performance metrics by agency/company for Superset dashboards';

-- Grant SELECT permissions to Superset user (adjust username as needed)
GRANT SELECT ON superset_expense_summary TO PUBLIC;
GRANT SELECT ON superset_bir_compliance TO PUBLIC;
GRANT SELECT ON superset_agency_metrics TO PUBLIC;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_expense_report_date_submitted ON expense_report(date_submitted);
CREATE INDEX IF NOT EXISTS idx_expense_report_company_id ON expense_report(company_id);
CREATE INDEX IF NOT EXISTS idx_bir_form_submission_date ON bir_form(submission_date);
CREATE INDEX IF NOT EXISTS idx_bir_form_company_id ON bir_form(company_id);

-- Expense fact view for analytics
create view if not exists public.vw_expense_fact as
select
    e.id,
    e.name,
    e.employee_id,
    e.total_amount as amount,
    e.date,
    coalesce(e.x_policy_breach, false) as policy_breach,
    e.x_ocr_confidence as ocr_conf,
    e.x_approval_latency_days as approval_latency,
    e.x_merchant as merchant,
    e.x_category as category
from staging_odoo.hr_expense e;
-- Replace with fdw/materialized import

-- Dataset: fact_invoice
-- Description: Invoice fact table with AR/AP aging and payment details
-- Schema: analytics
-- Refresh: Real-time via CDC

SELECT
    invoice_id,
    invoice_key,
    invoice_number,
    invoice_date,
    due_date,
    payment_date,
    invoice_type,
    partner_key,
    partner_name,
    company_key,
    fiscal_period,
    state,
    payment_state,
    amount_untaxed,
    amount_tax,
    amount_total,
    amount_residual,
    days_overdue,
    aging_bucket,
    is_paid,
    is_overdue,
    created_at,
    updated_at
FROM analytics.fact_invoice
WHERE invoice_date >= CURRENT_DATE - INTERVAL '2 years'
ORDER BY invoice_date DESC;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.fact_invoice
-- Type: Fact Table
-- Columns:
--   - invoice_id (INTEGER): Invoice ID
--   - invoice_key (INTEGER): Invoice surrogate key
--   - invoice_number (VARCHAR): Invoice number
--   - invoice_date (DATE): Invoice date
--   - due_date (DATE): Payment due date
--   - payment_date (TIMESTAMP): Payment timestamp
--   - invoice_type (VARCHAR): Invoice type (out_invoice, in_invoice, out_refund, in_refund)
--   - partner_key (INTEGER): Partner foreign key
--   - partner_name (VARCHAR): Partner name
--   - company_key (INTEGER): Company foreign key
--   - fiscal_period (VARCHAR): Fiscal period
--   - state (VARCHAR): Invoice state (draft, posted, cancel)
--   - payment_state (VARCHAR): Payment state (not_paid, in_payment, paid, partial, reversed)
--   - amount_untaxed (DECIMAL): Amount before tax
--   - amount_tax (DECIMAL): Tax amount
--   - amount_total (DECIMAL): Total amount including tax
--   - amount_residual (DECIMAL): Outstanding amount
--   - days_overdue (INTEGER): Days past due date
--   - aging_bucket (VARCHAR): Aging bucket (current, 1-30, 31-60, 61-90, 90+)
--   - is_paid (BOOLEAN): Paid in full flag
--   - is_overdue (BOOLEAN): Overdue flag
--   - created_at (TIMESTAMP): Record creation timestamp
--   - updated_at (TIMESTAMP): Record update timestamp

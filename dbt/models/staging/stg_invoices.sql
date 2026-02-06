-- Staging model for Odoo invoices (account.move)
-- Covers customer invoices and vendor bills

WITH source AS (
    SELECT * FROM {{ source('odoo_raw', 'account_move') }}
),

renamed AS (
    SELECT
        -- Primary key
        id AS move_id,
        
        -- Classification
        move_type,  -- 'out_invoice', 'in_invoice', 'out_refund', 'in_refund', etc.
        CASE 
            WHEN move_type IN ('out_invoice', 'out_refund') THEN 'customer'
            WHEN move_type IN ('in_invoice', 'in_refund') THEN 'vendor'
            ELSE 'other'
        END AS move_category,
        
        -- Document info
        name AS move_number,
        ref AS external_reference,
        state,  -- 'draft', 'posted', 'cancel'
        
        -- Parties
        partner_id,
        commercial_partner_id,
        
        -- Amounts
        amount_untaxed,
        amount_tax,
        amount_total,
        amount_residual,  -- Outstanding amount
        currency_id,
        
        -- Dates
        date AS accounting_date,
        invoice_date,
        invoice_date_due AS due_date,
        
        -- Payment
        payment_state,  -- 'not_paid', 'in_payment', 'paid', 'partial', 'reversed', 'invoicing_legacy'
        invoice_payment_term_id,
        
        -- Company context
        company_id,
        journal_id,
        fiscal_position_id,
        
        -- Origin
        invoice_origin,  -- SO number, PO number, etc.
        reversed_entry_id,  -- For credit notes
        
        -- Timestamps
        create_date AS created_at,
        write_date AS updated_at,
        invoice_date AS transaction_date,
        
        -- Computed flags
        CASE WHEN state = 'posted' THEN true ELSE false END AS is_posted,
        CASE WHEN amount_residual = 0 THEN true ELSE false END AS is_fully_paid,
        CASE WHEN invoice_date_due < CURRENT_DATE AND amount_residual > 0 THEN true ELSE false END AS is_overdue,
        
        -- Raw data backup
        row_to_json(source.*)::jsonb AS raw_data
        
    FROM source
)

SELECT * FROM renamed
WHERE state != 'cancel'  -- Exclude cancelled moves

-- Model configuration
-- {{ config(
--     materialized='table',
--     schema='staging',
--     tags=['staging', 'invoices', 'accounting', 'daily']
-- ) }}

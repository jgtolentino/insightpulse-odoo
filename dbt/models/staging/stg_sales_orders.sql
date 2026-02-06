-- Staging model for Odoo sales orders (sale.order)

WITH source AS (
    SELECT * FROM {{ source('odoo_raw', 'sale_order') }}
),

renamed AS (
    SELECT
        -- Primary key
        id AS order_id,
        
        -- Document info
        name AS order_number,
        client_order_ref AS customer_reference,
        state,  -- 'draft', 'sent', 'sale', 'done', 'cancel'
        
        -- Customer
        partner_id,
        partner_invoice_id,
        partner_shipping_id,
        
        -- Amounts
        amount_untaxed,
        amount_tax,
        amount_total,
        currency_id,
        
        -- Dates
        date_order AS order_date,
        validity_date AS quote_expiry_date,
        commitment_date AS promised_date,
        expected_date,
        
        -- Company context
        company_id,
        user_id AS salesperson_id,
        team_id AS sales_team_id,
        
        -- Invoice status
        invoice_status,  -- 'upselling', 'to invoice', 'invoiced', 'no'
        
        -- Additional info
        note AS internal_notes,
        payment_term_id,
        pricelist_id,
        
        -- Timestamps
        create_date AS created_at,
        write_date AS updated_at,
        
        -- Computed flags
        CASE WHEN state IN ('sale', 'done') THEN true ELSE false END AS is_confirmed,
        CASE WHEN invoice_status = 'invoiced' THEN true ELSE false END AS is_fully_invoiced,
        
        -- Raw data
        row_to_json(source.*)::jsonb AS raw_data
        
    FROM source
)

SELECT * FROM renamed
WHERE state != 'cancel'

-- Model configuration
-- {{ config(
--     materialized='table',
--     schema='staging',
--     tags=['staging', 'sales', 'daily']
-- ) }}

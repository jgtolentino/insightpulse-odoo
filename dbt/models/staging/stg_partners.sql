-- Staging model for Odoo partners (res.partner)
-- This model provides a cleaned, typed version of the raw partner data

WITH source AS (
    SELECT * FROM {{ source('odoo_raw', 'res_partner') }}
),

renamed AS (
    SELECT
        -- Primary key
        id AS partner_id,
        
        -- Core attributes
        name AS partner_name,
        display_name,
        ref AS partner_reference,
        
        -- Contact information
        email,
        phone,
        mobile,
        website,
        
        -- Address
        street,
        street2,
        city,
        state_id,
        zip AS postal_code,
        country_id,
        
        -- Classification
        company_type,
        is_company,
        parent_id,
        
        -- Business details
        vat AS tax_id,
        commercial_company_name,
        industry_id,
        
        -- Financials
        property_payment_term_id,
        property_supplier_payment_term_id,
        credit_limit,
        
        -- Flags
        active,
        customer_rank,
        supplier_rank,
        employee AS is_employee,
        
        -- Timestamps
        create_date AS created_at,
        write_date AS updated_at,
        create_uid AS created_by,
        write_uid AS updated_by,
        
        -- Additional fields (JSONB for flexibility)
        -- Store full record as JSONB for advanced queries
        row_to_json(source.*)::jsonb AS raw_data
        
    FROM source
)

SELECT * FROM renamed
WHERE active = true  -- Only active partners by default

-- Model configuration
-- {{ config(
--     materialized='table',
--     schema='staging',
--     tags=['staging', 'partners', 'daily']
-- ) }}

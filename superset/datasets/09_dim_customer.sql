-- Dataset: dim_customer
-- Description: Customer dimension table with segmentation and attributes
-- Schema: analytics
-- Refresh: Daily via CDC

SELECT
    customer_key,
    customer_id,
    customer_name,
    email,
    phone,
    street,
    city,
    state_name,
    country_name,
    zip,
    is_company,
    is_customer,
    is_supplier,
    customer_segment,
    industry,
    company_size,
    credit_limit,
    payment_terms,
    vat,
    created_date,
    updated_date
FROM analytics.dim_customer
WHERE is_active = true
ORDER BY customer_name;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.dim_customer
-- Type: Dimension Table
-- Columns:
--   - customer_key (INTEGER): Customer surrogate key (Primary Key)
--   - customer_id (INTEGER): Customer ID from source system
--   - customer_name (VARCHAR): Customer name
--   - email (VARCHAR): Email address
--   - phone (VARCHAR): Phone number
--   - street (VARCHAR): Street address
--   - city (VARCHAR): City
--   - state_name (VARCHAR): State/Province
--   - country_name (VARCHAR): Country
--   - zip (VARCHAR): Postal code
--   - is_company (BOOLEAN): Company flag
--   - is_customer (BOOLEAN): Customer flag
--   - is_supplier (BOOLEAN): Supplier flag
--   - customer_segment (VARCHAR): Customer segment (VIP, Enterprise, SMB, etc.)
--   - industry (VARCHAR): Industry classification
--   - company_size (VARCHAR): Company size category
--   - credit_limit (DECIMAL): Credit limit
--   - payment_terms (VARCHAR): Payment terms
--   - vat (VARCHAR): VAT/Tax ID
--   - created_date (DATE): Record creation date
--   - updated_date (DATE): Record update date

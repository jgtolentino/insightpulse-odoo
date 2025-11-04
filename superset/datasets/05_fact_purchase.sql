-- Dataset: fact_purchase
-- Description: Purchase order fact table with vendor and procurement metrics
-- Schema: analytics
-- Refresh: Real-time via CDC

SELECT
    purchase_id,
    purchase_key,
    order_date,
    approval_date,
    receipt_date,
    supplier_key,
    supplier_name,
    product_key,
    company_key,
    state,
    amount_untaxed,
    amount_tax,
    amount_total,
    quantity,
    unit_price,
    days_to_approve,
    days_to_receive,
    on_time_delivery,
    is_approved,
    is_received,
    product_category,
    product_name,
    created_at,
    updated_at
FROM analytics.fact_purchase
WHERE order_date >= CURRENT_DATE - INTERVAL '2 years'
ORDER BY order_date DESC;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.fact_purchase
-- Type: Fact Table
-- Columns:
--   - purchase_id (INTEGER): Purchase order ID
--   - purchase_key (INTEGER): Purchase surrogate key
--   - order_date (DATE): Order date
--   - approval_date (TIMESTAMP): Approval timestamp
--   - receipt_date (TIMESTAMP): Receipt timestamp
--   - supplier_key (INTEGER): Supplier foreign key
--   - supplier_name (VARCHAR): Supplier name
--   - product_key (INTEGER): Product foreign key
--   - company_key (INTEGER): Company foreign key
--   - state (VARCHAR): Purchase state (draft, sent, purchase, done, cancel)
--   - amount_untaxed (DECIMAL): Amount before tax
--   - amount_tax (DECIMAL): Tax amount
--   - amount_total (DECIMAL): Total amount including tax
--   - quantity (DECIMAL): Quantity ordered
--   - unit_price (DECIMAL): Unit price
--   - days_to_approve (INTEGER): Days from creation to approval
--   - days_to_receive (INTEGER): Days from order to receipt
--   - on_time_delivery (BOOLEAN): On-time delivery flag
--   - is_approved (BOOLEAN): Approval flag
--   - is_received (BOOLEAN): Receipt flag
--   - product_category (VARCHAR): Product category
--   - product_name (VARCHAR): Product name
--   - created_at (TIMESTAMP): Record creation timestamp
--   - updated_at (TIMESTAMP): Record update timestamp

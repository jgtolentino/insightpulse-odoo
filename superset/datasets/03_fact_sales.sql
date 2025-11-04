-- Dataset: fact_sales
-- Description: Sales order fact table with all transaction details
-- Schema: analytics
-- Refresh: Real-time via CDC

SELECT
    sale_id,
    sale_key,
    order_date,
    confirmation_date,
    delivery_date,
    customer_key,
    product_key,
    company_key,
    sales_team_key,
    salesperson_key,
    salesperson_name,
    sales_team_name,
    state,
    amount_untaxed,
    amount_tax,
    amount_total,
    quantity,
    unit_price,
    discount_percent,
    margin,
    margin_percent,
    days_to_deliver,
    days_to_close,
    is_confirmed,
    is_delivered,
    sales_quota,
    created_at,
    updated_at
FROM analytics.fact_sales
WHERE order_date >= CURRENT_DATE - INTERVAL '2 years'
ORDER BY order_date DESC;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.fact_sales
-- Type: Fact Table
-- Columns:
--   - sale_id (INTEGER): Sale order ID
--   - sale_key (INTEGER): Sale surrogate key
--   - order_date (DATE): Order date
--   - confirmation_date (TIMESTAMP): Confirmation timestamp
--   - delivery_date (TIMESTAMP): Delivery timestamp
--   - customer_key (INTEGER): Customer foreign key
--   - product_key (INTEGER): Product foreign key
--   - company_key (INTEGER): Company foreign key
--   - sales_team_key (INTEGER): Sales team foreign key
--   - salesperson_key (INTEGER): Salesperson foreign key
--   - salesperson_name (VARCHAR): Salesperson name
--   - sales_team_name (VARCHAR): Sales team name
--   - state (VARCHAR): Order state (draft, sent, sale, done, cancel)
--   - amount_untaxed (DECIMAL): Amount before tax
--   - amount_tax (DECIMAL): Tax amount
--   - amount_total (DECIMAL): Total amount including tax
--   - quantity (DECIMAL): Quantity ordered
--   - unit_price (DECIMAL): Unit price
--   - discount_percent (DECIMAL): Discount percentage
--   - margin (DECIMAL): Profit margin amount
--   - margin_percent (DECIMAL): Profit margin percentage
--   - days_to_deliver (INTEGER): Days from order to delivery
--   - days_to_close (INTEGER): Days from draft to confirmed
--   - is_confirmed (BOOLEAN): Order confirmed flag
--   - is_delivered (BOOLEAN): Order delivered flag
--   - sales_quota (DECIMAL): Sales quota for period
--   - created_at (TIMESTAMP): Record creation timestamp
--   - updated_at (TIMESTAMP): Record update timestamp

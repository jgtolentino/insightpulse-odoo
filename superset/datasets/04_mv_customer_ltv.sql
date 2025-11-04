-- Dataset: mv_customer_ltv
-- Description: Customer lifetime value metrics
-- Schema: analytics
-- Refresh: Hourly via materialized view

SELECT
    customer_key,
    customer_name,
    company_id,
    lifetime_value,
    total_orders,
    avg_order_value,
    first_order_date,
    last_order_date,
    days_since_last_order,
    customer_segment,
    is_active,
    total_revenue_ytd,
    total_revenue_last_year
FROM analytics.mv_customer_ltv
WHERE company_id IS NOT NULL
ORDER BY lifetime_value DESC;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.mv_customer_ltv
-- Type: Materialized View
-- Columns:
--   - customer_key (INTEGER): Customer foreign key
--   - customer_name (VARCHAR): Customer name
--   - company_id (INTEGER): Company ID
--   - lifetime_value (DECIMAL): Total customer lifetime value
--   - total_orders (INTEGER): Total number of orders
--   - avg_order_value (DECIMAL): Average order value
--   - first_order_date (DATE): First order date
--   - last_order_date (DATE): Most recent order date
--   - days_since_last_order (INTEGER): Days since last purchase
--   - customer_segment (VARCHAR): Customer segment (VIP, Regular, New, etc.)
--   - is_active (BOOLEAN): Active customer flag
--   - total_revenue_ytd (DECIMAL): Revenue year-to-date
--   - total_revenue_last_year (DECIMAL): Revenue from previous year

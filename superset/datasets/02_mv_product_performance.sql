-- Dataset: mv_product_performance
-- Description: Product performance metrics including revenue, quantity, and margin
-- Schema: analytics
-- Refresh: Hourly via materialized view

SELECT
    product_key,
    product_name,
    product_category,
    company_id,
    total_revenue,
    total_quantity_sold,
    total_orders,
    avg_price,
    avg_margin_percent,
    last_sale_date,
    first_sale_date
FROM analytics.mv_product_performance
WHERE company_id IS NOT NULL
ORDER BY total_revenue DESC;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.mv_product_performance
-- Type: Materialized View
-- Columns:
--   - product_key (INTEGER): Product foreign key
--   - product_name (VARCHAR): Product name
--   - product_category (VARCHAR): Product category
--   - company_id (INTEGER): Company ID
--   - total_revenue (DECIMAL): Total revenue from product
--   - total_quantity_sold (DECIMAL): Total quantity sold
--   - total_orders (INTEGER): Number of orders
--   - avg_price (DECIMAL): Average selling price
--   - avg_margin_percent (DECIMAL): Average profit margin percentage
--   - last_sale_date (DATE): Most recent sale date
--   - first_sale_date (DATE): First sale date

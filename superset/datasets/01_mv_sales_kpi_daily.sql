-- Dataset: mv_sales_kpi_daily
-- Description: Daily sales KPIs including revenue, orders, and customer metrics
-- Schema: analytics
-- Refresh: Hourly via materialized view

SELECT
    sale_date,
    company_key,
    company_name,
    confirmed_orders,
    confirmed_revenue,
    confirmed_quantity,
    customer_key,
    product_key,
    sales_team_key
FROM analytics.mv_sales_kpi_daily
WHERE sale_date >= CURRENT_DATE - INTERVAL '365 days'
ORDER BY sale_date DESC;

-- Table reference for Superset dataset configuration:
-- Table name: analytics.mv_sales_kpi_daily
-- Type: Materialized View
-- Columns:
--   - sale_date (DATE): Date of sale
--   - company_key (INTEGER): Company foreign key
--   - company_name (VARCHAR): Company name
--   - confirmed_orders (INTEGER): Number of confirmed orders
--   - confirmed_revenue (DECIMAL): Total confirmed revenue
--   - confirmed_quantity (DECIMAL): Total quantity sold
--   - customer_key (INTEGER): Customer foreign key
--   - product_key (INTEGER): Product foreign key
--   - sales_team_key (INTEGER): Sales team foreign key

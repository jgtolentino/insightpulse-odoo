-- ============================================================================
-- Odoo Analytics Views for Apache Superset
-- ============================================================================
-- 
-- These SQL views provide curated analytics data from Odoo for use in
-- Apache Superset dashboards. They are designed to:
--
-- 1. Optimize query performance with pre-aggregated data
-- 2. Provide clean, denormalized data for BI tools
-- 3. Support row-level security (RLS) filtering
-- 4. Enable multi-company analytics
--
-- Installation:
--   Execute this script in your Odoo PostgreSQL database as a superuser
--   or database owner. These views can be used directly in Superset.
--
-- Security:
--   - Create a read-only database user for Superset
--   - Grant SELECT privileges on these views only
--   - Configure RLS in Superset to filter by company_id
--
-- ============================================================================

-- ============================================================================
-- SALES ANALYTICS VIEWS
-- ============================================================================

-- Daily Sales KPI View
-- Aggregates sales orders by day with key performance metrics
DROP VIEW IF EXISTS vw_sales_kpi_day CASCADE;
CREATE OR REPLACE VIEW vw_sales_kpi_day AS
SELECT 
    date_trunc('day', so.date_order)::date as sale_date,
    so.company_id,
    c.name as company_name,
    COUNT(DISTINCT so.id) as order_count,
    COUNT(DISTINCT CASE WHEN so.state IN ('sale', 'done') THEN so.id END) as confirmed_order_count,
    COUNT(DISTINCT CASE WHEN so.state = 'done' THEN so.id END) as delivered_order_count,
    SUM(so.amount_total) as total_revenue,
    SUM(CASE WHEN so.state IN ('sale', 'done') THEN so.amount_total ELSE 0 END) as confirmed_revenue,
    SUM(CASE WHEN so.state = 'done' THEN so.amount_total ELSE 0 END) as delivered_revenue,
    AVG(so.amount_total) as avg_order_value,
    COUNT(DISTINCT so.partner_id) as unique_customers,
    COUNT(DISTINCT so.user_id) as active_salespeople
FROM sale_order so
JOIN res_company c ON so.company_id = c.id
WHERE so.date_order IS NOT NULL
GROUP BY date_trunc('day', so.date_order), so.company_id, c.name;

COMMENT ON VIEW vw_sales_kpi_day IS 'Daily sales KPIs aggregated from sale orders';


-- Product Performance View
-- Aggregates sales by product with profitability metrics
DROP VIEW IF EXISTS vw_product_performance CASCADE;
CREATE OR REPLACE VIEW vw_product_performance AS
SELECT 
    pt.id as product_tmpl_id,
    pt.name as product_name,
    pt.categ_id,
    pc.complete_name as category_name,
    sol.company_id,
    c.name as company_name,
    COUNT(DISTINCT sol.order_id) as order_count,
    SUM(sol.product_uom_qty) as total_qty_sold,
    SUM(sol.price_subtotal) as total_revenue,
    AVG(sol.price_unit) as avg_selling_price,
    AVG(pt.standard_price) as avg_cost_price,
    SUM(sol.price_subtotal - (sol.product_uom_qty * pt.standard_price)) as estimated_profit,
    MAX(so.date_order) as last_sale_date
FROM sale_order_line sol
JOIN sale_order so ON sol.order_id = so.id
JOIN product_product pp ON sol.product_id = pp.id
JOIN product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN product_category pc ON pt.categ_id = pc.id
JOIN res_company c ON sol.company_id = c.id
WHERE so.state IN ('sale', 'done')
GROUP BY pt.id, pt.name, pt.categ_id, pc.complete_name, sol.company_id, c.name;

COMMENT ON VIEW vw_product_performance IS 'Product sales performance with profitability metrics';


-- Customer Lifetime Value (LTV) View
DROP VIEW IF EXISTS vw_customer_ltv CASCADE;
CREATE OR REPLACE VIEW vw_customer_ltv AS
SELECT 
    p.id as partner_id,
    p.name as customer_name,
    p.email,
    p.phone,
    p.city,
    p.state_id,
    st.name as state_name,
    p.country_id,
    co.name as country_name,
    so.company_id,
    c.name as company_name,
    COUNT(DISTINCT so.id) as order_count,
    SUM(so.amount_total) as lifetime_value,
    AVG(so.amount_total) as avg_order_value,
    MIN(so.date_order) as first_order_date,
    MAX(so.date_order) as last_order_date,
    EXTRACT(DAYS FROM (MAX(so.date_order) - MIN(so.date_order))) as customer_age_days,
    SUM(so.amount_total) / NULLIF(EXTRACT(DAYS FROM (MAX(so.date_order) - MIN(so.date_order))), 0) as daily_revenue_rate
FROM res_partner p
JOIN sale_order so ON p.id = so.partner_id
LEFT JOIN res_country_state st ON p.state_id = st.id
LEFT JOIN res_country co ON p.country_id = co.id
JOIN res_company c ON so.company_id = c.id
WHERE so.state IN ('sale', 'done')
GROUP BY p.id, p.name, p.email, p.phone, p.city, p.state_id, st.name, p.country_id, co.name, so.company_id, c.name;

COMMENT ON VIEW vw_customer_ltv IS 'Customer lifetime value and engagement metrics';


-- ============================================================================
-- INVENTORY & WAREHOUSE ANALYTICS VIEWS
-- ============================================================================

-- Stock Level Summary View
DROP VIEW IF EXISTS vw_stock_level_summary CASCADE;
CREATE OR REPLACE VIEW vw_stock_level_summary AS
SELECT 
    pp.id as product_id,
    pt.name as product_name,
    pt.categ_id,
    pc.complete_name as category_name,
    sl.company_id,
    c.name as company_name,
    sl.id as location_id,
    sl.complete_name as location_name,
    COALESCE(SUM(sq.quantity), 0) as available_qty,
    COALESCE(SUM(sq.reserved_quantity), 0) as reserved_qty,
    COALESCE(SUM(sq.quantity - sq.reserved_quantity), 0) as free_qty,
    pt.standard_price as unit_cost,
    COALESCE(SUM(sq.quantity), 0) * pt.standard_price as stock_value
FROM product_product pp
JOIN product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN product_category pc ON pt.categ_id = pc.id
CROSS JOIN stock_location sl
LEFT JOIN stock_quant sq ON sq.product_id = pp.id AND sq.location_id = sl.id
JOIN res_company c ON sl.company_id = c.id
WHERE sl.usage = 'internal'
GROUP BY pp.id, pt.name, pt.categ_id, pc.complete_name, sl.company_id, c.name, sl.id, sl.complete_name, pt.standard_price;

COMMENT ON VIEW vw_stock_level_summary IS 'Current stock levels by product and location';


-- Inventory Turnover View
DROP VIEW IF EXISTS vw_inventory_turnover CASCADE;
CREATE OR REPLACE VIEW vw_inventory_turnover AS
WITH sales_12m AS (
    SELECT 
        sol.product_id,
        sol.company_id,
        SUM(sol.product_uom_qty) as qty_sold_12m
    FROM sale_order_line sol
    JOIN sale_order so ON sol.order_id = so.id
    WHERE so.state IN ('sale', 'done')
      AND so.date_order >= CURRENT_DATE - INTERVAL '12 months'
    GROUP BY sol.product_id, sol.company_id
),
avg_inventory AS (
    SELECT 
        sq.product_id,
        sq.company_id,
        AVG(sq.quantity) as avg_qty_on_hand
    FROM stock_quant sq
    GROUP BY sq.product_id, sq.company_id
)
SELECT 
    pt.id as product_tmpl_id,
    pt.name as product_name,
    pt.categ_id,
    pc.complete_name as category_name,
    ai.company_id,
    c.name as company_name,
    COALESCE(s12.qty_sold_12m, 0) as qty_sold_12m,
    COALESCE(ai.avg_qty_on_hand, 0) as avg_qty_on_hand,
    CASE 
        WHEN COALESCE(ai.avg_qty_on_hand, 0) > 0 
        THEN COALESCE(s12.qty_sold_12m, 0) / ai.avg_qty_on_hand 
        ELSE 0 
    END as turnover_ratio,
    CASE 
        WHEN COALESCE(s12.qty_sold_12m, 0) > 0 
        THEN 365.0 * COALESCE(ai.avg_qty_on_hand, 0) / s12.qty_sold_12m 
        ELSE NULL 
    END as days_on_hand
FROM product_product pp
JOIN product_template pt ON pp.product_tmpl_id = pt.id
LEFT JOIN product_category pc ON pt.categ_id = pc.id
LEFT JOIN avg_inventory ai ON ai.product_id = pp.id
LEFT JOIN sales_12m s12 ON s12.product_id = pp.id AND s12.company_id = ai.company_id
JOIN res_company c ON ai.company_id = c.id
WHERE ai.company_id IS NOT NULL;

COMMENT ON VIEW vw_inventory_turnover IS 'Inventory turnover ratio and days on hand by product';


-- ============================================================================
-- ACCOUNTING & FINANCIAL ANALYTICS VIEWS
-- ============================================================================

-- Accounts Receivable Aging View
DROP VIEW IF EXISTS vw_ar_aging CASCADE;
CREATE OR REPLACE VIEW vw_ar_aging AS
SELECT 
    aml.id as move_line_id,
    aml.move_id,
    am.name as move_name,
    am.invoice_date,
    aml.date_maturity,
    aml.partner_id,
    p.name as partner_name,
    aml.company_id,
    c.name as company_name,
    aml.account_id,
    aa.name as account_name,
    aml.debit,
    aml.credit,
    aml.amount_residual,
    CURRENT_DATE - aml.date_maturity as days_overdue,
    CASE 
        WHEN aml.date_maturity >= CURRENT_DATE THEN 'Current'
        WHEN CURRENT_DATE - aml.date_maturity <= 30 THEN '1-30 days'
        WHEN CURRENT_DATE - aml.date_maturity <= 60 THEN '31-60 days'
        WHEN CURRENT_DATE - aml.date_maturity <= 90 THEN '61-90 days'
        ELSE '90+ days'
    END as aging_bucket
FROM account_move_line aml
JOIN account_move am ON aml.move_id = am.id
JOIN account_account aa ON aml.account_id = aa.id
JOIN res_partner p ON aml.partner_id = p.id
JOIN res_company c ON aml.company_id = c.id
WHERE aa.account_type = 'asset_receivable'
  AND aml.reconciled = FALSE
  AND aml.amount_residual > 0;

COMMENT ON VIEW vw_ar_aging IS 'Accounts receivable aging analysis';


-- Monthly Revenue by Account View
DROP VIEW IF EXISTS vw_monthly_revenue CASCADE;
CREATE OR REPLACE VIEW vw_monthly_revenue AS
SELECT 
    date_trunc('month', aml.date)::date as month,
    aml.company_id,
    c.name as company_name,
    aml.account_id,
    aa.code as account_code,
    aa.name as account_name,
    SUM(aml.credit - aml.debit) as revenue
FROM account_move_line aml
JOIN account_account aa ON aml.account_id = aa.id
JOIN account_move am ON aml.move_id = am.id
JOIN res_company c ON aml.company_id = c.id
WHERE aa.account_type IN ('income', 'income_other')
  AND am.state = 'posted'
GROUP BY date_trunc('month', aml.date), aml.company_id, c.name, aml.account_id, aa.code, aa.name;

COMMENT ON VIEW vw_monthly_revenue IS 'Monthly revenue aggregated by account';


-- ============================================================================
-- HR ANALYTICS VIEWS
-- ============================================================================

-- Employee Headcount View
DROP VIEW IF EXISTS vw_employee_headcount CASCADE;
CREATE OR REPLACE VIEW vw_employee_headcount AS
SELECT 
    date_trunc('month', CURRENT_DATE)::date as month,
    e.company_id,
    c.name as company_name,
    e.department_id,
    d.name as department_name,
    e.job_id,
    j.name as job_title,
    COUNT(DISTINCT e.id) FILTER (WHERE e.active = TRUE) as active_employees,
    COUNT(DISTINCT e.id) FILTER (WHERE e.active = FALSE) as inactive_employees,
    COUNT(DISTINCT e.id) as total_employees
FROM hr_employee e
LEFT JOIN hr_department d ON e.department_id = d.id
LEFT JOIN hr_job j ON e.job_id = j.id
JOIN res_company c ON e.company_id = c.id
GROUP BY date_trunc('month', CURRENT_DATE), e.company_id, c.name, e.department_id, d.name, e.job_id, j.name;

COMMENT ON VIEW vw_employee_headcount IS 'Employee headcount by department and job title';


-- ============================================================================
-- GRANTS FOR READ-ONLY SUPERSET USER
-- ============================================================================
-- 
-- Execute these commands to create a read-only user for Superset:
--
-- CREATE USER superset_readonly WITH PASSWORD 'your_secure_password';
-- GRANT CONNECT ON DATABASE your_odoo_db TO superset_readonly;
-- GRANT USAGE ON SCHEMA public TO superset_readonly;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO superset_readonly;
-- GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO superset_readonly;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO superset_readonly;
--
-- -- Grant access to analytics views specifically:
-- GRANT SELECT ON vw_sales_kpi_day TO superset_readonly;
-- GRANT SELECT ON vw_product_performance TO superset_readonly;
-- GRANT SELECT ON vw_customer_ltv TO superset_readonly;
-- GRANT SELECT ON vw_stock_level_summary TO superset_readonly;
-- GRANT SELECT ON vw_inventory_turnover TO superset_readonly;
-- GRANT SELECT ON vw_ar_aging TO superset_readonly;
-- GRANT SELECT ON vw_monthly_revenue TO superset_readonly;
-- GRANT SELECT ON vw_employee_headcount TO superset_readonly;
--
-- ============================================================================

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Create indexes on commonly filtered columns
CREATE INDEX IF NOT EXISTS idx_sale_order_date_company ON sale_order(date_order, company_id) WHERE state IN ('sale', 'done');
CREATE INDEX IF NOT EXISTS idx_sale_order_partner_company ON sale_order(partner_id, company_id) WHERE state IN ('sale', 'done');
CREATE INDEX IF NOT EXISTS idx_account_move_line_date_company ON account_move_line(date, company_id);
CREATE INDEX IF NOT EXISTS idx_stock_quant_product_location ON stock_quant(product_id, location_id);

-- ============================================================================
-- MATERIALIZED VIEWS (OPTIONAL - FOR LARGE DATASETS)
-- ============================================================================
--
-- For very large datasets, you can create materialized views and refresh them
-- periodically via a cron job:
--
-- CREATE MATERIALIZED VIEW mv_sales_kpi_day AS SELECT * FROM vw_sales_kpi_day;
-- CREATE UNIQUE INDEX ON mv_sales_kpi_day (sale_date, company_id);
--
-- -- Refresh command (run via cron):
-- REFRESH MATERIALIZED VIEW CONCURRENTLY mv_sales_kpi_day;
--
-- ============================================================================

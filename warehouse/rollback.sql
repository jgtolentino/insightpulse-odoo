-- Rollback script for T&E MVP warehouse views
-- Run this if you need to remove the T&E MVP database objects

-- Drop materialized views first (dependencies)
DROP MATERIALIZED VIEW IF EXISTS public.mv_expense_7d CASCADE;

-- Drop views
DROP VIEW IF EXISTS public.vw_expense_fact CASCADE;

-- Note: This does not drop the Skillsmith objects
-- See skillsmith/rollback.sql for Skillsmith cleanup

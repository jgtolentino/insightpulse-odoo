-- ============================================================================
-- Supabase RLS Remediation - Day 1: Tier 1 Critical Tables (Basic Protection)
-- ============================================================================
-- Date: November 4, 2025
-- Scope: Enable RLS on 59 public tables with basic policies
-- Security Level: CRITICAL - Addresses Supabase linter ERROR level issues
-- 
-- Strategy:
--   1. Enable RLS on all public tables
--   2. Grant service_role full access (system operations)
--   3. Grant authenticated users appropriate access based on table purpose
--   4. Phase 2 will add company_id columns and refined multi-tenant isolation
-- ============================================================================

BEGIN;

-- ============================================================================
-- TASK MANAGEMENT SYSTEM
-- ============================================================================

-- task_queue - Already has RLS enabled, ensure proper policies
ALTER TABLE IF EXISTS public.task_queue ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist and recreate
DROP POLICY IF EXISTS "Allow authenticated read on task_queue" ON public.task_queue;
DROP POLICY IF EXISTS "Service role full access on task_queue" ON public.task_queue;

CREATE POLICY "task_queue_authenticated_read" ON public.task_queue
  FOR SELECT TO authenticated
  USING (true);  -- All authenticated users can read (for now)

CREATE POLICY "task_queue_user_write" ON public.task_queue
  FOR ALL TO authenticated
  USING (created_by = auth.uid() OR created_by IS NULL);  -- Users can manage their own tasks

CREATE POLICY "task_queue_service_role" ON public.task_queue
  FOR ALL TO service_role
  USING (true);

-- task_route
ALTER TABLE IF EXISTS public.task_route ENABLE ROW LEVEL SECURITY;

CREATE POLICY "task_route_read_all" ON public.task_route
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "task_route_service_role" ON public.task_route
  FOR ALL TO service_role
  USING (true);

-- task_kind
ALTER TABLE IF EXISTS public.task_kind ENABLE ROW LEVEL SECURITY;

CREATE POLICY "task_kind_read_all" ON public.task_kind
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "task_kind_service_role" ON public.task_kind
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- WORKER SYSTEM
-- ============================================================================

-- worker_role
ALTER TABLE IF EXISTS public.worker_role ENABLE ROW LEVEL SECURITY;

CREATE POLICY "worker_role_read_all" ON public.worker_role
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "worker_role_service_role" ON public.worker_role
  FOR ALL TO service_role
  USING (true);

-- worker_label_map
ALTER TABLE IF EXISTS public.worker_label_map ENABLE ROW LEVEL SECURITY;

CREATE POLICY "worker_label_map_read_all" ON public.worker_label_map
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "worker_label_map_service_role" ON public.worker_label_map
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- EMAIL SYSTEM
-- ============================================================================

-- email_outbox
ALTER TABLE IF EXISTS public.email_outbox ENABLE ROW LEVEL SECURITY;

CREATE POLICY "email_outbox_read_all" ON public.email_outbox
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "email_outbox_service_role" ON public.email_outbox
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- GITHUB INTEGRATION
-- ============================================================================

-- github_repo_config
ALTER TABLE IF EXISTS public.github_repo_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "github_repo_config_read_all" ON public.github_repo_config
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "github_repo_config_service_role" ON public.github_repo_config
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- EXPENSE SYSTEM
-- ============================================================================

-- expense_daily_rollup
ALTER TABLE IF EXISTS public.expense_daily_rollup ENABLE ROW LEVEL SECURITY;

CREATE POLICY "expense_daily_rollup_read_all" ON public.expense_daily_rollup
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "expense_daily_rollup_service_role" ON public.expense_daily_rollup
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- ADDITIONAL TABLES FROM LINTER REPORT
-- ============================================================================

-- alembic_version (migration table)
ALTER TABLE IF EXISTS public.alembic_version ENABLE ROW LEVEL SECURITY;

CREATE POLICY "alembic_version_read_all" ON public.alembic_version
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "alembic_version_service_role" ON public.alembic_version
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- SUPERSET TABLES - Basic RLS (User & Permission)
-- ============================================================================

-- ab_user
ALTER TABLE IF EXISTS public.ab_user ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ab_user_own_record" ON public.ab_user
  FOR ALL TO authenticated
  USING (username = current_user);

CREATE POLICY "ab_user_service_role" ON public.ab_user
  FOR ALL TO service_role
  USING (true);

-- ab_role
ALTER TABLE IF EXISTS public.ab_role ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ab_role_read_all" ON public.ab_role
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "ab_role_service_role" ON public.ab_role
  FOR ALL TO service_role
  USING (true);

-- ab_permission
ALTER TABLE IF EXISTS public.ab_permission ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ab_permission_read_all" ON public.ab_permission
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "ab_permission_service_role" ON public.ab_permission
  FOR ALL TO service_role
  USING (true);

-- ab_permission_view
ALTER TABLE IF EXISTS public.ab_permission_view ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ab_permission_view_read_all" ON public.ab_permission_view
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "ab_permission_view_service_role" ON public.ab_permission_view
  FOR ALL TO service_role
  USING (true);

-- ab_view_menu
ALTER TABLE IF EXISTS public.ab_view_menu ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ab_view_menu_read_all" ON public.ab_view_menu
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "ab_view_menu_service_role" ON public.ab_view_menu
  FOR ALL TO service_role
  USING (true);

-- ab_user_role
ALTER TABLE IF EXISTS public.ab_user_role ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ab_user_role_own_roles" ON public.ab_user_role
  FOR ALL TO authenticated
  USING (user_id = (SELECT id FROM ab_user WHERE username = current_user));

CREATE POLICY "ab_user_role_service_role" ON public.ab_user_role
  FOR ALL TO service_role
  USING (true);

-- ab_permission_view_role
ALTER TABLE IF EXISTS public.ab_permission_view_role ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ab_permission_view_role_read_all" ON public.ab_permission_view_role
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "ab_permission_view_role_service_role" ON public.ab_permission_view_role
  FOR ALL TO service_role
  USING (true);

-- ab_register_user
ALTER TABLE IF EXISTS public.ab_register_user ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ab_register_user_own_record" ON public.ab_register_user
  FOR ALL TO authenticated
  USING (username = current_user);

CREATE POLICY "ab_register_user_service_role" ON public.ab_register_user
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- SUPERSET TABLES - Dashboards & Slices
-- ============================================================================

-- dashboards
ALTER TABLE IF EXISTS public.dashboards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dashboards_read_all" ON public.dashboards
  FOR SELECT TO authenticated
  USING (true);  -- All authenticated users can read dashboards

CREATE POLICY "dashboards_service_role" ON public.dashboards
  FOR ALL TO service_role
  USING (true);

-- slices (charts)
ALTER TABLE IF EXISTS public.slices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "slices_read_all" ON public.slices
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "slices_service_role" ON public.slices
  FOR ALL TO service_role
  USING (true);

-- dashboard_slices
ALTER TABLE IF EXISTS public.dashboard_slices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dashboard_slices_read_all" ON public.dashboard_slices
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "dashboard_slices_service_role" ON public.dashboard_slices
  FOR ALL TO service_role
  USING (true);

-- dashboard_user
ALTER TABLE IF EXISTS public.dashboard_user ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dashboard_user_read_all" ON public.dashboard_user
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "dashboard_user_service_role" ON public.dashboard_user
  FOR ALL TO service_role
  USING (true);

-- slice_user
ALTER TABLE IF EXISTS public.slice_user ENABLE ROW LEVEL SECURITY;

CREATE POLICY "slice_user_read_all" ON public.slice_user
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "slice_user_service_role" ON public.slice_user
  FOR ALL TO service_role
  USING (true);

-- dashboard_roles
ALTER TABLE IF EXISTS public.dashboard_roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dashboard_roles_read_all" ON public.dashboard_roles
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "dashboard_roles_service_role" ON public.dashboard_roles
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- SUPERSET TABLES - Database & Tables
-- ============================================================================

-- dbs
ALTER TABLE IF EXISTS public.dbs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dbs_read_all" ON public.dbs
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "dbs_service_role" ON public.dbs
  FOR ALL TO service_role
  USING (true);

-- tables
ALTER TABLE IF EXISTS public.tables ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tables_read_all" ON public.tables
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "tables_service_role" ON public.tables
  FOR ALL TO service_role
  USING (true);

-- table_columns
ALTER TABLE IF EXISTS public.table_columns ENABLE ROW LEVEL SECURITY;

CREATE POLICY "table_columns_read_all" ON public.table_columns
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "table_columns_service_role" ON public.table_columns
  FOR ALL TO service_role
  USING (true);

-- table_schema
ALTER TABLE IF EXISTS public.table_schema ENABLE ROW LEVEL SECURITY;

CREATE POLICY "table_schema_read_all" ON public.table_schema
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "table_schema_service_role" ON public.table_schema
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- SUPERSET TABLES - Queries & SQL
-- ============================================================================

-- query
ALTER TABLE IF EXISTS public.query ENABLE ROW LEVEL SECURITY;

CREATE POLICY "query_read_all" ON public.query
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "query_service_role" ON public.query
  FOR ALL TO service_role
  USING (true);

-- saved_query
ALTER TABLE IF EXISTS public.saved_query ENABLE ROW LEVEL SECURITY;

CREATE POLICY "saved_query_read_all" ON public.saved_query
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "saved_query_service_role" ON public.saved_query
  FOR ALL TO service_role
  USING (true);

-- sql_metrics
ALTER TABLE IF EXISTS public.sql_metrics ENABLE ROW LEVEL SECURITY;

CREATE POLICY "sql_metrics_read_all" ON public.sql_metrics
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "sql_metrics_service_role" ON public.sql_metrics
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- SUPERSET TABLES - Additional
-- ============================================================================

-- logs
ALTER TABLE IF EXISTS public.logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "logs_service_role" ON public.logs
  FOR ALL TO service_role
  USING (true);

-- keyvalue
ALTER TABLE IF EXISTS public.keyvalue ENABLE ROW LEVEL SECURITY;

CREATE POLICY "keyvalue_read_all" ON public.keyvalue
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "keyvalue_service_role" ON public.keyvalue
  FOR ALL TO service_role
  USING (true);

-- key_value
ALTER TABLE IF EXISTS public.key_value ENABLE ROW LEVEL SECURITY;

CREATE POLICY "key_value_read_all" ON public.key_value
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "key_value_service_role" ON public.key_value
  FOR ALL TO service_role
  USING (true);

-- annotation_layer
ALTER TABLE IF EXISTS public.annotation_layer ENABLE ROW LEVEL SECURITY;

CREATE POLICY "annotation_layer_read_all" ON public.annotation_layer
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "annotation_layer_service_role" ON public.annotation_layer
  FOR ALL TO service_role
  USING (true);

-- annotation
ALTER TABLE IF EXISTS public.annotation ENABLE ROW LEVEL SECURITY;

CREATE POLICY "annotation_read_all" ON public.annotation
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "annotation_service_role" ON public.annotation
  FOR ALL TO service_role
  USING (true);

-- sqlatable_user
ALTER TABLE IF EXISTS public.sqlatable_user ENABLE ROW LEVEL SECURITY;

CREATE POLICY "sqlatable_user_read_all" ON public.sqlatable_user
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "sqlatable_user_service_role" ON public.sqlatable_user
  FOR ALL TO service_role
  USING (true);

-- rls_filter_roles
ALTER TABLE IF EXISTS public.rls_filter_roles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "rls_filter_roles_read_all" ON public.rls_filter_roles
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "rls_filter_roles_service_role" ON public.rls_filter_roles
  FOR ALL TO service_role
  USING (true);

-- rls_filter_tables
ALTER TABLE IF EXISTS public.rls_filter_tables ENABLE ROW LEVEL SECURITY;

CREATE POLICY "rls_filter_tables_read_all" ON public.rls_filter_tables
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "rls_filter_tables_service_role" ON public.rls_filter_tables
  FOR ALL TO service_role
  USING (true);

-- cache_keys
ALTER TABLE IF EXISTS public.cache_keys ENABLE ROW LEVEL SECURITY;

CREATE POLICY "cache_keys_service_role" ON public.cache_keys
  FOR ALL TO service_role
  USING (true);

-- report_recipient
ALTER TABLE IF EXISTS public.report_recipient ENABLE ROW LEVEL SECURITY;

CREATE POLICY "report_recipient_read_all" ON public.report_recipient
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "report_recipient_service_role" ON public.report_recipient
  FOR ALL TO service_role
  USING (true);

-- report_schedule_user
ALTER TABLE IF EXISTS public.report_schedule_user ENABLE ROW LEVEL SECURITY;

CREATE POLICY "report_schedule_user_read_all" ON public.report_schedule_user
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "report_schedule_user_service_role" ON public.report_schedule_user
  FOR ALL TO service_role
  USING (true);

-- dynamic_plugin
ALTER TABLE IF EXISTS public.dynamic_plugin ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dynamic_plugin_read_all" ON public.dynamic_plugin
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "dynamic_plugin_service_role" ON public.dynamic_plugin
  FOR ALL TO service_role
  USING (true);

-- report_execution_log
ALTER TABLE IF EXISTS public.report_execution_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY "report_execution_log_read_all" ON public.report_execution_log
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "report_execution_log_service_role" ON public.report_execution_log
  FOR ALL TO service_role
  USING (true);

-- embedded_dashboards
ALTER TABLE IF EXISTS public.embedded_dashboards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "embedded_dashboards_read_all" ON public.embedded_dashboards
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "embedded_dashboards_service_role" ON public.embedded_dashboards
  FOR ALL TO service_role
  USING (true);

-- row_level_security_filters
ALTER TABLE IF EXISTS public.row_level_security_filters ENABLE ROW LEVEL SECURITY;

CREATE POLICY "row_level_security_filters_read_all" ON public.row_level_security_filters
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "row_level_security_filters_service_role" ON public.row_level_security_filters
  FOR ALL TO service_role
  USING (true);

-- ssh_tunnels
ALTER TABLE IF EXISTS public.ssh_tunnels ENABLE ROW LEVEL SECURITY;

CREATE POLICY "ssh_tunnels_service_role" ON public.ssh_tunnels
  FOR ALL TO service_role
  USING (true);

-- tagged_object
ALTER TABLE IF EXISTS public.tagged_object ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tagged_object_read_all" ON public.tagged_object
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "tagged_object_service_role" ON public.tagged_object
  FOR ALL TO service_role
  USING (true);

-- tag
ALTER TABLE IF EXISTS public.tag ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tag_read_all" ON public.tag
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "tag_service_role" ON public.tag
  FOR ALL TO service_role
  USING (true);

-- user_favorite_tag
ALTER TABLE IF EXISTS public.user_favorite_tag ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_favorite_tag_read_all" ON public.user_favorite_tag
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "user_favorite_tag_service_role" ON public.user_favorite_tag
  FOR ALL TO service_role
  USING (true);

-- database_user_oauth2_tokens
ALTER TABLE IF EXISTS public.database_user_oauth2_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "database_user_oauth2_tokens_service_role" ON public.database_user_oauth2_tokens
  FOR ALL TO service_role
  USING (true);

-- user_attribute
ALTER TABLE IF EXISTS public.user_attribute ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user_attribute_read_all" ON public.user_attribute
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "user_attribute_service_role" ON public.user_attribute
  FOR ALL TO service_role
  USING (true);

-- tab_state
ALTER TABLE IF EXISTS public.tab_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tab_state_read_all" ON public.tab_state
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "tab_state_service_role" ON public.tab_state
  FOR ALL TO service_role
  USING (true);

-- report_schedule
ALTER TABLE IF EXISTS public.report_schedule ENABLE ROW LEVEL SECURITY;

CREATE POLICY "report_schedule_read_all" ON public.report_schedule
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "report_schedule_service_role" ON public.report_schedule
  FOR ALL TO service_role
  USING (true);

-- css_templates
ALTER TABLE IF EXISTS public.css_templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "css_templates_read_all" ON public.css_templates
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "css_templates_service_role" ON public.css_templates
  FOR ALL TO service_role
  USING (true);

-- favstar
ALTER TABLE IF EXISTS public.favstar ENABLE ROW LEVEL SECURITY;

CREATE POLICY "favstar_read_all" ON public.favstar
  FOR SELECT TO authenticated
  USING (true);

CREATE POLICY "favstar_service_role" ON public.favstar
  FOR ALL TO service_role
  USING (true);

-- ============================================================================
-- VALIDATION
-- ============================================================================

DO $$
DECLARE
  v_disabled_count INTEGER;
  v_enabled_count INTEGER;
BEGIN
  -- Count tables without RLS
  SELECT COUNT(DISTINCT t.tablename) INTO v_disabled_count
  FROM pg_tables t
  LEFT JOIN pg_class c ON t.tablename = c.relname
  WHERE t.schemaname = 'public'
    AND (c.relrowsecurity IS NULL OR c.relrowsecurity = false);

  -- Count tables with RLS
  SELECT COUNT(DISTINCT t.tablename) INTO v_enabled_count
  FROM pg_tables t
  JOIN pg_class c ON t.tablename = c.relname
  WHERE t.schemaname = 'public'
    AND c.relrowsecurity = true;

  RAISE NOTICE 'Tables with RLS ENABLED: %', v_enabled_count;
  RAISE NOTICE 'Tables with RLS DISABLED: %', v_disabled_count;
  
  IF v_disabled_count > 10 THEN
    RAISE WARNING 'Still % tables without RLS protection', v_disabled_count;
  END IF;
END $$;

COMMIT;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================

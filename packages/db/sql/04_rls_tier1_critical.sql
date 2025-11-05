-- ============================================================================
-- Supabase RLS Remediation - Day 1: Tier 1 Critical Tables
-- ============================================================================
-- Date: November 4, 2025
-- Scope: 15 critical tables requiring immediate company isolation
-- Security Level: CRITICAL
-- 
-- Tables:
--   - Task Management (10 tables)
--   - Worker System (2 tables)
--   - Email System (1 table)
--   - GitHub Integration (1 table)
--   - Expense System (1 table)
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. TASK MANAGEMENT SYSTEM (10 tables)
-- ============================================================================

-- 1.1 task_queue - Main task queue with company isolation
-- ============================================================================
ALTER TABLE public.task_queue ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see tasks from their company
CREATE POLICY "task_queue_company_isolation" ON public.task_queue
  FOR ALL 
  TO authenticated
  USING (company_id = (core.jwt_company_id()));

-- Policy: Service role has full access (system operations)
CREATE POLICY "task_queue_service_role" ON public.task_queue
  FOR ALL 
  TO service_role
  USING (true);

-- Policy: Anon role can only read public tasks (if needed)
CREATE POLICY "task_queue_anon_read" ON public.task_queue
  FOR SELECT
  TO anon
  USING (status = 'public');

-- 1.2 task_route - Task routing configuration
-- ============================================================================
ALTER TABLE public.task_route ENABLE ROW LEVEL SECURITY;

CREATE POLICY "task_route_company_isolation" ON public.task_route
  FOR ALL
  TO authenticated
  USING (company_id = (core.jwt_company_id()));

CREATE POLICY "task_route_service_role" ON public.task_route
  FOR ALL
  TO service_role
  USING (true);

-- 1.3 task_kind - Reference table (read-only for all authenticated)
-- ============================================================================
ALTER TABLE public.task_kind ENABLE ROW LEVEL SECURITY;

CREATE POLICY "task_kind_read_all" ON public.task_kind
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "task_kind_service_role" ON public.task_kind
  FOR ALL
  TO service_role
  USING (true);

-- 1.4 task_comment - Task comments with company isolation
-- ============================================================================
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'task_comment') THEN
    ALTER TABLE public.task_comment ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "task_comment_company_isolation" ON public.task_comment
      FOR ALL
      TO authenticated
      USING (
        task_id IN (SELECT id FROM task_queue WHERE company_id = (core.jwt_company_id()))
      );
    
    CREATE POLICY "task_comment_service_role" ON public.task_comment
      FOR ALL
      TO service_role
      USING (true);
  END IF;
END $$;

-- 1.5 task_history - Task audit trail with company isolation
-- ============================================================================
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'task_history') THEN
    ALTER TABLE public.task_history ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "task_history_company_isolation" ON public.task_history
      FOR ALL
      TO authenticated
      USING (
        task_id IN (SELECT id FROM task_queue WHERE company_id = (core.jwt_company_id()))
      );
    
    CREATE POLICY "task_history_service_role" ON public.task_history
      FOR ALL
      TO service_role
      USING (true);
  END IF;
END $$;

-- 1.6 task_attachment - Task file attachments with company isolation
-- ============================================================================
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'task_attachment') THEN
    ALTER TABLE public.task_attachment ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "task_attachment_company_isolation" ON public.task_attachment
      FOR ALL
      TO authenticated
      USING (
        task_id IN (SELECT id FROM task_queue WHERE company_id = (core.jwt_company_id()))
      );
    
    CREATE POLICY "task_attachment_service_role" ON public.task_attachment
      FOR ALL
      TO service_role
      USING (true);
  END IF;
END $$;

-- 1.7 task_label - Task labels with company isolation
-- ============================================================================
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'task_label') THEN
    ALTER TABLE public.task_label ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "task_label_company_isolation" ON public.task_label
      FOR ALL
      TO authenticated
      USING (
        task_id IN (SELECT id FROM task_queue WHERE company_id = (core.jwt_company_id()))
      );
    
    CREATE POLICY "task_label_service_role" ON public.task_label
      FOR ALL
      TO service_role
      USING (true);
  END IF;
END $$;

-- 1.8 task_dependency - Task dependencies with company isolation
-- ============================================================================
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'task_dependency') THEN
    ALTER TABLE public.task_dependency ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "task_dependency_company_isolation" ON public.task_dependency
      FOR ALL
      TO authenticated
      USING (
        task_id IN (SELECT id FROM task_queue WHERE company_id = (core.jwt_company_id())) AND
        depends_on_task_id IN (SELECT id FROM task_queue WHERE company_id = (core.jwt_company_id()))
      );
    
    CREATE POLICY "task_dependency_service_role" ON public.task_dependency
      FOR ALL
      TO service_role
      USING (true);
  END IF;
END $$;

-- 1.9 task_watchers - Task watchers with company isolation
-- ============================================================================
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'task_watchers') THEN
    ALTER TABLE public.task_watchers ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "task_watchers_company_isolation" ON public.task_watchers
      FOR ALL
      TO authenticated
      USING (
        task_id IN (SELECT id FROM task_queue WHERE company_id = (core.jwt_company_id()))
      );
    
    CREATE POLICY "task_watchers_service_role" ON public.task_watchers
      FOR ALL
      TO service_role
      USING (true);
  END IF;
END $$;

-- 1.10 task_sla - Task SLA tracking with company isolation
-- ============================================================================
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'task_sla') THEN
    ALTER TABLE public.task_sla ENABLE ROW LEVEL SECURITY;
    
    CREATE POLICY "task_sla_company_isolation" ON public.task_sla
      FOR ALL
      TO authenticated
      USING (
        task_id IN (SELECT id FROM task_queue WHERE company_id = (core.jwt_company_id()))
      );
    
    CREATE POLICY "task_sla_service_role" ON public.task_sla
      FOR ALL
      TO service_role
      USING (true);
  END IF;
END $$;

-- ============================================================================
-- 2. WORKER SYSTEM (2 tables)
-- ============================================================================

-- 2.1 worker_role - Reference table (read-only for authenticated)
-- ============================================================================
ALTER TABLE public.worker_role ENABLE ROW LEVEL SECURITY;

CREATE POLICY "worker_role_read_all" ON public.worker_role
  FOR SELECT
  TO authenticated
  USING (true);

CREATE POLICY "worker_role_service_role" ON public.worker_role
  FOR ALL
  TO service_role
  USING (true);

-- 2.2 worker_label_map - Worker label mapping with company isolation
-- ============================================================================
ALTER TABLE public.worker_label_map ENABLE ROW LEVEL SECURITY;

CREATE POLICY "worker_label_map_company_isolation" ON public.worker_label_map
  FOR ALL
  TO authenticated
  USING (company_id = (core.jwt_company_id()));

CREATE POLICY "worker_label_map_service_role" ON public.worker_label_map
  FOR ALL
  TO service_role
  USING (true);

-- ============================================================================
-- 3. EMAIL SYSTEM (1 table)
-- ============================================================================

-- 3.1 email_outbox - Email queue with sender/recipient company isolation
-- ============================================================================
ALTER TABLE public.email_outbox ENABLE ROW LEVEL SECURITY;

-- Policy: Users can see emails sent by their company OR sent to their company
CREATE POLICY "email_outbox_company_isolation" ON public.email_outbox
  FOR ALL
  TO authenticated
  USING (
    company_id = (core.jwt_company_id()) OR 
    recipient_company_id = (core.jwt_company_id())
  );

CREATE POLICY "email_outbox_service_role" ON public.email_outbox
  FOR ALL
  TO service_role
  USING (true);

-- ============================================================================
-- 4. GITHUB INTEGRATION (1 table)
-- ============================================================================

-- 4.1 github_repo_config - GitHub repository configuration with company isolation
-- ============================================================================
ALTER TABLE public.github_repo_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "github_repo_config_company_isolation" ON public.github_repo_config
  FOR ALL
  TO authenticated
  USING (company_id = (core.jwt_company_id()));

CREATE POLICY "github_repo_config_service_role" ON public.github_repo_config
  FOR ALL
  TO service_role
  USING (true);

-- ============================================================================
-- 5. EXPENSE SYSTEM (1 table)
-- ============================================================================

-- 5.1 expense_daily_rollup - Expense rollup with company isolation
-- ============================================================================
ALTER TABLE public.expense_daily_rollup ENABLE ROW LEVEL SECURITY;

CREATE POLICY "expense_daily_rollup_company_isolation" ON public.expense_daily_rollup
  FOR ALL
  TO authenticated
  USING (company_id = (core.jwt_company_id()));

CREATE POLICY "expense_daily_rollup_service_role" ON public.expense_daily_rollup
  FOR ALL
  TO service_role
  USING (true);

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Verify all Tier 1 tables have RLS enabled
DO $$
DECLARE
  v_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_count
  FROM pg_tables t
  JOIN pg_class c ON t.tablename = c.relname
  WHERE t.schemaname = 'public'
    AND t.tablename IN (
      'task_queue', 'task_route', 'task_kind', 
      'worker_role', 'worker_label_map',
      'email_outbox', 'github_repo_config', 'expense_daily_rollup'
    )
    AND c.relrowsecurity = true;

  RAISE NOTICE 'Tier 1 tables with RLS enabled: %', v_count;
  
  IF v_count < 8 THEN
    RAISE EXCEPTION 'Not all Tier 1 critical tables have RLS enabled! Expected 8, got %', v_count;
  END IF;
END $$;

-- Verify policies exist
DO $$
DECLARE
  v_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_count
  FROM pg_policies
  WHERE schemaname = 'public'
    AND tablename IN (
      'task_queue', 'task_route', 'task_kind',
      'worker_role', 'worker_label_map',
      'email_outbox', 'github_repo_config', 'expense_daily_rollup'
    );

  RAISE NOTICE 'RLS policies created: %', v_count;
  
  IF v_count < 16 THEN
    RAISE WARNING 'Expected at least 16 policies, found %', v_count;
  END IF;
END $$;

COMMIT;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================

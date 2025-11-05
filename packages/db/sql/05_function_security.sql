-- ============================================================================
-- Supabase RLS Remediation - Day 4: Function Security and Configuration
-- ============================================================================
-- Date: November 4, 2025
-- Scope: Fix 51 WARN level issues from Supabase linter
-- Security Level: WARNING - Security hardening
--
-- Issues addressed:
--   1. 33+ functions with SECURITY DEFINER but no SET search_path
--   2. 4 extensions in public schema (should be in extensions schema)
--   3. 2 auth config issues (leaked password protection, MFA options)
-- ============================================================================

BEGIN;

-- ============================================================================
-- 1. FIX SECURITY DEFINER FUNCTIONS - Add SET search_path
-- ============================================================================
--
-- SECURITY DEFINER functions without SET search_path are vulnerable to
-- privilege escalation attacks. We set search_path to prevent this.
--
-- Pattern: SET search_path = schema_name, pg_temp
--
-- NOTE: We can only alter functions we own. System functions (graphql,
-- pgbouncer, storage) owned by Supabase require support intervention.
-- ============================================================================

-- SYSTEM FUNCTIONS (Cannot alter - owned by Supabase):
-- - graphql.get_schema_version
-- - graphql.increment_schema_version
-- - pgbouncer.get_auth
-- - storage.* (7 functions)
-- These require Supabase support ticket to fix

-- Operations schema functions (if they exist and we own them)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'ops' AND p.proname = 'route_and_enqueue') THEN
    ALTER FUNCTION ops.route_and_enqueue(text, jsonb) SET search_path = ops, pg_temp;
    RAISE NOTICE 'Fixed: ops.route_and_enqueue';
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'ops' AND p.proname = 'snapshot_visual_baseline') THEN
    ALTER FUNCTION ops.snapshot_visual_baseline(text, text, text, jsonb) SET search_path = ops, pg_temp;
    RAISE NOTICE 'Fixed: ops.snapshot_visual_baseline';
  END IF;
END $$;

-- Public schema task management functions
ALTER FUNCTION public.claim_task(uuid) SET search_path = public, pg_temp;
ALTER FUNCTION public.route_and_enqueue(text, jsonb) SET search_path = public, pg_temp;
ALTER FUNCTION public.rpc_enqueue_odoo_visual(text, text, text, jsonb) SET search_path = public, pg_temp;
ALTER FUNCTION public.rpc_runbot_record(text, text, text, jsonb) SET search_path = public, pg_temp;
ALTER FUNCTION public.rpc_task_comment(uuid, text, text) SET search_path = public, pg_temp;

-- Public schema secret vault functions (if not migrated to secret_vault schema)
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'get_all_secrets') THEN
    ALTER FUNCTION public.get_all_secrets() SET search_path = public, pg_temp;
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'get_secret') THEN
    ALTER FUNCTION public.get_secret(text, text) SET search_path = public, pg_temp;
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'get_secrets_needing_rotation') THEN
    ALTER FUNCTION public.get_secrets_needing_rotation() SET search_path = public, pg_temp;
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'get_sync_targets') THEN
    ALTER FUNCTION public.get_sync_targets(text) SET search_path = public, pg_temp;
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'list_secret_names') THEN
    ALTER FUNCTION public.list_secret_names() SET search_path = public, pg_temp;
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'log_sync') THEN
    ALTER FUNCTION public.log_sync(text, text, text, boolean, text) SET search_path = public, pg_temp;
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'record_rotation') THEN
    ALTER FUNCTION public.record_rotation(text, text, text, text) SET search_path = public, pg_temp;
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'rotate_secret') THEN
    ALTER FUNCTION public.rotate_secret(text, text) SET search_path = public, pg_temp;
  END IF;

  IF EXISTS (SELECT 1 FROM pg_proc p JOIN pg_namespace n ON p.pronamespace = n.oid WHERE n.nspname = 'public' AND p.proname = 'store_secret') THEN
    ALTER FUNCTION public.store_secret(text, text, text, jsonb) SET search_path = public, pg_temp;
  END IF;
END $$;

-- Public schema snapshot function
ALTER FUNCTION public.snapshot_schema() SET search_path = public, pg_temp;

-- Secret vault schema functions
ALTER FUNCTION secret_vault.get_all_secrets() SET search_path = secret_vault, pg_temp;
ALTER FUNCTION secret_vault.get_secrets_needing_rotation() SET search_path = secret_vault, pg_temp;
ALTER FUNCTION secret_vault.get_sync_targets(text) SET search_path = secret_vault, pg_temp;
ALTER FUNCTION secret_vault.log_sync(text, text, text, boolean, text) SET search_path = secret_vault, pg_temp;
ALTER FUNCTION secret_vault.needs_rotation(timestamp with time zone, interval) SET search_path = secret_vault, pg_temp;
ALTER FUNCTION secret_vault.record_rotation(text, text, text, text) SET search_path = secret_vault, pg_temp;

-- Storage schema functions
ALTER FUNCTION storage.add_prefixes(text[], text[]) SET search_path = storage, pg_temp;
ALTER FUNCTION storage.delete_leaf_prefixes(text, text) SET search_path = storage, pg_temp;
ALTER FUNCTION storage.delete_prefix(text, text) SET search_path = storage, pg_temp;
ALTER FUNCTION storage.lock_top_prefixes(text, text) SET search_path = storage, pg_temp;
ALTER FUNCTION storage.objects_delete_cleanup(text, text[], text[]) SET search_path = storage, pg_temp;
ALTER FUNCTION storage.objects_update_cleanup(text, text[], text[]) SET search_path = storage, pg_temp;
ALTER FUNCTION storage.prefixes_delete_cleanup(text, text[]) SET search_path = storage, pg_temp;

-- ============================================================================
-- 2. MOVE EXTENSIONS TO EXTENSIONS SCHEMA
-- ============================================================================
--
-- Extensions should be installed in the 'extensions' schema, not 'public'
-- This follows Supabase best practices and security guidelines
-- ============================================================================

-- Note: Moving extensions requires superuser privileges
-- For Supabase hosted databases, this must be done via Supabase dashboard
-- or support request. Documenting the required changes here:

-- MANUAL STEP REQUIRED (Cannot be done via migration):
-- 1. Contact Supabase support or use dashboard to move extensions:
--    - pg_net (currently in public, should be in extensions)
--    - vector (currently in public, should be in extensions)
--    - pg_trgm (currently in public, should be in extensions)
--    - http (currently in public, should be in extensions)
--
-- 2. Alternatively, recreate extensions in correct schema:
--    DROP EXTENSION IF EXISTS pg_net CASCADE;
--    CREATE EXTENSION IF NOT EXISTS pg_net WITH SCHEMA extensions;
--
--    DROP EXTENSION IF EXISTS vector CASCADE;
--    CREATE EXTENSION IF NOT EXISTS vector WITH SCHEMA extensions;
--
--    DROP EXTENSION IF EXISTS pg_trgm CASCADE;
--    CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA extensions;
--
--    DROP EXTENSION IF EXISTS http CASCADE;
--    CREATE EXTENSION IF NOT EXISTS http WITH SCHEMA extensions;

DO $$
BEGIN
  RAISE NOTICE 'Extensions in public schema detected. Manual intervention required.';
  RAISE NOTICE 'Contact Supabase support to move: pg_net, vector, pg_trgm, http to extensions schema.';
END $$;

-- ============================================================================
-- 3. AUTH CONFIGURATION IMPROVEMENTS
-- ============================================================================
--
-- Enable security features in Supabase auth configuration
-- These require Supabase dashboard/API changes, cannot be done via SQL
-- ============================================================================

-- MANUAL STEP REQUIRED (Must be done via Supabase dashboard):
-- 1. Enable leaked password protection:
--    Settings > Authentication > Leaked Password Protection > Enable
--
-- 2. Configure MFA options:
--    Settings > Authentication > Multi-Factor Authentication > Enable TOTP
--    Settings > Authentication > Multi-Factor Authentication > Configure max verified factors

DO $$
BEGIN
  RAISE NOTICE 'Auth configuration changes required via Supabase dashboard:';
  RAISE NOTICE '1. Enable leaked password protection';
  RAISE NOTICE '2. Configure MFA options (TOTP, max verified factors)';
END $$;

-- ============================================================================
-- VALIDATION QUERIES
-- ============================================================================

-- Check functions still missing search_path
DO $$
DECLARE
  v_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_count
  FROM pg_proc p
  JOIN pg_namespace n ON p.pronamespace = n.oid
  WHERE p.prosecdef = true
    AND (p.proconfig IS NULL OR NOT array_to_string(p.proconfig, ',') LIKE '%search_path%')
    AND n.nspname NOT IN ('pg_catalog', 'information_schema');

  RAISE NOTICE 'SECURITY DEFINER functions without search_path: %', v_count;

  IF v_count > 0 THEN
    RAISE WARNING 'Some SECURITY DEFINER functions still lack SET search_path. Review needed.';
  ELSE
    RAISE NOTICE 'All SECURITY DEFINER functions now have SET search_path configured.';
  END IF;
END $$;

-- Check extensions in wrong schema
DO $$
DECLARE
  v_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO v_count
  FROM pg_extension e
  JOIN pg_namespace n ON e.extnamespace = n.oid
  WHERE n.nspname = 'public'
    AND e.extname IN ('pg_net', 'vector', 'pg_trgm', 'http');

  RAISE NOTICE 'Extensions in public schema (should be in extensions): %', v_count;

  IF v_count > 0 THEN
    RAISE WARNING 'Extensions detected in public schema. Manual migration required.';
  END IF;
END $$;

COMMIT;

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================

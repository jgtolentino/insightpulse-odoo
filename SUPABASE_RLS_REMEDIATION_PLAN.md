# 🔒 Supabase RLS Remediation Plan
**Date**: November 4, 2025  
**Severity**: 🔴 **CRITICAL** - 59 ERROR + 51 WARN issues  
**Sprint**: Sprint 1 Week 1 (Immediate Action Required)

---

## Executive Summary

Supabase database linter identified **110 security issues** requiring immediate remediation:

**ERROR (59 issues)**:
- 1× Security Definer View without proper isolation
- 58× Public tables without Row Level Security (RLS) policies

**WARN (51 issues)**:
- 47× Functions with mutable search_path (privilege escalation risk)
- 4× Extensions in public schema (namespace pollution)
- 2× Auth configuration weaknesses (MFA, password protection)

**Overall Risk**: **9.2/10 (Critical)** - Immediate action required

---

## 🔴 Critical Issues (ERROR Level)

### 1. Security Definer View (1 issue)

**Finding**: View `public.expense_feed` defined with SECURITY DEFINER
- **Risk**: Enforces view creator's permissions, not querying user's permissions
- **Impact**: Potential privilege escalation, bypasses RLS
- **CVSS**: 8.5 (High)

**Remediation**:
```sql
-- Option 1: Remove SECURITY DEFINER (recommended)
CREATE OR REPLACE VIEW public.expense_feed AS
  SELECT * FROM expenses WHERE company_id = (core.jwt_company_id());
-- Do NOT add SECURITY DEFINER

-- Option 2: If SECURITY DEFINER needed, add explicit RLS checks
CREATE OR REPLACE VIEW public.expense_feed 
SECURITY DEFINER AS
  SELECT * FROM expenses 
  WHERE company_id = (core.jwt_company_id())
  AND (SELECT current_user) IN (SELECT username FROM authorized_users);
```

---

### 2. RLS Disabled on Public Tables (58 issues)

**Critical Impact Tables** (Tier 1 - Immediate):
- **Task Management**: `task_queue`, `task_route`, `task_kind` (10 tables)
- **Worker System**: `worker_role`, `worker_label_map` (2 tables)
- **Email**: `email_outbox` (1 table)
- **GitHub Integration**: `github_repo_config` (1 table)
- **Expenses**: `expense_daily_rollup` (1 table)

**Superset Tables** (Tier 2 - High Priority):
- **User Management**: `ab_user`, `ab_role`, `ab_user_role` (17 tables)
- **Dashboards**: `dashboards`, `slices`, `dashboard_slices` (20 tables)
- **Database**: `dbs`, `tables`, `table_columns` (8 tables)
- **Queries**: `query`, `saved_query`, `sql_metrics` (10 tables)

**Migration Tables** (Tier 3 - Medium Priority):
- `alembic_version` (Superset schema versioning)

---

## 🎯 Remediation Strategy by Tier

### Tier 1: Critical Business Tables (15 tables)

**Priority**: 🔴 **IMMEDIATE** (Complete in 4 hours)  
**Rationale**: Direct business data exposure, multi-agency isolation required

#### Task Management System (10 tables)

```sql
-- 1. task_queue - Isolate by company_id
ALTER TABLE public.task_queue ENABLE ROW LEVEL SECURITY;

CREATE POLICY "task_queue_company_isolation" ON public.task_queue
  FOR ALL USING (company_id = (core.jwt_company_id()));

-- Service role bypass (for system operations)
CREATE POLICY "task_queue_service_role" ON public.task_queue
  FOR ALL TO service_role USING (true);

-- 2. task_route - Isolate by company_id
ALTER TABLE public.task_route ENABLE ROW LEVEL SECURITY;

CREATE POLICY "task_route_company_isolation" ON public.task_route
  FOR ALL USING (company_id = (core.jwt_company_id()));

CREATE POLICY "task_route_service_role" ON public.task_route
  FOR ALL TO service_role USING (true);

-- 3. task_kind - Reference table (read-only for all authenticated)
ALTER TABLE public.task_kind ENABLE ROW LEVEL SECURITY;

CREATE POLICY "task_kind_read_all" ON public.task_kind
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "task_kind_service_role" ON public.task_kind
  FOR ALL TO service_role USING (true);

-- Repeat for: task_comment, task_history, task_attachment, task_label, task_dependency, task_watchers, task_sla
```

#### Worker System (2 tables)

```sql
-- 1. worker_role - Reference table
ALTER TABLE public.worker_role ENABLE ROW LEVEL SECURITY;

CREATE POLICY "worker_role_read_all" ON public.worker_role
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "worker_role_service_role" ON public.worker_role
  FOR ALL TO service_role USING (true);

-- 2. worker_label_map - Isolate by company_id
ALTER TABLE public.worker_label_map ENABLE ROW LEVEL SECURITY;

CREATE POLICY "worker_label_map_company_isolation" ON public.worker_label_map
  FOR ALL USING (company_id = (core.jwt_company_id()));

CREATE POLICY "worker_label_map_service_role" ON public.worker_label_map
  FOR ALL TO service_role USING (true);
```

#### Email System (1 table)

```sql
-- email_outbox - Isolate by sender company
ALTER TABLE public.email_outbox ENABLE ROW LEVEL SECURITY;

CREATE POLICY "email_outbox_company_isolation" ON public.email_outbox
  FOR ALL USING (
    company_id = (core.jwt_company_id()) OR 
    recipient_company_id = (core.jwt_company_id())
  );

CREATE POLICY "email_outbox_service_role" ON public.email_outbox
  FOR ALL TO service_role USING (true);
```

#### GitHub Integration (1 table)

```sql
-- github_repo_config - Isolate by company_id
ALTER TABLE public.github_repo_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY "github_repo_config_company_isolation" ON public.github_repo_config
  FOR ALL USING (company_id = (core.jwt_company_id()));

CREATE POLICY "github_repo_config_service_role" ON public.github_repo_config
  FOR ALL TO service_role USING (true);
```

#### Expense System (1 table)

```sql
-- expense_daily_rollup - Isolate by company_id
ALTER TABLE public.expense_daily_rollup ENABLE ROW LEVEL SECURITY;

CREATE POLICY "expense_daily_rollup_company_isolation" ON public.expense_daily_rollup
  FOR ALL USING (company_id = (core.jwt_company_id()));

CREATE POLICY "expense_daily_rollup_service_role" ON public.expense_daily_rollup
  FOR ALL TO service_role USING (true);
```

---

### Tier 2: Superset Tables (45 tables)

**Priority**: 🟠 **HIGH** (Complete in 2 days)  
**Rationale**: BI system tables, read-mostly with admin write access

**Strategy**: Use Superset's built-in RLS system via `row_level_security_filters` table

#### User & Permission Tables (17 tables)

```sql
-- Superset manages its own permissions via Flask-AppBuilder
-- Enable RLS but allow Superset service account full access

ALTER TABLE public.ab_user ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ab_user_superset_service" ON public.ab_user
  FOR ALL TO service_role USING (true);

ALTER TABLE public.ab_role ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ab_role_superset_service" ON public.ab_role
  FOR ALL TO service_role USING (true);

ALTER TABLE public.ab_permission ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ab_permission_superset_service" ON public.ab_permission
  FOR ALL TO service_role USING (true);

ALTER TABLE public.ab_permission_view ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ab_permission_view_superset_service" ON public.ab_permission_view
  FOR ALL TO service_role USING (true);

ALTER TABLE public.ab_view_menu ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ab_view_menu_superset_service" ON public.ab_view_menu
  FOR ALL TO service_role USING (true);

ALTER TABLE public.ab_user_role ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ab_user_role_superset_service" ON public.ab_user_role
  FOR ALL TO service_role USING (true);

ALTER TABLE public.ab_permission_view_role ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ab_permission_view_role_superset_service" ON public.ab_permission_view_role
  FOR ALL TO service_role USING (true);

ALTER TABLE public.ab_register_user ENABLE ROW LEVEL SECURITY;
CREATE POLICY "ab_register_user_superset_service" ON public.ab_register_user
  FOR ALL TO service_role USING (true);

-- Repeat for remaining 9 ab_* tables
```

#### Dashboard Tables (20 tables)

```sql
-- Dashboards - User-specific access
ALTER TABLE public.dashboards ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dashboards_owner_access" ON public.dashboards
  FOR ALL USING (
    created_by_fk = (SELECT id FROM ab_user WHERE username = current_user) OR
    id IN (SELECT dashboard_id FROM dashboard_user WHERE user_id = (SELECT id FROM ab_user WHERE username = current_user))
  );

CREATE POLICY "dashboards_service_role" ON public.dashboards
  FOR ALL TO service_role USING (true);

-- Slices (Charts) - User-specific access
ALTER TABLE public.slices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "slices_owner_access" ON public.slices
  FOR ALL USING (
    created_by_fk = (SELECT id FROM ab_user WHERE username = current_user) OR
    id IN (SELECT slice_id FROM slice_user WHERE user_id = (SELECT id FROM ab_user WHERE username = current_user))
  );

CREATE POLICY "slices_service_role" ON public.slices
  FOR ALL TO service_role USING (true);

-- dashboard_slices - Junction table
ALTER TABLE public.dashboard_slices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dashboard_slices_inherit" ON public.dashboard_slices
  FOR ALL USING (
    dashboard_id IN (SELECT id FROM dashboards) -- Inherits dashboard access
  );

CREATE POLICY "dashboard_slices_service_role" ON public.dashboard_slices
  FOR ALL TO service_role USING (true);

-- Repeat for remaining 17 dashboard-related tables
```

#### Database Connection Tables (8 tables)

```sql
-- dbs - Database connections (admin only)
ALTER TABLE public.dbs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "dbs_admin_only" ON public.dbs
  FOR ALL USING (
    (SELECT id FROM ab_user WHERE username = current_user) IN 
    (SELECT user_id FROM ab_user_role WHERE role_id IN 
     (SELECT id FROM ab_role WHERE name IN ('Admin', 'Alpha')))
  );

CREATE POLICY "dbs_service_role" ON public.dbs
  FOR ALL TO service_role USING (true);

-- tables - Table metadata (read-only for users with dashboard access)
ALTER TABLE public.tables ENABLE ROW LEVEL SECURITY;

CREATE POLICY "tables_read_all_authenticated" ON public.tables
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "tables_write_admin" ON public.tables
  FOR INSERT, UPDATE, DELETE USING (
    (SELECT id FROM ab_user WHERE username = current_user) IN 
    (SELECT user_id FROM ab_user_role WHERE role_id IN 
     (SELECT id FROM ab_role WHERE name IN ('Admin', 'Alpha')))
  );

CREATE POLICY "tables_service_role" ON public.tables
  FOR ALL TO service_role USING (true);

-- Repeat for remaining 6 database-related tables
```

---

### Tier 3: Migration & System Tables (1 table)

**Priority**: 🟡 **MEDIUM** (Complete in 1 day)  
**Rationale**: Schema versioning table, low risk but should be protected

```sql
-- alembic_version - Read-only for authenticated, write for service role
ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY;

CREATE POLICY "alembic_version_read_all" ON public.alembic_version
  FOR SELECT USING (auth.role() = 'authenticated');

CREATE POLICY "alembic_version_service_role" ON public.alembic_version
  FOR ALL TO service_role USING (true);
```

---

## ⚠️ Warning Issues (WARN Level)

### 1. Function Search Path Mutable (47 functions)

**Finding**: Functions without fixed `search_path` parameter
- **Risk**: Privilege escalation via search_path manipulation
- **Impact**: Attackers can create malicious schemas to hijack function calls
- **CVSS**: 7.0 (High)

**Affected Functions**:
- Task system: `task_enqueue`, `task_claim`, `task_complete`, `task_fail`, `task_heartbeat`
- Routing: `route_and_enqueue` (public, ops, agent schemas)
- Secrets: `store_secret`, `get_secret`, `rotate_secret`, `get_secrets_needing_rotation`
- Operations: `snapshot_now`, `snapshot_visual_baseline`, `jwt_company_id`
- Cache: `cache_get`, `cache_put` (platinum schema)
- ETL: `match_chunks` (gold schema)
- Superset: All Superset RPC functions

**Remediation Pattern**:
```sql
-- BEFORE (vulnerable)
CREATE OR REPLACE FUNCTION public.task_enqueue(...)
RETURNS void AS $$
BEGIN
  -- function body
END;
$$ LANGUAGE plpgsql;

-- AFTER (secure)
CREATE OR REPLACE FUNCTION public.task_enqueue(...)
RETURNS void AS $$
BEGIN
  -- function body
END;
$$ LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public, pg_temp;
-- ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ Fixed search path prevents privilege escalation
```

**Batch Remediation Script**:
```sql
-- Generate ALTER statements for all vulnerable functions
SELECT format(
  'ALTER FUNCTION %I.%I(%s) SET search_path = %I, pg_temp;',
  n.nspname,
  p.proname,
  pg_get_function_identity_arguments(p.oid),
  n.nspname
)
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname IN ('public', 'ops', 'agent', 'core', 'gold', 'platinum', 'secret_vault')
  AND p.prosecdef = false  -- Not SECURITY DEFINER
  AND p.proname IN (
    'task_enqueue', 'task_claim', 'task_complete', 'task_fail', 'task_heartbeat',
    'route_and_enqueue', 'store_secret', 'get_secret', 'rotate_secret',
    'snapshot_now', 'jwt_company_id', 'cache_get', 'cache_put', 'match_chunks'
    -- Add remaining 32 functions
  );
```

---

### 2. Extensions in Public Schema (4 extensions)

**Finding**: Extensions installed in `public` schema
- **Risk**: Namespace pollution, privilege escalation potential
- **Impact**: Functions/types collide with user objects
- **CVSS**: 5.0 (Medium)

**Affected Extensions**:
- `pg_net` - HTTP client for PostgreSQL
- `vector` - pgvector for embeddings
- `pg_trgm` - Trigram matching for fuzzy search
- `http` - HTTP client (alternative to pg_net)

**Remediation**:
```sql
-- Move extensions to dedicated schema
CREATE SCHEMA IF NOT EXISTS extensions;

-- pg_net
ALTER EXTENSION pg_net SET SCHEMA extensions;

-- vector (pgvector)
ALTER EXTENSION vector SET SCHEMA extensions;

-- pg_trgm
ALTER EXTENSION pg_trgm SET SCHEMA extensions;

-- http
ALTER EXTENSION http SET SCHEMA extensions;

-- Update search_path for all users
ALTER DATABASE postgres SET search_path = public, extensions;
```

---

### 3. Auth Configuration Weaknesses (2 issues)

#### Issue 1: Leaked Password Protection Disabled

**Finding**: HaveIBeenPwned.org integration disabled
- **Risk**: Users can set compromised passwords
- **Impact**: Account takeover via known password leaks
- **CVSS**: 6.0 (Medium)

**Remediation**:
```bash
# Enable via Supabase Dashboard
# Authentication > Providers > Email > Password Options
# ✅ Enable "Check password against leaked password database"

# Or via API
curl -X PATCH https://api.supabase.com/v1/projects/spdtwktxdalcfigzeqrz/config/auth \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "SECURITY_REFRESH_TOKEN_REUSE_INTERVAL": 10,
    "PASSWORD_MIN_LENGTH": 8,
    "PASSWORD_REQUIRED_CHARACTERS": ["lower", "upper", "number", "special"],
    "SECURITY_LEAKED_PASSWORD_PROTECTION": true
  }'
```

#### Issue 2: Insufficient MFA Options

**Finding**: Too few MFA methods enabled
- **Risk**: Weak account security, limited MFA adoption
- **Impact**: Easier account compromise, lower security posture
- **CVSS**: 5.5 (Medium)

**Remediation**:
```bash
# Enable multiple MFA methods via Supabase Dashboard
# Authentication > Providers > Phone Auth
# ✅ Enable Phone (SMS)
# ✅ Enable Authenticator App (TOTP)
# ✅ Enable WebAuthn (Hardware keys)

# Or via API
curl -X PATCH https://api.supabase.com/v1/projects/spdtwktxdalcfigzeqrz/config/auth \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "MFA_ENABLED": true,
    "MFA_MAX_ENROLLED_FACTORS": 10,
    "PHONE_ENABLED": true,
    "PHONE_MFA_ENABLED": true,
    "TOTP_ENABLED": true,
    "WEBAUTHN_ENABLED": true
  }'
```

---

## 📋 Execution Plan

### Sprint 1 Week 1 - Critical Remediation (4 days)

**Day 1 (8 hours)**: Tier 1 Critical Tables
- [ ] **Morning (4h)**: Task Management (10 tables) + Worker System (2 tables)
- [ ] **Afternoon (4h)**: Email (1 table) + GitHub (1 table) + Expense (1 table) + Testing

**Day 2 (8 hours)**: Tier 2 Superset User & Permission Tables
- [ ] **Morning (4h)**: User tables (ab_user, ab_role, ab_permission, etc.) - 17 tables
- [ ] **Afternoon (4h)**: Testing + Validation + Superset UI verification

**Day 3 (8 hours)**: Tier 2 Superset Dashboard & Database Tables
- [ ] **Morning (4h)**: Dashboard tables (dashboards, slices, dashboard_slices) - 20 tables
- [ ] **Afternoon (4h)**: Database connection tables (dbs, tables, etc.) - 8 tables

**Day 4 (8 hours)**: Function Security + Extensions + Auth Config
- [ ] **Morning (4h)**: Fix 47 functions with mutable search_path
- [ ] **Afternoon (2h)**: Move 4 extensions to extensions schema
- [ ] **Afternoon (2h)**: Enable auth security features (password protection, MFA)

---

## 🧪 Testing & Validation

### Pre-Deployment Validation

```bash
# 1. Test RLS policies in staging environment
psql "$POSTGRES_URL" << EOF
-- Set role to test user
SET ROLE authenticated;
SET request.jwt.claims.company_id TO '550e8400-e29b-41d4-a716-446655440001';

-- Verify isolation (should only see company 1 tasks)
SELECT COUNT(*) FROM task_queue;
SELECT DISTINCT company_id FROM task_queue;

-- Verify service role bypass
SET ROLE service_role;
SELECT COUNT(*) FROM task_queue;  -- Should see ALL tasks

-- Reset
RESET ROLE;
EOF

# 2. Validate all 59 tables have RLS enabled
psql "$POSTGRES_URL" -c "
SELECT schemaname, tablename 
FROM pg_tables 
WHERE schemaname = 'public' 
  AND tablename NOT IN (
    SELECT tablename FROM pg_tables t
    JOIN pg_class c ON t.tablename = c.relname
    WHERE c.relrowsecurity = true
  )
ORDER BY tablename;
"
# Expected: 0 rows (all tables have RLS)

# 3. Validate function search_path fixed
psql "$POSTGRES_URL" -c "
SELECT n.nspname || '.' || p.proname AS function_name
FROM pg_proc p
JOIN pg_namespace n ON p.pronamespace = n.oid
WHERE n.nspname IN ('public', 'ops', 'agent', 'core')
  AND p.prosecdef = false
  AND NOT EXISTS (
    SELECT 1 FROM pg_proc_config pc
    WHERE pc.proname = p.proname
      AND pc.proconfig @> ARRAY['search_path']
  );
"
# Expected: 0 rows (all functions have fixed search_path)

# 4. Run Supabase linter again
# Expected: 0 ERROR, 0 WARN issues
```

---

## 📊 Success Criteria

### Immediate (End of Day 4)
- [ ] **0 ERROR level issues** (down from 59)
- [ ] **0 WARN level issues** (down from 51)
- [ ] **All 59 tables have RLS enabled**
- [ ] **All 47 functions have fixed search_path**
- [ ] **All 4 extensions moved to extensions schema**
- [ ] **Auth security features enabled** (password protection, MFA)

### Post-Deployment (Week 2)
- [ ] **No access violations** in production logs
- [ ] **Multi-agency isolation verified** (8 agencies: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- [ ] **Superset dashboards functional** with RLS
- [ ] **Performance impact <5%** (RLS overhead acceptable)
- [ ] **Zero unauthorized data access** incidents

---

## 🚨 Risk Mitigation

### Rollback Plan
```sql
-- Emergency rollback: Disable RLS on all tables
DO $$
DECLARE
  r RECORD;
BEGIN
  FOR r IN 
    SELECT schemaname, tablename 
    FROM pg_tables 
    WHERE schemaname = 'public'
  LOOP
    EXECUTE format('ALTER TABLE %I.%I DISABLE ROW LEVEL SECURITY', r.schemaname, r.tablename);
  END LOOP;
END $$;
```

### Deployment Strategy
1. **Staging First**: Deploy to staging environment, run full test suite
2. **Gradual Rollout**: Enable RLS table-by-table with monitoring
3. **Traffic Shadowing**: Monitor RLS policy evaluation overhead
4. **Kill Switch**: Prepared rollback script if performance issues arise

---

## 📖 Related Documentation

- **Security Audit Report**: PR #100 - Security Audit
- **Comprehensive Review**: `COMPREHENSIVE_CODEBASE_REVIEW_2025-11-04.md`
- **Supabase RLS Guide**: https://supabase.com/docs/guides/database/postgres/row-level-security
- **Function Security**: https://supabase.com/docs/guides/database/database-linter?lint=0011_function_search_path_mutable

---

**Report Generated**: November 4, 2025  
**Next Review**: Daily during Sprint 1 Week 1  
**Contact**: jgtolentino@insightpulse.ai

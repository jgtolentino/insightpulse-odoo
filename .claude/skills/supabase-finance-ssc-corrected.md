# Supabase Finance SSC Orchestrator Skill (CORRECTED)

**Version:** 2.0.0 (Architecture Corrected)
**Project:** InsightPulse AI (spdtwktxdalcfigzeqrz)
**Purpose:** Production-grade Finance Shared Service Center operations with correct multi-tenant architecture

---

## 🎯 Architecture Overview

**CRITICAL:** This skill extends the existing SaaS Core Schema with Finance SSC-specific tables.

### **Correct Multi-Tenant Structure:**

```
TBWA Finance SSC (1 Tenant)
├── 8 Projects (Agencies):
│   ├── RIM Agency
│   ├── CKVC Agency
│   ├── BOM Agency
│   ├── JPAL Agency
│   ├── JLI Agency
│   ├── JAP Agency
│   ├── LAS Agency
│   └── RMQB Agency
├── Finance SSC Tables (this skill):
│   ├── month_end_tasks (tenant_id + project_id)
│   ├── bir_filing_schedule (tenant_id + project_id)
│   ├── atp_tracking (tenant_id + project_id)
│   └── compliance_audit_log (tenant_id)
└── Existing SaaS Core Tables:
    ├── tenants (from 003_saas_core_schema.sql)
    ├── projects (from 003_saas_core_schema.sql)
    ├── users (from 003_saas_core_schema.sql)
    ├── workflows (from 003_saas_core_schema.sql)
    └── ... (50+ other tables)
```

**Key Principles:**
- ✅ Reuse existing `tenants` and `projects` tables (DON'T create `agencies` table!)
- ✅ All Finance SSC tables reference `tenant_id` and `project_id`
- ✅ RLS policies use existing `auth.user_tenant_ids()` helper
- ✅ Cross-agency consolidation works (all under one tenant)
- ✅ Future customers get their own isolated tenant

---

## 📋 Component Architecture

### 1. Local Development Environment

**Setup Command:**
```bash
# Initialize Supabase locally
npx supabase init

# Start local stack (Postgres + Auth + Storage + Edge Functions)
npx supabase start

# Access local dashboard
open http://localhost:54323
```

**Local Services:**
- **Postgres:** localhost:54322 (direct connection)
- **API Gateway:** localhost:54321
- **Studio Dashboard:** localhost:54323
- **Inbucket (Email testing):** localhost:54324

---

### 2. Database Schema for Finance SSC

**Prerequisites:**
- `003_saas_core_schema.sql` must be applied first!
- This migration extends the existing schema

**Migration File:** `004_finance_ssc_extensions.sql`

```sql
-- =============================================================================
-- Finance SSC Extensions to SaaS Core Schema
-- Extends 003_saas_core_schema.sql with Finance SSC-specific tables
-- =============================================================================

-- Enable required extensions (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_cron";
CREATE EXTENSION IF NOT EXISTS "pg_net"; -- For HTTP requests from cron

-- =============================================================================
-- MONTH-END CLOSING TASKS
-- =============================================================================

CREATE TABLE month_end_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  period TEXT NOT NULL, -- 'January 2025', 'February 2025'
  task_name TEXT NOT NULL,
  task_type TEXT NOT NULL CHECK (task_type IN (
    'journal_entry',
    'reconciliation',
    'trial_balance',
    'consolidation',
    'reporting',
    'review'
  )),
  due_date DATE NOT NULL,
  priority TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'critical')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN (
    'pending',
    'in_progress',
    'review',
    'completed',
    'blocked'
  )),
  assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
  completed_at TIMESTAMPTZ,
  completed_by UUID REFERENCES users(id),
  notes TEXT,
  external_id TEXT, -- Notion page ID for sync
  external_url TEXT, -- Notion page URL
  metadata JSONB, -- Additional flexible data
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT month_end_tasks_project_belongs_to_tenant
    FOREIGN KEY (tenant_id, project_id)
    REFERENCES projects(tenant_id, id)
);

-- Indexes for common queries
CREATE INDEX idx_month_end_tasks_tenant ON month_end_tasks(tenant_id);
CREATE INDEX idx_month_end_tasks_project ON month_end_tasks(project_id);
CREATE INDEX idx_month_end_tasks_status ON month_end_tasks(status);
CREATE INDEX idx_month_end_tasks_due_date ON month_end_tasks(due_date);
CREATE INDEX idx_month_end_tasks_period ON month_end_tasks(period);
CREATE INDEX idx_month_end_tasks_assigned ON month_end_tasks(assigned_to);

COMMENT ON TABLE month_end_tasks IS 'Month-end closing tasks for each agency (project) under TBWA Finance SSC tenant';
COMMENT ON COLUMN month_end_tasks.project_id IS 'References agency project (RIM, CKVC, BOM, etc.)';

-- =============================================================================
-- BIR TAX FILING SCHEDULE
-- =============================================================================

CREATE TABLE bir_filing_schedule (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  form_type TEXT NOT NULL CHECK (form_type IN (
    '1601-C',  -- Monthly withholding tax
    '2550Q',   -- Quarterly VAT
    '1702-RT', -- Annual income tax return
    '1702-EX', -- Annual ITR for exempt
    '0619-E',  -- Monthly remittance (EWT)
    '0619-F',  -- Monthly remittance (VAT)
    '2307'     -- Certificate of withholding
  )),
  filing_period TEXT NOT NULL, -- 'January 2025', 'Q1 2025'
  due_date DATE NOT NULL,
  filing_status TEXT NOT NULL DEFAULT 'pending' CHECK (filing_status IN (
    'pending',
    'prepared',
    'filed',
    'late',
    'amended'
  )),
  filed_date DATE,
  filed_by UUID REFERENCES users(id),
  confirmation_number TEXT,
  amount_paid NUMERIC(12, 2),
  notes TEXT,
  external_id TEXT, -- Notion page ID
  external_url TEXT, -- Notion page URL
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT bir_filing_project_belongs_to_tenant
    FOREIGN KEY (tenant_id, project_id)
    REFERENCES projects(tenant_id, id)
);

-- Indexes for BIR queries
CREATE INDEX idx_bir_filing_tenant ON bir_filing_schedule(tenant_id);
CREATE INDEX idx_bir_filing_project ON bir_filing_schedule(project_id);
CREATE INDEX idx_bir_filing_status ON bir_filing_schedule(filing_status);
CREATE INDEX idx_bir_filing_due_date ON bir_filing_schedule(due_date);
CREATE INDEX idx_bir_filing_form_type ON bir_filing_schedule(form_type);
CREATE INDEX idx_bir_filing_period ON bir_filing_schedule(filing_period);

COMMENT ON TABLE bir_filing_schedule IS 'BIR tax filing schedules for each agency (project)';

-- =============================================================================
-- ATP (AUTHORIZATION TO PRINT) TRACKING
-- =============================================================================

CREATE TABLE atp_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  atp_number TEXT NOT NULL,
  document_type TEXT NOT NULL, -- 'Sales Invoice', 'Official Receipt'
  issue_date DATE NOT NULL,
  expiry_date DATE NOT NULL,
  status TEXT NOT NULL DEFAULT 'active' CHECK (status IN (
    'active',
    'expiring_soon',
    'expired',
    'renewed'
  )),
  renewal_date DATE,
  notes TEXT,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT atp_project_belongs_to_tenant
    FOREIGN KEY (tenant_id, project_id)
    REFERENCES projects(tenant_id, id),
  UNIQUE(tenant_id, project_id, atp_number)
);

-- Indexes for ATP queries
CREATE INDEX idx_atp_tenant ON atp_tracking(tenant_id);
CREATE INDEX idx_atp_project ON atp_tracking(project_id);
CREATE INDEX idx_atp_status ON atp_tracking(status);
CREATE INDEX idx_atp_expiry_date ON atp_tracking(expiry_date);

COMMENT ON TABLE atp_tracking IS 'BIR Authorization to Print tracking for each agency';

-- =============================================================================
-- COMPLIANCE AUDIT LOG (Tenant-level, not per-project)
-- =============================================================================

CREATE TABLE compliance_audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id), -- Optional: can be tenant-level event
  table_name TEXT NOT NULL,
  record_id UUID NOT NULL,
  action TEXT NOT NULL CHECK (action IN ('INSERT', 'UPDATE', 'DELETE')),
  old_data JSONB,
  new_data JSONB,
  changed_by UUID REFERENCES users(id),
  ip_address INET,
  user_agent TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for audit queries
CREATE INDEX idx_compliance_audit_tenant ON compliance_audit_log(tenant_id);
CREATE INDEX idx_compliance_audit_project ON compliance_audit_log(project_id);
CREATE INDEX idx_compliance_audit_table ON compliance_audit_log(table_name);
CREATE INDEX idx_compliance_audit_record ON compliance_audit_log(record_id);
CREATE INDEX idx_compliance_audit_created ON compliance_audit_log(created_at);
CREATE INDEX idx_compliance_audit_user ON compliance_audit_log(changed_by);

COMMENT ON TABLE compliance_audit_log IS 'Audit trail for BIR compliance (10-year retention)';

-- =============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- =============================================================================

-- Enable RLS on all Finance SSC tables
ALTER TABLE month_end_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE bir_filing_schedule ENABLE ROW LEVEL SECURITY;
ALTER TABLE atp_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_audit_log ENABLE ROW LEVEL SECURITY;

-- ✅ Month-End Tasks Policies (use existing helper functions!)
CREATE POLICY "Users can view month-end tasks for their tenant"
  ON month_end_tasks FOR SELECT
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY "Users can insert month-end tasks for their tenant"
  ON month_end_tasks FOR INSERT
  WITH CHECK (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY "Users can update month-end tasks for their tenant"
  ON month_end_tasks FOR UPDATE
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY "Users can delete month-end tasks for their tenant"
  ON month_end_tasks FOR DELETE
  USING (
    tenant_id = ANY(auth.user_tenant_ids())
    AND auth.user_has_permission('task.delete', tenant_id)
  );

-- ✅ BIR Filing Policies (same pattern)
CREATE POLICY "Users can view BIR filings for their tenant"
  ON bir_filing_schedule FOR SELECT
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY "Users can manage BIR filings for their tenant"
  ON bir_filing_schedule FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- ✅ ATP Policies (same pattern)
CREATE POLICY "Users can view ATP for their tenant"
  ON atp_tracking FOR SELECT
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY "Users can manage ATP for their tenant"
  ON atp_tracking FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- ✅ Audit Log Policies (read-only for most users)
CREATE POLICY "Users can view audit logs for their tenant"
  ON compliance_audit_log FOR SELECT
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY "System can insert audit logs"
  ON compliance_audit_log FOR INSERT
  WITH CHECK (true); -- System can always log

-- =============================================================================
-- FUNCTIONS FOR AUTOMATION
-- =============================================================================

-- Function: Generate month-end tasks for all projects in a tenant
CREATE OR REPLACE FUNCTION generate_month_end_tasks(
  p_tenant_id UUID,
  p_period TEXT,
  p_project_ids UUID[] DEFAULT NULL -- If NULL, generate for all projects
)
RETURNS TABLE (
  task_id UUID,
  project_name TEXT,
  task_name TEXT,
  due_date DATE
) AS $$
DECLARE
  v_project_id UUID;
  v_project_name TEXT;
  v_base_date DATE;
  v_next_month_start DATE;
BEGIN
  -- Parse period to get base date (e.g., "January 2025" -> 2025-01-01)
  v_base_date := to_date(p_period || ' 01', 'FMMonth YYYY DD');
  v_next_month_start := v_base_date + INTERVAL '1 month';

  -- Get project IDs (all if not specified)
  IF p_project_ids IS NULL THEN
    p_project_ids := ARRAY(
      SELECT id FROM projects WHERE tenant_id = p_tenant_id
    );
  END IF;

  -- Loop through projects
  FOREACH v_project_id IN ARRAY p_project_ids LOOP
    -- Get project name
    SELECT name INTO v_project_name FROM projects WHERE id = v_project_id;

    -- Task 1: Review Journal Entries (due 10th of next month)
    INSERT INTO month_end_tasks (
      tenant_id, project_id, period, task_name, task_type,
      due_date, priority, status
    )
    VALUES (
      p_tenant_id, v_project_id, p_period,
      'Review Journal Entries', 'journal_entry',
      v_next_month_start + 9, -- 10th
      'high', 'pending'
    )
    ON CONFLICT DO NOTHING
    RETURNING id, v_project_name, task_name, due_date
    INTO task_id, project_name, task_name, due_date;

    IF FOUND THEN RETURN NEXT; END IF;

    -- Task 2: Bank Reconciliation (due 15th of next month)
    INSERT INTO month_end_tasks (
      tenant_id, project_id, period, task_name, task_type,
      due_date, priority, status
    )
    VALUES (
      p_tenant_id, v_project_id, p_period,
      'Complete Bank Reconciliation', 'reconciliation',
      v_next_month_start + 14, -- 15th
      'high', 'pending'
    )
    ON CONFLICT DO NOTHING
    RETURNING id, v_project_name, task_name, due_date
    INTO task_id, project_name, task_name, due_date;

    IF FOUND THEN RETURN NEXT; END IF;

    -- Task 3: Trial Balance (due 20th of next month)
    INSERT INTO month_end_tasks (
      tenant_id, project_id, period, task_name, task_type,
      due_date, priority, status
    )
    VALUES (
      p_tenant_id, v_project_id, p_period,
      'Generate Trial Balance', 'trial_balance',
      v_next_month_start + 19, -- 20th
      'critical', 'pending'
    )
    ON CONFLICT DO NOTHING
    RETURNING id, v_project_name, task_name, due_date
    INTO task_id, project_name, task_name, due_date;

    IF FOUND THEN RETURN NEXT; END IF;
  END LOOP;

  -- Task 4: Consolidation (tenant-level, after all agencies done)
  INSERT INTO month_end_tasks (
    tenant_id, project_id, period, task_name, task_type,
    due_date, priority, status
  )
  VALUES (
    p_tenant_id, p_project_ids[1], p_period, -- Assign to first project
    'Consolidate All Agencies', 'consolidation',
    v_next_month_start + 24, -- 25th
    'critical', 'pending'
  )
  ON CONFLICT DO NOTHING
  RETURNING id, 'Consolidated', task_name, due_date
  INTO task_id, project_name, task_name, due_date;

  IF FOUND THEN RETURN NEXT; END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION generate_month_end_tasks IS
  'Generate month-end closing tasks for all projects (agencies) in a tenant';

-- Function: Check upcoming BIR deadlines across all projects
CREATE OR REPLACE FUNCTION get_upcoming_bir_deadlines(
  p_tenant_id UUID,
  days_ahead INT DEFAULT 7
)
RETURNS TABLE (
  filing_id UUID,
  project_name TEXT,
  form_type TEXT,
  due_date DATE,
  days_remaining INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    bf.id AS filing_id,
    p.name AS project_name,
    bf.form_type,
    bf.due_date,
    (bf.due_date - CURRENT_DATE)::INT as days_remaining
  FROM bir_filing_schedule bf
  JOIN projects p ON bf.project_id = p.id
  WHERE bf.tenant_id = p_tenant_id
    AND bf.filing_status = 'pending'
    AND bf.due_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + days_ahead)
  ORDER BY bf.due_date ASC, p.name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION get_upcoming_bir_deadlines IS
  'Get upcoming BIR filing deadlines for all projects in a tenant';

-- Function: Check expiring ATPs across all projects
CREATE OR REPLACE FUNCTION check_expiring_atps(
  p_tenant_id UUID,
  days_ahead INT DEFAULT 30
)
RETURNS TABLE (
  atp_id UUID,
  project_name TEXT,
  atp_number TEXT,
  expiry_date DATE,
  days_remaining INT
) AS $$
BEGIN
  RETURN QUERY
  SELECT
    atp.id AS atp_id,
    p.name AS project_name,
    atp.atp_number,
    atp.expiry_date,
    (atp.expiry_date - CURRENT_DATE)::INT as days_remaining
  FROM atp_tracking atp
  JOIN projects p ON atp.project_id = p.id
  WHERE atp.tenant_id = p_tenant_id
    AND atp.status = 'active'
    AND atp.expiry_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + days_ahead)
  ORDER BY atp.expiry_date ASC, p.name;

  -- Update status to 'expiring_soon'
  UPDATE atp_tracking
  SET status = 'expiring_soon',
      updated_at = NOW()
  WHERE tenant_id = p_tenant_id
    AND status = 'active'
    AND expiry_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + days_ahead);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- TRIGGERS FOR AUDIT LOGGING
-- =============================================================================

-- Generic audit trigger function for Finance SSC tables
CREATE OR REPLACE FUNCTION finance_ssc_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'DELETE' THEN
    INSERT INTO compliance_audit_log (
      tenant_id, project_id, table_name, record_id,
      action, old_data, changed_by, ip_address
    )
    VALUES (
      OLD.tenant_id,
      OLD.project_id,
      TG_TABLE_NAME,
      OLD.id,
      TG_OP,
      row_to_json(OLD),
      auth.uid(),
      inet_client_addr()
    );
    RETURN OLD;
  ELSIF TG_OP = 'UPDATE' THEN
    INSERT INTO compliance_audit_log (
      tenant_id, project_id, table_name, record_id,
      action, old_data, new_data, changed_by, ip_address
    )
    VALUES (
      NEW.tenant_id,
      NEW.project_id,
      TG_TABLE_NAME,
      NEW.id,
      TG_OP,
      row_to_json(OLD),
      row_to_json(NEW),
      auth.uid(),
      inet_client_addr()
    );
    RETURN NEW;
  ELSIF TG_OP = 'INSERT' THEN
    INSERT INTO compliance_audit_log (
      tenant_id, project_id, table_name, record_id,
      action, new_data, changed_by, ip_address
    )
    VALUES (
      NEW.tenant_id,
      NEW.project_id,
      TG_TABLE_NAME,
      NEW.id,
      TG_OP,
      row_to_json(NEW),
      auth.uid(),
      inet_client_addr()
    );
    RETURN NEW;
  END IF;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Attach audit triggers to Finance SSC tables
CREATE TRIGGER month_end_tasks_audit
  AFTER INSERT OR UPDATE OR DELETE ON month_end_tasks
  FOR EACH ROW EXECUTE FUNCTION finance_ssc_audit_trigger();

CREATE TRIGGER bir_filing_audit
  AFTER INSERT OR UPDATE OR DELETE ON bir_filing_schedule
  FOR EACH ROW EXECUTE FUNCTION finance_ssc_audit_trigger();

CREATE TRIGGER atp_tracking_audit
  AFTER INSERT OR UPDATE OR DELETE ON atp_tracking
  FOR EACH ROW EXECUTE FUNCTION finance_ssc_audit_trigger();

-- =============================================================================
-- UPDATED_AT TRIGGER
-- =============================================================================

-- Attach to Finance SSC tables (reuse existing function from core schema)
CREATE TRIGGER month_end_tasks_updated_at
  BEFORE UPDATE ON month_end_tasks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER bir_filing_updated_at
  BEFORE UPDATE ON bir_filing_schedule
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER atp_tracking_updated_at
  BEFORE UPDATE ON atp_tracking
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- SUMMARY
-- =============================================================================

COMMENT ON SCHEMA public IS 'InsightPulse Finance SSC - Multi-tenant extensions applied';
```

---

### 3. Edge Functions Setup

**Function 1: Month-End Kickoff**

File: `supabase/functions/month-end-kickoff/index.ts`

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const { tenant_slug, period, project_ids } = await req.json()

    // Validate inputs
    if (!tenant_slug || !period) {
      throw new Error('Invalid input: tenant_slug and period required')
    }

    // Get tenant ID from slug
    const { data: tenant, error: tenantError } = await supabaseClient
      .from('tenants')
      .select('id')
      .eq('slug', tenant_slug)
      .single()

    if (tenantError) throw new Error(`Tenant not found: ${tenant_slug}`)

    // Call database function to generate tasks
    const { data, error } = await supabaseClient
      .rpc('generate_month_end_tasks', {
        p_tenant_id: tenant.id,
        p_period: period,
        p_project_ids: project_ids || null // Generate for all projects if not specified
      })

    if (error) throw error

    console.log(`Generated ${data.length} month-end tasks for ${tenant_slug} - ${period}`)

    return new Response(
      JSON.stringify({
        success: true,
        tenant: tenant_slug,
        period,
        tasks_created: data.length,
        tasks: data
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      },
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      },
    )
  }
})
```

**Function 2: BIR Deadline Reminder**

File: `supabase/functions/bir-deadline-reminder/index.ts`

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const { tenant_slug } = await req.json()

    // Get tenant ID
    const { data: tenant, error: tenantError } = await supabaseClient
      .from('tenants')
      .select('id')
      .eq('slug', tenant_slug || 'tbwa-finance-ssc')
      .single()

    if (tenantError) throw tenantError

    // Get upcoming deadlines (next 7 days)
    const { data: deadlines, error } = await supabaseClient
      .rpc('get_upcoming_bir_deadlines', {
        p_tenant_id: tenant.id,
        days_ahead: 7
      })

    if (error) throw error

    console.log(`Found ${deadlines.length} upcoming BIR deadlines for ${tenant_slug}`)

    // Group by project for notification
    const byProject = deadlines.reduce((acc, d) => {
      if (!acc[d.project_name]) acc[d.project_name] = []
      acc[d.project_name].push(d)
      return acc
    }, {})

    // Log reminders (in production, send emails/Slack)
    for (const [project, filings] of Object.entries(byProject)) {
      console.log(`⚠️  ${project}: ${filings.length} filing(s) due`)
      for (const filing of filings) {
        console.log(`   - ${filing.form_type} due in ${filing.days_remaining} days`)
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        tenant: tenant_slug,
        deadlines_count: deadlines.length,
        by_project: byProject,
        deadlines
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      },
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      },
    )
  }
})
```

**Function 3: ATP Expiry Monitor**

File: `supabase/functions/atp-expiry-monitor/index.ts`

```typescript
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    const { tenant_slug } = await req.json()

    // Get tenant ID
    const { data: tenant, error: tenantError } = await supabaseClient
      .from('tenants')
      .select('id')
      .eq('slug', tenant_slug || 'tbwa-finance-ssc')
      .single()

    if (tenantError) throw tenantError

    // Check ATPs expiring in next 30 days
    const { data: expiring, error } = await supabaseClient
      .rpc('check_expiring_atps', {
        p_tenant_id: tenant.id,
        days_ahead: 30
      })

    if (error) throw error

    console.log(`Found ${expiring.length} ATPs expiring soon for ${tenant_slug}`)

    // Group by project
    const byProject = expiring.reduce((acc, atp) => {
      if (!acc[atp.project_name]) acc[atp.project_name] = []
      acc[atp.project_name].push(atp)
      return acc
    }, {})

    for (const [project, atps] of Object.entries(byProject)) {
      console.log(`🔔 ${project}: ${atps.length} ATP(s) expiring`)
      for (const atp of atps) {
        console.log(`   - ${atp.atp_number} expires in ${atp.days_remaining} days`)
      }
    }

    return new Response(
      JSON.stringify({
        success: true,
        tenant: tenant_slug,
        expiring_count: expiring.length,
        by_project: byProject,
        expiring_atps: expiring
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      },
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ error: error.message }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 400,
      },
    )
  }
})
```

---

### 4. Cron Jobs Setup

**Migration File:** `005_finance_ssc_cron_jobs.sql`

```sql
-- =============================================================================
-- Finance SSC Cron Jobs
-- Scheduled automation for TBWA Finance SSC tenant
-- =============================================================================

-- IMPORTANT: Replace with your actual Supabase project URL and service key!

-- ============================================
-- CRON JOB 1: Daily BIR Deadline Check
-- ============================================
SELECT cron.schedule(
  'tbwa-bir-deadline-reminder-daily',
  '0 8 * * *', -- Every day at 8 AM Manila time
  $$
  SELECT
    net.http_post(
      url := 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/bir-deadline-reminder',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key', true)
      ),
      body := jsonb_build_object(
        'tenant_slug', 'tbwa-finance-ssc'
      )
    ) AS request_id;
  $$
);

-- ============================================
-- CRON JOB 2: Weekly ATP Expiry Check
-- ============================================
SELECT cron.schedule(
  'tbwa-atp-expiry-monitor-weekly',
  '0 9 * * 1', -- Every Monday at 9 AM
  $$
  SELECT
    net.http_post(
      url := 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/atp-expiry-monitor',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key', true)
      ),
      body := jsonb_build_object(
        'tenant_slug', 'tbwa-finance-ssc'
      )
    ) AS request_id;
  $$
);

-- ============================================
-- CRON JOB 3: Monthly Month-End Kickoff
-- ============================================
SELECT cron.schedule(
  'tbwa-month-end-kickoff-monthly',
  '0 6 1 * *', -- 1st of each month at 6 AM
  $$
  SELECT
    net.http_post(
      url := 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/month-end-kickoff',
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'Authorization', 'Bearer ' || current_setting('app.settings.service_role_key', true)
      ),
      body := jsonb_build_object(
        'tenant_slug', 'tbwa-finance-ssc',
        'period', to_char(CURRENT_DATE, 'FMMonth YYYY'),
        'project_ids', NULL -- Generate for all projects
      )
    ) AS request_id;
  $$
);

-- ============================================
-- HELPFUL QUERIES FOR MONITORING
-- ============================================

-- View all scheduled jobs
-- SELECT * FROM cron.job;

-- View recent job runs
-- SELECT
--   jobid,
--   runid,
--   job_pid,
--   database,
--   username,
--   command,
--   status,
--   return_message,
--   start_time,
--   end_time
-- FROM cron.job_run_details
-- ORDER BY start_time DESC
-- LIMIT 20;

-- Check for failed jobs
-- SELECT * FROM cron.job_run_details
-- WHERE status = 'failed'
-- ORDER BY start_time DESC;
```

---

## 🚀 Deployment Workflow

### Step 1: Apply Core Schema (Prerequisites)
```bash
# Ensure 003_saas_core_schema.sql is applied first!
psql $POSTGRES_URL -f supabase/migrations/003_saas_core_schema.sql

# Run the corrected seed script
psql $POSTGRES_URL -f scripts/seed_agencies.sql
```

### Step 2: Apply Finance SSC Extensions
```bash
# Apply Finance SSC tables
psql $POSTGRES_URL -f supabase/migrations/004_finance_ssc_extensions.sql

# Apply cron jobs
psql $POSTGRES_URL -f supabase/migrations/005_finance_ssc_cron_jobs.sql
```

### Step 3: Deploy Edge Functions
```bash
# Deploy all functions
supabase functions deploy month-end-kickoff
supabase functions deploy bir-deadline-reminder
supabase functions deploy atp-expiry-monitor
```

### Step 4: Test the Integration
```bash
# Test month-end kickoff
curl -i --location --request POST \
  'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/month-end-kickoff' \
  --header 'Authorization: Bearer YOUR_ANON_KEY' \
  --header 'Content-Type: application/json' \
  --data '{
    "tenant_slug": "tbwa-finance-ssc",
    "period": "November 2025"
  }'

# Test BIR deadline reminder
curl -i --location --request POST \
  'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/bir-deadline-reminder' \
  --header 'Authorization: Bearer YOUR_ANON_KEY' \
  --header 'Content-Type: application/json' \
  --data '{"tenant_slug": "tbwa-finance-ssc"}'
```

---

## 📊 Example Queries

### View Month-End Progress (Cross-Agency)
```sql
SELECT
  p.name AS agency,
  met.status,
  COUNT(*) as task_count,
  COUNT(*) FILTER (WHERE met.due_date < CURRENT_DATE) as overdue_count
FROM month_end_tasks met
JOIN projects p ON met.project_id = p.id
WHERE met.tenant_id = (SELECT id FROM tenants WHERE slug = 'tbwa-finance-ssc')
  AND met.period = 'November 2025'
GROUP BY p.name, met.status
ORDER BY p.name, met.status;
```

### BIR Compliance Dashboard
```sql
SELECT
  p.name AS agency,
  bf.form_type,
  bf.filing_status,
  bf.due_date,
  (bf.due_date - CURRENT_DATE) as days_remaining
FROM bir_filing_schedule bf
JOIN projects p ON bf.project_id = p.id
WHERE bf.tenant_id = (SELECT id FROM tenants WHERE slug = 'tbwa-finance-ssc')
  AND bf.filing_status = 'pending'
  AND bf.due_date >= CURRENT_DATE
ORDER BY bf.due_date, p.name;
```

### Audit Trail (10-Year Retention for BIR)
```sql
SELECT
  p.name AS agency,
  cal.table_name,
  cal.action,
  u.full_name AS changed_by,
  cal.created_at
FROM compliance_audit_log cal
LEFT JOIN projects p ON cal.project_id = p.id
LEFT JOIN users u ON cal.changed_by = u.id
WHERE cal.tenant_id = (SELECT id FROM tenants WHERE slug = 'tbwa-finance-ssc')
  AND cal.created_at >= NOW() - INTERVAL '30 days'
ORDER BY cal.created_at DESC
LIMIT 100;
```

---

## ✅ Verification Checklist

- [ ] Core schema (003_saas_core_schema.sql) applied
- [ ] Seed script (seed_agencies.sql) executed - 1 tenant, 8 projects created
- [ ] Finance SSC extensions (004_finance_ssc_extensions.sql) applied
- [ ] Cron jobs (005_finance_ssc_cron_jobs.sql) scheduled
- [ ] Edge Functions deployed
- [ ] RLS policies active (users only see their tenant's data)
- [ ] Month-end tasks generated successfully
- [ ] BIR deadline reminders working
- [ ] ATP expiry monitoring active
- [ ] Audit logging capturing all changes

---

## 🎯 Key Differences from Original (Wrong) Version

| Aspect | ❌ Wrong (v1.0) | ✅ Correct (v2.0) |
|--------|----------------|-------------------|
| **Structure** | Separate `agencies` table | Reuse `tenants` + `projects` |
| **Foreign Keys** | `agency_code TEXT` | `tenant_id UUID` + `project_id UUID` |
| **RLS Policies** | Custom agency logic | Use `auth.user_tenant_ids()` |
| **Functions** | Accept `agency_codes[]` | Accept `tenant_id` + `project_ids[]` |
| **Consolidation** | Not possible | Easy cross-agency queries |
| **Scalability** | Limited to 8 agencies | Unlimited projects per tenant |
| **Multi-Customer** | Not supported | Add new tenants for new customers |

---

## 💰 Cost Analysis

**Self-Hosted Supabase:**
- No Supabase Cloud fees: **$25/month saved**
- Runs on existing DigitalOcean: **$0 additional**
- **Total savings: $300/year**

---

## 📚 Related Documentation

- **SaaS Core Schema:** `supabase/migrations/003_saas_core_schema.sql`
- **Corrected Seed Script:** `scripts/seed_agencies.sql`
- **Architecture Fix Commit:** `7225d25`
- **Notion Integration:** `docs/NOTION_INTEGRATION_MAPPING.md`
- **Migration Strategy:** `docs/FINANCE_SSC_MIGRATION_STRATEGY.md`

---

**Version:** 2.0.0 (Corrected)
**Last Updated:** November 6, 2025
**Maintained By:** Jake Tolentino (@jgtolentino)

**⚠️ IMPORTANT:** Always use this corrected version. The original v1.0 skill with `agencies` table is DEPRECATED and should not be used.

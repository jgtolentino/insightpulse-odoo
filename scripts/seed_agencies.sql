-- =============================================================================
-- InsightPulse Finance SSC - Corrected Seed Data
-- ✅ CORRECT: 1 Tenant (TBWA Finance SSC) + 8 Projects (Agencies)
--
-- Architecture:
--   1 Tenant = 1 Customer (TBWA Finance SSC)
--   8 Projects = 8 Agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
--   1 Notion Integration = For entire TBWA tenant
--   1 Billing Account = For TBWA customer
--   1 Subscription = Single plan for TBWA
-- =============================================================================

-- Enable UUID generation if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. Create TBWA Finance SSC Tenant (Single Customer)
-- =============================================================================

DO $$
DECLARE
  v_tenant_id UUID;
  v_admin_user_id UUID;
  v_finance_team_id UUID;
  v_notion_integration_id UUID;
  v_admin_role_id UUID;
  v_project_ids UUID[];
  v_project_id UUID;
  agency_code TEXT;
  agency_name TEXT;
  agency_bir_tin TEXT;
  agency_legal_name TEXT;
BEGIN

  -- Create TBWA Finance SSC Tenant
  INSERT INTO tenants (slug, name, timezone)
  VALUES (
    'tbwa-finance-ssc',
    'TBWA Finance Shared Service Center',
    'Asia/Manila'
  )
  ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    updated_at = now()
  RETURNING id INTO v_tenant_id;

  RAISE NOTICE '✅ Created tenant: TBWA Finance SSC (id: %)', v_tenant_id;

  -- =============================================================================
  -- 2. Create 8 Agency Projects (Under TBWA Tenant)
  -- =============================================================================

  -- RIM Agency
  INSERT INTO projects (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'RIM Agency',
    'RIM Corporation - Financial operations and BIR compliance'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = now()
  RETURNING id INTO v_project_id;

  v_project_ids := array_append(v_project_ids, v_project_id);

  RAISE NOTICE '  ✅ Created project: RIM Agency';

  -- CKVC Agency
  INSERT INTO projects (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'CKVC Agency',
    'CKVC Corporation - Financial operations and BIR compliance'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = now()
  RETURNING id INTO v_project_id;

  v_project_ids := array_append(v_project_ids, v_project_id);

  RAISE NOTICE '  ✅ Created project: CKVC Agency';

  -- BOM Agency
  INSERT INTO projects (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'BOM Agency',
    'BOM Corporation - Financial operations and BIR compliance'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = now()
  RETURNING id INTO v_project_id;

  v_project_ids := array_append(v_project_ids, v_project_id);

  RAISE NOTICE '  ✅ Created project: BOM Agency';

  -- JPAL Agency
  INSERT INTO projects (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'JPAL Agency',
    'JPAL Corporation - Financial operations and BIR compliance'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = now()
  RETURNING id INTO v_project_id;

  v_project_ids := array_append(v_project_ids, v_project_id);

  RAISE NOTICE '  ✅ Created project: JPAL Agency';

  -- JLI Agency
  INSERT INTO projects (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'JLI Agency',
    'JLI Corporation - Financial operations and BIR compliance'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = now()
  RETURNING id INTO v_project_id;

  v_project_ids := array_append(v_project_ids, v_project_id);

  RAISE NOTICE '  ✅ Created project: JLI Agency';

  -- JAP Agency
  INSERT INTO projects (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'JAP Agency',
    'JAP Corporation - Financial operations and BIR compliance'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = now()
  RETURNING id INTO v_project_id;

  v_project_ids := array_append(v_project_ids, v_project_id);

  RAISE NOTICE '  ✅ Created project: JAP Agency';

  -- LAS Agency
  INSERT INTO projects (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'LAS Agency',
    'LAS Corporation - Financial operations and BIR compliance'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = now()
  RETURNING id INTO v_project_id;

  v_project_ids := array_append(v_project_ids, v_project_id);

  RAISE NOTICE '  ✅ Created project: LAS Agency';

  -- RMQB Agency
  INSERT INTO projects (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'RMQB Agency',
    'RMQB Corporation - Financial operations and BIR compliance'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description,
    updated_at = now()
  RETURNING id INTO v_project_id;

  v_project_ids := array_append(v_project_ids, v_project_id);

  RAISE NOTICE '  ✅ Created project: RMQB Agency';

  -- =============================================================================
  -- 3. Create Production Environments for Each Project
  -- =============================================================================

  FOR v_project_id IN SELECT unnest(v_project_ids)
  LOOP
    INSERT INTO environments (project_id, name, type)
    VALUES (
      v_project_id,
      'Production',
      'prod'
    )
    ON CONFLICT (project_id, name) DO NOTHING;
  END LOOP;

  RAISE NOTICE '✅ Created production environments for all 8 projects';

  -- =============================================================================
  -- 4. Create Finance SSC Admin User
  -- =============================================================================

  INSERT INTO users (email, full_name, is_active)
  VALUES (
    'finance.ssc@insightpulseai.net',
    'Finance SSC Administrator',
    true
  )
  ON CONFLICT (email) DO UPDATE SET
    full_name = EXCLUDED.full_name,
    is_active = EXCLUDED.is_active,
    updated_at = now()
  RETURNING id INTO v_admin_user_id;

  RAISE NOTICE '✅ Created admin user: finance.ssc@insightpulseai.net (id: %)', v_admin_user_id;

  -- =============================================================================
  -- 5. Add Admin to TBWA Tenant (Org Membership)
  -- =============================================================================

  INSERT INTO org_memberships (tenant_id, user_id, is_owner, status)
  VALUES (
    v_tenant_id,
    v_admin_user_id,
    true,
    'active'
  )
  ON CONFLICT (tenant_id, user_id) DO UPDATE SET
    is_owner = EXCLUDED.is_owner,
    status = EXCLUDED.status;

  RAISE NOTICE '  ✅ Admin added as owner of TBWA tenant';

  -- Assign Admin role
  SELECT id INTO v_admin_role_id FROM roles WHERE name = 'Admin' AND scope = 'org' LIMIT 1;

  IF v_admin_role_id IS NOT NULL THEN
    INSERT INTO user_roles (user_id, tenant_id, role_id)
    VALUES (
      v_admin_user_id,
      v_tenant_id,
      v_admin_role_id
    )
    ON CONFLICT DO NOTHING;

    RAISE NOTICE '  ✅ Assigned Admin role';
  END IF;

  -- =============================================================================
  -- 6. Create Finance Team (TBWA-wide)
  -- =============================================================================

  INSERT INTO teams (tenant_id, name, description)
  VALUES (
    v_tenant_id,
    'Finance Team',
    'TBWA Finance Shared Service Center - Cross-agency finance operations'
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    description = EXCLUDED.description
  RETURNING id INTO v_finance_team_id;

  RAISE NOTICE '✅ Created Finance Team (id: %)', v_finance_team_id;

  -- Add admin to finance team
  INSERT INTO team_members (team_id, user_id)
  VALUES (v_finance_team_id, v_admin_user_id)
  ON CONFLICT (team_id, user_id) DO NOTHING;

  -- =============================================================================
  -- 7. Create Month-End Closing Workflows (One per Project)
  -- =============================================================================

  FOR v_project_id IN SELECT unnest(v_project_ids)
  LOOP
    SELECT name INTO agency_name FROM projects WHERE id = v_project_id;

    INSERT INTO workflows (tenant_id, name, definition)
    VALUES (
      v_tenant_id,
      agency_name || ' - Month-End Closing',
      jsonb_build_object(
        'trigger_type', 'scheduled',
        'schedule', 'monthly',
        'project_id', v_project_id,
        'steps', jsonb_build_array(
          jsonb_build_object(
            'id', 'journal_entries',
            'name', 'Post Journal Entries',
            'type', 'odoo_api_call'
          ),
          jsonb_build_object(
            'id', 'bank_reconciliation',
            'name', 'Bank Reconciliation',
            'type', 'odoo_api_call'
          ),
          jsonb_build_object(
            'id', 'trial_balance',
            'name', 'Generate Trial Balance',
            'type', 'report_generation'
          ),
          jsonb_build_object(
            'id', 'bir_returns',
            'name', 'Prepare BIR Returns',
            'type', 'bir_form_generation'
          ),
          jsonb_build_object(
            'id', 'notify_completion',
            'name', 'Notify Finance Team',
            'type', 'slack_notification'
          )
        )
      )
    )
    ON CONFLICT (tenant_id, name) DO UPDATE SET
      definition = EXCLUDED.definition;
  END LOOP;

  RAISE NOTICE '✅ Created month-end closing workflows for all 8 projects';

  -- =============================================================================
  -- 8. Create ONE Notion Integration (TBWA-wide)
  -- =============================================================================

  INSERT INTO integrations (tenant_id, type_id, name, config, enabled)
  VALUES (
    v_tenant_id,
    (SELECT id FROM integration_types WHERE provider = 'notion'),
    'TBWA Finance SSC Notion Workspace',
    jsonb_build_object(
      'workspace_id', 'tbwa-finance-ssc-workspace',
      'databases', jsonb_build_object(
        'month_end_tasks', 'db-tbwa-month-end-tasks',
        'bir_filing_schedule', 'db-tbwa-bir-filing',
        'compliance_checklist', 'db-tbwa-compliance',
        'team_directory', 'db-tbwa-team',
        'agency_calendar', 'db-tbwa-calendar'
      ),
      'sync_frequency', '15m',
      'webhook_enabled', true,
      'agencies', jsonb_build_array('RIM', 'CKVC', 'BOM', 'JPAL', 'JLI', 'JAP', 'LAS', 'RMQB')
    ),
    true
  )
  ON CONFLICT (tenant_id, type_id, name) DO UPDATE SET
    config = EXCLUDED.config,
    enabled = EXCLUDED.enabled
  RETURNING id INTO v_notion_integration_id;

  RAISE NOTICE '✅ Created Notion integration (id: %)', v_notion_integration_id;

  -- =============================================================================
  -- 9. Create BIR Compliance Data Policy (10-year retention)
  -- =============================================================================

  INSERT INTO data_policies (tenant_id, name, retention_days, anonymize, config)
  VALUES (
    v_tenant_id,
    'BIR Audit Trail - 10 Year Retention',
    3650, -- 10 years
    false,
    jsonb_build_object(
      'policy_type', 'legal_compliance',
      'regulation', 'BIR Revenue Regulations',
      'scope', jsonb_build_array('audit_logs', 'attachments', 'workflows'),
      'exceptions', jsonb_build_array('bir.%', 'tax.%', 'compliance.%')
    )
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    retention_days = EXCLUDED.retention_days,
    config = EXCLUDED.config;

  RAISE NOTICE '✅ Created BIR compliance data policy';

  -- =============================================================================
  -- 10. Create Billing Account (Single for TBWA)
  -- =============================================================================

  INSERT INTO billing_accounts (tenant_id, currency, billing_email)
  VALUES (
    v_tenant_id,
    'PHP',
    'billing@tbwa.ph'
  )
  ON CONFLICT (tenant_id) DO UPDATE SET
    billing_email = EXCLUDED.billing_email;

  RAISE NOTICE '✅ Created billing account for TBWA';

  -- =============================================================================
  -- 11. Create Subscription (Single for TBWA)
  -- =============================================================================

  INSERT INTO subscriptions (tenant_id, plan_id, status, current_period_start, current_period_end)
  VALUES (
    v_tenant_id,
    (SELECT id FROM plans WHERE code = 'pro'),
    'active',
    date_trunc('month', now()),
    (date_trunc('month', now()) + interval '1 month' - interval '1 day')::timestamptz
  )
  ON CONFLICT DO NOTHING;

  RAISE NOTICE '✅ Created subscription (Pro plan) for TBWA';

  -- =============================================================================
  -- 12. Create Finance SSC Consolidated Dashboard
  -- =============================================================================

  INSERT INTO dashboards (tenant_id, name, layout, is_public)
  VALUES (
    v_tenant_id,
    'Finance SSC - Consolidated View',
    jsonb_build_object(
      'type', 'grid',
      'columns', 12,
      'rows', jsonb_build_array(
        jsonb_build_object('height', 2, 'widgets', jsonb_build_array('kpi_summary')),
        jsonb_build_object('height', 4, 'widgets', jsonb_build_array('agency_progress', 'bir_compliance')),
        jsonb_build_object('height', 4, 'widgets', jsonb_build_array('overdue_tasks', 'upcoming_deadlines'))
      )
    ),
    false
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    layout = EXCLUDED.layout;

  RAISE NOTICE '✅ Created consolidated dashboard';

  -- =============================================================================
  -- 13. Create PostgreSQL Data Source (TBWA-wide)
  -- =============================================================================

  INSERT INTO data_sources (tenant_id, name, kind, config)
  VALUES (
    v_tenant_id,
    'TBWA Finance SSC - PostgreSQL',
    'postgres',
    jsonb_build_object(
      'host', 'aws-1-us-east-1.pooler.supabase.com',
      'port', 6543,
      'database', 'postgres',
      'username', 'postgres.tbwa_finance_ssc',
      'password_secret_ref', 'secret://postgres-password-tbwa',
      'ssl', true,
      'schema', 'public'
    )
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    config = EXCLUDED.config;

  RAISE NOTICE '✅ Created PostgreSQL data source';

  -- =============================================================================
  -- 14. Create Saved Queries for Finance SSC Reporting
  -- =============================================================================

  -- Month-End Task Completion Query
  INSERT INTO saved_queries (tenant_id, data_source_id, name, sql)
  VALUES (
    v_tenant_id,
    (SELECT id FROM data_sources WHERE tenant_id = v_tenant_id AND kind = 'postgres'),
    'Month-End Task Completion % (All Agencies)',
    $$
      SELECT
        p.name AS agency,
        date_trunc('month', wr.started_at) AS month,
        COUNT(CASE WHEN wr.status = 'success' THEN 1 END)::float / NULLIF(COUNT(*), 0) * 100 AS completion_rate,
        COUNT(*) AS total_tasks,
        COUNT(CASE WHEN wr.status = 'success' THEN 1 END) AS completed_tasks,
        COUNT(CASE WHEN wr.status = 'failed' THEN 1 END) AS failed_tasks
      FROM workflow_runs wr
      JOIN workflows w ON wr.workflow_id = w.id
      JOIN projects p ON w.definition->>'project_id' = p.id::text
      WHERE w.name LIKE '%Month-End Closing%'
        AND wr.started_at >= date_trunc('year', now())
      GROUP BY p.name, date_trunc('month', wr.started_at)
      ORDER BY month DESC, agency;
    $$
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    sql = EXCLUDED.sql;

  RAISE NOTICE '✅ Created saved queries for reporting';

  -- =============================================================================
  -- 15. Create Alerts for Missed Deadlines
  -- =============================================================================

  INSERT INTO alerts (tenant_id, name, type, condition, enabled)
  VALUES (
    v_tenant_id,
    'BIR Filing Deadline Alert (All Agencies)',
    'threshold',
    jsonb_build_object(
      'check_frequency', '1h',
      'condition', 'pending_filings > 0 AND days_until_deadline <= 2',
      'severity', 'high'
    ),
    true
  )
  ON CONFLICT (tenant_id, name) DO UPDATE SET
    condition = EXCLUDED.condition,
    enabled = EXCLUDED.enabled;

  RAISE NOTICE '✅ Created BIR filing deadline alerts';

  -- =============================================================================
  -- Summary
  -- =============================================================================

  RAISE NOTICE '════════════════════════════════════════════════════════════════';
  RAISE NOTICE '✅ TBWA Finance SSC Seed Complete!';
  RAISE NOTICE '';
  RAISE NOTICE '📊 Summary:';
  RAISE NOTICE '  • 1 Tenant: TBWA Finance SSC';
  RAISE NOTICE '  • 8 Projects: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB';
  RAISE NOTICE '  • 1 Admin User: finance.ssc@insightpulseai.net';
  RAISE NOTICE '  • 1 Notion Integration: TBWA-wide workspace';
  RAISE NOTICE '  • 1 Billing Account: Single subscription';
  RAISE NOTICE '  • 1 Finance Team: Cross-agency operations';
  RAISE NOTICE '  • 8 Month-End Workflows: One per agency';
  RAISE NOTICE '  • 1 Consolidated Dashboard: All agencies visible';
  RAISE NOTICE '';
  RAISE NOTICE '🎯 Next Steps:';
  RAISE NOTICE '  1. Configure Notion integration token in secrets';
  RAISE NOTICE '  2. Update database IDs in Notion integration config';
  RAISE NOTICE '  3. Deploy Notion webhook handler Edge Function';
  RAISE NOTICE '  4. Test two-way sync';
  RAISE NOTICE '  5. Add additional finance team members';
  RAISE NOTICE '════════════════════════════════════════════════════════════════';

END $$;

-- =============================================================================
-- Verification Queries
-- =============================================================================

-- Verify tenant and projects
SELECT
  t.slug AS tenant,
  t.name AS tenant_name,
  COUNT(DISTINCT p.id) AS project_count,
  array_agg(DISTINCT p.name ORDER BY p.name) AS projects
FROM tenants t
LEFT JOIN projects p ON p.tenant_id = t.id
WHERE t.slug = 'tbwa-finance-ssc'
GROUP BY t.slug, t.name;

-- Verify integrations (should be 1)
SELECT
  t.name AS tenant,
  COUNT(i.id) AS integration_count,
  array_agg(i.name) AS integrations
FROM tenants t
LEFT JOIN integrations i ON i.tenant_id = t.id
WHERE t.slug = 'tbwa-finance-ssc'
GROUP BY t.name;

-- Verify billing (should be 1)
SELECT
  t.name AS tenant,
  ba.currency,
  ba.billing_email,
  s.status AS subscription_status,
  p.name AS plan_name
FROM tenants t
JOIN billing_accounts ba ON ba.tenant_id = t.id
LEFT JOIN subscriptions s ON s.tenant_id = t.id
LEFT JOIN plans p ON s.plan_id = p.id
WHERE t.slug = 'tbwa-finance-ssc';

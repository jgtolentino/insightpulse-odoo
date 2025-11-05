-- =============================================================================
-- InsightPulse Finance SSC - Agency Seed Data
-- Creates 8 agency tenants with BIR compliance settings
-- =============================================================================

-- Enable UUID generation if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- 1. Create Agency Tenants
-- =============================================================================

INSERT INTO tenants (slug, name, timezone, metadata) VALUES
  (
    'rim',
    'RIM Agency',
    'Asia/Manila',
    jsonb_build_object(
      'agency_code', 'RIM',
      'legal_name', 'RIM Corporation',
      'bir_tin', '000-000-000-000',
      'bir_rdo', 'RDO 039',
      'industry', 'Financial Services',
      'fiscal_year_end', '12-31',
      'tax_type', 'corporate',
      'compliance_requirements', jsonb_build_array(
        '1601-C', '1702-RT', '2550Q', 'ATP'
      )
    )
  ),
  (
    'ckvc',
    'CKVC Agency',
    'Asia/Manila',
    jsonb_build_object(
      'agency_code', 'CKVC',
      'legal_name', 'CKVC Corporation',
      'bir_tin', '000-000-000-001',
      'bir_rdo', 'RDO 039',
      'industry', 'Financial Services',
      'fiscal_year_end', '12-31',
      'tax_type', 'corporate',
      'compliance_requirements', jsonb_build_array(
        '1601-C', '1702-RT', '2550Q', 'ATP'
      )
    )
  ),
  (
    'bom',
    'BOM Agency',
    'Asia/Manila',
    jsonb_build_object(
      'agency_code', 'BOM',
      'legal_name', 'BOM Corporation',
      'bir_tin', '000-000-000-002',
      'bir_rdo', 'RDO 039',
      'industry', 'Financial Services',
      'fiscal_year_end', '12-31',
      'tax_type', 'corporate',
      'compliance_requirements', jsonb_build_array(
        '1601-C', '1702-RT', '2550Q', 'ATP'
      )
    )
  ),
  (
    'jpal',
    'JPAL Agency',
    'Asia/Manila',
    jsonb_build_object(
      'agency_code', 'JPAL',
      'legal_name', 'JPAL Corporation',
      'bir_tin', '000-000-000-003',
      'bir_rdo', 'RDO 039',
      'industry', 'Financial Services',
      'fiscal_year_end', '12-31',
      'tax_type', 'corporate',
      'compliance_requirements', jsonb_build_array(
        '1601-C', '1702-RT', '2550Q', 'ATP'
      )
    )
  ),
  (
    'jli',
    'JLI Agency',
    'Asia/Manila',
    jsonb_build_object(
      'agency_code', 'JLI',
      'legal_name', 'JLI Corporation',
      'bir_tin', '000-000-000-004',
      'bir_rdo', 'RDO 039',
      'industry', 'Financial Services',
      'fiscal_year_end', '12-31',
      'tax_type', 'corporate',
      'compliance_requirements', jsonb_build_array(
        '1601-C', '1702-RT', '2550Q', 'ATP'
      )
    )
  ),
  (
    'jap',
    'JAP Agency',
    'Asia/Manila',
    jsonb_build_object(
      'agency_code', 'JAP',
      'legal_name', 'JAP Corporation',
      'bir_tin', '000-000-000-005',
      'bir_rdo', 'RDO 039',
      'industry', 'Financial Services',
      'fiscal_year_end', '12-31',
      'tax_type', 'corporate',
      'compliance_requirements', jsonb_build_array(
        '1601-C', '1702-RT', '2550Q', 'ATP'
      )
    )
  ),
  (
    'las',
    'LAS Agency',
    'Asia/Manila',
    jsonb_build_object(
      'agency_code', 'LAS',
      'legal_name', 'LAS Corporation',
      'bir_tin', '000-000-000-006',
      'bir_rdo', 'RDO 039',
      'industry', 'Financial Services',
      'fiscal_year_end', '12-31',
      'tax_type', 'corporate',
      'compliance_requirements', jsonb_build_array(
        '1601-C', '1702-RT', '2550Q', 'ATP'
      )
    )
  ),
  (
    'rmqb',
    'RMQB Agency',
    'Asia/Manila',
    jsonb_build_object(
      'agency_code', 'RMQB',
      'legal_name', 'RMQB Corporation',
      'bir_tin', '000-000-000-007',
      'bir_rdo', 'RDO 039',
      'industry', 'Financial Services',
      'fiscal_year_end', '12-31',
      'tax_type', 'corporate',
      'compliance_requirements', jsonb_build_array(
        '1601-C', '1702-RT', '2550Q', 'ATP'
      )
    )
  )
ON CONFLICT (slug) DO UPDATE SET
  name = EXCLUDED.name,
  metadata = EXCLUDED.metadata,
  updated_at = now();

-- =============================================================================
-- 2. Create Finance SSC Admin User
-- =============================================================================

INSERT INTO users (email, full_name, metadata) VALUES
  (
    'finance.ssc@insightpulseai.net',
    'Finance SSC Administrator',
    jsonb_build_object(
      'department', 'Finance Shared Service Center',
      'role', 'SSC Admin',
      'certifications', jsonb_build_array('CPA', 'BIR Accredited')
    )
  )
ON CONFLICT (email) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  metadata = EXCLUDED.metadata,
  updated_at = now();

-- =============================================================================
-- 3. Add Admin to All Agency Tenants
-- =============================================================================

INSERT INTO org_memberships (tenant_id, user_id, is_owner, status)
SELECT
  t.id AS tenant_id,
  (SELECT id FROM users WHERE email = 'finance.ssc@insightpulseai.net') AS user_id,
  true AS is_owner,
  'active' AS status
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id, user_id) DO UPDATE SET
  is_owner = EXCLUDED.is_owner,
  status = EXCLUDED.status;

-- =============================================================================
-- 4. Create Finance SSC Team (Cross-Agency)
-- =============================================================================

-- Create team for each agency
INSERT INTO teams (tenant_id, name, description, metadata)
SELECT
  t.id AS tenant_id,
  'Finance Team' AS name,
  'Finance and Accounting Team for ' || t.name AS description,
  jsonb_build_object(
    'function', 'finance',
    'size', 5,
    'skills', jsonb_build_array('accounting', 'bir_compliance', 'month_end_closing')
  ) AS metadata
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id, name) DO NOTHING;

-- =============================================================================
-- 5. Create Finance SSC Project (Consolidation)
-- =============================================================================

INSERT INTO projects (tenant_id, name, description, metadata)
SELECT
  t.id AS tenant_id,
  'Month-End Closing' AS name,
  'Monthly financial close and reporting for ' || t.name AS description,
  jsonb_build_object(
    'project_type', 'recurring',
    'frequency', 'monthly',
    'stakeholders', jsonb_build_array('CFO', 'Finance Manager', 'BIR Compliance Officer'),
    'deliverables', jsonb_build_array(
      'Trial Balance',
      'Financial Statements',
      'BIR Returns',
      'Management Reports'
    )
  ) AS metadata
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id, name) DO NOTHING;

-- Create environments for each project
INSERT INTO environments (project_id, name, type, metadata)
SELECT
  p.id AS project_id,
  'Production' AS name,
  'prod' AS type,
  jsonb_build_object(
    'odoo_instance', 'erp.insightpulseai.net',
    'database', t.slug || '_prod'
  ) AS metadata
FROM projects p
JOIN tenants t ON p.tenant_id = t.id
WHERE p.name = 'Month-End Closing'
ON CONFLICT (project_id, name) DO NOTHING;

-- =============================================================================
-- 6. Register Integration Types
-- =============================================================================

-- Notion integration type (if not already exists)
INSERT INTO integration_types (provider, display_name, docs_url) VALUES
  ('notion', 'Notion Workspace', 'https://developers.notion.com')
ON CONFLICT (provider) DO NOTHING;

-- =============================================================================
-- 7. Create Notion Integrations for Each Agency
-- =============================================================================

INSERT INTO integrations (tenant_id, type_id, name, config, enabled, metadata)
SELECT
  t.id AS tenant_id,
  (SELECT id FROM integration_types WHERE provider = 'notion') AS type_id,
  t.name || ' - Notion Workspace' AS name,
  jsonb_build_object(
    'workspace_id', 'notion-workspace-id',
    'database_ids', jsonb_build_object(
      'month_end_tasks', 'db-' || t.slug || '-month-end',
      'bir_filing_schedule', 'db-' || t.slug || '-bir-filing',
      'compliance_checklist', 'db-' || t.slug || '-compliance'
    ),
    'sync_frequency', '15m',
    'webhook_secret', 'will-be-replaced-by-secret'
  ) AS config,
  true AS enabled,
  jsonb_build_object(
    'last_sync', null,
    'sync_errors', 0,
    'total_records', 0
  ) AS metadata
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id, type_id, name) DO NOTHING;

-- =============================================================================
-- 8. Create BIR Compliance Data Policies
-- =============================================================================

INSERT INTO data_policies (tenant_id, name, retention_days, anonymize, config)
SELECT
  t.id AS tenant_id,
  'BIR Audit Trail - 10 Year Retention' AS name,
  3650 AS retention_days, -- 10 years
  false AS anonymize,
  jsonb_build_object(
    'policy_type', 'legal_compliance',
    'regulation', 'BIR Revenue Regulations',
    'scope', jsonb_build_array('audit_logs', 'attachments', 'workflows'),
    'exceptions', jsonb_build_array('bir.%', 'tax.%', 'compliance.%')
  ) AS config
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id, name) DO NOTHING;

-- =============================================================================
-- 9. Create Billing Accounts (Free Plan for All Agencies)
-- =============================================================================

INSERT INTO billing_accounts (tenant_id, currency, billing_email, metadata)
SELECT
  t.id AS tenant_id,
  'PHP' AS currency,
  'billing@' || t.slug || '.ph' AS billing_email,
  jsonb_build_object(
    'vat_registered', true,
    'bir_2307_required', false,
    'payment_terms', 'net_30'
  ) AS metadata
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id) DO NOTHING;

-- Subscribe all agencies to Free plan
INSERT INTO subscriptions (tenant_id, plan_id, status, current_period_start, current_period_end)
SELECT
  t.id AS tenant_id,
  (SELECT id FROM plans WHERE code = 'free') AS plan_id,
  'active' AS status,
  date_trunc('month', now()) AS current_period_start,
  (date_trunc('month', now()) + interval '1 month' - interval '1 day')::timestamptz AS current_period_end
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id, plan_id) DO NOTHING;

-- =============================================================================
-- 10. Create Shared Dashboards
-- =============================================================================

-- Finance SSC Consolidated Dashboard
INSERT INTO dashboards (tenant_id, name, layout, is_public, metadata)
SELECT
  t.id AS tenant_id,
  'Finance SSC - Consolidated View' AS name,
  jsonb_build_object(
    'type', 'grid',
    'columns', 12,
    'rows', jsonb_build_array(
      jsonb_build_object('height', 2),
      jsonb_build_object('height', 4),
      jsonb_build_object('height', 4)
    )
  ) AS layout,
  false AS is_public,
  jsonb_build_object(
    'refresh_interval', 300,
    'theme', 'light',
    'filters', jsonb_build_object(
      'default_period', 'current_month',
      'agencies', jsonb_build_array('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
    )
  ) AS metadata
FROM tenants t
WHERE t.slug = 'rim' -- Create once for RIM, shared across agencies
ON CONFLICT (tenant_id, name) DO NOTHING;

-- =============================================================================
-- 11. Create Default Data Sources
-- =============================================================================

-- PostgreSQL data source for each agency
INSERT INTO data_sources (tenant_id, name, kind, config, metadata)
SELECT
  t.id AS tenant_id,
  t.name || ' - PostgreSQL' AS name,
  'postgres' AS kind,
  jsonb_build_object(
    'host', 'aws-1-us-east-1.pooler.supabase.com',
    'port', 6543,
    'database', 'postgres',
    'username', 'postgres.' || t.slug,
    'password_secret_ref', 'secret://postgres-password-' || t.slug,
    'ssl', true,
    'schema', t.slug
  ) AS config,
  jsonb_build_object(
    'connection_pool', jsonb_build_object(
      'min', 2,
      'max', 10
    ),
    'query_timeout', 30000
  ) AS metadata
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id, name) DO NOTHING;

-- =============================================================================
-- 12. Create Saved Queries for Finance SSC Reporting
-- =============================================================================

-- Month-End Task Completion Query
INSERT INTO saved_queries (tenant_id, data_source_id, name, sql, metadata)
SELECT
  t.id AS tenant_id,
  ds.id AS data_source_id,
  'Month-End Task Completion %' AS name,
  $$
    SELECT
      date_trunc('month', wr.started_at) AS month,
      COUNT(CASE WHEN wr.status = 'completed' THEN 1 END)::float / NULLIF(COUNT(*), 0) * 100 AS completion_rate,
      COUNT(*) AS total_tasks,
      COUNT(CASE WHEN wr.status = 'completed' THEN 1 END) AS completed_tasks,
      COUNT(CASE WHEN wr.status = 'failed' THEN 1 END) AS failed_tasks
    FROM workflow_runs wr
    JOIN workflows w ON wr.workflow_id = w.id
    WHERE w.name LIKE '%Month-End%'
      AND wr.started_at >= date_trunc('year', now())
    GROUP BY 1
    ORDER BY 1 DESC;
  $$ AS sql,
  jsonb_build_object(
    'category', 'finance_ssc',
    'refresh_interval', 3600,
    'cache_ttl', 1800
  ) AS metadata
FROM tenants t
JOIN data_sources ds ON t.id = ds.tenant_id
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
  AND ds.kind = 'postgres'
ON CONFLICT (tenant_id, name) DO NOTHING;

-- BIR Filing Compliance Query
INSERT INTO saved_queries (tenant_id, data_source_id, name, sql, metadata)
SELECT
  t.id AS tenant_id,
  ds.id AS data_source_id,
  'BIR Filing Compliance Status' AS name,
  $$
    SELECT
      date_trunc('month', al.created_at) AS month,
      al.metadata->>'form_type' AS form_type,
      COUNT(*) AS total_filings,
      COUNT(CASE WHEN al.metadata->>'status' = 'filed' THEN 1 END) AS filed_on_time,
      COUNT(CASE WHEN al.metadata->>'status' = 'late' THEN 1 END) AS filed_late,
      COUNT(CASE WHEN al.metadata->>'status' = 'pending' THEN 1 END) AS pending
    FROM audit_logs al
    WHERE al.action LIKE 'bir.%'
      AND al.created_at >= date_trunc('year', now())
    GROUP BY 1, 2
    ORDER BY 1 DESC, 2;
  $$ AS sql,
  jsonb_build_object(
    'category', 'bir_compliance',
    'refresh_interval', 7200,
    'alert_on_late_filings', true
  ) AS metadata
FROM tenants t
JOIN data_sources ds ON t.id = ds.tenant_id
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
  AND ds.kind = 'postgres'
ON CONFLICT (tenant_id, name) DO NOTHING;

-- =============================================================================
-- 13. Create Alerts for Missed Deadlines
-- =============================================================================

INSERT INTO alerts (tenant_id, name, type, condition, enabled, metadata)
SELECT
  t.id AS tenant_id,
  'BIR Filing Deadline Alert' AS name,
  'threshold' AS type,
  jsonb_build_object(
    'check_frequency', '1h',
    'condition', 'pending_filings > 0 AND days_until_deadline <= 2',
    'severity', 'high',
    'query', 'SELECT COUNT(*) as pending_filings, MIN((metadata->>''filing_deadline'')::date - CURRENT_DATE) as days_until_deadline FROM audit_logs WHERE action = ''bir.filing_pending'' AND tenant_id = ''' || t.id || ''''
  ) AS condition,
  true AS enabled,
  jsonb_build_object(
    'escalation_path', jsonb_build_array('finance_manager', 'cfo', 'compliance_officer'),
    'auto_remind', true,
    'reminder_hours', jsonb_build_array(48, 24, 12, 6)
  ) AS metadata
FROM tenants t
WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT (tenant_id, name) DO NOTHING;

-- Add Slack notification channel for alerts
INSERT INTO alert_channels (alert_id, channel, config)
SELECT
  a.id AS alert_id,
  'slack' AS channel,
  jsonb_build_object(
    'webhook_url', 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL',
    'channel', '#finance-ssc-alerts',
    'username', 'BIR Compliance Bot',
    'icon_emoji', ':warning:'
  ) AS config
FROM alerts a
JOIN tenants t ON a.tenant_id = t.id
WHERE a.name = 'BIR Filing Deadline Alert'
  AND t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
ON CONFLICT DO NOTHING;

-- =============================================================================
-- Verification Queries
-- =============================================================================

-- Count created records
DO $$
DECLARE
  tenant_count INT;
  integration_count INT;
  project_count INT;
  dashboard_count INT;
BEGIN
  SELECT COUNT(*) INTO tenant_count FROM tenants WHERE slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb');
  SELECT COUNT(*) INTO integration_count FROM integrations WHERE tenant_id IN (SELECT id FROM tenants WHERE slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb'));
  SELECT COUNT(*) INTO project_count FROM projects WHERE tenant_id IN (SELECT id FROM tenants WHERE slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb'));
  SELECT COUNT(*) INTO dashboard_count FROM dashboards WHERE tenant_id IN (SELECT id FROM tenants WHERE slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb'));

  RAISE NOTICE '✅ Tenants created: %', tenant_count;
  RAISE NOTICE '✅ Integrations created: %', integration_count;
  RAISE NOTICE '✅ Projects created: %', project_count;
  RAISE NOTICE '✅ Dashboards created: %', dashboard_count;
END $$;

-- =============================================================================
-- Summary
-- =============================================================================

COMMENT ON TABLE tenants IS 'Finance SSC Agencies: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB';

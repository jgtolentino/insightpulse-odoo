-- =============================================================================
-- InsightPulse SaaS Core Schema
-- Multi-tenant, RBAC, integrations, billing, AI, BI, tickets
-- Generated from schema.dbml
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";

-- =============================================================================
-- Enums
-- =============================================================================

CREATE TYPE environment_type AS ENUM ('dev', 'staging', 'prod');
CREATE TYPE plan_interval AS ENUM ('monthly', 'yearly');
CREATE TYPE provider_type AS ENUM ('github', 'slack', 'odoo', 'supabase', 'google', 'azuread', 'okta', 'notion', 'webhook');
CREATE TYPE api_key_scope AS ENUM ('org', 'project', 'environment');
CREATE TYPE alert_type AS ENUM ('threshold', 'anomaly', 'schedule', 'change');
CREATE TYPE channel_type AS ENUM ('email', 'slack', 'webhook');
CREATE TYPE secret_format AS ENUM ('opaque', 'json', 'pem', 'jwt');
CREATE TYPE invoice_status AS ENUM ('draft', 'open', 'paid', 'void', 'uncollectible');
CREATE TYPE payment_status AS ENUM ('pending', 'succeeded', 'failed', 'refunded');
CREATE TYPE ticket_state AS ENUM ('open', 'in_progress', 'waiting', 'resolved', 'closed');
CREATE TYPE severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE webhook_status AS ENUM ('queued', 'delivered', 'failed');
CREATE TYPE role_scope AS ENUM ('global', 'org', 'project');

-- =============================================================================
-- Tenancy & Identity
-- =============================================================================

CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  timezone TEXT NOT NULL DEFAULT 'Asia/Manila',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON COLUMN tenants.slug IS 'URL id, e.g., acme';

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  password_hash TEXT,
  full_name TEXT,
  picture_url TEXT,
  is_staff BOOLEAN NOT NULL DEFAULT false,
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

COMMENT ON COLUMN users.password_hash IS 'Only if local auth is enabled';

CREATE TABLE org_memberships (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  is_owner BOOLEAN NOT NULL DEFAULT false,
  invited_by UUID,
  invited_at TIMESTAMPTZ DEFAULT now(),
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, user_id)
);

COMMENT ON COLUMN org_memberships.status IS 'active|invited|disabled';

CREATE TABLE teams (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, name)
);

CREATE TABLE team_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (team_id, user_id)
);

CREATE TABLE roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  scope role_scope NOT NULL DEFAULT 'org',
  description TEXT,
  UNIQUE (name, scope)
);

CREATE TABLE permissions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,
  description TEXT
);

COMMENT ON COLUMN permissions.code IS 'e.g., repo.write, billing.read, dashboard.manage';

CREATE TABLE role_permissions (
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
  UNIQUE (role_id, permission_id)
);

CREATE TABLE user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tenant_id UUID REFERENCES tenants(id),
  project_id UUID,
  role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON TABLE user_roles IS 'Scope determined by which foreign key is non-null';

CREATE TABLE sso_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  provider provider_type NOT NULL DEFAULT 'google',
  saml_metadata XML,
  oidc_issuer TEXT,
  client_id TEXT,
  client_secret TEXT,
  settings JSONB,
  enabled BOOLEAN DEFAULT true,
  UNIQUE (tenant_id, provider)
);

CREATE TABLE user_identities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  tenant_id UUID REFERENCES tenants(id),
  provider provider_type NOT NULL,
  subject TEXT NOT NULL,
  email TEXT,
  raw JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (provider, subject)
);

COMMENT ON COLUMN user_identities.subject IS 'sub/NameID';

CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  project_id UUID,
  environment_id UUID,
  name TEXT NOT NULL,
  scope api_key_scope NOT NULL DEFAULT 'org',
  hash TEXT NOT NULL UNIQUE,
  last_used_at TIMESTAMPTZ,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  revoked_at TIMESTAMPTZ
);

COMMENT ON COLUMN api_keys.hash IS 'store hash, not plaintext';

-- =============================================================================
-- Projects & Environments
-- =============================================================================

CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, name)
);

CREATE TABLE environments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  type environment_type NOT NULL DEFAULT 'prod',
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (project_id, name)
);

-- Add foreign key for user_roles.project_id
ALTER TABLE user_roles ADD FOREIGN KEY (project_id) REFERENCES projects(id);

-- Add foreign keys for api_keys
ALTER TABLE api_keys ADD FOREIGN KEY (project_id) REFERENCES projects(id);
ALTER TABLE api_keys ADD FOREIGN KEY (environment_id) REFERENCES environments(id);

-- =============================================================================
-- Integrations & Webhooks
-- =============================================================================

CREATE TABLE integration_types (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider provider_type NOT NULL UNIQUE,
  display_name TEXT NOT NULL,
  docs_url TEXT
);

CREATE TABLE integrations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  type_id UUID NOT NULL REFERENCES integration_types(id),
  name TEXT NOT NULL,
  config JSONB NOT NULL,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, type_id, name)
);

COMMENT ON COLUMN integrations.config IS 'host, repo, workspace, instance_url, etc.';

CREATE TABLE integration_secrets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_id UUID NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
  format secret_format NOT NULL DEFAULT 'opaque',
  ciphertext BYTEA NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE integration_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_id UUID NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,
  payload JSONB NOT NULL,
  received_at TIMESTAMPTZ DEFAULT now(),
  processed_at TIMESTAMPTZ,
  status TEXT DEFAULT 'queued',
  error TEXT
);

CREATE INDEX idx_integration_events_integration_received ON integration_events(integration_id, received_at);

CREATE TABLE webhooks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  url TEXT NOT NULL,
  secret TEXT,
  description TEXT,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, url)
);

CREATE TABLE webhook_deliveries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
  event TEXT NOT NULL,
  payload JSONB NOT NULL,
  status webhook_status DEFAULT 'queued',
  response_code INTEGER,
  response_ms INTEGER,
  error TEXT,
  attempted_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_webhook_deliveries_webhook_attempted ON webhook_deliveries(webhook_id, attempted_at);

-- =============================================================================
-- Audit, Policies, Secrets
-- =============================================================================

CREATE TABLE audit_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID REFERENCES tenants(id),
  user_id UUID REFERENCES users(id),
  actor_type TEXT NOT NULL DEFAULT 'user',
  action TEXT NOT NULL,
  target_type TEXT,
  target_id TEXT,
  ip INET,
  user_agent TEXT,
  diff JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON COLUMN audit_logs.actor_type IS 'user|api|system';
COMMENT ON COLUMN audit_logs.action IS 'e.g., repo.commit, billing.update';

CREATE INDEX idx_audit_logs_tenant_created ON audit_logs(tenant_id, created_at);

CREATE TABLE data_policies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  retention_days INTEGER,
  anonymize BOOLEAN DEFAULT false,
  config JSONB,
  UNIQUE (tenant_id, name)
);

CREATE TABLE consents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  purpose TEXT NOT NULL,
  granted BOOLEAN NOT NULL,
  granted_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, user_id, purpose)
);

CREATE TABLE secrets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  latest_version INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, name)
);

CREATE TABLE secret_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  secret_id UUID NOT NULL REFERENCES secrets(id) ON DELETE CASCADE,
  version INTEGER NOT NULL,
  format secret_format NOT NULL DEFAULT 'opaque',
  ciphertext BYTEA NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (secret_id, version)
);

-- =============================================================================
-- Billing, Plans, Usage
-- =============================================================================

CREATE TABLE billing_accounts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,
  currency CHAR(3) NOT NULL DEFAULT 'USD',
  billing_email TEXT NOT NULL,
  tax_id TEXT,
  address JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE plans (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  interval plan_interval NOT NULL DEFAULT 'monthly',
  price_cents INTEGER NOT NULL,
  meta JSONB
);

COMMENT ON COLUMN plans.code IS 'e.g., starter, pro, enterprise';

CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  plan_id UUID NOT NULL REFERENCES plans(id) ON DELETE RESTRICT,
  status TEXT NOT NULL DEFAULT 'active',
  current_period_start TIMESTAMPTZ NOT NULL DEFAULT now(),
  current_period_end TIMESTAMPTZ NOT NULL,
  cancel_at TIMESTAMPTZ,
  canceled_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON COLUMN subscriptions.status IS 'active|past_due|canceled';

CREATE INDEX idx_subscriptions_tenant_status ON subscriptions(tenant_id, status);

CREATE TABLE invoices (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  subscription_id UUID NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
  number TEXT NOT NULL UNIQUE,
  status invoice_status NOT NULL DEFAULT 'open',
  amount_due_cents INTEGER NOT NULL,
  amount_paid_cents INTEGER NOT NULL DEFAULT 0,
  issued_at TIMESTAMPTZ DEFAULT now(),
  due_at TIMESTAMPTZ,
  meta JSONB
);

CREATE TABLE invoice_lines (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  description TEXT NOT NULL,
  quantity NUMERIC(18,6) NOT NULL DEFAULT 1,
  unit_price_cents INTEGER NOT NULL,
  amount_cents INTEGER NOT NULL
);

CREATE TABLE payments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  invoice_id UUID NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
  status payment_status NOT NULL DEFAULT 'pending',
  amount_cents INTEGER NOT NULL,
  processor TEXT NOT NULL,
  reference TEXT,
  processed_at TIMESTAMPTZ,
  error TEXT
);

COMMENT ON COLUMN payments.processor IS 'e.g., stripe, xendit';

CREATE TABLE usage_counters (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id),
  metric TEXT NOT NULL,
  period_start DATE NOT NULL,
  period_end DATE NOT NULL,
  value NUMERIC(20,6) NOT NULL DEFAULT 0,
  UNIQUE (tenant_id, project_id, metric, period_start, period_end)
);

COMMENT ON COLUMN usage_counters.metric IS 'e.g., tokens, jobs, dashboards_rendered';

CREATE TABLE metered_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id),
  metric TEXT NOT NULL,
  value NUMERIC(20,6) NOT NULL DEFAULT 1,
  occurred_at TIMESTAMPTZ DEFAULT now(),
  meta JSONB
);

CREATE INDEX idx_metered_events_tenant_metric_occurred ON metered_events(tenant_id, metric, occurred_at);

-- =============================================================================
-- Data Sources, BI, Alerts
-- =============================================================================

CREATE TABLE data_sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  kind TEXT NOT NULL,
  config JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, name)
);

COMMENT ON COLUMN data_sources.kind IS 'postgres|mysql|bigquery|clickhouse|http|supabase';
COMMENT ON COLUMN data_sources.config IS 'host, db, user (stored via secret reference)';

CREATE TABLE dashboards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id),
  name TEXT NOT NULL,
  layout JSONB NOT NULL,
  is_public BOOLEAN DEFAULT false,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, name)
);

CREATE TABLE widgets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  dashboard_id UUID NOT NULL REFERENCES dashboards(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  query_id UUID,
  viz_type TEXT NOT NULL,
  position JSONB NOT NULL,
  options JSONB
);

COMMENT ON COLUMN widgets.viz_type IS 'line, bar, pie, table, kpi, map';
COMMENT ON COLUMN widgets.position IS 'x,y,w,h';

CREATE TABLE saved_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  data_source_id UUID NOT NULL REFERENCES data_sources(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  sql TEXT NOT NULL,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, name)
);

-- Add foreign key for widgets.query_id
ALTER TABLE widgets ADD FOREIGN KEY (query_id) REFERENCES saved_queries(id);

CREATE TABLE alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  type alert_type NOT NULL,
  query_id UUID REFERENCES saved_queries(id),
  condition JSONB,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, name)
);

COMMENT ON COLUMN alerts.condition IS 'threshold config, schedule cron, etc.';

CREATE TABLE alert_channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
  channel channel_type NOT NULL,
  config JSONB NOT NULL
);

COMMENT ON COLUMN alert_channels.config IS 'email(s), slack webhook, etc.';

CREATE TABLE alert_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  alert_id UUID NOT NULL REFERENCES alerts(id) ON DELETE CASCADE,
  fired_at TIMESTAMPTZ DEFAULT now(),
  payload JSONB,
  delivered BOOLEAN DEFAULT false
);

-- =============================================================================
-- AI (Models, Prompts, RAG, OCR)
-- =============================================================================

CREATE TABLE model_providers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL UNIQUE,
  base_url TEXT
);

COMMENT ON COLUMN model_providers.name IS 'openai, anthropic, deepseek, llama';

CREATE TABLE llm_models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  provider_id UUID NOT NULL REFERENCES model_providers(id),
  name TEXT NOT NULL,
  context_tokens INTEGER,
  input_cost_per_mtok_usd NUMERIC(10,6),
  output_cost_per_mtok_usd NUMERIC(10,6),
  UNIQUE (provider_id, name)
);

COMMENT ON COLUMN llm_models.name IS 'gpt-4.1, claude-3.7, r1-distill-qwen-7b';

CREATE TABLE prompt_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  template TEXT NOT NULL,
  meta JSONB,
  UNIQUE (tenant_id, name)
);

CREATE TABLE prompt_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  model_id UUID NOT NULL REFERENCES llm_models(id) ON DELETE RESTRICT,
  template_id UUID REFERENCES prompt_templates(id),
  input_tokens INTEGER,
  output_tokens INTEGER,
  cost_usd NUMERIC(12,6),
  latency_ms INTEGER,
  request JSONB,
  response JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_prompt_runs_tenant_created ON prompt_runs(tenant_id, created_at);

CREATE TABLE rag_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  source TEXT,
  title TEXT,
  path TEXT,
  meta JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON COLUMN rag_documents.source IS 'url|upload|gdrive';

CREATE TABLE rag_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
  seq INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  UNIQUE (document_id, seq)
);

COMMENT ON COLUMN rag_chunks.embedding IS 'pgvector';

CREATE INDEX idx_rag_chunks_embedding ON rag_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE TABLE ocr_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  source_url TEXT,
  status TEXT NOT NULL DEFAULT 'queued',
  engine TEXT NOT NULL DEFAULT 'paddleocr-vl',
  params JSONB,
  result JSONB,
  created_at TIMESTAMPTZ DEFAULT now(),
  completed_at TIMESTAMPTZ
);

-- =============================================================================
-- Support, Tickets, Workflows
-- =============================================================================

CREATE TABLE tickets (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  project_id UUID REFERENCES projects(id),
  number TEXT NOT NULL UNIQUE,
  title TEXT NOT NULL,
  state ticket_state NOT NULL DEFAULT 'open',
  severity severity NOT NULL DEFAULT 'medium',
  assignee_id UUID,
  created_by UUID,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  due_at TIMESTAMPTZ,
  meta JSONB
);

CREATE TABLE ticket_comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ticket_id UUID NOT NULL REFERENCES tickets(id) ON DELETE CASCADE,
  author_id UUID NOT NULL REFERENCES users(id) ON DELETE SET NULL,
  body TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  owner_type TEXT NOT NULL,
  owner_id UUID NOT NULL,
  filename TEXT NOT NULL,
  content_type TEXT,
  byte_size INTEGER,
  storage_url TEXT,
  checksum TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

COMMENT ON COLUMN attachments.owner_type IS 'ticket|ocr|dashboard|webhook|audit';

CREATE INDEX idx_attachments_tenant_owner ON attachments(tenant_id, owner_type, owner_id);

CREATE TABLE workflows (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  definition JSONB NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, name)
);

COMMENT ON COLUMN workflows.definition IS 'DAG or state machine';

CREATE TABLE workflow_runs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workflow_id UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
  triggered_by UUID,
  status TEXT NOT NULL DEFAULT 'running',
  input JSONB,
  output JSONB,
  started_at TIMESTAMPTZ DEFAULT now(),
  finished_at TIMESTAMPTZ
);

-- =============================================================================
-- Domains & DNS
-- =============================================================================

CREATE TABLE domains (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  host TEXT NOT NULL,
  verified BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (tenant_id, host)
);

COMMENT ON COLUMN domains.host IS 'insightpulseai.net, erp.insightpulseai.net';

CREATE TABLE dns_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  type TEXT NOT NULL,
  ttl INTEGER DEFAULT 3600,
  data TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (domain_id, name, type)
);

COMMENT ON COLUMN dns_records.name IS '@, www, erp, mcp, agent, superset, ocr';
COMMENT ON COLUMN dns_records.type IS 'A, AAAA, CNAME, TXT, CAA';

CREATE TABLE certificates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  domain_id UUID NOT NULL REFERENCES domains(id) ON DELETE CASCADE,
  issuer TEXT,
  not_before TIMESTAMPTZ,
  not_after TIMESTAMPTZ,
  cert_pem TEXT,
  key_pem TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- =============================================================================
-- GitHub / Slack Cache Tables
-- =============================================================================

CREATE TABLE github_repos (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_id UUID NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
  repo_full_name TEXT NOT NULL,
  default_branch TEXT,
  visibility TEXT,
  meta JSONB,
  UNIQUE (integration_id, repo_full_name)
);

COMMENT ON COLUMN github_repos.repo_full_name IS 'owner/name';

CREATE TABLE slack_workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  integration_id UUID NOT NULL REFERENCES integrations(id) ON DELETE CASCADE,
  team_id TEXT NOT NULL,
  team_name TEXT,
  UNIQUE (integration_id, team_id)
);

CREATE TABLE slack_channels (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  workspace_id UUID NOT NULL REFERENCES slack_workspaces(id) ON DELETE CASCADE,
  channel_id TEXT NOT NULL,
  name TEXT,
  is_private BOOLEAN,
  UNIQUE (workspace_id, channel_id)
);

-- =============================================================================
-- Row Level Security (RLS) Policies
-- =============================================================================

-- Enable RLS on all tenant-scoped tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE org_memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE teams ENABLE ROW LEVEL SECURITY;
ALTER TABLE team_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE environments ENABLE ROW LEVEL SECURITY;
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_secrets ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhooks ENABLE ROW LEVEL SECURITY;
ALTER TABLE webhook_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE consents ENABLE ROW LEVEL SECURITY;
ALTER TABLE secrets ENABLE ROW LEVEL SECURITY;
ALTER TABLE secret_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE billing_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoices ENABLE ROW LEVEL SECURITY;
ALTER TABLE invoice_lines ENABLE ROW LEVEL SECURITY;
ALTER TABLE payments ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_counters ENABLE ROW LEVEL SECURITY;
ALTER TABLE metered_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboards ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_channels ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE rag_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE ocr_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE tickets ENABLE ROW LEVEL SECURITY;
ALTER TABLE ticket_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE attachments ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE domains ENABLE ROW LEVEL SECURITY;
ALTER TABLE dns_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE certificates ENABLE ROW LEVEL SECURITY;

-- =============================================================================
-- Helper Functions
-- =============================================================================

-- Function to get current user's tenant memberships
CREATE OR REPLACE FUNCTION auth.user_tenant_ids()
RETURNS UUID[] AS $$
  SELECT ARRAY_AGG(tenant_id)
  FROM org_memberships
  WHERE user_id = auth.uid()
    AND status = 'active';
$$ LANGUAGE SQL STABLE;

-- Function to check if user is tenant owner
CREATE OR REPLACE FUNCTION auth.is_tenant_owner(tenant_uuid UUID)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM org_memberships
    WHERE tenant_id = tenant_uuid
      AND user_id = auth.uid()
      AND is_owner = true
      AND status = 'active'
  );
$$ LANGUAGE SQL STABLE;

-- Function to check if user has permission
CREATE OR REPLACE FUNCTION auth.user_has_permission(permission_code TEXT, tenant_uuid UUID DEFAULT NULL)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1
    FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    JOIN permissions p ON rp.permission_id = p.id
    WHERE ur.user_id = auth.uid()
      AND p.code = permission_code
      AND (tenant_uuid IS NULL OR ur.tenant_id = tenant_uuid)
  );
$$ LANGUAGE SQL STABLE;

-- =============================================================================
-- RLS Policies
-- =============================================================================

-- Tenants: Users can only see tenants they are members of
CREATE POLICY tenant_access_policy ON tenants
  FOR ALL
  USING (id = ANY(auth.user_tenant_ids()));

-- Org Memberships: Users can see memberships for their tenants
CREATE POLICY org_membership_policy ON org_memberships
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Teams: Scoped to tenant
CREATE POLICY team_policy ON teams
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Projects: Scoped to tenant
CREATE POLICY project_policy ON projects
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Environments: Access via projects
CREATE POLICY environment_policy ON environments
  FOR ALL
  USING (
    project_id IN (
      SELECT id FROM projects WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Integrations: Scoped to tenant
CREATE POLICY integration_policy ON integrations
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Integration Secrets: Access via integrations
CREATE POLICY integration_secret_policy ON integration_secrets
  FOR ALL
  USING (
    integration_id IN (
      SELECT id FROM integrations WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Webhooks: Scoped to tenant
CREATE POLICY webhook_policy ON webhooks
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Audit Logs: Users can see their tenant's audit logs (read-only for most)
CREATE POLICY audit_log_read_policy ON audit_logs
  FOR SELECT
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY audit_log_insert_policy ON audit_logs
  FOR INSERT
  WITH CHECK (true); -- System can always insert

-- Billing: Only tenant owners can see billing
CREATE POLICY billing_account_policy ON billing_accounts
  FOR ALL
  USING (auth.is_tenant_owner(tenant_id));

CREATE POLICY subscription_policy ON subscriptions
  FOR ALL
  USING (auth.is_tenant_owner(tenant_id));

-- Dashboards: Scoped to tenant, or public
CREATE POLICY dashboard_read_policy ON dashboards
  FOR SELECT
  USING (
    is_public = true
    OR tenant_id = ANY(auth.user_tenant_ids())
  );

CREATE POLICY dashboard_write_policy ON dashboards
  FOR INSERT
  WITH CHECK (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY dashboard_update_policy ON dashboards
  FOR UPDATE
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY dashboard_delete_policy ON dashboards
  FOR DELETE
  USING (
    tenant_id = ANY(auth.user_tenant_ids())
    AND auth.user_has_permission('dashboard.delete', tenant_id)
  );

-- Data Sources: Scoped to tenant
CREATE POLICY data_source_policy ON data_sources
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Saved Queries: Scoped to tenant
CREATE POLICY saved_query_policy ON saved_queries
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Alerts: Scoped to tenant
CREATE POLICY alert_policy ON alerts
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- AI/RAG: Scoped to tenant
CREATE POLICY prompt_template_policy ON prompt_templates
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY prompt_run_policy ON prompt_runs
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY rag_document_policy ON rag_documents
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY rag_chunk_policy ON rag_chunks
  FOR ALL
  USING (
    document_id IN (
      SELECT id FROM rag_documents WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- OCR Jobs: Scoped to tenant
CREATE POLICY ocr_job_policy ON ocr_jobs
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Tickets: Scoped to tenant
CREATE POLICY ticket_policy ON tickets
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY ticket_comment_policy ON ticket_comments
  FOR ALL
  USING (
    ticket_id IN (
      SELECT id FROM tickets WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Attachments: Scoped to tenant
CREATE POLICY attachment_policy ON attachments
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Workflows: Scoped to tenant
CREATE POLICY workflow_policy ON workflows
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY workflow_run_policy ON workflow_runs
  FOR ALL
  USING (
    workflow_id IN (
      SELECT id FROM workflows WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Domains: Scoped to tenant
CREATE POLICY domain_policy ON domains
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY dns_record_policy ON dns_records
  FOR ALL
  USING (
    domain_id IN (
      SELECT id FROM domains WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

CREATE POLICY certificate_policy ON certificates
  FOR ALL
  USING (
    domain_id IN (
      SELECT id FROM domains WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Secrets: Scoped to tenant
CREATE POLICY secret_policy ON secrets
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY secret_version_policy ON secret_versions
  FOR ALL
  USING (
    secret_id IN (
      SELECT id FROM secrets WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Usage/Metering: Scoped to tenant
CREATE POLICY usage_counter_policy ON usage_counters
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

CREATE POLICY metered_event_policy ON metered_events
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Data Policies: Scoped to tenant
CREATE POLICY data_policy_policy ON data_policies
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Consents: Scoped to tenant
CREATE POLICY consent_policy ON consents
  FOR ALL
  USING (tenant_id = ANY(auth.user_tenant_ids()));

-- Integration Events: Via integrations
CREATE POLICY integration_event_policy ON integration_events
  FOR ALL
  USING (
    integration_id IN (
      SELECT id FROM integrations WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Webhook Deliveries: Via webhooks
CREATE POLICY webhook_delivery_policy ON webhook_deliveries
  FOR ALL
  USING (
    webhook_id IN (
      SELECT id FROM webhooks WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Alert Channels: Via alerts
CREATE POLICY alert_channel_policy ON alert_channels
  FOR ALL
  USING (
    alert_id IN (
      SELECT id FROM alerts WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- Alert Events: Via alerts
CREATE POLICY alert_event_policy ON alert_events
  FOR ALL
  USING (
    alert_id IN (
      SELECT id FROM alerts WHERE tenant_id = ANY(auth.user_tenant_ids())
    )
  );

-- =============================================================================
-- Seed Data: Integration Types
-- =============================================================================

INSERT INTO integration_types (provider, display_name, docs_url) VALUES
  ('github', 'GitHub', 'https://docs.github.com/en/rest'),
  ('slack', 'Slack', 'https://api.slack.com'),
  ('odoo', 'Odoo ERP', 'https://www.odoo.com/documentation'),
  ('supabase', 'Supabase', 'https://supabase.com/docs'),
  ('google', 'Google Workspace', 'https://developers.google.com'),
  ('azuread', 'Azure Active Directory', 'https://docs.microsoft.com/en-us/azure/active-directory'),
  ('okta', 'Okta', 'https://developer.okta.com'),
  ('notion', 'Notion', 'https://developers.notion.com'),
  ('webhook', 'Generic Webhook', NULL)
ON CONFLICT (provider) DO NOTHING;

-- =============================================================================
-- Seed Data: Model Providers & LLM Models
-- =============================================================================

INSERT INTO model_providers (name, base_url) VALUES
  ('openai', 'https://api.openai.com/v1'),
  ('anthropic', 'https://api.anthropic.com/v1'),
  ('deepseek', 'https://api.deepseek.com/v1'),
  ('llama', NULL)
ON CONFLICT (name) DO NOTHING;

INSERT INTO llm_models (provider_id, name, context_tokens, input_cost_per_mtok_usd, output_cost_per_mtok_usd)
SELECT
  (SELECT id FROM model_providers WHERE name = 'openai'),
  'gpt-4o',
  128000,
  2.50,
  10.00
WHERE NOT EXISTS (
  SELECT 1 FROM llm_models WHERE name = 'gpt-4o'
);

INSERT INTO llm_models (provider_id, name, context_tokens, input_cost_per_mtok_usd, output_cost_per_mtok_usd)
SELECT
  (SELECT id FROM model_providers WHERE name = 'anthropic'),
  'claude-3-5-sonnet-20241022',
  200000,
  3.00,
  15.00
WHERE NOT EXISTS (
  SELECT 1 FROM llm_models WHERE name = 'claude-3-5-sonnet-20241022'
);

INSERT INTO llm_models (provider_id, name, context_tokens, input_cost_per_mtok_usd, output_cost_per_mtok_usd)
SELECT
  (SELECT id FROM model_providers WHERE name = 'deepseek'),
  'deepseek-chat',
  64000,
  0.14,
  0.28
WHERE NOT EXISTS (
  SELECT 1 FROM llm_models WHERE name = 'deepseek-chat'
);

-- =============================================================================
-- Seed Data: Roles & Permissions
-- =============================================================================

INSERT INTO roles (name, scope, description) VALUES
  ('Admin', 'org', 'Full access to organization'),
  ('Developer', 'org', 'Can manage projects and integrations'),
  ('Viewer', 'org', 'Read-only access'),
  ('Billing Admin', 'org', 'Can manage billing and subscriptions'),
  ('Project Admin', 'project', 'Full access to project'),
  ('Project Developer', 'project', 'Can deploy and manage project resources'),
  ('Project Viewer', 'project', 'Read-only access to project')
ON CONFLICT (name, scope) DO NOTHING;

INSERT INTO permissions (code, description) VALUES
  ('org.read', 'View organization details'),
  ('org.write', 'Modify organization settings'),
  ('org.delete', 'Delete organization'),
  ('user.invite', 'Invite users to organization'),
  ('user.remove', 'Remove users from organization'),
  ('project.create', 'Create new projects'),
  ('project.read', 'View project details'),
  ('project.write', 'Modify project settings'),
  ('project.delete', 'Delete projects'),
  ('integration.create', 'Create new integrations'),
  ('integration.read', 'View integrations'),
  ('integration.write', 'Modify integrations'),
  ('integration.delete', 'Delete integrations'),
  ('billing.read', 'View billing information'),
  ('billing.write', 'Modify billing settings'),
  ('dashboard.create', 'Create dashboards'),
  ('dashboard.read', 'View dashboards'),
  ('dashboard.write', 'Modify dashboards'),
  ('dashboard.delete', 'Delete dashboards'),
  ('secret.create', 'Create secrets'),
  ('secret.read', 'Read secrets'),
  ('secret.write', 'Update secrets'),
  ('secret.delete', 'Delete secrets'),
  ('audit.read', 'View audit logs'),
  ('ticket.create', 'Create tickets'),
  ('ticket.read', 'View tickets'),
  ('ticket.write', 'Modify tickets'),
  ('ticket.delete', 'Delete tickets')
ON CONFLICT (code) DO NOTHING;

-- =============================================================================
-- Seed Data: Plans
-- =============================================================================

INSERT INTO plans (code, name, interval, price_cents, meta) VALUES
  ('free', 'Free', 'monthly', 0, '{"max_projects": 1, "max_users": 3, "max_dashboards": 5}'::jsonb),
  ('starter', 'Starter', 'monthly', 2900, '{"max_projects": 5, "max_users": 10, "max_dashboards": 20}'::jsonb),
  ('pro', 'Pro', 'monthly', 9900, '{"max_projects": 20, "max_users": 50, "max_dashboards": 100}'::jsonb),
  ('enterprise', 'Enterprise', 'monthly', 29900, '{"max_projects": -1, "max_users": -1, "max_dashboards": -1}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- =============================================================================
-- Indexes for Performance
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_org_memberships_user ON org_memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_org_memberships_tenant ON org_memberships(tenant_id);
CREATE INDEX IF NOT EXISTS idx_projects_tenant ON projects(tenant_id);
CREATE INDEX IF NOT EXISTS idx_environments_project ON environments(project_id);
CREATE INDEX IF NOT EXISTS idx_integrations_tenant ON integrations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_dashboards_tenant ON dashboards(tenant_id);
CREATE INDEX IF NOT EXISTS idx_dashboards_project ON dashboards(project_id);
CREATE INDEX IF NOT EXISTS idx_tickets_tenant ON tickets(tenant_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assignee ON tickets(assignee_id);
CREATE INDEX IF NOT EXISTS idx_workflows_tenant ON workflows(tenant_id);

-- =============================================================================
-- Triggers for Updated_at Columns
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dashboards_updated_at BEFORE UPDATE ON dashboards
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_saved_queries_updated_at BEFORE UPDATE ON saved_queries
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tickets_updated_at BEFORE UPDATE ON tickets
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Comments
-- =============================================================================

COMMENT ON DATABASE CURRENT_DATABASE() IS 'InsightPulse SaaS Core - Multi-tenant platform with RBAC, integrations, billing, AI, BI, and workflows';

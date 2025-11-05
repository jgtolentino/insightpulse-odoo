-- === IP PARITY DELTA (safe to run multiple times) ==========================
create schema if not exists app;
create schema if not exists ip;

-- Guard helpers (used by RLS)
create or replace function app.current_tenant_id() returns uuid
language sql stable as $$ select nullif(current_setting('app.tenant_id', true),'')::uuid $$;

-- Enums
do $$
begin
  if not exists (select 1 from pg_type where typname='ip_event_state') then
    create type ip_event_state as enum ('pending','sent','failed');
  end if;
  if not exists (select 1 from pg_type where typname='ip_provider') then
    create type ip_provider as enum ('github','gitlab','notion','supabase','slack','mattermost','superset','odoo','web');
  end if;
  if not exists (select 1 from pg_type where typname='ip_channel') then
    create type ip_channel as enum ('email','slack','mattermost','webhook','push','system');
  end if;
end $$;

-- OAuth installations & tokens (ciphertexts only; use Vault/KMS for keys)
create table if not exists ip_oauth_connection (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  provider ip_provider not null,
  app_type text not null default 'app',
  account_login text,
  installation_id text,
  client_id text,
  scopes text[],
  access_token_ciphertext bytea,
  refresh_token_ciphertext bytea,
  token_expires_at timestamptz,
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists ip_oauth_connection_tenant_idx on ip_oauth_connection(tenant_id);
create unique index if not exists ip_oauth_unique_install on ip_oauth_connection(tenant_id, provider, coalesce(installation_id,''));

-- Webhook deliveries (ingress) + reliable outbox (egress)
create table if not exists ip_webhook_delivery (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  provider ip_provider not null,
  event text not null,
  signature text,
  payload jsonb not null,
  status text not null default 'received',
  response_code int,
  response_ms int,
  retried_count int not null default 0,
  next_retry_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists ip_webhook_delivery_tenant_created on ip_webhook_delivery(tenant_id, created_at desc);

create table if not exists ip_event_outbox (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  aggregate_type text not null,
  aggregate_id uuid,
  event_type text not null,
  payload jsonb not null,
  state ip_event_state not null default 'pending',
  last_error text,
  created_at timestamptz not null default now(),
  sent_at timestamptz
);
create index if not exists ip_event_outbox_tenant_state on ip_event_outbox(tenant_id, state, created_at);

-- Feature flags & secret references (pointer only)
create table if not exists ip_feature_flag (
  key text primary key,
  description text,
  default_on boolean not null default false,
  created_at timestamptz not null default now()
);
create table if not exists ip_feature_flag_override (
  key text references ip_feature_flag(key) on delete cascade,
  tenant_id uuid,
  subject_type text,        -- 'user' | 'project' | etc.
  subject_id uuid,
  enabled boolean not null,
  created_at timestamptz not null default now(),
  primary key (key, tenant_id, subject_type, subject_id)
);
create table if not exists ip_secret_ref (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  scope text not null,      -- 'oauth','webhook','workflow','superset'
  name text not null,
  provider text not null,   -- 'vault','env','supabase','do_secrets'
  locator text not null,    -- path/key/id, never the secret value
  created_at timestamptz not null default now()
);

-- n8n / workflow runs
create table if not exists ip_workflow (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  name text not null,
  source text not null default 'n8n',
  external_id text,
  config jsonb not null default '{}',
  created_at timestamptz not null default now()
);
create table if not exists ip_workflow_run (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  workflow_id uuid not null references ip_workflow(id) on delete cascade,
  status text not null default 'queued', -- queued|running|success|error
  started_at timestamptz,
  finished_at timestamptz,
  input jsonb not null default '{}',
  output jsonb,
  error text
);
create index if not exists ip_workflow_run_lookup on ip_workflow_run(tenant_id, workflow_id, started_at desc);

-- Superset embedding
create table if not exists ip_superset_dashboard (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  external_id text not null,
  title text,
  slug text,
  embed_uuid uuid,          -- for guest tokens / embed links
  rls jsonb not null default '{}',
  created_at timestamptz not null default now(),
  unique(tenant_id, external_id)
);

-- Knowledge base + search
create extension if not exists pg_trgm;
create table if not exists ip_kb_page (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  parent_id uuid references ip_kb_page(id) on delete cascade,
  title text not null,
  slug text not null,
  content_md text not null default '',
  content_html text,
  visibility text not null default 'private',
  version int not null default 1,
  tsv_document tsvector,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(tenant_id, parent_id, slug)
);
create index if not exists ip_kb_page_tsv on ip_kb_page using gin(tsv_document);

create or replace function ip_kb_tsv_update() returns trigger as $$
begin
  new.tsv_document := to_tsvector('english', coalesce(new.title,'') || ' ' || coalesce(new.content_md,''));
  return new;
end $$ language plpgsql;

do $$ begin
  if not exists (select 1 from pg_trigger where tgname='ip_kb_tsv_update_trg') then
    create trigger ip_kb_tsv_update_trg
    before insert or update on ip_kb_page
    for each row execute function ip_kb_tsv_update();
  end if;
end $$;

-- Embeddings (pgvector)
create extension if not exists vector;
create table if not exists ip_embedding (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  source_type text not null,            -- 'kb_page','doc','chat'
  source_id uuid,
  model text not null,
  dim int not null,
  vec vector(1536),
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now()
);
do $$ begin
  if not exists (select 1 from pg_indexes where indexname='ip_embedding_vec_idx') then
    create index ip_embedding_vec_idx on ip_embedding using ivfflat (vec vector_l2_ops) with (lists=100);
  end if;
end $$;

-- Chat bridge (Slack/Mattermost mirror)
create table if not exists ip_chat_workspace (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  provider ip_provider not null,  -- slack|mattermost
  external_id text not null,
  name text,
  created_at timestamptz not null default now(),
  unique(tenant_id, provider, external_id)
);
create table if not exists ip_chat_channel (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  workspace_id uuid not null references ip_chat_workspace(id) on delete cascade,
  external_id text not null,
  name text,
  created_at timestamptz not null default now(),
  unique(workspace_id, external_id)
);
create table if not exists ip_chat_message (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  channel_id uuid not null references ip_chat_channel(id) on delete cascade,
  external_id text,
  user_id uuid,
  body text not null,
  attachments jsonb not null default '[]',
  ts timestamptz not null default now()
);
create index if not exists ip_chat_message_lookup on ip_chat_message(channel_id, ts);

create table if not exists ip_chat_bridge (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  channel_id uuid not null references ip_chat_channel(id) on delete cascade,
  linked_model text not null,      -- e.g. 'project.task'
  linked_id text not null,         -- store Odoo id as text
  direction text not null default 'bi', -- in|out|bi
  created_at timestamptz not null default now(),
  unique (channel_id, linked_model, linked_id)
);

-- Observability & backups
create table if not exists ip_audit_log (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  actor_type text, actor_id uuid,
  action text not null,
  object_type text, object_id text,
  before jsonb, after jsonb,
  ip_address inet, user_agent text,
  created_at timestamptz not null default now()
);
create index if not exists ip_audit_log_tenant_created on ip_audit_log(tenant_id, created_at desc);

create table if not exists ip_health_check (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  component text not null,          -- 'odoo','superset','n8n','db'
  status text not null,             -- ok|degraded|down
  details jsonb not null default '{}',
  checked_at timestamptz not null default now()
);

create table if not exists ip_incident (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  title text not null,
  severity text not null,           -- sev1..sev4
  status text not null default 'open',
  timeline jsonb not null default '[]',
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);

create table if not exists ip_backup_snapshot (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  system text not null,             -- 'postgres','filestore','superset'
  location text not null,           -- s3/minio path
  size_bytes bigint,
  checksum text,
  created_at timestamptz not null default now()
);

-- Notifications
create table if not exists ip_notification (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  user_id uuid,
  kind text not null,               -- 'alert','reminder','system'
  title text not null,
  body text not null,
  channel ip_channel not null default 'system',
  send_after timestamptz default now(),
  sent_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists ip_notification_queue on ip_notification(tenant_id, channel, send_after);

-- Enable RLS and apply a generic tenant policy to all ip.* tables with tenant_id
do $$
declare r record;
begin
  for r in
    select c.table_schema, c.table_name
    from information_schema.columns c
    join information_schema.tables t
      on t.table_schema=c.table_schema and t.table_name=c.table_name and t.table_type='BASE TABLE'
    where c.table_schema in ('ip') and c.column_name='tenant_id'
  loop
    execute format('alter table %I.%I enable row level security;', r.table_schema, r.table_name);
    if not exists (
      select 1 from pg_policies
      where schemaname=r.table_schema and tablename=r.table_name and policyname='tenant_isolation'
    ) then
      execute format('create policy tenant_isolation on %I.%I using (tenant_id = app.current_tenant_id()) with check (tenant_id = app.current_tenant_id());', r.table_schema, r.table_name);
    end if;
  end loop;
end $$;
-- ===========================================================================

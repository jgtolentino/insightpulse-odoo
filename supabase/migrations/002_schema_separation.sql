-- Schema Separation: superset + ops
-- Purpose: Isolate Superset metadata from application tables

-- ============================================================================
-- SCHEMA CREATION
-- ============================================================================

-- Superset metadata schema (used via search_path in connection string)
create schema if not exists superset;
comment on schema superset is 'Apache Superset metadata tables (dashboards, charts, datasets)';

-- Operations schema for application tables
create schema if not exists ops;
comment on schema ops is 'InsightPulse application operations data';

-- Grant usage to service roles
grant usage on schema superset to postgres, authenticated, service_role;
grant usage on schema ops to postgres, authenticated, service_role;

-- ============================================================================
-- SUPERSET SCHEMA
-- ============================================================================

-- Superset will create its own tables via `superset db upgrade`
-- We just ensure the schema exists and is isolated via search_path parameter:
-- postgresql://...?options=-csearch_path%3Dsuperset

-- ============================================================================
-- OPS SCHEMA - Application Tables
-- ============================================================================

-- Task Queue (already created in scout_bronze, migrate to ops)
create table if not exists ops.task_queue (
  id bigserial primary key,
  kind text not null check (kind in (
    'DEPLOY_WEB', 'DEPLOY_ADE', 'DOCS_SYNC', 'CLIENT_OP', 'DB_OP',
    'RUNBOT_SYNC', 'ODOO_BUILD', 'ODOO_INSTALL_TEST', 'ODOO_MIGRATE_MODULE',
    'ODOO_VISUAL_DIFF', 'ODOO_PACKAGE_RELEASE'
  )),
  payload jsonb not null default '{}'::jsonb,
  status text not null default 'pending' check (status in (
    'pending', 'processing', 'completed', 'failed', 'cancelled'
  )),
  pr_number integer,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  completed_at timestamptz,
  error_message text
);

create index if not exists idx_task_queue_status on ops.task_queue(status, created_at);
create index if not exists idx_task_queue_kind on ops.task_queue(kind);
create index if not exists idx_task_queue_pr on ops.task_queue(pr_number) where pr_number is not null;

comment on table ops.task_queue is 'Task bus for deployment, build, and automation workflows';

-- Visual Parity Registry
create table if not exists ops.visual_baseline (
  id bigserial primary key,
  route text not null,
  viewport text not null check (viewport in ('mobile', 'desktop')),
  odoo_version text not null default '19.0',
  screenshot_data bytea not null,
  screenshot_hash text not null,
  created_at timestamptz not null default now()
);

create unique index if not exists idx_visual_baseline_route_viewport
  on ops.visual_baseline(route, viewport, odoo_version);

comment on table ops.visual_baseline is 'Baseline screenshots for visual parity testing';

create table if not exists ops.visual_result (
  id bigserial primary key,
  baseline_id bigint references ops.visual_baseline(id) on delete cascade,
  pr_number integer,
  route text not null,
  viewport text not null,
  ssim_score numeric(5,4),
  passed boolean not null,
  screenshot_data bytea,
  diff_image bytea,
  created_at timestamptz not null default now()
);

create index if not exists idx_visual_result_pr on ops.visual_result(pr_number);
create index if not exists idx_visual_result_baseline on ops.visual_result(baseline_id);

comment on table ops.visual_result is 'Visual parity test results with SSIM scores';

-- Forum Posts (MCP knowledge base)
create table if not exists ops.forum_posts (
  id bigserial primary key,
  post_id text unique not null,
  title text not null,
  content text not null,
  author text,
  category text,
  tags text[],
  url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists idx_forum_posts_search on ops.forum_posts using gin(to_tsvector('english', title || ' ' || content));
create index if not exists idx_forum_posts_category on ops.forum_posts(category);
create index if not exists idx_forum_posts_tags on ops.forum_posts using gin(tags);

comment on table ops.forum_posts is 'Scraped Odoo forum posts for MCP knowledge base';

-- ============================================================================
-- RPC FUNCTIONS (ops schema)
-- ============================================================================

-- Task queue enqueue function
create or replace function ops.route_and_enqueue(
  p_kind text,
  p_payload jsonb default '{}'::jsonb,
  p_pr_number integer default null
)
returns bigint
language plpgsql
security definer
as $$
declare
  v_task_id bigint;
begin
  insert into ops.task_queue (kind, payload, pr_number)
  values (p_kind, p_payload, p_pr_number)
  returning id into v_task_id;

  return v_task_id;
end;
$$;

comment on function ops.route_and_enqueue is 'Enqueue task for automated workflows';

-- Visual parity snapshot function
create or replace function ops.snapshot_visual_baseline(
  p_route text,
  p_viewport text,
  p_odoo_version text,
  p_screenshot_data bytea
)
returns bigint
language plpgsql
security definer
as $$
declare
  v_hash text;
  v_baseline_id bigint;
begin
  -- Generate hash
  v_hash := encode(digest(p_screenshot_data, 'sha256'), 'hex');

  -- Upsert baseline
  insert into ops.visual_baseline (route, viewport, odoo_version, screenshot_data, screenshot_hash)
  values (p_route, p_viewport, p_odoo_version, p_screenshot_data, v_hash)
  on conflict (route, viewport, odoo_version)
  do update set
    screenshot_data = excluded.screenshot_data,
    screenshot_hash = excluded.screenshot_hash,
    created_at = now()
  returning id into v_baseline_id;

  return v_baseline_id;
end;
$$;

comment on function ops.snapshot_visual_baseline is 'Store or update visual parity baseline screenshot';

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

-- Grant ops schema permissions
grant all on all tables in schema ops to postgres, service_role;
grant select, insert, update on all tables in schema ops to authenticated;
grant all on all sequences in schema ops to postgres, service_role, authenticated;
grant execute on all functions in schema ops to postgres, service_role, authenticated;

-- Default permissions for future objects
alter default privileges in schema ops grant all on tables to postgres, service_role;
alter default privileges in schema ops grant select, insert, update on tables to authenticated;
alter default privileges in schema ops grant all on sequences to postgres, service_role, authenticated;

-- ============================================================================
-- MIGRATION NOTES
-- ============================================================================

-- If task_queue already exists in scout_bronze, migrate data:
-- INSERT INTO ops.task_queue SELECT * FROM scout_bronze.task_queue;
-- DROP TABLE scout_bronze.task_queue;

-- Superset connection string should use search_path:
-- postgresql://user:pass@host:port/db?options=-csearch_path%3Dsuperset

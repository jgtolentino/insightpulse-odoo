-- LLM Metrics Dataset for Superset
-- ----------------------------------
-- Tracks LLM router performance, costs, and quality metrics

-- Main metrics view
create or replace view superset.llm_metrics_daily as
select
  date_trunc('day', created_at) as metric_date,
  task_type,
  provider,
  model,
  count(*) as request_count,
  avg(accuracy) as avg_accuracy,
  percentile_cont(0.95) within group (order by latency_ms) as p95_latency_ms,
  avg(latency_ms) as avg_latency_ms,
  sum(cost_usd) as total_cost_usd,
  avg(cost_usd) as avg_cost_usd,
  sum(tokens_used) as total_tokens,
  count(*) filter (where success = true) as success_count,
  count(*) filter (where success = false) as failure_count,
  (count(*) filter (where success = true))::float / nullif(count(*), 0) as success_rate,
  avg(fallback_count) as avg_fallback_count
from ip.llm_request_log
where created_at >= current_date - interval '90 days'
group by 1, 2, 3, 4;

-- Cost tracking by tenant
create or replace view superset.llm_cost_by_tenant as
select
  date_trunc('day', created_at) as metric_date,
  tenant_id,
  t.name as tenant_name,
  task_type,
  provider,
  sum(cost_usd) as daily_cost_usd,
  count(*) as request_count,
  sum(tokens_used) as total_tokens
from ip.llm_request_log l
join tenants t on t.id = l.tenant_id
where created_at >= current_date - interval '90 days'
group by 1, 2, 3, 4, 5;

-- Quality metrics (accuracy trends)
create or replace view superset.llm_quality_trends as
select
  date_trunc('day', created_at) as metric_date,
  task_type,
  provider,
  avg(accuracy) as avg_accuracy,
  stddev(accuracy) as accuracy_stddev,
  percentile_cont(0.5) within group (order by accuracy) as p50_accuracy,
  percentile_cont(0.95) within group (order by accuracy) as p95_accuracy,
  count(*) filter (where accuracy < 0.90) as low_accuracy_count
from ip.llm_request_log
where created_at >= current_date - interval '90 days'
  and accuracy is not null
group by 1, 2, 3;

-- Provider performance comparison
create or replace view superset.llm_provider_comparison as
select
  provider,
  model,
  count(*) as total_requests,
  avg(accuracy) as avg_accuracy,
  avg(latency_ms) as avg_latency_ms,
  percentile_cont(0.95) within group (order by latency_ms) as p95_latency_ms,
  sum(cost_usd) as total_cost_usd,
  avg(cost_usd) as avg_cost_per_request,
  (count(*) filter (where success = true))::float / nullif(count(*), 0) as success_rate,
  avg(fallback_count) as avg_fallback_count
from ip.llm_request_log
where created_at >= current_date - interval '30 days'
group by 1, 2
order by total_requests desc;

-- Prompt performance (by prompt_id from registry)
create or replace view superset.llm_prompt_performance as
select
  prompt_id,
  prompt_version,
  task_type,
  count(*) as request_count,
  avg(accuracy) as avg_accuracy,
  avg(latency_ms) as avg_latency_ms,
  sum(cost_usd) as total_cost_usd,
  (count(*) filter (where success = true))::float / nullif(count(*), 0) as success_rate,
  max(created_at) as last_used_at
from ip.llm_request_log
where created_at >= current_date - interval '30 days'
  and prompt_id is not null
group by 1, 2, 3;

-- Budget burn rate
create or replace view superset.llm_budget_burn as
select
  date_trunc('day', created_at) as metric_date,
  tenant_id,
  sum(sum(cost_usd)) over (partition by tenant_id order by date_trunc('day', created_at)) as cumulative_cost_usd,
  sum(cost_usd) as daily_cost_usd,
  count(*) as daily_requests
from ip.llm_request_log
where created_at >= date_trunc('month', current_date)
group by 1, 2;

-- Guardrail triggers
create or replace view superset.llm_guardrail_triggers as
select
  date_trunc('day', created_at) as metric_date,
  guardrail_type,
  count(*) as trigger_count,
  count(distinct tenant_id) as affected_tenants,
  count(distinct user_id) as affected_users
from ip.llm_guardrail_log
where created_at >= current_date - interval '90 days'
group by 1, 2;

-- Create base table if it doesn't exist (for router to log to)
create table if not exists ip.llm_request_log (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  user_id uuid,
  task_type text not null,
  prompt_id text,
  prompt_version text,
  provider text not null,
  model text not null,
  accuracy float,
  latency_ms float not null,
  cost_usd float not null,
  tokens_used int not null,
  success boolean not null default true,
  fallback_count int not null default 0,
  error_message text,
  metadata jsonb not null default '{}',
  created_at timestamptz not null default now()
);

create index if not exists llm_request_log_tenant_date_idx on ip.llm_request_log(tenant_id, created_at desc);
create index if not exists llm_request_log_task_provider_idx on ip.llm_request_log(task_type, provider, created_at desc);
create index if not exists llm_request_log_prompt_idx on ip.llm_request_log(prompt_id, created_at desc);

create table if not exists ip.llm_guardrail_log (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  user_id uuid,
  guardrail_type text not null,
  trigger_reason text not null,
  input_preview text,
  severity text not null default 'medium',
  created_at timestamptz not null default now()
);

create index if not exists llm_guardrail_log_tenant_date_idx on ip.llm_guardrail_log(tenant_id, created_at desc);

-- Enable RLS
alter table ip.llm_request_log enable row level security;
alter table ip.llm_guardrail_log enable row level security;

create policy tenant_isolation on ip.llm_request_log
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

create policy tenant_isolation on ip.llm_guardrail_log
  using (tenant_id = app.current_tenant_id())
  with check (tenant_id = app.current_tenant_id());

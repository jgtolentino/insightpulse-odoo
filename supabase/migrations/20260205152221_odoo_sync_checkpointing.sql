create schema if not exists ops;

-- Per-model sync config + checkpoints
create table if not exists ops.odoo_sync_config (
  key text primary key,
  value jsonb not null default '{}'::jsonb,
  updated_at timestamptz not null default now()
);

-- Example config keys:
--  key='odoo_to_sb:res.partner' value={"domain":[["is_company","=",true]],"fields":["id","name","email","phone","write_date"],"page_size":200}
--  key='sb_to_odoo:res.partner' value={"max_batch":50,"max_attempts":5}

create table if not exists ops.odoo_sync_checkpoints (
  key text primary key,                -- e.g. 'odoo_to_sb:res.partner'
  cursor jsonb not null default '{}'::jsonb,  -- e.g. {"offset":0,"last_write_date":"..."} (choose strategy)
  updated_at timestamptz not null default now()
);

-- Outbox: add next_run_at + backoff support
alter table ops.odoo_outbox
  add column if not exists next_run_at timestamptz not null default now();

create index if not exists odoo_outbox_next_run_idx
  on ops.odoo_outbox(status, next_run_at);

-- Default configs (safe upserts)
insert into ops.odoo_sync_config(key, value)
values
('odoo_to_sb:res.partner', jsonb_build_object(
  'domain', jsonb_build_array(jsonb_build_array('is_company','=',true)),
  'fields', jsonb_build_array('id','name','email','phone','write_date'),
  'page_size', 200
)),
('sb_to_odoo:res.partner', jsonb_build_object(
  'max_batch', 50,
  'max_attempts', 5,
  'base_backoff_seconds', 10
))
on conflict (key) do update set value = excluded.value, updated_at = now();

insert into ops.odoo_sync_checkpoints(key, cursor)
values
('odoo_to_sb:res.partner', jsonb_build_object('offset', 0))
on conflict (key) do nothing;

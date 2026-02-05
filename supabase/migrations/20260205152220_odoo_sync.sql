-- Odoo <-> Supabase sync primitives (idempotent-ish)
create schema if not exists ops;

-- Track runs (optional but useful)
create table if not exists ops.odoo_sync_runs (
  id bigserial primary key,
  direction text not null check (direction in ('odoo_to_sb','sb_to_odoo')),
  status text not null default 'queued' check (status in ('queued','running','succeeded','failed')),
  created_at timestamptz not null default now(),
  started_at timestamptz,
  finished_at timestamptz,
  meta jsonb not null default '{}'::jsonb,
  error text
);

-- Queue of outbound events from Supabase to Odoo (write-behind)
create table if not exists ops.odoo_outbox (
  id bigserial primary key,
  model text not null,                 -- e.g., res.partner
  operation text not null,             -- upsert|delete
  payload jsonb not null,              -- arbitrary
  idempotency_key text not null,       -- caller-provided
  status text not null default 'queued' check (status in ('queued','processing','done','failed')),
  attempts int not null default 0,
  locked_at timestamptz,
  locked_by text,
  last_error text,
  created_at timestamptz not null default now()
);

create unique index if not exists odoo_outbox_idem_uq
  on ops.odoo_outbox(idempotency_key);

create index if not exists odoo_outbox_status_idx
  on ops.odoo_outbox(status, created_at);

-- Optional: a simple mirror table for demo (partners)
create table if not exists public.odoo_partners (
  odoo_id bigint primary key,
  name text,
  email text,
  phone text,
  write_date timestamptz,
  raw jsonb not null default '{}'::jsonb,
  synced_at timestamptz not null default now()
);

-- Helper: enqueue changes from Supabase into outbox (example for partners)
create or replace function ops.enqueue_odoo_partner_upsert()
returns trigger
language plpgsql
as $$
declare
  idem text;
begin
  -- idempotency: stable key per record + updated_at if present; fallback to txid
  idem := 'partner:' || coalesce(new.odoo_id::text, '0') || ':' || txid_current()::text;

  insert into ops.odoo_outbox(model, operation, payload, idempotency_key)
  values (
    'res.partner',
    'upsert',
    jsonb_build_object(
      'odoo_id', new.odoo_id,
      'name', new.name,
      'email', new.email,
      'phone', new.phone
    ),
    idem
  )
  on conflict (idempotency_key) do nothing;

  return new;
end;
$$;

drop trigger if exists trg_enqueue_partner on public.odoo_partners;
create trigger trg_enqueue_partner
after insert or update on public.odoo_partners
for each row execute function ops.enqueue_odoo_partner_upsert();

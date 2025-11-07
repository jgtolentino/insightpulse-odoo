-- schema
create schema if not exists analytics;

create table if not exists analytics.ip_ocr_receipts (
  id            bigint generated always as identity primary key,
  filename      text not null,
  uploaded_by   text,
  created_at    timestamptz default now(),
  line_count    int,
  receipt_date  date,
  total_amount  numeric(14,2),
  vat_amount    numeric(14,2),
  bir_atp       text,
  tin           text,
  payload       jsonb not null,
  source        text not null default 'odoo',
  dedupe_key    text unique
);

-- fast filters
create index if not exists idx_ip_ocr_receipts_created_at on analytics.ip_ocr_receipts (created_at);
create index if not exists idx_ip_ocr_receipts_dedupe on analytics.ip_ocr_receipts (dedupe_key);

-- simple daily rollup for Superset
create or replace view analytics.v_ip_ocr_receipts_daily as
select
  date_trunc('day', created_at) as day,
  count(*)                      as receipts
from analytics.ip_ocr_receipts
group by 1
order by 1;

-- RLS
alter table analytics.ip_ocr_receipts enable row level security;

-- service role: full access (used by server-side key ONLY)
create policy ip_ocr_srv_ins
on analytics.ip_ocr_receipts
as permissive for insert
to service_role
with check (true);

create policy ip_ocr_srv_sel
on analytics.ip_ocr_receipts
as permissive for select
to service_role
using (true);

-- optional: authenticated read-only
create policy ip_ocr_auth_sel
on analytics.ip_ocr_receipts
for select
to authenticated
using (true);

-- idempotent upsert RPC (preferred from Odoo)
create or replace function analytics.upsert_ip_ocr_receipt(
  p_filename text,
  p_uploaded_by text,
  p_line_count int,
  p_receipt_date date,
  p_total_amount numeric,
  p_vat_amount numeric,
  p_bir_atp text,
  p_tin text,
  p_payload jsonb,
  p_dedupe_key text
) returns bigint
language plpgsql
security definer
as $$
declare v_id bigint;
begin
  insert into analytics.ip_ocr_receipts(
    filename, uploaded_by, line_count, receipt_date, total_amount, vat_amount,
    bir_atp, tin, payload, dedupe_key
  )
  values (
    p_filename, p_uploaded_by, p_line_count, p_receipt_date, p_total_amount, p_vat_amount,
    p_bir_atp, p_tin, p_payload, p_dedupe_key
  )
  on conflict (dedupe_key) do update set
    uploaded_by  = excluded.uploaded_by,
    line_count   = excluded.line_count,
    receipt_date = excluded.receipt_date,
    total_amount = excluded.total_amount,
    vat_amount   = excluded.vat_amount,
    bir_atp      = excluded.bir_atp,
    tin          = excluded.tin,
    payload      = excluded.payload
  returning id into v_id;
  return v_id;
end $$;

-- Skillsmith: Auto-skill builder schema
-- Normalizes and fingerprints errors for pattern mining

create extension if not exists pgcrypto;

-- Strip volatile bits from messages (UUIDs, ids, timestamps) to improve clustering
create or replace function public.normalize_error_message(txt text)
returns text language sql immutable as $$
  select regexp_replace(
           regexp_replace(
             regexp_replace(
               regexp_replace(coalesce($1,''), '\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b','<uuid>','gi'),
               '\b\d{13,}\b','<epoch>','g'),
             '\b\d{6,}\b','<int>','g'),
           '\b20\d{2}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\b','<ts>','g');
$$;

-- Stable fingerprint for clustering (type + component + normalized message)
create or replace function public.error_fingerprint(_type text, _component text, _msg text)
returns uuid language sql immutable as $$
  select ('00000000-0000-0000-0000-' ||
          substr(encode(digest(coalesce($1,'')||'|'||coalesce($2,'')||'|'||public.normalize_error_message($3),'md5'),'hex'),9))::uuid;
$$;

-- Rollup of recent errors into signatures
create materialized view if not exists public.error_signatures as
select
  public.error_fingerprint(e.error, e.component, e.error) as fp,
  e.component,
  split_part(coalesce(e.error,''),' ',1) as kind,
  public.normalize_error_message(e.error) as norm_msg,
  count(*) as hits_30d,
  count(*) filter (where e.ts > now() - interval '7 days') as hits_7d,
  array_agg(distinct e.tags) as tags
from public.agent_errors e
where e.ts > now() - interval '30 days'
group by 1,2,3,4;

create index if not exists idx_error_signatures_fp on public.error_signatures(fp);

-- Support view: top candidates by volume & recency
create or replace view public.error_candidates as
select *,
  (hits_7d*0.7 + hits_30d*0.3) as impact_score
from public.error_signatures
where hits_7d > 1
order by impact_score desc;

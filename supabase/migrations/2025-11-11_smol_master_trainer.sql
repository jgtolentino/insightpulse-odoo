-- === Schema =================================================================
create schema if not exists smol;

-- === Tables =================================================================
create table if not exists smol.ml_datasets (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  url text,
  license text,
  split text check (split in ('train','val','test')) default 'train',
  checksum text,
  bytes bigint check (bytes >= 0),
  created_at timestamptz not null default now()
);

create table if not exists smol.ml_eval_runs (
  id uuid primary key default gen_random_uuid(),
  cfg jsonb not null default '{}'::jsonb,
  scores jsonb not null default '{}'::jsonb,
  passed boolean not null default false,
  notes text,
  created_at timestamptz not null default now()
);

create table if not exists smol.ml_artifacts (
  id uuid primary key default gen_random_uuid(),
  cfg jsonb not null default '{}'::jsonb,
  path text not null,
  sha256 text,
  eval_id uuid references smol.ml_eval_runs(id) on delete set null,
  promoted boolean not null default false,
  created_at timestamptz not null default now()
);

-- === RLS ====================================================================
alter table smol.ml_datasets   enable row level security;
alter table smol.ml_eval_runs  enable row level security;
alter table smol.ml_artifacts  enable row level security;

-- Read policies for authenticated users
do $$
begin
  perform 1 from pg_policies where schemaname='smol' and tablename='ml_datasets'   and policyname='ml_datasets_select_auth';
  if not found then create policy ml_datasets_select_auth   on smol.ml_datasets  for select to authenticated using (true); end if;

  perform 1 from pg_policies where schemaname='smol' and tablename='ml_eval_runs'  and policyname='ml_eval_runs_select_auth';
  if not found then create policy ml_eval_runs_select_auth  on smol.ml_eval_runs   for select to authenticated using (true); end if;

  perform 1 from pg_policies where schemaname='smol' and tablename='ml_artifacts'  and policyname='ml_artifacts_select_auth';
  if not found then create policy ml_artifacts_select_auth  on smol.ml_artifacts   for select to authenticated using (true); end if;
end $$;

-- Write policies for authenticated users
do $$
begin
  perform 1 from pg_policies where schemaname='smol' and tablename='ml_datasets'   and policyname='ml_datasets_insert_auth';
  if not found then create policy ml_datasets_insert_auth   on smol.ml_datasets  for insert to authenticated with check (true); end if;

  perform 1 from pg_policies where schemaname='smol' and tablename='ml_eval_runs'  and policyname='ml_eval_runs_insert_auth';
  if not found then create policy ml_eval_runs_insert_auth  on smol.ml_eval_runs   for insert to authenticated with check (true); end if;

  perform 1 from pg_policies where schemaname='smol' and tablename='ml_artifacts'  and policyname='ml_artifacts_insert_auth';
  if not found then create policy ml_artifacts_insert_auth  on smol.ml_artifacts   for insert to authenticated with check (true); end if;
end $$;

-- === Buckets (Supabase Storage) ============================================
-- Create private buckets for raw/clean/artifacts
insert into storage.buckets (id, name, public) values
  ('smol-ml-raw',       'smol-ml-raw',       false),
  ('smol-ml-clean',     'smol-ml-clean',     false),
  ('smol-ml-artifacts', 'smol-ml-artifacts', false)
on conflict (id) do nothing;

-- Storage RLS policies
do $$
begin
  perform 1 from pg_policies where schemaname='storage' and tablename='objects' and policyname='read_smol_ml_clean_auth';
  if not found then create policy read_smol_ml_clean_auth
    on storage.objects for select to authenticated using (bucket_id = 'smol-ml-clean'); end if;

  perform 1 from pg_policies where schemaname='storage' and tablename='objects' and policyname='read_smol_ml_artifacts_auth';
  if not found then create policy read_smol_ml_artifacts_auth
    on storage.objects for select to authenticated using (bucket_id = 'smol-ml-artifacts'); end if;

  perform 1 from pg_policies where schemaname='storage' and tablename='objects' and policyname='write_smol_ml_clean_auth';
  if not found then create policy write_smol_ml_clean_auth
    on storage.objects for insert to authenticated with check (bucket_id = 'smol-ml-clean'); end if;

  perform 1 from pg_policies where schemaname='storage' and tablename='objects' and policyname='write_smol_ml_artifacts_auth';
  if not found then create policy write_smol_ml_artifacts_auth
    on storage.objects for insert to authenticated with check (bucket_id = 'smol-ml-artifacts'); end if;
end $$;

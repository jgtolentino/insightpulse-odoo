-- ============================================================================
-- SaaS Feature Matrix Schema
-- ============================================================================
-- Purpose: Track which SaaS features are covered by Odoo CE/OCA/ipai modules
-- Usage: Central source of truth for reverse mapping agent
-- ============================================================================

-- 1. SaaS Products Registry
-- ============================================================================
create table if not exists saas_products (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  name text not null,
  homepage_url text,
  active boolean default true,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

comment on table saas_products is 'Registry of SaaS products being replaced with Odoo CE parity';
comment on column saas_products.slug is 'URL-safe identifier (e.g., cheqroom, concur_expense, notion_business)';
comment on column saas_products.homepage_url is 'Official product website for reference';

-- 2. Feature Status Enum
-- ============================================================================
create type saas_feature_status as enum ('covered', 'partial', 'gap');

comment on type saas_feature_status is 'Coverage status: covered (100%), partial (50-99%), gap (0-49%)';

-- 3. Feature → Odoo Mapping
-- ============================================================================
create table if not exists saas_feature_mappings (
  id uuid primary key default gen_random_uuid(),
  saas_product_id uuid not null references saas_products(id) on delete cascade,
  feature_key text not null,
  feature_name text not null,
  category text,
  status saas_feature_status not null,
  criticality int default 3 check (criticality between 1 and 5),

  -- Odoo module mapping
  odoo_core_modules text[] default '{}',
  oca_modules text[] default '{}',
  ipai_modules text[] default '{}',

  -- Enterprise reference (not installed)
  enterprise_equiv text[] default '{}',

  -- Gap tracking
  requires_ipai text[] default '{}',

  notes text,
  created_at timestamptz default now(),
  updated_at timestamptz default now(),

  unique(saas_product_id, feature_key)
);

comment on table saas_feature_mappings is 'Maps SaaS features to Odoo CE/OCA/ipai modules with gap tracking';
comment on column saas_feature_mappings.feature_key is 'Unique identifier within product (e.g., equipment_catalog, expense_submission)';
comment on column saas_feature_mappings.criticality is '1=Nice-to-have, 5=Business-critical';
comment on column saas_feature_mappings.odoo_core_modules is 'CE core modules providing this feature';
comment on column saas_feature_mappings.oca_modules is 'OCA community modules required';
comment on column saas_feature_mappings.ipai_modules is 'Custom ipai_* modules implemented';
comment on column saas_feature_mappings.enterprise_equiv is 'Enterprise modules that would provide this (for reference only)';
comment on column saas_feature_mappings.requires_ipai is 'List of ipai_* modules needed to close gap';

-- 4. Artifact Tracking
-- ============================================================================
create table if not exists saas_feature_artifacts (
  id uuid primary key default gen_random_uuid(),
  feature_mapping_id uuid not null references saas_feature_mappings(id) on delete cascade,
  artifact_type text not null check (artifact_type in ('prd', 'module', 'n8n_workflow', 'test', 'doc')),
  path text,
  ref text,
  url text,
  created_at timestamptz default now(),

  unique(feature_mapping_id, artifact_type, path)
);

comment on table saas_feature_artifacts is 'Links features to PRDs, modules, tests, and automation';
comment on column saas_feature_artifacts.artifact_type is 'Type: prd, module, n8n_workflow, test, doc';
comment on column saas_feature_artifacts.path is 'File path in repository';
comment on column saas_feature_artifacts.ref is 'Git commit hash or branch reference';
comment on column saas_feature_artifacts.url is 'External URL (e.g., n8n workflow, GitHub issue)';

-- 5. Indexes
-- ============================================================================
create index idx_saas_feature_mappings_product on saas_feature_mappings(saas_product_id);
create index idx_saas_feature_mappings_status on saas_feature_mappings(status);
create index idx_saas_feature_mappings_criticality on saas_feature_mappings(criticality desc);
create index idx_saas_feature_artifacts_mapping on saas_feature_artifacts(feature_mapping_id);
create index idx_saas_feature_artifacts_type on saas_feature_artifacts(artifact_type);

-- 6. RLS Policies
-- ============================================================================
alter table saas_products enable row level security;
alter table saas_feature_mappings enable row level security;
alter table saas_feature_artifacts enable row level security;

-- Allow authenticated users to read all data
create policy "Allow read access for authenticated users"
  on saas_products for select
  using (auth.role() = 'authenticated');

create policy "Allow read access for authenticated users"
  on saas_feature_mappings for select
  using (auth.role() = 'authenticated');

create policy "Allow read access for authenticated users"
  on saas_feature_artifacts for select
  using (auth.role() = 'authenticated');

-- Allow service role full access
create policy "Allow service role full access"
  on saas_products for all
  using (auth.role() = 'service_role');

create policy "Allow service role full access"
  on saas_feature_mappings for all
  using (auth.role() = 'service_role');

create policy "Allow service role full access"
  on saas_feature_artifacts for all
  using (auth.role() = 'service_role');

-- 7. Updated Timestamp Trigger
-- ============================================================================
create or replace function update_updated_at_column()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger update_saas_products_updated_at
  before update on saas_products
  for each row execute procedure update_updated_at_column();

create trigger update_saas_feature_mappings_updated_at
  before update on saas_feature_mappings
  for each row execute procedure update_updated_at_column();

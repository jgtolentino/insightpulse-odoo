-- Medallion starter for IPAI bridges
create schema if not exists scout_bronze;
create schema if not exists scout_silver;
create schema if not exists scout_gold;

-- Concur (SAE-like)
create table if not exists scout_bronze.expense_raw (
  id bigserial primary key,
  payload jsonb not null,
  source text default 'concur',
  ingested_at timestamptz default now()
);

-- Ariba cXML
create table if not exists scout_bronze.ariba_cxml (
  id bigserial primary key,
  doc_type text not null,       -- PO|Invoice
  xml text not null,
  ingested_at timestamptz default now()
);

-- Salesforce CRM
create table if not exists scout_bronze.crm_accounts (
  external_id text primary key,
  payload jsonb not null,
  ingested_at timestamptz default now()
);

-- Clarity PPM
create table if not exists scout_bronze.ppm_projects (
  external_id text primary key,
  payload jsonb not null,
  ingested_at timestamptz default now()
);

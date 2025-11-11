-- Migration 004: BIR Transaction Tables for Multi-Form Batch Generator
-- Purpose: Create tables for BIR tax compliance workflows (Forms 1601-C, 2550Q/M, 2307)
-- Multi-tenant: All tables use company_id + tenant_id with RLS policies

-- Ensure scout schema exists (create if not present)
CREATE SCHEMA IF NOT EXISTS scout;

-- ============================================================================
-- Table 1: scout.transactions (Withholding Tax Transactions)
-- Purpose: Store WHT transactions for Form 1601-C and 2307 generation
-- ============================================================================

CREATE TABLE scout.transactions (
  id BIGSERIAL PRIMARY KEY,

  -- Multi-tenant isolation (REQUIRED for company separation)
  company_id INTEGER NOT NULL,
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

  -- Transaction details
  transaction_date DATE NOT NULL,
  transaction_type TEXT NOT NULL CHECK (transaction_type IN ('withholding_tax', 'vat_output', 'vat_input')),

  -- Vendor/Payee information (recipient of payment)
  payee_tin TEXT NOT NULL,  -- Format: 123-456-789-000
  payee_name TEXT NOT NULL,

  -- Financial details
  income_payment NUMERIC(18,2) NOT NULL,  -- Gross amount paid
  atc_code TEXT NOT NULL,  -- BIR ATC code (e.g., WC010, WI050)
  tax_rate NUMERIC(5,4) NOT NULL,  -- e.g., 0.01 = 1%, 0.15 = 15%
  amount_withheld NUMERIC(18,2) NOT NULL,  -- Tax withheld amount

  -- Payor/Company information (entity making payment)
  payor_tin TEXT NOT NULL,
  payor_name TEXT NOT NULL,

  -- Metadata
  reference_number TEXT,  -- Invoice/PO number
  description TEXT,

  -- Audit trail
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES users(id),

  -- Constraints
  CONSTRAINT check_positive_amounts CHECK (income_payment >= 0 AND amount_withheld >= 0),
  CONSTRAINT check_tax_rate CHECK (tax_rate >= 0 AND tax_rate <= 1)
);

-- Performance indexes
CREATE INDEX idx_transactions_company_date ON scout.transactions(company_id, transaction_date DESC);
CREATE INDEX idx_transactions_type ON scout.transactions(transaction_type);
CREATE INDEX idx_transactions_payee_tin ON scout.transactions(payee_tin);
CREATE INDEX idx_transactions_atc_code ON scout.transactions(atc_code);
CREATE INDEX idx_transactions_tenant ON scout.transactions(tenant_id);

-- Row Level Security (Multi-tenant isolation)
ALTER TABLE scout.transactions ENABLE ROW LEVEL SECURITY;

-- Policy 1: Tenant-based access (regular users)
CREATE POLICY transaction_tenant_policy ON scout.transactions
  FOR ALL
  USING (tenant_id = ANY(COALESCE(auth.user_tenant_ids(), ARRAY[]::uuid[])));

-- Policy 2: Service role bypass (for backend agent operations)
CREATE POLICY transaction_service_role_policy ON scout.transactions
  FOR ALL
  USING (auth.role() = 'service_role');

COMMENT ON TABLE scout.transactions IS 'BIR withholding tax transactions for Form 1601-C and 2307 generation';
COMMENT ON COLUMN scout.transactions.company_id IS 'Odoo res.company ID for multi-tenant legal entity isolation';
COMMENT ON COLUMN scout.transactions.atc_code IS 'BIR Alphanumeric Tax Code (e.g., WC010=1% prof fees, WI050=15% interest)';

-- ============================================================================
-- Table 2: scout.vat_transactions (VAT Transactions)
-- Purpose: Store VAT transactions for Form 2550Q/M generation
-- ============================================================================

CREATE TABLE scout.vat_transactions (
  id BIGSERIAL PRIMARY KEY,

  -- Multi-tenant isolation
  company_id INTEGER NOT NULL,
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

  -- Period (monthly or quarterly)
  month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
  year INTEGER NOT NULL CHECK (year BETWEEN 2020 AND 2100),

  -- Transaction type
  transaction_type TEXT NOT NULL CHECK (transaction_type IN ('vat_output', 'vat_input', 'vat_exempt', 'vat_zero_rated')),

  -- Financial details
  total_sales NUMERIC(18,2) NOT NULL DEFAULT 0,
  vat_exempt_sales NUMERIC(18,2) NOT NULL DEFAULT 0,
  vat_zero_rated NUMERIC(18,2) NOT NULL DEFAULT 0,
  taxable_sales NUMERIC(18,2) NOT NULL DEFAULT 0,
  vat_amount NUMERIC(18,2) NOT NULL DEFAULT 0,

  -- Vendor/Customer information
  partner_tin TEXT,
  partner_name TEXT,

  -- Metadata
  reference_number TEXT,
  description TEXT,

  -- Audit trail
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by UUID REFERENCES users(id),

  -- Constraints
  CONSTRAINT check_vat_positive CHECK (
    total_sales >= 0 AND
    vat_exempt_sales >= 0 AND
    vat_zero_rated >= 0 AND
    taxable_sales >= 0 AND
    vat_amount >= 0
  ),
  CONSTRAINT check_vat_period UNIQUE (company_id, month, year, transaction_type, COALESCE(reference_number, ''))
);

-- Performance indexes
CREATE INDEX idx_vat_transactions_company_period ON scout.vat_transactions(company_id, year DESC, month DESC);
CREATE INDEX idx_vat_transactions_type ON scout.vat_transactions(transaction_type);
CREATE INDEX idx_vat_transactions_tenant ON scout.vat_transactions(tenant_id);

-- Row Level Security
ALTER TABLE scout.vat_transactions ENABLE ROW LEVEL SECURITY;

-- Policy 1: Tenant-based access
CREATE POLICY vat_transaction_tenant_policy ON scout.vat_transactions
  FOR ALL
  USING (tenant_id = ANY(COALESCE(auth.user_tenant_ids(), ARRAY[]::uuid[])));

-- Policy 2: Service role bypass
CREATE POLICY vat_transaction_service_role_policy ON scout.vat_transactions
  FOR ALL
  USING (auth.role() = 'service_role');

COMMENT ON TABLE scout.vat_transactions IS 'BIR VAT transactions for Form 2550Q (quarterly) and 2550M (monthly) generation';
COMMENT ON COLUMN scout.vat_transactions.company_id IS 'Odoo res.company ID for multi-tenant legal entity isolation';

-- ============================================================================
-- Table 3: scout.bir_batch_generation (Batch Generation Audit Trail)
-- Purpose: Store BIR batch form generation results and metadata
-- ============================================================================

CREATE TABLE scout.bir_batch_generation (
  id BIGSERIAL PRIMARY KEY,

  -- Multi-tenant isolation
  company_id INTEGER NOT NULL,
  tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,

  -- Batch identification
  batch_id TEXT NOT NULL UNIQUE,  -- Format: company{id}_{year}{month}_{timestamp}

  -- Period
  month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
  year INTEGER NOT NULL CHECK (year BETWEEN 2020 AND 2100),

  -- Generation details
  forms_generated INTEGER NOT NULL DEFAULT 0,
  form_types TEXT NOT NULL,  -- Comma-separated list (e.g., "1601-C,2550Q,2307")

  -- Batch results (JSON structure from BIRBatchGenerator)
  batch_data JSONB NOT NULL DEFAULT '{}'::jsonb,

  -- Status workflow
  state TEXT NOT NULL DEFAULT 'draft' CHECK (state IN ('draft', 'submitted', 'cancelled')),

  -- Audit trail
  generated_by UUID REFERENCES users(id),
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  submitted_at TIMESTAMPTZ,

  -- Unique constraint per period
  CONSTRAINT unique_batch_per_period UNIQUE (company_id, year, month, batch_id)
);

-- Performance indexes
CREATE INDEX idx_bir_batch_company ON scout.bir_batch_generation(company_id, year DESC, month DESC);
CREATE INDEX idx_bir_batch_state ON scout.bir_batch_generation(state);
CREATE INDEX idx_bir_batch_id ON scout.bir_batch_generation(batch_id);
CREATE INDEX idx_bir_batch_tenant ON scout.bir_batch_generation(tenant_id);

-- Row Level Security
ALTER TABLE scout.bir_batch_generation ENABLE ROW LEVEL SECURITY;

-- Policy 1: Tenant-based access
CREATE POLICY bir_batch_tenant_policy ON scout.bir_batch_generation
  FOR ALL
  USING (tenant_id = ANY(COALESCE(auth.user_tenant_ids(), ARRAY[]::uuid[])));

-- Policy 2: Service role bypass
CREATE POLICY bir_batch_service_role_policy ON scout.bir_batch_generation
  FOR ALL
  USING (auth.role() = 'service_role');

COMMENT ON TABLE scout.bir_batch_generation IS 'BIR batch form generation results and audit trail';
COMMENT ON COLUMN scout.bir_batch_generation.batch_data IS 'Complete JSON output from BIRBatchGenerator.generate_batch() method';

-- ============================================================================
-- Trigger Function: Auto-update updated_at timestamp
-- ============================================================================

CREATE OR REPLACE FUNCTION scout.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach triggers to tables
CREATE TRIGGER update_transactions_updated_at
  BEFORE UPDATE ON scout.transactions
  FOR EACH ROW EXECUTE FUNCTION scout.update_updated_at_column();

CREATE TRIGGER update_vat_transactions_updated_at
  BEFORE UPDATE ON scout.vat_transactions
  FOR EACH ROW EXECUTE FUNCTION scout.update_updated_at_column();

-- ============================================================================
-- Validation Queries (for testing)
-- ============================================================================

-- Verify tables exist
DO $$
BEGIN
  ASSERT (SELECT to_regclass('scout.transactions') IS NOT NULL), 'scout.transactions not created';
  ASSERT (SELECT to_regclass('scout.vat_transactions') IS NOT NULL), 'scout.vat_transactions not created';
  ASSERT (SELECT to_regclass('scout.bir_batch_generation') IS NOT NULL), 'scout.bir_batch_generation not created';
  RAISE NOTICE '✅ All BIR tables created successfully';
END $$;

-- Verify RLS enabled
DO $$
BEGIN
  ASSERT (SELECT relrowsecurity FROM pg_class WHERE oid = 'scout.transactions'::regclass) = true, 'RLS not enabled on scout.transactions';
  ASSERT (SELECT relrowsecurity FROM pg_class WHERE oid = 'scout.vat_transactions'::regclass) = true, 'RLS not enabled on scout.vat_transactions';
  ASSERT (SELECT relrowsecurity FROM pg_class WHERE oid = 'scout.bir_batch_generation'::regclass) = true, 'RLS not enabled on scout.bir_batch_generation';
  RAISE NOTICE '✅ RLS policies enabled on all tables';
END $$;

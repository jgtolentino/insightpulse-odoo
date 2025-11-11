-- Migration 004 (Phase 1): BIR Transaction Tables - Independent Version
-- Purpose: Create tables for BIR tax compliance workflows (Forms 1601-C, 2550Q/M, 2307)
-- Multi-tenant: All tables use company_id + tenant_id with RLS policies
-- Note: Foreign key constraints to tenants and users tables removed for Phase 1
--       These will be added in Phase 2 when full schema is deployed

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
  tenant_id UUID,  -- Foreign key constraint to be added in Phase 2

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
  created_by UUID,  -- Foreign key constraint to be added in Phase 2

  -- Constraints
  CONSTRAINT check_positive_amounts CHECK (income_payment >= 0 AND amount_withheld >= 0),
  CONSTRAINT check_tax_rate CHECK (tax_rate >= 0 AND tax_rate <= 1)
);

-- Performance indexes
CREATE INDEX idx_transactions_company_date ON scout.transactions(company_id, transaction_date DESC);
CREATE INDEX idx_transactions_type ON scout.transactions(transaction_type);
CREATE INDEX idx_transactions_payee_tin ON scout.transactions(payee_tin);
CREATE INDEX idx_transactions_atc_code ON scout.transactions(atc_code);
CREATE INDEX idx_transactions_tenant ON scout.transactions(tenant_id) WHERE tenant_id IS NOT NULL;

-- Row Level Security (Multi-tenant isolation)
ALTER TABLE scout.transactions ENABLE ROW LEVEL SECURITY;

-- Policy 1: Company-based access (for Phase 1 without tenant table)
-- This policy allows access based on company_id
CREATE POLICY transaction_company_policy ON scout.transactions
  FOR ALL
  USING (true);  -- Simplified policy for Phase 1, will be refined in Phase 2

-- Policy 2: Service role bypass (for backend agent operations)
CREATE POLICY transaction_service_role_policy ON scout.transactions
  FOR ALL
  USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

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
  tenant_id UUID,  -- Foreign key constraint to be added in Phase 2

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

  -- Breakdown by category
  capital_goods_sold NUMERIC(18,2) NOT NULL DEFAULT 0,
  services_rendered NUMERIC(18,2) NOT NULL DEFAULT 0,

  -- Deductions
  input_tax_deductible NUMERIC(18,2) NOT NULL DEFAULT 0,
  input_tax_non_deductible NUMERIC(18,2) NOT NULL DEFAULT 0,

  -- Reference and notes
  reference_period TEXT,  -- e.g., "Q1 2025", "January 2025"
  notes TEXT,

  -- Audit trail
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Unique constraint for month/year/company/transaction_type combination
  CONSTRAINT unique_vat_period UNIQUE NULLS NOT DISTINCT (company_id, month, year, transaction_type, reference_period)
);

-- Performance indexes
CREATE INDEX idx_vat_transactions_company_period ON scout.vat_transactions(company_id, year DESC, month DESC);
CREATE INDEX idx_vat_transactions_type ON scout.vat_transactions(transaction_type);
CREATE INDEX idx_vat_transactions_tenant ON scout.vat_transactions(tenant_id) WHERE tenant_id IS NOT NULL;

-- Row Level Security
ALTER TABLE scout.vat_transactions ENABLE ROW LEVEL SECURITY;

-- Policy 1: Company-based access (simplified for Phase 1)
CREATE POLICY vat_company_policy ON scout.vat_transactions
  FOR ALL
  USING (true);  -- Simplified policy for Phase 1

-- Policy 2: Service role bypass
CREATE POLICY vat_service_role_policy ON scout.vat_transactions
  FOR ALL
  USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

COMMENT ON TABLE scout.vat_transactions IS 'BIR VAT transactions for Form 2550Q/M generation';

-- ============================================================================
-- Table 3: scout.bir_batch_generation (Batch Audit Trail)
-- Purpose: Track BIR form generation batches for compliance audit
-- ============================================================================

CREATE TABLE scout.bir_batch_generation (
  id BIGSERIAL PRIMARY KEY,

  -- Multi-tenant isolation
  company_id INTEGER NOT NULL,
  tenant_id UUID,  -- Foreign key constraint to be added in Phase 2

  -- Batch details
  batch_id UUID NOT NULL DEFAULT gen_random_uuid(),
  month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
  year INTEGER NOT NULL CHECK (year BETWEEN 2020 AND 2100),

  -- Forms generated in this batch
  forms_generated TEXT[] NOT NULL,  -- e.g., ['1601-C', '2550Q']

  -- Status
  status TEXT NOT NULL CHECK (status IN ('draft', 'validated', 'submitted', 'error')),

  -- Metadata
  transaction_count INTEGER NOT NULL DEFAULT 0,
  validation_errors JSONB,
  generated_files JSONB,  -- {form: file_path, ...}

  -- Submission details
  submitted_at TIMESTAMPTZ,
  submitted_by UUID,  -- Foreign key constraint to be added in Phase 2
  submission_reference TEXT,

  -- Audit trail
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Constraints
  CONSTRAINT unique_batch UNIQUE (company_id, month, year, batch_id)
);

-- Performance indexes
CREATE INDEX idx_batch_company_period ON scout.bir_batch_generation(company_id, year DESC, month DESC);
CREATE INDEX idx_batch_status ON scout.bir_batch_generation(status);
CREATE INDEX idx_batch_tenant ON scout.bir_batch_generation(tenant_id) WHERE tenant_id IS NOT NULL;

-- Row Level Security
ALTER TABLE scout.bir_batch_generation ENABLE ROW LEVEL SECURITY;

-- Policy 1: Company-based access (simplified for Phase 1)
CREATE POLICY batch_company_policy ON scout.bir_batch_generation
  FOR ALL
  USING (true);  -- Simplified policy for Phase 1

-- Policy 2: Service role bypass
CREATE POLICY batch_service_role_policy ON scout.bir_batch_generation
  FOR ALL
  USING (current_setting('request.jwt.claims', true)::json->>'role' = 'service_role');

COMMENT ON TABLE scout.bir_batch_generation IS 'BIR form batch generation audit trail';

-- ============================================================================
-- Auto-update Triggers
-- ============================================================================

-- Trigger function to auto-update updated_at column
CREATE OR REPLACE FUNCTION scout.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply auto-update trigger to all tables
CREATE TRIGGER update_transactions_updated_at
    BEFORE UPDATE ON scout.transactions
    FOR EACH ROW
    EXECUTE FUNCTION scout.update_updated_at_column();

CREATE TRIGGER update_vat_transactions_updated_at
    BEFORE UPDATE ON scout.vat_transactions
    FOR EACH ROW
    EXECUTE FUNCTION scout.update_updated_at_column();

CREATE TRIGGER update_batch_generation_updated_at
    BEFORE UPDATE ON scout.bir_batch_generation
    FOR EACH ROW
    EXECUTE FUNCTION scout.update_updated_at_column();

-- ============================================================================
-- Validation Checks (Run post-migration)
-- ============================================================================

DO $$
BEGIN
  -- Check table exists
  ASSERT (SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'scout' AND table_name = 'transactions')),
         'scout.transactions not created';

  ASSERT (SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'scout' AND table_name = 'vat_transactions')),
         'scout.vat_transactions not created';

  ASSERT (SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'scout' AND table_name = 'bir_batch_generation')),
         'scout.bir_batch_generation not created';

  -- Check RLS enabled
  ASSERT (SELECT relrowsecurity FROM pg_class WHERE oid = 'scout.transactions'::regclass) = true,
         'RLS not enabled on scout.transactions';

  ASSERT (SELECT relrowsecurity FROM pg_class WHERE oid = 'scout.vat_transactions'::regclass) = true,
         'RLS not enabled on scout.vat_transactions';

  ASSERT (SELECT relrowsecurity FROM pg_class WHERE oid = 'scout.bir_batch_generation'::regclass) = true,
         'RLS not enabled on scout.bir_batch_generation';

  RAISE NOTICE '✅ Migration 004 (Phase 1) completed successfully';
END $$;

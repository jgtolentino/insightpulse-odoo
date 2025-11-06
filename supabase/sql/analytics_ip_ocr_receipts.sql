-- =====================================================
-- Supabase Analytics: OCR Receipt Tracking
-- =====================================================
-- Purpose: Track receipt uploads, OCR performance, and usage metrics
-- Integration: Odoo ip_expense_mvp → AI Inference Hub → Supabase
-- Superset Dataset: analytics.v_ip_ocr_receipts_daily
-- =====================================================

-- Create analytics schema
CREATE SCHEMA IF NOT EXISTS analytics;

-- =====================================================
-- Table: analytics.ip_ocr_receipts
-- =====================================================
-- Stores OCR receipt processing records with idempotent upserts
-- Dedupe key prevents duplicate entries from retry logic

CREATE TABLE IF NOT EXISTS analytics.ip_ocr_receipts (
  id BIGSERIAL PRIMARY KEY,

  -- Receipt metadata
  filename TEXT NOT NULL,
  line_count INT NOT NULL DEFAULT 0,
  total_amount NUMERIC(12,2),
  currency TEXT DEFAULT 'PHP',

  -- User tracking (optional - not mapped in MVP)
  uploaded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,

  -- OCR results (full JSON for debugging/reprocessing)
  ocr_json JSONB,

  -- Deduplication
  dedupe_key TEXT UNIQUE NOT NULL,

  -- Timestamps
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_ip_ocr_receipts_created_at
  ON analytics.ip_ocr_receipts(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ip_ocr_receipts_uploaded_by
  ON analytics.ip_ocr_receipts(uploaded_by);

CREATE INDEX IF NOT EXISTS idx_ip_ocr_receipts_dedupe_key
  ON analytics.ip_ocr_receipts(dedupe_key);

-- Trigger: Update updated_at on modifications
CREATE OR REPLACE FUNCTION analytics.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ip_ocr_receipts_updated_at ON analytics.ip_ocr_receipts;
CREATE TRIGGER trg_ip_ocr_receipts_updated_at
  BEFORE UPDATE ON analytics.ip_ocr_receipts
  FOR EACH ROW
  EXECUTE FUNCTION analytics.update_updated_at();

-- =====================================================
-- RLS Policies
-- =====================================================
ALTER TABLE analytics.ip_ocr_receipts ENABLE ROW LEVEL SECURITY;

-- Policy: Read access for authenticated users
DROP POLICY IF EXISTS ip_ocr_receipts_read ON analytics.ip_ocr_receipts;
CREATE POLICY ip_ocr_receipts_read ON analytics.ip_ocr_receipts
  FOR SELECT
  USING (
    auth.role() IN ('authenticated', 'service_role')
  );

-- Policy: Write access for service_role only (via RPC)
DROP POLICY IF EXISTS ip_ocr_receipts_write ON analytics.ip_ocr_receipts;
CREATE POLICY ip_ocr_receipts_write ON analytics.ip_ocr_receipts
  FOR INSERT
  TO service_role
  WITH CHECK (true);

DROP POLICY IF EXISTS ip_ocr_receipts_update ON analytics.ip_ocr_receipts;
CREATE POLICY ip_ocr_receipts_update ON analytics.ip_ocr_receipts
  FOR UPDATE
  TO service_role
  USING (true)
  WITH CHECK (true);

-- =====================================================
-- RPC: Idempotent Upsert
-- =====================================================
-- Called by Odoo controller after OCR processing
-- Uses dedupe_key to prevent duplicate entries on retries

CREATE OR REPLACE FUNCTION analytics.upsert_ip_ocr_receipt(
  p_filename TEXT,
  p_line_count INT,
  p_total_amount NUMERIC,
  p_currency TEXT,
  p_uploaded_by UUID,
  p_ocr_json JSONB,
  p_dedupe_key TEXT
) RETURNS BIGINT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = analytics, public
AS $$
DECLARE
  v_id BIGINT;
BEGIN
  -- Upsert: Insert or update on conflict
  INSERT INTO analytics.ip_ocr_receipts (
    filename,
    line_count,
    total_amount,
    currency,
    uploaded_by,
    ocr_json,
    dedupe_key,
    created_at
  ) VALUES (
    p_filename,
    p_line_count,
    p_total_amount,
    COALESCE(p_currency, 'PHP'),
    p_uploaded_by,
    p_ocr_json,
    p_dedupe_key,
    NOW()
  )
  ON CONFLICT (dedupe_key)
  DO UPDATE SET
    line_count = EXCLUDED.line_count,
    total_amount = EXCLUDED.total_amount,
    ocr_json = EXCLUDED.ocr_json,
    updated_at = NOW()
  RETURNING id INTO v_id;

  RETURN v_id;
END;
$$;

-- Grant execute to service_role
GRANT EXECUTE ON FUNCTION analytics.upsert_ip_ocr_receipt TO service_role;

-- =====================================================
-- View: Daily Aggregates (Superset Dataset)
-- =====================================================
-- Pre-aggregated daily stats for Superset dashboards
-- Optimized for time-series charts and KPIs

CREATE OR REPLACE VIEW analytics.v_ip_ocr_receipts_daily AS
SELECT
  DATE_TRUNC('day', created_at)::DATE AS day,
  COUNT(*) AS receipts,
  SUM(COALESCE(total_amount, 0)) AS total_amount,
  AVG(COALESCE(total_amount, 0)) AS avg_amount,
  AVG(line_count) AS avg_lines,
  COUNT(DISTINCT uploaded_by) AS unique_users
FROM analytics.ip_ocr_receipts
GROUP BY DATE_TRUNC('day', created_at)::DATE
ORDER BY day DESC;

-- Grant select to authenticated users
GRANT SELECT ON analytics.v_ip_ocr_receipts_daily TO authenticated;

-- =====================================================
-- View: Hourly Aggregates (Real-time Monitoring)
-- =====================================================
-- Useful for monitoring current day performance

CREATE OR REPLACE VIEW analytics.v_ip_ocr_receipts_hourly AS
SELECT
  DATE_TRUNC('hour', created_at)::TIMESTAMPTZ AS hour,
  COUNT(*) AS receipts,
  SUM(COALESCE(total_amount, 0)) AS total_amount,
  AVG(line_count) AS avg_lines
FROM analytics.ip_ocr_receipts
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', created_at)::TIMESTAMPTZ
ORDER BY hour DESC;

GRANT SELECT ON analytics.v_ip_ocr_receipts_hourly TO authenticated;

-- =====================================================
-- Sample Data (for testing)
-- =====================================================
-- Uncomment to insert test data

/*
INSERT INTO analytics.ip_ocr_receipts (filename, line_count, total_amount, currency, dedupe_key, ocr_json)
VALUES
  ('receipt_001.jpg', 22, 150.50, 'PHP', 'test_dedupe_001', '{"lines": [{"text": "GROCERY STORE", "confidence": 0.98}]}'::jsonb),
  ('receipt_002.jpg', 18, 89.75, 'PHP', 'test_dedupe_002', '{"lines": [{"text": "RESTAURANT", "confidence": 0.95}]}'::jsonb),
  ('receipt_003.jpg', 25, 230.00, 'PHP', 'test_dedupe_003', '{"lines": [{"text": "HARDWARE STORE", "confidence": 0.97}]}'::jsonb);
*/

-- =====================================================
-- Verification Queries
-- =====================================================

-- Check table structure
-- \d analytics.ip_ocr_receipts

-- View recent receipts
-- SELECT id, filename, line_count, total_amount, created_at
-- FROM analytics.ip_ocr_receipts
-- ORDER BY created_at DESC
-- LIMIT 10;

-- View daily stats
-- SELECT * FROM analytics.v_ip_ocr_receipts_daily
-- ORDER BY day DESC
-- LIMIT 14;

-- Test RPC function
-- SELECT analytics.upsert_ip_ocr_receipt(
--   'test.jpg', 20, 100.00, 'PHP', NULL,
--   '{"test": true}'::jsonb, 'test_dedupe_key_123'
-- );

-- =====================================================
-- Cleanup (use with caution)
-- =====================================================
-- DROP VIEW IF EXISTS analytics.v_ip_ocr_receipts_daily CASCADE;
-- DROP VIEW IF EXISTS analytics.v_ip_ocr_receipts_hourly CASCADE;
-- DROP FUNCTION IF EXISTS analytics.upsert_ip_ocr_receipt CASCADE;
-- DROP TABLE IF EXISTS analytics.ip_ocr_receipts CASCADE;
-- DROP SCHEMA IF EXISTS analytics CASCADE;

-- =====================================================
-- Notes
-- =====================================================
-- 1. Dedupe key format: SHA256(filename + user_id + timestamp)
-- 2. RPC function uses SECURITY DEFINER to bypass RLS
-- 3. Service role key required for writes (Odoo controller)
-- 4. Views optimized for Superset time-series charts
-- 5. Hourly view retains 7 days (adjust as needed)
-- =====================================================

-- End of migration

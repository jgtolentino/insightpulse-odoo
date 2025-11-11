-- Rollback Migration 004: BIR Transaction Tables
-- Purpose: Safely remove all BIR-related tables and functions
-- Usage: psql "$POSTGRES_URL" -f supabase/migrations/004_bir_transactions_rollback.sql

-- Drop tables in reverse order (handles foreign key dependencies)
DROP TABLE IF EXISTS scout.bir_batch_generation CASCADE;
DROP TABLE IF EXISTS scout.vat_transactions CASCADE;
DROP TABLE IF EXISTS scout.transactions CASCADE;

-- Drop trigger function
DROP FUNCTION IF EXISTS scout.update_updated_at_column CASCADE;

-- Verification
DO $$
BEGIN
  IF to_regclass('scout.transactions') IS NULL AND
     to_regclass('scout.vat_transactions') IS NULL AND
     to_regclass('scout.bir_batch_generation') IS NULL THEN
    RAISE NOTICE '✅ Rollback complete: All BIR tables dropped';
  ELSE
    RAISE WARNING '⚠️ Some tables may still exist';
  END IF;
END $$;

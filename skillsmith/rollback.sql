-- Rollback script for Skillsmith schema
-- Run this if you need to remove Skillsmith database objects

-- Drop views
DROP VIEW IF EXISTS public.error_candidates CASCADE;

-- Drop materialized views
DROP MATERIALIZED VIEW IF EXISTS public.error_signatures CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS public.error_fingerprint(text, text, text);
DROP FUNCTION IF EXISTS public.normalize_error_message(text);

-- Drop extension (only if no other objects use it)
-- DROP EXTENSION IF EXISTS pgcrypto;

-- Note: This does not drop the agent_errors table
-- Review your schema to see if agent_errors should be preserved

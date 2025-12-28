-- Migration 001: Create examples schema for Superset sample data
-- This recreates the schema from examples.db in PostgreSQL

CREATE SCHEMA IF NOT EXISTS examples;
COMMENT ON SCHEMA examples IS 'Superset example data migrated from examples.db';

-- Create tracking table for migration state
CREATE TABLE IF NOT EXISTS public.schema_migrations (
  version TEXT PRIMARY KEY,
  applied_at TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO public.schema_migrations (version)
VALUES ('001_create_examples_schema')
ON CONFLICT (version) DO NOTHING;

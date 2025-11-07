-- =============================================================================
-- Enable and Configure Postgres Extensions
-- Extensions: pg_cron, pg_net (webhooks), and supporting extensions
-- =============================================================================

-- Enable pg_cron for scheduled jobs
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Enable pg_net for HTTP requests and webhooks
CREATE EXTENSION IF NOT EXISTS pg_net;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA cron TO postgres;
GRANT USAGE ON SCHEMA net TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA cron TO postgres;

-- =============================================================================
-- COMMENT
-- =============================================================================
COMMENT ON EXTENSION pg_cron IS 'Schedule recurring Postgres jobs';
COMMENT ON EXTENSION pg_net IS 'Make HTTP requests from Postgres for webhooks';

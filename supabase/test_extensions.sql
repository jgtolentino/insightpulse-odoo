-- =============================================================================
-- Test Postgres Extensions
-- Quick tests to verify pg_cron, pg_net, and GraphQL are working
-- =============================================================================

-- =============================================================================
-- 1. TEST: pg_cron Extension
-- =============================================================================
DO $$
BEGIN
  -- Check if pg_cron is installed
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') THEN
    RAISE NOTICE '✅ pg_cron extension is installed';
  ELSE
    RAISE EXCEPTION '❌ pg_cron extension is NOT installed';
  END IF;
END $$;

-- Schedule a simple test job (runs every minute)
SELECT cron.schedule(
  'test-job-simple',
  '* * * * *',  -- Every minute
  $$
  INSERT INTO audit_logs (actor_type, action, created_at)
  VALUES ('system', 'test.cron_job', NOW());
  $$
);

-- Verify the job was scheduled
SELECT
  jobid,
  jobname,
  schedule,
  active,
  nodename
FROM cron.job
WHERE jobname = 'test-job-simple';

-- Wait 1-2 minutes, then check if it ran
-- SELECT * FROM audit_logs WHERE action = 'test.cron_job' ORDER BY created_at DESC LIMIT 5;

-- Clean up test job
-- SELECT cron.unschedule('test-job-simple');

-- =============================================================================
-- 2. TEST: pg_net Extension (Webhooks)
-- =============================================================================
DO $$
BEGIN
  -- Check if pg_net is installed
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_net') THEN
    RAISE NOTICE '✅ pg_net extension is installed';
  ELSE
    RAISE EXCEPTION '❌ pg_net extension is NOT installed';
  END IF;
END $$;

-- Test HTTP POST to a public webhook testing service
DO $$
DECLARE
  request_id BIGINT;
BEGIN
  SELECT net.http_post(
    url := 'https://webhook.site/unique-url',  -- Replace with your webhook.site URL
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'User-Agent', 'InsightPulse-Supabase/1.0'
    ),
    body := jsonb_build_object(
      'test', true,
      'message', 'Test from pg_net',
      'timestamp', NOW()
    )
  ) INTO request_id;

  RAISE NOTICE '✅ Webhook sent! Request ID: %', request_id;
END $$;

-- Check the webhook request status
-- Note: May take a few seconds to process
SELECT
  id,
  status_code,
  error_msg,
  created,
  updated
FROM net._http_response
ORDER BY created DESC
LIMIT 5;

-- =============================================================================
-- 3. TEST: Webhook Trigger Function
-- =============================================================================

-- Insert a test ticket to trigger Slack notification
-- (This will only work if you have a Slack integration configured)
INSERT INTO tickets (tenant_id, number, title, state, severity, meta)
SELECT
  t.id,
  'TEST-001',
  'Test High-Severity Ticket for Webhook',
  'open',
  'high',
  jsonb_build_object('test', true)
FROM tenants t
LIMIT 1;

-- Check if webhook delivery was logged
SELECT
  w.url,
  wd.event,
  wd.status,
  wd.response_code,
  wd.attempted_at
FROM webhook_deliveries wd
JOIN webhooks w ON w.id = wd.webhook_id
WHERE wd.event = 'ticket.created'
ORDER BY wd.attempted_at DESC
LIMIT 5;

-- Clean up test ticket
-- DELETE FROM tickets WHERE number = 'TEST-001' AND meta->>'test' = 'true';

-- =============================================================================
-- 4. TEST: Cron Job Health View
-- =============================================================================

-- Check cron job health
SELECT * FROM vw_cron_job_health;

-- =============================================================================
-- 5. TEST: Webhook Health View
-- =============================================================================

-- Check webhook health
SELECT * FROM vw_webhook_health;

-- =============================================================================
-- 6. TEST: GraphQL (via Supabase Dashboard)
-- =============================================================================

-- You need to test GraphQL in the Supabase Dashboard GraphiQL interface:
-- https://supabase.com/dashboard/project/YOUR_PROJECT_ID/api/graphiql

-- Example GraphQL query to run in GraphiQL:
/*
query TestGraphQL {
  tenantsCollection(first: 5) {
    edges {
      node {
        id
        slug
        name
        created_at
      }
    }
  }
}
*/

-- =============================================================================
-- 7. CLEANUP: Remove Test Data
-- =============================================================================

-- Unschedule test cron job
SELECT cron.unschedule('test-job-simple');

-- Remove test audit logs
DELETE FROM audit_logs WHERE action = 'test.cron_job';

-- Remove test tickets
DELETE FROM tickets WHERE number = 'TEST-001' AND meta->>'test' = 'true';

-- =============================================================================
-- VERIFICATION SUMMARY
-- =============================================================================

DO $$
DECLARE
  cron_installed BOOLEAN;
  net_installed BOOLEAN;
  cron_jobs_count INT;
  webhook_deliveries_count INT;
BEGIN
  -- Check extensions
  SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_cron') INTO cron_installed;
  SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_net') INTO net_installed;

  -- Count jobs
  SELECT COUNT(*) INTO cron_jobs_count FROM cron.job;
  SELECT COUNT(*) INTO webhook_deliveries_count FROM webhook_deliveries WHERE attempted_at > NOW() - INTERVAL '1 hour';

  -- Print summary
  RAISE NOTICE '==============================================';
  RAISE NOTICE 'POSTGRES EXTENSIONS TEST SUMMARY';
  RAISE NOTICE '==============================================';
  RAISE NOTICE '';
  RAISE NOTICE '✅ pg_cron installed: %', cron_installed;
  RAISE NOTICE '✅ pg_net installed: %', net_installed;
  RAISE NOTICE '';
  RAISE NOTICE '📊 Active cron jobs: %', cron_jobs_count;
  RAISE NOTICE '📊 Recent webhook deliveries (last hour): %', webhook_deliveries_count;
  RAISE NOTICE '';
  RAISE NOTICE '==============================================';
END $$;

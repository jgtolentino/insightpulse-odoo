-- pg_cron jobs for scheduled maintenance and monitoring

-- Ensure pg_cron extension is enabled
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- 1. Prune old heartbeats (older than 30 days)
SELECT cron.schedule(
  'prune_old_heartbeats',
  '0 2 * * *',  -- Daily at 2 AM
  $$
    DELETE FROM ops_heartbeats
    WHERE created_at < NOW() - INTERVAL '30 days';
  $$
);

-- 2. Prune old incidents (closed and older than 90 days)
SELECT cron.schedule(
  'prune_old_incidents',
  '5 3 * * *',  -- Daily at 3:05 AM
  $$
    DELETE FROM ops_incidents
    WHERE status = 'closed'
      AND closed_at < NOW() - INTERVAL '90 days';
  $$
);

-- 3. Prune completed webhook queue items (older than 7 days)
SELECT cron.schedule(
  'prune_completed_webhooks',
  '10 3 * * *',  -- Daily at 3:10 AM
  $$
    DELETE FROM ops_webhook_queue
    WHERE status = 'done'
      AND created_at < NOW() - INTERVAL '7 days';
  $$
);

-- 4. Prune old healing actions (older than 60 days)
SELECT cron.schedule(
  'prune_old_healing_actions',
  '15 3 * * *',  -- Daily at 3:15 AM
  $$
    DELETE FROM ops_healing_actions
    WHERE completed_at < NOW() - INTERVAL '60 days';
  $$
);

-- 5. Heartbeat guard: Alert if synthetic heartbeat is stale (>25 hours)
SELECT cron.schedule(
  'heartbeat_guard_check',
  '0 * * * *',  -- Every hour
  $$
    INSERT INTO ops_heartbeats (source, status, meta)
    SELECT
      'hb_guard',
      'warn',
      jsonb_build_object(
        'note', 'synthetic heartbeat stale',
        'last_seen', MAX(created_at),
        'age_hours', EXTRACT(EPOCH FROM (NOW() - MAX(created_at))) / 3600
      )
    FROM ops_heartbeats
    WHERE source = 'synthetic_order_flow'
    HAVING EXTRACT(EPOCH FROM (NOW() - MAX(created_at))) > 90000;  -- 25 hours
  $$
);

-- 6. Auto-close incidents that have been acknowledged for >7 days
SELECT cron.schedule(
  'auto_close_old_incidents',
  '30 4 * * *',  -- Daily at 4:30 AM
  $$
    UPDATE ops_incidents
    SET status = 'closed',
        closed_at = NOW(),
        resolved_by = 'auto-closed'
    WHERE status = 'ack'
      AND acknowledged_at < NOW() - INTERVAL '7 days';
  $$
);

-- 7. Cleanup stale processing webhooks (stuck for >1 hour)
SELECT cron.schedule(
  'cleanup_stale_webhooks',
  '*/30 * * * *',  -- Every 30 minutes
  $$
    UPDATE ops_webhook_queue
    SET status = 'error',
        error = 'Stuck in processing state for >1 hour, auto-reset',
        updated_at = NOW()
    WHERE status = 'processing'
      AND updated_at < NOW() - INTERVAL '1 hour';
  $$
);

-- View scheduled jobs
-- SELECT * FROM cron.job;

-- To unschedule a job (if needed):
-- SELECT cron.unschedule('job_name');

-- To see job run history:
-- SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 20;

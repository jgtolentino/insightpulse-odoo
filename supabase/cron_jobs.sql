-- =============================================================================
-- pg_cron Jobs Configuration
-- Schedule recurring database maintenance and business logic jobs
-- =============================================================================

-- =============================================================================
-- 1. CLEANUP: Webhook Deliveries (Weekly - Sunday 3 AM)
-- =============================================================================
SELECT cron.schedule(
  'cleanup-webhook-deliveries',
  '0 3 * * 0',  -- Every Sunday at 3:00 AM
  $$
  DELETE FROM webhook_deliveries
  WHERE attempted_at < NOW() - INTERVAL '90 days'
    AND status IN ('delivered', 'failed');
  $$
);

-- =============================================================================
-- 2. CLEANUP: Old Audit Logs (Weekly - Sunday 3:30 AM)
-- =============================================================================
SELECT cron.schedule(
  'cleanup-audit-logs',
  '30 3 * * 0',  -- Every Sunday at 3:30 AM
  $$
  DELETE FROM audit_logs
  WHERE created_at < NOW() - INTERVAL '1 year';
  $$
);

-- =============================================================================
-- 3. CLEANUP: Old GitHub Webhooks (Weekly - Sunday 4 AM)
-- =============================================================================
SELECT cron.schedule(
  'cleanup-github-webhooks',
  '0 4 * * 0',  -- Every Sunday at 4:00 AM
  $$
  DELETE FROM github_webhooks
  WHERE received_at < NOW() - INTERVAL '180 days';
  $$
);

-- =============================================================================
-- 4. AGGREGATION: Usage Counters (Hourly)
-- =============================================================================
SELECT cron.schedule(
  'aggregate-usage-counters',
  '0 * * * *',  -- Every hour at minute 0
  $$
  INSERT INTO usage_counters (tenant_id, project_id, metric, period_start, period_end, value)
  SELECT
    tenant_id,
    project_id,
    metric,
    DATE_TRUNC('hour', occurred_at) AS period_start,
    DATE_TRUNC('hour', occurred_at) + INTERVAL '1 hour' AS period_end,
    SUM(value) AS value
  FROM metered_events
  WHERE occurred_at >= NOW() - INTERVAL '2 hours'
    AND occurred_at < NOW() - INTERVAL '1 hour'
  GROUP BY tenant_id, project_id, metric, DATE_TRUNC('hour', occurred_at)
  ON CONFLICT (tenant_id, project_id, metric, period_start, period_end)
  DO UPDATE SET value = usage_counters.value + EXCLUDED.value;
  $$
);

-- =============================================================================
-- 5. FINANCE SSC: Month-End Close Reminder (Last Day of Month at 6 PM)
-- =============================================================================
SELECT cron.schedule(
  'month-end-close-reminder',
  '0 18 L * *',  -- 6:00 PM on last day of each month
  $$
  WITH agencies AS (
    SELECT id, slug, name
    FROM tenants
    WHERE slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb')
  )
  INSERT INTO tickets (tenant_id, number, title, state, severity, created_by, meta)
  SELECT
    a.id,
    'MEC-' || a.slug || '-' || TO_CHAR(NOW(), 'YYYYMM'),
    'Month-End Close for ' || a.name || ' - ' || TO_CHAR(NOW(), 'Month YYYY'),
    'open',
    'high',
    NULL,  -- System-generated
    jsonb_build_object(
      'type', 'month_end_close',
      'period', TO_CHAR(NOW(), 'YYYY-MM'),
      'agency', a.slug,
      'tasks', jsonb_build_array(
        'Review journal entries',
        'Reconcile bank statements',
        'Run trial balance',
        'Prepare financial statements',
        'Submit to BIR if required'
      )
    )
  FROM agencies a;
  $$
);

-- =============================================================================
-- 6. FINANCE SSC: Daily Bank Reconciliation Check (Weekdays at 2 AM)
-- =============================================================================
SELECT cron.schedule(
  'daily-bank-reconciliation-check',
  '0 2 * * 1-5',  -- Monday-Friday at 2:00 AM
  $$
  -- This would call your custom reconciliation function
  -- For now, it logs an audit entry
  INSERT INTO audit_logs (tenant_id, user_id, actor_type, action, target_type, created_at)
  SELECT
    t.id,
    NULL,
    'system',
    'bank_reconciliation.daily_check',
    'bank_account',
    NOW()
  FROM tenants t
  WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb');
  $$
);

-- =============================================================================
-- 7. BIR COMPLIANCE: Quarterly Report Reminder (1st of Jan, Apr, Jul, Oct at 9 AM)
-- =============================================================================
SELECT cron.schedule(
  'bir-quarterly-report-reminder',
  '0 9 1 1,4,7,10 *',  -- 9:00 AM on 1st of Jan, Apr, Jul, Oct
  $$
  INSERT INTO tickets (tenant_id, number, title, state, severity, due_at, meta)
  SELECT
    t.id,
    'BIR-' || t.slug || '-' || TO_CHAR(NOW(), 'YYYYQ'),
    'BIR 2550Q Quarterly VAT Report - Q' || EXTRACT(QUARTER FROM NOW() - INTERVAL '1 quarter') || ' ' || EXTRACT(YEAR FROM NOW()),
    'open',
    'critical',
    NOW() + INTERVAL '25 days',  -- BIR deadline is typically 25th of the month
    jsonb_build_object(
      'type', 'bir_quarterly_report',
      'report_code', '2550Q',
      'quarter', EXTRACT(QUARTER FROM NOW() - INTERVAL '1 quarter'),
      'year', EXTRACT(YEAR FROM NOW()),
      'deadline', TO_CHAR(NOW() + INTERVAL '25 days', 'YYYY-MM-DD')
    )
  FROM tenants t
  WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb');
  $$
);

-- =============================================================================
-- 8. MONITORING: Check Failed Workflow Runs (Every 4 hours)
-- =============================================================================
SELECT cron.schedule(
  'check-failed-workflows',
  '0 */4 * * *',  -- Every 4 hours
  $$
  -- Create alert for workflows that have been running > 24 hours
  INSERT INTO alert_events (alert_id, fired_at, payload, delivered)
  SELECT
    a.id,
    NOW(),
    jsonb_build_object(
      'workflow_run_id', wr.id,
      'workflow_name', w.name,
      'started_at', wr.started_at,
      'hours_running', EXTRACT(EPOCH FROM (NOW() - wr.started_at)) / 3600,
      'status', wr.status
    ),
    false
  FROM workflow_runs wr
  JOIN workflows w ON w.id = wr.workflow_id
  JOIN alerts a ON a.name = 'Long Running Workflows'
  WHERE wr.status = 'running'
    AND wr.started_at < NOW() - INTERVAL '24 hours';
  $$
);

-- =============================================================================
-- 9. OPTIMIZATION: Update Statistics (Daily at 1 AM)
-- =============================================================================
SELECT cron.schedule(
  'analyze-database',
  '0 1 * * *',  -- Daily at 1:00 AM
  $$
  ANALYZE;
  $$
);

-- =============================================================================
-- 10. INTEGRATION: Sync GitHub Repository Cache (Every 6 hours)
-- =============================================================================
SELECT cron.schedule(
  'sync-github-repos',
  '0 */6 * * *',  -- Every 6 hours
  $$
  -- This would call your GitHub API sync function
  -- Placeholder for now
  SELECT 1;
  $$
);

-- =============================================================================
-- MANAGEMENT QUERIES
-- =============================================================================

-- List all scheduled jobs
-- SELECT * FROM cron.job ORDER BY schedule;

-- View job run history
-- SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 50;

-- Unschedule a job (example)
-- SELECT cron.unschedule('cleanup-webhook-deliveries');

-- Update job schedule (example)
-- SELECT cron.alter_job(
--   job_id := (SELECT jobid FROM cron.job WHERE jobname = 'cleanup-webhook-deliveries'),
--   schedule := '0 4 * * 0'  -- Change to 4 AM on Sunday
-- );

-- View cron job health (create view first)
CREATE OR REPLACE VIEW vw_cron_job_health AS
SELECT
  j.jobname,
  j.schedule,
  j.active,
  j.nodename,
  COUNT(jrd.runid) AS total_runs,
  COUNT(jrd.runid) FILTER (WHERE jrd.status = 'succeeded') AS successful_runs,
  COUNT(jrd.runid) FILTER (WHERE jrd.status = 'failed') AS failed_runs,
  MAX(jrd.start_time) AS last_run,
  ROUND(AVG(EXTRACT(EPOCH FROM (jrd.end_time - jrd.start_time)))) AS avg_duration_seconds
FROM cron.job j
LEFT JOIN cron.job_run_details jrd ON jrd.jobid = j.jobid
  AND jrd.start_time > NOW() - INTERVAL '30 days'
GROUP BY j.jobname, j.schedule, j.active, j.nodename
ORDER BY j.jobname;

COMMENT ON VIEW vw_cron_job_health IS 'Health monitoring for pg_cron scheduled jobs (last 30 days)';

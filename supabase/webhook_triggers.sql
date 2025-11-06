-- =============================================================================
-- Database Webhook Triggers (pg_net)
-- Real-time notifications when database events occur
-- =============================================================================

-- =============================================================================
-- HELPER: Generic Webhook Function
-- =============================================================================
CREATE OR REPLACE FUNCTION send_webhook(
  webhook_url TEXT,
  event_name TEXT,
  event_payload JSONB,
  webhook_secret TEXT DEFAULT NULL
)
RETURNS BIGINT AS $$
DECLARE
  request_id BIGINT;
  headers JSONB;
BEGIN
  -- Build headers
  headers := jsonb_build_object('Content-Type', 'application/json');

  IF webhook_secret IS NOT NULL THEN
    headers := headers || jsonb_build_object(
      'X-Webhook-Secret', webhook_secret,
      'X-Webhook-Signature', encode(
        hmac(event_payload::text, webhook_secret, 'sha256'),
        'hex'
      )
    );
  END IF;

  -- Send HTTP POST request
  SELECT net.http_post(
    url := webhook_url,
    headers := headers,
    body := jsonb_build_object(
      'event', event_name,
      'timestamp', NOW(),
      'data', event_payload
    )
  ) INTO request_id;

  RETURN request_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- 1. GITHUB: New Issue Webhook to Odoo
-- =============================================================================
CREATE OR REPLACE FUNCTION notify_odoo_github_issue()
RETURNS TRIGGER AS $$
DECLARE
  webhook_url TEXT := 'https://erp.insightpulseai.net/pulser_hub/github/issue';
  request_id BIGINT;
  action TEXT;
BEGIN
  action := NEW.payload->>'action';

  -- Only process opened, closed, or reopened issues
  IF action IN ('opened', 'closed', 'reopened') THEN
    request_id := send_webhook(
      webhook_url := webhook_url,
      event_name := 'github.issue.' || action,
      event_payload := jsonb_build_object(
        'issue_number', (NEW.payload->'issue'->>'number')::int,
        'issue_title', NEW.payload->'issue'->>'title',
        'issue_body', NEW.payload->'issue'->>'body',
        'repository', NEW.payload->'repository'->>'full_name',
        'sender', NEW.payload->'sender'->>'login',
        'url', NEW.payload->'issue'->>'html_url',
        'state', NEW.payload->'issue'->>'state',
        'labels', NEW.payload->'issue'->'labels',
        'assignees', NEW.payload->'issue'->'assignees',
        'created_at', NEW.received_at
      ),
      webhook_secret := current_setting('app.webhook_secret', true)
    );

    -- Log the webhook delivery
    INSERT INTO webhook_deliveries (webhook_id, event, payload, status)
    SELECT
      w.id,
      'github.issue.' || action,
      jsonb_build_object('request_id', request_id, 'issue_number', NEW.payload->'issue'->>'number'),
      'queued'
    FROM webhooks w
    WHERE w.url = webhook_url
    LIMIT 1;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
DROP TRIGGER IF EXISTS on_github_issue_webhook ON github_webhooks;
CREATE TRIGGER on_github_issue_webhook
  AFTER INSERT ON github_webhooks
  FOR EACH ROW
  WHEN (NEW.event_type = 'issues')
  EXECUTE FUNCTION notify_odoo_github_issue();

-- =============================================================================
-- 2. GITHUB: New Pull Request Webhook to Odoo
-- =============================================================================
CREATE OR REPLACE FUNCTION notify_odoo_github_pr()
RETURNS TRIGGER AS $$
DECLARE
  webhook_url TEXT := 'https://erp.insightpulseai.net/pulser_hub/github/pr';
  request_id BIGINT;
  action TEXT;
BEGIN
  action := NEW.payload->>'action';

  -- Process PR events
  IF action IN ('opened', 'closed', 'reopened', 'synchronize') THEN
    request_id := send_webhook(
      webhook_url := webhook_url,
      event_name := 'github.pull_request.' || action,
      event_payload := jsonb_build_object(
        'pr_number', (NEW.payload->'pull_request'->>'number')::int,
        'pr_title', NEW.payload->'pull_request'->>'title',
        'pr_body', NEW.payload->'pull_request'->>'body',
        'repository', NEW.payload->'repository'->>'full_name',
        'sender', NEW.payload->'sender'->>'login',
        'url', NEW.payload->'pull_request'->>'html_url',
        'state', NEW.payload->'pull_request'->>'state',
        'merged', NEW.payload->'pull_request'->>'merged',
        'base_branch', NEW.payload->'pull_request'->'base'->>'ref',
        'head_branch', NEW.payload->'pull_request'->'head'->>'ref',
        'created_at', NEW.received_at
      ),
      webhook_secret := current_setting('app.webhook_secret', true)
    );

    INSERT INTO webhook_deliveries (webhook_id, event, payload, status)
    SELECT
      w.id,
      'github.pull_request.' || action,
      jsonb_build_object('request_id', request_id, 'pr_number', NEW.payload->'pull_request'->>'number'),
      'queued'
    FROM webhooks w
    WHERE w.url = webhook_url
    LIMIT 1;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
DROP TRIGGER IF EXISTS on_github_pr_webhook ON github_webhooks;
CREATE TRIGGER on_github_pr_webhook
  AFTER INSERT ON github_webhooks
  FOR EACH ROW
  WHEN (NEW.event_type = 'pull_request')
  EXECUTE FUNCTION notify_odoo_github_pr();

-- =============================================================================
-- 3. TICKETS: New Ticket to Slack
-- =============================================================================
CREATE OR REPLACE FUNCTION notify_slack_new_ticket()
RETURNS TRIGGER AS $$
DECLARE
  slack_webhook TEXT;
  tenant_name TEXT;
  request_id BIGINT;
BEGIN
  -- Get Slack webhook URL from integrations
  SELECT i.config->>'webhook_url', t.name
  INTO slack_webhook, tenant_name
  FROM integrations i
  JOIN integration_types it ON it.id = i.type_id
  JOIN tenants t ON t.id = i.tenant_id
  WHERE it.provider = 'slack'
    AND i.tenant_id = NEW.tenant_id
    AND i.enabled = true
  LIMIT 1;

  IF slack_webhook IS NOT NULL THEN
    request_id := send_webhook(
      webhook_url := slack_webhook,
      event_name := 'ticket.created',
      event_payload := jsonb_build_object(
        'text', format('🎫 New Ticket: *%s*', NEW.title),
        'blocks', jsonb_build_array(
          jsonb_build_object(
            'type', 'section',
            'text', jsonb_build_object(
              'type', 'mrkdwn',
              'text', format(
                '*New Ticket Created*\n• *Ticket:* %s\n• *Title:* %s\n• *Severity:* %s\n• *Tenant:* %s\n• *Created:* %s',
                NEW.number,
                NEW.title,
                NEW.severity,
                tenant_name,
                TO_CHAR(NEW.created_at, 'YYYY-MM-DD HH24:MI')
              )
            )
          )
        )
      )
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
DROP TRIGGER IF EXISTS on_ticket_created_notify_slack ON tickets;
CREATE TRIGGER on_ticket_created_notify_slack
  AFTER INSERT ON tickets
  FOR EACH ROW
  WHEN (NEW.severity IN ('high', 'critical'))
  EXECUTE FUNCTION notify_slack_new_ticket();

-- =============================================================================
-- 4. INVOICES: High-Value Invoice Alert
-- =============================================================================
CREATE OR REPLACE FUNCTION alert_high_value_invoice()
RETURNS TRIGGER AS $$
DECLARE
  alert_webhook TEXT := 'https://erp.insightpulseai.net/api/alerts/invoice';
  request_id BIGINT;
  threshold_cents INT := 10000000;  -- ₱100,000
BEGIN
  IF NEW.amount_due_cents > threshold_cents THEN
    request_id := send_webhook(
      webhook_url := alert_webhook,
      event_name := 'invoice.high_value',
      event_payload := jsonb_build_object(
        'invoice_number', NEW.number,
        'amount_cents', NEW.amount_due_cents,
        'amount_php', ROUND(NEW.amount_due_cents / 100.0, 2),
        'status', NEW.status,
        'issued_at', NEW.issued_at,
        'due_at', NEW.due_at
      )
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
DROP TRIGGER IF EXISTS on_high_value_invoice ON invoices;
CREATE TRIGGER on_high_value_invoice
  AFTER INSERT ON invoices
  FOR EACH ROW
  EXECUTE FUNCTION alert_high_value_invoice();

-- =============================================================================
-- 5. WORKFLOW: Workflow Status Change to Notion
-- =============================================================================
CREATE OR REPLACE FUNCTION sync_workflow_to_notion()
RETURNS TRIGGER AS $$
DECLARE
  notion_webhook TEXT := 'https://api.notion.com/v1/pages';
  notion_token TEXT;
  request_id BIGINT;
BEGIN
  -- Only process when workflow is completed
  IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
    -- Get Notion integration token
    SELECT is_ciphertext::text INTO notion_token
    FROM integration_secrets is_tbl
    JOIN integrations i ON i.id = is_tbl.integration_id
    JOIN integration_types it ON it.id = i.type_id
    JOIN workflows w ON w.tenant_id = i.tenant_id
    WHERE it.provider = 'notion'
      AND w.id = NEW.workflow_id
      AND i.enabled = true
    LIMIT 1;

    IF notion_token IS NOT NULL THEN
      -- Note: This is a simplified example. Real Notion API requires more complex setup
      PERFORM net.http_post(
        url := notion_webhook,
        headers := jsonb_build_object(
          'Authorization', 'Bearer ' || notion_token,
          'Content-Type', 'application/json',
          'Notion-Version', '2022-06-28'
        ),
        body := jsonb_build_object(
          'parent', jsonb_build_object('database_id', 'YOUR_NOTION_DATABASE_ID'),
          'properties', jsonb_build_object(
            'Name', jsonb_build_object(
              'title', jsonb_build_array(
                jsonb_build_object('text', jsonb_build_object('content', 'Workflow: ' || NEW.id))
              )
            ),
            'Status', jsonb_build_object('select', jsonb_build_object('name', 'Completed'))
          )
        )
      );
    END IF;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
DROP TRIGGER IF EXISTS on_workflow_completed ON workflow_runs;
CREATE TRIGGER on_workflow_completed
  AFTER UPDATE ON workflow_runs
  FOR EACH ROW
  WHEN (NEW.status = 'completed')
  EXECUTE FUNCTION sync_workflow_to_notion();

-- =============================================================================
-- 6. AUDIT: Critical Security Events to Security Dashboard
-- =============================================================================
CREATE OR REPLACE FUNCTION alert_security_events()
RETURNS TRIGGER AS $$
DECLARE
  security_webhook TEXT := 'https://erp.insightpulseai.net/api/security/alert';
  request_id BIGINT;
  critical_actions TEXT[] := ARRAY[
    'user.delete',
    'org.delete',
    'billing.update',
    'secret.read',
    'secret.delete',
    'integration.delete'
  ];
BEGIN
  IF NEW.action = ANY(critical_actions) THEN
    request_id := send_webhook(
      webhook_url := security_webhook,
      event_name := 'security.critical_action',
      event_payload := jsonb_build_object(
        'action', NEW.action,
        'actor_type', NEW.actor_type,
        'user_id', NEW.user_id,
        'tenant_id', NEW.tenant_id,
        'target_type', NEW.target_type,
        'target_id', NEW.target_id,
        'ip', NEW.ip,
        'user_agent', NEW.user_agent,
        'timestamp', NEW.created_at
      )
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger
DROP TRIGGER IF EXISTS on_critical_audit_log ON audit_logs;
CREATE TRIGGER on_critical_audit_log
  AFTER INSERT ON audit_logs
  FOR EACH ROW
  EXECUTE FUNCTION alert_security_events();

-- =============================================================================
-- MONITORING VIEW: Webhook Health
-- =============================================================================
CREATE OR REPLACE VIEW vw_webhook_health AS
SELECT
  w.url,
  w.description,
  w.enabled,
  COUNT(wd.id) AS total_deliveries,
  COUNT(wd.id) FILTER (WHERE wd.status = 'delivered') AS successful,
  COUNT(wd.id) FILTER (WHERE wd.status = 'failed') AS failed,
  ROUND(
    100.0 * COUNT(wd.id) FILTER (WHERE wd.status = 'delivered') / NULLIF(COUNT(wd.id), 0),
    2
  ) AS success_rate_pct,
  ROUND(AVG(wd.response_ms)) AS avg_response_ms,
  MAX(wd.attempted_at) AS last_attempt
FROM webhooks w
LEFT JOIN webhook_deliveries wd ON wd.webhook_id = w.id
  AND wd.attempted_at > NOW() - INTERVAL '7 days'
GROUP BY w.id, w.url, w.description, w.enabled
ORDER BY w.enabled DESC, total_deliveries DESC;

COMMENT ON VIEW vw_webhook_health IS 'Webhook delivery health metrics (last 7 days)';

-- =============================================================================
-- UTILITY: Retry Failed Webhooks
-- =============================================================================
CREATE OR REPLACE FUNCTION retry_failed_webhooks()
RETURNS TABLE(webhook_id UUID, retried_count INT) AS $$
DECLARE
  delivery RECORD;
  request_id BIGINT;
  retry_count INT := 0;
BEGIN
  FOR delivery IN
    SELECT
      wd.id AS delivery_id,
      wd.webhook_id,
      w.url,
      w.secret,
      wd.event,
      wd.payload
    FROM webhook_deliveries wd
    JOIN webhooks w ON w.id = wd.webhook_id
    WHERE wd.status = 'failed'
      AND wd.attempted_at > NOW() - INTERVAL '1 day'
      AND w.enabled = true
    ORDER BY wd.attempted_at DESC
    LIMIT 100
  LOOP
    request_id := send_webhook(
      webhook_url := delivery.url,
      event_name := delivery.event,
      event_payload := delivery.payload,
      webhook_secret := delivery.secret
    );

    UPDATE webhook_deliveries
    SET status = 'queued', attempted_at = NOW()
    WHERE id = delivery.delivery_id;

    retry_count := retry_count + 1;
  END LOOP;

  RETURN QUERY SELECT NULL::UUID, retry_count;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION retry_failed_webhooks IS 'Retry failed webhook deliveries from the last 24 hours';

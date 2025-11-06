# Postgres Extensions Leverage Guide

## Overview
Your Supabase instance has three powerful extensions installed:
1. **pg_cron** - Schedule recurring database jobs
2. **Database Webhooks (pg_net)** - Real-time webhooks on table events
3. **GraphQL** - Query your database via GraphQL

---

## 1. pg_cron: Schedule Recurring Jobs

### Use Cases for InsightPulse Finance SSC

#### A. Auto-reconcile Bank Transactions (Daily at 2 AM)
```sql
-- Schedule daily bank reconciliation
SELECT cron.schedule(
  'daily-bank-reconciliation',
  '0 2 * * *',  -- Every day at 2:00 AM
  $$
  SELECT reconcile_bank_transactions();
  $$
);
```

#### B. Month-End Close Reminder (Last Day of Month)
```sql
-- Trigger month-end close workflow
SELECT cron.schedule(
  'month-end-close-trigger',
  '0 18 L * *',  -- 6 PM on last day of month
  $$
  INSERT INTO tickets (tenant_id, number, title, state, severity, meta)
  SELECT
    t.id,
    'MEC-' || TO_CHAR(NOW(), 'YYYYMM'),
    'Month-End Close for ' || TO_CHAR(NOW(), 'Month YYYY'),
    'open',
    'high',
    jsonb_build_object(
      'type', 'month_end_close',
      'period', TO_CHAR(NOW(), 'YYYY-MM')
    )
  FROM tenants t
  WHERE t.slug IN ('rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb');
  $$
);
```

#### C. Clean Up Old Webhook Deliveries (Weekly)
```sql
-- Archive old webhook deliveries to reduce table bloat
SELECT cron.schedule(
  'cleanup-webhook-deliveries',
  '0 3 * * 0',  -- Every Sunday at 3 AM
  $$
  DELETE FROM webhook_deliveries
  WHERE attempted_at < NOW() - INTERVAL '90 days'
    AND status IN ('delivered', 'failed');
  $$
);
```

#### D. BIR Compliance Report Generation (Quarterly)
```sql
-- Generate BIR quarterly reports
SELECT cron.schedule(
  'bir-quarterly-reports',
  '0 9 1 1,4,7,10 *',  -- 9 AM on 1st of Jan, Apr, Jul, Oct
  $$
  INSERT INTO ocr_jobs (tenant_id, status, engine, params)
  SELECT
    t.id,
    'queued',
    'bir-report-generator',
    jsonb_build_object(
      'report_type', '2550Q',
      'quarter', EXTRACT(QUARTER FROM NOW() - INTERVAL '1 quarter'),
      'year', EXTRACT(YEAR FROM NOW())
    )
  FROM tenants t;
  $$
);
```

#### E. Update Usage Counters (Hourly)
```sql
-- Aggregate metered events into usage counters
SELECT cron.schedule(
  'aggregate-usage-counters',
  '0 * * * *',  -- Every hour
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
  WHERE occurred_at >= NOW() - INTERVAL '1 hour'
    AND occurred_at < NOW()
  GROUP BY tenant_id, project_id, metric, DATE_TRUNC('hour', occurred_at)
  ON CONFLICT (tenant_id, project_id, metric, period_start, period_end)
  DO UPDATE SET value = usage_counters.value + EXCLUDED.value;
  $$
);
```

### Managing Cron Jobs

```sql
-- List all scheduled jobs
SELECT * FROM cron.job ORDER BY schedule;

-- View job run history
SELECT * FROM cron.job_run_details
ORDER BY start_time DESC
LIMIT 20;

-- Unschedule a job
SELECT cron.unschedule('daily-bank-reconciliation');

-- Update a job schedule
SELECT cron.alter_job(
  job_id := (SELECT jobid FROM cron.job WHERE jobname = 'cleanup-webhook-deliveries'),
  schedule := '0 4 * * 0'  -- Change to 4 AM on Sunday
);
```

---

## 2. Database Webhooks (pg_net): Real-Time Integration

### Use Cases for InsightPulse

#### A. Notify Odoo When GitHub Issue Created
```sql
-- Create a function to send webhook
CREATE OR REPLACE FUNCTION notify_odoo_github_issue()
RETURNS TRIGGER AS $$
DECLARE
  webhook_url TEXT := 'https://erp.insightpulseai.net/pulser_hub/github/issue';
  request_id BIGINT;
BEGIN
  -- Send webhook to Odoo via pg_net
  SELECT net.http_post(
    url := webhook_url,
    headers := jsonb_build_object(
      'Content-Type', 'application/json',
      'X-Webhook-Secret', current_setting('app.webhook_secret', true)
    ),
    body := jsonb_build_object(
      'event', 'github.issue.created',
      'issue_number', (NEW.payload->>'number')::int,
      'issue_title', NEW.payload->>'title',
      'repository', NEW.payload->'repository'->>'full_name',
      'sender', NEW.payload->'sender'->>'login',
      'url', NEW.payload->>'html_url',
      'created_at', NEW.received_at
    )
  ) INTO request_id;

  -- Log the webhook delivery
  INSERT INTO webhook_deliveries (webhook_id, event, payload, status)
  SELECT
    w.id,
    'github.issue.created',
    jsonb_build_object('request_id', request_id, 'issue', NEW.payload),
    'queued'
  FROM webhooks w
  WHERE w.url = webhook_url
  LIMIT 1;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Attach trigger to github_webhooks table
CREATE TRIGGER on_github_issue_created
  AFTER INSERT ON github_webhooks
  FOR EACH ROW
  WHEN (NEW.event_type = 'issues' AND NEW.payload->>'action' = 'opened')
  EXECUTE FUNCTION notify_odoo_github_issue();
```

#### B. Notify Slack When BIR Report Ready
```sql
CREATE OR REPLACE FUNCTION notify_slack_bir_report()
RETURNS TRIGGER AS $$
DECLARE
  slack_webhook TEXT := 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK';
  tenant_name TEXT;
BEGIN
  -- Get tenant name
  SELECT name INTO tenant_name FROM tenants WHERE id = NEW.tenant_id;

  -- Send to Slack
  PERFORM net.http_post(
    url := slack_webhook,
    headers := jsonb_build_object('Content-Type', 'application/json'),
    body := jsonb_build_object(
      'text', format('✅ BIR Report Ready for %s', tenant_name),
      'blocks', jsonb_build_array(
        jsonb_build_object(
          'type', 'section',
          'text', jsonb_build_object(
            'type', 'mrkdwn',
            'text', format('*BIR Report Completed*\n• Tenant: %s\n• Report Type: %s\n• Status: %s',
              tenant_name,
              NEW.params->>'report_type',
              NEW.status
            )
          )
        )
      )
    )
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_bir_report_completed
  AFTER UPDATE ON ocr_jobs
  FOR EACH ROW
  WHEN (
    OLD.status != 'completed'
    AND NEW.status = 'completed'
    AND NEW.engine = 'bir-report-generator'
  )
  EXECUTE FUNCTION notify_slack_bir_report();
```

#### C. Sync Notion When Ticket Created
```sql
CREATE OR REPLACE FUNCTION sync_notion_ticket()
RETURNS TRIGGER AS $$
DECLARE
  notion_api_url TEXT := 'https://api.notion.com/v1/pages';
  notion_token TEXT;
BEGIN
  -- Get Notion token from integration secrets
  SELECT ciphertext::text INTO notion_token
  FROM integration_secrets is
  JOIN integrations i ON i.id = is.integration_id
  JOIN integration_types it ON it.id = i.type_id
  WHERE it.provider = 'notion'
    AND i.tenant_id = NEW.tenant_id
  LIMIT 1;

  -- Create Notion page
  PERFORM net.http_post(
    url := notion_api_url,
    headers := jsonb_build_object(
      'Authorization', 'Bearer ' || notion_token,
      'Content-Type', 'application/json',
      'Notion-Version', '2022-06-28'
    ),
    body := jsonb_build_object(
      'parent', jsonb_build_object(
        'database_id', '12345678-1234-1234-1234-123456789abc'  -- Your Notion database ID
      ),
      'properties', jsonb_build_object(
        'Name', jsonb_build_object(
          'title', jsonb_build_array(
            jsonb_build_object('text', jsonb_build_object('content', NEW.title))
          )
        ),
        'Status', jsonb_build_object(
          'select', jsonb_build_object('name', NEW.state)
        ),
        'Severity', jsonb_build_object(
          'select', jsonb_build_object('name', NEW.severity)
        )
      )
    )
  );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_ticket_created_sync_notion
  AFTER INSERT ON tickets
  FOR EACH ROW
  EXECUTE FUNCTION sync_notion_ticket();
```

#### D. Alert on High-Value Invoice
```sql
CREATE OR REPLACE FUNCTION alert_high_value_invoice()
RETURNS TRIGGER AS $$
DECLARE
  alert_webhook TEXT := 'https://erp.insightpulseai.net/api/alerts/invoice';
BEGIN
  -- Alert if invoice is > ₱100,000
  IF NEW.amount_due_cents > 10000000 THEN
    PERFORM net.http_post(
      url := alert_webhook,
      headers := jsonb_build_object('Content-Type', 'application/json'),
      body := jsonb_build_object(
        'event', 'invoice.high_value',
        'invoice_number', NEW.number,
        'amount', NEW.amount_due_cents / 100.0,
        'currency', 'PHP',
        'issued_at', NEW.issued_at
      )
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_high_value_invoice
  AFTER INSERT ON invoices
  FOR EACH ROW
  EXECUTE FUNCTION alert_high_value_invoice();
```

### Monitoring Webhook Deliveries

```sql
-- Check webhook delivery status
SELECT
  id,
  event,
  status,
  response_code,
  response_ms,
  attempted_at,
  error
FROM webhook_deliveries
WHERE attempted_at > NOW() - INTERVAL '1 hour'
ORDER BY attempted_at DESC;

-- Retry failed webhooks
CREATE OR REPLACE FUNCTION retry_failed_webhooks()
RETURNS void AS $$
DECLARE
  delivery RECORD;
  request_id BIGINT;
BEGIN
  FOR delivery IN
    SELECT wd.*, w.url, w.secret
    FROM webhook_deliveries wd
    JOIN webhooks w ON w.id = wd.webhook_id
    WHERE wd.status = 'failed'
      AND wd.attempted_at > NOW() - INTERVAL '1 day'
  LOOP
    SELECT net.http_post(
      url := delivery.url,
      headers := jsonb_build_object(
        'Content-Type', 'application/json',
        'X-Webhook-Secret', delivery.secret
      ),
      body := delivery.payload
    ) INTO request_id;

    UPDATE webhook_deliveries
    SET status = 'queued', attempted_at = NOW()
    WHERE id = delivery.id;
  END LOOP;
END;
$$ LANGUAGE plpgsql;
```

---

## 3. GraphQL: Query Your Database

### Accessing GraphiQL Interface

Navigate to your Supabase dashboard:
```
https://supabase.com/dashboard/project/YOUR_PROJECT_ID/api/graphiql
```

### Example Queries for Finance SSC

#### A. Query Tenants and Recent Tickets
```graphql
query GetTenantsWithTickets {
  tenantsCollection {
    edges {
      node {
        id
        slug
        name
        ticketsCollection(
          filter: { state: { eq: "open" } }
          orderBy: { created_at: DescNullsLast }
          first: 5
        ) {
          edges {
            node {
              number
              title
              severity
              created_at
            }
          }
        }
      }
    }
  }
}
```

#### B. Query Usage Metrics by Tenant
```graphql
query GetUsageByTenant($tenantId: UUID!) {
  usage_countersCollection(
    filter: { tenant_id: { eq: $tenantId } }
    orderBy: { period_start: DescNullsLast }
    first: 30
  ) {
    edges {
      node {
        metric
        value
        period_start
        period_end
      }
    }
  }
}
```

#### C. Query Recent GitHub Webhooks
```graphql
query GetRecentGitHubWebhooks {
  github_webhooksCollection(
    orderBy: { received_at: DescNullsLast }
    first: 20
  ) {
    edges {
      node {
        event_type
        delivery_id
        received_at
        payload
      }
    }
  }
}
```

#### D. Query Billing Summary
```graphql
query GetBillingSummary($tenantId: UUID!) {
  subscriptionsCollection(
    filter: { tenant_id: { eq: $tenantId } }
    first: 1
  ) {
    edges {
      node {
        status
        current_period_start
        current_period_end
        plan {
          name
          price_cents
          interval
        }
        invoicesCollection(
          orderBy: { issued_at: DescNullsLast }
          first: 10
        ) {
          edges {
            node {
              number
              status
              amount_due_cents
              amount_paid_cents
              issued_at
            }
          }
        }
      }
    }
  }
}
```

#### E. Mutation: Create Ticket
```graphql
mutation CreateTicket($tenantId: UUID!, $title: String!, $severity: severity!) {
  insertIntotickets_tableCollection(
    objects: [
      {
        tenant_id: $tenantId
        number: "TKT-AUTO"
        title: $title
        severity: $severity
        state: open
      }
    ]
  ) {
    records {
      id
      number
      title
      created_at
    }
  }
}
```

### GraphQL from Your Application

#### Using JavaScript/TypeScript
```typescript
// Install: npm install @supabase/supabase-js

import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  'https://spdtwktxdalcfigzeqrz.supabase.co',
  'YOUR_SUPABASE_ANON_KEY'
);

// Query using GraphQL
const { data, error } = await supabase.graphql.query({
  query: `
    query GetOpenTickets {
      ticketsCollection(filter: { state: { eq: "open" } }) {
        edges {
          node {
            id
            number
            title
            severity
          }
        }
      }
    }
  `
});
```

#### Using Python
```python
# Install: pip install supabase

from supabase import create_client

supabase = create_client(
    'https://spdtwktxdalcfigzeqrz.supabase.co',
    'YOUR_SUPABASE_ANON_KEY'
)

# Query using GraphQL
result = supabase.graphql.query("""
  query GetOpenTickets {
    ticketsCollection(filter: { state: { eq: "open" } }) {
      edges {
        node {
          id
          number
          title
          severity
        }
      }
    }
  }
""")
```

---

## Combined Use Case: End-to-End Automation

### Scenario: Automated Month-End Close Workflow

```sql
-- 1. pg_cron: Schedule the month-end close trigger
SELECT cron.schedule(
  'month-end-automation',
  '0 0 L * *',  -- Midnight on last day of month
  $$
  -- Create month-end close workflow
  WITH new_workflow AS (
    INSERT INTO workflow_runs (workflow_id, status, input, started_at)
    SELECT
      w.id,
      'running',
      jsonb_build_object(
        'period', TO_CHAR(NOW(), 'YYYY-MM'),
        'agencies', ARRAY['rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb']
      ),
      NOW()
    FROM workflows w
    WHERE w.name = 'month_end_close'
    RETURNING id
  )
  SELECT id FROM new_workflow;
  $$
);

-- 2. Database Webhook: Notify stakeholders when workflow starts
CREATE OR REPLACE FUNCTION notify_month_end_start()
RETURNS TRIGGER AS $$
BEGIN
  IF (NEW.input->>'period') IS NOT NULL THEN
    -- Send to Slack
    PERFORM net.http_post(
      url := 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
      headers := jsonb_build_object('Content-Type', 'application/json'),
      body := jsonb_build_object(
        'text', format('🚀 Month-End Close Started: %s', NEW.input->>'period'),
        'channel', '#finance-ssc'
      )
    );

    -- Send to Odoo
    PERFORM net.http_post(
      url := 'https://erp.insightpulseai.net/api/workflows/month-end-start',
      headers := jsonb_build_object('Content-Type', 'application/json'),
      body := jsonb_build_object(
        'workflow_run_id', NEW.id,
        'period', NEW.input->>'period',
        'agencies', NEW.input->'agencies'
      )
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER on_month_end_workflow_start
  AFTER INSERT ON workflow_runs
  FOR EACH ROW
  WHEN (NEW.status = 'running')
  EXECUTE FUNCTION notify_month_end_start();

-- 3. Query workflow status via GraphQL
-- (Use GraphiQL or API client)
```

---

## Performance & Monitoring

### Enable Query Logging
```sql
-- Track slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();
```

### Monitor pg_cron Jobs
```sql
-- Create a dashboard query for Superset
CREATE OR REPLACE VIEW vw_cron_job_health AS
SELECT
  j.jobname,
  j.schedule,
  j.active,
  COUNT(jrd.runid) AS total_runs,
  COUNT(jrd.runid) FILTER (WHERE jrd.status = 'succeeded') AS successful_runs,
  COUNT(jrd.runid) FILTER (WHERE jrd.status = 'failed') AS failed_runs,
  MAX(jrd.start_time) AS last_run,
  AVG(EXTRACT(EPOCH FROM (jrd.end_time - jrd.start_time))) AS avg_duration_seconds
FROM cron.job j
LEFT JOIN cron.job_run_details jrd ON jrd.jobid = j.jobid
WHERE jrd.start_time > NOW() - INTERVAL '30 days'
GROUP BY j.jobname, j.schedule, j.active;
```

### Monitor Webhook Health
```sql
CREATE OR REPLACE VIEW vw_webhook_health AS
SELECT
  w.url,
  w.enabled,
  COUNT(wd.id) AS total_deliveries,
  COUNT(wd.id) FILTER (WHERE wd.status = 'delivered') AS successful,
  COUNT(wd.id) FILTER (WHERE wd.status = 'failed') AS failed,
  AVG(wd.response_ms) AS avg_response_ms,
  MAX(wd.attempted_at) AS last_attempt
FROM webhooks w
LEFT JOIN webhook_deliveries wd ON wd.webhook_id = w.id
WHERE wd.attempted_at > NOW() - INTERVAL '7 days'
GROUP BY w.url, w.enabled;
```

---

## Security Best Practices

### 1. Secure Webhook Secrets
```sql
-- Store webhook secrets in the secrets table
INSERT INTO secrets (tenant_id, name, latest_version)
SELECT id, 'webhook_secret', 1
FROM tenants;

INSERT INTO secret_versions (secret_id, version, format, ciphertext)
SELECT
  s.id,
  1,
  'opaque',
  pgp_sym_encrypt('your-webhook-secret', current_setting('app.encryption_key'))
FROM secrets s
WHERE s.name = 'webhook_secret';
```

### 2. Validate Webhook Signatures
```sql
CREATE OR REPLACE FUNCTION validate_webhook_signature(
  payload TEXT,
  signature TEXT,
  secret TEXT
) RETURNS BOOLEAN AS $$
BEGIN
  RETURN signature = encode(
    hmac(payload, secret, 'sha256'),
    'hex'
  );
END;
$$ LANGUAGE plpgsql;
```

### 3. Rate Limit pg_net Requests
```sql
-- Track and limit webhook requests per minute
CREATE TABLE IF NOT EXISTS webhook_rate_limits (
  webhook_id UUID PRIMARY KEY REFERENCES webhooks(id),
  requests_count INT DEFAULT 0,
  window_start TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION check_webhook_rate_limit(webhook_uuid UUID)
RETURNS BOOLEAN AS $$
DECLARE
  current_count INT;
  max_requests INT := 60;  -- 60 requests per minute
BEGIN
  -- Reset counter if window expired
  UPDATE webhook_rate_limits
  SET requests_count = 0, window_start = NOW()
  WHERE webhook_id = webhook_uuid
    AND window_start < NOW() - INTERVAL '1 minute';

  -- Get current count
  SELECT requests_count INTO current_count
  FROM webhook_rate_limits
  WHERE webhook_id = webhook_uuid;

  -- Increment counter
  UPDATE webhook_rate_limits
  SET requests_count = requests_count + 1
  WHERE webhook_id = webhook_uuid;

  RETURN current_count < max_requests;
END;
$$ LANGUAGE plpgsql;
```

---

## Next Steps

1. **Enable Extensions** (if not already enabled):
```sql
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS pg_net;
```

2. **Grant Permissions**:
```sql
GRANT USAGE ON SCHEMA cron TO postgres;
GRANT USAGE ON SCHEMA net TO postgres;
```

3. **Test Each Extension**:
   - pg_cron: Create a simple test job
   - pg_net: Test a webhook call
   - GraphQL: Run a test query in GraphiQL

4. **Monitor Performance**:
   - Set up Superset dashboards for cron job health
   - Monitor webhook delivery rates
   - Track GraphQL query performance

5. **Implement Gradually**:
   - Start with read-only operations
   - Test in dev environment first
   - Roll out to production with monitoring

---

## Resources

- [Supabase pg_cron Documentation](https://supabase.com/docs/guides/database/extensions/pg_cron)
- [Supabase Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- [Supabase GraphQL API](https://supabase.com/docs/guides/api/graphql)
- [pg_net GitHub](https://github.com/supabase/pg_net)
- [PostgreSQL Trigger Functions](https://www.postgresql.org/docs/current/plpgsql-trigger.html)

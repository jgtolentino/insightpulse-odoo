# Postgres Extensions Quick Reference

## 🚀 Quick Start

### 1. Enable Extensions (Run Once)
```bash
psql "$POSTGRES_URL" -f supabase/migrations/004_enable_extensions.sql
```

### 2. Test Extensions
```bash
psql "$POSTGRES_URL" -f supabase/test_extensions.sql
```

### 3. Set Up Cron Jobs
```bash
psql "$POSTGRES_URL" -f supabase/cron_jobs.sql
```

### 4. Set Up Webhooks
```bash
psql "$POSTGRES_URL" -f supabase/webhook_triggers.sql
```

---

## 📋 Common Commands

### pg_cron Management

```sql
-- List all cron jobs
SELECT * FROM cron.job ORDER BY schedule;

-- View recent job runs
SELECT * FROM cron.job_run_details ORDER BY start_time DESC LIMIT 20;

-- Check job health
SELECT * FROM vw_cron_job_health;

-- Unschedule a job
SELECT cron.unschedule('job-name-here');

-- Update job schedule
SELECT cron.alter_job(
  job_id := (SELECT jobid FROM cron.job WHERE jobname = 'your-job-name'),
  schedule := '0 3 * * *'  -- New schedule
);
```

### Webhook Management

```sql
-- View webhook health
SELECT * FROM vw_webhook_health;

-- Check recent webhook deliveries
SELECT * FROM webhook_deliveries
WHERE attempted_at > NOW() - INTERVAL '1 hour'
ORDER BY attempted_at DESC;

-- Retry failed webhooks
SELECT * FROM retry_failed_webhooks();

-- Add a new webhook
INSERT INTO webhooks (tenant_id, url, secret, description)
SELECT id, 'https://your-webhook-url.com', 'your-secret', 'Description'
FROM tenants WHERE slug = 'rim';
```

### GraphQL Queries

Access GraphiQL: `https://supabase.com/dashboard/project/YOUR_PROJECT_ID/api/graphiql`

```graphql
# Get tenants with open tickets
query {
  tenantsCollection {
    edges {
      node {
        slug
        name
        ticketsCollection(filter: { state: { eq: "open" } }) {
          edges {
            node {
              number
              title
              severity
            }
          }
        }
      }
    }
  }
}
```

---

## 🔧 Cron Schedule Syntax

| Expression | Description |
|------------|-------------|
| `* * * * *` | Every minute |
| `0 * * * *` | Every hour |
| `0 0 * * *` | Daily at midnight |
| `0 2 * * *` | Daily at 2 AM |
| `0 0 * * 0` | Weekly (Sunday at midnight) |
| `0 0 1 * *` | Monthly (1st at midnight) |
| `0 0 L * *` | Last day of month |
| `0 9 1 1,4,7,10 *` | Quarterly (Jan, Apr, Jul, Oct) |
| `0 2 * * 1-5` | Weekdays at 2 AM |

**Format:** `minute hour day month weekday`

---

## 📊 Pre-Built Monitoring Dashboards

### Cron Job Health
```sql
SELECT * FROM vw_cron_job_health;
```

**Columns:**
- `jobname`: Name of the cron job
- `schedule`: Cron expression
- `active`: Whether job is active
- `total_runs`: Total executions (last 30 days)
- `successful_runs`: Successful executions
- `failed_runs`: Failed executions
- `last_run`: Last execution timestamp
- `avg_duration_seconds`: Average execution time

### Webhook Health
```sql
SELECT * FROM vw_webhook_health;
```

**Columns:**
- `url`: Webhook endpoint
- `enabled`: Active status
- `total_deliveries`: Total attempts (last 7 days)
- `successful`: Successfully delivered
- `failed`: Failed attempts
- `success_rate_pct`: Success percentage
- `avg_response_ms`: Average response time
- `last_attempt`: Last delivery attempt

---

## 💡 Use Case Examples

### Finance SSC Automation

#### Month-End Close
```sql
-- Already scheduled in cron_jobs.sql
-- Runs at 6 PM on last day of month
-- Creates tickets for all 8 agencies
```

#### BIR Quarterly Reports
```sql
-- Already scheduled in cron_jobs.sql
-- Runs at 9 AM on 1st of Jan, Apr, Jul, Oct
-- Creates BIR 2550Q reminder tickets
```

#### Daily Bank Reconciliation
```sql
-- Already scheduled in cron_jobs.sql
-- Runs at 2 AM Monday-Friday
-- Logs reconciliation audit entries
```

### Real-Time Integrations

#### GitHub → Odoo
```sql
-- Automatic: Triggers on new issues/PRs
-- Webhook: erp.insightpulseai.net/pulser_hub/github
-- See: webhook_triggers.sql
```

#### Tickets → Slack
```sql
-- Automatic: High/critical severity tickets
-- Gets Slack URL from integrations table
-- See: webhook_triggers.sql
```

#### Invoices → Alert System
```sql
-- Automatic: Invoices > ₱100,000
-- Webhook: erp.insightpulseai.net/api/alerts/invoice
-- See: webhook_triggers.sql
```

---

## 🛠️ Troubleshooting

### Cron Jobs Not Running?

```sql
-- Check if job is active
SELECT * FROM cron.job WHERE jobname = 'your-job-name';

-- Check for errors
SELECT * FROM cron.job_run_details
WHERE jobid = (SELECT jobid FROM cron.job WHERE jobname = 'your-job-name')
ORDER BY start_time DESC LIMIT 10;

-- Check Postgres logs
-- In Supabase Dashboard: Logs > Postgres Logs
```

### Webhooks Failing?

```sql
-- Check webhook status
SELECT * FROM webhook_deliveries
WHERE status = 'failed'
ORDER BY attempted_at DESC LIMIT 10;

-- Test webhook URL manually
SELECT net.http_post(
  url := 'your-webhook-url',
  headers := '{"Content-Type": "application/json"}'::jsonb,
  body := '{"test": true}'::jsonb
);

-- Check response
SELECT * FROM net._http_response ORDER BY created DESC LIMIT 5;

-- Retry failed webhooks
SELECT * FROM retry_failed_webhooks();
```

### GraphQL Not Working?

1. Check Supabase Dashboard: API Settings → GraphQL
2. Ensure RLS policies allow access
3. Check authentication token
4. Test in GraphiQL interface first

---

## 🔐 Security Notes

### Webhook Secrets

```sql
-- Store secrets properly
INSERT INTO secrets (tenant_id, name)
SELECT id, 'webhook_secret' FROM tenants WHERE slug = 'rim';

-- Never hardcode secrets in SQL
-- Use: current_setting('app.webhook_secret', true)
```

### Rate Limiting

```sql
-- Webhook rate limits are enforced
-- Default: 60 requests per minute
-- See: webhook_triggers.sql → check_webhook_rate_limit()
```

### Audit Logging

```sql
-- All webhook calls are logged
SELECT * FROM webhook_deliveries WHERE attempted_at > NOW() - INTERVAL '1 day';

-- Critical actions trigger security alerts
SELECT * FROM audit_logs WHERE action LIKE 'secret.%' ORDER BY created_at DESC;
```

---

## 📚 Resources

- **Full Guide:** `supabase/POSTGRES_EXTENSIONS_GUIDE.md`
- **Migrations:** `supabase/migrations/004_enable_extensions.sql`
- **Cron Jobs:** `supabase/cron_jobs.sql`
- **Webhooks:** `supabase/webhook_triggers.sql`
- **Tests:** `supabase/test_extensions.sql`

### External Docs
- [Supabase pg_cron](https://supabase.com/docs/guides/database/extensions/pg_cron)
- [Supabase Database Webhooks](https://supabase.com/docs/guides/database/webhooks)
- [Supabase GraphQL](https://supabase.com/docs/guides/api/graphql)
- [pg_cron GitHub](https://github.com/citusdata/pg_cron)
- [pg_net GitHub](https://github.com/supabase/pg_net)

---

## 🎯 Next Steps

1. ✅ Enable extensions: `004_enable_extensions.sql`
2. ✅ Run tests: `test_extensions.sql`
3. ✅ Set up cron jobs: `cron_jobs.sql`
4. ✅ Set up webhooks: `webhook_triggers.sql`
5. 📊 Create Superset dashboards for monitoring
6. 🔔 Configure Slack/Notion integrations
7. 🚀 Customize for your use cases

---

## 💬 Support

For issues or questions:
1. Check logs in Supabase Dashboard
2. Review `vw_cron_job_health` and `vw_webhook_health`
3. Test with `test_extensions.sql`
4. Refer to full guide: `POSTGRES_EXTENSIONS_GUIDE.md`

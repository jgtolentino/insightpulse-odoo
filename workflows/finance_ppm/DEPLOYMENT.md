# Finance PPM n8n Workflows - Deployment Guide

## Overview

Three production-ready n8n workflows for Finance PPM automation:

1. **BIR Deadline Alert** (`bir_deadline_alert.json`)
   - Daily scan for upcoming BIR filing deadlines
   - Schedule: Daily at 8:00 AM
   - Urgency-based routing to Mattermost channels

2. **Task Escalation** (`task_escalation.json`)
   - Alert supervisors for overdue Finance PPM tasks
   - Schedule: Twice daily (9:00 AM, 2:00 PM)
   - Escalation to directors for critical tasks

3. **Monthly Report** (`monthly_report.json`)
   - End-of-month compliance summary generation
   - Schedule: 1st of each month at 9:00 AM
   - Archives to Supabase + alerts Finance Director

## Prerequisites

### 1. Supabase Database
✅ **COMPLETED** - Table `finance_ppm.monthly_reports` created successfully

**Connection Details**:
- Host: `aws-1-us-east-1.pooler.supabase.com`
- Port: `6543` (pooler)
- Database: `postgres`
- Schema: `finance_ppm`

**Verification**:
```sql
SELECT schemaname, tablename, tableowner
FROM pg_tables
WHERE schemaname = 'finance_ppm' AND tablename = 'monthly_reports';
```

### 2. n8n Instance
- URL: `https://n8n.insightpulseai.net/`
- Status: ✅ Accessible
- API Access: ⚠️ Requires configuration

### 3. Odoo Instance
- URL: `https://odoo.insightpulseai.net/`
- Module: `ipai_finance_ppm` (v1.0.0)
- Status: ✅ Deployed and running
- Database: `production`

### 4. Mattermost Channels
Required channels:
- `finance-urgent` - Critical alerts
- `finance-escalations` - High-priority escalations
- `finance-alerts` - Normal notifications
- `finance-reports` - Monthly reports

## Deployment Steps

### Step 1: Configure n8n Credentials

**A. Odoo XML-RPC Credentials**

1. Navigate to: `https://n8n.insightpulseai.net/` → Settings → Credentials
2. Click "Add Credential" → Search for "HTTP Basic Auth"
3. Create credential: **Odoo Production**
   - Username: `admin` (or your Odoo username)
   - Password: `[Your Odoo password]`
4. Save credential

**B. Mattermost Webhook URL**

1. In Mattermost, go to: Settings → Integrations → Incoming Webhooks
2. Create webhook for each channel:
   - `finance-urgent`
   - `finance-escalations`
   - `finance-alerts`
   - `finance-reports`
3. Copy webhook URLs
4. In n8n: Settings → Credentials → Add "Mattermost Webhook"
   - Name: **Mattermost Finance Webhooks**
   - Store each webhook URL as environment variable or custom field

**C. Supabase Credentials**

1. In n8n: Settings → Credentials → Add "HTTP Basic Auth" or "PostgreSQL"
2. Create credential: **Supabase Production**
   - Method 1 (PostgreSQL):
     - Host: `aws-1-us-east-1.pooler.supabase.com`
     - Port: `6543`
     - Database: `postgres`
     - User: `postgres.ublqmilcjtpnflofprkr`
     - Password: `1G8TRd5wE7b9szBH`
   - Method 2 (REST API):
     - URL: `https://ublqmilcjtpnflofprkr.supabase.co/rest/v1/`
     - Service Role Key: `[Use SUPABASE_SERVICE_ROLE_KEY]`

### Step 2: Import Workflows

**Option A: Manual Import via UI** (Recommended)

1. Navigate to: `https://n8n.insightpulseai.net/workflows`
2. Click "+" → "Import from File"
3. Upload each workflow JSON file:
   - `bir_deadline_alert.json`
   - `task_escalation.json`
   - `monthly_report.json`
4. For each workflow:
   - Review nodes and connections
   - Update credentials to use the ones created in Step 1
   - Click "Save"

**Option B: API Import** (Once API access is configured)

```bash
# Set API key
export N8N_API_KEY="your_n8n_api_key"

# Import workflows
for workflow in bir_deadline_alert.json task_escalation.json monthly_report.json; do
  curl -X POST "https://n8n.insightpulseai.net/api/v1/workflows" \
    -H "X-N8N-API-KEY: $N8N_API_KEY" \
    -H "Content-Type: application/json" \
    -d @$workflow
done
```

### Step 3: Configure Workflow Settings

For each imported workflow:

**A. BIR Deadline Alert**
1. Open workflow in n8n editor
2. Click "Schedule Trigger" node
   - Verify cron: `0 8 * * *` (8 AM daily)
   - Timezone: UTC+8 (Philippine Time)
3. Click "Odoo Auth" node
   - Select credential: **Odoo Production**
4. Click "Send to Mattermost" node
   - Update webhook URL for appropriate channel
5. Test workflow manually: Click "Execute Workflow"
6. Activate workflow: Toggle "Active" switch

**B. Task Escalation**
1. Open workflow in n8n editor
2. Click "Schedule Trigger" node
   - Verify cron: `0 9,14 * * *` (9 AM and 2 PM)
   - Timezone: UTC+8
3. Update Odoo credentials
4. Update Mattermost webhook URLs:
   - Critical → `finance-urgent`
   - High → `finance-escalations`
5. Test and activate

**C. Monthly Report**
1. Open workflow in n8n editor
2. Click "Schedule Trigger" node
   - Verify cron: `0 9 1 * *` (9 AM, 1st of month)
   - Timezone: UTC+8
3. Update Odoo credentials
4. Click "Archive to Supabase" node
   - Configure PostgreSQL connection
   - Schema: `finance_ppm`
   - Table: `monthly_reports`
5. Update Mattermost webhook URL
6. Test and activate

### Step 4: Test Workflows

**Manual Test Execution**:

For each workflow:
1. Open workflow in n8n editor
2. Click "Execute Workflow" button
3. Monitor execution in real-time
4. Verify:
   - ✅ Odoo authentication successful
   - ✅ Data retrieved from Odoo
   - ✅ Business logic executed correctly
   - ✅ Mattermost notification sent
   - ✅ (Monthly Report only) Data saved to Supabase

**Test Queries**:

```sql
-- Verify monthly report saved
SELECT period, compliance_rate, alert_sent
FROM finance_ppm.monthly_reports
ORDER BY generated_at DESC
LIMIT 1;

-- Check workflow execution metadata
SELECT workflow_id, execution_id, generated_at
FROM finance_ppm.monthly_reports
WHERE period = TO_CHAR(CURRENT_DATE, 'YYYY-MM');
```

### Step 5: Verify Deployment

Run the verification script:

```bash
cd /Users/tbwa/odoo-ce/workflows/finance_ppm
./verify_deployment.sh
```

Expected output:
```
✅ n8n Instance: Accessible
✅ Odoo Instance: Accessible
✅ Supabase Table: finance_ppm.monthly_reports exists
✅ BIR Deadline Alert: Active
✅ Task Escalation: Active
✅ Monthly Report: Active
✅ All workflows operational
```

## Monitoring & Maintenance

### Execution Logs

Monitor workflow executions:
1. Navigate to: `https://n8n.insightpulseai.net/executions`
2. Filter by workflow name
3. Check for errors or failures

### Error Notifications

All workflows include error handling:
- Retry logic (3 attempts with exponential backoff)
- Error notifications to `finance-urgent` channel
- Execution summary logging

### Monthly Review

Check monthly report compliance:
```sql
SELECT
    period,
    compliance_rate,
    late_filings,
    finance_director_notified
FROM finance_ppm.monthly_reports
WHERE generated_at >= CURRENT_DATE - INTERVAL '12 months'
ORDER BY period DESC;
```

## Troubleshooting

### Workflow Not Executing

**Check 1: Workflow Active Status**
- Go to n8n → Workflows → Check "Active" toggle

**Check 2: Schedule Trigger**
- Open workflow → Click "Schedule Trigger" node
- Verify cron expression is valid
- Check timezone setting (UTC+8)

**Check 3: Credentials**
- Settings → Credentials
- Test each credential connection

### Odoo Authentication Failed

**Error**: `Authentication failed` or `Invalid UID`

**Solution**:
1. Verify Odoo credentials in n8n
2. Test Odoo login manually at `https://odoo.insightpulseai.net/`
3. Check if user has access to `ipai_finance_ppm` module
4. Update "Odoo Auth" node with correct credentials

### Mattermost Notification Not Sent

**Error**: `Webhook URL not found` or `Message delivery failed`

**Solution**:
1. Verify webhook URLs in Mattermost
2. Check channel names match exactly
3. Test webhook with curl:
```bash
curl -X POST "https://mattermost.insightpulseai.net/hooks/YOUR_WEBHOOK_ID" \
  -H "Content-Type: application/json" \
  -d '{"text":"Test notification"}'
```

### Supabase Insert Failed

**Error**: `Permission denied for schema finance_ppm`

**Solution**:
1. Verify RLS policies are configured
2. Check service role key is being used
3. Run migration script again if table missing:
```bash
psql "$POSTGRES_URL" -f /Users/tbwa/odoo-ce/migrations/003_finance_ppm_reports.sql
```

## Rollback Procedure

If workflows cause issues:

1. **Deactivate workflows immediately**:
   - Go to n8n → Workflows
   - Toggle "Active" switch OFF for each workflow

2. **Review execution logs**:
   - Check last 10 executions for errors
   - Identify root cause

3. **Restore previous version** (if applicable):
   - Export current workflow (backup)
   - Import previous working version
   - Test before reactivating

4. **Database rollback** (if data corruption):
```sql
-- Delete problematic monthly report
DELETE FROM finance_ppm.monthly_reports
WHERE period = 'YYYY-MM' AND execution_id = 'problematic_id';
```

## Support

For issues or questions:
- Documentation: This file
- Odoo Logs: `ssh root@odoo.insightpulseai.net "docker logs odoo-odoo-1 --tail 100"`
- n8n Logs: Check execution history in n8n UI
- Supabase: Check table via psql or Supabase dashboard

## Changelog

### 2025-11-23 - Initial Deployment
- Created 3 workflows: BIR alerts, task escalation, monthly report
- Created Supabase table: `finance_ppm.monthly_reports`
- Applied migration: `003_finance_ppm_reports.sql`
- Documented deployment procedure

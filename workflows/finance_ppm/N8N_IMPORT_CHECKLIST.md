# n8n Workflow Import Checklist

**Deployment Date**: 2025-11-23
**Status**: Ready for manual import
**Estimated Time**: 15-30 minutes

---

## Pre-Import Setup

### 1. Access n8n Instance
- [ ] Navigate to: `https://n8n.insightpulseai.net/`
- [ ] Login with your credentials
- [ ] Verify you have admin/workflow creation permissions

### 2. Gather Required Credentials

#### A. Odoo XML-RPC
- [ ] Odoo URL: `https://erp.insightpulseai.net/`
- [ ] Database name: `production`
- [ ] Username: `admin` (or your Odoo username)
- [ ] Password: `[Your Odoo password]`

#### B. Mattermost Webhooks
Create webhooks for these channels:
- [ ] `finance-urgent` - Critical alerts
- [ ] `finance-escalations` - High-priority escalations
- [ ] `finance-alerts` - Normal notifications
- [ ] `finance-reports` - Monthly reports

**Steps to create webhooks**:
1. Go to: `https://mattermost.insightpulseai.net/`
2. Settings → Integrations → Incoming Webhooks
3. Click "Add Incoming Webhook"
4. Select channel
5. Copy webhook URL
6. Repeat for all 4 channels

#### C. Supabase Database
- [ ] Connection method: PostgreSQL OR REST API
- [ ] If PostgreSQL:
  - Host: `aws-1-us-east-1.pooler.supabase.com`
  - Port: `6543`
  - Database: `postgres`
  - User: `postgres.ublqmilcjtpnflofprkr`
  - Password: `1G8TRd5wE7b9szBH`
- [ ] If REST API:
  - URL: `https://ublqmilcjtpnflofprkr.supabase.co/rest/v1/`
  - Service Role Key: `[Use SUPABASE_SERVICE_ROLE_KEY]`

---

## Workflow Import Order

Import in this sequence (top-down for shared credentials):

### Workflow 1: Monthly Report
**File**: `monthly_report.json` (15.5 KB, 11 nodes)

- [ ] Go to: n8n → Workflows → "+" → "Import from File"
- [ ] Upload: `/Users/tbwa/odoo-ce/workflows/finance_ppm/monthly_report.json`
- [ ] Review imported workflow:
  - [ ] 11 nodes visible
  - [ ] Connections intact
  - [ ] Schedule trigger: `0 9 1 * *` (1st of month, 9 AM)
- [ ] Configure credentials:
  - [ ] Node "Odoo Auth" → Select/Create "Odoo Production"
  - [ ] Node "Archive to Supabase" → Select/Create "Supabase Production"
  - [ ] Node "Post to Mattermost" → Enter webhook URL for `finance-reports`
  - [ ] Node "Alert Finance Director" → Enter webhook URL for `finance-urgent`
- [ ] Save workflow (name: "Finance PPM - Monthly Compliance Report")
- [ ] Test execution:
  - [ ] Click "Execute Workflow"
  - [ ] Monitor execution log
  - [ ] Verify: Odoo auth successful
  - [ ] Verify: Data retrieved from Odoo
  - [ ] Verify: Mattermost notification sent
  - [ ] Verify: Supabase insert successful
- [ ] Activate workflow (toggle "Active" switch)

### Workflow 2: BIR Deadline Alert
**File**: `bir_deadline_alert.json` (11.3 KB, 9 nodes)

- [ ] Import: n8n → Workflows → "+" → "Import from File"
- [ ] Upload: `/Users/tbwa/odoo-ce/workflows/finance_ppm/bir_deadline_alert.json`
- [ ] Review imported workflow:
  - [ ] 9 nodes visible
  - [ ] Schedule trigger: `0 8 * * *` (daily 8 AM)
- [ ] Configure credentials:
  - [ ] Node "Odoo Auth" → Select "Odoo Production" (reuse from Workflow 1)
  - [ ] Node "Send to Mattermost" → Enter webhook URL for:
    - Critical urgency → `finance-urgent`
    - High/Normal urgency → `finance-alerts`
- [ ] Save workflow (name: "Finance PPM - BIR Deadline Alert")
- [ ] Test execution:
  - [ ] Click "Execute Workflow"
  - [ ] Verify: BIR schedules retrieved
  - [ ] Verify: Urgency calculated correctly
  - [ ] Verify: Mattermost notification sent
- [ ] Activate workflow

### Workflow 3: Task Escalation
**File**: `task_escalation.json` (13.4 KB, 10 nodes)

- [ ] Import: n8n → Workflows → "+" → "Import from File"
- [ ] Upload: `/Users/tbwa/odoo-ce/workflows/finance_ppm/task_escalation.json`
- [ ] Review imported workflow:
  - [ ] 10 nodes visible
  - [ ] Schedule trigger: `0 9,14 * * *` (9 AM and 2 PM daily)
- [ ] Configure credentials:
  - [ ] Node "Odoo Auth" → Select "Odoo Production" (reuse)
  - [ ] Node "Send Escalation" → Enter webhook URL for:
    - Critical → `finance-urgent`
    - High → `finance-escalations`
  - [ ] Node "Log in Odoo Chatter" → Uses same Odoo credentials
- [ ] Save workflow (name: "Finance PPM - Task Escalation")
- [ ] Test execution:
  - [ ] Click "Execute Workflow"
  - [ ] Verify: Overdue tasks retrieved
  - [ ] Verify: Severity calculated
  - [ ] Verify: Escalation message sent
  - [ ] Verify: Odoo chatter log created
- [ ] Activate workflow

---

## Post-Import Verification

### 1. Check Active Workflows
- [ ] Navigate to: n8n → Workflows
- [ ] Verify all 3 workflows show "Active" status:
  - [ ] Finance PPM - Monthly Compliance Report
  - [ ] Finance PPM - BIR Deadline Alert
  - [ ] Finance PPM - Task Escalation

### 2. Verify Schedule Triggers
- [ ] Monthly Report: Next run = 1st of next month at 9:00 AM
- [ ] BIR Alert: Next run = Tomorrow at 8:00 AM
- [ ] Task Escalation: Next run = Today at 2:00 PM (or tomorrow 9:00 AM)

### 3. Check Execution History
- [ ] Go to: n8n → Executions
- [ ] Verify manual test executions logged
- [ ] Check for any errors or warnings

### 4. Database Verification
Run this query in Supabase or psql:
```sql
-- Should return 1 row from test execution
SELECT
    period,
    compliance_rate,
    alert_sent,
    generated_at
FROM finance_ppm.monthly_reports
ORDER BY generated_at DESC
LIMIT 1;
```

- [ ] Test report exists in database
- [ ] All required columns populated
- [ ] `alert_sent` = true if test included alert

### 5. Mattermost Verification
- [ ] Check `finance-reports` channel for test notification
- [ ] Check `finance-alerts` channel for BIR alert (if any deadlines found)
- [ ] Check `finance-escalations` channel for task escalation (if any overdue tasks)
- [ ] Verify message formatting is correct

---

## Troubleshooting

### Workflow Import Fails
**Error**: "Invalid workflow format"

**Solution**:
1. Verify JSON file integrity:
   ```bash
   jq empty /Users/tbwa/odoo-ce/workflows/finance_ppm/monthly_report.json
   ```
2. Re-download workflow file from repository
3. Try importing again

### Odoo Authentication Fails
**Error**: "Authentication failed" or "Invalid credentials"

**Solution**:
1. Test Odoo login manually at `https://erp.insightpulseai.net/`
2. Verify database name is exactly `production`
3. Check user has access to Finance PPM module
4. Update credential in n8n → Settings → Credentials

### Mattermost Notification Not Sent
**Error**: "Webhook URL not found" or "Failed to send message"

**Solution**:
1. Verify webhook URL is correct (copy from Mattermost)
2. Test webhook with curl:
   ```bash
   curl -X POST "https://mattermost.insightpulseai.net/hooks/YOUR_WEBHOOK_ID" \
     -H "Content-Type: application/json" \
     -d '{"text":"Test notification from n8n"}'
   ```
3. Check channel permissions in Mattermost

### Supabase Insert Fails
**Error**: "Permission denied" or "Table not found"

**Solution**:
1. Verify table exists:
   ```sql
   SELECT * FROM finance_ppm.monthly_reports LIMIT 1;
   ```
2. Check RLS policies are configured
3. Verify service role key is being used (not anon key)
4. Reapply migration if needed:
   ```bash
   psql "$POSTGRES_URL" -f /Users/tbwa/odoo-ce/migrations/003_finance_ppm_reports.sql
   ```

### Workflow Executes But No Data
**Error**: Workflow runs but retrieves 0 records from Odoo

**Solution**:
1. Check if Finance PPM module is installed in Odoo:
   ```bash
   # Login to Odoo → Apps → Search "Finance PPM"
   # Should show "Installed" status
   ```
2. Verify seed data exists:
   - Go to: Finance PPM → BIR Schedule
   - Should see 8 forms with deadlines
3. Check Odoo query filters in workflow
4. Adjust date ranges if testing with future dates

---

## Rollback Procedure

If workflows cause issues:

1. **Deactivate immediately**:
   - [ ] Go to n8n → Workflows
   - [ ] Toggle "Active" OFF for all 3 workflows

2. **Review execution logs**:
   - [ ] n8n → Executions → Check last 10 runs
   - [ ] Identify error patterns

3. **Delete test data** (if needed):
   ```sql
   DELETE FROM finance_ppm.monthly_reports
   WHERE generated_at >= CURRENT_DATE;
   ```

4. **Delete workflows** (if needed):
   - [ ] n8n → Workflows → Select workflow → Delete
   - [ ] Workflows can be re-imported from JSON files

---

## Sign-Off Checklist

### Final Verification
- [ ] All 3 workflows imported successfully
- [ ] All credentials configured correctly
- [ ] All workflows tested manually (green execution)
- [ ] All workflows activated
- [ ] Mattermost notifications received
- [ ] Supabase data saved correctly
- [ ] No errors in execution logs
- [ ] Schedule triggers verified for next run

### Documentation
- [ ] DEPLOYMENT.md read and understood
- [ ] DEPLOYMENT_SUMMARY.md reviewed
- [ ] CHANGELOG.md updated (already done)
- [ ] This checklist completed

### Communication
- [ ] Finance team notified of automation go-live
- [ ] Mattermost channel members alerted to expect notifications
- [ ] Support team informed of new workflows

---

## Next Steps After Import

### 1. Monitor First Executions
- [ ] BIR Alert: Check tomorrow at 8:00 AM
- [ ] Task Escalation: Check today at 2:00 PM (or tomorrow 9:00 AM)
- [ ] Monthly Report: Check 1st of next month at 9:00 AM

### 2. Performance Tuning (Optional)
- [ ] Review execution times in n8n logs
- [ ] Optimize queries if execution >30 seconds
- [ ] Add caching if needed

### 3. Dashboard Setup (Optional)
- [ ] Create Supabase dashboard for monthly reports
- [ ] Build Mattermost bot for on-demand queries
- [ ] Integrate with Odoo UI panel

### 4. Documentation Updates
- [ ] Document any credential changes
- [ ] Update DEPLOYMENT.md with actual webhook URLs
- [ ] Add troubleshooting notes based on issues encountered

---

**Import completed by**: _______________
**Date**: _______________
**Time spent**: _______________
**Issues encountered**: _______________

---

## Support Contacts

- **Technical Support**: Jake Tolentino (Finance SSC Manager)
- **Deployment Guide**: `/Users/tbwa/odoo-ce/workflows/finance_ppm/DEPLOYMENT.md`
- **Verification Script**: `/Users/tbwa/odoo-ce/workflows/finance_ppm/verify_deployment.sh`

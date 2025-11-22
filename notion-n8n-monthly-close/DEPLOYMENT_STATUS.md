# n8n Finance Automation - Deployment Status

**Date**: 2025-11-21
**Status**: ✅ Workflows deployed to production n8n
**Environment**: https://ipa.insightpulseai.net
**Container**: odoo-ipa-1

---

## ✅ Completed

### 1. Infrastructure Setup
- ✅ Workflow registry system (`workflows/index.yaml`)
- ✅ CLI management tool (`scripts/n8n-sync.sh`)
- ✅ Documentation (`N8N_CLI_README.md`, `WORKFLOW_CONVENTIONS.md`)
- ✅ Git repository structure

### 2. Production Workflows Deployed

#### W001_OD_MNTH_CLOSE_SYNC (ID: 25)
**Name**: `closing_daily_digest`
**Schedule**: 8 AM PHT, weekdays (Mon-Fri)
**Purpose**: Daily digest of overdue/due-soon closing tasks by cluster

**Workflow**:
```
Cron Trigger (8 AM PHT)
  ↓
Odoo XML-RPC Query (project.task)
  Filter: stage IN (In Progress, Blocked, Ready to Post)
  Filter: cluster != null
  ↓
JavaScript Function (Parse & Group by Cluster)
  ↓
JavaScript Function (Build Mattermost Message)
  ↓
Mattermost Post (#finance-alerts)
```

**Sample Output**:
```markdown
## 🚨 Daily Closing Digest

**Date**: November 21, 2025

### CKVC
- **In Progress**: 3
- **Blocked**: 1 ⚠️
- **Ready to Post**: 2
- **Total**: 6

**Blocked Tasks**:
  - AR aging reconciliation (CKVC) - Deadline: 2025-11-22

[View in Odoo](https://erp.insightpulseai.net/web#action=project.action_view_task)
```

#### W002_OD_BIR_ALERTS (ID: 26)
**Name**: `bir_calendar_alerts`
**Schedule**: 9 AM PHT, daily
**Purpose**: 7-day advance alerts for BIR filing deadlines

**Workflow**:
```
Cron Trigger (9 AM PHT)
  ↓
Calculate Target Date (today + 7 days)
  ↓
Odoo XML-RPC Query (project.task)
  Filter: bir_deadline = target_date
  Filter: bir_form != null
  Filter: stage != Done
  ↓
If (Has Upcoming Deadlines?)
  ├─ YES → Build Alert Message → Mattermost Post
  └─ NO  → Silent exit
```

**Sample Output**:
```markdown
## 📅 BIR Filing Alerts (7 Days)

**Alert Date**: November 21, 2025

### 1601-C
- **CKVC** (CKVC)
  Deadline: 2025-11-28
  [View Task](https://erp.insightpulseai.net/web#id=123&model=project.task)

### 2550Q
- **RIM** (RIM)
  Deadline: 2025-11-28
  [View Task](https://erp.insightpulseai.net/web#id=124&model=project.task)

---
**Action Required**: Please review and file before deadline.
@finance-team @ckvc @rim
```

#### W101_SB_CLOSE_SNAPSHOT (ID: 30)
**Name**: `supabase_close_state_snapshot`
**Schedule**: 11 PM PHT, daily
**Purpose**: Nightly snapshot of closing state to Supabase

**Workflow**:
```
Cron Trigger (11 PM PHT)
  ↓
HTTP Request → Supabase Edge Function
  URL: https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/monthly_close_reminder
  Method: POST
  Body: {"source": "n8n", "runType": "nightly_snapshot"}
  ↓
If (Status Code = 200?)
  ├─ YES → Mattermost Success Notification
  └─ NO  → Mattermost Failure Alert
```

**Sample Success Output**:
```markdown
✅ **Monthly Close Snapshot Complete**

Snapshot created at: 2025-11-21 23:00:00 PHT

Source: n8n automation

[View in Supabase](https://supabase.com/dashboard/project/spdtwktxdalcfigzeqrz/editor)
```

---

## 🔄 Next Steps

### Step 1: Configure Credentials in n8n UI

Login to https://ipa.insightpulseai.net and configure these credentials:

#### 1.1 Odoo Basic Auth (ID: 1)
```yaml
Type: HTTP Basic Auth
Name: "Odoo Basic Auth"
User: <odoo_uid>
Password: <odoo_api_key>
```

#### 1.2 Mattermost Webhooks

**Finance Alerts (ID: 2)**:
```yaml
Type: Mattermost Webhook
Name: "Mattermost Finance Alerts"
Webhook URL: https://mattermost.insightpulseai.net/hooks/<webhook-id>
```

**BIR Alerts (ID: 3)**:
```yaml
Type: Mattermost Webhook
Name: "Mattermost BIR Alerts"
Webhook URL: https://mattermost.insightpulseai.net/hooks/<webhook-id>
```

#### 1.3 Supabase Service Role (ID: 4)
```yaml
Type: HTTP Header Auth
Name: "Supabase Service Role Key"
Header Name: "Authorization"
Header Value: "Bearer <service_role_key>"
```

### Step 2: Test Workflows Manually

For each workflow, in the n8n UI:

1. Open workflow editor
2. Click "Execute Workflow" button
3. Verify nodes execute successfully
4. Check Mattermost for test messages
5. Review any errors in execution logs

**Test Commands (CLI alternative)**:
```bash
# W001 - Daily closing digest
ssh root@erp.insightpulseai.net "docker exec -u node odoo-ipa-1 n8n execute --id 25"

# W002 - BIR alerts
ssh root@erp.insightpulseai.net "docker exec -u node odoo-ipa-1 n8n execute --id 26"

# W101 - Closing snapshot
ssh root@erp.insightpulseai.net "docker exec -u node odoo-ipa-1 n8n execute --id 30"
```

### Step 3: Activate Workflows

After successful testing, activate workflows:

**Via UI**:
- Toggle "Active" switch for each workflow

**Via CLI**:
```bash
ssh root@erp.insightpulseai.net "docker exec -u node odoo-ipa-1 n8n update:workflow --id=25 --active=true"
ssh root@erp.insightpulseai.net "docker exec -u node odoo-ipa-1 n8n update:workflow --id=26 --active=true"
ssh root@erp.insightpulseai.net "docker exec -u node odoo-ipa-1 n8n update:workflow --id=30 --active=true"
```

### Step 4: Implement Supabase Edge Function

Create Edge Function for W101_SB_CLOSE_SNAPSHOT:

**File**: `supabase/functions/monthly_close_reminder/index.ts`

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  try {
    const { source, runType, timestamp } = await req.json()

    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Query Odoo closing state via Supabase
    // (requires prior sync or real-time replication)

    // Insert snapshot
    const { data, error } = await supabase
      .from('close_state_snapshots')
      .insert({
        source,
        run_type: runType,
        timestamp: timestamp || new Date().toISOString(),
        snapshot_data: {
          // closing state data
        }
      })

    if (error) throw error

    return new Response(
      JSON.stringify({ success: true, data }),
      { headers: { 'Content-Type': 'application/json' }, status: 200 }
    )
  } catch (error) {
    return new Response(
      JSON.stringify({ success: false, error: error.message }),
      { headers: { 'Content-Type': 'application/json' }, status: 500 }
    )
  }
})
```

**Deploy**:
```bash
supabase functions deploy monthly_close_reminder --project-ref spdtwktxdalcfigzeqrz
```

### Step 5: Optional - Setup pg_cron (Alternative to W101)

If you prefer database-native scheduling instead of n8n for snapshots:

```sql
-- Enable pg_cron extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- Schedule nightly snapshot at 11 PM PHT (15:00 UTC)
SELECT cron.schedule(
  'monthly_close_snapshot',
  '0 15 * * *',
  $$
  SELECT net.http_post(
    url := 'https://spdtwktxdalcfigzeqrz.supabase.co/functions/v1/monthly_close_reminder',
    headers := '{"Content-Type": "application/json", "Authorization": "Bearer ' || current_setting('app.service_role_key') || '"}'::jsonb,
    body := '{"source": "pg_cron", "runType": "nightly_snapshot"}'::jsonb
  ) AS request_id;
  $$
);
```

---

## 📊 Monitoring & Maintenance

### Check Workflow Status
```bash
# List all workflows
./scripts/n8n-sync.sh list

# Check workflow status
./scripts/n8n-sync.sh status
```

### Backup Workflows
```bash
# Create timestamped backup
./scripts/n8n-sync.sh backup
```

### View Execution Logs
```bash
# SSH into server
ssh root@erp.insightpulseai.net

# View n8n container logs
docker logs -f odoo-ipa-1
```

### Troubleshooting

**Workflow not executing**:
1. Check if workflow is active: `./scripts/n8n-sync.sh status`
2. Verify credentials are configured in n8n UI
3. Check container logs for errors

**Mattermost webhook not working**:
1. Verify webhook URL is correct
2. Test webhook with curl:
   ```bash
   curl -X POST https://mattermost.insightpulseai.net/hooks/<webhook-id> \
     -H "Content-Type: application/json" \
     -d '{"text": "Test message"}'
   ```

**Odoo XML-RPC errors**:
1. Verify Odoo credentials (uid, password)
2. Check Odoo server is accessible: `curl https://erp.insightpulseai.net`
3. Verify XML-RPC endpoint: `curl https://erp.insightpulseai.net/xmlrpc/2/common`

---

## 🎯 Success Criteria

- [ ] All credentials configured in n8n
- [ ] W001 successfully posts daily closing digest to Mattermost
- [ ] W002 successfully posts BIR alerts 7 days before deadline
- [ ] W101 successfully triggers Supabase Edge Function
- [ ] All workflows activated and running on schedule
- [ ] Edge Function deployed and operational
- [ ] No errors in n8n execution logs

---

**Last Updated**: 2025-11-21
**Maintained By**: Finance SSC Team - InsightPulse AI

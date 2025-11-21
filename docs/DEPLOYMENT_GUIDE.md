# Deployment Guide: Finance Stack Health Monitoring & Automation

Complete deployment guide for the InsightPulse finance automation infrastructure.

## Prerequisites

### Access Requirements

- [x] SSH access to `erp.insightpulseai.net`
- [x] Admin access to n8n (`https://ipa.insightpulseai.net`)
- [x] Supabase project access (`xkxyvboeubffxxbebsll`)
- [x] GitHub repository admin access
- [x] Mattermost webhook access

### Required Credentials

```bash
# Odoo
ODOO_URL=https://erp.insightpulseai.net
ODOO_DB=odoo
ODOO_LOGIN=jgtolentino_rn@yahoo.com
ODOO_PASSWORD=<from_1password>

# Supabase
SUPABASE_PROJECT_REF=xkxyvboeubffxxbebsll
SUPABASE_URL=https://xkxyvboeubffxxbebsll.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<from_supabase_dashboard>

# n8n
N8N_API_KEY=<from_n8n_settings>
N8N_WEBHOOK_URL=<webhook_url_for_alerts>

# Mattermost
MATTERMOST_WEBHOOK_URL=<from_mattermost_integrations>
```

## Phase 1: Supabase Setup (15 minutes)

### Step 1.1: Create Health Check Table

```bash
# Navigate to Supabase SQL Editor
# https://supabase.com/dashboard/project/xkxyvboeubffxxbebsll/sql/new

# Copy and execute: packages/db/sql/02_health_check_table.sql
```

**Verification:**
```sql
-- Check table exists
SELECT * FROM public.health_check LIMIT 1;

-- Check views exist
SELECT * FROM public.health_check_summary;
```

### Step 1.2: Create Knowledge Embeddings Table (for Knowledge Gov workflow)

```sql
CREATE TABLE IF NOT EXISTS public.knowledge_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  page_id INTEGER NOT NULL,
  page_name TEXT NOT NULL,
  embedding VECTOR(1536),
  content TEXT,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX ON public.knowledge_embeddings USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX ON public.knowledge_embeddings(page_id);

ALTER TABLE public.knowledge_embeddings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow authenticated read"
  ON public.knowledge_embeddings
  FOR SELECT
  USING (auth.role() = 'authenticated');
```

## Phase 2: Server Deployment (30 minutes)

### Step 2.1: Deploy Scripts to erp.insightpulseai.net

```bash
# SSH to server
ssh root@erp.insightpulseai.net

# Create directory structure
mkdir -p /opt/odoo-ce/notion-n8n-monthly-close/scripts
mkdir -p /opt/odoo-ce/scripts
mkdir -p /opt/odoo-ce/packages/db/sql

# Exit SSH for now
exit
```

### Step 2.2: Copy Files to Server

```bash
# From your local odoo-ce repository
cd /Users/tbwa/Documents/GitHub/odoo-ce

# Copy scripts
scp scripts/check_project_tasks.py root@erp.insightpulseai.net:/opt/odoo-ce/scripts/
scp notion-n8n-monthly-close/scripts/verify_finance_stack.sh root@erp.insightpulseai.net:/opt/odoo-ce/notion-n8n-monthly-close/scripts/

# Copy SQL schema
scp packages/db/sql/02_health_check_table.sql root@erp.insightpulseai.net:/opt/odoo-ce/packages/db/sql/

# Set permissions
ssh root@erp.insightpulseai.net "chmod +x /opt/odoo-ce/scripts/check_project_tasks.py"
ssh root@erp.insightpulseai.net "chmod +x /opt/odoo-ce/notion-n8n-monthly-close/scripts/verify_finance_stack.sh"
```

### Step 2.3: Configure Environment Variables on Server

```bash
ssh root@erp.insightpulseai.net

# Create .env file for health checks
cat > /opt/odoo-ce/.env.health << 'EOF'
ODOO_URL=https://erp.insightpulseai.net
ODOO_DB=odoo
ODOO_LOGIN=jgtolentino_rn@yahoo.com
ODOO_PASSWORD=<actual_password>

SUPABASE_PROJECT_REF=xkxyvboeubffxxbebsll
SUPABASE_SERVICE_ROLE_KEY=<actual_key>

N8N_API_KEY=<actual_key>
EOF

chmod 600 /opt/odoo-ce/.env.health
```

### Step 2.4: Test Scripts Manually

```bash
# Source environment
source /opt/odoo-ce/.env.health

# Test check_project_tasks.py
cd /opt/odoo-ce
python3 scripts/check_project_tasks.py

# Test verify_finance_stack.sh
cd /opt/odoo-ce/notion-n8n-monthly-close
./scripts/verify_finance_stack.sh --env prod --verbose
```

**Expected:** All checks should pass with green ✅ marks.

## Phase 3: n8n Configuration (45 minutes)

### Step 3.1: Create Odoo Credentials

1. Go to `https://ipa.insightpulseai.net` → Settings → Credentials
2. Click "+ Add Credential" → Search "Odoo"
3. Create credential: `odoo-prod-main`
   - Base URL: `https://erp.insightpulseai.net`
   - Database: `odoo`
   - Username: `jgtolentino_rn@yahoo.com`
   - Password/API Key: `<from_1password>`
4. Test connection → Save

5. Repeat for `odoo-staging`:
   - Base URL: `https://staging.insightpulseai.net`
   - Database: `odoo`
   - Username: `jgtolentino_rn@yahoo.com`
   - Password/API Key: `<from_1password>`

### Step 3.2: Create Other Credentials

**OpenAI API (for Knowledge Gov):**
- Type: HTTP Header Auth
- Name: `OpenAI API`
- Header Name: `Authorization`
- Header Value: `Bearer <openai_api_key>`

**Supabase Postgres (for Knowledge Gov):**
- Type: Postgres
- Name: `Supabase Postgres`
- Host: `aws-1-us-east-1.pooler.supabase.com`
- Port: `6543`
- Database: `postgres`
- User: `postgres`
- Password: `<from_supabase_dashboard>`
- SSL: Enabled

### Step 3.3: Import Workflows

1. Navigate to n8n: `https://ipa.insightpulseai.net`
2. Click "+" → "Import from File"
3. Import workflows in order:
   - `W150_FINANCE_HEALTH_CHECK.json`
   - `ODOO_EXPENSE_OCR.json`
   - `ODOO_BIR_PREP.json`
   - `ODOO_KNOWLEDGE_GOV.json`

### Step 3.4: Configure Workflow Credentials

For each workflow, replace placeholders:
- `REPLACE_WITH_ODOO_CREDENTIAL_ID` → Select `odoo-prod-main`
- `REPLACE_WITH_OPENAI_CREDENTIAL_ID` → Select `OpenAI API`
- `REPLACE_WITH_SUPABASE_CREDENTIAL_ID` → Select `Supabase Postgres`

### Step 3.5: Configure Environment Variables in n8n

Settings → Variables:
- `SUPABASE_SERVICE_ROLE_KEY`: `<from_supabase>`
- `N8N_API_KEY`: `<from_n8n_user_settings>`
- `MATTERMOST_WEBHOOK_URL`: `<from_mattermost>`
- `ODOO_PASSWORD`: `<from_1password>`

### Step 3.6: Test Workflows

**Test W150 (Health Check):**
1. Open workflow → Click "Test workflow"
2. Should execute both SSH commands
3. Check Mattermost #finance-alerts for notification

**Test ODOO_EXPENSE_OCR:**
1. Open workflow → Get webhook URL
2. Test webhook: `curl -X POST <webhook-url> -d '{"id": 1}'`
3. Should fail gracefully (expense 1 may not exist)

**Test ODOO_BIR_PREP:**
1. Open workflow → Click "Execute Workflow"
2. Should generate BIR forms for previous month
3. Check Odoo for created forms

**Test ODOO_KNOWLEDGE_GOV:**
1. Open workflow → Get webhook URL
2. Test webhook: `curl -X POST <webhook-url> -d '{"id": 1}'`
3. Should process knowledge page

### Step 3.7: Enable Workflows

For production:
- ✅ Enable W150_FINANCE_HEALTH_CHECK (cron: daily 7:30 AM PHT)
- ⚠️ Enable ODOO_EXPENSE_OCR (webhook: on-demand)
- ✅ Enable ODOO_BIR_PREP (cron: monthly 5th 2 AM)
- ⚠️ Enable ODOO_KNOWLEDGE_GOV (webhook: on-demand)

## Phase 4: GitHub Actions Setup (20 minutes)

### Step 4.1: Add Repository Secrets

Navigate to: `https://github.com/jgtolentino/odoo-ce/settings/secrets/actions`

Add secrets:
```
SSH_PRIVATE_KEY          <private_key_for_erp_server>
SSH_KNOWN_HOSTS          <output_of: ssh-keyscan erp.insightpulseai.net>
SUPABASE_SERVICE_ROLE_KEY <from_supabase_dashboard>
N8N_API_KEY              <from_n8n_user_settings>
ODOO_PASSWORD            <from_1password>
N8N_WEBHOOK_URL          <webhook_url_for_w150_alerts>
```

### Step 4.2: Enable Workflow

1. Go to Actions tab
2. Find "Finance Stack Health Check"
3. Enable workflow
4. Run manual trigger to test

### Step 4.3: Verify Execution

- Check Actions tab for workflow run
- Download artifact "health-report-prod-{run_id}"
- Verify Mattermost notification received

## Phase 5: Odoo Integration (30 minutes)

### Step 5.1: Create Webhook Server Actions

In Odoo (as admin):

**For Expense OCR:**
1. Go to Settings → Technical → Automation → Server Actions
2. Create new:
   - Name: `Expense Created - Trigger OCR`
   - Model: `hr.expense`
   - Trigger: On Creation
   - Action: Execute Python Code
   - Code:
   ```python
   import requests
   import json

   url = "https://ipa.insightpulseai.net/webhook/odoo/expense/created"
   payload = {
       "id": record.id,
       "employee_id": record.employee_id.id,
       "total_amount": record.total_amount,
       "state": record.state
   }
   requests.post(url, json=payload, timeout=5)
   ```

**For Knowledge Governance:**
1. Create new:
   - Name: `Knowledge Page Updated - Trigger Governance`
   - Model: `insightpulse_knowledge.page`
   - Trigger: On Update
   - Action: Execute Python Code
   - Code:
   ```python
   import requests
   import json

   url = "https://ipa.insightpulseai.net/webhook/odoo/knowledge/page-updated"
   payload = {
       "id": record.id,
       "name": record.name,
       "owner_id": record.owner_id.id if record.owner_id else None
   }
   requests.post(url, json=payload, timeout=5)
   ```

### Step 5.2: Test Odoo → n8n Integration

1. Create a test expense in Odoo
2. Check n8n execution log for ODOO_EXPENSE_OCR workflow
3. Verify Mattermost notification

## Phase 6: Monitoring Setup (15 minutes)

### Step 6.1: Configure Mattermost Channels

Create channels (if not exist):
- `#finance-alerts` - Health check failures, BIR notifications
- `#finance-ssc` - Expense OCR notifications
- `#finance-knowledge` - Knowledge page updates

### Step 6.2: Create Supabase Dashboard

Optional: Create saved queries in Supabase for easy monitoring:

**Health Status Dashboard:**
```sql
SELECT * FROM public.health_check_summary ORDER BY environment;
```

**Recent Failures:**
```sql
SELECT * FROM public.health_check_recent_failures LIMIT 20;
```

### Step 6.3: Bookmark Important Links

- Supabase Health Checks: `https://supabase.com/dashboard/project/xkxyvboeubffxxbebsll/editor/29274?sort=created_at%3Adesc`
- n8n Workflows: `https://ipa.insightpulseai.net/workflows`
- GitHub Actions: `https://github.com/jgtolentino/odoo-ce/actions/workflows/health-check.yml`
- Mattermost Alerts: `https://mattermost.insightpulseai.net/finance-alerts`

## Verification Checklist

### ✅ Scripts Deployed
- [ ] `check_project_tasks.py` on server and executable
- [ ] `verify_finance_stack.sh` on server and executable
- [ ] Both scripts run successfully manually

### ✅ Supabase Configured
- [ ] `health_check` table created with RLS
- [ ] `knowledge_embeddings` table created
- [ ] Helper views and functions working

### ✅ n8n Workflows Operational
- [ ] All 4 workflows imported
- [ ] Credentials configured correctly
- [ ] W150 cron enabled and tested
- [ ] Webhook workflows tested

### ✅ GitHub Actions Working
- [ ] All secrets configured
- [ ] Manual run successful
- [ ] Artifacts uploaded correctly
- [ ] Mattermost alerts received

### ✅ Odoo Integration Complete
- [ ] Server actions created for webhooks
- [ ] Test expense triggered OCR workflow
- [ ] Test knowledge page triggered governance

### ✅ Monitoring Active
- [ ] Mattermost channels configured
- [ ] Daily health checks running
- [ ] Supabase dashboard accessible

## Next Steps

**Week 1: Observation**
- Monitor daily health check reports
- Validate all alerts are actionable
- Fine-tune thresholds if needed

**Week 2: Optimization**
- Review Supabase query performance
- Optimize workflow execution times
- Document common issues and fixes

**Week 3: Expansion**
- Add additional validation gates
- Create custom dashboards
- Implement predictive alerting

## Rollback Procedure

If issues arise:

```bash
# Disable n8n workflows
# Via UI: Open workflow → Click "Active" toggle → Disable

# Disable GitHub Actions
# Via UI: Actions → Workflow → Disable workflow

# Remove Odoo server actions
# Settings → Technical → Automation → Server Actions → Archive

# Keep Supabase tables (data is valuable for troubleshooting)
```

## Support

**Documentation:**
- Health Check Guide: `docs/HEALTH_CHECK.md`
- n8n Workflows: `docs/N8N_WORKFLOWS.md` (to be created)
- Project Visibility: `docs/PROJECT_VISIBILITY_TROUBLESHOOTING.md` (to be created)

**Troubleshooting:**
- Check Mattermost #finance-alerts for automated reports
- Review GitHub Actions artifacts for detailed logs
- Query Supabase health_check table for historical data
- SSH to server and run scripts manually with `--verbose`

**Emergency Contact:**
- Jake Tolentino (jgtolentino_rn@yahoo.com)

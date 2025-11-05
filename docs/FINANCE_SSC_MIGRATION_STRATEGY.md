# Finance SSC Migration Strategy

Complete migration plan from standalone Notion workspace to InsightPulse SaaS platform.

## 📋 Executive Summary

### Current State
- **Manual Workflows**: Month-end closing tasks tracked in Notion
- **Scattered Data**: BIR compliance in spreadsheets, Notion, and email
- **No Automation**: Manual reminders, status updates, and reporting
- **Limited Visibility**: No real-time dashboards or consolidated views

### Future State
- **Automated Workflows**: Month-end and BIR filing workflows with auto-sync
- **Centralized Platform**: All finance operations in InsightPulse SaaS
- **Two-Way Sync**: Notion ↔ InsightPulse real-time synchronization
- **Real-Time Dashboards**: Finance SSC oversight across all 8 agencies
- **Audit Trail**: Immutable compliance tracking for BIR requirements

### Migration Timeline: **4 Weeks**
- Week 1: Platform setup + data seeding
- Week 2: Notion integration + workflow import
- Week 3: Testing + parallel run
- Week 4: Cutover + training

---

## 🎯 Phase 1: Platform Setup (Week 1)

### Day 1-2: Database Setup

#### Step 1: Apply SaaS Core Schema
```bash
# Connect to Supabase
export POSTGRES_URL="postgresql://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres"

# Apply migration
psql $POSTGRES_URL -f supabase/migrations/003_saas_core_schema.sql

# Verify tables created
psql $POSTGRES_URL -c "\dt public.*" | grep -E "tenants|projects|workflows"
```

**Expected Output:**
```
✓ 75+ tables created
✓ 13 enum types created
✓ 50+ RLS policies enabled
✓ Seed data inserted (integration types, roles, permissions, plans)
```

#### Step 2: Seed TBWA Finance SSC Data
```bash
# Seed tenant, projects (agencies), users, integrations
psql $POSTGRES_URL -f scripts/seed_agencies.sql
```

**Expected Output:**
```
✅ 1 Tenant: TBWA Finance SSC
✅ 8 Projects: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB (under TBWA tenant)
✅ 2 Admin Users: jgtolentino_rn@yahoo.com, support@insightpulseai.com
✅ 1 Notion Integration: TBWA-wide workspace (not per-agency!)
✅ 1 Billing Account: Single subscription for TBWA
✅ 1 Finance Team: Cross-agency operations
✅ 8 Month-End Workflows: One per project
✅ 1 Consolidated Dashboard: All agencies visible
```

#### Step 3: Create Finance SSC Admin Users
```sql
-- Run this in psql or Supabase SQL Editor

-- Admin User 1: Jake Tolentino
INSERT INTO users (email, full_name, metadata) VALUES
  (
    'jgtolentino_rn@yahoo.com',
    'Jake Tolentino',
    jsonb_build_object(
      'department', 'Finance Shared Service Center',
      'role', 'SSC Admin'
    )
  )
RETURNING id;

-- Admin User 2: InsightPulse Support
INSERT INTO users (email, full_name, metadata) VALUES
  (
    'support@insightpulseai.com',
    'InsightPulse Support',
    jsonb_build_object(
      'department', 'Finance Shared Service Center',
      'role', 'Technical Support'
    )
  )
RETURNING id;

-- Note the returned user IDs
-- ✅ Add both to TBWA tenant (not per-agency!)
INSERT INTO org_memberships (tenant_id, user_id, is_owner, status)
SELECT t.id, '<user_id_from_above>', true, 'active'
FROM tenants t
WHERE t.slug = 'tbwa-finance-ssc';

-- Assign Admin role (single tenant, not 8!)
INSERT INTO user_roles (user_id, tenant_id, role_id)
SELECT
  '<user_id>',
  t.id,
  (SELECT id FROM roles WHERE name = 'Admin' AND scope = 'org')
FROM tenants t
WHERE t.slug = 'tbwa-finance-ssc';
```

### Day 3-4: Configure Integrations

#### Step 1: Set Up Notion Integration

```bash
# 1. Create Notion integration at https://www.notion.so/my-integrations
# 2. Name: "InsightPulse Finance SSC"
# 3. Copy the integration token (starts with secret_...)
```

#### Step 2: Share Notion Databases with Integration
```
✅ Share these TBWA-wide databases with your Notion integration:
- TBWA Finance SSC - Month-End Tasks (includes all 8 agencies)
- TBWA Finance SSC - BIR Filing Schedule (includes all 8 agencies)
- TBWA Finance SSC - Compliance Checklist (includes all 8 agencies)
- TBWA Finance SSC - Team Directory (TBWA-wide)
- TBWA Finance SSC - Agency Calendar (TBWA-wide)

Note: These are SHARED databases, not per-agency databases!
Each database has an "Agency" property to filter data by agency.
```

#### Step 3: Get Notion Database IDs
```bash
# Database IDs are in the URL:
# https://www.notion.so/{database_id}?v=...
# Copy each database ID
```

#### Step 4: Store Integration Secrets
```sql
-- ✅ Store ONE Notion integration token for TBWA tenant (not 8!)
DO $$
DECLARE
  tbwa_tenant_id UUID;
BEGIN
  -- Get TBWA tenant ID
  SELECT id INTO tbwa_tenant_id FROM tenants WHERE slug = 'tbwa-finance-ssc';

  -- Create secret
  INSERT INTO secrets (tenant_id, name, latest_version)
  VALUES (tbwa_tenant_id, 'notion-integration-token', 1);

  -- Store encrypted token
  INSERT INTO secret_versions (secret_id, version, format, ciphertext)
  SELECT
    s.id,
    1,
    'opaque',
    pgp_sym_encrypt('secret_YOUR_NOTION_TOKEN', 'encryption_key_here') -- Replace with actual token
  FROM secrets s
  WHERE s.name = 'notion-integration-token' AND s.tenant_id = tbwa_tenant_id;

  RAISE NOTICE 'Stored Notion integration token for TBWA tenant';
END $$;
```

#### Step 5: Update Integration Config
```sql
-- ✅ Update THE integration (singular!) with actual Notion database IDs
UPDATE integrations
SET config = jsonb_set(
  jsonb_set(
    jsonb_set(
      jsonb_set(
        jsonb_set(
          config,
          '{databases,month_end_tasks}',
          '"YOUR_MONTH_END_DB_ID"'::jsonb
        ),
        '{databases,bir_filing_schedule}',
        '"YOUR_BIR_FILING_DB_ID"'::jsonb
      ),
      '{databases,compliance_checklist}',
      '"YOUR_COMPLIANCE_DB_ID"'::jsonb
    ),
    '{databases,team_directory}',
    '"YOUR_TEAM_DB_ID"'::jsonb
  ),
  '{databases,agency_calendar}',
  '"YOUR_CALENDAR_DB_ID"'::jsonb
)
WHERE tenant_id = (SELECT id FROM tenants WHERE slug = 'tbwa-finance-ssc')
  AND type_id = (SELECT id FROM integration_types WHERE provider = 'notion');
```

### Day 5-7: Deploy Edge Functions

#### Step 1: Install Supabase CLI
```bash
# Install Supabase CLI
npm install -g supabase

# Login to Supabase
supabase login

# Link to project
supabase link --project-ref spdtwktxdalcfigzeqrz
```

#### Step 2: Create Notion Webhook Handler
```typescript
// supabase/functions/notion-webhook/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  const { page_id, properties, database_id } = await req.json()

  // Log webhook event
  const { data: event } = await supabase
    .from('integration_events')
    .insert({
      integration_id: '...', // Look up by database_id
      event_type: 'notion.database.updated',
      payload: { page_id, properties, database_id },
      status: 'queued'
    })
    .select()
    .single()

  // Process event (sync to workflow_runs)
  // ... (see NOTION_INTEGRATION_MAPPING.md for full logic)

  return new Response('OK', { status: 200 })
})
```

#### Step 3: Deploy Edge Functions
```bash
# Deploy Notion webhook handler
supabase functions deploy notion-webhook

# Set environment secrets
supabase secrets set NOTION_TOKEN="secret_YOUR_TOKEN"

# Test function
curl -X POST https://YOUR_PROJECT.supabase.co/functions/v1/notion-webhook \
  -H "Content-Type: application/json" \
  -d '{"page_id": "test", "properties": {}}'
```

---

## 🔄 Phase 2: Notion Integration & Data Migration (Week 2)

### Day 8-9: Initial Data Sync

#### Step 1: Export Existing Notion Data
```bash
# Use Notion API to export all current tasks
# Create a sync script

cat > scripts/notion_initial_sync.py <<EOF
import requests
import psycopg2
from datetime import datetime

# Notion API
NOTION_TOKEN = "secret_YOUR_TOKEN"
DATABASE_ID = "YOUR_DB_ID"

# Fetch all pages from Notion
response = requests.post(
    f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
    headers={
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28"
    }
)

pages = response.json()['results']

# Connect to Supabase
conn = psycopg2.connect("postgresql://...")
cur = conn.cursor()

# For each Notion page, create workflow_run
for page in pages:
    props = page['properties']

    # Map Notion properties to workflow_run
    task_name = props['Task Name']['title'][0]['plain_text']
    status = props['Status']['select']['name']
    owner = props['Owner']['people'][0]['email'] if props['Owner']['people'] else None
    due_date = props['Due Date']['date']['start'] if props['Due Date']['date'] else None

    # Insert workflow_run
    cur.execute("""
        INSERT INTO workflow_runs (workflow_id, status, input, metadata)
        VALUES (
            (SELECT id FROM workflows WHERE name LIKE '%Month-End Closing%' LIMIT 1),
            %s,
            %s,
            %s
        )
    """, (
        map_notion_status(status),
        {"task_name": task_name, "owner": owner, "due_date": due_date},
        {"notion_page_id": page['id'], "synced_from_notion": True}
    ))

conn.commit()
print(f"Synced {len(pages)} tasks from Notion")
EOF

python3 scripts/notion_initial_sync.py
```

#### Step 2: Verify Data Migration
```sql
-- Check migrated tasks
SELECT
  t.name AS agency,
  w.name AS workflow,
  wr.status,
  wr.input->>'task_name' AS task,
  wr.metadata->>'notion_page_id' AS notion_id
FROM workflow_runs wr
JOIN workflows w ON wr.workflow_id = w.id
JOIN tenants t ON w.tenant_id = t.id
WHERE wr.metadata->>'synced_from_notion' = 'true'
ORDER BY t.name, wr.created_at DESC;
```

### Day 10-11: Import Workflow Definitions

#### Step 1: Load Workflow JSON Definitions
```bash
# Load month-end closing workflow
cat workflows/month-end-closing.json | jq .

# Load BIR filing workflow
cat workflows/bir-filing-1601c.json | jq .
```

#### Step 2: Import into Database
```sql
-- Function to import workflow from JSON
CREATE OR REPLACE FUNCTION import_workflow_definition(
  p_tenant_id UUID,
  p_workflow_json JSONB
)
RETURNS UUID AS $$
DECLARE
  v_workflow_id UUID;
BEGIN
  INSERT INTO workflows (tenant_id, name, definition, metadata)
  VALUES (
    p_tenant_id,
    p_workflow_json->>'name',
    p_workflow_json->'steps',
    jsonb_build_object(
      'category', p_workflow_json->>'category',
      'version', p_workflow_json->>'version',
      'trigger_type', p_workflow_json->>'trigger_type',
      'schedule', p_workflow_json->'schedule',
      'metadata', p_workflow_json->'metadata'
    )
  )
  RETURNING id INTO v_workflow_id;

  RETURN v_workflow_id;
END;
$$ LANGUAGE plpgsql;

-- Import month-end closing workflow for each agency
DO $$
DECLARE
  workflow_json JSONB := '... paste month-end-closing.json content ...';
  agency_tenant_id UUID;
  agency_code TEXT;
BEGIN
  FOR agency_code IN SELECT unnest(ARRAY['rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb'])
  LOOP
    SELECT id INTO agency_tenant_id FROM tenants WHERE slug = agency_code;

    PERFORM import_workflow_definition(
      agency_tenant_id,
      workflow_json
    );

    RAISE NOTICE 'Imported month-end workflow for %', agency_code;
  END LOOP;
END $$;

-- Repeat for BIR filing workflow
```

### Day 12-14: Configure Two-Way Sync

#### Step 1: Enable Real-Time Sync (Notion → InsightPulse)
```bash
# Deploy workflow processor Edge Function
supabase functions deploy workflow-processor

# This function runs every 15 minutes to sync Notion updates
# See NOTION_INTEGRATION_MAPPING.md for full implementation
```

#### Step 2: Enable Status Updates (InsightPulse → Notion)
```sql
-- Trigger to update Notion when workflow_run changes
-- (Already created in NOTION_INTEGRATION_MAPPING.md)

-- Test the trigger
UPDATE workflow_runs
SET status = 'success'
WHERE metadata->>'notion_page_id' IS NOT NULL
LIMIT 1;

-- Verify integration_events created
SELECT * FROM integration_events
WHERE event_type = 'sync.to_notion.workflow_run_updated'
ORDER BY created_at DESC
LIMIT 5;
```

---

## 🧪 Phase 3: Testing & Parallel Run (Week 3)

### Day 15-17: End-to-End Testing

#### Test Case 1: Create Task in Notion → Syncs to InsightPulse
```
1. Create a new task in Notion "[RIM] Month-End Tasks"
2. Fill in properties: Task Name, Status, Owner, Due Date
3. Wait 15 minutes (or trigger manual sync)
4. Verify task appears in workflow_runs table
5. Verify task appears in InsightPulse dashboard
```

#### Test Case 2: Update Task in InsightPulse → Syncs to Notion
```
1. Update task status in InsightPulse (via API or UI)
2. Check integration_events table for sync event
3. Verify status updated in Notion
4. Verify "Last Synced" timestamp in Notion
```

#### Test Case 3: Month-End Workflow Execution
```
1. Trigger month-end closing workflow for RIM
2. Verify all steps execute in order
3. Check for Slack notifications
4. Verify dashboard updates
5. Verify audit logs created
```

#### Test Case 4: BIR Filing Workflow
```
1. Trigger BIR 1601-C filing workflow
2. Verify data extraction from Odoo
3. Check alphalist generation
4. Verify approval flow
5. Confirm audit log entry
```

### Day 18-21: Parallel Run

#### Week 3 Parallel Operation
- **Continue using Notion** as primary source of truth
- **Run InsightPulse in parallel** with auto-sync enabled
- **Compare results** daily:
  - Task completion rates
  - Notification accuracy
  - Data consistency

#### Daily Reconciliation Checklist
```sql
-- Compare Notion vs InsightPulse task counts
SELECT
  t.name AS agency,
  COUNT(*) FILTER (WHERE wr.metadata->>'synced_from_notion' = 'true') AS notion_tasks,
  COUNT(*) AS total_tasks,
  COUNT(*) FILTER (WHERE wr.status = 'success') AS completed
FROM workflow_runs wr
JOIN workflows w ON wr.workflow_id = w.id
JOIN tenants t ON w.tenant_id = t.id
WHERE wr.created_at >= date_trunc('week', now())
GROUP BY t.name;
```

---

## 🚀 Phase 4: Cutover & Training (Week 4)

### Day 22-23: Cutover Preparation

#### Pre-Cutover Checklist
- [ ] All 8 agencies' data fully migrated
- [ ] Two-way sync tested and working
- [ ] Dashboards configured and accessible
- [ ] Alerts configured (BIR deadlines, overdue tasks)
- [ ] Edge functions deployed and monitored
- [ ] Backup of Notion data taken
- [ ] Rollback plan documented

#### Cutover Plan (Saturday Morning - Low Activity)
```
06:00 - Stop Notion webhook (pause incoming changes)
06:15 - Final data sync from Notion to InsightPulse
06:30 - Verify data consistency (run reconciliation queries)
07:00 - Enable InsightPulse as primary system
07:15 - Re-enable Notion sync (InsightPulse → Notion for viewing)
08:00 - Monitor for 1 hour
09:00 - Notify team: Cutover complete
```

### Day 24-25: User Training

#### Training Session 1: Finance Team (2 hours)
**Topics:**
1. InsightPulse Dashboard Overview
   - Finance SSC consolidated view
   - Agency-specific drilldowns
   - Task management interface

2. Workflow Management
   - Creating manual workflow instances
   - Monitoring workflow progress
   - Handling workflow failures

3. Notion Integration
   - How two-way sync works
   - When to use Notion vs InsightPulse
   - Troubleshooting sync issues

#### Training Session 2: BIR Compliance Officers (1.5 hours)
**Topics:**
1. BIR Filing Workflows
   - Monthly 1601-C process
   - Quarterly 2550Q process
   - Annual 1702-RT/EX process

2. Approval Flows
   - Reviewing auto-generated forms
   - Approving/rejecting filings
   - Manual corrections

3. Audit Trail
   - Viewing BIR filing history
   - Exporting compliance reports
   - Legal hold for 10-year retention

#### Training Session 3: Management (1 hour)
**Topics:**
1. Executive Dashboards
   - Cross-agency performance
   - Compliance status
   - SLA tracking

2. Alert Management
   - Configuring custom alerts
   - Escalation paths
   - Mobile notifications

3. Reporting
   - Scheduled reports
   - Ad-hoc queries
   - Export functionality

### Day 26-28: Hypercare Period

#### Daily Standups (9 AM)
- Review previous 24h activity
- Address any sync issues
- Monitor system performance
- Gather user feedback

#### Issue Triage
```
Priority 1 (Fix within 1 hour):
- Data sync failures
- BIR filing workflow blocks
- Dashboard outages

Priority 2 (Fix within 4 hours):
- Notification delays
- Report generation errors
- Minor UI issues

Priority 3 (Fix within 1 week):
- Feature requests
- UI/UX improvements
- Documentation updates
```

---

## 📊 Success Metrics

### Week 1 Targets
- [ ] 100% of database schema deployed
- [ ] 8/8 agencies seeded
- [ ] All integrations configured

### Week 2 Targets
- [ ] 100% of historical Notion data migrated
- [ ] Workflow definitions imported
- [ ] Two-way sync enabled

### Week 3 Targets
- [ ] 95%+ sync accuracy (Notion ↔ InsightPulse)
- [ ] 0 critical bugs
- [ ] User acceptance sign-off

### Week 4 Targets
- [ ] 100% team trained
- [ ] Cutover completed
- [ ] No rollback required

### Post-Cutover (30 Days)
- [ ] 90%+ task completion rate maintained
- [ ] 100% BIR filing deadlines met
- [ ] < 5 support tickets/week
- [ ] 80%+ user satisfaction score

---

## 🔄 Rollback Plan

### Trigger Conditions
Rollback if any of:
- > 10% data loss during migration
- Critical sync failures > 4 hours
- BIR filing workflow complete failure
- User adoption < 50% after 1 week

### Rollback Steps (< 2 hours)
```
1. Disable InsightPulse webhooks
2. Re-enable Notion as primary system
3. Export any data created in InsightPulse during migration
4. Manual merge into Notion
5. Notify team
6. Schedule post-mortem
```

---

## 📚 Post-Migration Tasks

### Month 1
- [ ] Fine-tune workflow definitions based on user feedback
- [ ] Optimize dashboard queries for performance
- [ ] Create custom reports for management
- [ ] Document common troubleshooting steps

### Month 2
- [ ] Add additional agencies (if applicable)
- [ ] Implement advanced features (OCR, AI analysis)
- [ ] Integrate with external systems (banks, EFPS)
- [ ] Set up automated backups

### Month 3
- [ ] Review and optimize subscription plan
- [ ] Evaluate usage-based billing
- [ ] Plan for scale (additional users, projects)
- [ ] Conduct security audit

---

## 🆘 Support Contacts

### During Migration (24/7 Support)
- **Technical Issues**: support@insightpulseai.net
- **Notion Sync Issues**: Slack #insightpulse-support
- **Escalation**: Jake Tolentino (jake@insightpulseai.net)

### Post-Migration (Business Hours)
- **General Support**: support@insightpulseai.net
- **Training Requests**: training@insightpulseai.net
- **Feature Requests**: product@insightpulseai.net

---

## ✅ Migration Checklist

### Pre-Migration
- [ ] Database schema reviewed and approved
- [ ] Notion integration credentials obtained
- [ ] Team notified of migration schedule
- [ ] Backup of current Notion workspace created

### Week 1
- [ ] Database deployed
- [ ] Agencies seeded
- [ ] Integrations configured
- [ ] Edge functions deployed

### Week 2
- [ ] Historical data migrated
- [ ] Workflows imported
- [ ] Two-way sync enabled
- [ ] Initial testing completed

### Week 3
- [ ] End-to-end testing passed
- [ ] Parallel run completed
- [ ] Data reconciliation passed
- [ ] User acceptance obtained

### Week 4
- [ ] Cutover executed
- [ ] Team trained
- [ ] Hypercare support active
- [ ] Success metrics met

### Post-Migration
- [ ] Notion kept as read-only backup for 30 days
- [ ] Performance monitored
- [ ] Feedback collected
- [ ] Optimization implemented

---

**Migration Owner**: Finance SSC Technical Lead
**Last Updated**: 2025-11-05
**Document Version**: 1.0

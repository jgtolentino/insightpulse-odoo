# Notion → InsightPulse SaaS Integration Mapping

Complete mapping guide for syncing Notion workspace databases with the InsightPulse SaaS Core Schema.

## 🎯 Multi-Tenant Architecture

**IMPORTANT:** This integration uses a **single Notion workspace** for the entire TBWA Finance SSC tenant:

```
TBWA Finance SSC (1 Tenant)
  └── 1 Notion Integration (tenant-level)
      └── 5 Shared Notion Databases
          ├── Month-End Tasks (all 8 agencies)
          ├── BIR Filing Schedule (all 8 agencies)
          ├── Compliance Checklist (all 8 agencies)
          ├── Team Directory (TBWA-wide)
          └── Agency Calendar (TBWA-wide)
```

**Architecture:**
- ✅ 1 Tenant = TBWA Finance SSC (the customer)
- ✅ 8 Projects = Agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- ✅ 1 Notion Integration = Single workspace for all agencies
- ✅ Shared databases with "Agency" property to filter data

## 📋 Overview

### Integration Architecture

```
Notion Workspace (TBWA Finance SSC)
  ↓ [Webhooks / API Polling]
integration_events (Queue)
  ↓ [Event Processor]
workflows + workflow_runs (InsightPulse)
  ↓ [Status Updates]
Notion Database (Two-way Sync)
```

### Notion Databases → Schema Tables Mapping

| Notion Database | Schema Table(s) | Sync Direction | Update Frequency |
|----------------|-----------------|----------------|------------------|
| Month-End Tasks | `workflows`, `workflow_runs` | Two-way | Real-time |
| BIR Filing Schedule | `workflows`, `audit_logs` | Two-way | Real-time |
| Compliance Checklist | `tickets`, `attachments` | Two-way | 15 minutes |
| Team Directory | `users`, `org_memberships`, `teams` | One-way (Notion → DB) | Daily |
| Agency Calendar | `workflows` (scheduled) | One-way (Notion → DB) | Hourly |

---

## 🔄 1. Month-End Tasks Database

### Notion Database Structure

**Note:** ONE database for ALL agencies (not per-agency databases)

```yaml
Database Name: "TBWA Finance SSC - Month-End Tasks"
Properties:
  - Task Name (Title)
  - Agency (Select: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB) ← Filter by agency
  - Status (Select: Not Started, In Progress, Blocked, Completed)
  - Owner (Person)
  - Due Date (Date)
  - Priority (Select: Low, Medium, High, Critical)
  - Category (Select: Journal Entry, Reconciliation, Reporting, Review, BIR Filing)
  - Period (Formula: Month-Year, e.g., "Nov 2025")
  - Dependencies (Relation → Other tasks)
  - Notes (Rich Text)
  - Attachments (Files)
  - Last Updated (Last Edited Time)
```

### Mapping to Schema

#### Workflow Definition (Created Once per Project, All Under TBWA Tenant)

```sql
INSERT INTO workflows (tenant_id, name, definition)
VALUES (
  '<tbwa_tenant_id>',  -- ✅ All workflows belong to TBWA tenant
  'RIM Agency - Month-End Closing',
  jsonb_build_object(
    'trigger_type', 'scheduled',
    'schedule', 'monthly',
    'notion_source', jsonb_build_object(
      'database_id', 'db-rim-month-end',
      'sync_enabled', true
    ),
    'steps', jsonb_build_array(
      -- Steps defined below
    )
  ),
  jsonb_build_object(
    'category', 'month_end_closing',
    'fiscal_period', '2025-11',
    'agency', 'RIM'
  )
);
```

#### Workflow Run (Created for Each Notion Task)

```sql
-- Sync Notion task → workflow_run
INSERT INTO workflow_runs (workflow_id, status, input, output, metadata, started_at)
SELECT
  w.id AS workflow_id,
  CASE notion_task.status
    WHEN 'Not Started' THEN 'pending'
    WHEN 'In Progress' THEN 'running'
    WHEN 'Blocked' THEN 'failed'
    WHEN 'Completed' THEN 'success'
  END AS status,
  jsonb_build_object(
    'task_name', notion_task.task_name,
    'owner', notion_task.owner,
    'due_date', notion_task.due_date,
    'priority', notion_task.priority,
    'category', notion_task.category
  ) AS input,
  CASE
    WHEN notion_task.status = 'Completed' THEN
      jsonb_build_object(
        'completed_at', notion_task.last_updated,
        'completed_by', notion_task.owner
      )
    ELSE NULL
  END AS output,
  jsonb_build_object(
    'notion_page_id', notion_task.page_id,
    'notion_url', notion_task.url,
    'dependencies', notion_task.dependencies,
    'notes', notion_task.notes,
    'attachments', notion_task.attachments
  ) AS metadata,
  COALESCE(notion_task.started_at, notion_task.created_at) AS started_at
FROM workflows w
CROSS JOIN LATERAL (
  -- This is where Notion API response would be parsed
  SELECT
    '<notion_page_id>' AS page_id,
    'https://notion.so/...' AS url,
    'Journal Entry - Accruals' AS task_name,
    'In Progress' AS status,
    'jane@rim.ph' AS owner,
    '2025-11-05'::date AS due_date,
    'High' AS priority,
    'Journal Entry' AS category,
    '[]'::jsonb AS dependencies,
    'Need to accrue Q4 expenses' AS notes,
    '[]'::jsonb AS attachments,
    now() AS started_at,
    now() AS created_at,
    now() AS last_updated
) notion_task
WHERE w.name = 'RIM Month-End Closing - November 2025';
```

### Two-Way Sync Logic

#### Notion → InsightPulse (Webhook Handler)

```typescript
// supabase/functions/notion-webhook/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

serve(async (req) => {
  const { page_id, properties } = await req.json()

  const supabase = createClient(
    Deno.env.get('SUPABASE_URL')!,
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
  )

  // 1. Log the webhook event
  await supabase.from('integration_events').insert({
    integration_id: '<notion_integration_id>',
    event_type: 'notion.database.updated',
    payload: { page_id, properties },
    status: 'queued'
  })

  // 2. Find or create workflow_run
  const { data: existingRun } = await supabase
    .from('workflow_runs')
    .select('id')
    .eq('metadata->>notion_page_id', page_id)
    .single()

  if (existingRun) {
    // Update existing workflow_run
    await supabase
      .from('workflow_runs')
      .update({
        status: mapNotionStatusToWorkflowStatus(properties.Status.select.name),
        input: {
          task_name: properties['Task Name'].title[0].plain_text,
          owner: properties.Owner.people[0].email,
          due_date: properties['Due Date'].date.start,
          priority: properties.Priority.select.name,
          category: properties.Category.select.name
        },
        metadata: {
          ...existingRun.metadata,
          last_synced_from_notion: new Date().toISOString()
        }
      })
      .eq('id', existingRun.id)
  } else {
    // Create new workflow_run
    // (Insert logic similar to above SQL)
  }

  // 3. Mark event as processed
  await supabase
    .from('integration_events')
    .update({ status: 'processed', processed_at: new Date().toISOString() })
    .eq('payload->>page_id', page_id)

  return new Response('OK', { status: 200 })
})
```

#### InsightPulse → Notion (Status Update)

```sql
-- Trigger function to update Notion when workflow_run changes
CREATE OR REPLACE FUNCTION sync_workflow_run_to_notion()
RETURNS TRIGGER AS $$
DECLARE
  notion_integration_id UUID;
  notion_page_id TEXT;
BEGIN
  -- Extract Notion page ID from metadata
  notion_page_id := NEW.metadata->>'notion_page_id';

  IF notion_page_id IS NOT NULL THEN
    -- Get Notion integration
    SELECT i.id INTO notion_integration_id
    FROM integrations i
    JOIN workflows w ON w.tenant_id = i.tenant_id
    WHERE w.id = NEW.workflow_id
      AND i.type_id = (SELECT id FROM integration_types WHERE provider = 'notion')
    LIMIT 1;

    -- Queue update request to Notion
    INSERT INTO integration_events (integration_id, event_type, payload, status)
    VALUES (
      notion_integration_id,
      'sync.to_notion.workflow_run_updated',
      jsonb_build_object(
        'page_id', notion_page_id,
        'updates', jsonb_build_object(
          'Status', CASE NEW.status
            WHEN 'pending' THEN 'Not Started'
            WHEN 'running' THEN 'In Progress'
            WHEN 'failed' THEN 'Blocked'
            WHEN 'success' THEN 'Completed'
          END,
          'Last Synced', now()
        )
      ),
      'queued'
    );
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER workflow_run_sync_to_notion
  AFTER INSERT OR UPDATE ON workflow_runs
  FOR EACH ROW
  WHEN (NEW.metadata->>'notion_page_id' IS NOT NULL)
  EXECUTE FUNCTION sync_workflow_run_to_notion();
```

---

## 📅 2. BIR Filing Schedule Database

### Notion Database Structure

```yaml
Database Name: "TBWA Finance SSC - BIR Filing Schedule"
Properties:
  - Agency (Select: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB) ← Filter by agency
  - Form Type (Select: 1601-C, 1702-RT, 2550Q, 2550M, ATP)
  - Period (Formula: "2025-Q3" or "2025-11")
  - Filing Deadline (Date)
  - Status (Select: Pending, In Progress, Filed, Late, Exempt)
  - Amount (Number - Currency: PHP)
  - Reference No (Text - BIR confirmation)
  - Filed By (Person)
  - Filed Date (Date)
  - Attachments (Files - PDF copies of returns)
  - Notes (Rich Text)
```

### Mapping to Schema

#### Audit Log Entry (Each BIR Filing)

```sql
-- Create audit log when BIR form is filed
INSERT INTO audit_logs (tenant_id, user_id, action, resource_type, resource_id, metadata, created_at)
SELECT
  t.id AS tenant_id,
  (SELECT id FROM users WHERE email = notion_task.filed_by) AS user_id,
  CASE
    WHEN notion_task.status = 'Filed' THEN 'bir.form_submitted'
    WHEN notion_task.status = 'Late' THEN 'bir.form_submitted_late'
    WHEN notion_task.status = 'Exempt' THEN 'bir.form_exempted'
    ELSE 'bir.form_pending'
  END AS action,
  'tax_form' AS resource_type,
  notion_task.form_type || '-' || notion_task.period AS resource_id,
  jsonb_build_object(
    'form_type', notion_task.form_type,
    'period', notion_task.period,
    'filing_deadline', notion_task.filing_deadline,
    'amount', notion_task.amount,
    'reference_no', notion_task.reference_no,
    'filed_date', notion_task.filed_date,
    'status', notion_task.status,
    'notion_page_id', notion_task.page_id,
    'attachments', notion_task.attachments
  ) AS metadata,
  COALESCE(notion_task.filed_date, now()) AS created_at
FROM tenants t
CROSS JOIN LATERAL (
  -- Notion API response
  SELECT
    '1601-C' AS form_type,
    '2025-11' AS period,
    '2025-12-10'::date AS filing_deadline,
    'Filed' AS status,
    125000.00 AS amount,
    'BIR-2025-11-001' AS reference_no,
    'jane@rim.ph' AS filed_by,
    '2025-12-09'::date AS filed_date,
    '<notion_page_id>' AS page_id,
    '["1601C-Nov2025.pdf"]'::jsonb AS attachments
) notion_task
WHERE t.slug = 'rim';
```

#### Workflow for BIR Filing Reminder

```sql
-- Create workflow for BIR filing reminders
INSERT INTO workflows (tenant_id, name, definition, metadata)
VALUES (
  '<rim_tenant_id>',
  'BIR Filing Reminder - 1601-C Monthly',
  jsonb_build_object(
    'trigger_type', 'scheduled',
    'schedule', '0 9 5 * *', -- 9 AM on 5th of every month (5 days before deadline)
    'steps', jsonb_build_array(
      jsonb_build_object(
        'id', 'check_pending_filings',
        'type', 'query',
        'query', 'SELECT * FROM audit_logs WHERE action = ''bir.form_pending'' AND metadata->>''form_type'' = ''1601-C'' AND metadata->>''filing_deadline''::date - CURRENT_DATE <= 5'
      ),
      jsonb_build_object(
        'id', 'send_slack_reminder',
        'type', 'integration_call',
        'integration', 'slack',
        'action', 'send_message',
        'params', jsonb_build_object(
          'channel', '#finance-ssc-bir',
          'message', '🚨 BIR Form 1601-C due in {{days_remaining}} days. Please review and file.'
        )
      ),
      jsonb_build_object(
        'id', 'update_notion',
        'type', 'integration_call',
        'integration', 'notion',
        'action', 'update_page',
        'params', jsonb_build_object(
          'page_id', '{{notion_page_id}}',
          'properties', jsonb_build_object(
            'Status', 'In Progress',
            'Reminder Sent', 'now()'
          )
        )
      )
    )
  ),
  jsonb_build_object(
    'category', 'bir_compliance',
    'form_type', '1601-C',
    'frequency', 'monthly'
  )
);
```

---

## ✅ 3. Compliance Checklist Database

### Notion Database Structure

```yaml
Database Name: "TBWA Finance SSC - Compliance Checklist"
Properties:
  - Agency (Select: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB) ← Filter by agency
  - Item (Title - e.g., "ATP Validation", "Bank Reconciliation")
  - Type (Select: BIR, Audit, Internal Control, Documentation)
  - Frequency (Select: Daily, Weekly, Monthly, Quarterly, Annual)
  - Assignee (Person)
  - Last Checked (Date)
  - Next Due (Formula: Last Checked + Frequency)
  - Status (Select: Compliant, Non-Compliant, In Review, N/A)
  - Evidence (Files - Screenshots, reports, certificates)
  - Notes (Rich Text)
```

### Mapping to Schema

#### Tickets Table (For Non-Compliant Items)

```sql
-- Create ticket for non-compliant items
INSERT INTO tickets (tenant_id, number, title, state, severity, assignee_id, metadata, created_at)
SELECT
  t.id AS tenant_id,
  'COMP-' || to_char(now(), 'YYYYMMDD') || '-' || lpad(nextval('ticket_number_seq')::text, 4, '0') AS number,
  notion_item.item AS title,
  CASE notion_item.status
    WHEN 'Non-Compliant' THEN 'open'
    WHEN 'In Review' THEN 'in_progress'
    WHEN 'Compliant' THEN 'resolved'
    ELSE 'open'
  END AS state,
  CASE notion_item.type
    WHEN 'BIR' THEN 'critical'
    WHEN 'Audit' THEN 'high'
    ELSE 'medium'
  END AS severity,
  (SELECT id FROM users WHERE email = notion_item.assignee) AS assignee_id,
  jsonb_build_object(
    'compliance_type', notion_item.type,
    'frequency', notion_item.frequency,
    'last_checked', notion_item.last_checked,
    'next_due', notion_item.next_due,
    'notion_page_id', notion_item.page_id,
    'evidence', notion_item.evidence
  ) AS metadata,
  now() AS created_at
FROM tenants t
CROSS JOIN LATERAL (
  SELECT
    'ATP Validation - Missing Signatures' AS item,
    'BIR' AS type,
    'Monthly' AS frequency,
    'jane@rim.ph' AS assignee,
    '2025-10-31'::date AS last_checked,
    '2025-11-30'::date AS next_due,
    'Non-Compliant' AS status,
    '<notion_page_id>' AS page_id,
    '["atp-screenshot.png"]'::jsonb AS evidence
) notion_item
WHERE t.slug = 'rim'
  AND notion_item.status = 'Non-Compliant';
```

#### Attachments Table (Evidence Files)

```sql
-- Store compliance evidence attachments
INSERT INTO attachments (tenant_id, owner_type, owner_id, filename, storage_url, metadata)
SELECT
  t.id AS tenant_id,
  'ticket' AS owner_type,
  ticket.id AS owner_id,
  evidence_file->>'name' AS filename,
  evidence_file->>'url' AS storage_url,
  jsonb_build_object(
    'notion_file_id', evidence_file->>'id',
    'uploaded_at', evidence_file->>'uploaded_at',
    'file_type', 'compliance_evidence'
  ) AS metadata
FROM tickets ticket
JOIN tenants t ON ticket.tenant_id = t.id
CROSS JOIN jsonb_array_elements(ticket.metadata->'evidence') AS evidence_file
WHERE ticket.metadata->>'notion_page_id' IS NOT NULL;
```

---

## 👥 4. Team Directory Database

### Notion Database Structure

```yaml
Database Name: "Finance SSC Team Directory"
Properties:
  - Name (Title)
  - Email (Email)
  - Agency (Select: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
  - Role (Select: Accountant, Tax Specialist, Finance Manager, CFO)
  - Certifications (Multi-select: CPA, RIA, BIR Accredited)
  - Phone (Phone)
  - Start Date (Date)
  - Status (Select: Active, On Leave, Resigned)
```

### Mapping to Schema

#### Users + Org Memberships + Teams

```sql
-- Sync Notion team directory to users table
INSERT INTO users (email, full_name, metadata)
SELECT
  notion_person.email,
  notion_person.name,
  jsonb_build_object(
    'role', notion_person.role,
    'certifications', notion_person.certifications,
    'phone', notion_person.phone,
    'start_date', notion_person.start_date,
    'notion_page_id', notion_person.page_id
  )
FROM (
  -- Notion API response
  SELECT
    'jane.doe@rim.ph' AS email,
    'Jane Doe' AS name,
    'RIM' AS agency,
    'Finance Manager' AS role,
    '["CPA", "BIR Accredited"]'::jsonb AS certifications,
    '+63 917 123 4567' AS phone,
    '2020-01-15'::date AS start_date,
    'Active' AS status,
    '<notion_page_id>' AS page_id
) notion_person
WHERE notion_person.status = 'Active'
ON CONFLICT (email) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  metadata = EXCLUDED.metadata,
  updated_at = now();

-- Add to tenant org_memberships
INSERT INTO org_memberships (tenant_id, user_id, status)
SELECT
  t.id AS tenant_id,
  u.id AS user_id,
  'active' AS status
FROM users u
JOIN tenants t ON t.slug = lower(u.metadata->>'agency')
WHERE u.metadata->>'notion_page_id' IS NOT NULL
ON CONFLICT (tenant_id, user_id) DO NOTHING;

-- Add to team
INSERT INTO team_members (team_id, user_id)
SELECT
  tm.id AS team_id,
  u.id AS user_id
FROM users u
JOIN tenants t ON t.slug = lower(u.metadata->>'agency')
JOIN teams tm ON tm.tenant_id = t.id AND tm.name = 'Finance Team'
WHERE u.metadata->>'notion_page_id' IS NOT NULL
ON CONFLICT (team_id, user_id) DO NOTHING;
```

---

## 📆 5. Agency Calendar Database

### Notion Database Structure

```yaml
Database Name: "Finance SSC Calendar"
Properties:
  - Event (Title - e.g., "Month-End Cutoff", "BIR Filing Day")
  - Date (Date)
  - Type (Select: Deadline, Meeting, Holiday, Training)
  - Agency (Multi-select: RIM, CKVC, BOM, etc.)
  - Description (Rich Text)
  - Recurrence (Select: None, Daily, Weekly, Monthly, Quarterly, Annual)
```

### Mapping to Schema

#### Workflows (Scheduled Events)

```sql
-- Create scheduled workflows from calendar events
INSERT INTO workflows (tenant_id, name, definition, metadata)
SELECT
  t.id AS tenant_id,
  notion_event.event AS name,
  jsonb_build_object(
    'trigger_type', 'scheduled',
    'schedule', CASE notion_event.recurrence
      WHEN 'Daily' THEN '0 9 * * *'
      WHEN 'Weekly' THEN '0 9 * * 1'
      WHEN 'Monthly' THEN '0 9 1 * *'
      WHEN 'Quarterly' THEN '0 9 1 */3 *'
      WHEN 'Annual' THEN '0 9 1 1 *'
      ELSE NULL
    END,
    'steps', jsonb_build_array(
      jsonb_build_object(
        'id', 'send_reminder',
        'type', 'integration_call',
        'integration', 'slack',
        'action', 'send_message',
        'params', jsonb_build_object(
          'channel', '#finance-ssc',
          'message', '📅 Reminder: ' || notion_event.event || ' today'
        )
      )
    )
  ),
  jsonb_build_object(
    'event_type', notion_event.type,
    'event_date', notion_event.date,
    'notion_page_id', notion_event.page_id
  )
FROM tenants t
CROSS JOIN LATERAL (
  SELECT
    'Month-End Cutoff' AS event,
    '2025-11-30'::date AS date,
    'Deadline' AS type,
    '["RIM", "CKVC", "BOM", "JPAL", "JLI", "JAP", "LAS", "RMQB"]'::jsonb AS agency,
    'Monthly' AS recurrence,
    '<notion_page_id>' AS page_id
) notion_event
WHERE t.slug = ANY(ARRAY['rim', 'ckvc', 'bom', 'jpal', 'jli', 'jap', 'las', 'rmqb'])
  AND notion_event.recurrence IS NOT NULL;
```

---

## 🔧 Implementation Guide

### Step 1: Set Up Notion Integration

```bash
# 1. Create Notion integration at https://www.notion.so/my-integrations
# 2. Get the integration token (starts with secret_...)
# 3. Share your databases with the integration
# 4. Get database IDs from the database URLs
```

### Step 2: Store Integration Credentials

```sql
-- ✅ Create ONE Notion integration secret for TBWA tenant (not per-agency!)
INSERT INTO secrets (tenant_id, name, latest_version)
VALUES ('<tbwa_tenant_id>', 'notion-integration-token', 1);

INSERT INTO secret_versions (secret_id, version, format, ciphertext)
SELECT
  s.id,
  1,
  'opaque',
  pgp_sym_encrypt('secret_YOUR_NOTION_INTEGRATION_TOKEN', current_setting('app.settings.encryption_key'))
FROM secrets s
WHERE s.name = 'notion-integration-token'
  AND s.tenant_id = '<tbwa_tenant_id>';
```

### Step 3: Create Notion Database Sync Function

```sql
-- Function to sync Notion database to workflow_runs
CREATE OR REPLACE FUNCTION sync_notion_database_to_workflows(
  p_integration_id UUID,
  p_database_id TEXT,
  p_workflow_id UUID
)
RETURNS INTEGER AS $$
DECLARE
  v_count INTEGER := 0;
  v_notion_page JSONB;
  v_notion_pages JSONB[];
BEGIN
  -- Fetch pages from Notion API (this would be done via HTTP request in practice)
  -- For now, this is a placeholder

  -- Loop through Notion pages and create/update workflow_runs
  FOREACH v_notion_page IN ARRAY v_notion_pages
  LOOP
    -- Upsert workflow_run based on notion_page_id
    INSERT INTO workflow_runs (workflow_id, status, input, metadata)
    VALUES (
      p_workflow_id,
      map_notion_status_to_workflow_status(v_notion_page->'properties'->'Status'),
      v_notion_page->'properties',
      jsonb_build_object('notion_page_id', v_notion_page->>'id')
    )
    ON CONFLICT ((metadata->>'notion_page_id'))
    WHERE metadata->>'notion_page_id' IS NOT NULL
    DO UPDATE SET
      status = EXCLUDED.status,
      input = EXCLUDED.input,
      metadata = workflow_runs.metadata || EXCLUDED.metadata;

    v_count := v_count + 1;
  END LOOP;

  RETURN v_count;
END;
$$ LANGUAGE plpgsql;
```

### Step 4: Set Up Sync Cron Job

```sql
-- Use pg_cron to schedule regular syncs
SELECT cron.schedule(
  'sync-notion-month-end-tasks',
  '*/15 * * * *', -- Every 15 minutes
  $$
    SELECT sync_notion_database_to_workflows(
      integration_id,
      (config->>'database_ids'->>'month_end_tasks')::text,
      w.id
    )
    FROM integrations i
    JOIN workflows w ON w.tenant_id = i.tenant_id
    WHERE i.type_id = (SELECT id FROM integration_types WHERE provider = 'notion')
      AND w.name LIKE '%Month-End%';
  $$
);
```

### Step 5: Set Up Notion Webhooks (Real-time Sync)

```bash
# Deploy Supabase Edge Function
cd supabase/functions
supabase functions deploy notion-webhook

# Configure Notion webhook (via API or manually)
curl -X POST https://api.notion.com/v1/webhooks \
  -H "Authorization: Bearer $NOTION_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://YOUR_PROJECT.supabase.co/functions/v1/notion-webhook",
    "database_id": "YOUR_DATABASE_ID",
    "events": ["database.updated", "page.updated"]
  }'
```

---

## 📊 Property Mapping Reference

### Notion → Schema Field Type Mapping

| Notion Property Type | Schema Column Type | Transformation |
|---------------------|-------------------|----------------|
| Title | TEXT | Direct mapping |
| Rich Text | TEXT | Convert to plain text or store as HTML |
| Number | NUMERIC | Direct mapping |
| Select | TEXT or ENUM | Map select value to enum or text |
| Multi-select | JSONB (array) | Store as JSON array |
| Date | DATE or TIMESTAMPTZ | Parse ISO date string |
| Person | UUID (user_id) | Look up user by email |
| Files | JSONB (array) | Store file URLs, download to attachments table |
| Checkbox | BOOLEAN | Direct mapping |
| URL | TEXT | Direct mapping |
| Email | TEXT | Direct mapping |
| Phone | TEXT | Direct mapping |
| Formula | Depends on result type | Compute on sync or store result |
| Relation | UUID (foreign key) | Map related page ID to related record |
| Rollup | JSONB or NUMERIC | Store computed value |
| Created Time | TIMESTAMPTZ | Parse and store |
| Last Edited Time | TIMESTAMPTZ | Parse and store |

---

## 🚨 Error Handling & Monitoring

### Integration Event Status

```sql
-- Monitor failed sync events
SELECT
  ie.event_type,
  ie.error,
  COUNT(*) AS error_count,
  MAX(ie.received_at) AS last_occurrence
FROM integration_events ie
WHERE ie.status = 'failed'
  AND ie.received_at >= now() - interval '24 hours'
GROUP BY ie.event_type, ie.error
ORDER BY error_count DESC;
```

### Alert on Sync Failures

```sql
-- Create alert for repeated sync failures
INSERT INTO alerts (tenant_id, name, type, condition, enabled)
VALUES (
  '<rim_tenant_id>',
  'Notion Sync Failure Alert',
  'threshold',
  jsonb_build_object(
    'query', 'SELECT COUNT(*) FROM integration_events WHERE status = ''failed'' AND received_at >= now() - interval ''1 hour''',
    'threshold', 5,
    'operator', '>='
  ),
  true
);
```

---

## ✅ Validation Queries

### Check Sync Status

```sql
-- Last successful sync per integration
SELECT
  i.name AS integration,
  t.name AS tenant,
  MAX(ie.processed_at) AS last_successful_sync,
  COUNT(CASE WHEN ie.status = 'failed' THEN 1 END) AS failed_count_24h
FROM integrations i
JOIN tenants t ON i.tenant_id = t.id
LEFT JOIN integration_events ie ON ie.integration_id = i.id
  AND ie.received_at >= now() - interval '24 hours'
WHERE i.type_id = (SELECT id FROM integration_types WHERE provider = 'notion')
GROUP BY i.id, i.name, t.name;
```

### Compare Notion vs Database Counts

```sql
-- Compare task counts (requires Notion API call)
SELECT
  'Notion' AS source,
  COUNT(*) AS task_count
FROM notion_api_pages -- Hypothetical view from Notion API
UNION ALL
SELECT
  'Database' AS source,
  COUNT(*) AS task_count
FROM workflow_runs
WHERE metadata->>'notion_page_id' IS NOT NULL;
```

---

## 🎯 Next Steps

1. **Set up Notion integration credentials** in `secrets` table
2. **Deploy Notion webhook handler** as Supabase Edge Function
3. **Configure database IDs** in `integrations.config`
4. **Run initial sync** to populate `workflow_runs` from Notion
5. **Enable real-time webhooks** for two-way sync
6. **Monitor sync health** via `integration_events` and alerts

---

**Complete mapping achieved for:**
- ✅ Month-End Tasks → `workflows` + `workflow_runs`
- ✅ BIR Filing Schedule → `audit_logs` + `workflows`
- ✅ Compliance Checklist → `tickets` + `attachments`
- ✅ Team Directory → `users` + `org_memberships` + `teams`
- ✅ Agency Calendar → `workflows` (scheduled)

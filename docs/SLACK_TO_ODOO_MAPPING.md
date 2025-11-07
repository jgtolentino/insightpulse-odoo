# Slack ↔ Odoo Integration Mapping

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SLACK WORKSPACE                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  #rim-finance│  │ #ckvc-finance│  │#bir-compliance│              │
│  │  Channels    │  │  Channels    │  │   Channels   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                  │                       │
│         └─────────────────┴──────────────────┘                       │
│                           │                                          │
└───────────────────────────┼──────────────────────────────────────────┘
                            │
                            │ Webhooks / OAuth
                            │
┌───────────────────────────▼──────────────────────────────────────────┐
│                      ODOO ERP (19 CE)                                │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              slack_bridge Module                               │ │
│  │  ┌──────────────────┐  ┌──────────────────┐                   │ │
│  │  │ Webhook Receiver │  │ Message Sender   │                   │ │
│  │  │ /slack/events    │  │ Slack API Client │                   │ │
│  │  └────────┬─────────┘  └────────┬─────────┘                   │ │
│  │           │                     │                              │ │
│  │           └──────────┬──────────┘                              │ │
│  │                      │                                         │ │
│  │           ┌──────────▼──────────┐                              │ │
│  │           │  slack.channel      │                              │ │
│  │           │  (Mapping Table)    │                              │ │
│  │           └──────────┬──────────┘                              │ │
│  └────────────────────┬─┴──────────────────────────────────────┬──┘ │
│                       │                                        │    │
│  ┌────────────────────▼──────────────┐  ┌────────────────────▼────┐ │
│  │     Odoo Discuss (mail.channel)   │  │   ipai_agent            │ │
│  │     - Channels                    │  │   - AI Processing       │ │
│  │     - Messages                    │  │   - Context Awareness   │ │
│  │     - Threads                     │  │   - Action Execution    │ │
│  └───────────────────┬───────────────┘  └────────────────────────┘ │
│                      │                                              │
└──────────────────────┼──────────────────────────────────────────────┘
                       │
                       │ Real-time sync via pg_net
                       │
┌──────────────────────▼───────────────────────────────────────────────┐
│                     SUPABASE (PostgreSQL)                            │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ slack_workspaces │  │  slack_channels  │  │  integrations    │  │
│  │ - team_id        │  │  - channel_id    │  │  - config        │  │
│  │ - team_name      │  │  - name          │  │  - secrets       │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
│  pg_net triggers → Webhook notifications to external systems         │
└───────────────────────────────────────────────────────────────────────┘
```

---

## Concept Mapping

### Slack → Odoo

| Slack Concept | Odoo Equivalent | Supabase Table | Notes |
|---------------|-----------------|----------------|-------|
| **Workspace** | Company/Database | `slack_workspaces` | One workspace per Odoo instance |
| **Channel** | `mail.channel` | `slack_channels` + `slack.channel` (Odoo) | Bidirectional sync |
| **User** | `res.users` | `users` | Linked via email/OAuth |
| **Message** | `mail.message` | N/A (transient) | Posted to chatter |
| **Thread** | Message threading (`parent_id`) | N/A | Odoo native threading |
| **Reaction** | `mail.message` reactions | N/A | Odoo 19 feature |
| **File/Attachment** | `ir.attachment` | `attachments` | Linked to messages |
| **App Mention** | `@ipai-bot` mention | N/A | Triggers AI agent |
| **Slash Command** | Controller route | N/A | `/odoo`, `/expense`, `/bir` |
| **Bot User** | System user (`user_agent_bot`) | N/A | Posts automated responses |
| **OAuth Token** | System Parameter | `integration_secrets` | Encrypted storage |
| **Webhook** | Odoo controller | `webhooks` + `webhook_deliveries` | Event subscriptions |

---

## Data Flow

### 1. Slack → Odoo (Inbound)

```
┌─────────────┐
│   Slack     │ User posts message in #rim-finance
│   Channel   │ "@InsightPulse Odoo show me SO001"
└──────┬──────┘
       │
       │ POST /slack/events (webhook)
       │ Headers: X-Slack-Signature, X-Slack-Request-Timestamp
       │ Body: {type: "event_callback", event: {...}}
       │
┌──────▼──────┐
│   Odoo      │ 1. Verify HMAC signature
│ /slack/     │ 2. Check timestamp (< 5 min)
│  events     │ 3. Extract event data
└──────┬──────┘
       │
       │ 4. Lookup channel mapping
       │    SELECT * FROM slack.channel WHERE channel_id = 'C123'
       │
┌──────▼──────────┐
│ slack.channel   │ Returns: agency_code='RIM', channel_type='finance'
│ (Mapping Table) │
└──────┬──────────┘
       │
       │ 5. Check if @ipai-bot mentioned
       │
┌──────▼────────┐
│  ipai_agent   │ 6. Extract query: "show me SO001"
│  (AI Agent)   │ 7. Build context: user, agency, permissions
│               │ 8. Execute: Search sale.order for SO001
│               │ 9. Format response
└──────┬────────┘
       │
       │ 10. Post response to Slack
       │     POST https://slack.com/api/chat.postMessage
       │     Headers: Authorization: Bearer xoxb-...
       │     Body: {channel: "C123", text: "...", thread_ts: "..."}
       │
┌──────▼──────┐
│   Slack     │ User sees response in thread
│   Channel   │
└─────────────┘
```

### 2. Odoo → Slack (Outbound)

```
┌─────────────┐
│   Odoo      │ Expense approved in Odoo
│   Expense   │ self.env['slack.bridge'].post_expense_notification(...)
└──────┬──────┘
       │
       │ 1. Get agency from expense
       │    agency = expense.employee_id.agency_id.code  # 'RIM'
       │
┌──────▼──────────┐
│ slack.channel   │ 2. Lookup channel
│ (Mapping Table) │    channel_id = get_channel_for_agency('RIM', 'finance')
└──────┬──────────┘
       │
       │ 3. Format message with blocks/attachments
       │
┌──────▼────────┐
│ slack.bridge  │ 4. Send to Slack API
│ .post_message │    POST https://slack.com/api/chat.postMessage
│               │    Body: {
│               │      channel: "C123",
│               │      text: "✅ Expense EXP-001 approved",
│               │      blocks: [{...}]
│               │    }
└──────┬────────┘
       │
       │ 5. Log delivery
       │    INSERT INTO webhook_deliveries (...)
       │
┌──────▼──────┐
│  Supabase   │ 6. Store delivery record
│  webhook_   │    status='delivered', response_code=200
│  deliveries │
└──────┬──────┘
       │
       │ 7. (Optional) Trigger pg_net webhook
       │    Notify external dashboard of delivery
       │
┌──────▼──────┐
│   Slack     │ User sees notification in #rim-finance
│   Channel   │
└─────────────┘
```

---

## Database Schema Mapping

### Supabase ↔ Odoo

#### 1. Workspaces

**Supabase:**
```sql
CREATE TABLE slack_workspaces (
  id UUID PRIMARY KEY,
  integration_id UUID REFERENCES integrations(id),
  team_id TEXT NOT NULL,          -- Slack workspace ID (T01234567)
  team_name TEXT,                 -- "InsightPulse Finance SSC"
  UNIQUE (integration_id, team_id)
);
```

**Odoo:**
```python
# Stored in System Parameters
slack.team_id = 'T01234567'
slack.team_name = 'InsightPulse Finance SSC'
```

---

#### 2. Channels

**Supabase:**
```sql
CREATE TABLE slack_channels (
  id UUID PRIMARY KEY,
  workspace_id UUID REFERENCES slack_workspaces(id),
  channel_id TEXT NOT NULL,       -- C01234567
  name TEXT,                      -- 'rim-finance'
  is_private BOOLEAN,
  UNIQUE (workspace_id, channel_id)
);
```

**Odoo:**
```python
class SlackChannel(models.Model):
    _name = "slack.channel"

    channel_id = fields.Char()      # C01234567 (matches Supabase)
    channel_name = fields.Char()    # #rim-finance
    agency_code = fields.Selection([
        ('RIM', 'RIM'),
        ('CKVC', 'CKVC'),
        # ... other agencies
    ])
    channel_type = fields.Selection([
        ('general', 'General'),
        ('finance', 'Finance'),
        ('sales', 'Sales'),
        ('expense', 'Expense'),
        ('bir', 'BIR Compliance'),
        ('support', 'Support'),
    ])
    auto_respond = fields.Boolean()
```

**Sync Logic:**
```python
# When Slack channel is added in Odoo, sync to Supabase
def create(self, vals):
    channel = super().create(vals)
    # Sync to Supabase
    self.env['supabase.sync'].sync_slack_channel(channel)
    return channel
```

---

#### 3. Integrations

**Supabase:**
```sql
CREATE TABLE integrations (
  id UUID PRIMARY KEY,
  tenant_id UUID REFERENCES tenants(id),
  type_id UUID REFERENCES integration_types(id),  -- provider='slack'
  name TEXT,                                      -- 'Slack Workspace'
  config JSONB,                                   -- {webhook_url, oauth_redirect, ...}
  enabled BOOLEAN
);

CREATE TABLE integration_secrets (
  id UUID PRIMARY KEY,
  integration_id UUID REFERENCES integrations(id),
  format secret_format,           -- 'opaque'
  ciphertext BYTEA                -- Encrypted bot token
);
```

**Odoo:**
```python
# System Parameters
slack.bot_token = 'xoxb-...'          # OAuth Bot Token
slack.signing_secret = '...'           # For webhook verification
slack.app_id = 'A01234567'
slack.client_id = '...'
slack.client_secret = '...'
```

**Security:**
- Odoo: Stored in `ir.config_parameter` (encrypted at rest by database)
- Supabase: Stored in `integration_secrets.ciphertext` (PGP encrypted)

---

## Integration Patterns

### Pattern 1: Event Subscriptions (Slack → Odoo)

**Slack Configuration:**
```
Event Subscriptions URL: https://erp.insightpulseai.net/slack/events

Subscribed Events:
- app_mention
- message.channels
```

**Odoo Controller:**
```python
@http.route('/slack/events', type='json', auth='public', csrf=False)
def slack_events(self, **kwargs):
    # 1. Verify signature
    slack_signature = request.httprequest.headers.get('X-Slack-Signature')
    timestamp = request.httprequest.headers.get('X-Slack-Request-Timestamp')
    if not self._verify_slack_signature(slack_signature, timestamp):
        return {'error': 'Invalid signature'}, 403

    # 2. Handle URL verification
    if kwargs.get('type') == 'url_verification':
        return {'challenge': kwargs['challenge']}

    # 3. Process event
    event = kwargs.get('event', {})
    if event.get('type') == 'app_mention':
        self._handle_app_mention(event)
    elif event.get('type') == 'message':
        self._handle_message(event)

    return {'status': 'ok'}
```

**pg_net Webhook (Supabase → External):**
```sql
-- Triggered when Slack event is processed
CREATE OR REPLACE FUNCTION notify_slack_event_processed()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM net.http_post(
    url := 'https://analytics.insightpulseai.net/slack/event',
    headers := jsonb_build_object('Content-Type', 'application/json'),
    body := jsonb_build_object(
      'event_type', NEW.event_type,
      'channel', NEW.channel_id,
      'user', NEW.user_id,
      'timestamp', NEW.created_at
    )
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

---

### Pattern 2: Slash Commands

**Slack Configuration:**
```
Command: /odoo
Request URL: https://erp.insightpulseai.net/slack/command
Short Description: Odoo queries and automation
Usage Hint: help, ping, so [number]
```

**Odoo Controller:**
```python
@http.route('/slack/command', type='http', auth='public', csrf=False, methods=['POST'])
def slack_command(self, **kwargs):
    # Verify signature
    if not self._verify_slack_signature():
        return Response('Unauthorized', status=403)

    # Parse command
    command = kwargs.get('command')      # '/odoo'
    text = kwargs.get('text', '')        # 'so SO001'
    channel_id = kwargs.get('channel_id')
    user_id = kwargs.get('user_id')

    # Route to handler
    if command == '/odoo':
        response = self._handle_odoo_command(text, channel_id, user_id)
    elif command == '/expense':
        response = self._handle_expense_command(text, channel_id, user_id)
    elif command == '/bir':
        response = self._handle_bir_command(text, channel_id, user_id)

    # Return formatted response
    return Response(json.dumps(response), content_type='application/json')
```

**Example: `/odoo so SO001`**
```python
def _handle_odoo_command(self, text, channel_id, user_id):
    parts = text.split()

    if parts[0] == 'so' and len(parts) > 1:
        so_name = parts[1]
        # Search sale order
        so = request.env['sale.order'].sudo().search([('name', '=', so_name)], limit=1)

        if so:
            return {
                'response_type': 'in_channel',
                'blocks': [
                    {
                        'type': 'section',
                        'text': {
                            'type': 'mrkdwn',
                            'text': f'*Sale Order: {so.name}*\n' +
                                   f'• Customer: {so.partner_id.name}\n' +
                                   f'• Amount: ₱{so.amount_total:,.2f}\n' +
                                   f'• Status: {so.state}'
                        }
                    }
                ]
            }
        else:
            return {'text': f'❌ Sale order {so_name} not found'}
```

---

### Pattern 3: Automated Notifications (Odoo → Slack)

**Expense Approval Notification:**

```python
# In hr_expense/models/hr_expense.py
class HrExpense(models.Model):
    _inherit = 'hr.expense'

    def action_approve(self):
        res = super().action_approve()
        # Send Slack notification
        self.env['slack.bridge'].post_expense_notification(
            expense_id=self.id,
            action='approved'
        )
        return res
```

**Slack Bridge Implementation:**
```python
# In slack_bridge/models/slack_bridge.py
def post_expense_notification(self, expense_id, action):
    expense = self.env['hr.expense'].browse(expense_id)

    # Get agency
    agency = expense.employee_id.agency_id.code

    # Get Slack channel
    channel_id = self.env['slack.channel'].get_channel_for_agency(
        agency_code=agency,
        channel_type='expense'
    )

    if not channel_id:
        return

    # Format message
    emoji = {
        'approved': '✅',
        'rejected': '❌',
        'submitted': '📝',
        'paid': '💰'
    }.get(action, '📌')

    blocks = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': f'{emoji} *Expense {action.upper()}*\n' +
                       f'• *Number:* {expense.name}\n' +
                       f'• *Employee:* {expense.employee_id.name}\n' +
                       f'• *Amount:* ₱{expense.total_amount:,.2f}\n' +
                       f'• *Description:* {expense.name}'
            }
        }
    ]

    # Post to Slack
    self.post_message(channel_id, f'Expense {action}', blocks=blocks)
```

**Supabase Webhook Logging:**
```sql
-- Log all Slack API calls for analytics
CREATE TRIGGER on_slack_message_sent
  AFTER INSERT ON webhook_deliveries
  FOR EACH ROW
  WHEN (NEW.event LIKE 'slack.%')
  EXECUTE FUNCTION log_slack_message_metrics();
```

---

## Channel Mappings

### Finance SSC Agency Channels

| Agency | Slack Channel | Channel ID | Odoo Mapping | Type |
|--------|---------------|------------|--------------|------|
| **RIM** | `#rim-finance` | `C_RIM_FIN` | `slack.channel` record | finance |
| **CKVC** | `#ckvc-finance` | `C_CKVC_FIN` | `slack.channel` record | finance |
| **BOM** | `#bom-finance` | `C_BOM_FIN` | `slack.channel` record | finance |
| **JPAL** | `#jpal-finance` | `C_JPAL_FIN` | `slack.channel` record | finance |
| **JLI** | `#jli-finance` | `C_JLI_FIN` | `slack.channel` record | finance |
| **JAP** | `#jap-finance` | `C_JAP_FIN` | `slack.channel` record | finance |
| **LAS** | `#las-finance` | `C_LAS_FIN` | `slack.channel` record | finance |
| **RMQB** | `#rmqb-finance` | `C_RMQB_FIN` | `slack.channel` record | finance |

### Cross-Agency Channels

| Purpose | Slack Channel | Channel ID | Type |
|---------|---------------|------------|------|
| **BIR Compliance** | `#bir-compliance` | `C_BIR_COMP` | bir |
| **Finance General** | `#finance-general` | `C_FIN_GEN` | finance |
| **Expense Approvals** | `#expense-approvals` | `C_EXP_APPR` | expense |
| **Sales** | `#sales` | `C_SALES` | sales |
| **Support** | `#support` | `C_SUPPORT` | support |

---

## Use Cases

### Use Case 1: Expense Approval Workflow

**Scenario:** Finance manager approves expense in Odoo

**Flow:**
1. Manager clicks "Approve" on expense EXP-001 in Odoo
2. Odoo triggers `action_approve()`
3. `slack_bridge.post_expense_notification()` called
4. Lookup agency: Employee → Agency → Channel mapping
5. Format Slack message with blocks
6. POST to Slack API: `chat.postMessage`
7. Log delivery in Supabase `webhook_deliveries`
8. Team sees notification in `#rim-finance`

**Notification Example:**
```
✅ EXPENSE APPROVED
• Number: EXP-001
• Employee: Juan Dela Cruz
• Amount: ₱12,500.00
• Description: Travel to Manila for client meeting
```

---

### Use Case 2: AI Agent Query via Slack

**Scenario:** User asks AI agent about sale order

**Flow:**
1. User posts in `#rim-finance`: `@InsightPulse Odoo what is status of SO001?`
2. Slack sends webhook to Odoo `/slack/events`
3. Odoo verifies signature, extracts event
4. Detects `@InsightPulse Odoo` mention
5. Routes to `ipai_agent` with context:
   - User: john.doe@rim.com
   - Agency: RIM
   - Channel: #rim-finance
   - Permissions: {can_approve_expenses: false, ...}
6. Agent processes query:
   - Parse intent: "status of SO001"
   - Search: `sale.order` where `name = 'SO001'`
   - Format response
7. Post threaded reply to Slack
8. Log interaction in `ipai.agent.log`

**Agent Response:**
```
📊 Sale Order SO001

• Customer: ABC Corporation
• Amount: ₱125,000.00
• Status: Sale Order (confirmed)
• Delivery: Pending
• Invoice: Not created

Next actions:
- Validate delivery
- Create invoice
```

---

### Use Case 3: BIR Deadline Reminder (Automated)

**Scenario:** pg_cron triggers quarterly BIR reminder

**Flow:**
1. **pg_cron** executes at 9 AM on 1st of Jan/Apr/Jul/Oct:
   ```sql
   SELECT cron.schedule(
     'bir-quarterly-report-reminder',
     '0 9 1 1,4,7,10 *',
     $$
     INSERT INTO tickets (tenant_id, number, title, severity, ...)
     SELECT ... FROM tenants WHERE slug IN ('rim', 'ckvc', ...);
     $$
   );
   ```

2. **Ticket Created** → Triggers Odoo notification via webhook
3. **Odoo** receives webhook from Supabase
4. **slack_bridge** posts to `#bir-compliance`:
   ```
   🚨 BIR 2550Q Quarterly VAT Report Due

   • Quarter: Q4 2024
   • Deadline: 2025-01-25
   • Days Remaining: 25

   Action Required:
   ☐ Prepare VAT summary
   ☐ Review input/output VAT
   ☐ File electronically via eBIR
   ```

5. **Supabase** logs delivery in `webhook_deliveries`

---

### Use Case 4: Slash Command for Quick Lookup

**Scenario:** User needs expense status quickly

**Flow:**
1. User types in Slack: `/expense status EXP-001`
2. Slack POSTs to Odoo `/slack/command`
3. Odoo controller:
   - Verifies signature
   - Parses: `command='/expense'`, `text='status EXP-001'`
   - Searches `hr.expense` for `name = 'EXP-001'`
   - Formats response with blocks
4. Returns JSON response immediately (< 3 seconds)
5. Slack displays inline response

**Response:**
```
📝 Expense EXP-001

• Employee: Maria Santos
• Amount: ₱8,500.00
• Category: Meals & Entertainment
• Status: Pending Approval
• Manager: Jose Reyes
• Submitted: 2025-11-05

/expense approve EXP-001 to approve
```

---

## Security & Authentication

### 1. Webhook Signature Verification

**Slack → Odoo:**
```python
def _verify_slack_signature(self, slack_signature, timestamp):
    # Get signing secret from config
    signing_secret = request.env['ir.config_parameter'].sudo().get_param('slack.signing_secret')

    # Check timestamp (prevent replay attacks)
    if abs(time.time() - int(timestamp)) > 300:  # 5 minutes
        return False

    # Compute signature
    sig_basestring = f'v0:{timestamp}:{request.httprequest.data.decode()}'
    my_signature = 'v0=' + hmac.new(
        signing_secret.encode(),
        sig_basestring.encode(),
        hashlib.sha256
    ).hexdigest()

    # Compare signatures
    return hmac.compare_digest(my_signature, slack_signature)
```

### 2. OAuth Token Storage

**Odoo:**
```python
# System Parameters (encrypted at rest by PostgreSQL)
self.env['ir.config_parameter'].sudo().set_param(
    'slack.bot_token',
    'xoxb-1234567890-...'
)
```

**Supabase:**
```sql
-- Encrypted with pgcrypto
INSERT INTO integration_secrets (integration_id, format, ciphertext)
VALUES (
  integration_id,
  'opaque',
  pgp_sym_encrypt('xoxb-1234567890-...', current_setting('app.encryption_key'))
);
```

### 3. Rate Limiting

**Odoo:**
```python
# In slack_bridge controller
@http.route('/slack/events', ...)
def slack_events(self, **kwargs):
    # Check rate limit (max 100 requests/minute)
    if self._is_rate_limited(request.httprequest.remote_addr):
        return {'error': 'Rate limit exceeded'}, 429
    # ...
```

**Supabase:**
```sql
-- pg_net rate limiting
SELECT check_webhook_rate_limit(webhook_id);
```

---

## Implementation Checklist

### Phase 1: Basic Integration ✅
- [x] Install `slack_bridge` module in Odoo
- [x] Create Slack App
- [x] Configure OAuth scopes
- [x] Set up event subscriptions
- [x] Add slash commands
- [x] Store bot token in Odoo
- [x] Test webhook connectivity

### Phase 2: Channel Mappings ✅
- [x] Create `slack.channel` records for all 8 agencies
- [x] Map finance channels per agency
- [x] Set up BIR compliance channel
- [x] Configure auto-respond settings
- [x] Test channel lookup logic

### Phase 3: Automated Notifications 🔄
- [ ] Expense approval notifications
- [ ] Sale order notifications
- [ ] BIR deadline reminders
- [ ] Invoice notifications
- [ ] Payment notifications

### Phase 4: AI Agent Integration 🔄
- [ ] Enable `ipai_agent` module
- [ ] Configure @ipai-bot mention detection
- [ ] Build permission context
- [ ] Test agency-specific queries
- [ ] Log all agent interactions

### Phase 5: Supabase Sync 📋
- [ ] Sync `slack_channels` to Supabase
- [ ] Set up pg_net webhooks
- [ ] Configure webhook delivery logging
- [ ] Create monitoring dashboards
- [ ] Test end-to-end data flow

### Phase 6: Advanced Features 📋
- [ ] Interactive message buttons
- [ ] File upload handling
- [ ] Thread management
- [ ] User provisioning (SCIM)
- [ ] Analytics dashboards

---

## Monitoring & Analytics

### Supabase Monitoring Views

**Slack Message Volume:**
```sql
CREATE VIEW vw_slack_message_volume AS
SELECT
  DATE_TRUNC('hour', attempted_at) AS hour,
  COUNT(*) AS message_count,
  COUNT(*) FILTER (WHERE status = 'delivered') AS delivered,
  COUNT(*) FILTER (WHERE status = 'failed') AS failed,
  ROUND(AVG(response_ms)) AS avg_response_ms
FROM webhook_deliveries
WHERE event LIKE 'slack.%'
  AND attempted_at > NOW() - INTERVAL '7 days'
GROUP BY DATE_TRUNC('hour', attempted_at)
ORDER BY hour DESC;
```

**Agency Activity:**
```sql
CREATE VIEW vw_slack_agency_activity AS
SELECT
  sc.agency_code,
  sc.channel_name,
  COUNT(wd.id) AS notification_count,
  MAX(wd.attempted_at) AS last_notification
FROM slack_channels sc
LEFT JOIN webhook_deliveries wd ON wd.payload->>'channel' = sc.channel_id
WHERE wd.attempted_at > NOW() - INTERVAL '30 days'
GROUP BY sc.agency_code, sc.channel_name
ORDER BY notification_count DESC;
```

### Superset Dashboard

Create dashboard at: `https://superset.insightpulseai.net/slack-metrics`

**Metrics:**
1. Messages sent (last 7 days)
2. Response time trends
3. Agency activity breakdown
4. Error rate by channel
5. AI agent usage statistics

---

## Troubleshooting

### Issue: Slack events not received

**Check:**
1. Nginx logs: `tail -f /var/log/nginx/access.log | grep slack`
2. Verify Request URL in Slack app settings
3. Test signature verification
4. Check firewall rules

**Solution:**
```bash
# Test webhook endpoint
curl -X POST https://erp.insightpulseai.net/slack/events \
  -H "Content-Type: application/json" \
  -d '{"type": "url_verification", "challenge": "test123"}'
```

### Issue: Messages not posting to Slack

**Check:**
1. Bot token valid: `slack.bot_token` in System Parameters
2. Bot invited to channel: `/invite @InsightPulse Odoo`
3. OAuth scopes include `chat:write`
4. Channel ID correct in mapping

**Solution:**
```python
# Test message posting
self.env['slack.bridge'].post_message(
    channel='C01234567',
    text='🧪 Test message'
)
```

### Issue: Signature verification failed

**Check:**
1. Signing secret matches Slack app
2. System time synchronized (NTP)
3. No proxy/CDN modifying headers
4. Request timestamp within 5 minutes

---

## Next Steps

1. **Review channel mappings**: Verify all 8 agencies have correct channel IDs
2. **Test notifications**: Approve test expense, verify Slack notification
3. **Enable AI agent**: Install `ipai_agent`, test @mentions
4. **Set up monitoring**: Create Superset dashboard for Slack metrics
5. **Customize workflows**: Add more notification types (invoices, payments, etc.)
6. **User training**: Document slash commands, share with team

---

## Resources

- **Slack API Documentation**: https://api.slack.com/
- **Slack App Management**: https://api.slack.com/apps
- **Odoo Module**: `/addons/slack_bridge`
- **Quick Start**: `docs/SLACK_QUICK_START.md`
- **Migration Guide**: `docs/SLACK_ENTERPRISE_MIGRATION.md`
- **Supabase Schema**: `supabase/migrations/003_saas_core_schema.sql`
- **Webhook Triggers**: `supabase/webhook_triggers.sql`

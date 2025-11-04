# Four Automation Modes Architecture

**System:** InsightPulse-Odoo Automation Platform
**AI Backend:** Claude 3.5 Sonnet via DigitalOcean Agent Platform
**Status:** Production-Ready (90% complete)

---

## Overview

InsightPulse provides **four distinct interfaces** for automation, all powered by the same Claude 3.5 Sonnet AI backend for consistent natural language understanding.

```
┌─────────────────────────────────────────────────────────────┐
│         Mode 1: Odoo Discuss (@ipai-bot)                    │
│  Internal team automation via Discuss channels              │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────────────┐
│         Mode 2: Pulse Hub Web UI                            │
│  Visual interface with one-click deployment buttons         │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────────────┐
│         Mode 3: AI Agent API                                │
│  Direct HTTP API for programmatic access                    │
└─────────────────┬───────────────────────────────────────────┘
                  │
┌─────────────────┴───────────────────────────────────────────┐
│         Mode 4: GitHub PR Bot (@claude)                     │
│  Code review automation via PR comments                     │
└─────────────────────────────────────────────────────────────┘
                  │
                  ▼
    ┌───────────────────────────────┐
    │  Claude 3.5 Sonnet AI Engine  │
    │  (DigitalOcean Agent Platform)│
    └───────────────────────────────┘
                  │
    ┌─────────────┴────────────────┐
    │     Tool Selection           │
    ├──────────────────────────────┤
    │ • DigitalOcean CLI (doctl)   │
    │ • Supabase RPC               │
    │ • GitHub API                 │
    │ • Odoo XML-RPC               │
    │ • OCR Services               │
    │ • Database Operations        │
    └──────────────────────────────┘
```

---

## Mode 1: Odoo Discuss (@ipai-bot)

### Target Users
- Finance SSC staff
- Operations managers
- IT administrators
- Multi-agency employees

### Access Method
1. Login to Odoo: https://erp.insightpulseai.net
2. Open Discuss app
3. Navigate to pre-configured channels (AI Agent Support, RIM - Finance, etc.)
4. Type `@ipai-bot` followed by natural language request

### Implementation
**Addon:** `ipai_agent` (custom Odoo 19 module)
**Pattern:** Message interception via `mail.channel` inheritance

```python
# models/mail_channel.py
class MailChannel(models.Model):
    _inherit = 'mail.channel'

    @api.model
    def message_post(self, **kwargs):
        result = super().message_post(**kwargs)

        body = kwargs.get('body', '')
        if '@ipai-bot' in body:
            self._handle_bot_mention(body, kwargs)

        return result

    def _handle_bot_mention(self, body, kwargs):
        # Extract request
        request_text = self._extract_bot_request(body)

        # Call AI agent
        response = self.env['ipai.agent.api'].send_request(
            message=request_text,
            user_id=kwargs.get('author_id'),
            context={'channel_id': self.id}
        )

        # Post response
        self.message_post(
            body=f"<p>{response}</p>",
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            author_id=self.env.ref('ipai_agent.ipai_bot_user').id
        )
```

### Pre-Configured Channels

```xml
<!-- data/channels.xml -->
<record id="channel_ai_support" model="mail.channel">
    <field name="name">AI Agent Support</field>
    <field name="description">General AI automation assistance</field>
</record>

<record id="channel_rim_finance" model="mail.channel">
    <field name="name">RIM - Finance</field>
    <field name="description">RIM agency financial operations</field>
</record>

<!-- 7 more channels for CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB -->
```

### Example Interactions

**Deployment:**
```
User: @ipai-bot Deploy ade-ocr to production with force rebuild
Bot: ✅ Starting deployment...
     App: ade-ocr-backend (b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9)
     Region: Singapore (sgp)
     Status: Building...
     [5 minutes later]
     ✅ Deployment complete! Health check passed.
     URL: https://ade-ocr-backend-d9dru.ondigitalocean.app
```

**BIR Form Generation:**
```
User: @ipai-bot Generate 1601-C form for CKVC for October 2024
Bot: 📄 Generating BIR Form 1601-C...
     Agency: CKVC (Company ID: 2)
     Period: October 2024
     ✅ Form generated and saved to Documents/BIR_Forms/
     Total tax: ₱45,230.00
     Filing deadline: November 10, 2024
```

**Expense Approval:**
```
User: @ipai-bot Approve all RIM expenses under $500 this week
Bot: 🔍 Searching expenses...
     Found 12 RIM expenses < $500 from Nov 1-7
     ✅ Approved 12 expenses
     Total: $3,245.50
     Rejected: 0
```

### Unique Capabilities

**Multi-Agency Context Awareness:**
- Automatically detects which agency based on channel name
- Filters data and permissions by company_id
- Handles cross-agency operations (consolidation, transfers)

**Infrastructure Automation:**
- Deploy DigitalOcean apps
- Run Supabase RPC functions
- Trigger GitHub Actions workflows
- Execute OCR batch processing

**Financial Operations:**
- BIR form generation (1601-C, 2550Q, 1702-RT)
- Expense approval workflows
- Month-end closing automation
- Multi-agency consolidation

---

## Mode 2: Pulse Hub Web UI

### Target Users
- Non-technical managers
- External stakeholders (view-only)
- Quick status checks
- Visual configuration

### Access Method
**URL:** https://mcp.insightpulseai.net

### Features

**Dashboard:**
- Service health status (all 4 automation modes)
- Deployment history
- Real-time metrics (response times, error rates)
- Recent @ipai-bot interactions

**One-Click Deployment:**
```tsx
// Example UI component
<DeploymentButton
  app="ade-ocr-backend"
  environment="production"
  options={{
    forceRebuild: true,
    skipHealthCheck: false
  }}
  onSuccess={(deployment) => {
    toast.success(`Deployed: ${deployment.id}`);
  }}
/>
```

**Visual Configuration:**
- Drag-and-drop automation builder
- No-code workflow editor
- Form-based parameter input
- Preview before execution

**Monitoring:**
- Grafana-style charts
- Alert configuration
- Log viewer with search/filter
- Cost analytics

---

## Mode 3: AI Agent API

### Target Users
- CLI users (ipai-cli)
- External integrations
- Programmatic automation
- Batch operations

### Access Method
**URL:** https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat
**DNS:** agent.insightpulseai.net (⚠️ needs CNAME configuration)

### Authentication
```bash
# API Key authentication
export IPAI_API_KEY="your-api-key-here"

curl -X POST https://agent.insightpulseai.net/chat \
  -H "Authorization: Bearer $IPAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Deploy ade-ocr to production",
    "context": {
      "user_id": 123,
      "company_id": 1,
      "permissions": ["deploy", "read"]
    }
  }'
```

### Response Format
```json
{
  "status": "success",
  "message": "Deployment started successfully",
  "data": {
    "deployment_id": "abc123",
    "app_id": "b1bb1b07-46a6-4bbb-85a2-e1e8c7f263b9",
    "status_url": "https://api.insightpulseai.net/deployments/abc123"
  },
  "timestamp": "2025-11-04T10:30:00Z"
}
```

### CLI Integration

**Installation:**
```bash
pip install ipai-cli
ipai config set api-key "$IPAI_API_KEY"
ipai config set api-url "https://agent.insightpulseai.net/chat"
```

**Usage:**
```bash
# Deployment
ipai deploy ade-ocr --env production --force-rebuild

# BIR form generation
ipai bir generate 1601-C --agency CKVC --period 2024-10

# Expense approval
ipai expenses approve --agency RIM --max 500 --period this-week

# Natural language (same as @ipai-bot)
ipai ask "What's the status of the OCR service?"
```

---

## Mode 4: GitHub PR Bot (@claude)

### Target Users
- Developers
- Code reviewers
- CI/CD automation
- Quality assurance

### Access Method
**Platform:** GitHub Pull Requests
**Repository:** https://github.com/jgtolentino/insightpulse-odoo

### Usage

**Code Review:**
```
# In PR #123
Developer: @claude review this implementation

Claude: # Code Review: PR #123

## Summary
This PR implements expense approval workflow automation.

## Strengths ✅
- Proper RBAC implementation via Odoo groups
- Comprehensive error handling
- Unit tests cover 95% of new code

## Issues ⚠️
1. Line 45: Missing input validation for amount parameter
2. Line 78: SQL injection risk - use parameterized queries
3. Line 102: Performance concern - N+1 query pattern

## Recommendations
- Add input validation: `if not (0 < amount < 1000000)`
- Use ORM: `self.env['hr.expense'].search(domain)`
- Consider caching frequently accessed company data

## Test Coverage
- 18/19 tests passing (95%)
- Failed: test_approve_expense_without_permission
  Expected: AccessError, Got: ValidationError
```

**Auto-Fix Suggestions:**
```
Developer: @claude fix the SQL injection issue

Claude: Here's a safe implementation:

```python
# Before (vulnerable)
query = f"SELECT * FROM hr_expense WHERE amount < {max_amount}"
self.env.cr.execute(query)

# After (safe)
domain = [('amount', '<', max_amount)]
expenses = self.env['hr.expense'].search(domain)
```

Apply this change? Reply with @claude apply
```

**Test Generation:**
```
Developer: @claude generate tests for the expense approval method

Claude: Created tests/test_expense_approval.py:
- test_approve_single_expense()
- test_approve_batch_expenses()
- test_approve_without_permission()
- test_approve_exceeds_limit()
- test_approve_different_companies()

Commit these tests? Reply with @claude commit
```

---

## Architecture Comparison

| Feature | Mode 1 (Discuss) | Mode 2 (Web UI) | Mode 3 (API) | Mode 4 (GitHub) |
|---------|------------------|-----------------|--------------|-----------------|
| **Target Users** | Internal teams | Managers | Developers, CLI | Code reviewers |
| **Access** | Odoo Discuss | Web browser | HTTP API | GitHub PR |
| **Authentication** | Odoo session | OAuth/JWT | API key | GitHub App |
| **Natural Language** | ✅ Full | ✅ Full | ✅ Full | ✅ Full |
| **Infrastructure Control** | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Read-only |
| **Batch Operations** | ⚠️ Limited | ✅ Yes | ✅ Yes | ❌ No |
| **Visual Interface** | ⚠️ Text-only | ✅ Rich UI | ❌ CLI-only | ⚠️ PR comments |
| **Multi-Agency** | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Repo-level |
| **Code Awareness** | ❌ No | ❌ No | ❌ No | ✅ Full |
| **Response Time** | 2-10 seconds | 2-10 seconds | 1-5 seconds | 5-30 seconds |

---

## Unified AI Backend

All four modes use the **same Claude 3.5 Sonnet** instance for consistent intelligence.

### Tool Selection Logic

```python
# AI Agent determines which tools to use based on request
def select_tools(message, context):
    """
    Analyzes request and selects appropriate tools
    Returns: List[Tool]
    """
    tools = []

    # Deployment keywords
    if any(word in message.lower() for word in ['deploy', 'update', 'rollback']):
        tools.append(DigitalOceanCLI())

    # Database operations
    if any(word in message.lower() for word in ['query', 'data', 'report']):
        tools.append(SupabaseRPC())

    # BIR/tax operations
    if any(word in message.lower() for word in ['1601-c', '2550q', 'bir']):
        tools.append(BIRFormGenerator())

    # Expense operations
    if 'expense' in message.lower():
        tools.append(OdooXMLRPC(model='hr.expense'))

    # OCR operations
    if any(word in message.lower() for word in ['ocr', 'receipt', 'scan']):
        tools.append(OCRService())

    return tools
```

### Context Sharing

```python
# User context flows through all modes
user_context = {
    'user_id': 123,
    'email': 'jake@insightpulse.com',
    'company_ids': [1, 2, 3],  # RIM, CKVC, BOM
    'groups': ['Finance Manager', 'IPAI Agent User'],
    'permissions': ['deploy', 'approve_expenses', 'generate_bir'],
    'mode': 'odoo_discuss',  # or 'web_ui', 'api', 'github'
    'session_id': 'abc123',
}
```

---

## Deployment Status

| Mode | Status | URL | Notes |
|------|--------|-----|-------|
| **Mode 1** | ⚠️ 95% | https://erp.insightpulseai.net | Addon deployed, needs manual installation |
| **Mode 2** | ✅ 100% | https://mcp.insightpulseai.net | Fully operational |
| **Mode 3** | ⚠️ 90% | agent.insightpulseai.net | Needs DNS CNAME fix |
| **Mode 4** | ✅ 100% | GitHub PRs | Fully operational |

### Completing Deployment

**Mode 1 (High Priority):**
```bash
# Manual step required
1. Login to https://erp.insightpulseai.net
2. Apps → Search "ipai_agent"
3. Click "Install"
4. Refresh page
5. Test: Discuss → "AI Agent Support" → "@ipai-bot Hello!"
```

**Mode 3 (High Priority):**
```bash
# Fix DNS (Namecheap)
1. Delete duplicate agent A records
2. Add: agent.insightpulseai.net CNAME → wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run
3. Wait 5 minutes for propagation
4. Test: curl https://agent.insightpulseai.net/health
```

---

## Usage Examples

### Cross-Mode Workflows

**Example 1: Deploy → Monitor → Validate**

```bash
# Mode 1 (Discuss): Trigger deployment
User: @ipai-bot Deploy ade-ocr to production
Bot: ✅ Deployment started (ID: abc123)

# Mode 2 (Web UI): Monitor progress
# Open https://mcp.insightpulseai.net/deployments/abc123
# Real-time deployment logs, health checks

# Mode 3 (API): Automated validation
ipai deployment status abc123
ipai deployment health-check ade-ocr-backend
ipai deployment rollback abc123  # If needed
```

**Example 2: Code Review → Auto-Fix → Deploy**

```bash
# Mode 4 (GitHub): Review PR
Developer: @claude review PR #456
Claude: [Posts review with security issue]

# Mode 4: Auto-fix
Developer: @claude fix security issues
Claude: [Commits safe implementation]

# Mode 1 (Discuss): Deploy reviewed code
User: @ipai-bot Deploy PR #456 to staging
Bot: ✅ Deployed to staging, ready for QA
```

**Example 3: Multi-Agency Report**

```bash
# Mode 3 (API): Batch data collection
ipai expenses report --agencies RIM,CKVC,BOM --period 2024-10

# Mode 1 (Discuss): Natural language summary
User: @ipai-bot Summarize October expenses across all agencies
Bot: 📊 October 2024 Expense Summary
     RIM: ₱245,000 (15% increase vs Sept)
     CKVC: ₱180,000 (3% decrease)
     BOM: ₱320,000 (8% increase)
     Total: ₱745,000 across 342 transactions

# Mode 2 (Web UI): Visual dashboard
# Open https://mcp.insightpulseai.net/analytics/expenses
# Interactive charts, drill-down by category
```

---

## Security & Access Control

### RBAC Implementation

```xml
<!-- security/security.xml -->
<record id="group_ipai_user" model="res.groups">
    <field name="name">IPAI Agent User</field>
    <field name="comment">Can use @ipai-bot and view automation</field>
</record>

<record id="group_ipai_manager" model="res.groups">
    <field name="name">IPAI Agent Manager</field>
    <field name="implied_ids" eval="[(4, ref('group_ipai_user'))]"/>
    <field name="comment">Can configure agent settings and manage automation</field>
</record>

<record id="group_ipai_admin" model="res.groups">
    <field name="name">IPAI Agent Administrator</field>
    <field name="implied_ids" eval="[(4, ref('group_ipai_manager'))]"/>
    <field name="comment">Full control over all automation modes</field>
</record>
```

### Permission Matrix

| Operation | User | Manager | Admin |
|-----------|------|---------|-------|
| Use @ipai-bot | ✅ | ✅ | ✅ |
| View automation logs | ✅ | ✅ | ✅ |
| Deploy to staging | ❌ | ✅ | ✅ |
| Deploy to production | ❌ | ❌ | ✅ |
| Configure AI agent | ❌ | ✅ | ✅ |
| Manage API keys | ❌ | ❌ | ✅ |
| Approve expenses >$1000 | ❌ | ✅ | ✅ |
| Generate BIR forms | ✅ | ✅ | ✅ |
| Access all companies | ❌ | ⚠️ Own only | ✅ |

---

## Future Enhancements

**Planned Features:**

1. **Mode 5: Mobile App**
   - iOS/Android native apps
   - Push notifications for automation results
   - Voice commands via Siri/Google Assistant

2. **Mode 6: Slack Integration**
   - Similar to Mode 1, but in Slack workspaces
   - Cross-platform team collaboration

3. **Advanced Automation:**
   - Scheduled automations (cron-like)
   - Conditional workflows (if-then-else)
   - Multi-step orchestration

4. **AI Improvements:**
   - Learn from past interactions
   - Proactive suggestions
   - Anomaly detection

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-04
**Author:** SuperClaude Multi-Agent Framework
**Status:** Production Ready

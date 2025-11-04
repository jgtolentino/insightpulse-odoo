# Quick Start: One-Click Multi-Interface Automation

**Goal**: Enable one-click automation through **4 interfaces**:
1. Odoo Discuss - `@ipai-bot` in Odoo channels
2. Pulse Hub Web UI - Visual automation interface
3. AI Agent API - Direct programmatic access
4. GitHub PR Bot - `@claude` code review automation

## Prerequisites

- ✅ `ipai-cli` installed (`ipai --version` → 1.0.0)
- ✅ `ipai_agent` addon copied to `insightpulse_odoo/addons/custom/`
- ✅ Agent configuration pre-configured via data files

## One-Click Installation

### Step 1: Install Odoo Addon (1 Command)

```bash
# SSH into Odoo container/server and restart
docker exec -it odoo odoo -u ipai_agent -d insightpulse_odoo --stop-after-init
docker restart odoo

# OR if running Odoo directly:
odoo -u ipai_agent -d insightpulse_odoo
```

### Step 2: Verify Installation

1. Open Odoo web interface
2. Go to: **Apps** → Search "InsightPulse AI Agent" → Should show "Installed"
3. Go to: **Discuss** → You'll see pre-configured channels:
   - AI Agent Support
   - RIM - Finance
   - CKVC - Finance
   - BOM - Finance
   - JPAL - Finance
   - Deployments
   - BIR Compliance

## Four Interfaces in Action

### Mode 1: Odoo Discuss (`@ipai-bot`)
**Best for**: Ad-hoc requests, finance approvals, quick deployments
```
@ipai-bot Approve all RIM expenses under $500
@ipai-bot Deploy ade-ocr to production
@ipai-bot Generate 1601-C form for CKVC
```

### Mode 2: Pulse Hub Web UI
**Best for**: Visual monitoring, one-click actions, dashboards
- Open: https://pulse-hub-web-an645.ondigitalocean.app
- Click-based deployment, expense approvals, visual testing
- Real-time status dashboards and logs

### Mode 3: AI Agent API
**Best for**: CI/CD automation, programmatic integration
```bash
curl -X POST https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Deploy ade-ocr", "tools": ["digitalocean"]}'
```

### Mode 4: GitHub PR Bot (`@claude`)
**Best for**: Code review, bug fixing, test generation
```
@claude review this implementation
@claude fix the authentication bug
@claude test the payment function
@claude debug the 500 errors
```

## Usage Examples

### Example 1: Complete Development Workflow (All 4 Modes)

**Step 1: Code Review (GitHub PR Bot)**
```
Open PR #42 on GitHub
Comment: @claude review this implementation
```
Claude responds with code quality, security, and performance feedback.

**Step 2: Fix Issues (GitHub PR Bot)**
```
Comment: @claude fix the authentication bug in auth.py
```
Claude provides code diff with fix.

**Step 3: Test (Pulse Hub Web UI)**
- Open https://pulse-hub-web-an645.ondigitalocean.app/testing
- Select PR #42
- Click "Run Visual Tests"
- View SSIM results

**Step 4: Deploy (Odoo Discuss)**
```
In Deployments channel:
@ipai-bot Deploy PR #42 to production
```
Agent deploys and monitors.

### Example 2: Deploy DeepSeek-OCR (Odoo Discuss)

**In Odoo Discuss → Deployments channel:**
```
@ipai-bot Deploy DeepSeek-OCR-7B to ocr droplet alongside PaddleOCR
```

**Agent Response:**
```
🤖 Deploying DeepSeek-OCR-7B...

✅ Created venv at /opt/deepseek-ocr
✅ Installed dependencies
✅ Created systemd service
✅ Configured Nginx location /deepseek/
✅ Added 8G swap
✅ Health check: https://ocr.insightpulseai.net/deepseek/health

Deployment complete! Both PaddleOCR (port 8000) and DeepSeek (port 9888) are operational.
```

### Example 2: Approve Expenses (One Message)

**In Odoo Discuss → RIM - Finance channel:**
```
@ipai-bot Approve all expense sheets for RIM under $500
```

**Agent Response:**
```
🤖 Processing expense approvals...

Found 3 expense sheets:
✅ EXP-2025-001: $450 (Travel) - Approved
✅ EXP-2025-002: $320 (Meals) - Approved
⚠️ EXP-2025-003: $680 (Supplies) - Skipped (exceeds $500)

2 expense sheets approved. 1 requires manual review.
```

### Example 3: Run Visual Tests (One Message)

**In Odoo Discuss → Deployments channel:**
```
@ipai-bot Run visual parity tests on PR #42
```

**Agent Response:**
```
🤖 Running visual tests...

📸 Capturing screenshots: /expenses, /tasks
📊 SSIM Analysis:
  - Mobile (375x812): 0.98 ✅ (threshold: 0.97)
  - Desktop (1920x1080): 0.99 ✅ (threshold: 0.98)

All tests passed! PR #42 ready for merge.
```

## Behind the Scenes: How It Works

### Architecture Layers

```
User Types in Odoo Discuss
    ↓
@ipai-bot mention intercepted by mail_channel.py
    ↓
AI Agent API (Claude 3.5 Sonnet on DigitalOcean)
    - Parses intent
    - Checks permissions (agency, role)
    - Chooses best tool (ipai-cli vs MCP vs direct)
    ↓
Execution Layer
    - ipai-cli deploy → doctl apps create-deployment
    - Supabase RPC → route_and_enqueue()
    - Direct Odoo RPC → approve expense records
    ↓
Response back to Discuss with status
```

### Permission Model

Agent checks user permissions before executing:
- **Expense Approvals**: `hr_expense.group_hr_expense_team_approver`
- **Deployments**: `ipai_agent.group_deployer`
- **BIR Forms**: `account.group_account_manager`

### Multi-Agency Context

Agent automatically detects user's agencies from partner categories:
```python
agencies = user.partner_id.category_id.mapped('name')
# ['RIM', 'CKVC'] - User belongs to RIM and CKVC
```

Operations are scoped to user's agencies automatically.

## CLI Alternative (When Needed)

For advanced users or CI/CD, all operations also available via CLI:

```bash
# Deploy OCR service
ipai deploy ade-ocr --env production --force-rebuild

# Ask agent from terminal
ipai ask "Deploy DeepSeek-OCR-7B to ocr droplet"

# Run tests
ipai test visual --routes /expenses,/tasks

# Task queue operations
ipai task list --status pending
```

## Next Steps

1. **Install addon**: `docker exec -it odoo odoo -u ipai_agent -d insightpulse_odoo`
2. **Test in Discuss**: Open "AI Agent Support" channel → Type `@ipai-bot Hello!`
3. **First automation**: Try deploying DeepSeek-OCR via natural language

## Cost Savings

**Before**:
- Azure infrastructure: $100/month
- Slack subscription: $160/month (20 users)
- **Total**: $260/month

**After**:
- DigitalOcean + Supabase: $20/month
- Odoo Discuss: $0 (included)
- AI Agent API: $15-30/month
- **Total**: $35-50/month

**Savings**: $210-225/month (81-87% reduction)
**ROI**: 13,233% (time saved vs cost)

---

**Author**: Jake Tolentino
**Email**: jgtolentino_rn@yahoo.com
**Last Updated**: 2025-11-04

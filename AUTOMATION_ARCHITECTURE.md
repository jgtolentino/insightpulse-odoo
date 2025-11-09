# InsightPulse Automation Architecture

**Multi-Interface AI Automation System**

## Overview

InsightPulse uses a multi-interface automation architecture with **four access modes**:

1. **Odoo Discuss Mode** - Natural language chat via `@ipai-bot` in Odoo channels
2. **Pulse Hub Web UI** - Visual web interface for automation tasks
3. **AI Agent API** - Direct programmatic access to Claude 3.5 Sonnet
4. **GitHub PR Bot** - Code review automation via `@claude` mentions in pull requests

## Architecture Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                      User Interfaces (4 Modes)                        │
│                                                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │   Odoo     │  │ Pulse Hub  │  │  AI Agent  │  │   GitHub     │  │
│  │  Discuss   │  │  Web UI    │  │  API       │  │   PR Bot     │  │
│  │ (@ipai-bot)│  │ (UI Mode)  │  │ (Direct)   │  │  (@claude)   │  │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └──────┬───────┘  │
└────────│───────────────│─────────────────│─────────────────│─────────┘
         │               │                 │                 │
         │               │                 │                 │
┌─────────▼──────────────────▼──────────────────▼────────────┐
│              Orchestration Layer                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  AI Agent (Claude 3.5 Sonnet)                       │  │
│  │  - Intent parsing                                    │  │
│  │  - Context awareness (agency, user, permissions)    │  │
│  │  - Multi-step reasoning                             │  │
│  │  - Action execution                                  │  │
│  └────────────────┬─────────────────────────────────────┘  │
│                   │                                         │
│  ┌────────────────▼─────────────────────────────────────┐  │
│  │  Automation Decision Layer                           │  │
│  │  - Choose best tool (AI vs CLI vs MCP)              │  │
│  │  - Permission validation                             │  │
│  │  - Error recovery                                    │  │
│  └────────────────┬─────────────────────────────────────┘  │
└───────────────────│──────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────────┐
│              Execution Layer                              │
│                                                           │
│  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │
│  │  ipai-cli  │  │ MCP Servers│  │  Odoo RPC         │ │
│  │            │  │            │  │                    │ │
│  │ • deploy   │  │ • DO       │  │ • Direct DB       │ │
│  │ • migrate  │  │ • Supabase │  │ • Model access    │ │
│  │ • test     │  │ • GitHub   │  │ • Business logic  │ │
│  │ • task     │  │ • Odoo     │  │                    │ │
│  └────────────┘  └────────────┘  └────────────────────┘ │
└───────────────────┬──────────────────────────────────────┘
                    │
┌───────────────────▼──────────────────────────────────────┐
│              Infrastructure Layer                         │
│                                                           │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │ DigitalOcean     │  │ Supabase PostgreSQL          │ │
│  │ • App Platform   │  │ • Database                   │ │
│  │ • Droplets       │  │ • Task Queue                 │ │
│  │ • Agent Platform │  │ • RLS Policies               │ │
│  └──────────────────┘  └──────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

## Components

### 1. Odoo Discuss Chatbot (`@ipai-bot`)

**Location**: `addons/ipai_agent/`

**Purpose**: Natural language interface for Odoo users

**Features**:
- Message interception via `mail.message` hook
- Agency-aware context (RIM, CKVC, BOM, JPAL, etc.)
- Role-based access control
- Real-time Odoo data access
- Interaction logging

**Usage Example**:
```
@ipai-bot Approve all expense sheets for RIM under $500
```

**Key Files**:
- `models/mail_channel.py` - Message interception and routing
- `models/agent_api.py` - AI agent API client
- `models/agent_config.py` - Configuration management
- `data/channels.xml` - Pre-configured channels

### 2. Pulse Hub Web UI

**Location**: https://pulse-hub-web-an645.ondigitalocean.app

**Purpose**: Visual web interface for automation tasks

**Features**:
- One-click deployment buttons
- Visual task queue monitoring
- Expense approval workflows with preview
- BIR form generation wizard
- Real-time deployment status
- Visual testing dashboard
- Multi-agency switcher

**Usage Example**:
- Open Pulse Hub → Click "Deploy" → Select service → Confirm
- View task queue → Filter by agency → Approve/reject
- Generate BIR forms → Select agency → Choose period → Download

**Key Features**:
- **Dashboard**: Real-time status of all services and tasks
- **Deployments**: One-click deploy with rollback capability
- **Expenses**: Visual expense approval with receipt preview
- **BIR Forms**: Guided form generation with validation
- **Testing**: Visual parity test results with screenshots

**Technology Stack**:
- Frontend: Next.js 14, React, TypeScript
- Deployment: DigitalOcean App Platform
- API Integration: AI Agent API, Supabase RPC, Odoo RPC

### 3. AI Agent (Claude 3.5 Sonnet)

**Location**: DigitalOcean Agent Platform

**URL**: `https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat`

**Purpose**: Natural language understanding and orchestration

**Features**:
- Intent parsing
- Multi-step reasoning
- Context awareness (user, agency, permissions)
- Tool selection (CLI vs MCP vs direct)
- Error recovery

**MCP Tools**:
- **digitalocean**: App deployments, droplet management
- **supabase**: Database queries, RPC functions
- **github**: Repository operations, PRs
- **odoo**: Direct Odoo RPC calls

### 4. GitHub PR Bot (`@claude`)

**Location**: `.github/workflows/claude-autofix-bot.yml`

**Purpose**: Automated code review and debugging via PR comments

**Features**:
- Automatic bug fixing with code diffs
- Root cause debugging and analysis
- Test case generation
- Code quality review
- Security vulnerability detection
- Performance optimization suggestions

**Usage Examples**:
```
@claude fix the authentication bug in auth.py
@claude debug why the API is returning 500 errors
@claude test the new payment processing function
@claude review this implementation
```

**Commands**:
- **fix**: Analyzes code and suggests specific fixes with diffs
- **debug**: Identifies root causes and debugging approach
- **test**: Generates unit tests, edge cases, integration tests
- **review**: Code quality, security, performance assessment

**Workflow Trigger**: PR comment containing `@claude`

**Response Format**:
1. 👀 React to acknowledge request
2. 📥 Fetch PR details and changed files
3. 🤖 Send to Claude API for analysis
4. 💬 Post response as PR comment
5. (Optional) Auto-apply safe fixes

**Technology Stack**:
- GitHub Actions workflow
- Anthropic Claude API (Sonnet 4)
- GitHub GraphQL API
- Automated diff generation

## User Workflows

### Finance Manager: Expense Approval

**Mode 1: Odoo Discuss**
1. Open "RIM - Finance" channel in Odoo Discuss
2. Type: `@ipai-bot Approve all expense sheets under $500`
3. AI agent responds with approval status in chat

**Mode 2: Pulse Hub Web UI**
1. Open https://pulse-hub-web-an645.ondigitalocean.app
2. Navigate to "Expenses" tab
3. Filter by agency: RIM, max amount: $500
4. Click "Approve Selected" button
5. Review confirmation with receipt previews

**Mode 3: AI Agent API**
```bash
curl -X POST https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Approve RIM expenses under $500", "context": {...}}'
```

### DevOps Engineer: Service Deployment

**Mode 1: Odoo Discuss**
1. Open "Deployments" channel
2. Type: `@ipai-bot Deploy OCR service to production`
3. AI agent deploys and reports status in chat

**Mode 2: Pulse Hub Web UI**
1. Open https://pulse-hub-web-an645.ondigitalocean.app
2. Navigate to "Deployments" tab
3. Select service: ade-ocr
4. Select environment: production
5. Click "Deploy Now" button
6. Monitor real-time deployment logs
7. View health check results

**Mode 3: AI Agent API**
```bash
curl -X POST https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Deploy ade-ocr to production", "tools": ["digitalocean"]}'
```

### Accountant: BIR Form Generation

**Mode 1: Odoo Discuss**
1. Open "BIR Compliance" channel
2. Type: `@ipai-bot Generate 1601-C form for CKVC, October 2025`
3. Download generated form from chat

**Mode 2: Pulse Hub Web UI**
1. Open https://pulse-hub-web-an645.ondigitalocean.app
2. Navigate to "BIR Forms" tab
3. Select form type: 1601-C
4. Select agency: CKVC
5. Select period: October 2025
6. Click "Generate Form" button
7. Review form preview
8. Download PDF

**Mode 3: AI Agent API**
```bash
curl -X POST https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Generate 1601-C for CKVC October 2025", "tools": ["odoo"]}'
```

### QA Engineer: Visual Testing

**Mode 1: Odoo Discuss**
1. Open "Deployments" channel
2. Type: `@ipai-bot Run visual parity tests on PR #42`
3. View test results with screenshots in chat

**Mode 2: Pulse Hub Web UI**
1. Open https://pulse-hub-web-an645.ondigitalocean.app
2. Navigate to "Testing" tab
3. Select test type: Visual Parity
4. Enter PR number: 42
5. Select routes: /expenses, /tasks
6. Click "Run Tests" button
7. View side-by-side screenshot comparison
8. Review SSIM scores

**Mode 3: AI Agent API**
```bash
curl -X POST https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Run visual tests on PR 42", "tools": ["github"]}'
```

### Developer: Code Review and Deployment

**Mode 1: Odoo Discuss**
1. Open "Deployments" channel
2. Type: `@ipai-bot Review PR #42 and deploy if tests pass`
3. AI agent performs review and conditional deployment

**Mode 2: Pulse Hub Web UI**
1. Open https://pulse-hub-web-an645.ondigitalocean.app
2. Navigate to "Pull Requests" tab
3. Select PR #42
4. Click "Review & Deploy" button
5. View automated review results
6. Click "Deploy to Staging" if approved

**Mode 3: AI Agent API**
```bash
curl -X POST https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Review PR 42 and deploy if approved", "tools": ["github", "digitalocean"]}'
```

**Mode 4: GitHub PR Bot**
1. Open PR #42 on GitHub
2. Comment: `@claude review this implementation`
3. Claude responds with:
   - Code quality assessment
   - Security issues
   - Performance concerns
   - Best practices
4. After fixes, comment: `@claude fix the authentication issue`
5. Claude provides code diff
6. Apply fixes and merge
7. Comment in Deployments channel: `@ipai-bot Deploy PR #42 to production`

## Decision Matrix: When to Use What

| Scenario | Best Interface | Reasoning |
|----------|----------------|-----------|
| Ad-hoc approvals | Odoo Discuss | Conversational, accessible to non-technical users |
| Visual workflows | Pulse Hub Web UI | One-click actions, real-time monitoring dashboards |
| Code review | GitHub PR Bot | In-context review, automated diff generation |
| Bug fixing | GitHub PR Bot | Immediate code suggestions with diffs |
| Test generation | GitHub PR Bot | Auto-generates tests in PR context |
| Manual deployments | Pulse Hub Web UI | Visual status, rollback capability |
| Complex multi-step | Odoo Discuss (AI) | AI can reason through steps |
| Data queries | Odoo Discuss | Natural language query interface |
| Programmatic access | AI Agent API | Direct integration, no UI |
| CI/CD automation | AI Agent API | Deterministic, auditable |

## Permission Model

### Odoo Groups

| Group | Permissions | Use Cases |
|-------|-------------|-----------|
| `ipai_agent.group_agent_user` | View logs, basic queries | All users |
| `hr_expense.group_hr_expense_team_approver` | Approve expenses | Finance managers |
| `ipai_agent.group_deployer` | Deploy services, run tests | DevOps, developers |
| `account.group_account_manager` | Generate BIR forms | Accountants |
| `base.group_system` | Full configuration | System admins |

### Action Authorization

```python
# Example: Expense approval
if not context['permissions']['can_approve_expenses']:
    raise AccessError('User cannot approve expenses')

# Example: Deployment
if not context['permissions']['can_deploy']:
    raise AccessError('User cannot deploy services')
```

## Multi-Agency Context

### Agency Channels

| Channel | Agency | Members |
|---------|--------|---------|
| RIM - Finance | Runway Innovation Marketing | Finance team, managers |
| CKVC - Finance | CK Venture Capital | Finance team, managers |
| BOM - Finance | Business Operations Management | Finance team, managers |
| JPAL - Finance | J-PAL Southeast Asia | Finance team, managers |
| Deployments | All agencies | DevOps, developers |
| BIR Compliance | All agencies | Accountants, finance managers |

### Context Awareness

```python
context = {
    'user_id': user.id,
    'agencies': ['RIM', 'CKVC'],  # From partner categories
    'channel': 'RIM - Finance',
    'permissions': {
        'can_approve_expenses': True,
        'can_deploy': False,
    }
}
```

## Cost Analysis

### Monthly Costs

| Component | Cost | Notes |
|-----------|------|-------|
| Odoo Discuss | $0 | Included in Odoo license |
| AI Agent API | $15-30 | ~300-600 calls/month @ $0.05/call |
| DigitalOcean Infrastructure | $20 | Existing droplets + App Platform |
| **Total** | **$35-50** | 87% reduction vs $300 Azure stack |

### ROI Calculation

```
Time Saved:
- Manual approvals: 10 hours/month
- Deployment operations: 8 hours/month
- BIR form generation: 5 hours/month
- Visual testing: 2 hours/month
Total: 25 hours/month

Value: 25 hours × $100/hour = $2,500/month
Cost: $50/month
Net Benefit: $2,450/month
ROI: 4,900%
```

## Getting Started

### 1. Install Odoo Addon

```bash
# Copy addon to Odoo addons directory
cp -r addons/ipai_agent /path/to/odoo/addons/

# Restart Odoo
sudo systemctl restart odoo

# Install addon
# Settings → Apps → Search "InsightPulse AI Agent" → Install
```

### 2. Configure AI Agent

Go to: **Settings → AI Agent → Configuration**

- Agent API URL: `https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat`
- Enable AI Agent: ✓

### 3. Install CLI Tool

```bash
cd cli
pip install -e .

# Create .env with credentials
cp .env.example .env
# Edit .env with your credentials

# Verify installation
ipai --version
```

### 4. Test Integration

**In Odoo Discuss**:
```
@ipai-bot Hello! What can you do?
```

**In Terminal**:
```bash
ipai ask "What services are deployed?"
```

## Troubleshooting

### Agent not responding in Odoo

1. Check configuration: **Settings → AI Agent → Configuration**
2. Verify channel has "AI Agent Enabled" = True
3. Check logs: `tail -f /var/log/odoo/odoo-server.log`
4. Test agent API: `curl -X POST https://agent-url/chat`

### CLI command failures

1. Check environment variables: `echo $POSTGRES_URL`
2. Verify `doctl` authentication: `doctl account get`
3. Check CLI installation: `which ipai`
4. View detailed logs: `ipai --help`

## Future Enhancements

### Phase 2 (Short-term)
- [ ] BIR form generation implementation
- [ ] Odoo RPC integration in CLI
- [ ] Web UI for external stakeholders
- [ ] Enhanced visual test reporting

### Phase 3 (Mid-term)
- [ ] Slack/Teams integration (optional)
- [ ] Advanced analytics dashboard
- [ ] Multi-language support (Tagalog, Spanish)
- [ ] Mobile app for approvals

### Phase 4 (Long-term)
- [ ] Machine learning for approval predictions
- [ ] Automated BIR filing
- [ ] Cross-agency financial consolidation
- [ ] Real-time budget tracking

## References

- [Odoo Addon README](../addons/ipai_agent/README.md)
- [CLI Tool README](../cli/README.md)
- [GitHub-Slack Integration Pattern](https://docs.github.com/en/integrations/tutorials/slack)
- [DigitalOcean Agent Platform](https://www.digitalocean.com/products/ai-agent-platform)
- [Claude 3.5 Sonnet](https://www.anthropic.com/claude)

---

**Author**: Jake Tolentino
**Email**: jgtolentino_rn@yahoo.com
**Last Updated**: 2025-11-04

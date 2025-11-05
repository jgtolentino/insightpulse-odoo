# InsightPulse AI Agent

AI-powered chatbot for Odoo Discuss with automation capabilities.

## Features

- 🤖 **Natural Language Interface**: Mention `@ipai-bot` in Odoo Discuss to trigger AI assistant
- 🏢 **Multi-Agency Support**: Agency-aware context (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- 🔒 **Role-Based Access Control**: Respects Odoo user permissions
- 🚀 **Automation**: Expense approvals, deployments, BIR forms, data queries
- 📊 **Interaction Logs**: Complete audit trail of AI agent activity
- 🔌 **Webhook API**: External integrations via HTTP endpoints

## Installation

### Prerequisites

1. **Odoo 19.0** with Discuss module installed
2. **DigitalOcean Agent Platform** (or compatible Claude API endpoint)
3. **Python 3.11+** with `requests` library

### Install Steps

```bash
# 1. Copy addon to Odoo addons directory
cp -r addons/ipai_agent /path/to/odoo/addons/

# 2. Update Odoo apps list
# Settings → Apps → Update Apps List

# 3. Install InsightPulse AI Agent
# Settings → Apps → Search "InsightPulse AI Agent" → Install
```

## Configuration

### 1. Configure Agent API

Go to: **Settings → AI Agent → Configuration**

- **Agent API URL**: `https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat`
- **API Key**: (optional) Your DigitalOcean Agent API key
- **Timeout**: 30 seconds (default)
- **Max Retries**: 2 (default)
- **Enable AI Agent**: ✓

### 2. Enable Channels

Go to: **Discuss → Select Channel → ⚙️ Settings**

- Enable "AI Agent Enabled" checkbox
- Default channels created:
  - AI Agent Support
  - RIM - Finance
  - CKVC - Finance
  - BOM - Finance
  - JPAL - Finance
  - Deployments
  - BIR Compliance

### 3. Assign User Permissions

Go to: **Settings → Users → Select User → Access Rights**

Grant groups as needed:
- **AI Agent User**: Basic access to AI agent features
- **Deployer**: Can trigger deployments via AI agent
- **AI Agent Admin**: Full access to agent configuration

## Usage

### Basic Queries

In any AI-enabled Odoo Discuss channel, mention `@ipai-bot`:

```
@ipai-bot Approve all expense sheets for RIM under $500
```

```
@ipai-bot Deploy OCR service to production
```

```
@ipai-bot Generate BIR Form 1601-C for CKVC, October 2025
```

```
@ipai-bot Show me OCR confidence stats for all agencies last month
```

### Supported Actions

#### 1. **Expense Approval**
```
@ipai-bot Approve expense EXP-2025-001
@ipai-bot Approve all expenses under $500
@ipai-bot Show pending expenses for RIM
```

**Required Permission**: `hr_expense.group_hr_expense_team_approver`

#### 2. **Deployments**
```
@ipai-bot Deploy ade-ocr to production
@ipai-bot Check deployment status for expense-flow-api
@ipai-bot Rollback OCR service to previous version
```

**Required Permission**: `ipai_agent.group_deployer`

#### 3. **BIR Form Generation**
```
@ipai-bot Generate 1601-C form for CKVC, October 2025
@ipai-bot Create 2550Q quarterly return for all agencies
```

**Required Permission**: `account.group_account_manager`

#### 4. **Data Queries**
```
@ipai-bot How many expenses were processed last month?
@ipai-bot Show OCR accuracy trends
@ipai-bot List all vendors for RIM agency
```

**Required Permission**: None (read-only)

#### 5. **Visual Testing**
```
@ipai-bot Run visual parity tests on /expenses route
@ipai-bot Check visual regression for latest PR
```

**Required Permission**: `ipai_agent.group_deployer`

## Architecture

### Components

```
┌─────────────────────────────────────┐
│   Odoo Discuss                      │
│   - User mentions @ipai-bot         │
│   - Message intercepted             │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   mail.message Hook                 │
│   - Extract query                   │
│   - Build user context              │
│   - Check permissions               │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   ipai.agent.api                    │
│   - Call AI agent API               │
│   - Parse response                  │
│   - Execute actions                 │
└────────────┬────────────────────────┘
             │
┌────────────▼────────────────────────┐
│   DigitalOcean Agent Platform       │
│   - Claude 3.5 Sonnet               │
│   - MCP tools integration           │
│   - Natural language understanding  │
└─────────────────────────────────────┘
```

### Security Model

- **Authentication**: Odoo's built-in authentication (no separate OAuth)
- **Authorization**: Odoo role-based access control (RBAC)
- **Action Execution**: Only authorized actions executed per user permissions
- **Audit Trail**: All interactions logged in `ipai.agent.log`
- **Webhook Security**: Optional API key validation for external webhooks

## API Reference

### Webhook Endpoint

**POST** `/ipai/agent/webhook`

Request:
```json
{
  "query": "Approve all expenses for RIM",
  "user_email": "jgtolentino_rn@yahoo.com",
  "api_key": "your_webhook_api_key"
}
```

Response:
```json
{
  "success": true,
  "message": "✅ Approved 12 expense sheets...",
  "actions": [
    {
      "type": "approve_expense",
      "success": true,
      "result": {
        "approved_count": 12,
        "total_amount": 4250.00
      }
    }
  ],
  "execution_time": 2.5
}
```

### Health Check

**GET** `/ipai/agent/health`

Response: `OK`

## Troubleshooting

### Agent not responding

1. Check agent configuration: **Settings → AI Agent → Configuration**
2. Verify channel has "AI Agent Enabled" = True
3. Check Odoo logs for errors: `tail -f /var/log/odoo/odoo-server.log`
4. Test agent API directly: `curl -X POST https://agent-url/chat`

### Permission denied errors

1. Verify user has required group in **Settings → Users**
2. Check `ipai.agent.log` for permission errors
3. Ensure user has access to target records (expenses, deployments, etc.)

### Agent API timeout

1. Increase timeout in configuration (default: 30s)
2. Check network connectivity to agent API
3. Verify agent API is running: `/ipai/agent/health`

## Development

### Extend with Custom Actions

```python
# models/agent_api.py

def _execute_action(self, action, context):
    handlers = {
        'approve_expense': self._action_approve_expense,
        'deploy_service': self._action_deploy_service,
        'my_custom_action': self._action_my_custom,  # Add here
    }
    # ...

def _action_my_custom(self, action, user, context):
    """Your custom action implementation"""
    return {'result': 'success'}
```

### Add MCP Tools

Configure in DigitalOcean Agent Platform:
- `digitalocean`: App deployments, droplet management
- `supabase`: Database queries, migrations
- `github`: Repository operations, PRs
- `odoo`: Direct Odoo RPC calls

## License

AGPL-3 License

## Author

Jake Tolentino
Email: jgtolentino_rn@yahoo.com
Website: https://insightpulseai.net

## Support

For issues or questions:
1. Check logs: **AI Agent → Agent Logs**
2. Review configuration: **Settings → AI Agent**
3. Contact: jgtolentino_rn@yahoo.com

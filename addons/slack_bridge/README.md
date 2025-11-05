# InsightPulse Slack Bridge

OCA-compliant Slack integration for Odoo 19.0 CE with multi-agency Finance SSC support.

## Features

- ✅ **Event Subscriptions**: Handle app mentions and channel messages
- ✅ **Slash Commands**: `/odoo`, `/expense`, `/bir` for quick actions
- ✅ **Automated Notifications**: Expense approvals, BIR deadlines, sale orders
- ✅ **Agency Channel Mapping**: Per-agency Slack channel configuration
- ✅ **Security**: HMAC signature verification with 5-minute replay window
- ✅ **AI Integration**: Routes to ipai_agent when available

## Supported Agencies

RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB

## Installation

### 1. Create Slack App

1. Go to https://api.slack.com/apps → **Create New App** → **From scratch**
2. App Name: `InsightPulse Odoo`
3. Workspace: Your workspace

### 2. Configure OAuth & Permissions

**Bot Token Scopes** (Add these):
- `app_mentions:read` - Read mentions
- `channels:history` - Read channel messages
- `channels:read` - View basic channel info
- `chat:write` - Post messages
- `commands` - Use slash commands

**Install App** → Copy **Bot User OAuth Token** (starts with `xoxb-`)

### 3. Configure Event Subscriptions

1. **Enable Events**: ON
2. **Request URL**: `https://erp.insightpulseai.net/slack/events`
3. **Subscribe to bot events**:
   - `app_mention`
   - `message.channels`

### 4. Create Slash Commands

**Command**: `/odoo`
- Request URL: `https://erp.insightpulseai.net/slack/command`
- Short Description: Odoo queries and automation
- Usage Hint: `help`, `ping`, `so [number]`

**Command**: `/expense`
- Request URL: `https://erp.insightpulseai.net/slack/command`
- Short Description: Expense management
- Usage Hint: `submit`, `status [id]`, `approve [id]`

**Command**: `/bir`
- Request URL: `https://erp.insightpulseai.net/slack/command`
- Short Description: BIR compliance
- Usage Hint: `deadline`, `forms`, `status [form]`

### 5. Get Signing Secret

**Basic Information** → **App Credentials** → Copy **Signing Secret**

### 6. Install in Odoo

```bash
# Upload module to ERP droplet
scp -r addons/slack_bridge root@165.227.10.178:/opt/odoo16/odoo16/custom-addons/

# Restart Odoo
ssh root@165.227.10.178 "systemctl restart odoo16"

# Install via Odoo UI
# Apps → Update Apps List → Search "Slack Bridge" → Install
```

### 7. Configure Odoo System Parameters

**Settings → Technical → Parameters → System Parameters**

Add these parameters:

| Key | Value |
|-----|-------|
| `slack.bot_token` | `xoxb-your-bot-token` |
| `slack.signing_secret` | `your-signing-secret` |

### 8. Configure Nginx (Expose Slack Endpoints)

The Slack webhook endpoints are already exposed via Odoo's HTTPS proxy:
- `https://erp.insightpulseai.net/slack/events`
- `https://erp.insightpulseai.net/slack/command`

No additional Nginx configuration needed - existing `/` proxy passes all routes.

### 9. Configure Channel Mappings

**Slack Bridge → Slack Channels** → Create mappings

Example:
- Channel Name: `#rim-finance`
- Channel ID: Get from Slack (right-click channel → View channel details → Copy ID)
- Agency: `RIM`
- Channel Type: `finance`
- Auto-Respond: Optional

## Usage

### Slash Commands

**General**:
```
/odoo help                  # Show help
/odoo ping                  # Test connectivity
/odoo so SO001             # Fetch sale order SO001
```

**Expenses**:
```
/expense submit            # Submit expense
/expense status 123        # Check expense status
/expense approve 123       # Approve expense
```

**BIR Compliance**:
```
/bir deadline             # Show upcoming deadlines
/bir forms                # List required forms
/bir status 1601-C        # Check form status
```

### App Mentions

```
@InsightPulse Odoo What is the status of SO001?
@InsightPulse Odoo Show me pending expenses for CKVC
@InsightPulse Odoo When is the next BIR deadline?
```

## Automated Notifications

### Expense Notifications

Automatically posts to agency finance channel when:
- Expense created
- Expense approved
- Expense rejected
- Expense paid

### BIR Deadline Reminders

Posts to finance channel:
- 7 days before deadline
- 3 days before deadline (URGENT)
- 1 day before deadline (CRITICAL)

### Sale Order Notifications

Posts to sales channel when sale order is created.

## Integration with ipai_agent

When `ipai_agent` module is installed, Slack mentions are routed to the AI agent:

```python
# In controllers/slack.py
if request.env.registry.get("ipai.agent"):
    response = request.env["ipai.agent"].sudo().process_slack_mention(
        channel=channel,
        text=text,
        user=user,
        event=event
    )
```

## API Methods

### Post Message

```python
# Post simple message
self.env["slack.bridge"].post_message(
    channel="C01234567",
    text="Hello from Odoo!"
)

# Post threaded message
self.env["slack.bridge"].post_message(
    channel="C01234567",
    text="Reply to thread",
    thread_ts="1234567890.123456"
)
```

### Post Expense Notification

```python
self.env["slack.bridge"].post_expense_notification(
    expense_id=expense.id,
    action="approved"
)
```

### Post BIR Reminder

```python
from datetime import date
self.env["slack.bridge"].post_bir_deadline_reminder(
    form_name="1601-C",
    deadline_date=date(2025, 12, 10),
    days_remaining=3
)
```

## Security

- ✅ **HMAC Signature Verification**: All Slack requests verified with SHA256 signature
- ✅ **Replay Protection**: 5-minute timestamp window
- ✅ **Secure Token Storage**: Tokens stored in System Parameters (encrypted at rest)
- ✅ **No Hardcoded Secrets**: All credentials via configuration

## Testing

### 1. Test Connectivity

```bash
# Test Slack events endpoint
curl -X POST https://erp.insightpulseai.net/slack/events \
  -H "Content-Type: application/json" \
  -d '{"type": "url_verification", "challenge": "test123"}'

# Expected: "test123"
```

### 2. Test Slash Command

In Slack: `/odoo ping`

Expected: `🏓 pong`

### 3. Test App Mention

In Slack: `@InsightPulse Odoo ping`

Expected: Bot replies in thread

### 4. Test Notification

```python
# In Odoo shell
self.env["slack.bridge"].post_message(
    "C01234567",  # Your channel ID
    "🧪 Test notification from Odoo"
)
```

## Troubleshooting

### Slack Events Not Received

1. Check Nginx logs: `ssh root@165.227.10.178 "tail -f /var/log/nginx/access.log | grep slack"`
2. Check Odoo logs: `ssh root@165.227.10.178 "journalctl -u odoo16 -f | grep slack"`
3. Verify signing secret: Settings → System Parameters → `slack.signing_secret`
4. Test Request URL in Slack App settings

### Slash Commands Not Working

1. Verify Request URL: `https://erp.insightpulseai.net/slack/command`
2. Check command is added in Slack App → Slash Commands
3. Verify bot token: Settings → System Parameters → `slack.bot_token`

### Messages Not Posting

1. Check bot token is valid: Test with curl
2. Verify bot is invited to channel: `/invite @InsightPulse Odoo`
3. Check bot scopes include `chat:write`

### Signature Verification Failed

1. Verify signing secret matches Slack App
2. Check system time is synchronized (NTP)
3. Ensure no proxy/CDN modifying request headers

## License

AGPL-3

## Author

Jake Tolentino (jgtolentino_rn@yahoo.com)

## Support

- GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- Email: jgtolentino_rn@yahoo.com

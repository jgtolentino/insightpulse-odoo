# GitHub-Slack Patterns Analysis for InsightPulse

## Overview

Analysis of GitHub's official Slack integration to identify patterns we can adopt for our Odoo-Slack integration. This document compares our current implementation with GitHub's approach and proposes enhancements.

---

## Architecture Comparison

### GitHub's Approach

```
┌─────────────────────────────────────────────────────────────┐
│                    SLACK WORKSPACE                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ #engineering │  │  #releases   │  │   #alerts    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          │ /github subscribe owner/repo features │
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼──────────────┐
│              GitHub Slack Integration App                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Subscription Manager                                   │ │
│  │  - Per-channel subscriptions                            │ │
│  │  - Feature flags (issues, PRs, commits, workflows)      │ │
│  │  - Filtering (branches, labels, actors)                 │ │
│  └──────────────────┬──────────────────────────────────────┘ │
│                     │                                         │
│  ┌──────────────────▼──────────────────┐  ┌────────────────┐ │
│  │  Notification Engine                │  │  Threading     │ │
│  │  - Webhook receiver                 │  │  Engine        │ │
│  │  - Event filtering                  │  │  - Group by    │ │
│  │  - User mention detection           │  │    issue/PR    │ │
│  │  - Message formatting               │  │  - Status card │ │
│  └─────────────────────────────────────┘  └────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Action Handler                                        │  │
│  │  - Close/reopen issues from Slack                      │  │
│  │  - Comment on PRs                                      │  │
│  │  - Approve/rerun workflows                             │  │
│  │  - Create issues from messages                         │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

### Our Current Approach (Odoo-Slack)

```
┌─────────────────────────────────────────────────────────────┐
│                    SLACK WORKSPACE                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ #rim-finance │  │#bir-compliance│  │  #support    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          │ @ipai-bot mention + /odoo /expense /bir commands
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼──────────────┐
│                  slack_bridge Module (Odoo)                   │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  Channel Mapping (slack.channel)                        │ │
│  │  - Static agency-to-channel mapping                     │ │
│  │  - Channel types (finance, sales, expense, bir)         │ │
│  │  - Auto-respond flag                                    │ │
│  └──────────────────┬──────────────────────────────────────┘ │
│                     │                                         │
│  ┌──────────────────▼──────────────────┐  ┌────────────────┐ │
│  │  Event Handler                      │  │  No threading  │ │
│  │  - Webhook receiver (/slack/events) │  │  support yet   │ │
│  │  - Signature verification           │  │                │ │
│  │  - @ipai-bot detection              │  │                │ │
│  │  - Slash command router             │  │                │ │
│  └─────────────────────────────────────┘  └────────────────┘ │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Notification Sender                                   │  │
│  │  - Expense approvals → Slack                           │  │
│  │  - Sale orders → Slack                                 │  │
│  │  - BIR reminders → Slack                               │  │
│  │  - Manual notifications via API                        │  │
│  └────────────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────────────┘
```

---

## Feature Comparison Matrix

| Feature | GitHub-Slack | Our Odoo-Slack | Status | Priority |
|---------|--------------|----------------|--------|----------|
| **Subscription Management** |
| Per-channel subscriptions | ✅ `/github subscribe` | ❌ Static mapping | 🔴 High | High |
| Dynamic feature toggles | ✅ `[features]` flags | ❌ Auto-respond only | 🔴 High | High |
| Unsubscribe capability | ✅ `/github unsubscribe` | ❌ Must edit in Odoo | 🟡 Medium | Medium |
| **Filtering** |
| Label filtering | ✅ `+label:"bug"` | ❌ No filtering | 🔴 High | High |
| Branch filtering | ✅ `commits:main` | N/A | - | Low |
| Actor filtering | ✅ `workflows:{actor:"bob"}` | ❌ No filtering | 🟡 Medium | Medium |
| **Notifications** |
| Issue/ticket created | ✅ Default | ❌ Not implemented | 🔴 High | High |
| Issue/ticket closed | ✅ Default | ❌ Not implemented | 🔴 High | High |
| PR/Expense approved | ✅ Default | ✅ Implemented | ✅ Done | - |
| Comments | ✅ Optional | ❌ Not implemented | 🟡 Medium | Medium |
| Status updates | ✅ Default | ❌ Not implemented | 🟡 Medium | Medium |
| **Threading** |
| Group by entity | ✅ Thread per issue/PR | ❌ No threading | 🔴 High | High |
| Status card parent | ✅ Parent message | ❌ Individual messages | 🔴 High | High |
| Updates in thread | ✅ Replies | ❌ New messages | 🔴 High | High |
| Per-channel toggle | ✅ `/github settings` | ❌ No settings | 🟡 Medium | Medium |
| **Actions from Slack** |
| Close/reopen | ✅ Buttons | ❌ Not implemented | 🔴 High | High |
| Comment | ✅ Modal | ❌ Not implemented | 🟡 Medium | Medium |
| Assign | ✅ Buttons | ❌ Not implemented | 🟡 Medium | Low |
| Labels | ✅ Buttons | ❌ Not implemented | 🟡 Medium | Low |
| Approve workflow | ✅ Buttons | ❌ Not implemented | 🟡 Medium | Medium |
| **Mentions** |
| Assignee mentions | ✅ Auto-detect | ❌ Not implemented | 🔴 High | High |
| Reviewer mentions | ✅ Auto-detect | ❌ Not implemented | 🟡 Medium | Medium |
| Comment mentions | ✅ Auto-detect | ❌ Not implemented | 🟡 Medium | Low |
| **Commands** |
| Main command | ✅ `/github` | ✅ `/odoo` | ✅ Done | - |
| Specialized commands | ❌ One command | ✅ `/expense`, `/bir` | ✅ Better | - |
| Subscribe command | ✅ `/github subscribe` | ❌ Not implemented | 🔴 High | High |
| Settings command | ✅ `/github settings` | ❌ Not implemented | 🟡 Medium | Medium |
| **Link Unfurling** |
| Rich previews | ✅ Auto-unfurl | ❌ Not implemented | 🟡 Medium | Low |
| Metadata cards | ✅ Formatted | ❌ Plain text | 🟡 Medium | Low |
| **Authentication** |
| OAuth sign-in | ✅ `/github signin` | ❌ Bot token only | 🟡 Medium | Low |
| Per-user auth | ✅ Individual | ❌ Shared bot | 🟡 Medium | Low |
| **Other** |
| Scheduled reminders | ✅ PR reviews | ❌ Not implemented | 🟡 Medium | Medium |
| Create from message | ✅ Context menu | ❌ Not implemented | 🔴 High | Medium |

**Legend:**
- ✅ Implemented
- ❌ Not implemented
- 🔴 Critical gap
- 🟡 Enhancement opportunity
- N/A Not applicable

---

## Key Patterns to Adopt

### 1. **Subscription Management** 🔴 HIGH PRIORITY

**GitHub Pattern:**
```
/github subscribe owner/repo issues pulls commits releases
/github unsubscribe owner/repo commits
/github subscribe owner/repo issues +label:"bug" +label:"urgent"
```

**Proposed Odoo Pattern:**
```
/odoo subscribe expense.approval finance.invoice bir.deadline
/odoo unsubscribe finance.invoice
/odoo subscribe expense.approval +agency:"RIM" +amount:">50000"
```

**Implementation:**
```python
# New model: slack.subscription
class SlackSubscription(models.Model):
    _name = "slack.subscription"
    _description = "Slack Channel Subscription"

    channel_id = fields.Char(required=True)
    channel_name = fields.Char()
    user_id = fields.Many2one('res.users')  # Who subscribed

    # Subscription types
    subscription_type = fields.Selection([
        ('expense.approval', 'Expense Approvals'),
        ('expense.submission', 'Expense Submissions'),
        ('expense.payment', 'Expense Payments'),
        ('invoice.created', 'Invoice Created'),
        ('invoice.payment', 'Invoice Payment'),
        ('sale.order', 'Sale Orders'),
        ('ticket.created', 'Tickets Created'),
        ('ticket.closed', 'Tickets Closed'),
        ('bir.deadline', 'BIR Deadlines'),
        ('bank.reconciliation', 'Bank Reconciliation'),
    ])

    # Filters (JSONB)
    filters = fields.Json(string="Filters", help="""
    Examples:
    - {"agency": "RIM"}
    - {"amount_min": 50000}
    - {"severity": ["high", "critical"]}
    - {"labels": ["urgent", "bug"]}
    """)

    active = fields.Boolean(default=True)
    created_date = fields.Datetime(default=fields.Datetime.now)

    @api.model
    def process_subscription_command(self, channel_id, text, user_id):
        """Process /odoo subscribe or /odoo unsubscribe command

        Args:
            channel_id: Slack channel ID
            text: Command text (e.g., "subscribe expense.approval +agency:RIM")
            user_id: Slack user ID

        Returns:
            str: Response message
        """
        parts = text.split()
        action = parts[0]  # 'subscribe' or 'unsubscribe'

        if action == 'subscribe':
            return self._handle_subscribe(channel_id, parts[1:], user_id)
        elif action == 'unsubscribe':
            return self._handle_unsubscribe(channel_id, parts[1:], user_id)
        else:
            return "Usage: /odoo subscribe|unsubscribe [types] [+filters]"

    def _handle_subscribe(self, channel_id, args, user_id):
        """Create subscription with filters"""
        # Parse subscription types and filters
        types = [arg for arg in args if not arg.startswith('+')]
        filters = self._parse_filters([arg for arg in args if arg.startswith('+')])

        # Create subscriptions
        for sub_type in types:
            self.create({
                'channel_id': channel_id,
                'subscription_type': sub_type,
                'filters': filters,
                'user_id': user_id,
            })

        return f"✅ Subscribed to {', '.join(types)} in this channel"

    def _parse_filters(self, filter_args):
        """Parse +key:value filters into JSON

        Examples:
            ['+agency:RIM', '+amount:>50000']
            → {'agency': 'RIM', 'amount_min': 50000}
        """
        filters = {}
        for arg in filter_args:
            if ':' not in arg:
                continue
            key, value = arg[1:].split(':', 1)  # Remove '+' prefix

            # Handle comparison operators
            if value.startswith('>'):
                filters[f'{key}_min'] = float(value[1:])
            elif value.startswith('<'):
                filters[f'{key}_max'] = float(value[1:])
            else:
                filters[key] = value

        return filters

    @api.model
    def get_subscribed_channels(self, event_type, record):
        """Get channels subscribed to this event type with matching filters

        Args:
            event_type: e.g., 'expense.approval'
            record: The Odoo record that triggered the event

        Returns:
            list: List of channel IDs to notify
        """
        subscriptions = self.search([
            ('subscription_type', '=', event_type),
            ('active', '=', True)
        ])

        matching_channels = []
        for sub in subscriptions:
            if self._matches_filters(record, sub.filters):
                matching_channels.append(sub.channel_id)

        return matching_channels

    def _matches_filters(self, record, filters):
        """Check if record matches subscription filters"""
        if not filters:
            return True

        for key, value in filters.items():
            # Handle special keys
            if key.endswith('_min'):
                field = key[:-4]
                if record[field] < value:
                    return False
            elif key.endswith('_max'):
                field = key[:-4]
                if record[field] > value:
                    return False
            elif key == 'agency':
                if hasattr(record, 'agency_id') and record.agency_id.code != value:
                    return False
            elif key == 'severity':
                if hasattr(record, 'severity') and record.severity not in value:
                    return False
            # Add more filter types as needed

        return True
```

**Usage in notification logic:**
```python
# In slack_bridge/models/slack_bridge.py
def post_expense_notification(self, expense_id, action):
    expense = self.env['hr.expense'].browse(expense_id)

    # OLD: Static channel lookup
    # channel_id = self.env['slack.channel'].get_channel_for_agency(...)

    # NEW: Dynamic subscription lookup
    event_type = f'expense.{action}'
    channels = self.env['slack.subscription'].get_subscribed_channels(
        event_type=event_type,
        record=expense
    )

    # Post to all subscribed channels
    for channel_id in channels:
        self.post_message(channel_id, ...)
```

---

### 2. **Message Threading** 🔴 HIGH PRIORITY

**GitHub Pattern:**
```
Parent Message (Issue/PR card):
┌─────────────────────────────────────────┐
│ 🔵 #123 Bug in expense approval         │
│ Status: Open                            │
│ Assignee: @john                         │
│ Labels: bug, urgent                     │
│ [Close] [Comment] [Assign]              │
└─────────────────────────────────────────┘
  ↳ Thread Reply 1: "John commented: ..."
  ↳ Thread Reply 2: "Status changed to In Progress"
  ↳ Thread Reply 3: "Pull request #456 linked"
```

**Proposed Odoo Pattern:**
```
Parent Message (Expense/Ticket card):
┌─────────────────────────────────────────┐
│ 📝 EXP-001 Travel to Manila              │
│ Status: Pending Approval                │
│ Employee: Juan Dela Cruz                │
│ Amount: ₱12,500.00                      │
│ Agency: RIM                             │
│ [Approve] [Reject] [Comment]            │
└─────────────────────────────────────────┘
  ↳ Thread Reply 1: "Submitted for approval"
  ↳ Thread Reply 2: "Manager requested more info"
  ↳ Thread Reply 3: "✅ Approved by Jose Reyes"
```

**Implementation:**
```python
# New model: slack.thread
class SlackThread(models.Model):
    _name = "slack.thread"
    _description = "Slack Message Thread Tracking"

    channel_id = fields.Char(required=True)
    thread_ts = fields.Char(required=True, help="Slack thread timestamp (parent message)")

    # Link to Odoo record
    model = fields.Char(required=True, help="e.g., 'hr.expense'")
    res_id = fields.Integer(required=True, help="Record ID")

    # Parent message info
    parent_message_id = fields.Char(help="Slack message ID")
    parent_text = fields.Text(help="Parent message text")

    # Metadata
    created_date = fields.Datetime(default=fields.Datetime.now)
    last_updated = fields.Datetime()
    reply_count = fields.Integer(default=0)

    _sql_constraints = [
        ('unique_thread', 'UNIQUE(channel_id, model, res_id)',
         'Only one thread per record per channel')
    ]

    @api.model
    def get_or_create_thread(self, channel_id, model, res_id):
        """Get existing thread or create new parent message

        Args:
            channel_id: Slack channel ID
            model: Odoo model name (e.g., 'hr.expense')
            res_id: Record ID

        Returns:
            str: thread_ts (Slack thread timestamp)
        """
        thread = self.search([
            ('channel_id', '=', channel_id),
            ('model', '=', model),
            ('res_id', '=', res_id)
        ], limit=1)

        if thread:
            return thread.thread_ts

        # Create new parent message
        record = self.env[model].browse(res_id)
        parent_message = self._create_parent_card(channel_id, record)

        # Store thread
        thread = self.create({
            'channel_id': channel_id,
            'thread_ts': parent_message['ts'],
            'model': model,
            'res_id': res_id,
            'parent_message_id': parent_message['ts'],
            'parent_text': parent_message['text'],
        })

        return thread.thread_ts

    def _create_parent_card(self, channel_id, record):
        """Create rich parent message card for the record

        Args:
            channel_id: Slack channel ID
            record: Odoo record (expense, ticket, invoice, etc.)

        Returns:
            dict: Slack API response with 'ts' (timestamp)
        """
        # Build blocks based on record type
        blocks = self._build_record_card(record)

        # Post to Slack
        slack_api = self.env['slack.bridge']
        response = slack_api.post_message(
            channel=channel_id,
            text=f"{record._description}: {record.display_name}",
            blocks=blocks
        )

        return response

    def _build_record_card(self, record):
        """Build Slack block kit card for record"""
        if record._name == 'hr.expense':
            return self._build_expense_card(record)
        elif record._name == 'helpdesk.ticket':
            return self._build_ticket_card(record)
        elif record._name == 'account.move':
            return self._build_invoice_card(record)
        else:
            return self._build_generic_card(record)

    def _build_expense_card(self, expense):
        """Build expense card with action buttons"""
        status_emoji = {
            'draft': '📝',
            'reported': '📋',
            'approved': '✅',
            'done': '💰',
            'refused': '❌'
        }.get(expense.state, '📌')

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{status_emoji} {expense.name}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Employee:*\n{expense.employee_id.name}"},
                    {"type": "mrkdwn", "text": f"*Amount:*\n₱{expense.total_amount:,.2f}"},
                    {"type": "mrkdwn", "text": f"*Status:*\n{expense.state.title()}"},
                    {"type": "mrkdwn", "text": f"*Agency:*\n{expense.employee_id.agency_id.code or 'N/A'}"},
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{expense.name}"
                }
            },
            {
                "type": "divider"
            }
        ]

        # Add action buttons if pending approval
        if expense.state == 'reported':
            blocks.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "✅ Approve"},
                        "style": "primary",
                        "value": f"approve_{expense.id}",
                        "action_id": "expense_approve"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "❌ Reject"},
                        "style": "danger",
                        "value": f"reject_{expense.id}",
                        "action_id": "expense_reject"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "💬 Comment"},
                        "value": f"comment_{expense.id}",
                        "action_id": "expense_comment"
                    }
                ]
            })

        return blocks

    def post_thread_reply(self, text, update_parent=False):
        """Post a reply to this thread

        Args:
            text: Reply text
            update_parent: If True, also update parent card with new status
        """
        slack_api = self.env['slack.bridge']
        slack_api.post_message(
            channel=self.channel_id,
            text=text,
            thread_ts=self.thread_ts  # Reply to thread
        )

        self.write({
            'last_updated': fields.Datetime.now(),
            'reply_count': self.reply_count + 1
        })

        if update_parent:
            # Update parent card
            record = self.env[self.model].browse(self.res_id)
            new_blocks = self._build_record_card(record)
            slack_api.update_message(
                channel=self.channel_id,
                ts=self.parent_message_id,
                blocks=new_blocks
            )


# Usage in notification logic
def post_expense_notification(self, expense_id, action):
    expense = self.env['hr.expense'].browse(expense_id)

    # Get subscribed channels
    channels = self.env['slack.subscription'].get_subscribed_channels(
        event_type=f'expense.{action}',
        record=expense
    )

    for channel_id in channels:
        # Get or create thread
        thread = self.env['slack.thread'].get_or_create_thread(
            channel_id=channel_id,
            model='hr.expense',
            res_id=expense.id
        )

        # Post update as thread reply
        message = self._format_expense_update(expense, action)

        self.env['slack.thread'].search([
            ('channel_id', '=', channel_id),
            ('model', '=', 'hr.expense'),
            ('res_id', '=', expense.id)
        ]).post_thread_reply(
            text=message,
            update_parent=True  # Update parent card with new status
        )
```

---

### 3. **Interactive Actions** 🔴 HIGH PRIORITY

**GitHub Pattern:**
- Close/reopen issues from Slack buttons
- Approve/comment on PRs
- Assign labels and users
- Rerun workflows

**Proposed Odoo Pattern:**
- Approve/reject expenses from Slack buttons
- Comment on tickets
- Assign tickets to users
- Change status of records

**Implementation:**
```python
# New controller for Slack interactive actions
# In slack_bridge/controllers/slack.py

@http.route('/slack/interactive', type='http', auth='public', csrf=False, methods=['POST'])
def slack_interactive(self, **kwargs):
    """Handle Slack interactive actions (button clicks, modals, etc.)

    Slack sends interactive payloads to this endpoint when users click buttons
    """
    # Parse payload
    payload = json.loads(request.params.get('payload', '{}'))

    # Verify signature
    if not self._verify_slack_signature():
        return Response('Unauthorized', status=403)

    # Extract action info
    action_id = payload['actions'][0]['action_id']
    action_value = payload['actions'][0]['value']
    user_id = payload['user']['id']
    channel_id = payload['channel']['id']
    message_ts = payload['message']['ts']

    # Route to handler
    if action_id == 'expense_approve':
        return self._handle_expense_approve(action_value, user_id, channel_id, message_ts)
    elif action_id == 'expense_reject':
        return self._handle_expense_reject(action_value, user_id, channel_id, message_ts)
    elif action_id == 'expense_comment':
        return self._handle_expense_comment(action_value, user_id, channel_id, message_ts)
    elif action_id == 'ticket_assign':
        return self._handle_ticket_assign(action_value, user_id, channel_id, message_ts)
    # ... more handlers

    return Response('Action not supported', status=400)

def _handle_expense_approve(self, action_value, user_id, channel_id, message_ts):
    """Handle expense approval from Slack button

    Args:
        action_value: e.g., "approve_123" where 123 is expense ID
        user_id: Slack user ID who clicked button
        channel_id: Slack channel ID
        message_ts: Message timestamp

    Returns:
        Response: Updated message or error
    """
    # Extract expense ID
    expense_id = int(action_value.split('_')[1])

    # Get Odoo user from Slack user
    odoo_user = self._get_odoo_user_from_slack(user_id)
    if not odoo_user:
        return self._respond_ephemeral("❌ Your Slack account is not linked to Odoo")

    # Approve expense
    expense = request.env['hr.expense'].sudo(odoo_user.id).browse(expense_id)

    if not expense.exists():
        return self._respond_ephemeral("❌ Expense not found")

    # Check permissions
    if not expense.check_access_rights('write', raise_exception=False):
        return self._respond_ephemeral("❌ You don't have permission to approve expenses")

    try:
        expense.action_approve()

        # Update thread
        thread = request.env['slack.thread'].search([
            ('channel_id', '=', channel_id),
            ('model', '=', 'hr.expense'),
            ('res_id', '=', expense_id)
        ], limit=1)

        if thread:
            thread.post_thread_reply(
                text=f"✅ Approved by <@{user_id}>",
                update_parent=True
            )

        return self._respond_success("✅ Expense approved!")

    except Exception as e:
        _logger.error(f"Error approving expense: {str(e)}")
        return self._respond_ephemeral(f"❌ Error: {str(e)}")

def _get_odoo_user_from_slack(self, slack_user_id):
    """Map Slack user to Odoo user

    This requires a new mapping table or using email matching
    """
    # Option 1: Mapping table
    mapping = request.env['slack.user.mapping'].sudo().search([
        ('slack_user_id', '=', slack_user_id)
    ], limit=1)

    if mapping:
        return mapping.odoo_user_id

    # Option 2: Get Slack user email and match
    slack_api = request.env['slack.bridge']
    user_info = slack_api.get_user_info(slack_user_id)
    email = user_info.get('profile', {}).get('email')

    if email:
        user = request.env['res.users'].sudo().search([
            ('email', '=', email)
        ], limit=1)

        if user:
            # Create mapping for future
            request.env['slack.user.mapping'].sudo().create({
                'slack_user_id': slack_user_id,
                'odoo_user_id': user.id,
            })
            return user

    return None

def _respond_ephemeral(self, text):
    """Send ephemeral response (only visible to user who clicked)"""
    return Response(
        json.dumps({
            "response_type": "ephemeral",
            "text": text
        }),
        content_type='application/json'
    )

def _respond_success(self, text):
    """Send in-channel response (visible to everyone)"""
    return Response(
        json.dumps({
            "response_type": "in_channel",
            "text": text
        }),
        content_type='application/json'
    )
```

**New Model: Slack User Mapping**
```python
class SlackUserMapping(models.Model):
    _name = "slack.user.mapping"
    _description = "Slack to Odoo User Mapping"

    slack_user_id = fields.Char(required=True, index=True)
    slack_user_name = fields.Char()
    slack_email = fields.Char()
    odoo_user_id = fields.Many2one('res.users', required=True)

    _sql_constraints = [
        ('unique_slack_user', 'UNIQUE(slack_user_id)',
         'Slack user already mapped!')
    ]
```

---

### 4. **User Mentions** 🔴 HIGH PRIORITY

**GitHub Pattern:**
```
Notification: "@john you've been assigned to issue #123"
Notification: "@sarah requested your review on PR #456"
```

**Proposed Odoo Pattern:**
```
Notification: "<@U123456> you've been assigned to ticket TKT-001"
Notification: "<@U789012> your expense EXP-001 has been approved"
```

**Implementation:**
```python
def _get_slack_user_mention(self, odoo_user):
    """Get Slack mention string for Odoo user

    Args:
        odoo_user: res.users record

    Returns:
        str: "<@U123456>" or user name if not found
    """
    mapping = self.env['slack.user.mapping'].search([
        ('odoo_user_id', '=', odoo_user.id)
    ], limit=1)

    if mapping:
        return f"<@{mapping.slack_user_id}>"
    else:
        return odoo_user.name

# Usage in notifications
def post_expense_notification(self, expense_id, action):
    expense = self.env['hr.expense'].browse(expense_id)

    # Mention relevant users
    if action == 'submitted':
        # Mention manager
        manager_mention = self._get_slack_user_mention(expense.employee_id.parent_id.user_id)
        text = f"📝 {expense.employee_id.name} submitted expense {expense.name} for your review, {manager_mention}"

    elif action == 'approved':
        # Mention employee
        employee_mention = self._get_slack_user_mention(expense.employee_id.user_id)
        text = f"✅ {employee_mention} your expense {expense.name} has been approved!"

    elif action == 'rejected':
        # Mention employee
        employee_mention = self._get_slack_user_mention(expense.employee_id.user_id)
        text = f"❌ {employee_mention} your expense {expense.name} was rejected"

    # Post to channel...
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2) 🔴 HIGH PRIORITY

**Tasks:**
1. Create `slack.subscription` model
2. Implement `/odoo subscribe` and `/odoo unsubscribe` commands
3. Update notification logic to use subscriptions
4. Add basic filter support (+agency, +amount)
5. Test subscription workflow end-to-end

**Deliverables:**
- Users can subscribe to events from Slack
- Notifications only go to subscribed channels
- Basic filtering works

---

### Phase 2: Threading (Week 3-4) 🔴 HIGH PRIORITY

**Tasks:**
1. Create `slack.thread` model
2. Implement parent card creation
3. Update notifications to use threading
4. Build expense, ticket, invoice card templates
5. Add thread reply logic
6. Test thread updates

**Deliverables:**
- One parent message per record
- Updates appear as thread replies
- Parent card updates with status changes
- Reduced channel noise

---

### Phase 3: Interactive Actions (Week 5-6) 🔴 HIGH PRIORITY

**Tasks:**
1. Set up `/slack/interactive` endpoint
2. Create `slack.user.mapping` model
3. Implement expense approve/reject buttons
4. Add comment modal
5. Handle permission checks
6. Test interactive workflows

**Deliverables:**
- Approve/reject expenses from Slack
- Comment on records from Slack
- Proper permission enforcement
- User mapping system

---

### Phase 4: User Mentions (Week 7) 🟡 MEDIUM PRIORITY

**Tasks:**
1. Build user mention helper
2. Update all notifications to mention relevant users
3. Add assignment notifications
4. Test mention accuracy

**Deliverables:**
- Assignees get mentioned
- Submitters get mentioned
- Approvers get mentioned
- Mentions work across agencies

---

### Phase 5: Advanced Features (Week 8+) 🟡 MEDIUM PRIORITY

**Tasks:**
1. Scheduled reminders (pending approvals)
2. Link unfurling for Odoo URLs
3. Per-channel threading settings
4. Create record from Slack message (context menu)
5. Analytics dashboard

**Deliverables:**
- Daily reminder for pending approvals
- Rich previews of Odoo links
- User can toggle threading per channel
- Create expense/ticket from Slack
- Slack usage metrics in Superset

---

## Quick Wins

These can be implemented immediately with minimal effort:

### 1. Add Emoji to Status Messages
```python
STATUS_EMOJI = {
    'draft': '📝',
    'submitted': '📋',
    'approved': '✅',
    'paid': '💰',
    'rejected': '❌',
    'cancelled': '🚫',
}

def post_expense_notification(self, expense_id, action):
    expense = self.env['hr.expense'].browse(expense_id)
    emoji = STATUS_EMOJI.get(expense.state, '📌')
    text = f"{emoji} Expense {expense.name} {action}"
    # ...
```

### 2. Add View in Odoo Link
```python
def _get_odoo_url(self, record):
    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
    return f"{base_url}/web#id={record.id}&model={record._name}&view_type=form"

# In notification:
text = f"View in Odoo: {self._get_odoo_url(expense)}"
```

### 3. Add Formatted Amounts
```python
def _format_currency(self, amount, currency='PHP'):
    symbol = {'PHP': '₱', 'USD': '$', 'EUR': '€'}.get(currency, '')
    return f"{symbol}{amount:,.2f}"

# Usage:
text = f"Amount: {self._format_currency(expense.total_amount)}"
```

---

## Testing Plan

### Unit Tests
```python
# tests/test_slack_subscription.py
class TestSlackSubscription(TransactionCase):
    def test_subscribe_command(self):
        """Test /odoo subscribe command"""
        result = self.env['slack.subscription'].process_subscription_command(
            channel_id='C123',
            text='subscribe expense.approval +agency:RIM',
            user_id='U456'
        )
        self.assertIn('Subscribed', result)

        # Check subscription created
        sub = self.env['slack.subscription'].search([
            ('channel_id', '=', 'C123'),
            ('subscription_type', '=', 'expense.approval')
        ])
        self.assertTrue(sub)
        self.assertEqual(sub.filters['agency'], 'RIM')

    def test_filter_matching(self):
        """Test filter matching logic"""
        sub = self.env['slack.subscription'].create({
            'channel_id': 'C123',
            'subscription_type': 'expense.approval',
            'filters': {'agency': 'RIM', 'amount_min': 10000}
        })

        # Matching expense
        expense1 = self.env['hr.expense'].create({
            'name': 'Test Expense',
            'employee_id': self.employee_rim.id,  # RIM employee
            'total_amount': 15000,
        })
        self.assertTrue(sub._matches_filters(expense1, sub.filters))

        # Non-matching expense (wrong agency)
        expense2 = self.env['hr.expense'].create({
            'name': 'Test Expense 2',
            'employee_id': self.employee_ckvc.id,  # CKVC employee
            'total_amount': 15000,
        })
        self.assertFalse(sub._matches_filters(expense2, sub.filters))
```

### Integration Tests
```python
# tests/test_slack_threading.py
class TestSlackThreading(TransactionCase):
    def test_thread_creation(self):
        """Test thread creation and updates"""
        expense = self.env['hr.expense'].create({...})

        # First notification creates thread
        thread_ts = self.env['slack.thread'].get_or_create_thread(
            channel_id='C123',
            model='hr.expense',
            res_id=expense.id
        )
        self.assertTrue(thread_ts)

        # Second notification reuses thread
        thread_ts2 = self.env['slack.thread'].get_or_create_thread(
            channel_id='C123',
            model='hr.expense',
            res_id=expense.id
        )
        self.assertEqual(thread_ts, thread_ts2)
```

---

## Metrics & Success Criteria

**Week 4 Goals:**
- [ ] 80% of notifications use threading
- [ ] 50% of channels using subscriptions
- [ ] <100ms subscription lookup time
- [ ] Zero duplicate parent cards

**Week 8 Goals:**
- [ ] 50% of approvals done from Slack
- [ ] 90% user mention accuracy
- [ ] <200ms interactive action response
- [ ] 10+ subscription filters in use

**Analytics to Track:**
- Subscription adoption rate
- Thread usage vs. flat messages
- Interactive action success rate
- User mention accuracy
- Notification delivery time
- Channel noise reduction (messages/day before/after)

---

## Next Steps

1. **Review this document** with the team
2. **Prioritize features** based on user feedback
3. **Create Jira/GitHub issues** for Phase 1 tasks
4. **Set up development environment** for testing Slack interactions
5. **Start with subscription model** (highest impact, foundational)

---

## Resources

- **GitHub Slack Integration**: https://github.com/integrations/slack
- **Slack Block Kit Builder**: https://app.slack.com/block-kit-builder
- **Slack API Docs**: https://api.slack.com/
- **Our Current Implementation**:
  - `addons/slack_bridge/`
  - `docs/SLACK_TO_ODOO_MAPPING.md`
  - `docs/SLACK_QUICK_START.md`

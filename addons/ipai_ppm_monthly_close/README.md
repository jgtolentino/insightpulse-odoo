# PPM Monthly Close Scheduler

Automated monthly financial close scheduling with PPM and Notion workspace parity.

## Overview

This module implements a **recurring monthly close workflow** based on your requirements:

- **Start Date**: 3rd business day before month-end (S = C - 3 working days)
- **Review Window**: S + 1 working day (AM)
- **Approval Window**: S + 1 working day (EOD)
- **Recurrence**: Every month, automatically created by cron

### Example for November 2025

- **Month End (C)**: Friday, 28 Nov 2025 (last business day)
- **Prep Start (S)**: Monday, 24 Nov 2025 (C - 3 business days)
- **Review Due**: Tuesday, 25 Nov 2025 AM
- **Approval Due**: Tuesday, 25 Nov 2025 EOD

## Architecture

### Data Models

```
ppm.monthly.close
├── close_month (Date)
├── month_end_date (computed)
├── prep_start_date (computed: C - 3 business days)
├── review_due_date (computed: S + 1 business day)
├── approval_due_date (computed: S + 1 business day EOD)
└── task_ids (One2many → ppm.close.task)

ppm.close.task
├── monthly_close_id (Many2one)
├── template_id (Many2one → ppm.close.template)
├── owner_code, reviewer_code, approver_code
├── state: todo → in_progress → for_review → for_approval → done
└── Completion tracking (prep/review/approval dates + users)

ppm.close.template
├── task_category
├── detailed_task
├── agency_code, owner_code, reviewer_code, approver_code
└── prep_days, review_days, approval_days
```

### Business Day Logic

The module implements sophisticated business day calculations:

```python
# Find last business day of month
C = get_previous_business_day(last_day_of_month)

# Calculate prep start (3 business days before C)
S = subtract_business_days(C, 3)

# Review and approval dates
review_due = add_business_days(S, 1)
approval_due = add_business_days(S, 1)  # Same day, EOD
```

**Excluded Days**: Weekends (Saturday, Sunday)
**TODO**: Integration with `resource.calendar` for Philippine holidays

## Installation

### Prerequisites

```bash
# Install Odoo CE 18.0
sudo apt install odoo
```

### Install Module

```bash
# Navigate to addons directory
cd /opt/odoo-ce/addons

# Copy module
cp -r /path/to/ipai_ppm_monthly_close .

# Restart Odoo
sudo systemctl restart odoo

# Install via UI
# Apps → Update Apps List → Search "PPM Monthly Close" → Install
```

### Initial Configuration

1. **Configure Templates** (`Monthly Close → Templates`):
   - 10 sample templates are pre-loaded from your closing sheet
   - Customize owner/reviewer/approver codes to match your employee IDs
   - Add/remove templates as needed

2. **Enable Cron Jobs** (automatic):
   - `Create Next Month's Close Schedule` - Runs daily at 2 AM
   - `Send Daily Task Reminders` - Runs daily at 8 AM

3. **Create First Schedule** (manual for testing):
   ```
   Monthly Close → Close Schedules → Create
   Close Month: November 2025
   → Click "Generate Tasks"
   → Click "Start Close Process"
   ```

## Usage

### For Task Owners

1. **Receive Notification**: Email/n8n notification on prep start date (24 Nov)
2. **Start Preparation**: Open task → Click "Start Prep"
3. **Complete Work**: Perform closing activities
4. **Submit for Review**: Click "Submit for Review" when done

### For Reviewers

1. **Receive Notification**: When task submitted for review
2. **Review Work**: Verify completeness and accuracy
3. **Action**:
   - **Approve**: Click "Submit for Approval"
   - **Reject**: Click "Reject" (returns to owner)

### For Approvers

1. **Receive Notification**: When task submitted for approval
2. **Final Review**: Validate all requirements met
3. **Action**:
   - **Approve**: Click "Approve" (marks task as done)
   - **Reject**: Click "Reject" (returns to owner)

### For Finance Managers

**Dashboard View** (`Monthly Close → Close Schedules`):
- See all close schedules (past, current, future)
- Track progress percentage
- Gantt view for timeline visualization
- Calendar view for scheduling

**Operations**:
- **Generate Tasks**: Create tasks from templates
- **Start Close**: Send notifications to all owners
- **Complete Close**: Mark entire close as done (all tasks must be complete)

## Automation

### Cron Jobs

**1. Create Monthly Close Schedule** (Daily 2 AM)
```python
# Auto-creates next month's schedule 3 days before month-end
model.cron_create_monthly_close()
```

**2. Send Daily Reminders** (Daily 8 AM)
```python
# Sends reminders based on current date:
# - Tasks in 'todo' state on prep_start date → notify owners
# - Tasks in 'for_review' state on review_due date → notify reviewers
# - Tasks in 'for_approval' state on approval_due date → notify approvers
model.cron_send_daily_reminders()
```

### n8n Integration

**Workflow**: `ppm_monthly_close_automation.json`

```
Daily 8 AM Trigger
└→ Call Odoo Daily Reminders (Odoo JSON-RPC)
   └→ Notify Mattermost (Success confirmation)
```

**To Install**:
```bash
# Import workflow to n8n
curl -X POST "https://ipa.insightpulseai.net/api/v1/workflows" \
  -H "X-N8N-API-KEY: $N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d @automations/n8n/workflows/ppm_monthly_close_automation.json
```

## Clarity PPM Parity

This module provides **Clarity PPM-equivalent functionality**:

| Clarity PPM Feature | Odoo Implementation |
|---------------------|---------------------|
| Project Templates | `ppm.close.template` |
| Work Breakdown Structure | `ppm.close.task` with sequence |
| Resource Assignment | owner_code, reviewer_code, approver_code |
| Gantt Scheduling | Gantt view with computed dates |
| Workflow Gates | State transitions (todo → in_progress → for_review → for_approval → done) |
| Effort Tracking | prep_days, review_days, approval_days |
| Status Reporting | Progress percentage, task statistics |
| Recurring Projects | Monthly cron auto-creation |

### Clarity Mapping

**Clarity Concept** → **Odoo Equivalent**
- Portfolio → Multi-agency consolidation
- Program → Monthly close schedule
- Project → Individual closing task
- Task → Subtask (detailed_task field)
- Resource → Employee codes
- Milestone → State transitions
- Gantt → Native Odoo Gantt view

## Notion Workspace Parity

Provides **Notion-equivalent database functionality**:

| Notion Feature | Odoo Implementation |
|----------------|---------------------|
| Database | `ppm.close.task` model |
| Properties | Fields (owner_code, reviewer_code, etc.) |
| Relations | Many2one to monthly_close_id |
| Rollups | Computed fields (progress_percentage, task_count) |
| Formula | Business day calculations |
| Timeline View | Calendar and Gantt views |
| Kanban Board | Tree view with state grouping |
| Automation | Odoo cron + n8n workflows |

## Recurrence Rule Implementation

**Formal Specification**:
```
Given:
  M = target month (e.g., November 2025)

Compute:
  1. C = last_business_day(last_day_of(M))
  2. S = subtract_business_days(C, 3)
  3. R = add_business_days(S, 1)  # Review due
  4. A = R  # Approval due (same day, EOD)

Create:
  Schedule with:
    - prep_start_date = S
    - review_due_date = R
    - approval_due_date = A
    - Tasks from active templates
```

**Pseudo-RRULE**:
```
FREQ=MONTHLY
INTERVAL=1
BYDAY=3BD_BEFORE_MONTH_END
ACTION=CREATE_SCHEDULE_AND_TASKS
```

## Multi-Agency Support

Supports **8 agencies** from your setup:

1. **RIM** - Primary consolidation agency
2. **CKVC** - Accounts payable focus
3. **BOM** - Payroll processing
4. **JPAL** - Revenue recognition
5. **JLI** - Bank reconciliation
6. **JAP** - Fixed assets
7. **LAS** - Inventory count
8. **RMQB** - Expense accruals

**Cross-Agency Tasks**:
- Consolidated reporting (all 8 agencies)
- BIR compliance (centralized)

## Notifications

### Odoo Native (TODO)

```python
# In action_notify_owner()
self.activity_schedule(
    'mail.mail_activity_data_todo',
    user_id=user.id,
    summary=f"Monthly Close Task: {self.name}"
)
```

### n8n Webhook (Implemented)

```python
# Call n8n webhook
requests.post(
    f"{N8N_BASE_URL}/webhook/monthly-close-notify",
    json={
        "task_id": self.id,
        "task_name": self.name,
        "recipient": self.owner_code,
        "type": "owner_notification"
    }
)
```

### Mattermost (via n8n)

```
n8n receives webhook
└→ Format message
   └→ POST to Mattermost channel
      Text: "[@owner_code] Task ready: {task_name}"
```

## Testing

### November 2025 Test Scenario

```python
# Create schedule for November 2025
close = env['ppm.monthly.close'].create({
    'close_month': '2025-11-01'
})

# Expected computed dates:
# - close_month: 2025-11-01 (stored as first day)
# - month_end_date: 2025-11-28 (last business day - Friday)
# - prep_start_date: 2025-11-24 (Monday, C - 3 business days)
# - review_due_date: 2025-11-25 (Tuesday AM)
# - approval_due_date: 2025-11-25 (Tuesday EOD)

# Generate tasks
close.action_generate_tasks()
# → Creates 10 tasks from templates

# Start process
close.action_start_close()
# → Sends notifications to all owners

# Verify
assert len(close.task_ids) == 10
assert close.state == 'in_progress'
```

### Cron Test

```bash
# Manually trigger cron
odoo-bin shell -d production
>>> env['ppm.monthly.close'].cron_create_monthly_close()
# Should create schedule for next month if S date is today
```

## Troubleshooting

### Tasks Not Generated

**Symptom**: Click "Generate Tasks" but no tasks created

**Solutions**:
1. Check templates exist: `Monthly Close → Templates`
2. Verify templates are active: `active = True`
3. Check logs: `grep "Generated.*tasks" /var/log/odoo/odoo.log`

### Cron Not Running

**Symptom**: Schedules not auto-created

**Solutions**:
1. Verify cron active: `Settings → Technical → Scheduled Actions`
2. Check cron logs: `grep "cron_create_monthly_close" /var/log/odoo/odoo.log`
3. Manually trigger: Scheduled Actions → "Create Next Month's Close Schedule" → Run

### Wrong Dates Calculated

**Symptom**: prep_start_date not 3 business days before month-end

**Solutions**:
1. Verify business day logic excludes weekends only
2. TODO: Add Philippine holiday calendar integration
3. Check logs for date calculations

## Roadmap

### Version 1.1.0 (Planned)

- [ ] Philippine holiday calendar integration via `resource.calendar`
- [ ] Email notifications (in addition to n8n)
- [ ] Mobile-responsive Gantt view
- [ ] Task dependency management (task A must complete before task B)
- [ ] Historical analytics dashboard

### Version 1.2.0 (Planned)

- [ ] Integration with BIR e-filing (1601-C, 2550Q)
- [ ] Automated consolidation reporting
- [ ] Budget vs. actual variance analysis
- [ ] AI-powered task duration prediction

## Support

**Documentation**: This README
**Issues**: GitHub Issues (jgtolentino/odoo-ce)
**Contact**: jgtolentino_rn@yahoo.com

## License

LGPL-3 (Odoo Community License)

## Credits

**Author**: InsightPulse AI
**Maintainer**: Jake Tolentino
**Framework**: Agent Skills Architecture v1.0
**Inspiration**: Clarity PPM + Notion Workspace

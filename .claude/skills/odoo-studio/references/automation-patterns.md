# Odoo Studio Automation Patterns

Complete guide to automated actions in Odoo Studio based on https://www.odoo.com/documentation/19.0/applications/studio/automated_actions.html

---

## What Are Automated Actions?

**Automated Actions** are rules that automatically trigger when specific conditions are met. They eliminate manual, repetitive tasks by executing actions in response to record changes.

**Common Use Cases:**
- Send email notifications when invoice is created
- Auto-assign tasks when status changes
- Create follow-up activities on deal closure
- Update related records when field changes
- Send webhooks to external systems
- Execute custom Python code

---

## Trigger Types

### 1. On Creation
**When:** New record is created
**Use Cases:**
- Send welcome email to new customer
- Create default tasks for new project
- Notify team when new lead arrives
- Set default values on creation

**Example:** "When new expense created, assign to employee's manager"

### 2. On Update
**When:** Existing record is modified
**Use Cases:**
- Send notification when status changes
- Update related records
- Log changes to audit trail
- Trigger approval workflow

**Example:** "When invoice status → Paid, send payment confirmation email"

### 3. On Creation & Update
**When:** Record created OR modified
**Use Cases:**
- Keep related records synchronized
- Validate data on save
- Update computed fields
- Trigger external webhooks

**Example:** "When customer address changes, update all related invoices"

### 4. On Deletion
**When:** Before record is deleted
**Use Cases:**
- Archive related records
- Send deletion notification
- Prevent deletion if conditions met
- Clean up related data

**Example:** "When project deleted, archive all related tasks"

### 5. Based on Form Modification
**When:** Specific field changes in form view
**Use Cases:**
- Field-level triggers
- Conditional field updates
- Real-time validations
- Dynamic form behavior

**Example:** "When priority field changes to 'High', notify manager immediately"

**Advantages:**
- Faster than "On Update" (no database write required)
- Immediate user feedback
- Can prevent form save

**Limitations:**
- Only works in form view (not API/imports)
- Limited to single field changes

### 6. Based on Timed Condition
**When:** Scheduled execution (cron-based)
**Use Cases:**
- Daily/weekly/monthly tasks
- Deadline reminders
- Recurring workflows
- Cleanup operations

**Example:** "Every day, send reminder for invoices due in 3 days"

**Configuration:**
- Trigger Date: Field to check (e.g., `invoice_date_due`)
- Delay: When to trigger (-3 days, +1 week, etc.)
- Repeat: How often to check (every X minutes/hours)

---

## Conditions (Filters)

Automated actions can be filtered to apply only to specific records using **domain filters**.

### Domain Examples

#### Simple Conditions

```python
# Only draft records
[('state', '=', 'draft')]

# Amount greater than 1000
[('amount', '>', 1000)]

# Active records only
[('active', '=', True)]

# Specific user
[('user_id', '=', user.id)]
```

#### Combined Conditions (AND)

```python
# High priority AND assigned to me
[
    ('priority', '=', '3'),
    ('user_id', '=', user.id)
]

# Invoices overdue AND not paid
[
    ('invoice_date_due', '<', today),
    ('payment_state', '!=', 'paid')
]
```

#### Multiple Options (OR)

```python
# Status is approved OR done
['|',
    ('state', '=', 'approved'),
    ('state', '=', 'done')
]

# Priority is high OR urgent
['|',
    ('priority', '=', 'high'),
    ('priority', '=', 'urgent')
]
```

#### Complex Logic (AND + OR)

```python
# (High priority OR urgent) AND (assigned to me)
['&',
    '|',
        ('priority', '=', 'high'),
        ('priority', '=', 'urgent'),
    ('user_id', '=', user.id)
]
```

#### Relational Fields

```python
# Customer is from specific country
[('partner_id.country_id.code', '=', 'PH')]

# Project manager is specific user
[('project_id.user_id', '=', 5)]

# Invoice company is active
[('company_id.active', '=', True)]
```

#### Date Comparisons

```python
# Due in next 3 days
[('deadline', '<=', (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'))]

# Created this month
[('create_date', '>=', (datetime.now().replace(day=1)).strftime('%Y-%m-%d'))]
```

---

## Actions

### 1. Execute Python Code

**Purpose:** Run custom logic (requires Developer Mode)

**Available Variables:**
- `env`: Odoo environment
- `model`: Current model
- `record` / `records`: Triggering record(s)
- `log(message, level='info')`: Log function
- `Warning`: Exception class

**Examples:**

```python
# Update field based on calculation
for rec in records:
    rec.total = rec.subtotal * 1.12

# Create related record
for rec in records:
    env['project.task'].create({
        'name': f'Follow up: {rec.name}',
        'project_id': rec.project_id.id,
        'user_id': rec.user_id.id,
    })

# Send notification
for rec in records:
    rec.message_post(
        body=f'Status changed to {rec.state}',
        message_type='notification',
        subtype_xmlid='mail.mt_note'
    )

# Raise warning (prevent action)
for rec in records:
    if rec.amount > 10000 and not rec.manager_approval:
        raise Warning('Manager approval required for amounts over $10,000')
```

### 2. Create New Record

**Purpose:** Auto-create related records

**Configuration:**
- Target Model: Which model to create
- Field Mappings: Values from source → target

**Example Use Cases:**
- Create task when project created
- Create invoice when SO confirmed
- Create follow-up activity

**Field Mapping:**
```
Source Field → Target Field
name → subject
user_id → user_id
date_deadline → date_deadline
```

### 3. Update the Record

**Purpose:** Modify triggering record fields

**Configuration:**
- Field: Which field to update
- Value: New value (static or computed)

**Examples:**
- Set `state` = 'approved'
- Set `user_id` = Current user's manager
- Set `date_approved` = Today
- Clear `partner_id` (set to empty)

### 4. Execute Multiple Actions

**Purpose:** Run several actions in sequence

**Example Workflow:**
1. Update record (set status)
2. Send email notification
3. Create activity
4. Add follower

### 5. Send Email

**Purpose:** Send email using template

**Configuration:**
- Email Template: Choose from templates
- Recipients: To/CC/BCC
- Dynamic content via placeholders

**Email Template Variables:**
```
${object.name} - Record name
${object.user_id.name} - Assigned user
${object.partner_id.email} - Customer email
${object.amount_total} - Total amount
```

**Example:** "When invoice paid, send thank-you email to customer"

### 6. Add Followers

**Purpose:** Subscribe users to record (for notifications)

**Configuration:**
- User/Partner to follow
- Can be static or computed

**Example:** "When deal reaches $10k, add sales manager as follower"

### 7. Create Next Activity

**Purpose:** Schedule task/call/meeting

**Configuration:**
- Activity Type: Task, Call, Meeting, Email
- Summary: Activity title
- Due Date: Relative or fixed
- Assigned To: User
- Note: Additional details

**Example:** "When lead status → Qualified, create 'Call customer' activity in 2 days"

### 8. Send SMS Text Message

**Purpose:** Send SMS to contact

**Requirements:**
- SMS provider configured
- Phone number field on record

**Example:** "When delivery scheduled, send SMS to customer with ETA"

### 9. Send Webhook / API Call

**Purpose:** POST data to external URL

**Configuration:**
- Target URL: External endpoint
- Payload: JSON data to send
- Headers: Authentication, content-type

**Example Payload:**
```json
{
    "event": "invoice_paid",
    "invoice_id": "${object.id}",
    "amount": "${object.amount_total}",
    "customer": "${object.partner_id.name}",
    "timestamp": "${datetime.now().isoformat()}"
}
```

**Use Cases:**
- Sync to external CRM
- Trigger Zapier workflow
- Update BI dashboard
- Send to message queue

---

## Common Automation Patterns

### Pattern 1: Status Change Notification

**Scenario:** Notify team when status changes

```
Trigger: On Update
Filter: [('state', '=', 'approved')]
Action: Send Email
Template: "Status Changed to Approved"
Recipients: object.user_id (assigned user)
```

### Pattern 2: Auto-Assignment

**Scenario:** Assign record to manager when amount exceeds threshold

```
Trigger: On Creation & Update
Filter: [('amount', '>', 1000)]
Action: Update Record
Field: manager_id
Value: record.user_id.parent_id (user's manager)
```

### Pattern 3: Create Follow-Up Task

**Scenario:** Create task when deal is won

```
Trigger: On Update
Filter: [('stage_id.is_won', '=', True)]
Action: Create New Record
Target Model: project.task
Mappings:
  - name → "Follow up: " + object.name
  - user_id → object.user_id
  - date_deadline → (now + 7 days)
```

### Pattern 4: Deadline Reminder

**Scenario:** Send reminder 3 days before deadline

```
Trigger: Based on Timed Condition
Trigger Date: date_deadline
Delay: -3 days
Repeat: Every 1 hour
Filter: [('state', '!=', 'done')]
Action: Create Activity
Activity Type: Reminder
Summary: "Deadline approaching: ${object.name}"
Assigned To: object.user_id
```

### Pattern 5: Approval Workflow

**Scenario:** Multi-level approval for expenses

```
Automation 1: Request Approval
Trigger: On Update
Filter: [('state', '=', 'submit')]
Action: Update Record + Send Email
  - Set state = 'pending_approval'
  - Send email to manager

Automation 2: Auto-Approve Small Amounts
Trigger: On Update
Filter: [('state', '=', 'submit'), ('amount', '<', 500)]
Action: Update Record
  - Set state = 'approved'
  - Set approved_by = manager
```

### Pattern 6: Data Synchronization

**Scenario:** Keep address synchronized across records

```
Trigger: On Update
Filter: [('partner_id', '!=', False)]
Action: Execute Python Code

# Copy partner address to record
for rec in records:
    rec.street = rec.partner_id.street
    rec.city = rec.partner_id.city
    rec.zip = rec.partner_id.zip
    rec.country_id = rec.partner_id.country_id
```

### Pattern 7: External Integration

**Scenario:** Send invoice data to external accounting system

```
Trigger: On Update
Filter: [('state', '=', 'posted')]
Action: Send Webhook
URL: https://api.external-system.com/invoices
Payload:
{
  "invoice_number": "${object.name}",
  "date": "${object.invoice_date}",
  "amount": ${object.amount_total},
  "customer_id": "${object.partner_id.ref}"
}
Headers:
  Authorization: Bearer YOUR_API_KEY
  Content-Type: application/json
```

### Pattern 8: Prevent Invalid Operations

**Scenario:** Block deletion if record has dependencies

```
Trigger: On Deletion
Filter: [('invoice_count', '>', 0)]
Action: Execute Python Code

raise Warning('Cannot delete sales order with existing invoices')
```

### Pattern 9: Batch Processing

**Scenario:** Nightly cleanup of old records

```
Trigger: Based on Timed Condition
Trigger Date: create_date
Delay: +30 days
Repeat: Every 24 hours
Filter: [('state', '=', 'cancelled')]
Action: Execute Python Code

# Archive old cancelled records
for rec in records:
    rec.active = False
```

### Pattern 10: Dynamic Field Updates

**Scenario:** Calculate shipping cost based on weight

```
Trigger: Based on Form Modification
Field: product_id
Action: Execute Python Code

for rec in records:
    total_weight = sum(rec.order_line.mapped('product_id.weight'))
    if total_weight < 5:
        rec.shipping_cost = 10
    elif total_weight < 20:
        rec.shipping_cost = 25
    else:
        rec.shipping_cost = 50
```

---

## Best Practices

### ✅ Do's

1. **Keep logic simple** - Complex workflows should be in Python code
2. **Test thoroughly** - Always test on staging first
3. **Use specific filters** - Avoid triggering on all records
4. **Document purpose** - Add description to automation
5. **Monitor execution** - Check logs for errors
6. **Use form modification** - For immediate user feedback
7. **Batch similar actions** - Reduce number of automations
8. **Handle errors** - Use try/except in Python code

### ❌ Don'ts

1. **Don't create infinite loops** - Avoid update triggering update
2. **Don't skip filters** - Unfiltered rules impact performance
3. **Don't use for complex logic** - Use Python methods instead
4. **Don't bypass security** - Respect access rights
5. **Don't forget performance** - Heavy operations slow system
6. **Don't hardcode IDs** - Use XML IDs for references
7. **Don't duplicate** - Check for existing automation first

---

## Debugging Automation

### Check Execution Logs

**Settings → Technical → Automation Rules → [Select Rule] → Logs**

Look for:
- Execution count
- Error messages
- Last execution time
- Failed records

### Common Issues

**Automation Not Triggering:**
- Filter too restrictive
- Wrong trigger type
- Record doesn't meet conditions
- Automation inactive

**Action Failing:**
- Permission errors
- Invalid field reference
- Missing related record
- Python code errors

**Performance Problems:**
- Too many records matched
- Complex Python code
- Nested automation loops
- Heavy database queries

### Testing Checklist

- [ ] Create test record that matches filter
- [ ] Verify automation triggers
- [ ] Check action executes correctly
- [ ] Verify no side effects
- [ ] Test with multiple records
- [ ] Check performance impact
- [ ] Review log for errors

---

## Advanced Examples

### Multi-Step Approval Chain

```python
# Automation 1: Submit for Approval
Trigger: On Update
Filter: [('state', '=', 'draft'), ('amount', '>', 1000)]
Action: Execute Multiple Actions
  1. Update state = 'pending_manager'
  2. Add follower: manager
  3. Send email to manager
  4. Create activity: "Review expense"

# Automation 2: Manager Approval
Trigger: On Update
Filter: [('state', '=', 'pending_manager'), ('manager_approved', '=', True)]
Action:
  if amount > 5000:
      state = 'pending_finance'
      send_email(finance_team)
  else:
      state = 'approved'

# Automation 3: Finance Approval
Trigger: On Update
Filter: [('state', '=', 'pending_finance'), ('finance_approved', '=', True)]
Action: Update state = 'approved'
```

### Smart Lead Assignment (Round-Robin)

```python
# Assign leads evenly across sales team
Trigger: On Creation
Filter: [('type', '=', 'lead')]
Action: Execute Python Code

# Get sales team users
sales_users = env['res.users'].search([
    ('groups_id', 'in', env.ref('sales_team.group_sale_salesman').id),
    ('active', '=', True)
])

if not sales_users:
    return

# Get user with fewest leads
user_lead_counts = []
for user in sales_users:
    count = env['crm.lead'].search_count([
        ('user_id', '=', user.id),
        ('type', '=', 'lead'),
        ('active', '=', True)
    ])
    user_lead_counts.append((user, count))

# Assign to user with minimum leads
next_user = min(user_lead_counts, key=lambda x: x[1])[0]
for rec in records:
    rec.user_id = next_user
```

### SLA Tracking & Escalation

```python
# Track response time and escalate if exceeded
Trigger: Based on Timed Condition
Trigger Date: create_date
Delay: +4 hours
Repeat: Every 30 minutes
Filter: [
    ('stage_id.name', '=', 'New'),
    ('user_id', '=', False)  # Unassigned
]
Action: Execute Multiple Actions
  1. Update priority = 'urgent'
  2. Send email to team lead
  3. Create activity: "SLA Breach - Assign Immediately"
  4. Add follower: team_lead
```

---

## Performance Optimization

### Reduce Trigger Frequency

```python
# Instead of "On Update" for any field:
Trigger: Based on Form Modification
Field: specific_field

# Or use stricter filters:
Filter: [('state', '=', 'specific_state')]
```

### Batch Processing

```python
# Process records in batches (not one-by-one)
Trigger: Based on Timed Condition
Repeat: Every 1 hour
Action: Execute Python Code

# Find eligible records
pending_records = env['sale.order'].search([
    ('state', '=', 'pending'),
    ('create_date', '<', (datetime.now() - timedelta(hours=24)))
], limit=100)

# Batch process
for batch in [pending_records[i:i+10] for i in range(0, len(pending_records), 10)]:
    batch.action_confirm()
    env.cr.commit()  # Commit per batch
```

### Avoid Loops

```python
# ❌ BAD: Can create infinite loop
Trigger: On Update
Action: Update field (triggers another update)

# ✅ GOOD: Check before updating
Trigger: On Update
Action: Execute Python Code

for rec in records:
    if rec.field_a != computed_value:
        rec.field_a = computed_value  # Only update if changed
```

---

## Resources

- [Official Automation Docs](https://www.odoo.com/documentation/19.0/applications/studio/automated_actions.html)
- [Domain Filter Reference](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#reference-orm-domains)
- [Email Template Guide](https://www.odoo.com/documentation/19.0/applications/general/email_communication/email_template.html)

---

**Master automated actions to eliminate manual work and boost productivity!** ⚡

# Odoo Studio Customization Guide for InsightPulse

**Version**: 19.0.1.0.0
**Last Updated**: October 30, 2025
**Target Audience**: Business users, Administrators, Technical implementers

## Table of Contents

1. [Overview](#overview)
2. [Studio vs Code Customization](#studio-vs-code-customization)
3. [Studio Compatibility Matrix](#studio-compatibility-matrix)
4. [Module-Specific Customization](#module-specific-customization)
5. [Common Customization Patterns](#common-customization-patterns)
6. [Automation Recipes](#automation-recipes)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Migration Guide](#migration-guide)

---

## Overview

### What is Odoo Studio?

Odoo Studio is a visual customization tool that enables no-code/low-code modifications to your Odoo environment. It provides drag-and-drop functionality for:

- **Fields & Widgets**: Add custom fields and modify display widgets
- **Views**: Customize forms, lists, kanban boards, graphs, pivots, calendars
- **Models**: Create new data models or extend existing ones
- **Automation**: Build workflows with triggers and actions
- **Reports**: Customize PDF reports with QWeb templates
- **Approvals**: Configure multi-stage approval rules

### InsightPulse Wave 1-3 Modules

Our platform consists of 10 enterprise-grade modules built on Odoo 19.0 CE:

| Module | Category | Studio-Friendly | Automation Support |
|--------|----------|-----------------|-------------------|
| **ipai_core** | Foundation | ⚠️ Limited | ✅ Full |
| **ipai_rate_policy** | Finance | ✅ Full | ✅ Full |
| **ipai_ppm** | Project Management | ✅ Full | ✅ Full |
| **ipai_ppm_costsheet** | Finance | ✅ Full | ✅ Full |
| **ipai_approvals** | Workflow | ✅ Full | ✅ Full |
| **ipai_procure** | Operations | ✅ Full | ✅ Full |
| **ipai_expense** | Finance | ✅ Full | ✅ Full |
| **ipai_subscriptions** | Finance | ✅ Full | ✅ Full |
| **ipai_saas_ops** | Operations | ✅ Full | ⚠️ Partial |
| **superset_connector** | Analytics | ❌ Code Only | ❌ None |
| **ipai_knowledge_ai** | AI/ML | ⚠️ Limited | ✅ Full |

**Legend**:
- ✅ Full: All features customizable via Studio
- ⚠️ Limited: Some restrictions (see module details)
- ❌ Code Only: Requires Python development

---

## Studio vs Code Customization

### When to Use Studio

✅ **Studio is Ideal For:**

1. **Field Management**
   - Adding custom fields to existing models
   - Modifying field properties (labels, help text, defaults)
   - Creating selection fields with predefined options
   - Adding computed fields with simple expressions

2. **View Customization**
   - Rearranging form layouts
   - Hiding/showing fields conditionally
   - Adding groups and notebooks (tabs)
   - Customizing list views (columns, filters, grouping)
   - Creating kanban cards and stages
   - Building pivot tables and graphs

3. **Simple Automation**
   - Email notifications on record creation/update
   - SMS alerts for status changes
   - Simple field updates based on triggers
   - Basic approval workflows
   - Scheduled actions (cron jobs)

4. **Report Customization**
   - Adding company logo and branding
   - Modifying report layouts
   - Adding custom fields to reports
   - Changing fonts, colors, and styling

### When to Use Code

⚠️ **Code is Required For:**

1. **Complex Business Logic**
   - Multi-step calculations with dependencies
   - Advanced data validation rules
   - Complex state machines with side effects
   - Integration with external APIs

2. **Performance-Critical Operations**
   - Bulk data processing (>1000 records)
   - Complex database queries with joins
   - Caching strategies
   - Background job optimization

3. **Security & Compliance**
   - Custom RLS (Row-Level Security) policies
   - Encryption/decryption logic
   - Audit trail requirements beyond standard tracking
   - Multi-tenancy isolation rules

4. **Advanced Integrations**
   - Third-party API connections
   - Webhook receivers
   - Custom authentication providers
   - Real-time data synchronization

### Hybrid Approach

🔄 **Recommended Pattern:**

1. Use **Studio** for 80% of customizations (fields, views, simple automation)
2. Use **Code** for 20% of complex logic (calculations, integrations, security)
3. Expose code-level functionality through Studio-customizable interfaces

**Example**: Rate calculation logic in Python, but markup percentage adjustable via Studio field.

---

## Studio Compatibility Matrix

### ipai_core (Foundation Module)

**Customization Level**: ⚠️ Limited

| Feature | Studio Support | Notes |
|---------|---------------|-------|
| Approval Flow Model | ✅ Fields | Do NOT modify `state` field values |
| Queue Job Integration | ❌ Code Only | Requires Python knowledge |
| Audit Trail Decorators | ❌ Code Only | Applied at model level |
| Multi-tenancy Utilities | ❌ Code Only | Security-critical |

**Safe to Customize**:
- Add custom fields to `approval.flow`
- Modify approval flow views (form, list, kanban)
- Create custom reports for approval history

**Do NOT Customize**:
- Queue job configuration
- Audit decorators
- RLS policy templates
- Multi-tenancy isolation logic

### ipai_rate_policy (Rate Calculation)

**Customization Level**: ✅ Full

#### Models

**rate.policy** - Main rate policy configuration

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `name` | Char | ✅ Yes | Policy name |
| `markup_percentage` | Float | ✅ Yes | Default: 25.0% |
| `effective_date` | Date | ✅ Yes | When policy becomes active |
| `state` | Selection | ⚠️ Read-only | Values: draft, active, archived |
| `line_ids` | One2many | ✅ Yes | Rate lines |
| `notes` | Text | ✅ Yes | Free-form notes |

**Custom Field Examples**:
```python
# Studio-created fields (automatically generated)
x_studio_region = fields.Selection([('us', 'US'), ('eu', 'EU'), ('apac', 'APAC')])
x_studio_approval_required = fields.Boolean(default=False)
x_studio_external_id = fields.Char()
```

**rate.policy.line** - Individual rate entries

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `policy_id` | Many2one | ❌ Required | Parent policy |
| `employee_id` | Many2one | ✅ Yes | Related employee |
| `p60_rate` | Float | ✅ Yes | Base rate from P60 |
| `calculated_rate` | Float | ⚠️ Computed | Auto-calculated |
| `effective_date` | Date | ✅ Yes | Line effective date |

**Safe to Customize**:
- Add custom fields (region, cost center, project)
- Modify form layouts (group fields logically)
- Create custom kanban views for policy tracking
- Add approval stages (requires ipai_approvals)

**Do NOT Customize**:
- `calculate_rate()` method logic
- `state` transition rules
- Computed field calculations

#### Automation Examples

**Example 1: Email on Policy Activation**
```
Trigger: Record Updated
Model: Rate Policy
Condition: state = 'active'
Action: Send Email
Recipients: Program Manager
Template: "Rate Policy {name} activated on {effective_date}"
```

**Example 2: Auto-Archive Expired Policies**
```
Trigger: Time-based (Daily at 2 AM)
Model: Rate Policy
Condition: expiry_date < today AND state = 'active'
Action: Python Code
Code:
  for record in records:
    record.action_archive_policy()
```

### ipai_ppm (Program/Project Management)

**Customization Level**: ✅ Full

#### Models

**ppm.program** - Program management

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `name` | Char | ✅ Yes | Program name |
| `code` | Char | ✅ Yes | Unique program code |
| `program_manager_id` | Many2one | ✅ Yes | Assigned manager |
| `state` | Selection | ⚠️ Read-only | draft, planning, active, on_hold, completed, cancelled |
| `project_ids` | One2many | ✅ Yes | Related projects |
| `roadmap_ids` | One2many | ✅ Yes | Program roadmaps |
| `risk_ids` | One2many | ✅ Yes | Risk register |
| `budget_ids` | One2many | ✅ Yes | Budget allocations |
| `total_budget` | Monetary | ⚠️ Computed | Sum of budget lines |

**ppm.roadmap** - Roadmap planning

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `program_id` | Many2one | ❌ Required | Parent program |
| `name` | Char | ✅ Yes | Milestone name |
| `planned_date` | Date | ✅ Yes | Target date |
| `actual_date` | Date | ✅ Yes | Actual completion |
| `progress` | Float | ✅ Yes | % complete (0-100) |

**ppm.risk** - Risk management

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `program_id` | Many2one | ❌ Required | Parent program |
| `name` | Char | ✅ Yes | Risk description |
| `probability` | Selection | ✅ Yes | low, medium, high |
| `impact` | Selection | ✅ Yes | low, medium, high, critical |
| `mitigation_plan` | Text | ✅ Yes | Response strategy |
| `owner_id` | Many2one | ✅ Yes | Risk owner |

**ppm.budget** - Budget tracking

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `program_id` | Many2one | ❌ Required | Parent program |
| `name` | Char | ✅ Yes | Budget line name |
| `amount` | Monetary | ✅ Yes | Allocated amount |
| `spent` | Monetary | ✅ Yes | Actual spent |
| `variance` | Monetary | ⚠️ Computed | Amount - spent |

**Safe to Customize**:
- Add custom fields (sponsor, department, strategic priority)
- Create custom dashboards (project portfolio view)
- Build kanban views for program states
- Add custom reports (program status report, risk matrix)
- Create approval workflows for budget changes

**Do NOT Customize**:
- State transition logic (draft → planning → active)
- Computed field calculations (total_budget, variance)
- Project relationship logic

#### Automation Examples

**Example 1: Budget Alert on Overspend**
```
Trigger: Record Updated
Model: PPM Budget
Condition: spent > amount * 0.9
Action: Send Email + Create Activity
Recipients: Program Manager, Finance Team
Activity Type: Warning
Summary: "Budget {name} at 90% utilization"
```

**Example 2: Auto-Create Risk Mitigation Tasks**
```
Trigger: Record Created
Model: PPM Risk
Condition: impact = 'critical'
Action: Python Code
Code:
  for risk in records:
    env['project.task'].create({
      'name': f"Mitigate: {risk.name}",
      'user_id': risk.owner_id.id,
      'priority': '3',  # High
      'description': risk.mitigation_plan,
    })
```

### ipai_saas_ops (SaaS Operations)

**Customization Level**: ✅ Full

#### Models

**saas.tenant** - Tenant management

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `name` | Char | ✅ Yes | Tenant name |
| `tenant_code` | Char | ✅ Yes | Unique code |
| `subdomain` | Char | ⚠️ Format-validated | must be DNS-safe |
| `database_name` | Char | ⚠️ Format-validated | PostgreSQL naming rules |
| `admin_email` | Char | ✅ Yes | Admin contact |
| `state` | Selection | ⚠️ Read-only | draft, provisioning, active, suspended, terminated |
| `plan_id` | Selection | ✅ Yes | trial, starter, professional, enterprise |
| `max_users` | Integer | ✅ Yes | User limit |
| `storage_limit_gb` | Float | ✅ Yes | Storage quota |
| `backup_ids` | One2many | ✅ Yes | Backup history |

**saas.backup** - Backup management

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `tenant_id` | Many2one | ❌ Required | Parent tenant |
| `name` | Char | ✅ Yes | Backup name |
| `backup_type` | Selection | ✅ Yes | manual, scheduled, pre_upgrade |
| `size_gb` | Float | ✅ Yes | Backup size |
| `created_date` | Datetime | ⚠️ Auto-set | Backup timestamp |
| `expiry_date` | Date | ✅ Yes | Retention period |

**saas.usage** - Usage tracking

| Field | Type | Studio-Customizable | Notes |
|-------|------|-------------------|-------|
| `tenant_id` | Many2one | ❌ Required | Parent tenant |
| `date` | Date | ⚠️ Auto-set | Measurement date |
| `active_users` | Integer | ✅ Yes | Current users |
| `storage_gb` | Float | ✅ Yes | Storage used |
| `api_calls` | Integer | ✅ Yes | API usage |

**Safe to Customize**:
- Add custom fields (industry, country, subscription_tier)
- Create custom views (tenant health dashboard)
- Build kanban views for tenant lifecycle
- Add usage alerts and notifications
- Create custom reports (usage trends, growth metrics)

**Do NOT Customize**:
- Provisioning logic (`action_provision()`)
- Database name validation
- State transition rules
- Backup restoration logic

**⚠️ Automation Restrictions**:
- Tenant provisioning requires code-level integration
- Backup operations use external scripts
- Usage collection runs via scheduled jobs

#### Automation Examples

**Example 1: Trial Expiration Notification**
```
Trigger: Time-based (Daily at 9 AM)
Model: SaaS Tenant
Condition: plan_id = 'trial' AND expiry_date <= today + 7 days
Action: Send Email
Recipients: Admin Email
Template: "Your trial expires in {expiry_date - today} days. Upgrade now!"
```

**Example 2: Auto-Suspend on Storage Limit**
```
Trigger: Record Updated
Model: SaaS Usage
Condition: storage_gb > tenant_id.storage_limit_gb
Action: Python Code + Send Email
Code:
  for usage in records:
    if usage.storage_gb > usage.tenant_id.storage_limit_gb:
      usage.tenant_id.action_suspend()
      # Email sent by separate automation
```

---

## Common Customization Patterns

### Pattern 1: Adding Custom Fields to Existing Models

**Scenario**: Add a "Department" field to Rate Policy

**Steps**:
1. Open Odoo Studio
2. Navigate to Finance → Rate Policies
3. Click "Edit" (Studio mode)
4. Drag "Many2one" field onto form
5. Configure:
   - Label: "Department"
   - Related Model: `hr.department`
   - Required: No
   - Default: User's department
6. Save and exit Studio

**Result**:
```python
# Auto-generated field (visible in Technical Settings)
x_studio_department = fields.Many2one('hr.department', string='Department')
```

**Use Cases**:
- Tracking which department owns a policy
- Filtering policies by department
- Department-specific approval rules

---

### Pattern 2: Creating Conditional Field Visibility

**Scenario**: Show "Termination Reason" field only when tenant is terminated

**Steps**:
1. Open Studio on SaaS Tenant form
2. Add Text field: `x_studio_termination_reason`
3. Click field → Properties → Invisible
4. Set condition: `[('state', '!=', 'terminated')]`
5. Save

**Result**:
- Field hidden until state = 'terminated'
- Appears automatically on status change
- Validation can be added via automation

**Advanced**:
```xml
<!-- Studio generates this XML -->
<field name="x_studio_termination_reason"
       invisible="state != 'terminated'"
       required="state == 'terminated'"/>
```

---

### Pattern 3: Custom Kanban Views for Workflow Management

**Scenario**: Program lifecycle kanban board

**Steps**:
1. Navigate to Programs list view
2. Switch to Kanban view
3. Enter Studio mode
4. Configure stages:
   - Group by: `state`
   - Card fields: `name`, `code`, `program_manager_id`, `total_budget`
   - Color: Based on `priority` (custom field)
5. Add progress bar: Show budget utilization
6. Enable drag-and-drop between states

**Result**:
```
┌─────────────┬──────────────┬─────────────┬──────────────┐
│   Draft     │   Planning   │   Active    │  Completed   │
├─────────────┼──────────────┼─────────────┼──────────────┤
│ Program A   │ Program C    │ Program E   │ Program G    │
│ $500K       │ $1.2M        │ $3.5M       │ $2.1M        │
│ [████░░░░░] │ [██████░░░░] │ [████████░] │ [██████████] │
└─────────────┴──────────────┴─────────────┴──────────────┘
```

---

### Pattern 4: Automated Email Notifications

**Scenario**: Notify stakeholders when program status changes

**Steps**:
1. Studio → Automations → Create
2. Configure:
   - **Trigger**: Record Updated
   - **Model**: PPM Program
   - **Apply On**: `state`
   - **Before Update Domain**: `[('state', '=', 'active')]`
   - **Action**: Send Email
   - **Recipients**: `program_manager_id`, followers
   - **Template**:
     ```
     Subject: Program Status Changed: {name}
     Body:
     Hello {program_manager_id.name},

     Program "{name}" status changed from {state_before} to {state}.

     Details:
     - Code: {code}
     - Budget: {total_budget}
     - Projects: {project_count}

     View Program: {url}
     ```

---

### Pattern 5: Computed Fields with Studio

**Scenario**: Calculate "Budget Health" indicator

**Steps**:
1. Add Float field: `x_studio_budget_health`
2. Mark as "Computed"
3. Dependencies: `total_budget`, `x_studio_actual_spent`
4. Python code (limited):
   ```python
   for record in self:
       if record.total_budget > 0:
           record.x_studio_budget_health = (
               record.x_studio_actual_spent / record.total_budget * 100
           )
       else:
           record.x_studio_budget_health = 0.0
   ```

**Limitations**:
- Simple expressions only
- No external API calls
- No multi-record operations
- Performance impact on large datasets

---

### Pattern 6: Multi-Stage Approval Workflows

**Scenario**: Rate policy changes require Finance → CFO → CEO approval

**Implementation** (Requires `ipai_approvals` module):

1. **Create Approval Flow**:
   ```
   Studio → Approvals → Create Flow
   Name: Rate Policy Change Approval
   Model: rate.policy
   ```

2. **Define Stages**:
   ```
   Stage 1: Finance Review
   - Approver Group: Finance Team
   - Condition: markup_percentage changed OR effective_date changed

   Stage 2: CFO Approval
   - Approver: CFO (user)
   - Condition: markup_percentage > 30%

   Stage 3: CEO Approval
   - Approver: CEO (user)
   - Condition: total_impact > $100,000 (custom field)
   ```

3. **Configure Actions**:
   - On Approval: Change state to 'active'
   - On Rejection: Send email to policy creator
   - Timeout: Escalate after 48 hours

**Result**:
```
Draft → Finance → CFO → CEO → Active
        Review    Approval  Approval
```

---

### Pattern 7: Dynamic Field Domains

**Scenario**: Filter employees by department when assigning to rate policy

**Steps**:
1. Studio → Rate Policy form → `employee_id` field
2. Properties → Domain
3. Set domain:
   ```python
   [('department_id', '=', x_studio_department)]
   ```

**Result**:
- Employee dropdown shows only employees from selected department
- Dynamic filtering as department changes
- Improves data quality and UX

---

### Pattern 8: Custom Report Templates

**Scenario**: Program Status Report with custom branding

**Steps**:
1. Studio → Reports → Create
2. Select Model: `ppm.program`
3. Paper format: A4, Portrait
4. Add elements:
   - Header: Company logo, report title
   - Body: Program details table
   - Footer: Page numbers, generation date

**QWeb Template Example**:
```xml
<template id="program_status_report">
  <t t-call="web.html_container">
    <t t-foreach="docs" t-as="program">
      <div class="page">
        <h1>Program Status Report</h1>
        <h2 t-field="program.name"/>

        <table class="table">
          <tr>
            <th>Field</th>
            <th>Value</th>
          </tr>
          <tr>
            <td>Code</td>
            <td t-field="program.code"/>
          </tr>
          <tr>
            <td>Manager</td>
            <td t-field="program.program_manager_id.name"/>
          </tr>
          <tr>
            <td>Budget</td>
            <td t-field="program.total_budget"/>
          </tr>
          <tr>
            <td>State</td>
            <td t-field="program.state"/>
          </tr>
        </table>

        <h3>Projects</h3>
        <ul>
          <t t-foreach="program.project_ids" t-as="project">
            <li t-field="project.name"/>
          </t>
        </ul>
      </div>
    </t>
  </t>
</template>
```

---

### Pattern 9: Webhook Integration

**Scenario**: Trigger external system when tenant is provisioned

**Steps**:
1. Studio → Automations → Create
2. Configure:
   - **Trigger**: Record Updated
   - **Model**: SaaS Tenant
   - **Condition**: `state = 'active'`
   - **Action**: Webhook
   - **URL**: `https://api.example.com/webhooks/tenant-provisioned`
   - **Method**: POST
   - **Payload**:
     ```json
     {
       "tenant_id": "{id}",
       "tenant_name": "{name}",
       "subdomain": "{subdomain}",
       "admin_email": "{admin_email}",
       "plan": "{plan_id}",
       "created_at": "{created_date}"
     }
     ```

**Security**:
- Add authentication header
- Use HTTPS only
- Validate webhook signatures
- Rate limit external calls

---

### Pattern 10: Scheduled Actions (Cron Jobs)

**Scenario**: Daily backup for all active tenants

**Steps**:
1. Studio → Automations → Create
2. Configure:
   - **Trigger**: Time-based
   - **Interval**: Days (1)
   - **Execute At**: 02:00 AM
   - **Model**: SaaS Tenant
   - **Domain**: `[('state', '=', 'active')]`
   - **Action**: Python Code
   - **Code**:
     ```python
     for tenant in records:
         env['saas.backup'].create({
             'tenant_id': tenant.id,
             'name': f'Auto Backup {fields.Date.today()}',
             'backup_type': 'scheduled',
             'created_date': fields.Datetime.now(),
         })
     ```

**Best Practices**:
- Run during off-peak hours
- Limit batch size for performance
- Add error handling and logging
- Monitor execution time and failures

---

## Automation Recipes

### Recipe 1: Approval Workflow with Escalation

**Use Case**: Expense approval with automatic escalation

**Configuration**:
```yaml
Automation: Expense Approval Flow
Trigger: Record Created
Model: hr.expense
Conditions:
  - amount > $500
Steps:
  1. Manager Approval:
     - Timeout: 24 hours
     - Escalation: Send reminder email

  2. Finance Approval:
     - Condition: amount > $2000
     - Timeout: 48 hours
     - Escalation: Assign to Finance Director

  3. CFO Approval:
     - Condition: amount > $10000
     - Required: Yes

Actions:
  - On Approval: Set state = 'approved', create accounting entry
  - On Rejection: Set state = 'refused', notify employee
```

**Studio Implementation**:
1. Create automation for each stage
2. Use Python code for state transitions
3. Email templates for notifications
4. Activity scheduling for escalation

---

### Recipe 2: Rate Policy Update Propagation

**Use Case**: When rate policy is updated, recalculate all active employee rates

**Configuration**:
```yaml
Automation: Rate Recalculation
Trigger: Record Updated
Model: rate.policy
Conditions:
  - markup_percentage changed OR effective_date changed
  - state = 'active'
Action: Python Code
Code: |
  for policy in records:
      # Recalculate all rate lines
      for line in policy.line_ids:
          line.calculated_rate = policy.calculate_rate(
              line.p60_rate,
              policy.markup_percentage
          )
      # Log recalculation
      env['rate.calculation.log'].create({
          'policy_id': policy.id,
          'calculation_date': fields.Datetime.now(),
          'reason': 'Policy updated',
      })
```

---

### Recipe 3: Tenant Usage Monitoring with Alerts

**Use Case**: Alert when tenant approaches resource limits

**Configuration**:
```yaml
Automation: Usage Alert - 80% Storage
Trigger: Record Updated
Model: saas.usage
Conditions:
  - storage_gb / tenant_id.storage_limit_gb >= 0.8
  - storage_gb / tenant_id.storage_limit_gb < 1.0
Actions:
  1. Send Email:
     - To: tenant_id.admin_email
     - Subject: "Storage Limit Warning"
     - Body: "You have used {storage_gb}GB of {storage_limit_gb}GB"

  2. Create Activity:
     - Assigned to: Account Manager
     - Type: To Do
     - Summary: "Follow up on storage upgrade"
```

**Additional Automations**:
- 90% threshold: Send SMS alert
- 95% threshold: Restrict uploads
- 100% threshold: Suspend tenant (with grace period)

---

### Recipe 4: Program Milestone Tracking

**Use Case**: Auto-update program progress based on milestone completion

**Configuration**:
```yaml
Automation: Milestone Progress Update
Trigger: Record Updated
Model: ppm.roadmap
Conditions:
  - actual_date is set
  - progress = 100
Action: Python Code
Code: |
  for milestone in records:
      program = milestone.program_id
      # Calculate overall program progress
      completed = len(program.roadmap_ids.filtered(lambda r: r.progress == 100))
      total = len(program.roadmap_ids)
      program.x_studio_completion_percentage = (completed / total * 100) if total > 0 else 0

      # Check if all milestones complete
      if program.x_studio_completion_percentage == 100:
          program.action_complete()
```

---

### Recipe 5: Risk-Based Budget Reserves

**Use Case**: Automatically allocate contingency reserves based on risk assessment

**Configuration**:
```yaml
Automation: Risk-Based Contingency
Trigger: Record Created or Updated
Model: ppm.risk
Conditions:
  - impact IN ['high', 'critical']
  - probability IN ['medium', 'high']
Action: Python Code
Code: |
  for risk in records:
      program = risk.program_id

      # Calculate contingency amount
      contingency_map = {
          ('high', 'medium'): 0.10,    # 10% of budget
          ('high', 'high'): 0.15,      # 15% of budget
          ('critical', 'medium'): 0.15, # 15% of budget
          ('critical', 'high'): 0.25,   # 25% of budget
      }

      key = (risk.impact, risk.probability)
      contingency_pct = contingency_map.get(key, 0.05)

      # Create/update contingency budget line
      budget = env['ppm.budget'].search([
          ('program_id', '=', program.id),
          ('name', '=', f'Contingency: {risk.name}')
      ], limit=1)

      if not budget:
          env['ppm.budget'].create({
              'program_id': program.id,
              'name': f'Contingency: {risk.name}',
              'amount': program.total_budget * contingency_pct,
          })
```

---

## Best Practices

### General Guidelines

1. **Documentation**
   - Document all Studio customizations in change log
   - Include business justification for each customization
   - Maintain naming conventions for custom fields (`x_studio_*`)
   - Create user guides for custom workflows

2. **Testing**
   - Test customizations in staging environment first
   - Validate automation rules with test data
   - Check performance impact on large datasets
   - Test with different user roles and permissions

3. **Performance**
   - Avoid computed fields on large datasets (>10,000 records)
   - Limit automation triggers to necessary conditions
   - Use scheduled actions for batch operations
   - Index custom fields used in searches/filters

4. **Security**
   - Review field-level access rights
   - Validate custom field domains and constraints
   - Test approval workflows with different user roles
   - Audit automation actions for privilege escalation

5. **Maintainability**
   - Keep customizations simple and purpose-driven
   - Avoid deep dependencies between custom fields
   - Use OCA modules when available instead of custom code
   - Plan for module upgrades and migrations

### Field Naming Conventions

**Studio Auto-Generated Fields**:
```
x_studio_[descriptive_name]
```

**Examples**:
- `x_studio_department` - Department reference
- `x_studio_approval_level` - Approval threshold
- `x_studio_risk_score` - Calculated risk score
- `x_studio_external_ref` - External system ID

**Avoid**:
- Generic names: `x_studio_field_1`, `x_studio_temp`
- Reserved words: `x_studio_id`, `x_studio_create_date`
- Special characters: `x_studio_field/name`, `x_studio_field name`

### View Customization Best Practices

1. **Form Views**
   - Group related fields in notebooks (tabs)
   - Use clear section headers
   - Place critical fields at the top
   - Hide technical fields from end users
   - Add help text for complex fields

2. **List Views**
   - Limit visible columns to 5-7 essential fields
   - Enable inline editing for frequently updated fields
   - Add filters for common search criteria
   - Group by logical categories (state, department, date)

3. **Kanban Views**
   - Use color coding for visual prioritization
   - Include key metrics on cards
   - Enable drag-and-drop for state changes
   - Add quick actions (approve, reject, escalate)

4. **Graph/Pivot Views**
   - Choose appropriate chart types (bar, line, pie)
   - Limit data points for readability
   - Add drill-down capability
   - Export to Excel for detailed analysis

### Automation Best Practices

1. **Trigger Design**
   - Use specific conditions to avoid unnecessary executions
   - Combine multiple conditions in single automation
   - Schedule batch operations during off-peak hours
   - Monitor automation execution logs

2. **Action Design**
   - Keep Python code simple and maintainable
   - Add error handling and logging
   - Avoid infinite loops (automation triggering itself)
   - Test with edge cases (null values, large numbers)

3. **Email Templates**
   - Use clear, professional language
   - Include relevant context and links
   - Test with different email clients
   - Respect user notification preferences

4. **Performance**
   - Batch operations when processing multiple records
   - Use queue jobs for long-running tasks
   - Implement rate limiting for external API calls
   - Monitor server resource usage

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Custom Field Not Appearing in View

**Symptoms**:
- Field created in Studio but not visible in form
- Field shows in Technical Settings but not in UI

**Solutions**:
1. Check field visibility conditions (`invisible` attribute)
2. Verify user has access rights to field
3. Clear browser cache and reload
4. Check if field is in hidden notebook tab
5. Verify field is not in archived form view

**Debug Steps**:
```python
# In Odoo shell
env['ir.ui.view'].search([('model', '=', 'rate.policy'), ('type', '=', 'form')])
# Find inherited view with custom field
# Check for invisible="1" or conditional visibility
```

---

#### Issue 2: Automation Not Triggering

**Symptoms**:
- Automation rule exists but never executes
- Email notifications not sent
- Python code not running

**Solutions**:
1. **Check Trigger Conditions**:
   - Verify domain filter matches records
   - Check before/after update conditions
   - Test with manual execution

2. **Check Automation State**:
   - Ensure automation is active (`active = True`)
   - Verify no conflicting automations
   - Check execution log for errors

3. **Check Permissions**:
   - Automation user has write access to model
   - Email template has correct sender
   - Python code has necessary permissions

**Debug Steps**:
```python
# Find automation
automation = env['base.automation'].search([('name', '=', 'Your Automation')])
print(automation.state)  # Should be 'code' or 'email'
print(automation.active)  # Should be True

# Test domain
records = env['rate.policy'].search(automation._get_domain())
print(len(records))  # Should match expected records

# Check logs
env['base.automation.log'].search([('automation_id', '=', automation.id)], order='create_date desc', limit=10)
```

---

#### Issue 3: Computed Field Shows Wrong Value

**Symptoms**:
- Computed field value incorrect or outdated
- Field not recalculating on dependency change
- Performance issues with computed fields

**Solutions**:
1. **Check Dependencies**:
   - Verify `@api.depends()` includes all dependencies
   - Test by manually changing dependency field
   - Check for circular dependencies

2. **Check Stored Flag**:
   - Stored computed fields only update when dependencies change
   - Non-stored fields compute on every read (slow)

3. **Check Compute Method**:
   - Add logging to compute method
   - Test with small dataset first
   - Verify no exceptions in compute logic

**Example Fix**:
```python
# Before (incorrect)
x_studio_health = fields.Float(compute='_compute_health')

def _compute_health(self):
    for record in self:
        record.x_studio_health = record.spent / record.budget  # Missing dependency

# After (correct)
x_studio_health = fields.Float(compute='_compute_health', store=True)

@api.depends('spent', 'budget')
def _compute_health(self):
    for record in self:
        if record.budget > 0:
            record.x_studio_health = record.spent / record.budget
        else:
            record.x_studio_health = 0.0
```

---

#### Issue 4: Performance Degradation After Customization

**Symptoms**:
- Slow form load times
- List views take long to render
- System unresponsive during business hours

**Solutions**:
1. **Identify Bottleneck**:
   - Check database query logs
   - Profile slow views with browser devtools
   - Monitor server CPU/memory usage

2. **Optimize Computed Fields**:
   - Add `store=True` to frequently read computed fields
   - Remove unnecessary computed fields
   - Batch compute operations

3. **Optimize Automations**:
   - Narrow domain filters
   - Schedule batch operations off-peak
   - Reduce automation frequency

4. **Database Optimization**:
   - Add indexes to custom fields used in searches
   - Vacuum and analyze database regularly
   - Archive old records

**Index Creation** (requires database access):
```sql
-- Add index to custom field
CREATE INDEX idx_rate_policy_x_studio_department
ON rate_policy (x_studio_department);

-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

---

#### Issue 5: Approval Workflow Stuck

**Symptoms**:
- Records stuck in approval state
- Approvers not receiving notifications
- Unable to approve or reject

**Solutions**:
1. **Check Approver Assignment**:
   - Verify approver user exists and is active
   - Check approver has necessary permissions
   - Verify approver group membership

2. **Check Workflow State**:
   - Look for blocking conditions
   - Check for missing required fields
   - Verify state transition logic

3. **Reset Workflow** (emergency):
   ```python
   # In Odoo shell (use with caution)
   record = env['rate.policy'].browse(123)
   record.write({'state': 'draft'})  # Reset to draft
   # Re-trigger approval flow
   ```

---

#### Issue 6: Custom Report Not Generating

**Symptoms**:
- PDF report blank or shows errors
- QWeb template syntax errors
- Missing data in report

**Solutions**:
1. **Check Template Syntax**:
   - Validate QWeb XML syntax
   - Test with simple template first
   - Check for typos in field names

2. **Check Data Context**:
   - Verify `docs` variable passed correctly
   - Check for null/empty related fields
   - Add null checks in template

3. **Check Report Action**:
   - Verify report action linked to correct model
   - Check report paperformat settings
   - Test with single record first

**Template Debugging**:
```xml
<!-- Add debug output to template -->
<t t-if="docs">
  <p>Found <t t-esc="len(docs)"/> records</p>
  <t t-foreach="docs" t-as="doc">
    <p>Processing: <t t-esc="doc.name"/></p>
  </t>
</t>
<t t-else>
  <p>No records found!</p>
</t>
```

---

### Getting Help

**Internal Resources**:
1. Check module documentation in `docs/` directory
2. Review existing customizations in Technical Settings → Studio → Customizations
3. Search automation logs for error messages
4. Check Odoo system logs (requires server access)

**External Resources**:
1. [Odoo Studio Documentation](https://www.odoo.com/documentation/19.0/applications/studio.html)
2. [Odoo Community Forums](https://www.odoo.com/forum)
3. [OCA GitHub Repositories](https://github.com/OCA)
4. InsightPulse Support Portal

**Escalation Path**:
1. Local Administrator (Studio customizations, user training)
2. Technical Team (complex automations, performance issues)
3. InsightPulse Support (module bugs, feature requests)
4. Odoo Official Support (platform bugs, security issues)

---

## Migration Guide

### Moving Customizations Between Environments

#### Scenario 1: Development → Staging → Production

**Studio Export/Import Method** (Recommended):

1. **Export from Development**:
   ```
   Studio → Customizations → Export
   - Select modules: ipai_rate_policy, ipai_ppm, ipai_saas_ops
   - Include: Custom fields, views, automations, reports
   - Format: ZIP file
   - Download: customizations_2025_10_30.zip
   ```

2. **Import to Staging**:
   ```
   Studio → Customizations → Import
   - Upload: customizations_2025_10_30.zip
   - Review changes: Check field conflicts
   - Apply: Staged import
   - Test: Validate all customizations work
   ```

3. **Promote to Production**:
   - Repeat import process
   - Schedule during maintenance window
   - Backup database before import
   - Monitor for issues post-import

**Database Copy Method** (Alternative):

```bash
# Dump customizations from development
pg_dump -h localhost -U odoo -d odoo_dev \
  --table=ir_ui_view \
  --table=ir_model_fields \
  --table=ir_model_data \
  --table=base_automation \
  --data-only \
  > customizations.sql

# Filter Studio customizations only
grep -E "x_studio_|studio_customization" customizations.sql > studio_only.sql

# Import to staging (after review)
psql -h staging.host -U odoo -d odoo_staging < studio_only.sql
```

---

#### Scenario 2: Handling Version Updates

**Pre-Update Checklist**:

1. **Document Current Customizations**:
   ```
   Generate report:
   - All custom fields (Technical Settings → Fields)
   - All automations (Technical Settings → Automation Rules)
   - All modified views (Technical Settings → Views)
   - All custom reports (Technical Settings → Reports)
   ```

2. **Export Customizations**:
   - Use Studio export feature
   - Backup database
   - Save module versions list

3. **Test in Sandbox**:
   - Clone production environment
   - Perform update in sandbox
   - Verify customizations still work
   - Note any conflicts or issues

**Update Process**:

```bash
# 1. Backup
pg_dump odoo_prod > backup_pre_update_$(date +%Y%m%d).sql

# 2. Update Odoo
docker pull odoo:19.0
docker-compose down
docker-compose up -d

# 3. Update modules
odoo-bin -u ipai_core,ipai_rate_policy,ipai_ppm,ipai_saas_ops -d odoo_prod --stop-after-init

# 4. Verify customizations
# Check Studio → Customizations for conflicts

# 5. Re-import if needed
# Studio → Import → customizations_backup.zip
```

**Post-Update Verification**:

1. ✅ All custom fields present and accessible
2. ✅ Views render correctly
3. ✅ Automations trigger as expected
4. ✅ Reports generate without errors
5. ✅ Computed fields calculate correctly
6. ✅ Approval workflows function properly

---

#### Scenario 3: Merging Customizations from Multiple Sources

**Conflict Resolution Strategy**:

1. **Identify Conflicts**:
   - Custom fields with same name, different types
   - Automations with overlapping triggers
   - View modifications to same form elements
   - Report templates with conflicting QWeb

2. **Resolution Methods**:

   **Field Conflicts**:
   ```
   Option A: Rename one field (e.g., x_studio_dept → x_studio_department_2)
   Option B: Merge into single field with union of both types
   Option C: Keep most comprehensive field, migrate data
   ```

   **Automation Conflicts**:
   ```
   Option A: Combine conditions into single automation
   Option B: Sequence automations (order matters)
   Option C: Split into separate triggers (before/after update)
   ```

   **View Conflicts**:
   ```
   Option A: Use inheritance hierarchy (view priorities)
   Option B: Merge modifications into single view
   Option C: Create separate views for different user groups
   ```

3. **Merge Process**:

   ```python
   # Script to merge customizations
   import odoorpc

   # Connect to both environments
   dev = odoorpc.ODOO('dev.host', port=8069)
   dev.login('odoo_dev', 'admin', 'password')

   staging = odoorpc.ODOO('staging.host', port=8069)
   staging.login('odoo_staging', 'admin', 'password')

   # Export custom fields from dev
   IrModelFields = dev.env['ir.model.fields']
   custom_fields = IrModelFields.search([('name', 'like', 'x_studio_%')])
   field_data = IrModelFields.read(custom_fields, ['name', 'model', 'ttype', 'required'])

   # Check for conflicts in staging
   for field in field_data:
       existing = staging.env['ir.model.fields'].search([
           ('name', '=', field['name']),
           ('model', '=', field['model'])
       ])
       if existing:
           print(f"Conflict: {field['name']} already exists in staging")
           # Handle conflict resolution
       else:
           # Create field in staging
           staging.env['ir.model.fields'].create({
               'name': field['name'],
               'model': field['model'],
               'ttype': field['ttype'],
               'required': field['required'],
           })
   ```

---

#### Scenario 4: Backup and Restore Customizations

**Backup Strategy**:

1. **Automated Daily Backups**:
   ```bash
   #!/bin/bash
   # /opt/odoo/backup/backup_customizations.sh

   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_DIR="/opt/odoo/backups/studio"

   # Export Studio customizations via Odoo CLI
   /opt/odoo/odoo-bin studio-export \
     --database=odoo_prod \
     --modules=ipai_rate_policy,ipai_ppm,ipai_saas_ops \
     --output="${BACKUP_DIR}/studio_${DATE}.zip"

   # Keep last 30 days
   find $BACKUP_DIR -name "studio_*.zip" -mtime +30 -delete
   ```

2. **Manual Backup Before Changes**:
   - Studio → Export → Download ZIP
   - Save with descriptive name: `studio_before_approval_changes_2025_10_30.zip`

**Restore Process**:

1. **Restore Recent Backup**:
   ```
   Studio → Import → Select backup file
   - Preview changes
   - Resolve conflicts
   - Apply restoration
   ```

2. **Restore Specific Customizations**:
   ```python
   # Selective restore script
   import zipfile
   import json

   # Extract specific customization from backup
   with zipfile.ZipFile('studio_backup.zip', 'r') as z:
       # Extract only rate policy customizations
       z.extract('ir_model_fields_rate_policy.json')

       # Load and filter
       with open('ir_model_fields_rate_policy.json') as f:
           fields = json.load(f)
           # Filter to specific field
           target_field = [f for f in fields if f['name'] == 'x_studio_department']

           # Restore via ORM
           env['ir.model.fields'].create(target_field[0])
   ```

---

### Version Control for Studio Customizations

**Git Integration** (Advanced):

1. **Export Customizations to XML**:
   ```bash
   # Export via Odoo CLI
   odoo-bin \
     --database=odoo_dev \
     --export-translations=customizations.xml \
     --modules=ipai_rate_policy,ipai_ppm,ipai_saas_ops

   # Filter Studio customizations
   grep -E "x_studio_|studio_customization" customizations.xml > studio_custom.xml
   ```

2. **Commit to Repository**:
   ```bash
   git add studio_custom.xml
   git commit -m "feat: Add department field to rate policy"
   git push origin feature/rate-policy-department
   ```

3. **Review and Merge**:
   - Create pull request
   - Review XML changes
   - Test in CI/CD pipeline
   - Merge to main branch

4. **Deploy to Production**:
   ```bash
   # Import from XML
   odoo-bin \
     --database=odoo_prod \
     --import-translations=studio_custom.xml \
     --stop-after-init
   ```

**Benefits**:
- Track changes over time
- Code review for customizations
- Rollback to previous versions
- Integration with CI/CD pipelines

---

## Additional Resources

### Official Documentation

- [Odoo Studio Guide](https://www.odoo.com/documentation/19.0/applications/studio.html)
- [Odoo Automation Rules](https://www.odoo.com/documentation/19.0/developer/reference/backend/actions.html#automated-actions)
- [QWeb Report Templates](https://www.odoo.com/documentation/19.0/developer/reference/frontend/qweb.html)

### Community Resources

- [OCA Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [Odoo Community Forum](https://www.odoo.com/forum/help-1)
- [GitHub OCA Modules](https://github.com/OCA)

### Training Materials

- Odoo eLearning: Studio Basics
- InsightPulse User Training Portal
- Video tutorials: YouTube Odoo Official Channel

### Support Contacts

- **Technical Support**: support@insightpulseai.net
- **Bug Reports**: GitHub Issues
- **Feature Requests**: Product roadmap portal
- **Emergency Hotline**: +1-XXX-XXX-XXXX (24/7)

---

**Document Version**: 1.0.0
**Last Updated**: October 30, 2025
**Next Review**: January 30, 2026
**Maintained By**: InsightPulse AI Technical Documentation Team

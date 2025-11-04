---
name: odoo-studio
description: Master Odoo Studio for no-code customization of Odoo apps. Add/modify fields, views, models, automation rules, webhooks, PDF reports, approval rules, and security rules without coding. Use when customizing Odoo without Python development.
---

# Odoo Studio Expert

Transform Claude into an Odoo Studio expert that helps customize Odoo applications without coding.

## What Odoo Studio Does

Odoo Studio is a **no-code customization toolbox** that allows modification of Odoo apps without programming knowledge. Studio provides visual editors for:

- ✅ **Fields** - Add custom fields to any model (20+ field types)
- ✅ **Views** - Customize forms, lists, Kanban, calendar, pivot, graph views
- ✅ **Models** - Create entirely new models (database tables)
- ✅ **Automation Rules** - Trigger actions based on conditions
- ✅ **Webhooks** - Send data to external systems
- ✅ **PDF Reports** - Design custom report templates
- ✅ **Approval Rules** - Multi-level approval workflows
- ✅ **Security Rules** - Control data access by user groups

## When to Use Studio vs Python

### Use Studio For:
- **Simple customizations** - Adding fields, hiding elements, changing labels
- **Prototyping** - Quick mockups before formal development
- **Business user changes** - Empowering non-developers to customize
- **Visual workflows** - Approval chains, automated actions
- **No deployment** - Changes apply immediately without code deployment

### Use Python Development For:
- **Complex business logic** - Multi-step calculations, external API calls
- **Performance-critical operations** - Batch processing, report generation
- **Unit testing** - Test-driven development requirements
- **Version control** - Tracking changes in Git
- **Reusable modules** - Distributing functionality across installations

## Accessing Studio

### Enable Studio
1. Navigate to any Odoo app
2. Click the **🎨 Toggle Studio** icon (top-right corner)
3. Studio sidebar opens on the right

### Alternative Access
1. Open any app
2. Click **🎨 Toggle Studio** icon
3. Use Studio's app navigator to jump to different models

### Exit Studio
Click **Close** button (upper-right corner)

## Studio Capabilities

### 1. Fields Management

**Add Custom Fields to Any Model**

Available field types:
- **Text** - Single-line text (Char)
- **Multiline Text** - Multi-line text area
- **Integer** - Whole numbers
- **Decimal** - Numbers with decimal places
- **Boolean** - Yes/No checkbox
- **Date** - Date picker
- **Date & Time** - Date + time picker
- **Selection** - Dropdown list with options
- **Priority** - Star rating widget
- **Tags** - Multiple selection tags
- **Monetary** - Currency amounts
- **Binary** - File upload
- **Image** - Image upload with preview
- **Html** - Rich text editor
- **Many2one** - Link to another record (foreign key)
- **One2many** - Multiple linked records (inverse)
- **Many2many** - Multiple-to-multiple relationships
- **Related Field** - Display field from related record
- **Computed Field** - Calculate value from other fields

**Field Properties:**
- **Field Name** - Technical identifier (auto-generated)
- **Field Label** - Display name for users
- **Help Tooltip** - Contextual help text
- **Required** - Make field mandatory
- **Read-only** - Prevent editing
- **Invisible** - Hide from view
- **Default Value** - Pre-fill value for new records

See [references/field-types-guide.md](references/field-types-guide.md) for detailed field configuration.

### 2. Views Customization

**Customize Existing Views**

Studio allows editing all Odoo view types:

**Form View** - Detail view for single record
- Drag-and-drop fields to reorder
- Add notebook tabs for organization
- Group fields into sections
- Add separator labels
- Configure field widgets (badge, progress bar, etc.)

**List View** - Table view of multiple records
- Add/remove columns
- Set default sort order
- Add row colors based on conditions
- Configure editable lists
- Add action buttons

**Kanban View** - Card-based visualization
- Customize card layout
- Add/remove fields displayed
- Configure drag-and-drop grouping
- Set card colors
- Add quick-create buttons

**Pivot View** - Interactive pivot table
- Configure row/column dimensions
- Add/remove measures
- Set default aggregations
- Enable drill-down

**Graph View** - Charts and visualizations
- Choose chart type (bar, line, pie)
- Configure axes and measures
- Set default grouping
- Enable stacking

**Calendar View** - Calendar visualization
- Set date field for events
- Configure event display
- Set default view (day/week/month)
- Add color coding

**Map View** - Geographic visualization
- Configure address fields
- Set map provider
- Add markers

**Timeline View** - Gantt-style timeline
- Set start/end date fields
- Configure row grouping
- Set dependencies

See [references/view-customization-guide.md](references/view-customization-guide.md) for view editing patterns.

### 3. Models Management

**Create New Models (Apps)**

Studio can create entirely new database tables:

1. Click **New Model** in Studio sidebar
2. Enter model name (e.g., "Equipment Request")
3. Studio generates:
   - Database table
   - Default fields (Name, Active, Company)
   - Form view
   - List view
   - Search filters
   - Access rights

**Model Features:**
- Auto-generated menu items
- Built-in search capability
- Chatter (messaging) integration
- Activity tracking
- Archive/unarchive functionality

See [examples/create-custom-model.md](examples/create-custom-model.md) for step-by-step walkthrough.

### 4. Automation Rules

**Create Triggered Actions**

Automation rules execute actions when conditions are met:

**Trigger Types:**
- **On Creation** - When new record created
- **On Update** - When record modified
- **On Deletion** - Before record deleted
- **Based on Form Modification** - When specific fields change
- **Based on Timed Condition** - Time-based triggers

**Conditions:**
- Filter records with domain expressions
- Check field values
- Compare dates
- Evaluate multiple conditions (AND/OR)

**Actions:**
- **Update Record** - Set field values
- **Create Record** - Create related record
- **Send Email** - Email notification
- **Add Followers** - Subscribe users
- **Create Activity** - Schedule task/call/meeting
- **Execute Python Code** - Custom logic (requires developer mode)
- **Send Webhook** - POST data to external URL

See [references/automation-patterns.md](references/automation-patterns.md) for common automation examples.

### 5. Webhooks

**Send Data to External Systems**

Webhooks POST data to external URLs when records change:

**Configuration:**
- **Target URL** - Endpoint to receive data
- **Trigger** - When to send (create, write, delete)
- **Model Filter** - Which records to monitor
- **Payload** - Data to send (JSON format)

**Use Cases:**
- Sync to external CRM
- Trigger Zapier workflows
- Update BI dashboards
- Send to message queues
- Integration with custom apps

See [examples/webhook-integration.md](examples/webhook-integration.md) for webhook setup.

### 6. PDF Reports

**Design Custom Print Templates**

Studio provides visual report designer:

**Report Builder:**
- Drag-and-drop components
- Add fields from model
- Insert static text/images
- Configure header/footer
- Set page layout (A4, Letter)
- Multi-page support

**Components:**
- Text blocks
- Field values
- Images/logos
- Tables (One2many records)
- Barcodes/QR codes
- Page breaks
- Conditional sections

**Report Types:**
- Invoice templates
- Quotation templates
- Delivery orders
- Purchase orders
- Custom documents

See [references/report-design-guide.md](references/report-design-guide.md) for report design patterns.

### 7. Approval Rules

**Multi-Level Approval Workflows**

Configure approval chains for records:

**Approval Configuration:**
- **Approval Type** - Model to apply approval (e.g., Expense, PO)
- **Approval Domain** - Which records require approval
- **Approvers** - Users/roles who can approve
- **Approval Sequence** - Order of approvers
- **Notification** - Email on approval request

**Approval States:**
- Draft → Waiting Approval → Approved → Done
- Or: Draft → Rejected → Cancelled

**Use Cases:**
- Expense approvals (Manager → Finance)
- Purchase order approvals (Team Lead → Procurement)
- Leave requests (Manager → HR)
- Budget approvals (Department → CFO)

See [examples/approval-workflow.md](examples/approval-workflow.md) for approval setup.

### 8. Security Rules

**Control Data Access**

Studio allows configuring:

**Access Rights (Model-Level):**
- Read, Write, Create, Delete permissions
- Per user group
- Applies to entire model

**Record Rules (Row-Level):**
- Filter which records users see
- Domain-based filtering
- Per user group
- Examples:
  - "Users see only their own records"
  - "Sales team sees only their region"
  - "Managers see all records"

**Field-Level Security:**
- Make fields read-only for certain groups
- Hide sensitive fields
- Restrict editing

See [references/security-configuration.md](references/security-configuration.md) for security patterns.

## Common Workflows

### Workflow 1: Add Custom Fields to Existing Model

**Scenario:** Add "Project Budget" field to project model

1. Open Projects app
2. Click **🎨 Toggle Studio**
3. Navigate to project form view
4. Click **+ Add** button
5. Select **Monetary** field type
6. Set label: "Project Budget"
7. Configure currency: Company currency
8. Save changes
9. Test: Create new project, enter budget

**Result:** Budget field now available on all projects

### Workflow 2: Create Kanban View Customization

**Scenario:** Add priority stars to task Kanban cards

1. Open Tasks in Kanban view
2. Click **🎨 Toggle Studio**
3. Studio shows Kanban editor
4. Click **Edit** on card template
5. Drag **Priority** field to card
6. Configure widget: "priority"
7. Position: Top-right of card
8. Save changes

**Result:** Star rating now visible on task cards

### Workflow 3: Create Automation Rule

**Scenario:** Auto-assign manager when expense exceeds $1000

1. Open Expenses app
2. Click **🎨 Toggle Studio**
3. Click **Automation** tab
4. Click **New Automation**
5. Set trigger: "On Creation and Update"
6. Add filter: `amount > 1000`
7. Add action: "Update Record"
8. Set field: `manager_id` = Current user's manager
9. Save automation

**Result:** High-value expenses auto-assigned to manager

### Workflow 4: Build Custom Model from Scratch

**Scenario:** Create "Equipment Request" model

1. Open any app, click **🎨 Toggle Studio**
2. Click **New Model** (+ icon)
3. Enter name: "Equipment Request"
4. Studio generates basic structure
5. Add custom fields:
   - Equipment Type (Selection: Laptop, Monitor, Phone)
   - Justification (Text)
   - Estimated Cost (Monetary)
   - Approver (Many2one → Users)
   - Status (Selection: Draft, Approved, Ordered, Delivered)
6. Customize form view layout
7. Add approval workflow
8. Configure access rights

**Result:** Complete Equipment Request app ready to use

See [examples/](examples/) directory for more workflow examples.

## Studio vs Manual Customization

### What Studio Generates

When you customize with Studio, it creates:
- **XML views** stored in ir.ui.view
- **Model fields** stored in ir.model.fields
- **Automation rules** stored in base.automation
- **Record rules** stored in ir.rule
- **Reports** stored in ir.actions.report

These customizations are stored in the database, not in Python code.

### Exporting Studio Customizations

To version control Studio changes:

1. **Export Module** (Developer mode required)
   - Enables → Developer Mode
   - Studio → Export as Module
   - Downloads .zip with Python/XML files

2. **Manual Export**
   - Settings → Technical → Views → Find custom views
   - Copy XML to custom module
   - Commit to Git

### Migrating Studio to Python Module

**When to Migrate:**
- Need version control
- Deploying to multiple instances
- Require unit tests
- Want better performance
- Complex logic beyond Studio capabilities

**Migration Process:**
1. Export Studio customizations
2. Create proper module structure
3. Add Python models for Studio-generated models
4. Convert automation rules to Python methods
5. Add unit tests
6. Deploy as regular module

See [references/studio-to-python-migration.md](references/studio-to-python-migration.md) for migration guide.

## Best Practices

### ✅ Do's

- **Prototype with Studio first** - Validate requirements before coding
- **Document customizations** - Add field help tooltips
- **Use meaningful labels** - Clear field names for users
- **Test before production** - Verify on staging database
- **Export regularly** - Backup customizations as modules
- **Keep it simple** - Studio for simple logic, Python for complex
- **Check performance** - Computed fields can slow down views
- **Limit automation** - Too many rules slow database

### ❌ Don'ts

- **Don't over-customize** - Each field adds overhead
- **Avoid computed fields in lists** - Slow performance
- **Don't skip testing** - Breaking changes affect all users
- **Never bypass security** - Use proper access rights
- **Avoid complex conditions** - Studio domain limits exist
- **Don't duplicate fields** - Use related fields instead
- **Never delete standard fields** - Can break Odoo core

## Pricing Consideration

⚠️ **Important:** Installing Studio triggers upgrade to Custom pricing plan:

**Standard Plan** → **Custom Plan**
- **Yearly/Multi-year:** 30-day upsell order generated
- **Monthly:** Immediate plan switch on next billing cycle

**Cost Impact:**
- Standard: Base features
- Custom: +Studio capability (additional cost per user)

**Before Installing:**
- Confirm budget approval
- Review Odoo pricing page
- Contact account manager for quotes

## Troubleshooting

### Studio Not Available
- **Cause:** Not on Custom plan or Studio not installed
- **Solution:** Contact account manager to upgrade plan

### Changes Not Saving
- **Cause:** Permission issues or database lock
- **Solution:** Check user has Studio group, try again

### Field Not Showing in View
- **Cause:** Field invisible or wrong view edited
- **Solution:** Check field properties, ensure correct view

### Automation Not Triggering
- **Cause:** Filter too restrictive or wrong trigger
- **Solution:** Check domain filter, test with sample record

### Performance Degraded
- **Cause:** Too many computed fields or automation rules
- **Solution:** Review field computation, optimize automation

## Resources

### Reference Documentation
- [references/field-types-guide.md](references/field-types-guide.md) - All field types explained
- [references/view-customization-guide.md](references/view-customization-guide.md) - View editing patterns
- [references/automation-patterns.md](references/automation-patterns.md) - Common automation examples
- [references/security-configuration.md](references/security-configuration.md) - Access control setup
- [references/report-design-guide.md](references/report-design-guide.md) - PDF report templates
- [references/studio-to-python-migration.md](references/studio-to-python-migration.md) - Convert to code

### Examples
- [examples/create-custom-model.md](examples/create-custom-model.md) - Build model from scratch
- [examples/approval-workflow.md](examples/approval-workflow.md) - Multi-level approvals
- [examples/webhook-integration.md](examples/webhook-integration.md) - External system integration
- [examples/custom-dashboard.md](examples/custom-dashboard.md) - Dashboard with KPIs

### Official Documentation
- [Odoo Studio Official Docs](https://www.odoo.com/documentation/19.0/applications/studio.html)

## Getting Started

Ask Claude:

```
"Add a 'Priority' field to my Sales Orders in Odoo Studio"
"Create a Kanban view for my custom Equipment Request model"
"Set up approval workflow: expenses over $1000 need manager approval"
"Build a custom PDF report template for delivery orders"
"Create automation: send email when invoice is overdue"
```

**No coding required - customize Odoo visually with Studio!** 🎨

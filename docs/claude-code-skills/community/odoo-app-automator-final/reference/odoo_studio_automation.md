# Odoo Studio Automation Reference

Programmatic configuration of Odoo Studio customizations for no-code module creation.

## What is Odoo Studio?

Odoo Studio is a no-code/low-code tool for customizing Odoo applications without writing Python code. It allows users to:
- Add custom fields to existing models
- Modify views (form, list, kanban, etc.)
- Create automated actions
- Set up workflows
- Configure reports
- Design dashboards

## Studio vs Custom Modules

### When to Use Studio

✅ **Quick prototyping**: Test ideas rapidly  
✅ **Simple customizations**: Add fields, modify views  
✅ **Business users**: Non-technical staff can customize  
✅ **Iterative development**: Easy to modify  
✅ **Visual design**: Drag-and-drop interface

### When to Use Custom Modules

✅ **Complex business logic**: Python code required  
✅ **Performance-critical**: Optimized code  
✅ **Version control**: Git-based workflows  
✅ **Reusability**: Share across databases  
✅ **External integrations**: API connections

### Hybrid Approach

**Best of both worlds:**
1. Use Studio for rapid prototyping
2. Export as custom module
3. Enhance with Python code
4. Version control in Git
5. Deploy via Odoo.sh

## Studio Capabilities

### 1. Field Management

**Add Custom Fields:**
- Char (text)
- Integer, Float, Monetary (numbers)
- Boolean (checkbox)
- Selection (dropdown)
- Date, Datetime
- Many2one (relation)
- One2many (reverse relation)
- Many2many (multiple relations)
- HTML, Text (multiline)
- Binary (file upload)

**Field Properties:**
- Label
- Help tooltip
- Default value
- Required
- Readonly
- Invisible (conditional)
- Domain filter (for relations)

### 2. View Customization

**Supported Views:**
- Form (detail page)
- List/Tree (table)
- Kanban (cards)
- Calendar
- Graph (charts)
- Pivot (tables with aggregation)
- Activity (timeline)
- Map (geolocation)

**View Operations:**
- Add/remove fields
- Reorder elements
- Add groups/pages/separators
- Set conditional visibility
- Customize labels
- Add buttons/actions

### 3. Automated Actions

**Triggers:**
- On Create
- On Update
- On Delete
- On specific field change
- Time-based (scheduled)

**Actions:**
- Update record
- Create new record
- Send email
- Execute Python code
- Call server action

### 4. Filters & Grouping

**Custom Filters:**
- Predefined search filters
- Default filters
- Group by options
- Favorite filters (saved searches)

### 5. Reports

**Report Types:**
- PDF reports
- Excel exports
- Custom layouts
- QR codes
- Barcodes

### 6. Access Rights

**Security:**
- Field-level access
- View-level access
- Record rules
- User groups

## Exporting Studio Customizations

### Export as Module

**Steps:**
1. Go to Studio
2. Click "Export" button
3. Select customizations to export
4. Download as ZIP

**Generated Module Structure:**
```
studio_customizations/
├── __manifest__.py
├── models/
│   └── models.py  # Field definitions
├── views/
│   └── views.xml  # View modifications
├── data/
│   └── actions.xml  # Automated actions
└── security/
    └── ir.model.access.csv
```

### Version Control

```bash
# Unzip exported module
unzip studio_customizations.zip -d custom_modules/

# Add to git
git add custom_modules/studio_customizations/
git commit -m "Export Studio customizations"
git push origin staging
```

## Programmatic Studio Configuration

### Creating Fields via XML

```xml
<record id="field_bir_form_manager_code" model="ir.model.fields">
    <field name="name">x_manager_code</field>
    <field name="model_id" ref="model_bir_form_1601c"/>
    <field name="field_description">Project Manager Code</field>
    <field name="ttype">selection</field>
    <field name="selection">
        [('RIM', 'RIM'), ('CKVC', 'CKVC'), ('BOM', 'BOM')]
    </field>
    <field name="required">True</field>
    <field name="store">True</field>
</record>
```

### Modifying Views via XML

```xml
<record id="view_bir_form_inherit" model="ir.ui.view">
    <field name="name">bir.form.1601c.form.inherit</field>
    <field name="model">bir.form.1601c</field>
    <field name="inherit_id" ref="bir_tax_filing.view_bir_form_1601c_form"/>
    <field name="arch" type="xml">
        <xpath expr="//field[@name='filing_period']" position="after">
            <field name="x_manager_code"/>
        </xpath>
    </field>
</record>
```

### Creating Automated Actions

```xml
<record id="action_notify_bir_deadline" model="base.automation">
    <field name="name">BIR Filing Deadline Reminder</field>
    <field name="model_id" ref="model_bir_form_1601c"/>
    <field name="trigger">on_time</field>
    <field name="interval_number">1</field>
    <field name="interval_type">days</field>
    <field name="code">
        # Find forms due in 3 days
        forms = records.search([
            ('state', '=', 'ready'),
            ('filing_deadline', '&lt;=', (datetime.today() + timedelta(days=3)).strftime('%Y-%m-%d'))
        ])
        
        # Send notification
        for form in forms:
            form.activity_schedule(
                'mail.mail_activity_data_todo',
                summary='BIR Filing Due Soon',
                note=f'Form {form.name} is due on {form.filing_deadline}'
            )
    </field>
</record>
```

## Studio to Module Workflow

### Step 1: Design in Studio

1. Open any app
2. Click Studio icon
3. Add fields, modify views
4. Test thoroughly
5. Export customizations

### Step 2: Convert to Module

```python
# Convert Studio fields to proper model fields

# Before (Studio):
# x_manager_code (added via Studio)

# After (Custom Module):
class BIRForm(models.Model):
    _inherit = 'bir.form.1601c'
    
    agency_code = fields.Selection([
        ('RIM', 'RIM'),
        ('CKVC', 'CKVC'),
        # ... more options
    ], string='Agency Code', required=True)
```

### Step 3: Enhance with Python

```python
# Add business logic that Studio can't do

class BIRForm(models.Model):
    _inherit = 'bir.form.1601c'
    
    @api.constrains('agency_code', 'filing_period')
    def _check_duplicate_filing(self):
        """Prevent duplicate filings for same agency/period"""
        for record in self:
            existing = self.search([
                ('id', '!=', record.id),
                ('agency_code', '=', record.agency_code),
                ('filing_period', '=', record.filing_period),
            ])
            if existing:
                raise ValidationError(
                    _('A filing for %s in %s already exists!') % 
                    (record.agency_code, record.filing_period)
                )
```

### Step 4: Deploy

```bash
git add custom_modules/enhanced_bir_filing/
git commit -m "Convert Studio customizations to module"
git push origin production
```

## AI Agent Automation Patterns

### Pattern 1: Field Generation

```python
def generate_studio_field(model, field_name, field_type, **kwargs):
    """Generate Studio-compatible field definition"""
    field_xml = f"""
    <record id="field_{model}_{field_name}" model="ir.model.fields">
        <field name="name">x_{field_name}</field>
        <field name="model_id" ref="model_{model}"/>
        <field name="field_description">{kwargs.get('label', field_name)}</field>
        <field name="ttype">{field_type}</field>
        <field name="required">{kwargs.get('required', False)}</field>
        <field name="store">True</field>
    </record>
    """
    return field_xml
```

### Pattern 2: View Modification

```python
def add_field_to_view(model, view_id, field_name, position='after', anchor_field=None):
    """Generate view inheritance to add field"""
    view_xml = f"""
    <record id="view_{model}_{view_id}_inherit" model="ir.ui.view">
        <field name="name">{model}.{view_id}.inherit</field>
        <field name="model">{model}</field>
        <field name="inherit_id" ref="{view_id}"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='{anchor_field}']" position="{position}">
                <field name="x_{field_name}"/>
            </xpath>
        </field>
    </record>
    """
    return view_xml
```

### Pattern 3: Automated Action Creation

```python
def create_scheduled_action(name, model, interval_days, code):
    """Generate scheduled action XML"""
    action_xml = f"""
    <record id="action_{name.lower().replace(' ', '_')}" model="base.automation">
        <field name="name">{name}</field>
        <field name="model_id" ref="model_{model}"/>
        <field name="trigger">on_time</field>
        <field name="interval_number">{interval_days}</field>
        <field name="interval_type">days</field>
        <field name="code">{code}</field>
    </record>
    """
    return action_xml
```

## Studio Limitations

### What Studio Cannot Do

❌ **Complex Python logic**: Multi-step computations, external API calls  
❌ **Performance optimization**: Database indexing, query optimization  
❌ **Custom widgets**: JavaScript/OWL components  
❌ **Advanced security**: Custom access control logic  
❌ **Data migrations**: Upgrade scripts  
❌ **Unit tests**: Automated testing  
❌ **External integrations**: Third-party API connections

### Solutions

**For limitations above:**
1. Export Studio customizations
2. Convert to custom module
3. Add Python code for complex features
4. Version control for team collaboration
5. Deploy via git

## Best Practices

### 1. Naming Conventions

**Studio fields:**
- Prefix: `x_` (automatic)
- Format: `x_descriptive_name`
- Example: `x_manager_code`, `x_filing_deadline`

**Custom module fields:**
- No prefix
- Format: `descriptive_name`
- Example: `agency_code`, `filing_deadline`

### 2. Migration Path

**Studio → Custom Module:**
1. Design in Studio (fast iteration)
2. Test with users
3. Export when stable
4. Convert to custom module
5. Add Python enhancements
6. Deploy

### 3. Documentation

**Always document:**
- Why customization was needed
- Business logic behind fields
- Workflow explanations
- User instructions

### 4. Testing

**Before exporting:**
- Test all fields
- Verify computed values
- Check automated actions
- Validate access rights
- Test on different user roles

## Integration with AI Agent

### AI-Assisted Studio Configuration

**Workflow:**
1. User describes requirement
2. AI generates Studio configuration XML
3. User imports via Studio or as module
4. AI helps test and refine
5. Export as final module

**Example Prompt:**
```
"Create Studio fields for tracking BIR filing status:
- Agency (selection: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- Filing Period (date)
- Status (selection: Draft, Ready, Filed, Paid)
- Amount Due (monetary)"
```

**AI Response:**
```xml
<!-- Generated Studio configuration -->
<odoo>
    <record id="field_bir_filing_agency" model="ir.model.fields">
        <!-- Field definition -->
    </record>
    <!-- More fields... -->
</odoo>
```

## Practical Example: Finance SSC

### Requirement

"Add fields to track multi-agency month-end closing status"

### Studio Solution

**Add to existing month-end module:**
1. **Agency Field**: Selection (RIM, CKVC, etc.)
2. **Closing Status**: Selection (Open, In Progress, Completed)
3. **Completion %**: Progress bar
4. **Tasks Remaining**: Integer
5. **Last Updated**: Datetime

**Automated Actions:**
- Send reminder if closing not started 3 days before deadline
- Notify finance manager when agency marks as completed
- Create dashboard widget showing status across agencies

### Export & Enhance

**Export from Studio → Add Python:**
```python
class MonthEndClosing(models.Model):
    _inherit = 'month.end.closing'
    
    @api.depends('task_ids.state')
    def _compute_completion_percentage(self):
        """Calculate completion % from task status"""
        for record in self:
            total_tasks = len(record.task_ids)
            if total_tasks:
                completed = len(record.task_ids.filtered(lambda t: t.state == 'done'))
                record.completion_percentage = (completed / total_tasks) * 100
            else:
                record.completion_percentage = 0.0
```

## Resources

- [Odoo Studio Documentation](https://www.odoo.com/documentation/19.0/applications/studio.html)
- [Studio Video Tutorials](https://www.odoo.com/slides/studio-31)
- [Studio Community Forum](https://www.odoo.com/forum/help-1)

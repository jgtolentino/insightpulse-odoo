---
name: Travel Expense Module
description: Generate SAP Concur alternative travel expense module for InsightPulse AI
---

# Travel Expense Management Module Generator

Generate a comprehensive Odoo 19 module for travel expense management as a SAP Concur alternative.

## Module Specification

**Module Name:** `ipai_travel_expense`
**Category:** Accounting/Finance
**Version:** 19.0.1.0.0
**Dependencies:** base, account, hr, hr_expense, ipai_expense, ipai_approvals

## Core Features

### 1. Travel Request Workflow
**Model:** `ipai.travel.request`

```python
# States: draft → submitted → approved → booked → in_progress → completed → cancelled
```

**Fields:**
- Request number (auto-generated)
- Employee (Many2one to hr.employee)
- Trip purpose (Text)
- Destination (Char)
- Start date / End date (Date)
- Estimated cost (Monetary with currency_id)
- Travel type (Selection: domestic, international)
- Transportation (Selection: flight, bus, car_rental, personal_vehicle)
- Accommodation needed (Boolean)
- State (Selection)
- Approval history (One2many)

**Methods:**
- `action_submit()` - Submit for approval
- `action_approve()` - Approve request
- `action_book()` - Mark as booked
- `action_start()` - Start travel
- `action_complete()` - Complete travel
- `action_cancel()` - Cancel request

### 2. Expense Report (Extend existing ipai_expense)
**Model:** `ipai.expense.report` (inherit)

**Additional Fields:**
- Travel request (Many2one to ipai.travel.request)
- Is travel expense (Boolean, computed)
- Per diem policy (Many2one to ipai.travel.perdiem.policy)
- Per diem amount (Monetary, computed)

### 3. Expense Line (Extend existing)
**Model:** `ipai.expense.line` (inherit)

**Additional Fields:**
- Travel request (related to report_id.travel_request_id)
- Expense category (Selection: transport, accommodation, meals, other)
- Is per diem eligible (Boolean)
- Receipt required (Boolean, computed based on policy)
- OCR data (JSON field)

### 4. Policy Engine
**Model:** `ipai.travel.policy`

**Purpose:** Define expense policies and limits

**Fields:**
- Policy name
- Active (Boolean)
- Company (Many2one)
- Employee categories (Many2many to hr.employee.category)
- Travel type (Selection: domestic, international)
- Maximum amounts by category (One2many to policy rules)
- Receipt requirements (JSON: {min_amount, required_fields})
- Per diem rules (One2many)
- Approval matrix (One2many)

**Methods:**
- `validate_expense()` - Check expense against policy
- `get_approval_sequence()` - Get approval chain
- `compute_per_diem()` - Calculate per diem allowance

### 5. Approval Matrix
**Model:** `ipai.travel.approval` (inherit ipai_approvals)

**Rules:**
- Amount < 5,000: Direct manager
- Amount 5,000-25,000: Manager → Department Head
- Amount 25,000-100,000: Manager → Dept Head → Finance Director
- Amount > 100,000: Manager → Dept Head → Finance → CEO

**Escalation:**
- 3 days without response → notify next level
- 7 days → auto-escalate to next approver

### 6. Per Diem Calculation
**Model:** `ipai.travel.perdiem.policy`

**Fields:**
- Destination type (Selection: local, domestic, international)
- Country/City (Char)
- Daily rate (Monetary)
- Meal allowance (Monetary)
- Incidental allowance (Monetary)
- Effective date (Date)

### 7. GL Posting Integration
**Model:** `account.move` (inherit)

**Features:**
- Auto-generate journal entries from approved expenses
- Map expense categories to GL accounts
- Split personal vs company expenses
- Handle multi-currency conversions
- Generate withholding tax entries (BIR compliance)

### 8. BIR Compliance (Philippines)
**Model:** `ipai.travel.bir.report`

**Features:**
- Form 1604-CF generation (withholding tax certificate)
- Track deductible vs non-deductible expenses
- VAT input tracking
- Monthly summary reports
- ATP (Authorization to Print) tracking

## Views

### Travel Request Views

**Form View:**
```xml
<form>
    <header>
        <button name="action_submit" type="object" string="Submit"
                class="btn-primary" states="draft"/>
        <button name="action_approve" type="object" string="Approve"
                class="btn-success" states="submitted"
                groups="ipai_travel_expense.group_travel_manager"/>
        <button name="action_book" type="object" string="Mark as Booked"
                states="approved"/>
        <field name="state" widget="statusbar"/>
    </header>
    <sheet>
        <div class="oe_title">
            <h1><field name="name"/></h1>
        </div>
        <group>
            <group>
                <field name="employee_id"/>
                <field name="trip_purpose"/>
                <field name="destination"/>
                <field name="travel_type"/>
            </group>
            <group>
                <field name="start_date"/>
                <field name="end_date"/>
                <field name="estimated_cost" widget="monetary"/>
                <field name="currency_id" invisible="1"/>
            </group>
        </group>
        <notebook>
            <page string="Transportation">
                <field name="transportation"/>
                <field name="accommodation_needed"/>
            </page>
            <page string="Policy Compliance">
                <field name="policy_id"/>
                <field name="policy_validation_message"/>
            </page>
            <page string="Approval History">
                <field name="approval_ids"/>
            </page>
        </notebook>
    </sheet>
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

**Kanban View:**
```xml
<kanban default_group_by="state">
    <field name="name"/>
    <field name="employee_id"/>
    <field name="destination"/>
    <field name="start_date"/>
    <field name="estimated_cost"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <div class="oe_kanban_content">
                    <div><strong><field name="name"/></strong></div>
                    <div><field name="employee_id"/></div>
                    <div><field name="destination"/> - <field name="start_date"/></div>
                    <div><field name="estimated_cost" widget="monetary"/></div>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

**Tree View:**
```xml
<tree>
    <field name="name"/>
    <field name="employee_id"/>
    <field name="destination"/>
    <field name="start_date"/>
    <field name="end_date"/>
    <field name="estimated_cost" widget="monetary"/>
    <field name="state" decoration-info="state=='draft'"
           decoration-warning="state=='submitted'"
           decoration-success="state=='approved'"/>
</tree>
```

### Dashboard View
```xml
<dashboard>
    <view type="pivot">
        <field name="travel_type"/>
        <field name="state"/>
        <field name="estimated_cost" type="measure"/>
    </view>
    <view type="graph">
        <field name="start_date" interval="month"/>
        <field name="estimated_cost" type="measure"/>
    </view>
</dashboard>
```

## Security

### Access Groups
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_travel_request_user,travel.request.user,model_ipai_travel_request,base.group_user,1,1,1,0
access_travel_request_manager,travel.request.manager,model_ipai_travel_request,ipai_travel_expense.group_travel_manager,1,1,1,1
access_travel_policy_user,travel.policy.user,model_ipai_travel_policy,base.group_user,1,0,0,0
access_travel_policy_manager,travel.policy.manager,model_ipai_travel_policy,ipai_travel_expense.group_travel_manager,1,1,1,1
```

### Record Rules
```xml
<!-- Users can only see own requests unless manager -->
<record id="travel_request_user_rule" model="ir.rule">
    <field name="name">User Own Travel Requests</field>
    <field name="model_id" ref="model_ipai_travel_request"/>
    <field name="domain_force">[('employee_id.user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>

<!-- Managers can see all requests -->
<record id="travel_request_manager_rule" model="ir.rule">
    <field name="name">Manager All Travel Requests</field>
    <field name="model_id" ref="model_ipai_travel_request"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('ipai_travel_expense.group_travel_manager'))]"/>
</record>
```

## Integration Points

### PaddleOCR for Receipt Scanning
```python
def ocr_receipt(self, image_data):
    """Extract receipt data using PaddleOCR service"""
    ocr_url = os.getenv('PADDLEOCR_URL')
    response = requests.post(f"{ocr_url}/api/ocr/receipt", files={'file': image_data})

    if response.status_code == 200:
        data = response.json()
        # Auto-fill expense line
        self.write({
            'date': data.get('date'),
            'description': data.get('vendor'),
            'amount': data.get('total_amount'),
            'tax_amount': data.get('vat_amount'),
        })

    return response.json()
```

### Supabase for Document Storage
```python
def upload_receipt(self, file_data, filename):
    """Upload receipt to Supabase storage"""
    supabase = self._get_supabase_client()

    file_path = f"travel-receipts/{self.travel_request_id.id}/{filename}"
    supabase.storage.from_('receipts').upload(file_path, file_data)

    public_url = supabase.storage.from_('receipts').get_public_url(file_path)
    self.receipt_url = public_url
```

### BIR Form Generation
```python
def generate_1604cf(self, period_start, period_end):
    """Generate BIR Form 1604-CF for withholding tax"""
    expenses = self.env['ipai.expense.line'].search([
        ('date', '>=', period_start),
        ('date', '<=', period_end),
        ('state', '=', 'paid'),
        ('withholding_tax_amount', '>', 0),
    ])

    # Generate form data
    form_data = {
        'tin': self.env.company.vat,
        'period': period_start.strftime('%Y-%m'),
        'total_amount': sum(expenses.mapped('amount')),
        'tax_withheld': sum(expenses.mapped('withholding_tax_amount')),
    }

    return self._render_bir_form('1604-CF', form_data)
```

## Mobile-Optimized Views

```xml
<!-- Mobile form view for quick expense entry -->
<record id="view_expense_line_mobile_form" model="ir.ui.view">
    <field name="name">ipai.expense.line.mobile.form</field>
    <field name="model">ipai.expense.line</field>
    <field name="priority">20</field>
    <field name="arch" type="xml">
        <form>
            <sheet>
                <group>
                    <field name="date"/>
                    <field name="category"/>
                    <field name="amount"/>
                    <field name="description"/>
                </group>
                <group>
                    <button name="action_ocr_receipt" type="object"
                            string="Scan Receipt" class="btn-primary"/>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

## Analytics & Dashboards

### Dashboard Components (Superset Integration)
1. **Travel Spend Analytics**
   - Total spend by month
   - Spend by employee
   - Spend by destination
   - Spend by category

2. **Policy Compliance**
   - Policy violations by type
   - Average approval time
   - Pending approvals by age
   - Escalated requests

3. **Per Diem Tracking**
   - Per diem vs actual spend
   - Savings by employee
   - Reimbursement timeline

## Testing Requirements

```python
class TestTravelRequest(TransactionCase):

    def test_submit_travel_request(self):
        """Test travel request submission"""
        request = self.env['ipai.travel.request'].create({
            'employee_id': self.employee.id,
            'destination': 'Manila',
            'start_date': '2025-11-01',
            'end_date': '2025-11-03',
            'trip_purpose': 'Client meeting',
            'estimated_cost': 15000,
        })
        request.action_submit()
        self.assertEqual(request.state, 'submitted')

    def test_policy_validation(self):
        """Test expense policy validation"""
        # Create expense exceeding policy limit
        expense = self.env['ipai.expense.line'].create({
            'date': '2025-11-01',
            'category': 'meals',
            'amount': 5000,  # Exceeds policy limit
        })
        with self.assertRaises(ValidationError):
            expense.validate_against_policy()
```

## Documentation

### README.md Contents
1. Overview of travel expense management
2. Installation instructions
3. Configuration steps
4. User guide with screenshots
5. Administrator guide
6. API documentation
7. Troubleshooting

## Performance Considerations

- Index frequently queried fields: employee_id, state, start_date
- Use stored computed fields for aggregations
- Batch approval notifications
- Lazy load receipt images
- Cache policy rules

## Deployment Checklist

- [ ] Install module dependencies
- [ ] Configure PaddleOCR URL
- [ ] Configure Supabase credentials
- [ ] Set up approval workflows
- [ ] Define travel policies
- [ ] Configure GL accounts
- [ ] Import per diem rates
- [ ] Set up user groups and permissions
- [ ] Test OCR functionality
- [ ] Test BIR form generation
- [ ] Train users

---

**Generate this module following OCA guidelines, InsightPulse AI standards, and the patterns from existing ipai_* modules.**

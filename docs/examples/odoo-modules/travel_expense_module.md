# Example: Travel & Expense Management Module

Self-hosted alternative to SAP Concur for travel requests and expense management.

## Cost Savings

**SAP Concur Pricing:**
- Standard: $8/user/month
- Professional: $12/user/month
- 100 users = $14,400/year

**This Module:** $0 (self-hosted on existing Odoo infrastructure)

**Annual Savings:** $14,400+

## Module Structure

```
travel_expense_management/
├── __manifest__.py
├── models/
│   ├── travel_request.py
│   ├── travel_policy.py
│   ├── expense_report.py
│   ├── expense_line.py
│   └── res_config_settings.py
├── views/
│   ├── travel_request_views.xml
│   ├── expense_report_views.xml
│   ├── travel_policy_views.xml
│   └── menu_views.xml
├── wizards/
│   ├── expense_approval_wizard.py
│   └── expense_gl_posting_wizard.py
├── security/
│   ├── ir.model.access.csv
│   └── security_groups.xml
├── data/
│   ├── default_policies.xml
│   ├── expense_categories.xml
│   └── email_templates.xml
└── static/
    └── src/
        └── js/
            └── receipt_ocr_widget.js
```

## Key Features

### 1. Travel Request Workflow

```python
class TravelRequest(models.Model):
    _name = 'travel.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', required=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    agency_code = fields.Selection([
        ('RIM', 'RIM'), ('CKVC', 'CKVC'), ('BOM', 'BOM'), ('JPAL', 'JPAL'),
        ('JLI', 'JLI'), ('JAP', 'JAP'), ('LAS', 'LAS'), ('RMQB', 'RMQB'),
    ], string='Agency', required=True)
    
    # Travel Details
    destination = fields.Char(string='Destination', required=True)
    purpose = fields.Text(string='Purpose', required=True)
    departure_date = fields.Datetime(string='Departure Date', required=True)
    return_date = fields.Datetime(string='Return Date', required=True)
    duration_days = fields.Integer(string='Duration (Days)', compute='_compute_duration')
    
    # Cost Estimates
    estimated_airfare = fields.Monetary(string='Estimated Airfare')
    estimated_accommodation = fields.Monetary(string='Estimated Accommodation')
    estimated_meals = fields.Monetary(string='Estimated Meals')
    estimated_transportation = fields.Monetary(string='Estimated Transportation')
    estimated_total = fields.Monetary(string='Estimated Total', compute='_compute_estimated_total')
    
    # Budget & Approval
    budget_code = fields.Char(string='Budget Code')
    policy_id = fields.Many2one('travel.policy', string='Travel Policy')
    policy_compliant = fields.Boolean(string='Policy Compliant', compute='_compute_policy_compliance')
    policy_violations = fields.Text(string='Policy Violations')
    
    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('manager_approved', 'Manager Approved'),
        ('finance_approved', 'Finance Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True)
    
    @api.depends('departure_date', 'return_date')
    def _compute_duration(self):
        for record in self:
            if record.departure_date and record.return_date:
                delta = record.return_date - record.departure_date
                record.duration_days = delta.days
            else:
                record.duration_days = 0
    
    def action_submit(self):
        self.write({'state': 'submitted'})
        # Send notification to manager
        
    def action_manager_approve(self):
        self.write({'state': 'manager_approved'})
        # Send notification to finance
        
    def action_finance_approve(self):
        self.write({'state': 'finance_approved'})
        # Send confirmation email to employee
```

### 2. Expense Report with OCR

```python
class ExpenseReport(models.Model):
    _name = 'expense.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Reference', required=True, default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    travel_request_id = fields.Many2one('travel.request', string='Related Travel Request')
    
    # Report Details
    report_date = fields.Date(string='Report Date', required=True, default=fields.Date.today)
    submission_date = fields.Date(string='Submission Date')
    
    # Expense Lines
    expense_line_ids = fields.One2many('expense.line', 'report_id', string='Expense Lines')
    
    # Totals
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_total_amount')
    approved_amount = fields.Monetary(string='Approved Amount')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    # Policy Validation
    policy_violations = fields.Text(string='Policy Violations', compute='_compute_policy_violations')
    
    # Workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('manager_review', 'Manager Review'),
        ('finance_review', 'Finance Review'),
        ('approved', 'Approved'),
        ('posted', 'Posted to GL'),
        ('rejected', 'Rejected'),
    ], default='draft', tracking=True)
    
    @api.depends('expense_line_ids.amount')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.amount for line in record.expense_line_ids)


class ExpenseLine(models.Model):
    _name = 'expense.line'
    
    report_id = fields.Many2one('expense.report', string='Expense Report', required=True)
    
    # Expense Details
    date = fields.Date(string='Date', required=True)
    category_id = fields.Many2one('expense.category', string='Category', required=True)
    description = fields.Text(string='Description')
    amount = fields.Monetary(string='Amount', required=True)
    currency_id = fields.Many2one('res.currency', related='report_id.currency_id')
    
    # Receipt
    receipt_image = fields.Binary(string='Receipt Image', attachment=True)
    receipt_filename = fields.Char(string='Receipt Filename')
    ocr_processed = fields.Boolean(string='OCR Processed', default=False)
    ocr_data = fields.Text(string='OCR Data')
    
    # GL Posting
    account_id = fields.Many2one('account.account', string='GL Account')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    
    # Policy Validation
    policy_limit = fields.Monetary(string='Policy Limit', related='category_id.daily_limit')
    exceeds_limit = fields.Boolean(string='Exceeds Limit', compute='_compute_exceeds_limit')
    
    @api.depends('amount', 'policy_limit')
    def _compute_exceeds_limit(self):
        for record in self:
            record.exceeds_limit = record.amount > record.policy_limit if record.policy_limit else False
    
    def action_process_receipt_ocr(self):
        """Process receipt image with PaddleOCR"""
        self.ensure_one()
        
        if not self.receipt_image:
            raise ValidationError(_('No receipt image to process'))
        
        # Call PaddleOCR service
        ocr_service = self.env['paddleocr.service']
        result = ocr_service.extract_receipt_data(self.receipt_image)
        
        # Update expense line with OCR data
        self.write({
            'ocr_processed': True,
            'ocr_data': str(result),
            'amount': result.get('total_amount', self.amount),
            'date': result.get('date', self.date),
            'description': result.get('vendor_name', self.description),
        })
```

### 3. Policy Configuration

```python
class TravelPolicy(models.Model):
    _name = 'travel.policy'
    
    name = fields.Char(string='Policy Name', required=True)
    active = fields.Boolean(default=True)
    
    # Limits
    daily_meal_limit = fields.Monetary(string='Daily Meal Limit')
    accommodation_limit = fields.Monetary(string='Accommodation Limit')
    
    # Rules
    requires_manager_approval = fields.Boolean(string='Requires Manager Approval', default=True)
    requires_finance_approval = fields.Boolean(string='Requires Finance Approval', default=True)
    requires_advance_booking_days = fields.Integer(string='Advance Booking Days', default=7)
    
    # Expense Categories
    category_ids = fields.One2many('expense.category', 'policy_id', string='Expense Categories')


class ExpenseCategory(models.Model):
    _name = 'expense.category'
    
    name = fields.Char(string='Category', required=True)
    policy_id = fields.Many2one('travel.policy', string='Policy')
    daily_limit = fields.Monetary(string='Daily Limit')
    requires_receipt = fields.Boolean(string='Requires Receipt', default=True)
    account_id = fields.Many2one('account.account', string='Default GL Account')
```

## Integration with PaddleOCR

### Receipt Processing Workflow

1. **Upload Receipt**: Employee takes photo of receipt
2. **OCR Processing**: PaddleOCR extracts:
   - Vendor name
   - Date
   - Total amount
   - Line items
   - Tax amounts
3. **Auto-Fill**: Expense line populated automatically
4. **Manual Review**: Employee verifies and adjusts if needed
5. **Approval**: Manager reviews and approves

### PaddleOCR Service Integration

```python
class PaddleOCRService(models.AbstractModel):
    _name = 'paddleocr.service'
    
    def extract_receipt_data(self, image_binary):
        """Extract data from receipt image using PaddleOCR"""
        import base64
        import requests
        
        # Convert binary to base64
        image_base64 = base64.b64encode(image_binary).decode('utf-8')
        
        # Call PaddleOCR API
        paddleocr_url = self.env['ir.config_parameter'].sudo().get_param('paddleocr.api.url')
        response = requests.post(
            f"{paddleocr_url}/extract-receipt",
            json={'image': image_base64}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise ValidationError(_('Failed to process receipt with OCR'))
```

## GL Posting Automation

```python
def action_post_to_gl(self):
    """Post approved expenses to General Ledger"""
    self.ensure_one()
    
    if self.state != 'approved':
        raise ValidationError(_('Only approved expense reports can be posted'))
    
    # Create journal entry
    move_vals = {
        'journal_id': self.env.ref('account.expenses_journal').id,
        'date': self.report_date,
        'ref': self.name,
        'line_ids': []
    }
    
    # Debit expense accounts
    for line in self.expense_line_ids:
        move_vals['line_ids'].append((0, 0, {
            'account_id': line.account_id.id,
            'analytic_account_id': line.analytic_account_id.id,
            'debit': line.amount,
            'credit': 0.0,
            'name': line.description,
        }))
    
    # Credit payable account
    payable_account = self.employee_id.address_home_id.property_account_payable_id
    move_vals['line_ids'].append((0, 0, {
        'account_id': payable_account.id,
        'debit': 0.0,
        'credit': self.approved_amount,
        'name': f'Expense reimbursement: {self.employee_id.name}',
    }))
    
    # Create and post the move
    move = self.env['account.move'].create(move_vals)
    move.action_post()
    
    self.write({'state': 'posted'})
```

## Email Notifications

Configured in `data/email_templates.xml`:

```xml
<record id="email_travel_request_submitted" model="mail.template">
    <field name="name">Travel Request: Submitted</field>
    <field name="model_id" ref="model_travel_request"/>
    <field name="subject">Travel Request ${object.name} - Pending Approval</field>
    <field name="body_html"><![CDATA[
        <p>Hello ${object.employee_id.parent_id.name},</p>
        <p>${object.employee_id.name} has submitted a travel request:</p>
        <ul>
            <li>Destination: ${object.destination}</li>
            <li>Dates: ${object.departure_date} to ${object.return_date}</li>
            <li>Estimated Cost: ${object.estimated_total}</li>
        </ul>
        <p>Please review and approve in Odoo.</p>
    ]]></field>
</record>
```

## Dashboard & Reports

### Travel Dashboard

- Pending travel requests
- Approved travel requests
- Travel expenses by category
- Policy compliance metrics
- Budget utilization

### Expense Reports

- Expense report by employee
- Expense analysis by category
- Policy violation report
- Aging report for pending approvals

## Mobile App Support

Odoo mobile app can:
- Submit travel requests on the go
- Take receipt photos immediately
- Upload expense reports from field
- Approve requests from mobile

## Benefits for Finance SSC

1. **Cost Savings**: $14,400/year vs SAP Concur
2. **Multi-Agency Support**: Handle RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB
3. **Automated OCR**: Reduce manual data entry
4. **Policy Enforcement**: Automatic validation
5. **GL Integration**: Seamless accounting
6. **Audit Trail**: Complete tracking
7. **Customizable**: Adapt to specific needs
8. **Self-Hosted**: No vendor lock-in

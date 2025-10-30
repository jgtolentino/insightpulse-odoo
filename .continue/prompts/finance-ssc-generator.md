---
name: Finance SSC Module
description: Generate Finance Shared Service Center automation for multi-agency operations
---

# Finance Shared Service Center (SSC) Automation

Generate comprehensive Odoo 19 modules for Finance SSC operations covering 8 agencies with Philippines BIR compliance.

## Module Specification

**Module Name:** `ipai_finance_ssc`
**Category:** Accounting/Finance
**Version:** 19.0.1.0.0
**Dependencies:** base, account, account_reconciliation, hr, ipai_approvals

## Multi-Agency Structure

### Agencies
1. **RIM** - Research & Impact Management
2. **CKVC** - Capital & Ventures Corp
3. **BOM** - Business Operations & Management
4. **JPAL** - J-PAL Southeast Asia
5. **JLI** - J-PAL Leadership Initiative
6. **JAP** - J-PAL Asia Programs
7. **LAS** - Leadership & Advisory Services
8. **RMQB** - Risk Management & Quality Board

## Core Features

### 1. Agency Management
**Model:** `ipai.ssc.agency`

**Fields:**
- Agency code (Char, required, unique)
- Agency name (Char, required)
- Company (Many2one to res.company)
- Currency (Many2one to res.currency)
- Parent agency (Many2one to self, for hierarchies)
- Active (Boolean)
- TIN (Char, BIR Tax Identification Number)
- ATP numbers (One2many, Authorization to Print)
- GL account prefix (Char, for account mapping)

**Methods:**
- `get_month_end_tasks()` - Get all tasks for this agency
- `get_bir_compliance_status()` - Check BIR filing status
- `consolidate_financials()` - Prepare consolidated reports

### 2. Month-End Closing Workflow
**Model:** `ipai.ssc.month.closing`

**States:** `draft → in_progress → review → completed → locked`

**Fields:**
- Closing period (Date: YYYY-MM)
- Agency (Many2one to ipai.ssc.agency)
- State (Selection)
- Task lines (One2many to ipai.ssc.closing.task)
- Assigned to (Many2one to res.users)
- Deadline (Datetime)
- Completion percentage (Float, computed)
- Issues count (Integer, computed)
- Sign-off by (Many2one to res.users)
- Sign-off date (Datetime)

**Key Tasks (per agency):**
1. Bank reconciliation
2. Accounts receivable aging
3. Accounts payable validation
4. Expense accruals
5. Revenue recognition
6. Depreciation posting
7. Inter-company eliminations
8. Trial balance validation
9. Management reports generation
10. BIR compliance check

**Methods:**
- `action_start_closing()` - Initialize month-end tasks
- `action_complete_task()` - Mark task complete
- `action_review()` - Submit for review
- `action_approve()` - Approve closing
- `action_lock()` - Lock period
- `send_deadline_reminders()` - Alert on overdue tasks

### 3. Task Management
**Model:** `ipai.ssc.closing.task`

**Fields:**
- Task name (Char)
- Task type (Selection: bank_recon, ar_aging, ap_validation, etc.)
- Closing period (Many2one to ipai.ssc.month.closing)
- Agency (related)
- Assigned to (Many2one to res.users)
- Priority (Selection: low, medium, high, urgent)
- Deadline (Datetime)
- State (Selection: pending, in_progress, blocked, completed)
- Progress percentage (Integer)
- Dependencies (Many2many to self)
- Notes (Text)
- Checklist items (One2many to ipai.ssc.task.checklist)

**Methods:**
- `action_start()` - Start task
- `check_dependencies()` - Validate dependencies met
- `escalate()` - Escalate to manager
- `calculate_progress()` - Update progress %

### 4. Bank Reconciliation
**Model:** `account.bank.statement` (inherit)

**Additional Features:**
- Auto-match transactions using AI/ML
- OCR integration for bank statements (PaddleOCR)
- Multi-currency reconciliation
- Automated journal entry creation
- Exception reporting

**Methods:**
- `auto_reconcile()` - Match transactions automatically
- `suggest_matches()` - AI-powered suggestions
- `generate_reconciliation_report()` - Export to Excel

### 5. Trial Balance Validation
**Model:** `ipai.ssc.trial.balance`

**Features:**
- Generate trial balance by agency
- Compare month-over-month variances
- Flag unusual movements (>20% variance)
- Validate debit = credit
- Export to Superset for analysis
- Link to supporting documents

**Fields:**
- Period (Date)
- Agency (Many2one)
- Account code (Many2one to account.account)
- Account name (related)
- Debit (Monetary)
- Credit (Monetary)
- Balance (Monetary, computed)
- Prior period balance (Monetary)
- Variance (Monetary, computed)
- Variance percentage (Float, computed)
- Flagged (Boolean, computed if variance > threshold)

### 6. Inter-Company Eliminations
**Model:** `ipai.ssc.intercompany.elimination`

**Purpose:** Eliminate inter-agency transactions for consolidated reporting

**Fields:**
- Period (Date)
- Source agency (Many2one)
- Target agency (Many2one)
- Transaction type (Selection: loan, expense_allocation, revenue_share)
- Amount (Monetary)
- Status (Selection: identified, matched, eliminated, unmatched)
- Source entry (Many2one to account.move)
- Target entry (Many2one to account.move)
- Elimination entry (Many2one to account.move)

**Methods:**
- `identify_intercompany_transactions()` - Find matching entries
- `create_elimination_entry()` - Generate journal entry
- `validate_elimination()` - Check if balanced

### 7. Automated Journal Entry Generation
**Model:** `ipai.ssc.journal.template`

**Purpose:** Auto-generate recurring journal entries

**Fields:**
- Template name (Char)
- Template type (Selection: accrual, depreciation, allocation)
- Agency (Many2one)
- Journal (Many2one to account.journal)
- Frequency (Selection: monthly, quarterly, annual)
- Account lines (One2many)
- Computation method (Selection: fixed, percentage, formula)
- Active (Boolean)

**Methods:**
- `generate_entry()` - Create journal entry for period
- `schedule_generation()` - Queue for automated processing

### 8. BIR Compliance Module
**Model:** `ipai.ssc.bir.filing`

**Forms Supported:**
- **1601-C** - Monthly Withholding Tax (Compensation)
- **1702-RT** - Annual Income Tax Return (Regular)
- **1702-EX** - Annual Income Tax Return (Exempt)
- **2550Q** - Quarterly VAT Return
- **2550M** - Monthly VAT Return (if applicable)
- **1604-CF** - Certificate of Withholding Tax at Source

**Fields:**
- Filing period (Date)
- Agency (Many2one)
- Form type (Selection)
- Filing deadline (Date, computed based on form type)
- Status (Selection: draft, ready, filed, accepted, rejected)
- Form data (JSON, structured data for form)
- PDF attachment (Binary)
- Filed by (Many2one to res.users)
- Filed date (Datetime)
- Confirmation number (Char)

**Methods:**
- `generate_form()` - Create form from transaction data
- `validate_form()` - Check completeness
- `export_to_bir_format()` - Export in BIR-accepted format
- `mark_as_filed()` - Record filing
- `send_reminder()` - Alert before deadline

### 9. ATP (Authorization to Print) Tracking
**Model:** `ipai.ssc.bir.atp`

**Purpose:** Track BIR authorization to print receipts/invoices

**Fields:**
- ATP number (Char, required)
- Agency (Many2one)
- Document type (Selection: sales_invoice, official_receipt)
- Series range start (Char)
- Series range end (Char)
- Valid from (Date)
- Valid until (Date)
- Current number (Char)
- Status (Selection: active, expired, used_up)

**Methods:**
- `get_next_number()` - Get next number in sequence
- `check_expiry()` - Alert if near expiry
- `validate_series()` - Ensure within range

### 10. Consolidated Reporting
**Model:** `ipai.ssc.consolidated.report`

**Reports:**
- Consolidated Statement of Financial Position (Balance Sheet)
- Consolidated Statement of Comprehensive Income (P&L)
- Consolidated Cash Flow Statement
- Consolidated Statement of Changes in Equity
- Notes to Financial Statements

**Fields:**
- Report period (Date)
- Report type (Selection)
- Agencies included (Many2many)
- Elimination entries applied (Boolean)
- Report data (JSON)
- PDF attachment (Binary)
- Generated by (Many2one to res.users)
- Generated date (Datetime)

## Views

### Month-End Closing Dashboard
```xml
<dashboard>
    <view type="kanban" group_by="agency_id">
        <card>
            <field name="agency_id"/>
            <field name="period"/>
            <field name="completion_percentage" widget="progressbar"/>
            <field name="deadline"/>
            <field name="state" widget="badge"/>
        </card>
    </view>
</dashboard>
```

### Task Board (Kanban)
```xml
<kanban default_group_by="state" quick_create="false">
    <field name="task_name"/>
    <field name="agency_id"/>
    <field name="assigned_to"/>
    <field name="deadline"/>
    <field name="priority"/>
    <templates>
        <t t-name="kanban-box">
            <div class="oe_kanban_card">
                <div class="oe_kanban_content">
                    <strong><field name="task_name"/></strong>
                    <div><field name="agency_id"/> - <field name="assigned_to"/></div>
                    <div>Deadline: <field name="deadline"/></div>
                    <field name="priority" widget="priority"/>
                    <field name="progress_percentage" widget="progressbar"/>
                </div>
            </div>
        </t>
    </templates>
</kanban>
```

### Trial Balance Pivot View
```xml
<pivot>
    <field name="agency_id" type="row"/>
    <field name="account_id" type="row"/>
    <field name="debit" type="measure"/>
    <field name="credit" type="measure"/>
    <field name="balance" type="measure"/>
</pivot>
```

### BIR Filing Calendar View
```xml
<calendar date_start="filing_deadline" color="status">
    <field name="form_type"/>
    <field name="agency_id"/>
</calendar>
```

## Automation & Scheduled Actions

### Daily Tasks
```python
# Check for upcoming deadlines (run daily at 8 AM)
def _cron_check_deadlines(self):
    """Send reminders for tasks due within 24 hours"""
    tomorrow = fields.Date.today() + timedelta(days=1)
    overdue_tasks = self.env['ipai.ssc.closing.task'].search([
        ('deadline', '<=', tomorrow),
        ('state', '!=', 'completed'),
    ])
    for task in overdue_tasks:
        task.send_reminder()
```

### Weekly Tasks
```python
# Generate weekly status report (run Friday 5 PM)
def _cron_weekly_status_report(self):
    """Send weekly progress report to managers"""
    closings = self.env['ipai.ssc.month.closing'].search([
        ('state', 'in', ['in_progress', 'review']),
    ])
    for closing in closings:
        closing.send_status_report()
```

### Monthly Tasks
```python
# Initialize next month closing (run last day of month)
def _cron_initialize_month_closing(self):
    """Create month-end closing records for all agencies"""
    next_month = fields.Date.today() + timedelta(days=32)
    next_month = next_month.replace(day=1)

    for agency in self.env['ipai.ssc.agency'].search([('active', '=', True)]):
        self.env['ipai.ssc.month.closing'].create({
            'period': next_month,
            'agency_id': agency.id,
        })._generate_tasks()
```

### BIR Filing Reminders
```python
# Check BIR filing deadlines (run daily)
def _cron_bir_filing_reminders(self):
    """Alert for upcoming BIR filings"""
    filings = self.env['ipai.ssc.bir.filing'].search([
        ('filing_deadline', '<=', fields.Date.today() + timedelta(days=3)),
        ('status', '!=', 'filed'),
    ])
    for filing in filings:
        filing.send_deadline_alert()
```

## Integration Points

### Supabase for Document Storage
```python
def upload_bank_statement(self, file_data, filename):
    """Upload bank statement to Supabase"""
    supabase = self._get_supabase_client()

    file_path = f"bank-statements/{self.agency_id.code}/{self.period}/{filename}"
    supabase.storage.from_('finance-documents').upload(file_path, file_data)

    return supabase.storage.from_('finance-documents').get_public_url(file_path)
```

### PaddleOCR for Bank Statement Processing
```python
def ocr_bank_statement(self, image_data):
    """Extract transactions from bank statement image"""
    ocr_url = os.getenv('PADDLEOCR_URL')
    response = requests.post(
        f"{ocr_url}/api/ocr/bank-statement",
        files={'file': image_data}
    )

    if response.status_code == 200:
        transactions = response.json().get('transactions', [])
        self._create_statement_lines(transactions)
```

### Apache Superset Dashboards
```python
# Export data to Superset-compatible format
def export_to_superset(self):
    """Prepare data for Superset dashboard"""
    data = {
        'agencies': self._get_agency_metrics(),
        'tasks': self._get_task_metrics(),
        'bir_compliance': self._get_bir_status(),
    }

    # Insert into Supabase tables for Superset
    supabase = self._get_supabase_client()
    supabase.table('ssc_metrics').insert(data).execute()
```

## Security

### Access Groups
```csv
id,name,comment
group_ssc_user,SSC User,Basic access to own tasks
group_ssc_accountant,SSC Accountant,Can process transactions
group_ssc_manager,SSC Manager,Can approve closings
group_ssc_director,SSC Director,Full access + consolidated reporting
```

### Access Rights
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_closing_user,closing.user,model_ipai_ssc_month_closing,group_ssc_user,1,0,0,0
access_closing_accountant,closing.accountant,model_ipai_ssc_month_closing,group_ssc_accountant,1,1,1,0
access_closing_manager,closing.manager,model_ipai_ssc_month_closing,group_ssc_manager,1,1,1,1
```

### Record Rules
```xml
<!-- Accountants can only see assigned agencies -->
<record id="closing_accountant_rule" model="ir.rule">
    <field name="name">SSC Accountant Agency Access</field>
    <field name="model_id" ref="model_ipai_ssc_month_closing"/>
    <field name="domain_force">[('agency_id.accountant_ids', 'in', [user.id])]</field>
    <field name="groups" eval="[(4, ref('group_ssc_accountant'))]"/>
</record>
```

## Analytics & Dashboards (Superset)

### 1. Month-End Performance Dashboard
- Average days to close by agency
- Task completion rate
- Overdue tasks trend
- Bottleneck identification

### 2. BIR Compliance Dashboard
- Filing status by form type
- On-time filing rate
- Upcoming deadlines calendar
- Penalty tracking

### 3. Financial Metrics Dashboard
- Trial balance by agency
- Variance analysis
- Inter-company transactions
- Consolidated P&L

### 4. Team Performance Dashboard
- Tasks completed per user
- Average resolution time
- Workload distribution
- Productivity trends

## Testing Requirements

```python
class TestMonthEndClosing(TransactionCase):

    def test_initialize_closing(self):
        """Test month-end closing initialization"""
        closing = self.env['ipai.ssc.month.closing'].create({
            'period': '2025-11-01',
            'agency_id': self.agency_rim.id,
        })
        closing._generate_tasks()

        self.assertEqual(len(closing.task_ids), 10)  # 10 standard tasks
        self.assertEqual(closing.state, 'draft')

    def test_task_dependencies(self):
        """Test task dependency validation"""
        task1 = self.env['ipai.ssc.closing.task'].create({
            'task_name': 'Bank Reconciliation',
            'task_type': 'bank_recon',
        })
        task2 = self.env['ipai.ssc.closing.task'].create({
            'task_name': 'Trial Balance',
            'task_type': 'trial_balance',
            'dependency_ids': [(6, 0, [task1.id])],
        })

        # Should fail if dependency not completed
        with self.assertRaises(ValidationError):
            task2.action_start()

    def test_bir_form_generation(self):
        """Test BIR form generation"""
        filing = self.env['ipai.ssc.bir.filing'].create({
            'period': '2025-11-01',
            'agency_id': self.agency_rim.id,
            'form_type': '1601c',
        })
        filing.generate_form()

        self.assertIsNotNone(filing.form_data)
        self.assertEqual(filing.status, 'ready')
```

## Deployment Checklist

- [ ] Configure agencies (all 8)
- [ ] Set up GL account mappings per agency
- [ ] Configure BIR form templates
- [ ] Import ATP numbers
- [ ] Set up user groups and permissions
- [ ] Configure Supabase storage buckets
- [ ] Set up PaddleOCR service
- [ ] Create Superset dashboards
- [ ] Configure scheduled actions (crons)
- [ ] Import prior period trial balances
- [ ] Train SSC team members
- [ ] Test month-end workflow end-to-end
- [ ] Test BIR form generation
- [ ] Validate consolidated reporting

---

**Generate this comprehensive Finance SSC module following OCA guidelines, Philippines BIR regulations, and PFRS (Philippine Financial Reporting Standards).**

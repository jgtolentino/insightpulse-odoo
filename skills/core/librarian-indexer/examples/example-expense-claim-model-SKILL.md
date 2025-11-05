# Expense Claim Model Specialist - Odoo Model Specialist

**Skill ID:** `expense-claim-model-specialist`
**Version:** 1.0.0
**Category:** Expense Management
**Expertise Level:** Advanced
**Last Updated:** 2025-11-05
**Source Module:** custom/expense_management/models/expense_claim.py

---

## 🎯 Purpose

This skill provides expertise in developing and maintaining Odoo models for expense management.

This Odoo model represents employee expense claims including receipts, categories, amounts, and approval workflow. It handles the complete lifecycle from submission to reimbursement.

This skill covers model design, field definitions, computed fields, constraints, and business logic implementation following OCA best practices.

---

## 📚 Core Competencies

### 1. Odoo Model Design

**Key Capabilities:**
1. Design expense claim data model with proper normalization
2. Implement expense line item relationships (One2many)
3. Define computed fields for totals and tax calculations
4. Implement state machine for approval workflow
5. Set up constraints for policy compliance
6. Manage receipt attachments and documentation
7. Implement security rules for employee data access
8. Optimize queries for expense reporting

### 2. Field Types & Configuration

**Model Fields:**
- `name` (Char) - Expense claim reference number [Required]
- `employee_id` (Many2one) - Employee submitting the claim [Required]
- `department_id` (Many2one) - Employee's department [Readonly]
- `submission_date` (Date) - Date claim was submitted [Required]
- `expense_date_from` (Date) - Period start date [Required]
- `expense_date_to` (Date) - Period end date [Required]
- `expense_line_ids` (One2many) - Individual expense line items
- `total_amount` (Float) - Total claim amount (computed) [Readonly]
- `total_tax` (Float) - Total tax amount (computed) [Readonly]
- `reimbursable_amount` (Float) - Amount to be reimbursed (computed) [Readonly]
- `currency_id` (Many2one) - Currency [Required]
- `state` (Selection) - Workflow state: draft/submitted/approved/paid/rejected [Required]
- `approver_id` (Many2one) - Current approver
- `approval_date` (Datetime) - Date of approval [Readonly]
- `rejection_reason` (Text) - Reason for rejection
- `receipt_count` (Integer) - Number of receipts attached (computed) [Readonly]
- `company_id` (Many2one) - Company [Required]
- `notes` (Text) - Additional notes

### 3. Business Logic

**Model Methods:**
- `action_submit()` - Submit claim for approval
- `action_approve()` - Approve the expense claim
- `action_reject(reason)` - Reject the claim with reason
- `action_request_payment()` - Request payment processing
- `action_mark_paid()` - Mark as paid
- `action_reset_to_draft()` - Reset to draft state
- `_compute_total_amount()` - Calculate total from line items
- `_compute_receipt_count()` - Count attached receipts
- `_check_policy_compliance()` - Validate against policies
- `_get_approval_hierarchy()` - Determine approval workflow

---

## 🛠️ Tools & Technologies

### Odoo Framework
- **Version:** Odoo 19.0 Community Edition
- **ORM:** Odoo ORM with PostgreSQL backend
- **API:** Odoo RPC, XML-RPC, JSON-RPC

### Required OCA Modules
- `base` - Core Odoo functionality
- `web` - Web interface components
- `hr` - Human Resources module
- `account` - Accounting integration

### Development Tools
- **IDE:** VSCode with Odoo extensions
- **Linting:** pylint-odoo, flake8-odoo
- **Testing:** Odoo test framework, pytest-odoo
- **Database:** PostgreSQL 15+

---

## 🎓 Competency Validation

### Odoo Model Development Checklist

#### Model Structure (20 points)
- [x] Proper model name following Odoo conventions (`expense.claim`)
- [x] Correct inheritance pattern (models.Model)
- [x] Proper `_name`, `_description`, and `_order` attributes
- [x] Implements `_sql_constraints` for data integrity
- [x] Uses appropriate `_rec_name` (defaults to 'name' field)

#### Field Definitions (20 points)
- [x] Fields have proper types (Char, Date, Many2one, One2many, etc.)
- [x] Required fields marked with `required=True`
- [x] Default values implemented properly (state='draft')
- [x] Help text provided for complex fields
- [x] Proper use of `related`, `computed`, `store` attributes

#### Computed Fields (15 points)
- [x] `@api.depends()` decorator lists all dependencies
- [x] Computed method handles empty recordsets
- [x] Proper use of `store=True` for performance optimization (total_amount)
- [ ] Inverse methods implemented for writable computed fields
- [ ] Search methods implemented for searchable computed fields

#### Constraints & Validations (15 points)
- [x] SQL constraints for unique reference numbers
- [x] `@api.constrains()` for business logic validation
- [x] Clear error messages for validation failures
- [x] Proper exception handling

#### Business Logic (20 points)
- [x] Can implement `action_submit()` method
- [x] Can implement `action_approve()` method
- [x] Can implement `action_reject()` method
- [x] Can implement `_compute_total_amount()` method
- [x] Can implement `_check_policy_compliance()` method

#### Security (10 points)
- [x] Record rules defined in `security/ir.model.access.csv`
- [x] Field-level security configured (employees see only their claims)
- [x] Proper user group assignments (employee, manager, finance)
- [x] XSS and SQL injection prevention

---

## 💼 Usage Examples

### Example 1: Basic Model Definition

```python
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ExpenseClaim(models.Model):
    _name = 'expense.claim'
    _description = 'Employee Expense Claim'
    _order = 'submission_date desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic fields
    name = fields.Char(
        string='Claim Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New',
        help='Unique reference number for the expense claim'
    )

    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True,
        default=lambda self: self.env.user.employee_id,
        tracking=True
    )

    active = fields.Boolean(
        string='Active',
        default=True
    )

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('submitted', 'Submitted'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
            ('rejected', 'Rejected')
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True
    )
```

### Example 2: Computed Field with Dependencies

```python
    # Computed fields
    expense_line_ids = fields.One2many(
        comodel_name='expense.claim.line',
        inverse_name='claim_id',
        string='Expense Lines'
    )

    total_amount = fields.Float(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
        readonly=True,
        tracking=True
    )

    @api.depends('expense_line_ids.amount', 'expense_line_ids.active')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(
                record.expense_line_ids.filtered('active').mapped('amount')
            )
```

### Example 3: Constraints and Validation

```python
    _sql_constraints = [
        (
            'name_unique',
            'UNIQUE(name)',
            'Expense claim reference must be unique!'
        ),
        (
            'total_amount_positive',
            'CHECK(total_amount >= 0)',
            'Total amount cannot be negative!'
        )
    ]

    @api.constrains('expense_date_from', 'expense_date_to')
    def _check_date_range(self):
        for record in self:
            if record.expense_date_from and record.expense_date_to:
                if record.expense_date_to < record.expense_date_from:
                    raise ValidationError(
                        'End date cannot be before start date!'
                    )

    @api.constrains('total_amount')
    def _check_policy_compliance(self):
        for record in self:
            if record.total_amount > 10000:
                # Check if requires special approval
                if not record.approver_id or record.approver_id.level < 3:
                    raise ValidationError(
                        'Claims over $10,000 require VP-level approval!'
                    )
```

### Example 4: Business Logic Method

```python
    def action_submit(self):
        """Submit expense claim for approval."""
        self.ensure_one()

        if self.state != 'draft':
            raise ValidationError(
                'Only draft claims can be submitted!'
            )

        if not self.expense_line_ids:
            raise ValidationError(
                'Cannot submit claim without expense lines!'
            )

        # Validate policy compliance
        self._check_policy_compliance()

        # Determine approver based on amount
        approver = self._get_approval_hierarchy()

        # Update state
        self.write({
            'state': 'submitted',
            'submission_date': fields.Date.today(),
            'approver_id': approver.id
        })

        # Send notification
        self._notify_approver(approver)

        # Create activity for approver
        self.activity_schedule(
            'expense_management.mail_activity_expense_approval',
            user_id=approver.user_id.id,
            summary=f'Approve expense claim {self.name}'
        )

        return True

    def action_approve(self):
        """Approve the expense claim."""
        self.ensure_one()

        if self.state != 'submitted':
            raise ValidationError(
                'Only submitted claims can be approved!'
            )

        # Check approver permissions
        if self.env.user.id != self.approver_id.user_id.id:
            if not self.env.user.has_group('expense_management.group_expense_manager'):
                raise ValidationError(
                    'You do not have permission to approve this claim!'
                )

        self.write({
            'state': 'approved',
            'approval_date': fields.Datetime.now()
        })

        # Notify employee
        self._notify_employee_approval()

        # Create accounting entry (if auto-posting enabled)
        if self.company_id.expense_auto_post:
            self._create_accounting_entry()

        return True
```

---

## 📖 Learning Resources

### Official Documentation
- [Odoo 19 ORM Documentation](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html)
- [Odoo Model Reference](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#model-reference)
- [Odoo Field Types](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html#fields)

### OCA Guidelines
- [OCA Development Guidelines](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
- [OCA Module Structure](https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md)
- [OCA Code Review Checklist](https://github.com/OCA/maintainer-tools/wiki/Code-review-checklist)

### Community Resources
- [Odoo Community Forums](https://www.odoo.com/forum)
- [OCA GitHub Repositories](https://github.com/OCA)
- [Odoo Apps Store](https://apps.odoo.com/)

### Recommended Books
- *Odoo Development Essentials* by Daniel Reis
- *Odoo Development Cookbook* by Holger Brunn
- *Working with Odoo 19* (Official guide)

---

## 📊 Success Metrics

### Code Quality Targets
- **OCA Compliance Score:** 100%
- **pylint-odoo Score:** > 9.0/10
- **Test Coverage:** > 90%
- **Documentation Coverage:** 100%

### Performance Targets
- **Query Optimization:** < 100ms for single record operations
- **Bulk Operations:** Handle 1000+ records efficiently
- **Memory Usage:** < 50MB for typical operations
- **Database Indexes:** Properly indexed foreign keys and search fields

### Functional Requirements
- All CRUD operations working correctly
- State transitions validated properly
- Security rules preventing unauthorized access
- Computed fields updating correctly
- Constraints enforcing data integrity
- Integration with accounting module
- Email notifications working
- Activity management integrated
- Approval workflow functioning
- Policy compliance enforced

---

## 🔗 Related Skills

### Prerequisites
- `python-odoo-basics` - Python and Odoo fundamentals
- `postgresql-basics` - Database design and SQL
- `odoo-framework-overview` - Odoo architecture understanding

### Related Odoo Skills
- `odoo-view-development` - XML views and UI
- `odoo-security-rules` - Access rights and record rules
- `odoo-workflow-management` - State machines and workflows
- `odoo-report-development` - QWeb reports
- `odoo-api-integration` - External API integration
- `expense-claim-line-model` - Line item model
- `expense-policy-management` - Policy configuration

### Business Domain Skills
- `expense-management-specialist` - Domain expertise
- `oca-compliance` - OCA standards and guidelines
- `database-optimization` - Query optimization and indexing

---

## 📝 Auto-Generation Metadata

**Generated:** 2025-11-05T10:35:00
**Source File:** `custom/expense_management/models/expense_claim.py`
**Analysis Tool:** librarian-indexer v1.0.0

**Model Details:**
- Model Name: `expense.claim`
- Inherits From: mail.thread, mail.activity.mixin
- Fields Count: 18
- Methods Count: 12
- Computed Fields: 3
- Constraints: 3

**Patterns Detected:**
- Odoo Model Pattern
- State Machine Pattern (draft→submitted→approved→paid)
- One2many Relationship Pattern
- Activity Mixin Pattern
- Mail Thread Pattern (chatter integration)

**Odoo-Specific Metrics:**
- OCA Compliance: 95%
- Model Complexity: High
- Dependencies: 3 modules (hr, account, mail)

---

**Note:** This skill was auto-generated from Odoo model analysis. Review and enhance with business domain knowledge, additional validation rules, and comprehensive test cases.

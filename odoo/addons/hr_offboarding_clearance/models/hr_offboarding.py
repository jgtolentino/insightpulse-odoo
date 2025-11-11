# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class HROffboarding(models.Model):
    """
    Employee Offboarding Clearance Management

    Manages multi-department clearance workflow for departing employees,
    including IT access revocation, finance clearance, and final pay computation.

    Multi-tenant: Isolated by company_id
    BIR Compliance: Integrates with scout.transactions for withholding tax
    """

    _name = 'hr.offboarding'
    _description = 'Employee Offboarding Clearance'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _order = 'exit_date desc, id desc'

    # ========================
    # Fields
    # ========================

    name = fields.Char(
        string='Reference',
        required=True,
        copy=False,
        readonly=True,
        index=True,
        default=lambda self: _('New')
    )

    # Multi-tenant isolation (REQUIRED)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True,
        tracking=True
    )

    # Employee Information
    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        index=True,
        tracking=True,
        domain="[('company_id', '=', company_id)]"
    )

    employee_tin = fields.Char(
        string='TIN',
        related='employee_id.identification_id',
        store=True,
        readonly=True
    )

    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        related='employee_id.department_id',
        store=True,
        readonly=True
    )

    job_id = fields.Many2one(
        'hr.job',
        string='Job Position',
        related='employee_id.job_id',
        store=True,
        readonly=True
    )

    # Exit Details
    exit_date = fields.Date(
        string='Last Working Day',
        required=True,
        tracking=True,
        help="Employee's last working day"
    )

    resignation_date = fields.Date(
        string='Resignation Date',
        tracking=True,
        help="Date employee submitted resignation"
    )

    exit_type = fields.Selection([
        ('voluntary', 'Voluntary Resignation'),
        ('retirement', 'Retirement'),
        ('contract_end', 'End of Contract'),
        ('termination', 'Termination'),
        ('mutual', 'Mutual Separation'),
    ], string='Exit Type', required=True, tracking=True)

    exit_reason = fields.Text(
        string='Reason for Leaving',
        tracking=True
    )

    # Workflow State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('clearance_pending', 'Clearance Pending'),
        ('it_cleared', 'IT Cleared'),
        ('finance_cleared', 'Finance Cleared'),
        ('admin_cleared', 'Admin Cleared'),
        ('final_pay_pending', 'Final Pay Pending'),
        ('final_pay_computed', 'Final Pay Computed'),
        ('bir_generated', 'BIR Form Generated'),
        ('done', 'Complete'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', required=True, tracking=True)

    # Clearance Components
    checklist_ids = fields.One2many(
        'hr.offboarding.checklist',
        'offboarding_id',
        string='Clearance Checklist'
    )

    clearance_progress = fields.Float(
        string='Clearance Progress (%)',
        compute='_compute_clearance_progress',
        store=True
    )

    # Signature Management
    sign_request_id = fields.Many2one(
        'sign.request',
        string='Signature Request',
        readonly=True,
        help="Digital signature request for clearance form"
    )

    sign_status = fields.Selection(
        related='sign_request_id.state',
        string='Signature Status',
        readonly=True
    )

    # Final Pay Computation
    final_pay_id = fields.Many2one(
        'hr.final.pay.computation',
        string='Final Pay Computation',
        readonly=True
    )

    final_pay_amount = fields.Monetary(
        string='Final Pay Amount',
        related='final_pay_id.total_amount',
        currency_field='currency_id',
        store=True,
        readonly=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )

    # BIR Form Generation
    bir_2316_id = fields.Many2one(
        'ir.attachment',
        string='BIR Form 2316',
        readonly=True,
        help="Generated BIR Form 2316 (Certificate of Compensation Payment/Tax Withheld)"
    )

    # Helpdesk Integration
    helpdesk_ticket_id = fields.Many2one(
        'helpdesk.ticket',
        string='Payroll Ticket',
        readonly=True,
        help="Helpdesk ticket for payroll team"
    )

    # Audit Trail
    created_by_user_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    approved_by_user_id = fields.Many2one(
        'res.users',
        string='Approved By',
        readonly=True,
        tracking=True
    )

    approved_date = fields.Datetime(
        string='Approval Date',
        readonly=True,
        tracking=True
    )

    # Notes
    notes = fields.Html(
        string='Internal Notes'
    )

    # ========================
    # Computed Fields
    # ========================

    @api.depends('checklist_ids', 'checklist_ids.completed')
    def _compute_clearance_progress(self):
        """Calculate clearance completion percentage"""
        for record in self:
            total = len(record.checklist_ids)
            if total == 0:
                record.clearance_progress = 0.0
            else:
                completed = len(record.checklist_ids.filtered('completed'))
                record.clearance_progress = (completed / total) * 100

    # ========================
    # CRUD Operations
    # ========================

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate sequence and initialize checklist"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.offboarding') or _('New')

        records = super().create(vals_list)

        for record in records:
            # Auto-generate clearance checklist
            record._generate_clearance_checklist()

        return records

    def write(self, vals):
        """Override write to handle state transitions"""
        result = super().write(vals)

        # Handle state-based automation
        if 'state' in vals:
            for record in self:
                record._handle_state_change()

        return result

    # ========================
    # Business Logic
    # ========================

    def _generate_clearance_checklist(self):
        """
        Generate default clearance checklist items based on company templates
        """
        self.ensure_one()

        templates = self.env['hr.offboarding.checklist.template'].search([
            '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)
        ])

        for template in templates:
            self.env['hr.offboarding.checklist'].create({
                'offboarding_id': self.id,
                'name': template.name,
                'department': template.department,
                'responsible_user_id': template.responsible_user_id.id,
                'sequence': template.sequence,
                'description': template.description,
            })

    def _handle_state_change(self):
        """Handle automated actions based on state transitions"""
        self.ensure_one()

        if self.state == 'clearance_pending':
            self._send_clearance_notification()

        elif self.state == 'admin_cleared':
            self._trigger_final_pay_computation()

        elif self.state == 'final_pay_computed':
            self._create_payroll_ticket()

        elif self.state == 'bir_generated':
            self._send_completion_notification()

    def _send_clearance_notification(self):
        """Send email notifications to clearance approvers"""
        self.ensure_one()

        template = self.env.ref('hr_offboarding_clearance.email_template_clearance_request')
        for checklist_item in self.checklist_ids.filtered(lambda c: not c.completed):
            if checklist_item.responsible_user_id:
                template.send_mail(self.id, force_send=True, email_values={
                    'email_to': checklist_item.responsible_user_id.partner_id.email
                })

    def _trigger_final_pay_computation(self):
        """Create and compute final pay record"""
        self.ensure_one()

        final_pay = self.env['hr.final.pay.computation'].create({
            'offboarding_id': self.id,
            'employee_id': self.employee_id.id,
            'exit_date': self.exit_date,
            'company_id': self.company_id.id,
        })

        final_pay.action_compute_final_pay()
        self.final_pay_id = final_pay.id

    def _create_payroll_ticket(self):
        """Create helpdesk ticket for payroll processing"""
        self.ensure_one()

        ticket = self.env['helpdesk.ticket'].create({
            'name': f'Final Pay - {self.employee_id.name}',
            'description': f"""
                <p>Final pay processing required for departing employee:</p>
                <ul>
                    <li>Employee: {self.employee_id.name}</li>
                    <li>Last Working Day: {self.exit_date}</li>
                    <li>Final Pay Amount: {self.final_pay_amount} {self.currency_id.name}</li>
                    <li>Clearance Status: {self.clearance_progress}% Complete</li>
                </ul>
                <p>Please process final payslip and disburse payment.</p>
            """,
            'partner_id': self.employee_id.user_id.partner_id.id,
            'company_id': self.company_id.id,
            'priority': '2',  # High priority
        })

        self.helpdesk_ticket_id = ticket.id

    def _send_completion_notification(self):
        """Send completion notification to employee and HR"""
        self.ensure_one()

        template = self.env.ref('hr_offboarding_clearance.email_template_offboarding_complete')
        template.send_mail(self.id, force_send=True)

    # ========================
    # Action Methods
    # ========================

    def action_start_clearance(self):
        """Start clearance workflow and generate signature request"""
        for record in self:
            if record.state != 'draft':
                raise UserError(_('Only draft offboarding records can start clearance.'))

            # Generate clearance form signature request
            sign_template = self.env.ref('hr_offboarding_clearance.clearance_form_sign_template')
            sign_request = self.env['sign.request'].create({
                'template_id': sign_template.id,
                'reference': f'Clearance - {record.employee_id.name}',
            })

            # Add signature items for each department
            departments = record.checklist_ids.mapped('department')
            for dept in departments:
                responsible = record.checklist_ids.filtered(
                    lambda c: c.department == dept and c.responsible_user_id
                ).responsible_user_id[:1]

                if responsible:
                    self.env['sign.request.item'].create({
                        'sign_request_id': sign_request.id,
                        'role_id': self.env.ref(f'hr_offboarding_clearance.sign_role_{dept}').id,
                        'partner_id': responsible.partner_id.id,
                    })

            sign_request.action_sent()
            record.sign_request_id = sign_request.id
            record.state = 'clearance_pending'

    def action_generate_bir_2316(self):
        """Generate BIR Form 2316 (Certificate of Compensation Payment/Tax Withheld)"""
        for record in self:
            if not record.final_pay_id:
                raise UserError(_('Final pay must be computed before generating BIR forms.'))

            # Generate XML for eBIRForms
            bir_xml = record.final_pay_id._generate_bir_2316_xml()

            # Save as attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'BIR_2316_{record.employee_id.name}_{record.exit_date.year}.xml',
                'datas': bir_xml,
                'res_model': 'hr.offboarding',
                'res_id': record.id,
                'mimetype': 'application/xml',
            })

            record.bir_2316_id = attachment.id
            record.state = 'bir_generated'

    def action_complete_offboarding(self):
        """Mark offboarding as complete"""
        for record in self:
            if record.clearance_progress < 100:
                raise UserError(_('All clearance items must be completed before closing.'))

            record.write({
                'state': 'done',
                'approved_by_user_id': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })

    def action_cancel_offboarding(self):
        """Cancel offboarding process"""
        for record in self:
            if record.state == 'done':
                raise UserError(_('Cannot cancel completed offboarding.'))

            record.state = 'cancelled'

    # ========================
    # Constraints
    # ========================

    @api.constrains('exit_date', 'resignation_date')
    def _check_dates(self):
        """Validate resignation and exit dates"""
        for record in self:
            if record.resignation_date and record.exit_date:
                if record.resignation_date > record.exit_date:
                    raise ValidationError(
                        _('Resignation date cannot be after exit date.')
                    )

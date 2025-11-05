# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class FinanceBIRComplianceTask(models.Model):
    """
    BIR (Bureau of Internal Revenue) compliance task for Philippine tax filings.
    Tracks BIR form submissions for each agency.
    """
    _name = 'finance.bir.compliance.task'
    _description = 'BIR Compliance Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'due_date, bir_form'

    # Basic Information
    name = fields.Char(
        string='Task Name',
        compute='_compute_name',
        store=True
    )
    period_id = fields.Many2one(
        'finance.closing.period',
        string='Closing Period',
        required=True,
        ondelete='cascade',
        index=True
    )
    company_id = fields.Many2one(
        'res.company',
        string='Agency/Company',
        required=True,
        default=lambda self: self.env.company
    )

    # BIR Form Details
    bir_form = fields.Selection([
        ('0605', 'Form 0605 - Withholding Tax Remittance'),
        ('1600', 'Form 1600 - Monthly Remittance Return of Income Taxes Withheld'),
        ('1601c', 'Form 1601-C - Monthly Remittance Return of Income Taxes'),
        ('1601e', 'Form 1601-E - Quarterly Remittance Return of Creditable Income Taxes'),
        ('1601f', 'Form 1601-F - Monthly Remittance Return of Final Income Taxes'),
        ('1602', 'Form 1602 - Monthly Remittance Return of Final Withholding Taxes'),
        ('1603', 'Form 1603 - Quarterly Remittance Return of Final Income Taxes'),
        ('1604c', 'Form 1604-C - Annual Information Return of Income Taxes Withheld on Compensation'),
        ('1604e', 'Form 1604-E - Annual Information Return of Creditable Income Taxes Withheld'),
        ('1604f', 'Form 1604-F - Annual Information Return of Final Income Taxes Withheld'),
        ('1700', 'Form 1700 - Annual Income Tax Return (Self-Employed)'),
        ('1701', 'Form 1701 - Annual Income Tax Return (Individual)'),
        ('1702rt', 'Form 1702-RT - Annual Income Tax Return (Regular Corporation)'),
        ('1702ex', 'Form 1702-EX - Annual Income Tax Return (Exempt Corporation)'),
        ('1702mn', 'Form 1702-MN - Minimum Corporate Income Tax Return'),
        ('1702q', 'Form 1702-Q - Quarterly Income Tax Return'),
        ('1800', 'Form 1800 - Protest'),
        ('2000', 'Form 2000 - Documentary Stamp Tax Declaration/Return'),
        ('2200m', 'Form 2200-M - Monthly Excise Tax Return'),
        ('2200q', 'Form 2200-Q - Quarterly Excise Tax Return'),
        ('2550m', 'Form 2550-M - Monthly VAT Declaration'),
        ('2550q', 'Form 2550-Q - Quarterly VAT Return'),
        ('2551m', 'Form 2551-M - Monthly Percentage Tax Return'),
        ('2551q', 'Form 2551-Q - Quarterly Percentage Tax Return'),
        ('bir_form_1', 'BIR Form 1 - Certificate of Tax Withheld'),
        ('bir_form_2', 'BIR Form 2 - Certificate of Income Payment'),
    ], string='BIR Form', required=True, tracking=True)

    # Filing Details
    filing_frequency = fields.Selection([
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ], string='Filing Frequency', required=True, default='monthly')

    due_date = fields.Date(
        string='Due Date',
        required=True,
        tracking=True,
        help='BIR filing deadline'
    )
    filing_date = fields.Date(
        string='Filing Date',
        tracking=True,
        help='Actual date filed with BIR'
    )

    # Status
    state = fields.Selection([
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('ready', 'Ready to File'),
        ('filed', 'Filed'),
        ('paid', 'Paid'),
    ], string='Status', default='pending', required=True, tracking=True)

    # Assignment
    prepared_by = fields.Many2one(
        'res.users',
        string='Prepared By',
        tracking=True
    )
    reviewed_by = fields.Many2one(
        'res.users',
        string='Reviewed By',
        tracking=True
    )
    filed_by = fields.Many2one(
        'res.users',
        string='Filed By',
        tracking=True
    )

    # Tax Details
    tax_amount = fields.Monetary(
        string='Tax Amount',
        currency_field='currency_id',
        tracking=True
    )
    penalty_amount = fields.Monetary(
        string='Penalty Amount',
        currency_field='currency_id',
        tracking=True
    )
    total_amount = fields.Monetary(
        string='Total Amount',
        compute='_compute_total_amount',
        store=True,
        currency_field='currency_id'
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    # Filing Information
    reference_number = fields.Char(
        string='Reference Number',
        tracking=True,
        help='BIR acknowledgment/reference number'
    )
    payment_reference = fields.Char(
        string='Payment Reference',
        tracking=True
    )

    # Attachments
    form_attachment_id = fields.Many2one(
        'ir.attachment',
        string='BIR Form (PDF)',
        help='Generated BIR form in PDF format'
    )
    acknowledgment_attachment_id = fields.Many2one(
        'ir.attachment',
        string='BIR Acknowledgment',
        help='BIR filing acknowledgment receipt'
    )
    payment_proof_attachment_id = fields.Many2one(
        'ir.attachment',
        string='Payment Proof',
        help='Payment confirmation from bank/BIR'
    )

    # Notes
    notes = fields.Html(
        string='Notes'
    )

    # Compliance Status
    is_overdue = fields.Boolean(
        string='Overdue',
        compute='_compute_overdue_status',
        store=True
    )
    days_overdue = fields.Integer(
        string='Days Overdue',
        compute='_compute_overdue_status',
        store=True
    )

    @api.depends('bir_form', 'period_id.name', 'company_id.name')
    def _compute_name(self):
        """Generate task name"""
        for task in self:
            bir_form_name = dict(self._fields['bir_form'].selection).get(task.bir_form, '')
            task.name = f"{bir_form_name} - {task.period_id.name} - {task.company_id.name}"

    @api.depends('tax_amount', 'penalty_amount')
    def _compute_total_amount(self):
        """Compute total amount including penalties"""
        for task in self:
            task.total_amount = task.tax_amount + task.penalty_amount

    @api.depends('due_date', 'state')
    def _compute_overdue_status(self):
        """Check if task is overdue"""
        today = fields.Date.today()
        for task in self:
            if task.state not in ('filed', 'paid') and task.due_date:
                task.is_overdue = task.due_date < today
                if task.is_overdue:
                    task.days_overdue = (today - task.due_date).days
                else:
                    task.days_overdue = 0
            else:
                task.is_overdue = False
                task.days_overdue = 0

    def action_prepare(self):
        """Start preparing the BIR form"""
        for task in self:
            if task.state != 'pending':
                raise UserError(_('Only pending tasks can be prepared.'))

            task.write({
                'state': 'preparing',
                'prepared_by': self.env.user.id,
            })
            task.message_post(body=_('BIR form preparation started.'))

    def action_mark_ready(self):
        """Mark form as ready to file"""
        for task in self:
            if task.state != 'preparing':
                raise UserError(_('Only forms being prepared can be marked as ready.'))

            task.write({'state': 'ready'})
            task.message_post(body=_('BIR form ready for filing.'))

    def action_file(self):
        """File the BIR form"""
        for task in self:
            if task.state != 'ready':
                raise UserError(_('Only ready forms can be filed.'))

            task.write({
                'state': 'filed',
                'filing_date': fields.Date.today(),
                'filed_by': self.env.user.id,
            })
            task.message_post(body=_('BIR form filed on %s.') % fields.Date.today())

    def action_mark_paid(self):
        """Mark payment as completed"""
        for task in self:
            if task.state != 'filed':
                raise UserError(_('Only filed forms can be marked as paid.'))

            task.write({'state': 'paid'})
            task.message_post(body=_('Payment completed.'))

    def action_upload_form(self):
        """Open form upload wizard"""
        self.ensure_one()
        return {
            'name': _('Upload BIR Form'),
            'type': 'ir.actions.act_window',
            'res_model': 'ir.attachment',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.id,
                'default_name': f'{self.bir_form}_{self.period_id.name}_{self.company_id.name}.pdf',
            }
        }

    @api.model
    def _cron_send_bir_deadline_reminders(self):
        """
        Cron job to send reminders for BIR filing deadlines
        Scheduled to run daily
        """
        today = fields.Date.today()
        upcoming_tasks = self.search([
            ('state', 'in', ('pending', 'preparing')),
            ('due_date', '>=', today),
        ])

        for task in upcoming_tasks:
            days_remaining = (task.due_date - today).days

            if days_remaining in (7, 3, 1):  # Send reminders
                if task.prepared_by:
                    task.activity_schedule(
                        'finance_ssc_closing.mail_act_bir_deadline',
                        user_id=task.prepared_by.id,
                        summary=_('BIR Filing Deadline: %s') % task.name,
                    )

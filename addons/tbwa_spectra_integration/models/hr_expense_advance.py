# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class HRExpenseAdvance(models.Model):
    """
    Cash Advance model with Spectra export tracking and dual approval workflow.

    Workflow:
    draft → submitted → approved (L1) → approved (L2) → paid → liquidated → done
           ↓ rejected
    """
    _name = 'hr.expense.advance'
    _description = 'Employee Cash Advance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string='Reference', required=True, readonly=True,
                      default=lambda self: _('New'), copy=False)
    date = fields.Date(string='Request Date', required=True,
                      default=fields.Date.context_today, tracking=True)

    # Employee
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,
                                  default=lambda self: self.env.user.employee_id,
                                  tracking=True)
    employee_code = fields.Char(string='Employee Code', related='employee_id.employee_code',
                                store=True, readonly=True)
    department_id = fields.Many2one('hr.department', string='Department',
                                    related='employee_id.department_id', store=True)

    # Amount
    amount = fields.Monetary(string='Cash Advance Amount', required=True,
                            currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  required=True)

    # Purpose
    description = fields.Text(string='Purpose', required=True,
                             help='Detailed purpose of cash advance')
    analytic_account_id = fields.Many2one('account.analytic.account',
                                          string='Project/Cost Center',
                                          tracking=True)

    # Approval workflow
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved_l1', 'Approved (Manager)'),
        ('approved_l2', 'Approved (Finance)'),
        ('rejected', 'Rejected'),
        ('paid', 'Paid'),
        ('liquidating', 'Liquidating'),
        ('done', 'Liquidated'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status')

    # Approvers (from approval matrix)
    approver_l1_id = fields.Many2one('res.users', string='Level 1 Approver',
                                     compute='_compute_approvers', store=True,
                                     readonly=False)
    approver_l2_id = fields.Many2one('res.users', string='Level 2 Approver',
                                     compute='_compute_approvers', store=True,
                                     readonly=False)

    # Approval dates
    approval_l1_date = fields.Datetime(string='L1 Approval Date', readonly=True)
    approval_l2_date = fields.Datetime(string='L2 Approval Date', readonly=True)
    approval_date = fields.Datetime(string='Final Approval Date',
                                    compute='_compute_approval_date', store=True)

    # Payment
    payment_date = fields.Date(string='Payment Date', tracking=True)
    payment_method = fields.Selection([
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('check', 'Check'),
    ], string='Payment Method')
    payment_reference = fields.Char(string='Payment Reference')

    # Liquidation
    liquidation_deadline = fields.Date(string='Liquidation Deadline',
                                      compute='_compute_liquidation_deadline',
                                      store=True,
                                      help='15 days from payment date')
    expense_sheet_id = fields.Many2one('hr.expense.sheet', string='Liquidation Report',
                                       readonly=True)
    is_liquidated = fields.Boolean(string='Liquidated', compute='_compute_liquidation',
                                   store=True)

    # Spectra export
    exported_to_spectra = fields.Boolean(string='Exported to Spectra', default=False,
                                         readonly=True, tracking=True)
    export_batch_id = fields.Many2one('tbwa.spectra.export', string='Export Batch',
                                      readonly=True)
    export_date = fields.Datetime(string='Export Date', readonly=True)

    # Metadata
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company, readonly=True)
    notes = fields.Text(string='Notes')

    @api.model
    def create(self, vals):
        """Generate reference on creation."""
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.expense.advance') or \
                          f"CA/{fields.Date.today().strftime('%Y%m')}/{self.env['ir.sequence'].next_by_code('hr.expense.advance.seq')}"
        return super(HRExpenseAdvance, self).create(vals)

    @api.depends('amount', 'employee_id', 'analytic_account_id')
    def _compute_approvers(self):
        """
        Determine approvers based on approval matrix.
        Uses amount thresholds and employee hierarchy.
        """
        ApprovalMatrix = self.env['tbwa.approval.matrix']

        for record in self:
            if not record.amount:
                continue

            # Find matching approval rule
            approval_rule = ApprovalMatrix.search([
                ('amount_min', '<=', record.amount),
                ('amount_max', '>=', record.amount),
                ('active', '=', True),
            ], limit=1)

            if not approval_rule:
                # Default: immediate manager + finance head
                record.approver_l1_id = record.employee_id.parent_id.user_id
                record.approver_l2_id = self.env.ref('tbwa_spectra_integration.user_finance_head',
                                                     raise_if_not_found=False)
            else:
                # Apply rule
                if approval_rule.approver_level_1 == 'manager':
                    record.approver_l1_id = record.employee_id.parent_id.user_id
                elif approval_rule.approver_level_1 == 'finance_head':
                    record.approver_l1_id = self.env.ref('tbwa_spectra_integration.user_finance_head',
                                                         raise_if_not_found=False)

                if approval_rule.approver_level_2 == 'finance_head':
                    record.approver_l2_id = self.env.ref('tbwa_spectra_integration.user_finance_head',
                                                         raise_if_not_found=False)
                elif approval_rule.approver_level_2 == 'cfo':
                    record.approver_l2_id = self.env.ref('tbwa_spectra_integration.user_cfo',
                                                         raise_if_not_found=False)

    @api.depends('approval_l2_date')
    def _compute_approval_date(self):
        """Final approval = L2 approval date."""
        for record in self:
            record.approval_date = record.approval_l2_date

    @api.depends('payment_date')
    def _compute_liquidation_deadline(self):
        """Liquidation deadline = payment date + 15 days."""
        for record in self:
            if record.payment_date:
                from datetime import timedelta
                record.liquidation_deadline = record.payment_date + timedelta(days=15)
            else:
                record.liquidation_deadline = False

    @api.depends('expense_sheet_id', 'expense_sheet_id.state')
    def _compute_liquidation(self):
        """Check if cash advance is liquidated."""
        for record in self:
            record.is_liquidated = bool(record.expense_sheet_id and
                                       record.expense_sheet_id.state in ['approve', 'done'])

    def action_submit(self):
        """Submit cash advance for approval."""
        self.ensure_one()

        if self.state != 'draft':
            raise UserError(_("Only draft cash advances can be submitted"))

        if not self.amount or self.amount <= 0:
            raise UserError(_("Amount must be greater than zero"))

        if not self.description:
            raise UserError(_("Purpose is required"))

        self.state = 'submitted'

        # Notify L1 approver
        if self.approver_l1_id:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.approver_l1_id.id,
                summary=_('Cash Advance Approval Required'),
                note=_(f'Cash advance request for {self.currency_id.symbol}{self.amount:,.2f} requires your approval.'),
            )

        self.message_post(
            body=_("Cash advance submitted for approval"),
            subtype_xmlid='mail.mt_comment'
        )

        return True

    def action_approve_l1(self):
        """Level 1 approval (Manager)."""
        self.ensure_one()

        if self.state != 'submitted':
            raise UserError(_("Cash advance must be submitted for approval"))

        if self.env.user != self.approver_l1_id:
            raise UserError(_("Only assigned approver can approve this request"))

        self.write({
            'state': 'approved_l1',
            'approval_l1_date': fields.Datetime.now(),
        })

        # Notify L2 approver
        if self.approver_l2_id:
            self.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=self.approver_l2_id.id,
                summary=_('Cash Advance Final Approval Required'),
                note=_(f'Cash advance for {self.employee_id.name} - {self.currency_id.symbol}{self.amount:,.2f}'),
            )

        self.message_post(
            body=_("Level 1 approval by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_comment'
        )

        return True

    def action_approve_l2(self):
        """Level 2 approval (Finance)."""
        self.ensure_one()

        if self.state != 'approved_l1':
            raise UserError(_("Cash advance must have L1 approval first"))

        if self.env.user != self.approver_l2_id:
            raise UserError(_("Only assigned finance approver can approve this request"))

        self.write({
            'state': 'approved_l2',
            'approval_l2_date': fields.Datetime.now(),
        })

        # Notify employee
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.employee_id.user_id.id,
            summary=_('Cash Advance Approved'),
            note=_('Your cash advance request has been approved. Please coordinate with Finance for payment.'),
        )

        self.message_post(
            body=_("Level 2 approval by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_comment'
        )

        return True

    def action_reject(self):
        """Reject cash advance."""
        self.ensure_one()

        if self.state not in ['submitted', 'approved_l1']:
            raise UserError(_("Cannot reject cash advance in current state"))

        self.state = 'rejected'

        # Notify employee
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.employee_id.user_id.id,
            summary=_('Cash Advance Rejected'),
            note=_('Your cash advance request has been rejected. Please contact your manager.'),
        )

        self.message_post(
            body=_("Rejected by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_comment'
        )

        return True

    def action_mark_paid(self):
        """Mark cash advance as paid."""
        self.ensure_one()

        if self.state != 'approved_l2':
            raise UserError(_("Cash advance must be fully approved before payment"))

        self.write({
            'state': 'paid',
            'payment_date': fields.Date.today(),
        })

        # Create liquidation reminder
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            user_id=self.employee_id.user_id.id,
            date_deadline=self.liquidation_deadline,
            summary=_('Cash Advance Liquidation Due'),
            note=_(f'Please submit expense report to liquidate cash advance of {self.currency_id.symbol}{self.amount:,.2f}'),
        )

        self.message_post(
            body=_("Cash advance paid"),
            subtype_xmlid='mail.mt_comment'
        )

        return True

    def action_create_liquidation(self):
        """Create expense sheet for liquidation."""
        self.ensure_one()

        if self.state != 'paid':
            raise UserError(_("Cash advance must be paid before liquidation"))

        if self.expense_sheet_id:
            # Open existing liquidation
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'hr.expense.sheet',
                'res_id': self.expense_sheet_id.id,
                'view_mode': 'form',
                'target': 'current',
            }

        # Create new expense sheet
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': f"Liquidation - {self.name}",
            'employee_id': self.employee_id.id,
            'cash_advance_id': self.id,
            'state': 'draft',
        })

        self.write({
            'expense_sheet_id': expense_sheet.id,
            'state': 'liquidating',
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.expense.sheet',
            'res_id': expense_sheet.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.model
    def cron_send_liquidation_reminders(self):
        """
        Daily cron to send reminders for overdue liquidations.
        Runs daily at 9 AM.
        """
        today = fields.Date.today()

        # Find paid cash advances approaching deadline (3 days before)
        from datetime import timedelta
        reminder_date = today + timedelta(days=3)

        advances = self.search([
            ('state', '=', 'paid'),
            ('liquidation_deadline', '=', reminder_date),
            ('is_liquidated', '=', False),
        ])

        for advance in advances:
            advance.activity_schedule(
                'mail.mail_activity_data_todo',
                user_id=advance.employee_id.user_id.id,
                summary=_('Cash Advance Liquidation Reminder'),
                note=_(f'Your cash advance liquidation is due in 3 days: {advance.liquidation_deadline}'),
            )

        # Find overdue liquidations
        overdue = self.search([
            ('state', '=', 'paid'),
            ('liquidation_deadline', '<', today),
            ('is_liquidated', '=', False),
        ])

        for advance in overdue:
            # Escalate to manager
            if advance.employee_id.parent_id:
                advance.activity_schedule(
                    'mail.mail_activity_data_warning',
                    user_id=advance.employee_id.parent_id.user_id.id,
                    summary=_('Overdue Cash Advance Liquidation'),
                    note=_(f'{advance.employee_id.name} has overdue liquidation: {advance.name}'),
                )

        _logger.info(f"Sent {len(advances)} liquidation reminders, {len(overdue)} escalations")

    @api.model
    def cron_monitor_approval_sla(self):
        """
        Hourly cron to monitor and escalate SLA breaches in approval workflow.
        Escalates cash advances that exceed approval time thresholds.
        """
        from datetime import timedelta
        now = fields.Datetime.now()

        # Find cash advances in approval states with breached SLA (>48 hours)
        breach_threshold = now - timedelta(hours=48)

        breached_advances = self.search([
            ('state', 'in', ['submitted', 'approved_l1']),
            ('submit_date', '<', breach_threshold),
        ])

        # Escalate to finance team
        finance_users = self.env.ref('tbwa_spectra_integration.group_tbwa_finance', raise_if_not_found=False)
        if not finance_users:
            _logger.warning("Finance group not found for SLA escalation")
            return

        for advance in breached_advances:
            # Calculate hours overdue
            age = now - advance.submit_date
            hours_overdue = age.total_seconds() / 3600

            # Escalate to all finance users
            for user in finance_users.users:
                advance.activity_schedule(
                    'mail.mail_activity_data_warning',
                    user_id=user.id,
                    summary=_('SLA BREACH: Cash Advance Approval Overdue'),
                    note=_(f'Cash advance {advance.name} for {advance.employee_id.name} '
                          f'has been pending for {hours_overdue:.1f} hours (SLA: 48h). '
                          f'Current state: {dict(advance._fields["state"].selection).get(advance.state)}'),
                )

            # Log breach
            advance.message_post(
                body=_(f'⚠️ SLA BREACH: Approval pending for {hours_overdue:.1f} hours'),
                message_type='notification',
            )

        _logger.info(f"SLA Monitor: {len(breached_advances)} advances escalated for breach")

# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class MonthEndClosingWizard(models.TransientModel):
    """
    Wizard to create multiple month-end closings for selected agencies
    """
    _name = 'finance.ssc.month.end.closing.wizard'
    _description = 'Month-End Closing Wizard'

    # Mode
    mode = fields.Selection(
        selection=[
            ('single', 'Single Agency'),
            ('multiple', 'Multiple Agencies'),
            ('all', 'All Active Agencies'),
        ],
        string='Mode',
        default='single',
        required=True,
    )

    # Agency selection
    agency_id = fields.Many2one(
        comodel_name='finance.ssc.agency',
        string='Agency',
        required=False,
    )
    agency_ids = fields.Many2many(
        comodel_name='finance.ssc.agency',
        relation='month_end_closing_wizard_agency_rel',
        column1='wizard_id',
        column2='agency_id',
        string='Agencies',
    )

    # Period
    period = fields.Date(
        string='Period',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
        help='First day of the month to close',
    )

    # Options
    auto_generate_checklist = fields.Boolean(
        string='Auto-Generate Checklist',
        default=True,
        help='Automatically create checklist items',
    )
    start_validation = fields.Boolean(
        string='Start Validation Immediately',
        default=False,
        help='Start validation process after creating closings',
    )

    # Summary
    estimated_closings = fields.Integer(
        string='Estimated Closings to Create',
        compute='_compute_estimated_closings',
    )

    @api.depends('mode', 'agency_id', 'agency_ids')
    def _compute_estimated_closings(self):
        """Compute how many closings will be created"""
        for wizard in self:
            if wizard.mode == 'single':
                wizard.estimated_closings = 1 if wizard.agency_id else 0
            elif wizard.mode == 'multiple':
                wizard.estimated_closings = len(wizard.agency_ids)
            elif wizard.mode == 'all':
                wizard.estimated_closings = self.env['finance.ssc.agency'].search_count([('active', '=', True)])
            else:
                wizard.estimated_closings = 0

    @api.onchange('mode')
    def _onchange_mode(self):
        """Clear selections when mode changes"""
        if self.mode == 'single':
            self.agency_ids = [(5, 0, 0)]
        elif self.mode in ('multiple', 'all'):
            self.agency_id = False

    def action_create_closings(self):
        """Create month-end closings"""
        self.ensure_one()

        # Get agencies
        agencies = self._get_selected_agencies()

        if not agencies:
            raise UserError(_('Please select at least one agency'))

        # Check for existing closings
        existing = self.env['finance.ssc.month.end.closing'].search([
            ('agency_id', 'in', agencies.ids),
            ('period', '=', self.period),
        ])

        if existing:
            raise UserError(_(
                'Month-end closing already exists for the following agencies in %s:\n%s'
            ) % (
                self.period.strftime('%B %Y'),
                '\n'.join(existing.mapped('agency_id.name'))
            ))

        # Create closings
        closings = self.env['finance.ssc.month.end.closing']

        for agency in agencies:
            closing = self.env['finance.ssc.month.end.closing'].create({
                'agency_id': agency.id,
                'period': self.period,
            })

            if self.auto_generate_checklist:
                closing._generate_default_checklist()

            if self.start_validation:
                closing.action_start_closing()

            closings |= closing

        # Return action to view created closings
        if len(closings) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Month-End Closing'),
                'res_model': 'finance.ssc.month.end.closing',
                'res_id': closings.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Month-End Closings'),
                'res_model': 'finance.ssc.month.end.closing',
                'domain': [('id', 'in', closings.ids)],
                'view_mode': 'tree,form',
                'target': 'current',
            }

    def _get_selected_agencies(self):
        """Get selected agencies based on mode"""
        self.ensure_one()

        if self.mode == 'single':
            if not self.agency_id:
                raise UserError(_('Please select an agency'))
            return self.agency_id
        elif self.mode == 'multiple':
            if not self.agency_ids:
                raise UserError(_('Please select at least one agency'))
            return self.agency_ids
        elif self.mode == 'all':
            return self.env['finance.ssc.agency'].search([('active', '=', True)])
        else:
            return self.env['finance.ssc.agency']


class MonthEndBatchProcessWizard(models.TransientModel):
    """
    Wizard to batch process month-end closings
    """
    _name = 'finance.ssc.month.end.batch.wizard'
    _description = 'Month-End Batch Process Wizard'

    closing_ids = fields.Many2many(
        comodel_name='finance.ssc.month.end.closing',
        relation='month_end_batch_closing_rel',
        column1='wizard_id',
        column2='closing_id',
        string='Closings',
        required=True,
    )

    action = fields.Selection(
        selection=[
            ('start', 'Start Closing Process'),
            ('validate', 'Validate Transactions'),
            ('generate_tb', 'Generate Trial Balance'),
            ('finalize', 'Finalize & Lock Period'),
        ],
        string='Action',
        required=True,
    )

    def action_execute(self):
        """Execute batch action"""
        self.ensure_one()

        if not self.closing_ids:
            raise UserError(_('Please select at least one closing'))

        success_count = 0
        error_messages = []

        for closing in self.closing_ids:
            try:
                if self.action == 'start':
                    closing.action_start_closing()
                elif self.action == 'validate':
                    closing.action_validate_transactions()
                elif self.action == 'generate_tb':
                    closing._generate_trial_balance()
                elif self.action == 'finalize':
                    closing.action_finalize_closing()

                success_count += 1

            except Exception as e:
                error_messages.append(f"{closing.name}: {str(e)}")

        # Show result
        if error_messages:
            message = _(
                'Batch process completed with errors.\n\n'
                'Success: %d\n'
                'Errors: %d\n\n'
                'Error details:\n%s'
            ) % (success_count, len(error_messages), '\n'.join(error_messages))

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Batch Process Completed with Errors'),
                    'message': message,
                    'type': 'warning',
                    'sticky': True,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Batch Process Completed'),
                    'message': _('Successfully processed %d closings') % success_count,
                    'type': 'success',
                    'sticky': False,
                }
            }

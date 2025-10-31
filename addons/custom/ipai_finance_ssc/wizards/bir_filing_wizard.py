# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class BIRFilingWizard(models.TransientModel):
    """
    Wizard to create BIR forms for selected agencies
    """
    _name = 'finance.ssc.bir.filing.wizard'
    _description = 'BIR Filing Wizard'

    # Form Type
    form_type = fields.Selection(
        selection=[
            ('1601c', 'Form 1601-C (Monthly Withholding Tax)'),
            ('2550q', 'Form 2550Q (Quarterly VAT)'),
            ('1702rt', 'Form 1702-RT (Annual Income Tax - Regular)'),
            ('1702ex', 'Form 1702-EX (Annual Income Tax - Exempt)'),
        ],
        string='Form Type',
        required=True,
        default='1601c',
    )

    # Agency selection
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
    agency_id = fields.Many2one(
        comodel_name='finance.ssc.agency',
        string='Agency',
    )
    agency_ids = fields.Many2many(
        comodel_name='finance.ssc.agency',
        relation='bir_filing_wizard_agency_rel',
        column1='wizard_id',
        column2='agency_id',
        string='Agencies',
    )

    # Period
    period_type = fields.Selection(
        selection=[
            ('month', 'Monthly'),
            ('quarter', 'Quarterly'),
            ('year', 'Annual'),
        ],
        string='Period Type',
        compute='_compute_period_type',
        store=True,
    )
    period_month = fields.Selection(
        selection=[
            ('01', 'January'), ('02', 'February'), ('03', 'March'),
            ('04', 'April'), ('05', 'May'), ('06', 'June'),
            ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December'),
        ],
        string='Month',
    )
    period_quarter = fields.Selection(
        selection=[
            ('Q1', 'Q1 (Jan-Mar)'),
            ('Q2', 'Q2 (Apr-Jun)'),
            ('Q3', 'Q3 (Jul-Sep)'),
            ('Q4', 'Q4 (Oct-Dec)'),
        ],
        string='Quarter',
    )
    period_year = fields.Selection(
        selection=lambda self: [(str(year), str(year)) for year in range(datetime.now().year - 2, datetime.now().year + 2)],
        string='Year',
        default=lambda self: str(datetime.now().year),
    )

    # Options
    auto_compute = fields.Boolean(
        string='Auto-Compute from Accounting',
        default=True,
        help='Automatically compute amounts from accounting data',
    )
    auto_validate = fields.Boolean(
        string='Auto-Validate',
        default=False,
        help='Automatically validate forms after creation',
    )

    # Summary
    estimated_forms = fields.Integer(
        string='Estimated Forms to Create',
        compute='_compute_estimated_forms',
    )
    period_from = fields.Date(
        string='Period From',
        compute='_compute_period_dates',
    )
    period_to = fields.Date(
        string='Period To',
        compute='_compute_period_dates',
    )

    @api.depends('form_type')
    def _compute_period_type(self):
        """Determine period type based on form type"""
        for wizard in self:
            if wizard.form_type in ('1601c',):
                wizard.period_type = 'month'
            elif wizard.form_type in ('2550q',):
                wizard.period_type = 'quarter'
            elif wizard.form_type in ('1702rt', '1702ex'):
                wizard.period_type = 'year'
            else:
                wizard.period_type = 'month'

    @api.depends('period_type', 'period_month', 'period_quarter', 'period_year')
    def _compute_period_dates(self):
        """Compute period start and end dates"""
        for wizard in self:
            if wizard.period_type == 'month' and wizard.period_month and wizard.period_year:
                year = int(wizard.period_year)
                month = int(wizard.period_month)
                wizard.period_from = datetime(year, month, 1).date()
                wizard.period_to = (wizard.period_from + relativedelta(months=1, days=-1))

            elif wizard.period_type == 'quarter' and wizard.period_quarter and wizard.period_year:
                year = int(wizard.period_year)
                quarter_months = {
                    'Q1': (1, 3),
                    'Q2': (4, 6),
                    'Q3': (7, 9),
                    'Q4': (10, 12),
                }
                start_month, end_month = quarter_months[wizard.period_quarter]
                wizard.period_from = datetime(year, start_month, 1).date()
                wizard.period_to = datetime(year, end_month, 1).date() + relativedelta(months=1, days=-1)

            elif wizard.period_type == 'year' and wizard.period_year:
                year = int(wizard.period_year)
                wizard.period_from = datetime(year, 1, 1).date()
                wizard.period_to = datetime(year, 12, 31).date()

            else:
                wizard.period_from = False
                wizard.period_to = False

    @api.depends('mode', 'agency_id', 'agency_ids')
    def _compute_estimated_forms(self):
        """Compute how many forms will be created"""
        for wizard in self:
            if wizard.mode == 'single':
                wizard.estimated_forms = 1 if wizard.agency_id else 0
            elif wizard.mode == 'multiple':
                wizard.estimated_forms = len(wizard.agency_ids)
            elif wizard.mode == 'all':
                wizard.estimated_forms = self.env['finance.ssc.agency'].search_count([('active', '=', True)])
            else:
                wizard.estimated_forms = 0

    @api.onchange('mode')
    def _onchange_mode(self):
        """Clear selections when mode changes"""
        if self.mode == 'single':
            self.agency_ids = [(5, 0, 0)]
        elif self.mode in ('multiple', 'all'):
            self.agency_id = False

    def action_create_forms(self):
        """Create BIR forms"""
        self.ensure_one()

        # Validate period
        if not self.period_from or not self.period_to:
            raise UserError(_('Please select a valid period'))

        # Get agencies
        agencies = self._get_selected_agencies()

        if not agencies:
            raise UserError(_('Please select at least one agency'))

        # Check for existing forms
        existing = self.env['finance.ssc.bir.form'].search([
            ('agency_id', 'in', agencies.ids),
            ('form_type', '=', self.form_type),
            ('period_from', '=', self.period_from),
            ('period_to', '=', self.period_to),
        ])

        if existing:
            raise UserError(_(
                'BIR form %s already exists for the following agencies:\n%s'
            ) % (
                dict(self._fields['form_type'].selection).get(self.form_type),
                '\n'.join(existing.mapped('agency_id.name'))
            ))

        # Create forms
        forms = self.env['finance.ssc.bir.form']

        for agency in agencies:
            form = self.env['finance.ssc.bir.form'].create({
                'agency_id': agency.id,
                'form_type': self.form_type,
                'period_from': self.period_from,
                'period_to': self.period_to,
            })

            if self.auto_compute:
                form.action_compute_amounts()

            if self.auto_validate:
                form.action_validate()

            forms |= form

        # Return action to view created forms
        if len(forms) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': _('BIR Form'),
                'res_model': 'finance.ssc.bir.form',
                'res_id': forms.id,
                'view_mode': 'form',
                'target': 'current',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'name': _('BIR Forms'),
                'res_model': 'finance.ssc.bir.form',
                'domain': [('id', 'in', forms.ids)],
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

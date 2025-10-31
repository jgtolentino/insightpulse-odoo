# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json


class BIRForm(models.Model):
    """
    Philippine BIR Tax Forms Management

    Supports:
    - 1601-C: Monthly Remittance Return of Income Taxes Withheld on Compensation
    - 2550Q: Quarterly VAT Return
    - 1702-RT: Annual Income Tax Return for Corporations (Regular)
    - 1702-EX: Annual Income Tax Return for Corporations (Exempt)
    """
    _name = 'finance.ssc.bir.form'
    _description = 'BIR Tax Form'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'filing_date desc, form_type'

    # Basic Information
    name = fields.Char(
        string='Form Reference',
        compute='_compute_name',
        store=True,
    )
    agency_id = fields.Many2one(
        comodel_name='finance.ssc.agency',
        string='Agency',
        required=True,
        tracking=True,
    )
    form_type = fields.Selection(
        selection=[
            ('1601c', 'Form 1601-C (Monthly Withholding Tax)'),
            ('2550q', 'Form 2550Q (Quarterly VAT)'),
            ('1702rt', 'Form 1702-RT (Annual Income Tax - Regular)'),
            ('1702ex', 'Form 1702-EX (Annual Income Tax - Exempt)'),
        ],
        string='Form Type',
        required=True,
        tracking=True,
    )
    period_type = fields.Selection(
        selection=[
            ('monthly', 'Monthly'),
            ('quarterly', 'Quarterly'),
            ('annual', 'Annual'),
        ],
        string='Period Type',
        compute='_compute_period_type',
        store=True,
    )

    # Period Information
    period_from = fields.Date(
        string='Period From',
        required=True,
        tracking=True,
    )
    period_to = fields.Date(
        string='Period To',
        required=True,
        tracking=True,
    )
    filing_date = fields.Date(
        string='Filing Date',
        required=True,
        tracking=True,
        help='Deadline for filing with BIR',
    )

    # Tax Amounts
    currency_id = fields.Many2one(
        related='agency_id.currency_id',
        string='Currency',
    )

    # 1601-C Fields
    compensation_paid = fields.Monetary(
        string='Compensation Paid',
        currency_field='currency_id',
        help='Total compensation subject to withholding',
    )
    tax_withheld = fields.Monetary(
        string='Tax Withheld',
        currency_field='currency_id',
        help='Total income tax withheld',
    )

    # 2550Q Fields
    vat_output = fields.Monetary(
        string='VAT Output',
        currency_field='currency_id',
        help='VAT on sales',
    )
    vat_input = fields.Monetary(
        string='VAT Input',
        currency_field='currency_id',
        help='VAT on purchases',
    )
    vat_payable = fields.Monetary(
        string='VAT Payable',
        currency_field='currency_id',
        compute='_compute_vat_payable',
        store=True,
    )

    # 1702 Fields
    gross_income = fields.Monetary(
        string='Gross Income',
        currency_field='currency_id',
    )
    deductions = fields.Monetary(
        string='Deductions',
        currency_field='currency_id',
    )
    taxable_income = fields.Monetary(
        string='Taxable Income',
        currency_field='currency_id',
        compute='_compute_taxable_income',
        store=True,
    )
    income_tax_due = fields.Monetary(
        string='Income Tax Due',
        currency_field='currency_id',
    )
    tax_credits = fields.Monetary(
        string='Tax Credits',
        currency_field='currency_id',
        help='Creditable withholding taxes',
    )
    tax_payable = fields.Monetary(
        string='Tax Payable',
        currency_field='currency_id',
        compute='_compute_tax_payable',
        store=True,
    )

    # Filing Status
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('computed', 'Computed'),
            ('validated', 'Validated'),
            ('filed', 'Filed'),
            ('paid', 'Paid'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )

    # ATP (Alphalist of Payees)
    atp_required = fields.Boolean(
        string='ATP Required',
        compute='_compute_atp_required',
    )
    atp_file = fields.Binary(
        string='ATP File',
        help='Alphalist of Payees (DAT file)',
    )
    atp_filename = fields.Char(
        string='ATP Filename',
    )

    # eBIR Export
    ebir_file = fields.Binary(
        string='eBIR File',
        help='Electronic BIR return file',
    )
    ebir_filename = fields.Char(
        string='eBIR Filename',
    )

    # Supporting Documents
    journal_entry_ids = fields.Many2many(
        comodel_name='account.move',
        relation='bir_form_journal_entry_rel',
        column1='bir_form_id',
        column2='move_id',
        string='Related Journal Entries',
    )

    # Payment Information
    payment_date = fields.Date(
        string='Payment Date',
        tracking=True,
    )
    payment_reference = fields.Char(
        string='Payment Reference',
        help='Bank reference or transaction number',
    )
    payment_amount = fields.Monetary(
        string='Amount Paid',
        currency_field='currency_id',
    )

    # BIR Information
    tin = fields.Char(
        related='agency_id.tin',
        string='TIN',
        readonly=True,
    )
    rdo_code = fields.Char(
        related='agency_id.rdo_code',
        string='RDO Code',
        readonly=True,
    )

    # Automation
    auto_computed = fields.Boolean(
        string='Auto-Computed',
        default=False,
        help='Whether amounts were auto-computed from accounting data',
    )
    computation_date = fields.Datetime(
        string='Computation Date',
        readonly=True,
    )

    @api.depends('agency_id', 'form_type', 'period_from')
    def _compute_name(self):
        """Generate form reference name"""
        for form in self:
            if form.agency_id and form.form_type and form.period_from:
                form.name = f"{form.agency_id.code}-{form.form_type.upper()}-{form.period_from.strftime('%Y%m')}"
            else:
                form.name = _('New BIR Form')

    @api.depends('form_type')
    def _compute_period_type(self):
        """Determine period type based on form"""
        mapping = {
            '1601c': 'monthly',
            '2550q': 'quarterly',
            '1702rt': 'annual',
            '1702ex': 'annual',
        }
        for form in self:
            form.period_type = mapping.get(form.form_type, 'monthly')

    @api.depends('vat_output', 'vat_input')
    def _compute_vat_payable(self):
        """Compute VAT payable"""
        for form in self:
            form.vat_payable = form.vat_output - form.vat_input

    @api.depends('gross_income', 'deductions')
    def _compute_taxable_income(self):
        """Compute taxable income"""
        for form in self:
            form.taxable_income = form.gross_income - form.deductions

    @api.depends('income_tax_due', 'tax_credits')
    def _compute_tax_payable(self):
        """Compute final tax payable"""
        for form in self:
            form.tax_payable = form.income_tax_due - form.tax_credits

    @api.depends('form_type')
    def _compute_atp_required(self):
        """Check if ATP is required"""
        for form in self:
            # ATP required for 1601-C and quarterly 2550Q
            form.atp_required = form.form_type in ['1601c', '2550q']

    @api.onchange('form_type', 'period_from')
    def _onchange_compute_period_to(self):
        """Auto-compute period_to based on form type"""
        if self.form_type and self.period_from:
            if self.form_type == '1601c':
                # Monthly: last day of month
                self.period_to = self.period_from + relativedelta(day=31)
            elif self.form_type == '2550q':
                # Quarterly: last day of quarter
                quarter_month = ((self.period_from.month - 1) // 3 + 1) * 3
                self.period_to = self.period_from.replace(month=quarter_month) + relativedelta(day=31)
            else:
                # Annual: December 31
                self.period_to = self.period_from.replace(month=12, day=31)

            # Compute filing date
            self._compute_filing_date()

    def _compute_filing_date(self):
        """Compute BIR filing deadline"""
        self.ensure_one()

        if self.form_type == '1601c':
            # 1601-C: 10th day of following month
            self.filing_date = self.period_to + relativedelta(days=10)
        elif self.form_type == '2550q':
            # 2550Q: 25th day of month following quarter
            self.filing_date = self.period_to + relativedelta(days=25)
        elif self.form_type in ['1702rt', '1702ex']:
            # 1702: April 15 of following year
            self.filing_date = self.period_to.replace(year=self.period_to.year + 1, month=4, day=15)

    def action_auto_compute(self):
        """Auto-compute tax amounts from accounting data"""
        self.ensure_one()

        if self.form_type == '1601c':
            self._compute_1601c()
        elif self.form_type == '2550q':
            self._compute_2550q()
        elif self.form_type in ['1702rt', '1702ex']:
            self._compute_1702()

        self.write({
            'state': 'computed',
            'auto_computed': True,
            'computation_date': fields.Datetime.now(),
        })

    def _compute_1601c(self):
        """Compute Form 1601-C from payroll data"""
        self.ensure_one()

        # Query payroll data for the period
        self.env.cr.execute("""
            SELECT
                SUM(total_amount) as total_compensation,
                SUM(tax_withheld) as total_tax
            FROM hr_payslip
            WHERE analytic_account_id = %s
                AND date_from >= %s
                AND date_to <= %s
                AND state = 'done'
        """, (
            self.agency_id.analytic_account_id.id,
            self.period_from,
            self.period_to,
        ))

        result = self.env.cr.dictfetchone()

        self.write({
            'compensation_paid': result.get('total_compensation', 0.0),
            'tax_withheld': result.get('total_tax', 0.0),
        })

    def _compute_2550q(self):
        """Compute Form 2550Q from sales and purchase data"""
        self.ensure_one()

        # Query VAT data
        self.env.cr.execute("""
            SELECT
                SUM(CASE WHEN aml.tax_line_id IS NOT NULL AND am.move_type = 'out_invoice'
                    THEN aml.balance ELSE 0 END) as vat_output,
                SUM(CASE WHEN aml.tax_line_id IS NOT NULL AND am.move_type = 'in_invoice'
                    THEN aml.balance ELSE 0 END) as vat_input
            FROM account_move_line aml
            JOIN account_move am ON am.id = aml.move_id
            WHERE aml.analytic_account_id = %s
                AND aml.date >= %s
                AND aml.date <= %s
                AND am.state = 'posted'
        """, (
            self.agency_id.analytic_account_id.id,
            self.period_from,
            self.period_to,
        ))

        result = self.env.cr.dictfetchone()

        self.write({
            'vat_output': result.get('vat_output', 0.0),
            'vat_input': abs(result.get('vat_input', 0.0)),  # Input is usually negative
        })

    def _compute_1702(self):
        """Compute Form 1702 from annual P&L"""
        self.ensure_one()

        # Query income statement accounts
        self.env.cr.execute("""
            SELECT
                SUM(CASE WHEN aa.user_type_id IN (
                    SELECT id FROM account_account_type WHERE type = 'income'
                ) THEN aml.credit - aml.debit ELSE 0 END) as gross_income,
                SUM(CASE WHEN aa.user_type_id IN (
                    SELECT id FROM account_account_type WHERE type = 'expense'
                ) THEN aml.debit - aml.credit ELSE 0 END) as total_deductions
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            WHERE aml.analytic_account_id = %s
                AND aml.date >= %s
                AND aml.date <= %s
                AND aml.parent_state = 'posted'
        """, (
            self.agency_id.analytic_account_id.id,
            self.period_from,
            self.period_to,
        ))

        result = self.env.cr.dictfetchone()

        gross_income = result.get('gross_income', 0.0)
        deductions = result.get('total_deductions', 0.0)
        taxable_income = gross_income - deductions

        # Compute tax using Philippine corporate tax rate (25% as of 2023)
        income_tax_due = taxable_income * 0.25 if taxable_income > 0 else 0.0

        self.write({
            'gross_income': gross_income,
            'deductions': deductions,
            'income_tax_due': income_tax_due,
        })

    def action_validate(self):
        """Validate BIR form data"""
        self.ensure_one()

        # Validate required fields
        errors = []

        if not self.tin:
            errors.append(_('TIN is required'))
        if not self.rdo_code:
            errors.append(_('RDO Code is required'))

        if self.form_type == '1601c':
            if self.compensation_paid <= 0:
                errors.append(_('Compensation paid must be greater than zero'))
            if self.tax_withheld < 0:
                errors.append(_('Tax withheld cannot be negative'))

        elif self.form_type == '2550q':
            if self.vat_output < 0:
                errors.append(_('VAT output cannot be negative'))
            if self.vat_payable < 0:
                errors.append(_('VAT payable cannot be negative (you may have VAT refund)'))

        if errors:
            raise ValidationError('\n'.join(errors))

        self.write({'state': 'validated'})

    def action_generate_ebir(self):
        """Generate eBIR file for electronic filing"""
        self.ensure_one()

        if self.state != 'validated':
            raise UserError(_('Form must be validated before generating eBIR file'))

        # Generate eBIR data structure
        ebir_data = self._prepare_ebir_data()

        # Convert to eBIR format (simplified - actual format is more complex)
        ebir_content = json.dumps(ebir_data, indent=2)

        filename = f"eBIR_{self.form_type}_{self.agency_id.code}_{self.period_from.strftime('%Y%m')}.json"

        self.write({
            'ebir_file': ebir_content.encode('utf-8'),
            'ebir_filename': filename,
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('eBIR Generated'),
                'message': _('eBIR file generated successfully: %s') % filename,
                'type': 'success',
                'sticky': False,
            }
        }

    def _prepare_ebir_data(self):
        """Prepare eBIR data structure"""
        self.ensure_one()

        return {
            'form_type': self.form_type,
            'tin': self.tin,
            'rdo_code': self.rdo_code,
            'taxpayer_name': self.agency_id.name,
            'period_from': self.period_from.isoformat(),
            'period_to': self.period_to.isoformat(),
            'filing_date': self.filing_date.isoformat(),
            'amounts': {
                'compensation_paid': self.compensation_paid,
                'tax_withheld': self.tax_withheld,
                'vat_output': self.vat_output,
                'vat_input': self.vat_input,
                'vat_payable': self.vat_payable,
                'gross_income': self.gross_income,
                'deductions': self.deductions,
                'taxable_income': self.taxable_income,
                'income_tax_due': self.income_tax_due,
                'tax_credits': self.tax_credits,
                'tax_payable': self.tax_payable,
            }
        }

    def action_mark_filed(self):
        """Mark form as filed with BIR"""
        self.ensure_one()
        self.write({'state': 'filed'})

    def action_record_payment(self):
        """Launch payment recording wizard"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Record BIR Payment'),
            'res_model': 'finance.ssc.bir.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_bir_form_id': self.id,
                'default_amount': self.tax_payable or self.vat_payable or self.tax_withheld,
            },
        }

    @api.model
    def cron_generate_monthly_forms(self):
        """Cron job to auto-generate monthly BIR forms"""
        # Generate 1601-C for all active agencies
        agencies = self.env['finance.ssc.agency'].search([('active', '=', True)])

        # Last month
        last_month = fields.Date.today() + relativedelta(months=-1, day=1)

        for agency in agencies:
            # Check if form already exists
            existing = self.search([
                ('agency_id', '=', agency.id),
                ('form_type', '=', '1601c'),
                ('period_from', '=', last_month),
            ])

            if not existing:
                form = self.create({
                    'agency_id': agency.id,
                    'form_type': '1601c',
                    'period_from': last_month,
                })
                form._onchange_compute_period_to()
                form.action_auto_compute()

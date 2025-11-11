# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from decimal import Decimal
import logging
import base64

_logger = logging.getLogger(__name__)


class HRFinalPayComputation(models.Model):
    """
    Final Pay Computation with BIR Integration

    Computes employee final pay including:
    - Prorated salary (15th/30th cutoff logic)
    - 13th month pay prorata
    - Unused leave credits
    - BIR withholding tax from scout.transactions
    - Other deductions

    Integrates with Supabase scout.transactions for YTD tax data
    """

    _name = 'hr.final.pay.computation'
    _description = 'Final Pay Computation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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

    offboarding_id = fields.Many2one(
        'hr.offboarding',
        string='Offboarding',
        required=True,
        ondelete='cascade',
        index=True
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        required=True,
        index=True
    )

    exit_date = fields.Date(
        string='Exit Date',
        required=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )

    # Salary Components
    monthly_salary = fields.Monetary(
        string='Monthly Salary',
        currency_field='currency_id',
        readonly=True,
        help="Basic monthly salary from contract"
    )

    prorated_salary = fields.Monetary(
        string='Prorated Salary',
        currency_field='currency_id',
        compute='_compute_prorated_salary',
        store=True,
        help="Salary for worked days in exit month"
    )

    prorated_13th_month = fields.Monetary(
        string='13th Month Pay',
        currency_field='currency_id',
        compute='_compute_13th_month',
        store=True,
        help="Prorated 13th month pay"
    )

    leave_credits_amount = fields.Monetary(
        string='Unused Leave Credits',
        currency_field='currency_id',
        help="Monetized value of unused leave credits"
    )

    other_earnings = fields.Monetary(
        string='Other Earnings',
        currency_field='currency_id',
        help="Other taxable earnings"
    )

    # Deductions
    withholding_tax = fields.Monetary(
        string='Withholding Tax',
        currency_field='currency_id',
        readonly=True,
        help="BIR withholding tax from scout.transactions"
    )

    sss_contribution = fields.Monetary(
        string='SSS Contribution',
        currency_field='currency_id'
    )

    philhealth_contribution = fields.Monetary(
        string='PhilHealth Contribution',
        currency_field='currency_id'
    )

    pagibig_contribution = fields.Monetary(
        string='Pag-IBIG Contribution',
        currency_field='currency_id'
    )

    other_deductions = fields.Monetary(
        string='Other Deductions',
        currency_field='currency_id',
        help="Loans, cash advances, etc."
    )

    # Totals
    total_earnings = fields.Monetary(
        string='Total Earnings',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    total_deductions = fields.Monetary(
        string='Total Deductions',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True
    )

    total_amount = fields.Monetary(
        string='Net Final Pay',
        currency_field='currency_id',
        compute='_compute_totals',
        store=True,
        tracking=True
    )

    # Computation Details
    worked_days = fields.Integer(
        string='Worked Days',
        compute='_compute_worked_days',
        store=True,
        help="Number of days worked in exit month"
    )

    cutoff_period = fields.Selection([
        ('first_half', '1st-15th'),
        ('second_half', '16th-30th/31st'),
        ('full_month', 'Full Month'),
    ], string='Cutoff Period', compute='_compute_cutoff_period', store=True)

    # BIR Integration
    ytd_income = fields.Monetary(
        string='YTD Gross Income',
        currency_field='currency_id',
        readonly=True,
        help="Year-to-date gross income from scout.transactions"
    )

    ytd_tax_withheld = fields.Monetary(
        string='YTD Tax Withheld',
        currency_field='currency_id',
        readonly=True,
        help="Year-to-date withholding tax from scout.transactions"
    )

    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('computed', 'Computed'),
        ('validated', 'Validated'),
        ('paid', 'Paid'),
    ], string='Status', default='draft', required=True, tracking=True)

    # Notes
    computation_notes = fields.Html(
        string='Computation Notes'
    )

    # ========================
    # Computed Fields
    # ========================

    @api.depends('exit_date', 'employee_id')
    def _compute_worked_days(self):
        """Calculate number of worked days in exit month"""
        for record in self:
            if not record.exit_date:
                record.worked_days = 0
                continue

            # Get first day of exit month
            first_day = record.exit_date.replace(day=1)

            # Count working days (Mon-Sat, excluding holidays)
            worked_days = 0
            current_day = first_day

            while current_day <= record.exit_date:
                # Check if it's a working day (Mon-Sat)
                if current_day.weekday() < 6:  # 0-5 = Mon-Sat
                    # TODO: Check against public holidays
                    worked_days += 1

                current_day += timedelta(days=1)

            record.worked_days = worked_days

    @api.depends('exit_date')
    def _compute_cutoff_period(self):
        """Determine payroll cutoff period based on exit date"""
        for record in self:
            if not record.exit_date:
                record.cutoff_period = False
                continue

            day = record.exit_date.day

            if day <= 15:
                record.cutoff_period = 'first_half'
            elif day >= 16:
                record.cutoff_period = 'second_half'

    @api.depends('monthly_salary', 'worked_days', 'exit_date')
    def _compute_prorated_salary(self):
        """
        Calculate prorated salary using 15th/30th cutoff logic

        Logic:
        - If worked ≥1 day within 1st-15th → include 15th pay
        - If worked ≥1 day within 16th-30th → include 30th pay
        """
        for record in self:
            if not record.monthly_salary or not record.exit_date:
                record.prorated_salary = 0.0
                continue

            day = record.exit_date.day
            half_month_salary = record.monthly_salary / 2

            if day <= 15:
                # Only 1st half pay
                record.prorated_salary = half_month_salary
            else:
                # Both halves
                record.prorated_salary = record.monthly_salary

    @api.depends('monthly_salary', 'exit_date')
    def _compute_13th_month(self):
        """
        Calculate prorated 13th month pay

        Formula: (Monthly Salary / 12) * (Months Worked + Fraction of Exit Month)
        """
        for record in self:
            if not record.monthly_salary or not record.exit_date:
                record.prorated_13th_month = 0.0
                continue

            # Get contract start date
            contract = record.employee_id.contract_id
            if not contract or not contract.date_start:
                record.prorated_13th_month = 0.0
                continue

            start_date = contract.date_start
            exit_date = record.exit_date

            # Calculate months worked
            months_worked = (exit_date.year - start_date.year) * 12 + (exit_date.month - start_date.month)

            # Add fraction for exit month
            days_in_exit_month = 30  # Simplified
            fraction = min(exit_date.day / days_in_exit_month, 1.0)

            total_months = months_worked + fraction

            record.prorated_13th_month = (record.monthly_salary / 12) * total_months

    @api.depends('prorated_salary', 'prorated_13th_month', 'leave_credits_amount', 'other_earnings',
                 'withholding_tax', 'sss_contribution', 'philhealth_contribution',
                 'pagibig_contribution', 'other_deductions')
    def _compute_totals(self):
        """Calculate total earnings, deductions, and net amount"""
        for record in self:
            record.total_earnings = (
                record.prorated_salary +
                record.prorated_13th_month +
                record.leave_credits_amount +
                record.other_earnings
            )

            record.total_deductions = (
                record.withholding_tax +
                record.sss_contribution +
                record.philhealth_contribution +
                record.pagibig_contribution +
                record.other_deductions
            )

            record.total_amount = record.total_earnings - record.total_deductions

    # ========================
    # CRUD Operations
    # ========================

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to generate sequence"""
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('hr.final.pay') or _('New')

        return super().create(vals_list)

    # ========================
    # Business Logic
    # ========================

    def action_compute_final_pay(self):
        """
        Main computation method

        Steps:
        1. Fetch employee contract data
        2. Query Supabase for BIR withholding tax
        3. Calculate prorated components
        4. Compute totals
        """
        for record in self:
            # 1. Get contract data
            contract = record.employee_id.contract_id
            if not contract:
                raise UserError(_('No active contract found for employee %s') % record.employee_id.name)

            record.monthly_salary = contract.wage

            # 2. Fetch BIR withholding tax from Supabase
            record._fetch_bir_withholding_tax()

            # 3. Calculate leave credits monetization
            record._compute_leave_credits()

            # 4. Update state
            record.state = 'computed'

            # 5. Log computation
            record.message_post(
                body=_("""
                    <p>Final pay computed successfully:</p>
                    <ul>
                        <li>Prorated Salary: %s</li>
                        <li>13th Month: %s</li>
                        <li>Leave Credits: %s</li>
                        <li>Withholding Tax: %s</li>
                        <li><strong>Net Amount: %s</strong></li>
                    </ul>
                """) % (
                    record.prorated_salary,
                    record.prorated_13th_month,
                    record.leave_credits_amount,
                    record.withholding_tax,
                    record.total_amount
                )
            )

    def _fetch_bir_withholding_tax(self):
        """
        Fetch YTD withholding tax from Supabase scout.transactions

        Queries scout.transactions table for:
        - All transactions for this employee (by TIN)
        - Year-to-date (same year as exit_date)
        - Sum of amount_withheld
        """
        self.ensure_one()

        try:
            supabase_client = self.env['supabase.client'].get_client()

            # Query scout.transactions
            transactions = supabase_client.query(
                "scout.transactions",
                filters={
                    "company_id": self.company_id.id,
                    "payee_tin": self.employee_id.identification_id,
                },
                select="income_payment,amount_withheld,transaction_date"
            )

            # Filter for current year
            year = self.exit_date.year
            ytd_transactions = [
                t for t in transactions
                if datetime.strptime(t['transaction_date'], '%Y-%m-%d').year == year
            ]

            # Calculate YTD totals
            self.ytd_income = sum(Decimal(str(t['income_payment'])) for t in ytd_transactions)
            self.ytd_tax_withheld = sum(Decimal(str(t['amount_withheld'])) for t in ytd_transactions)

            # For final month, withholding tax is already included in YTD
            # No additional tax for final pay (already withheld in prior payslips)
            self.withholding_tax = 0.0

            _logger.info(f"Fetched BIR tax data for {self.employee_id.name}: YTD Income={self.ytd_income}, YTD Tax={self.ytd_tax_withheld}")

        except Exception as e:
            _logger.error(f"Failed to fetch BIR withholding tax: {str(e)}")
            raise UserError(
                _('Failed to fetch BIR withholding tax data from Supabase.\n\nError: %s') % str(e)
            )

    def _compute_leave_credits(self):
        """Calculate monetized value of unused leave credits"""
        self.ensure_one()

        # Get unused leave allocations
        leave_allocations = self.env['hr.leave.allocation'].search([
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'validate'),
        ])

        total_unused_days = 0.0
        for allocation in leave_allocations:
            # Get remaining leaves
            remaining = allocation.number_of_days - allocation.leaves_taken

            # Only monetize vacation leaves (not sick leave)
            if allocation.holiday_status_id.code == 'VAC':
                total_unused_days += remaining

        # Monetize: Daily rate = Monthly Salary / 30
        daily_rate = self.monthly_salary / 30 if self.monthly_salary else 0.0
        self.leave_credits_amount = daily_rate * total_unused_days

    def _generate_bir_2316_xml(self):
        """
        Generate BIR Form 2316 XML for eBIRForms

        Returns base64-encoded XML string
        """
        self.ensure_one()

        # BIR Form 2316 structure (simplified)
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<eBIRForm2316>
    <Header>
        <TaxYear>{self.exit_date.year}</TaxYear>
        <TIN>{self.employee_id.identification_id}</TIN>
        <EmployeeName>{self.employee_id.name}</EmployeeName>
        <EmployerTIN>{self.company_id.vat}</EmployerTIN>
        <EmployerName>{self.company_id.name}</EmployerName>
    </Header>
    <Compensation>
        <GrossCompensation>{self.ytd_income}</GrossCompensation>
        <ThirteenthMonthPay>{self.prorated_13th_month}</ThirteenthMonthPay>
        <OtherBenefits>{self.other_earnings}</OtherBenefits>
    </Compensation>
    <Deductions>
        <SSSContribution>{self.sss_contribution}</SSSContribution>
        <PhilHealthContribution>{self.philhealth_contribution}</PhilHealthContribution>
        <PagIBIGContribution>{self.pagibig_contribution}</PagIBIGContribution>
    </Deductions>
    <TaxWithheld>
        <TotalTaxWithheld>{self.ytd_tax_withheld}</TotalTaxWithheld>
    </TaxWithheld>
    <NetPay>{self.total_amount}</NetPay>
</eBIRForm2316>
"""

        return base64.b64encode(xml_content.encode('utf-8'))

    def action_validate_computation(self):
        """Validate final pay computation"""
        for record in self:
            if record.state != 'computed':
                raise UserError(_('Only computed records can be validated.'))

            record.state = 'validated'

    def action_mark_paid(self):
        """Mark final pay as paid"""
        for record in self:
            if record.state != 'validated':
                raise UserError(_('Only validated records can be marked as paid.'))

            record.state = 'paid'

            # Update offboarding state
            if record.offboarding_id:
                record.offboarding_id.state = 'final_pay_computed'

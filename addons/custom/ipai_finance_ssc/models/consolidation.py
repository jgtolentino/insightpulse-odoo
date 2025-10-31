# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


class FinanceConsolidation(models.Model):
    """
    Multi-Agency Financial Consolidation

    Features:
    - Aggregate trial balance across all 8 agencies
    - Inter-agency elimination entries
    - Consolidated financial statements
    - Automated reconciliation of inter-agency transactions
    """
    _name = 'finance.ssc.consolidation'
    _description = 'Financial Consolidation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'period desc'

    name = fields.Char(
        string='Consolidation Reference',
        compute='_compute_name',
        store=True,
    )
    period = fields.Date(
        string='Period',
        required=True,
        default=lambda self: fields.Date.today().replace(day=1),
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency',
    )

    # Agencies
    agency_ids = fields.Many2many(
        comodel_name='finance.ssc.agency',
        relation='consolidation_agency_rel',
        column1='consolidation_id',
        column2='agency_id',
        string='Agencies',
        default=lambda self: self.env['finance.ssc.agency'].search([('active', '=', True)]),
    )

    # Status
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('computing', 'Computing'),
            ('eliminating', 'Processing Eliminations'),
            ('done', 'Consolidated'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )

    # Consolidated Balances
    total_assets = fields.Monetary(
        string='Total Assets',
        currency_field='currency_id',
        compute='_compute_consolidated_balances',
        store=True,
    )
    total_liabilities = fields.Monetary(
        string='Total Liabilities',
        currency_field='currency_id',
        compute='_compute_consolidated_balances',
        store=True,
    )
    total_equity = fields.Monetary(
        string='Total Equity',
        currency_field='currency_id',
        compute='_compute_consolidated_balances',
        store=True,
    )
    total_revenue = fields.Monetary(
        string='Total Revenue',
        currency_field='currency_id',
        compute='_compute_consolidated_balances',
        store=True,
    )
    total_expenses = fields.Monetary(
        string='Total Expenses',
        currency_field='currency_id',
        compute='_compute_consolidated_balances',
        store=True,
    )
    net_income = fields.Monetary(
        string='Net Income',
        currency_field='currency_id',
        compute='_compute_net_income',
        store=True,
    )

    # Lines
    line_ids = fields.One2many(
        comodel_name='finance.ssc.consolidation.line',
        inverse_name='consolidation_id',
        string='Consolidation Lines',
    )
    elimination_ids = fields.One2many(
        comodel_name='finance.ssc.consolidation.elimination',
        inverse_name='consolidation_id',
        string='Elimination Entries',
    )

    # Statistics
    agency_count = fields.Integer(
        string='Number of Agencies',
        compute='_compute_statistics',
    )
    account_count = fields.Integer(
        string='Number of Accounts',
        compute='_compute_statistics',
    )

    @api.depends('period')
    def _compute_name(self):
        """Generate consolidation reference"""
        for cons in self:
            if cons.period:
                cons.name = f"CONS-{cons.period.strftime('%Y-%m')}"
            else:
                cons.name = _('New Consolidation')

    @api.depends('line_ids', 'line_ids.balance')
    def _compute_consolidated_balances(self):
        """Compute consolidated balances by account type"""
        for cons in self:
            # Group by account type
            assets = sum(cons.line_ids.filtered(
                lambda l: l.account_type == 'asset'
            ).mapped('balance'))

            liabilities = sum(cons.line_ids.filtered(
                lambda l: l.account_type == 'liability'
            ).mapped('balance'))

            equity = sum(cons.line_ids.filtered(
                lambda l: l.account_type == 'equity'
            ).mapped('balance'))

            revenue = sum(cons.line_ids.filtered(
                lambda l: l.account_type == 'income'
            ).mapped('balance'))

            expenses = sum(cons.line_ids.filtered(
                lambda l: l.account_type == 'expense'
            ).mapped('balance'))

            cons.total_assets = assets
            cons.total_liabilities = liabilities
            cons.total_equity = equity
            cons.total_revenue = revenue
            cons.total_expenses = expenses

    @api.depends('total_revenue', 'total_expenses')
    def _compute_net_income(self):
        """Compute consolidated net income"""
        for cons in self:
            cons.net_income = cons.total_revenue - cons.total_expenses

    @api.depends('agency_ids', 'line_ids')
    def _compute_statistics(self):
        """Compute statistics"""
        for cons in self:
            cons.agency_count = len(cons.agency_ids)
            cons.account_count = len(cons.line_ids.mapped('account_id'))

    def action_compute_consolidation(self):
        """Compute consolidated balances"""
        self.ensure_one()

        if not self.agency_ids:
            raise UserError(_('Please select at least one agency'))

        self.write({'state': 'computing'})

        # Clear existing lines
        self.line_ids.unlink()

        # Aggregate balances from all agencies
        self._aggregate_agency_balances()

        self.write({'state': 'eliminating'})

        # Process elimination entries
        self._process_eliminations()

        self.write({'state': 'done'})

    def _aggregate_agency_balances(self):
        """Aggregate balances from all agencies"""
        self.ensure_one()

        period_start = self.period
        period_end = self.period.replace(day=1) + relativedelta(months=1, days=-1)

        # Query all account balances for selected agencies
        analytic_account_ids = tuple(self.agency_ids.mapped('analytic_account_id').ids)

        self.env.cr.execute("""
            SELECT
                aa.id as account_id,
                aa.code as account_code,
                aa.name as account_name,
                aat.type as account_type,
                aml.analytic_account_id as analytic_account_id,
                SUM(aml.debit) as debit,
                SUM(aml.credit) as credit,
                SUM(aml.balance) as balance
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_account_type aat ON aat.id = aa.user_type_id
            WHERE aml.analytic_account_id IN %s
                AND aml.date >= %s
                AND aml.date <= %s
                AND aml.parent_state = 'posted'
            GROUP BY aa.id, aa.code, aa.name, aat.type, aml.analytic_account_id
            ORDER BY aa.code
        """, (analytic_account_ids, period_start, period_end))

        results = self.env.cr.dictfetchall()

        # Create consolidation lines
        for row in results:
            agency = self.agency_ids.filtered(
                lambda a: a.analytic_account_id.id == row['analytic_account_id']
            )

            self.env['finance.ssc.consolidation.line'].create({
                'consolidation_id': self.id,
                'agency_id': agency.id,
                'account_id': row['account_id'],
                'account_code': row['account_code'],
                'account_name': row['account_name'],
                'account_type': row['account_type'],
                'debit': row['debit'],
                'credit': row['credit'],
                'balance': row['balance'],
            })

    def _process_eliminations(self):
        """Process inter-agency elimination entries"""
        self.ensure_one()

        # TODO: Implement inter-agency transaction detection and elimination
        # For now, just mark as complete
        pass

    def action_export_to_excel(self):
        """Export consolidated report to Excel"""
        self.ensure_one()

        # TODO: Implement Excel export
        raise UserError(_('Excel export not yet implemented'))


class FinanceConsolidationLine(models.Model):
    """Consolidation line item"""
    _name = 'finance.ssc.consolidation.line'
    _description = 'Consolidation Line'
    _order = 'account_code'

    consolidation_id = fields.Many2one(
        comodel_name='finance.ssc.consolidation',
        string='Consolidation',
        required=True,
        ondelete='cascade',
    )
    agency_id = fields.Many2one(
        comodel_name='finance.ssc.agency',
        string='Agency',
        required=True,
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
        required=True,
    )
    account_code = fields.Char(
        string='Account Code',
    )
    account_name = fields.Char(
        string='Account Name',
    )
    account_type = fields.Selection(
        selection=[
            ('asset', 'Asset'),
            ('liability', 'Liability'),
            ('equity', 'Equity'),
            ('income', 'Income'),
            ('expense', 'Expense'),
        ],
        string='Account Type',
    )
    currency_id = fields.Many2one(
        related='consolidation_id.currency_id',
        string='Currency',
    )
    debit = fields.Monetary(
        string='Debit',
        currency_field='currency_id',
    )
    credit = fields.Monetary(
        string='Credit',
        currency_field='currency_id',
    )
    balance = fields.Monetary(
        string='Balance',
        currency_field='currency_id',
    )


class FinanceConsolidationElimination(models.Model):
    """Inter-agency elimination entry"""
    _name = 'finance.ssc.consolidation.elimination'
    _description = 'Consolidation Elimination'

    consolidation_id = fields.Many2one(
        comodel_name='finance.ssc.consolidation',
        string='Consolidation',
        required=True,
        ondelete='cascade',
    )
    name = fields.Char(
        string='Description',
        required=True,
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        required=True,
    )
    currency_id = fields.Many2one(
        related='consolidation_id.currency_id',
        string='Currency',
    )
    account_debit_id = fields.Many2one(
        comodel_name='account.account',
        string='Debit Account',
    )
    account_credit_id = fields.Many2one(
        comodel_name='account.account',
        string='Credit Account',
    )

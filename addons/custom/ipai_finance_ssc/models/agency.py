# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class FinanceSscAgency(models.Model):
    """
    Multi-agency management for Finance Shared Service Center

    Manages 8 agencies:
    - RIM (Research Institute for Mindanao)
    - CKVC (Convergence Knowledge Ventures Corporation)
    - BOM (Business of Mindanao)
    - JPAL (Abdul Latif Jameel Poverty Action Lab)
    - JLI (Jaff Law Institute)
    - JAP (Jaff Advocacy Partners)
    - LAS (Legal Advisory Services)
    - RMQB (Research Mindanao Quality Benchmarking)
    """
    _name = 'finance.ssc.agency'
    _description = 'Finance SSC Agency'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'code'

    # Basic Information
    name = fields.Char(
        string='Agency Name',
        required=True,
        tracking=True,
    )
    code = fields.Selection(
        selection=[
            ('RIM', 'Research Institute for Mindanao'),
            ('CKVC', 'Convergence Knowledge Ventures Corporation'),
            ('BOM', 'Business of Mindanao'),
            ('JPAL', 'Abdul Latif Jameel Poverty Action Lab'),
            ('JLI', 'Jaff Law Institute'),
            ('JAP', 'Jaff Advocacy Partners'),
            ('LAS', 'Legal Advisory Services'),
            ('RMQB', 'Research Mindanao Quality Benchmarking'),
        ],
        string='Agency Code',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        string='Active',
        default=True,
        tracking=True,
    )

    # Company and Accounting
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
    )
    currency_id = fields.Many2one(
        related='company_id.currency_id',
        string='Currency',
        readonly=True,
    )
    analytic_account_id = fields.Many2one(
        comodel_name='account.analytic.account',
        string='Analytic Account',
        required=True,
        tracking=True,
        help='Analytic account for tracking transactions by agency',
    )

    # BIR Information
    tin = fields.Char(
        string='TIN',
        size=20,
        help='Tax Identification Number',
        tracking=True,
    )
    rdo_code = fields.Char(
        string='RDO Code',
        size=5,
        help='Revenue District Office Code',
        tracking=True,
    )

    # Bank Information
    bank_account_ids = fields.One2many(
        comodel_name='res.partner.bank',
        inverse_name='partner_id',
        string='Bank Accounts',
        domain="[('partner_id', '=', partner_id)]",
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Related Partner',
        help='Partner record for this agency',
    )

    # Month-End Tracking
    last_closed_period = fields.Date(
        string='Last Closed Period',
        readonly=True,
        help='Last successfully closed accounting period',
    )
    month_end_status = fields.Selection(
        selection=[
            ('open', 'Period Open'),
            ('closing', 'Month-End in Progress'),
            ('closed', 'Period Closed'),
        ],
        string='Month-End Status',
        default='open',
        tracking=True,
    )

    # Statistics
    transaction_count = fields.Integer(
        string='Transaction Count',
        compute='_compute_statistics',
        store=False,
    )
    total_debit = fields.Monetary(
        string='Total Debit',
        compute='_compute_statistics',
        store=False,
    )
    total_credit = fields.Monetary(
        string='Total Credit',
        compute='_compute_statistics',
        store=False,
    )

    # Integration Status
    supabase_synced = fields.Boolean(
        string='Supabase Synced',
        default=False,
        help='Whether data is synced to Supabase data warehouse',
    )
    notion_synced = fields.Boolean(
        string='Notion Synced',
        default=False,
        help='Whether tasks are synced to Notion',
    )
    last_sync_date = fields.Datetime(
        string='Last Sync Date',
        readonly=True,
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Agency code must be unique!'),
    ]

    @api.depends('analytic_account_id')
    def _compute_statistics(self):
        """Compute transaction statistics for each agency"""
        for agency in self:
            if not agency.analytic_account_id:
                agency.transaction_count = 0
                agency.total_debit = 0.0
                agency.total_credit = 0.0
                continue

            # Query account move lines
            self.env.cr.execute("""
                SELECT
                    COUNT(*) as count,
                    SUM(debit) as total_debit,
                    SUM(credit) as total_credit
                FROM account_move_line
                WHERE analytic_account_id = %s
                    AND parent_state = 'posted'
            """, (agency.analytic_account_id.id,))

            result = self.env.cr.dictfetchone()
            agency.transaction_count = result['count'] or 0
            agency.total_debit = result['total_debit'] or 0.0
            agency.total_credit = result['total_credit'] or 0.0

    @api.model
    def create(self, vals):
        """Create agency with automatic analytic account creation"""
        if not vals.get('analytic_account_id'):
            # Create analytic account automatically
            analytic_account = self.env['account.analytic.account'].create({
                'name': f"{vals.get('code')} - {vals.get('name')}",
                'code': vals.get('code'),
                'company_id': vals.get('company_id', self.env.company.id),
            })
            vals['analytic_account_id'] = analytic_account.id

        # Create partner if not exists
        if not vals.get('partner_id'):
            partner = self.env['res.partner'].create({
                'name': vals.get('name'),
                'is_company': True,
                'company_id': vals.get('company_id', self.env.company.id),
            })
            vals['partner_id'] = partner.id

        return super().create(vals)

    def action_generate_trial_balance(self):
        """Generate trial balance for this agency"""
        self.ensure_one()

        # Create wizard context
        return {
            'type': 'ir.actions.act_window',
            'name': _('Trial Balance - %s') % self.code,
            'res_model': 'account.financial.report',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_analytic_account_id': self.analytic_account_id.id,
                'default_date_from': fields.Date.today().replace(day=1),
                'default_date_to': fields.Date.today(),
            },
        }

    def action_month_end_closing(self):
        """Launch month-end closing wizard"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Month-End Closing - %s') % self.code,
            'res_model': 'month.end.closing.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_agency_id': self.id,
            },
        }

    def action_sync_to_supabase(self):
        """Sync agency data to Supabase"""
        self.ensure_one()

        connector = self.env['finance.ssc.supabase.connector']
        result = connector.sync_agency_data(self)

        self.write({
            'supabase_synced': True,
            'last_sync_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Successful'),
                'message': _('Data synced to Supabase successfully'),
                'type': 'success',
                'sticky': False,
            }
        }

    def action_sync_to_notion(self):
        """Sync tasks to Notion"""
        self.ensure_one()

        connector = self.env['finance.ssc.notion.connector']
        connector.sync_month_end_tasks(self)

        self.write({
            'notion_synced': True,
            'last_sync_date': fields.Datetime.now(),
        })

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Successful'),
                'message': _('Tasks synced to Notion successfully'),
                'type': 'success',
                'sticky': False,
            }
        }

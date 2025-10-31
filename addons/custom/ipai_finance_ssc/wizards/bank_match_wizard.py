# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class BankMatchWizard(models.TransientModel):
    """
    Wizard for manual bank reconciliation line matching
    """
    _name = 'finance.ssc.bank.match.wizard'
    _description = 'Bank Match Wizard'

    reconciliation_line_id = fields.Many2one(
        comodel_name='finance.ssc.bank.reconciliation.line',
        string='Bank Line',
        required=True,
        readonly=True,
    )

    # Bank line details (readonly)
    date = fields.Date(
        string='Bank Date',
        related='reconciliation_line_id.date',
        readonly=True,
    )
    description = fields.Char(
        string='Bank Description',
        related='reconciliation_line_id.description',
        readonly=True,
    )
    amount = fields.Monetary(
        string='Bank Amount',
        related='reconciliation_line_id.amount',
        readonly=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='reconciliation_line_id.currency_id',
        readonly=True,
    )

    # Search criteria
    search_mode = fields.Selection(
        selection=[
            ('auto', 'Auto-Suggest Candidates'),
            ('manual', 'Manual Search'),
        ],
        string='Search Mode',
        default='auto',
        required=True,
    )

    # Manual search fields
    search_amount = fields.Monetary(
        string='Search Amount',
        currency_field='currency_id',
    )
    search_date_from = fields.Date(
        string='Date From',
    )
    search_date_to = fields.Date(
        string='Date To',
    )
    search_description = fields.Char(
        string='Search Description',
    )
    search_account_id = fields.Many2one(
        comodel_name='account.account',
        string='Account',
    )

    # Candidates
    candidate_ids = fields.One2many(
        comodel_name='finance.ssc.bank.match.candidate',
        inverse_name='wizard_id',
        string='Matching Candidates',
    )

    # Selected match
    selected_move_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Selected Journal Item',
    )

    @api.onchange('reconciliation_line_id', 'search_mode')
    def _onchange_search_criteria(self):
        """Initialize search criteria from bank line"""
        if self.reconciliation_line_id and self.search_mode == 'auto':
            self.search_amount = self.amount
            self.search_date_from = self.date - fields.timedelta(days=3)
            self.search_date_to = self.date + fields.timedelta(days=3)
            self.search_description = self.description
            self._search_candidates()

    def action_search_candidates(self):
        """Search for matching candidates"""
        self.ensure_one()
        self._search_candidates()

    def _search_candidates(self):
        """Execute candidate search"""
        self.ensure_one()

        # Clear existing candidates
        self.candidate_ids.unlink()

        # Get agency analytic account
        agency = self.reconciliation_line_id.reconciliation_id.agency_id
        if not agency or not agency.analytic_account_id:
            return

        # Build search domain
        domain = [
            ('account_id.reconcile', '=', True),
            ('analytic_account_id', '=', agency.analytic_account_id.id),
            ('reconciled', '=', False),
            ('parent_state', '=', 'posted'),
        ]

        # Amount filter
        if self.search_amount:
            domain.append(('balance', '=', self.search_amount))
        elif self.amount:
            domain.append(('balance', '=', self.amount))

        # Date filter
        if self.search_date_from:
            domain.append(('date', '>=', self.search_date_from))
        if self.search_date_to:
            domain.append(('date', '<=', self.search_date_to))

        # Account filter
        if self.search_account_id:
            domain.append(('account_id', '=', self.search_account_id.id))

        # Search
        candidates = self.env['account.move.line'].search(domain, limit=50)

        # Create candidate records with match scores
        for candidate in candidates:
            match_score = self._calculate_match_score(candidate)

            self.env['finance.ssc.bank.match.candidate'].create({
                'wizard_id': self.id,
                'move_line_id': candidate.id,
                'match_score': match_score,
            })

    def _calculate_match_score(self, move_line):
        """Calculate match score for a candidate"""
        score = 0.0

        # Exact amount match: 40 points
        if abs(move_line.balance - self.amount) < 0.01:
            score += 40.0

        # Date proximity: up to 30 points
        if move_line.date and self.date:
            date_diff = abs((move_line.date - self.date).days)
            if date_diff == 0:
                score += 30.0
            elif date_diff <= 3:
                score += 30.0 - (date_diff * 5)

        # Description similarity: up to 30 points
        if self.description and (move_line.name or move_line.ref):
            from addons.ipai_finance_ssc.models.bank_reconciliation import BankReconciliation
            reconciliation = self.env['finance.ssc.bank.reconciliation'].browse(1)
            similarity = reconciliation._calculate_string_similarity(
                self.description,
                move_line.name or move_line.ref or ''
            )
            score += (similarity / 100.0) * 30.0

        return min(score, 100.0)

    def action_select_candidate(self):
        """Select a candidate from the list"""
        self.ensure_one()

        if not self.selected_move_line_id:
            raise UserError(_('Please select a journal item to match'))

        # Update the bank reconciliation line
        self.reconciliation_line_id.write({
            'matched_move_line_id': self.selected_move_line_id.id,
            'match_status': 'manual_matched',
            'match_score': 100.0,  # Manual matches get perfect score
        })

        return {'type': 'ir.actions.act_window_close'}

    def action_create_journal_entry(self):
        """Create a new journal entry for unmatched line"""
        self.ensure_one()

        # Return action to create journal entry
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Journal Entry'),
            'res_model': 'account.move',
            'view_mode': 'form',
            'context': {
                'default_move_type': 'entry',
                'default_date': self.date,
                'default_analytic_account_id': self.reconciliation_line_id.reconciliation_id.agency_id.analytic_account_id.id,
            },
            'target': 'current',
        }


class BankMatchCandidate(models.TransientModel):
    """
    Bank match candidate line
    """
    _name = 'finance.ssc.bank.match.candidate'
    _description = 'Bank Match Candidate'
    _order = 'match_score desc, date desc'

    wizard_id = fields.Many2one(
        comodel_name='finance.ssc.bank.match.wizard',
        string='Wizard',
        required=True,
        ondelete='cascade',
    )
    move_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Journal Item',
        required=True,
    )
    match_score = fields.Float(
        string='Match Score %',
        default=0.0,
    )

    # Related fields for display
    date = fields.Date(
        related='move_line_id.date',
        string='Date',
        readonly=True,
    )
    account_id = fields.Many2one(
        related='move_line_id.account_id',
        string='Account',
        readonly=True,
    )
    partner_id = fields.Many2one(
        related='move_line_id.partner_id',
        string='Partner',
        readonly=True,
    )
    name = fields.Char(
        related='move_line_id.name',
        string='Label',
        readonly=True,
    )
    ref = fields.Char(
        related='move_line_id.ref',
        string='Reference',
        readonly=True,
    )
    debit = fields.Monetary(
        related='move_line_id.debit',
        string='Debit',
        readonly=True,
        currency_field='currency_id',
    )
    credit = fields.Monetary(
        related='move_line_id.credit',
        string='Credit',
        readonly=True,
        currency_field='currency_id',
    )
    balance = fields.Monetary(
        related='move_line_id.balance',
        string='Balance',
        readonly=True,
        currency_field='currency_id',
    )
    currency_id = fields.Many2one(
        related='move_line_id.currency_id',
        readonly=True,
    )

    def action_select(self):
        """Select this candidate"""
        self.ensure_one()
        self.wizard_id.selected_move_line_id = self.move_line_id
        return self.wizard_id.action_select_candidate()

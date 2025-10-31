# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import re


class BankReconciliation(models.Model):
    """
    Automated Bank Reconciliation with 80% Auto-Match

    Features:
    - Smart matching algorithms
    - Fuzzy string matching for descriptions
    - Amount and date-based matching
    - Manual review workflow
    - Bulk operations
    """
    _name = 'finance.ssc.bank.reconciliation'
    _description = 'Bank Reconciliation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'reconciliation_date desc'

    name = fields.Char(
        string='Reference',
        required=True,
        default='New',
        readonly=True,
    )
    agency_id = fields.Many2one(
        comodel_name='finance.ssc.agency',
        string='Agency',
        required=True,
        tracking=True,
    )
    bank_account_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string='Bank Account',
        required=True,
        tracking=True,
    )
    reconciliation_date = fields.Date(
        string='Reconciliation Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
    )

    # Period
    period_from = fields.Date(
        string='Period From',
        required=True,
    )
    period_to = fields.Date(
        string='Period To',
        required=True,
    )

    # Status
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('matching', 'Auto-Matching'),
            ('review', 'Manual Review'),
            ('done', 'Reconciled'),
            ('cancelled', 'Cancelled'),
        ],
        string='Status',
        default='draft',
        required=True,
        tracking=True,
    )

    # Statistics
    total_bank_lines = fields.Integer(
        string='Total Bank Lines',
        compute='_compute_statistics',
        store=True,
    )
    matched_lines = fields.Integer(
        string='Matched Lines',
        compute='_compute_statistics',
        store=True,
    )
    unmatched_lines = fields.Integer(
        string='Unmatched Lines',
        compute='_compute_statistics',
        store=True,
    )
    match_rate = fields.Float(
        string='Match Rate %',
        compute='_compute_statistics',
        store=True,
    )

    # Currency
    currency_id = fields.Many2one(
        related='agency_id.currency_id',
        string='Currency',
    )

    # Balances
    opening_balance = fields.Monetary(
        string='Opening Balance',
        currency_field='currency_id',
    )
    closing_balance_bank = fields.Monetary(
        string='Closing Balance (Bank)',
        currency_field='currency_id',
    )
    closing_balance_odoo = fields.Monetary(
        string='Closing Balance (Odoo)',
        currency_field='currency_id',
        compute='_compute_odoo_balance',
        store=True,
    )
    difference = fields.Monetary(
        string='Difference',
        currency_field='currency_id',
        compute='_compute_difference',
        store=True,
    )

    # Lines
    line_ids = fields.One2many(
        comodel_name='finance.ssc.bank.reconciliation.line',
        inverse_name='reconciliation_id',
        string='Reconciliation Lines',
    )

    # Auto-matching Configuration
    auto_match_enabled = fields.Boolean(
        string='Enable Auto-Match',
        default=True,
    )
    match_threshold = fields.Float(
        string='Match Threshold %',
        default=85.0,
        help='Minimum similarity percentage for auto-match',
    )
    date_tolerance_days = fields.Integer(
        string='Date Tolerance (Days)',
        default=3,
        help='Number of days +/- to consider for date matching',
    )

    @api.model
    def create(self, vals):
        """Generate sequence number"""
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('finance.ssc.bank.reconciliation') or 'New'
        return super().create(vals)

    @api.depends('line_ids', 'line_ids.match_status')
    def _compute_statistics(self):
        """Compute matching statistics"""
        for rec in self:
            total = len(rec.line_ids)
            matched = len(rec.line_ids.filtered(lambda l: l.match_status in ['auto_matched', 'manual_matched']))
            unmatched = total - matched

            rec.total_bank_lines = total
            rec.matched_lines = matched
            rec.unmatched_lines = unmatched
            rec.match_rate = (matched / total * 100) if total > 0 else 0.0

    @api.depends('opening_balance', 'line_ids', 'line_ids.amount')
    def _compute_odoo_balance(self):
        """Compute Odoo closing balance"""
        for rec in self:
            total_movement = sum(rec.line_ids.mapped('amount'))
            rec.closing_balance_odoo = rec.opening_balance + total_movement

    @api.depends('closing_balance_bank', 'closing_balance_odoo')
    def _compute_difference(self):
        """Compute difference between bank and Odoo"""
        for rec in self:
            rec.difference = rec.closing_balance_bank - rec.closing_balance_odoo

    def action_start_auto_match(self):
        """Start automated matching process"""
        self.ensure_one()

        if not self.auto_match_enabled:
            raise UserError(_('Auto-matching is disabled'))

        self.write({'state': 'matching'})

        # Run auto-matching algorithms
        matched_count = self._run_auto_matching()

        self.write({'state': 'review'})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Auto-Match Complete'),
                'message': _('Matched %d out of %d lines (%.1f%%)') % (
                    matched_count,
                    self.total_bank_lines,
                    (matched_count / self.total_bank_lines * 100) if self.total_bank_lines > 0 else 0
                ),
                'type': 'success',
                'sticky': False,
            }
        }

    def _run_auto_matching(self):
        """Execute auto-matching algorithms"""
        self.ensure_one()
        matched_count = 0

        for line in self.line_ids.filtered(lambda l: l.match_status == 'unmatched'):
            # Try exact amount match
            if self._try_exact_amount_match(line):
                matched_count += 1
                continue

            # Try amount + date match
            if self._try_amount_date_match(line):
                matched_count += 1
                continue

            # Try fuzzy description match
            if self._try_fuzzy_description_match(line):
                matched_count += 1
                continue

        return matched_count

    def _try_exact_amount_match(self, line):
        """Match by exact amount only"""
        # Search for journal items with exact amount
        domain = [
            ('account_id.reconcile', '=', True),
            ('analytic_account_id', '=', self.agency_id.analytic_account_id.id),
            ('balance', '=', line.amount),
            ('reconciled', '=', False),
            ('parent_state', '=', 'posted'),
        ]

        candidates = self.env['account.move.line'].search(domain, limit=1)

        if len(candidates) == 1:
            line.write({
                'matched_move_line_id': candidates.id,
                'match_status': 'auto_matched',
                'match_score': 100.0,
            })
            return True

        return False

    def _try_amount_date_match(self, line):
        """Match by amount + date tolerance"""
        date_from = line.date + fields.timedelta(days=-self.date_tolerance_days)
        date_to = line.date + fields.timedelta(days=self.date_tolerance_days)

        domain = [
            ('account_id.reconcile', '=', True),
            ('analytic_account_id', '=', self.agency_id.analytic_account_id.id),
            ('balance', '=', line.amount),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('reconciled', '=', False),
            ('parent_state', '=', 'posted'),
        ]

        candidates = self.env['account.move.line'].search(domain, limit=1)

        if len(candidates) == 1:
            # Calculate match score based on date proximity
            date_diff = abs((candidates.date - line.date).days)
            match_score = 100.0 - (date_diff * 5)  # -5% per day difference

            line.write({
                'matched_move_line_id': candidates.id,
                'match_status': 'auto_matched',
                'match_score': match_score,
            })
            return True

        return False

    def _try_fuzzy_description_match(self, line):
        """Match by fuzzy string similarity"""
        if not line.description:
            return False

        # Search candidates by amount first
        domain = [
            ('account_id.reconcile', '=', True),
            ('analytic_account_id', '=', self.agency_id.analytic_account_id.id),
            ('balance', '=', line.amount),
            ('reconciled', '=', False),
            ('parent_state', '=', 'posted'),
        ]

        candidates = self.env['account.move.line'].search(domain, limit=10)

        best_match = None
        best_score = 0.0

        for candidate in candidates:
            # Calculate similarity score
            similarity = self._calculate_string_similarity(
                line.description,
                candidate.name or candidate.ref or ''
            )

            if similarity > best_score and similarity >= self.match_threshold:
                best_score = similarity
                best_match = candidate

        if best_match:
            line.write({
                'matched_move_line_id': best_match.id,
                'match_status': 'auto_matched',
                'match_score': best_score,
            })
            return True

        return False

    def _calculate_string_similarity(self, str1, str2):
        """Calculate similarity percentage between two strings"""
        # Simple implementation - can be enhanced with Levenshtein distance
        str1 = str1.lower().strip()
        str2 = str2.lower().strip()

        # Exact match
        if str1 == str2:
            return 100.0

        # Tokenize and compare
        tokens1 = set(re.findall(r'\w+', str1))
        tokens2 = set(re.findall(r'\w+', str2))

        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard similarity
        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))

        return (intersection / union) * 100.0 if union > 0 else 0.0

    def action_validate_reconciliation(self):
        """Validate and finalize reconciliation"""
        self.ensure_one()

        if self.unmatched_lines > 0:
            raise UserError(_(
                'Cannot validate reconciliation with %d unmatched lines. '
                'Please match or review all lines first.'
            ) % self.unmatched_lines)

        if abs(self.difference) > 0.01:
            raise UserError(_(
                'Cannot validate reconciliation with difference of %s. '
                'Bank balance must match Odoo balance.'
            ) % self.difference)

        # Create reconciliation entries
        self._create_reconciliation_entries()

        self.write({'state': 'done'})

    def _create_reconciliation_entries(self):
        """Create account reconciliations"""
        self.ensure_one()

        for line in self.line_ids.filtered(lambda l: l.matched_move_line_id):
            # Reconcile the matched lines
            line.matched_move_line_id.reconcile()

    def action_reset_to_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.line_ids.write({
            'matched_move_line_id': False,
            'match_status': 'unmatched',
            'match_score': 0.0,
        })
        self.write({'state': 'draft'})


class BankReconciliationLine(models.Model):
    """Bank reconciliation line"""
    _name = 'finance.ssc.bank.reconciliation.line'
    _description = 'Bank Reconciliation Line'
    _order = 'date, sequence'

    reconciliation_id = fields.Many2one(
        comodel_name='finance.ssc.bank.reconciliation',
        string='Reconciliation',
        required=True,
        ondelete='cascade',
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )

    # Bank Statement Data
    date = fields.Date(
        string='Date',
        required=True,
    )
    description = fields.Char(
        string='Description',
        required=True,
    )
    reference = fields.Char(
        string='Reference',
    )
    amount = fields.Monetary(
        string='Amount',
        currency_field='currency_id',
        required=True,
    )
    currency_id = fields.Many2one(
        related='reconciliation_id.currency_id',
        string='Currency',
    )

    # Matching
    match_status = fields.Selection(
        selection=[
            ('unmatched', 'Unmatched'),
            ('auto_matched', 'Auto-Matched'),
            ('manual_matched', 'Manual'),
            ('reviewed', 'Reviewed'),
        ],
        string='Match Status',
        default='unmatched',
        required=True,
    )
    matched_move_line_id = fields.Many2one(
        comodel_name='account.move.line',
        string='Matched Journal Item',
    )
    match_score = fields.Float(
        string='Match Score %',
        default=0.0,
    )

    # Notes
    notes = fields.Text(
        string='Notes',
    )

    def action_manual_match(self):
        """Open wizard for manual matching"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Manual Match'),
            'res_model': 'finance.ssc.bank.match.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_reconciliation_line_id': self.id,
                'default_amount': self.amount,
                'default_date': self.date,
            },
        }

    def action_unmatch(self):
        """Remove matching"""
        self.write({
            'matched_move_line_id': False,
            'match_status': 'unmatched',
            'match_score': 0.0,
        })

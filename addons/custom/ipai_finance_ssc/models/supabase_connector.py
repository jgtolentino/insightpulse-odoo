# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)

# Supabase client will be imported if available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    _logger.warning("Supabase Python client not installed. Run: pip install supabase")


class SupabaseConnector(models.Model):
    """
    Supabase PostgreSQL and pgVector Integration

    Features:
    - Real-time data warehouse sync
    - PostgreSQL RPC calls
    - pgVector similarity search
    - Batch operations
    - Trial balance replication
    """
    _name = 'finance.ssc.supabase.connector'
    _description = 'Supabase Connector'

    def _get_client(self) -> 'Client':
        """Get authenticated Supabase client"""
        if not SUPABASE_AVAILABLE:
            raise UserError(_(
                'Supabase client not available. '
                'Install with: pip install supabase'
            ))

        url = self.env['ir.config_parameter'].sudo().get_param('supabase.url')
        key = self.env['ir.config_parameter'].sudo().get_param('supabase.key')

        if not url or not key:
            raise UserError(_(
                'Supabase configuration missing. '
                'Set supabase.url and supabase.key in System Parameters'
            ))

        return create_client(url, key)

    def sync_agency_data(self, agency):
        """Sync agency financial data to Supabase"""
        if not agency:
            raise UserError(_('Agency is required'))

        supabase = self._get_client()

        # Get trial balance
        trial_balance = self._get_trial_balance(agency)

        # Push to Supabase RPC
        try:
            result = supabase.rpc('sync_trial_balance', {
                'p_agency_code': agency.code,
                'p_period': fields.Date.today().strftime('%Y-%m'),
                'p_balances': json.dumps(trial_balance)
            }).execute()

            _logger.info(f"Synced trial balance for {agency.code}: {len(trial_balance)} accounts")
            return result

        except Exception as e:
            _logger.error(f"Supabase sync failed for {agency.code}: {str(e)}")
            raise UserError(_('Supabase sync failed: %s') % str(e))

    def _get_trial_balance(self, agency):
        """Calculate trial balance for agency"""
        self.env.cr.execute("""
            SELECT
                aa.code as account_code,
                aa.name as account_name,
                aat.type as account_type,
                SUM(aml.debit) as debit,
                SUM(aml.credit) as credit,
                SUM(aml.balance) as balance,
                COUNT(*) as transaction_count
            FROM account_move_line aml
            JOIN account_account aa ON aa.id = aml.account_id
            JOIN account_account_type aat ON aat.id = aa.user_type_id
            WHERE aml.analytic_account_id = %s
                AND aml.parent_state = 'posted'
            GROUP BY aa.code, aa.name, aat.type
            ORDER BY aa.code
        """, (agency.analytic_account_id.id,))

        return self.env.cr.dictfetchall()

    def sync_all_agencies(self):
        """Sync all active agencies to Supabase"""
        agencies = self.env['finance.ssc.agency'].search([('active', '=', True)])

        success_count = 0
        error_count = 0

        for agency in agencies:
            try:
                self.sync_agency_data(agency)
                agency.write({
                    'supabase_synced': True,
                    'last_sync_date': fields.Datetime.now(),
                })
                success_count += 1
            except Exception as e:
                _logger.error(f"Failed to sync {agency.code}: {str(e)}")
                error_count += 1

        return {
            'success': success_count,
            'errors': error_count,
            'total': len(agencies),
        }

    def vector_search_similar_transactions(self, description, agency_id=None, limit=10):
        """Search for similar transactions using pgvector"""
        supabase = self._get_client()

        # Get embedding (would use OpenAI/Anthropic in production)
        embedding = self._get_embedding(description)

        # Build RPC parameters
        params = {
            'query_embedding': embedding,
            'match_threshold': 0.8,
            'match_count': limit,
        }

        if agency_id:
            params['p_agency_code'] = agency_id.code

        try:
            result = supabase.rpc('similarity_search_transactions', params).execute()
            return result.data
        except Exception as e:
            _logger.error(f"Vector search failed: {str(e)}")
            return []

    def _get_embedding(self, text):
        """Generate text embedding for vector search"""
        # Placeholder - integrate with OpenAI or Anthropic
        # For now, return dummy embedding
        return [0.0] * 1536

    def push_month_end_closing(self, closing):
        """Push month-end closing data to Supabase"""
        supabase = self._get_client()

        data = {
            'agency_code': closing.agency_id.code,
            'period': closing.period.isoformat(),
            'state': closing.state,
            'duration_hours': closing.duration_hours,
            'total_debit': float(closing.total_debit),
            'total_credit': float(closing.total_credit),
            'checklist_completion': closing.checklist_completion,
            'trial_balance': closing.trial_balance_data,
        }

        try:
            result = supabase.table('month_end_closings').upsert(data).execute()
            _logger.info(f"Pushed month-end closing for {closing.agency_id.code}")
            return result
        except Exception as e:
            _logger.error(f"Failed to push month-end closing: {str(e)}")
            raise UserError(_('Failed to sync month-end closing: %s') % str(e))

    def push_bir_form(self, bir_form):
        """Push BIR form data to Supabase"""
        supabase = self._get_client()

        data = {
            'agency_code': bir_form.agency_id.code,
            'form_type': bir_form.form_type,
            'period_from': bir_form.period_from.isoformat(),
            'period_to': bir_form.period_to.isoformat(),
            'filing_date': bir_form.filing_date.isoformat(),
            'state': bir_form.state,
            'tax_payable': float(bir_form.tax_payable or bir_form.vat_payable or bir_form.tax_withheld),
            'payment_date': bir_form.payment_date.isoformat() if bir_form.payment_date else None,
        }

        try:
            result = supabase.table('bir_forms').upsert(data).execute()
            _logger.info(f"Pushed BIR form {bir_form.form_type} for {bir_form.agency_id.code}")
            return result
        except Exception as e:
            _logger.error(f"Failed to push BIR form: {str(e)}")
            raise UserError(_('Failed to sync BIR form: %s') % str(e))

    @api.model
    def cron_sync_all_agencies(self):
        """Cron job to sync all agencies daily"""
        result = self.sync_all_agencies()
        _logger.info(f"Daily Supabase sync: {result['success']}/{result['total']} agencies synced")
        return result

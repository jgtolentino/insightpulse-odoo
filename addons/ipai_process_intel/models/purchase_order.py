# -*- coding: utf-8 -*-
from odoo import models, api


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'process.intel.mixin']

    def _get_pi_process_id(self):
        """Use PO name as process ID"""
        return self.name

    def _get_pi_process_type(self):
        """Procure-to-Pay process type"""
        return 'PROCURE_TO_PAY'

    @api.model
    def action_analyze_p2p_batch(self):
        """Analyze all POs from last 30 days"""
        recent_pos = self.search([
            ('create_date', '>=', (
                self.env.context.get('analysis_start_date') or
                (fields.Datetime.now() - timedelta(days=30))
            ))
        ])

        if not recent_pos:
            raise UserError(_('No purchase orders found in the selected date range.'))

        # Trigger batch analysis via Agent Gateway
        gateway_url = f"{recent_pos[0]._get_agent_gateway_base()}/agent/pi/p2p/batch"

        payload = {
            'process_ids': recent_pos.mapped('name'),
            'date_range': recent_pos[0]._get_pi_date_range(),
        }

        response = requests.post(gateway_url, json=payload, timeout=120)
        response.raise_for_status()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Batch P2P Analysis Triggered'),
                'message': _('Analyzing %d purchase orders...') % len(recent_pos),
                'type': 'info',
            }
        }

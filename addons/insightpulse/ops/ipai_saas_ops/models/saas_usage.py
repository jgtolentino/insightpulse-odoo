# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class SaaSUsage(models.Model):
    _name = 'saas.usage'
    _description = 'SaaS Usage'
    _order = 'usage_date desc'

    tenant_id = fields.Many2one(
        comodel_name='saas.tenant',
        string='Tenant',
        required=True,
        ondelete='cascade',
    )
    usage_date = fields.Date(
        string='Usage Date',
        required=True,
        default=fields.Date.context_today,
    )
    metric_type = fields.Selection(
        selection=[
            ('users', 'Active Users'),
            ('storage', 'Storage (GB)'),
            ('api_calls', 'API Calls'),
            ('transactions', 'Transactions'),
            ('bandwidth', 'Bandwidth (GB)'),
        ],
        string='Metric Type',
        required=True,
    )
    value = fields.Float(
        string='Value',
        required=True,
    )
    unit = fields.Char(
        string='Unit',
        compute='_compute_unit',
    )
    notes = fields.Text(
        string='Notes',
    )

    def _compute_unit(self):
        """Compute unit based on metric type."""
        unit_map = {
            'users': 'users',
            'storage': 'GB',
            'api_calls': 'calls',
            'transactions': 'txns',
            'bandwidth': 'GB',
        }
        for usage in self:
            usage.unit = unit_map.get(usage.metric_type, '')

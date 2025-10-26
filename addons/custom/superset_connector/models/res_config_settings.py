# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    superset_url = fields.Char(
        string='Superset URL',
        config_parameter='superset_connector.superset_url',
        help='Base URL of your Apache Superset instance (e.g., https://superset.example.com)'
    )
    superset_username = fields.Char(
        string='Superset Username',
        config_parameter='superset_connector.superset_username',
        help='Username for Superset API authentication'
    )
    superset_password = fields.Char(
        string='Superset Password',
        config_parameter='superset_connector.superset_password',
        help='Password for Superset API authentication'
    )
    superset_database_id = fields.Integer(
        string='Database ID',
        config_parameter='superset_connector.superset_database_id',
        help='Superset database ID for Odoo data source'
    )
    superset_enable_rls = fields.Boolean(
        string='Enable Row-Level Security',
        config_parameter='superset_connector.superset_enable_rls',
        default=True,
        help='Enable row-level security filtering based on user permissions'
    )
    superset_token_expiry = fields.Integer(
        string='Token Expiry (seconds)',
        config_parameter='superset_connector.superset_token_expiry',
        default=3600,
        help='Guest token expiry time in seconds (default: 1 hour)'
    )
    superset_csp_enabled = fields.Boolean(
        string='Enable CSP Headers',
        config_parameter='superset_connector.superset_csp_enabled',
        default=True,
        help='Add Content Security Policy headers for embedded dashboards'
    )

    @api.model
    def get_superset_config(self):
        """Get Superset configuration parameters"""
        return {
            'url': self.env['ir.config_parameter'].sudo().get_param('superset_connector.superset_url'),
            'username': self.env['ir.config_parameter'].sudo().get_param('superset_connector.superset_username'),
            'password': self.env['ir.config_parameter'].sudo().get_param('superset_connector.superset_password'),
            'database_id': int(self.env['ir.config_parameter'].sudo().get_param('superset_connector.superset_database_id', 0)),
            'enable_rls': self.env['ir.config_parameter'].sudo().get_param('superset_connector.superset_enable_rls', 'True') == 'True',
            'token_expiry': int(self.env['ir.config_parameter'].sudo().get_param('superset_connector.superset_token_expiry', 3600)),
            'csp_enabled': self.env['ir.config_parameter'].sudo().get_param('superset_connector.superset_csp_enabled', 'True') == 'True',
        }

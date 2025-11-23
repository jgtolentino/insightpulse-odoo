# -*- coding: utf-8 -*-
from . import models
from . import wizards

def post_init_hook(cr, registry):
    """
    Post-installation hook to configure Okta SSO and Spectra settings.
    """
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Set default Spectra export path
    IrConfigParam = env['ir.config_parameter']
    IrConfigParam.set_param('tbwa.spectra.export_path', '/exports/spectra')
    IrConfigParam.set_param('tbwa.spectra.archive_bucket', 'tbwa-spectra-exports')

    # Enable Okta SSO provider
    oauth_provider = env['auth.oauth.provider'].search([('name', '=', 'Okta TBWA')], limit=1)
    if not oauth_provider:
        env['auth.oauth.provider'].create({
            'name': 'Okta TBWA',
            'client_id': 'OKTA_CLIENT_ID',  # To be configured
            'auth_endpoint': 'https://tbwa.okta.com/oauth2/v1/authorize',
            'scope': 'openid profile email groups',
            'validation_endpoint': 'https://tbwa.okta.com/oauth2/v1/userinfo',
            'data_endpoint': 'https://tbwa.okta.com/oauth2/v1/userinfo',
            'enabled': True,
            'body': 'Login with Okta',
        })

    # Create default approval matrix
    ApprovalMatrix = env['tbwa.approval.matrix']
    if not ApprovalMatrix.search_count([]):
        # Default approval rules (will be customizable)
        ApprovalMatrix.create({
            'name': 'Cash Advance - Standard',
            'amount_min': 0.0,
            'amount_max': 50000.0,
            'approver_level_1': 'manager',
            'approver_level_2': 'finance_head',
        })
        ApprovalMatrix.create({
            'name': 'Cash Advance - High Value',
            'amount_min': 50000.01,
            'amount_max': 999999999.99,
            'approver_level_1': 'finance_head',
            'approver_level_2': 'cfo',
        })

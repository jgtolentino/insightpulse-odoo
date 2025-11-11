# -*- coding: utf-8 -*-

from . import models


def post_init_hook(cr, registry):
    """Post-installation hook to setup BIR compliance defaults"""
    from odoo import api, SUPERUSER_ID

    env = api.Environment(cr, SUPERUSER_ID, {})

    # Create default BIR configuration for each company
    companies = env['res.company'].search([])

    for company in companies:
        # Ensure company has Philippine tax configuration
        if company.country_id.code != 'PH':
            continue

        # Create default BIR settings (future enhancement)
        # For now, just log that module is installed
        _logger = env['ir.logging'].sudo()
        _logger.create({
            'name': 'ipai_bir_compliance',
            'type': 'server',
            'level': 'INFO',
            'message': f'BIR Compliance module installed for company: {company.name}',
            'path': 'ipai_bir_compliance',
            'func': 'post_init_hook',
        })

# -*- coding: utf-8 -*-
{
    'name': 'InsightPulseAI Custom Theme',
    'version': '18.0.1.0.0',
    'category': 'Theme/Backend',
    'summary': 'Unified branding theme for InsightPulse ERP',
    'description': """
InsightPulseAI Custom Theme for Odoo 18
========================================

Applies unified branding colors and design tokens:
- Primary Color: #1455C7 (InsightPulse Blue)
- Secondary Color: #111827 (Dark Gray)
- Accent Color: #F97316 (Orange)

Matches branding across all InsightPulse services:
- Odoo ERP
- Mattermost Chat
- Apache Superset
- n8n Automation

Configuration in: config/odoo18_desired_state.json
Branding spec: config/branding_theme.json
    """,
    'author': 'InsightPulseAI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': ['web', 'portal'],
    'data': [
        'views/templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_theme/static/src/css/odoo_custom_theme.css',
        ],
        'web.assets_frontend': [
            'custom_theme/static/src/css/odoo_custom_theme.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}

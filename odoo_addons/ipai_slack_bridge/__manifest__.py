# -*- coding: utf-8 -*-
{
    'name': 'IPAI Slack Bridge',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'Bidirectional Slack integration - OAuth, Events API, message sync',
    'description': """
Slack Bridge - Bidirectional Integration
========================================

Features:
- Slack App OAuth flow
- Events API (messages, reactions, files)
- Slash commands (/odoov, custom)
- Interactive components (buttons, modals)
- Bidirectional message sync
- File sync
- User mapping

Endpoints:
- POST /slack/oauth/callback
- POST /slack/events
- POST /slack/commands
- POST /slack/actions

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['ipai_chat_core', 'base_rest'],
    
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'IPAI Connect External',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'Guest/partner collaboration spaces (Slack Connect equivalent)',
    'description': """
External Connect - Guest Collaboration
======================================

Features:
- Guest/partner portal access
- Fenced channels (external-only)
- Invite management
- Access expiration
- Activity tracking
- Partner spaces

Use cases:
- Vendor collaboration
- Client communication
- Partner projects
- External consultants

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['ipai_chat_core', 'portal'],
    
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

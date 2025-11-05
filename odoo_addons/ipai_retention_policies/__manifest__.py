# -*- coding: utf-8 -*-
{
    'name': 'IPAI Retention Policies',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'Data retention, auto-purge, legal hold exceptions',
    'description': """
Retention Policies
=================

Features:
- Per-channel retention rules
- Global retention policies
- Auto-purge (nightly cron)
- Legal hold exceptions
- Important message exceptions
- Retention reporting
- Compliance dashboard

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['ipai_chat_core', 'ipai_audit_discovery'],
    
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

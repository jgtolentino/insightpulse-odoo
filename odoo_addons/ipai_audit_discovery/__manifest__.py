# -*- coding: utf-8 -*-
{
    'name': 'IPAI Audit & eDiscovery',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'Immutable audit trail, legal hold, eDiscovery export',
    'description': """
Audit & eDiscovery
=================

Features:
- Immutable audit trail
- Legal hold (freeze deletions)
- eDiscovery export (filtered)
- Export formats (JSON, CSV, ZIP)
- SIEM integration API
- Compliance reporting

Events tracked:
- User actions (login/logout)
- Channel operations
- Message operations
- File operations
- DLP violations
- Hold operations
- Export requests

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['ipai_chat_core', 'auditlog'],
    
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

# -*- coding: utf-8 -*-
{
    'name': 'IPAI DLP Guard',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'Data Loss Prevention - pattern detection, quarantine, review',
    'description': """
DLP Guard - Data Loss Prevention
================================

Features:
- Pattern-based detection (regex)
- Pre-defined rules (SSN, credit cards, API keys, TIN)
- Custom rules
- Actions (block, quarantine, mask, alert)
- Admin review queue
- Compliance reporting

Built-in patterns:
- US Social Security Numbers
- Credit card numbers
- API keys and tokens
- Philippine TIN
- Custom regex patterns

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['ipai_chat_core'],
    
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

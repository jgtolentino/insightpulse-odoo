# -*- coding: utf-8 -*-
{
    'name': 'IPAI Workflow Bot',
    'version': '19.0.1.0.0',
    'category': 'Discuss',
    'summary': 'Slash commands, interactive dialogs, workflow automation',
    'description': """
Workflow Bot - Automation
=========================

Features:
- Custom slash commands
- Interactive dialogs/modals
- Server action integration
- Workflow builder UI
- Command history
- Approval workflows

Built-in commands:
- /odoov - Search Odoo
- /approve - Approve request
- /status - Show status
- /leave - Request leave
- /expense - Create expense
- /invoice - Create invoice
- /task - Create task

    """,
    'author': 'InsightPulse AI',
    'website': 'https://github.com/jgtolentino/insightpulse-odoo',
    'license': 'LGPL-3',
    'depends': ['ipai_chat_core', 'base_automation'],
    
    'data': [
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

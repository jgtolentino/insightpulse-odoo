# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse AI Agent',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'AI-powered chatbot for Odoo Discuss with automation capabilities',
    'description': """
InsightPulse AI Agent
=====================

AI-powered chatbot integrated with Odoo Discuss for:
- Expense approval automation
- Deployment management
- BIR form generation
- Multi-agency financial operations
- Natural language automation

Features:
---------
* @ipai-bot mention to trigger AI assistant
* Agency-aware context (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
* Role-based access control
* Integration with DigitalOcean Agent Platform
* CLI command execution
* Real-time Odoo data access

Author: Jake Tolentino
License: AGPL-3
""",
    'author': 'Jake Tolentino',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
        'hr_expense',
        'account',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/bot_user.xml',
        'data/channels.xml',
        'views/chatbot_config_views.xml',
        'views/agent_log_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

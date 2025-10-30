# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    'name': 'InsightPulse SaaS Ops',
    'version': '19.0.1.0.0',
    'category': 'Operations',
    'summary': 'Self-service tenant creation and automated backups',
    'author': 'InsightPulse AI',
    'website': 'https://insightpulse.ai',
    'license': 'LGPL-3',
    'depends': [
        'ipai_core',
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/saas_tenant_views.xml',
        'views/saas_backup_views.xml',
        'views/saas_usage_views.xml',
        'views/saas_ops_menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

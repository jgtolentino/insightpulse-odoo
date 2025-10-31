# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse AI - Finance Shared Service Center',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Multi-agency Finance SSC with BIR compliance, month-end automation, and consolidation',
    'description': """
Multi-Agency Finance Shared Service Center
==========================================

Complete finance management for 8 agencies:
- RIM (Research Institute for Mindanao)
- CKVC (Convergence Knowledge Ventures Corporation)
- BOM (Business of Mindanao)
- JPAL (Abdul Latif Jameel Poverty Action Lab)
- JLI (Jaff Law Institute)
- JAP (Jaff Advocacy Partners)
- LAS (Legal Advisory Services)
- RMQB (Research Mindanao Quality Benchmarking)

Key Features:
- Month-end closing automation (10 days → 2 days)
- BIR forms auto-generation (1601-C, 2550Q, 1702-RT)
- Bank reconciliation with 80% auto-match
- Trial balance generation in 30 seconds
- Multi-agency consolidation
- Real-time Supabase sync
- Notion task management integration
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'analytic',
        'account_bank_statement_import',
        'account_reconcile_oca',  # OCA
        'account_financial_report',  # OCA
        'account_lock_date_update',  # OCA
        'queue_job',
    ],
    'data': [
        # Security
        'security/finance_ssc_security.xml',
        'security/ir.model.access.csv',

        # Master Data
        'data/agencies_data.xml',
        'data/bir_forms_data.xml',
        'data/ir_cron_data.xml',

        # Views
        'views/agency_views.xml',
        'views/month_end_closing_views.xml',
        'views/bir_forms_views.xml',
        'views/bank_reconciliation_views.xml',
        'views/consolidation_views.xml',
        'views/menus.xml',

        # Wizards
        'wizards/month_end_closing_wizard_views.xml',
        'wizards/bir_filing_wizard_views.xml',
        'wizards/consolidation_wizard_views.xml',

        # Reports
        'reports/trial_balance_report.xml',
        'reports/bir_forms_report.xml',
        'reports/consolidation_report.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}

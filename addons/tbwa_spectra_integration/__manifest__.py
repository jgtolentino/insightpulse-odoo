# -*- coding: utf-8 -*-
{
    'name': 'TBWA Spectra Integration',
    'version': '1.0.0',
    'category': 'Accounting/Finance',
    'summary': 'Spectra GL System Integration with Okta SSO and Expense Automation',
    'description': """
TBWA Spectra Integration Module
================================

Complete integration system for TBWA Finance Operations:

Features:
---------
* Spectra GL export automation (CSV/Excel formats)
* Okta SSO authentication with MFA enforcement
* Cash Advance workflow with Spectra mapping
* Expense liquidation with dual approval
* n8n automation triggers
* Compliance audit trails
* Role-based approval matrix

Spectra Mapping:
----------------
* Cash Advances → CASH_ADV_HO
* Liquidations → EXPENSE_ENTRY
* Vendor Payments → AP_LEDGER
* Journal Entries → GL_TRANSACTIONS
* Approval Trail → AUDIT_LOG

Export Templates:
-----------------
* TBWA_EXPENSES_MMYY.csv
* TBWA_JE_MMYY.csv
* TBWA_CA_MMYY.csv
* TBWA_AUDIT_MMYY.csv

Integration Stack:
------------------
* Odoo CE 18.0 (Core ERP)
* Okta SSO (Identity Provider)
* n8n (Automation Engine)
* Supabase (Export Archive)
* Spectra (Target GL System)

Environment: TBWA-PROD
""",
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'hr_expense',
        'account',
        'analytic',
        'mail',
        'auth_oauth',  # OCA module for Okta SSO
        'base_export_manager',  # OCA module for export templates
    ],
    'external_dependencies': {
        'python': [
            'okta',  # Okta SDK
            'pytz',  # Timezone handling
            'pandas',  # Data transformation
        ],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/tbwa_security.xml',
        'data/spectra_mapping_data.xml',
        'data/approval_matrix_data.xml',
        'data/export_templates_data.xml',
        'data/tbwa_cron.xml',
        'views/hr_expense_advance_views.xml',
        'views/spectra_export_views.xml',
        'views/spectra_mapping_views.xml',
        'views/approval_matrix_views.xml',
        'views/tbwa_menu.xml',
        'wizards/spectra_export_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
}

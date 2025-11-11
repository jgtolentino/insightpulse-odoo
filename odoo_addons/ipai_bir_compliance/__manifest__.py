# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse BIR Compliance',
    'version': '18.0.1.0.0',
    'category': 'Accounting/Localizations',
    'summary': 'Philippine BIR Tax Forms Automation (1601-C, 2550Q, 1702-RT)',
    'description': """
Philippine BIR Compliance Module
=================================

Automate Philippine Bureau of Internal Revenue (BIR) tax form generation,
validation, and e-filing for Finance Shared Service Centers.

Key Features:
-------------
* **Form 1601-C**: Monthly Withholding Tax Return
* **Form 2550Q**: Quarterly VAT Declaration
* **Form 1702-RT**: Annual Income Tax Return
* **Form 2307**: Certificate of Creditable Tax Withheld at Source

Features:
---------
* Auto-generate BIR forms from General Ledger transactions
* Validate forms against official BIR schemas (v8.0)
* Export to PDF (for printing) and XML (for eBIRForms upload)
* Multi-company support (8 legal entities)
* Audit trail with digital signatures
* 98%+ validation accuracy on historical data

Compliance:
-----------
* BIR Revenue Regulations compliance
* 10-year audit trail retention
* Immutable transaction logs
* Digital signature support

Multi-Agency Support:
---------------------
Pre-configured for 8 Philippine agencies:
* RIM - Refugee International Mission
* CKVC - CKVC Foundation
* BOM - BOM Organization
* JPAL - JPAL Philippines
* JLI - JLI Institute
* JAP - JAP Association
* LAS - LAS Services
* RMQB - RMQB Corp

Roadmap:
--------
* M1 (Weeks 5-8): Core forms (1601-C, 2550Q)
* M2 (Weeks 9-12): Advanced forms (1702-RT, 2307)
* M3 (Future): E-filing API integration

Technical Details:
------------------
* Python 3.10+
* PostgreSQL 15+
* Odoo 18.0 CE
* OCA modules: account-financial-reporting, account-financial-tools

Author: InsightPulse AI
License: LGPL-3
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'account_accountant',
        'l10n_ph',  # Philippine localization
    ],
    'external_dependencies': {
        'python': ['lxml', 'PyPDF2'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Data
        'data/bir_validation_rules.xml',
        'data/bir_tax_codes.xml',

        # Views
        'views/bir_menu.xml',
        'views/bir_form_1601c_views.xml',
        'views/bir_form_2550q_views.xml',
        'views/bir_form_1702rt_views.xml',

        # Reports
        'reports/bir_reports.xml',
        'reports/bir_1601c_pdf_template.xml',
        'reports/bir_2550q_pdf_template.xml',
    ],
    'demo': [
        # Demo data for testing
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'post_init_hook': 'post_init_hook',
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
}

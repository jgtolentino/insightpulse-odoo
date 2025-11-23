# -*- coding: utf-8 -*-
{
    "name": "TBWA Spectra Integration",
    "summary": "Integration with Spectra finance system for TBWA.",
    "version": "18.0.1.0.0",
    "category": "Accounting/Finance",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "account",
        "hr_expense",
    ],
    "data": [
        # Security (must load first)
        "security/tbwa_security.xml",
        "security/ir.model.access.csv",
        # Data files (load after security, before views)
        "data/users_data.xml",
        "data/tbwa_cron.xml",
        # 'data/spectra_mapping_data.xml',  # TODO: Create
        # 'data/approval_matrix_data.xml',  # TODO: Create
        # 'data/export_templates_data.xml',  # TODO: Create
        # Views (load last, comment out until created)
        'views/hr_expense_advance_views.xml',
        # 'views/spectra_export_views.xml',  # TODO: Create
        # 'views/spectra_mapping_views.xml',  # TODO: Create
        # 'views/approval_matrix_views.xml',  # TODO: Create
        # 'views/tbwa_menu.xml',  # TODO: Create
        # Wizards (load after views)
        # 'wizards/spectra_export_wizard_views.xml',  # TODO: Create
    ],
    "installable": True,
    "application": False,
}

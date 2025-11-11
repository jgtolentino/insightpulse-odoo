# -*- coding: utf-8 -*-
{
    "name": "InsightPulse AI - App Sources",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Display addon sources (OCA, Custom, Community) in Apps list",
    "description": """
        Enhanced Apps List with Source Information
        ==========================================

        Features:
        * Shows source repository for each module
        * Filters by source (Odoo Community, OCA, Custom)
        * Direct links to module documentation
        * Update tracking for OCA modules
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "depends": ["base"],
    "data": [
        "views/ir_module_module_views.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}

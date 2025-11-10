# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "InsightPulse PPM Core",
    "version": "19.0.1.0.0",
    "category": "Project",
    "summary": "Program/Project/Budget/Risk Management",
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "LGPL-3",
    "depends": [
        "ipai_core",
        "project",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ppm_program_views.xml",
        "views/ppm_roadmap_views.xml",
        "views/ppm_risk_views.xml",
        "views/ppm_budget_views.xml",
        "views/ppm_menu.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

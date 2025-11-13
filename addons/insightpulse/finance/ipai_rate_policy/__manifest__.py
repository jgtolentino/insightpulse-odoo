# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "InsightPulse Rate Policy Automation",
    "version": "18.0.1.0.0",
    "category": "Finance",
    "summary": "Automated rate calculation with P60 + 25% markup",
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "LGPL-3",
    "depends": [
        "ipai_core",
        "hr",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/rate_policy_views.xml",
        "views/rate_policy_line_views.xml",
        "views/rate_calculation_log_views.xml",
        "views/rate_policy_menu.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

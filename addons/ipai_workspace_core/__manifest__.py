# ipai_workspace_core/__manifest__.py
{
    "name": "InsightPulse Workspace Core",
    "summary": "Unified workspace model for marketing agencies and accounting firms.",
    "version": "18.0.1.0.0",
    "category": "InsightPulse/Core",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.com",
    "license": "AGPL-3",
    # Smart Delta: ONLY depend on the foundation module
    "depends": [
        "ipai_dev_studio_base",
    ],
    "data": [
        # security
        "security/ir.model.access.csv",
        # views
        "views/ipai_workspace_views.xml",
        "views/ipai_workspace_menu.xml",
    ],
    "demo": [],
    "application": False,
    "installable": True,
}

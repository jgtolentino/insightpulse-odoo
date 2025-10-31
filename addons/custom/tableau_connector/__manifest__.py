{
    "name": "Tableau Connector",
    "version": "19.0.251026.1",
    "category": "Connectors",
    "summary": "Tableau analytics integration for Odoo",
    "description": """
    Integrate Tableau dashboards and analytics into Odoo:
    - Embed Tableau dashboards in Odoo views
    - Data export from Odoo to Tableau
    - Authentication and security integration
    - Dashboard management interface
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/apps/tableau_connector",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/tableau_config_views.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}

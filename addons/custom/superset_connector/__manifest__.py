{
    "name": "Superset Connector",
    "version": "19.0.251027.1",
    "category": "Connectors",
    "summary": "Apache Superset integration for Odoo",
    "description": """
    Integrate Apache Superset dashboards and analytics into Odoo:
    - Embed Superset dashboards in Odoo views
    - Single Sign-On (SSO) integration
    - Dashboard management interface
    - Data source synchronization
    - URL injection protection (CVSS 6.5 fix)
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/odoo/apps/superset_connector",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "data/cron_jobs.xml",
        "views/superset_config_views.xml",
        "views/menus.xml",
        "views/templates/dashboard_templates.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}

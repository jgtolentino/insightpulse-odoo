{
    "name": "Superset BI Integration",
    "version": "19.0.1.0.0",
    "category": "Reporting",
    "summary": "Replace native Odoo dashboards with Superset BI analytics",
    "description": """
Superset BI Integration
=======================

Replaces Odoo's built-in Dashboards module with Superset-powered analytics:

* Sales Dashboard - Real-time sales metrics and forecasting
* Finance Dashboard - Financial KPIs and cash flow analysis
* HR Dashboard - Employee metrics and workforce analytics

All dashboards leverage Superset's advanced visualization capabilities
with proper RBAC and row-level security inherited from Odoo permissions.
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["base", "web"],
    "data": [
        "data/menu_data.xml",
    ],
    "assets": {},
    "installable": True,
    "application": False,
    "auto_install": False,
}

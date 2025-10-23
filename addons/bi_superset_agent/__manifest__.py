{
    "name": "BI Superset Agent",
    "version": "19.0.1.0.0",
    "category": "Business Intelligence",
    "summary": "Natural Language Analytics with Apache Superset",
    "description": """
        BI Superset Agent for Odoo 19
        ==============================

        Features:
        - Natural language to SQL query conversion
        - Automatic Superset chart generation
        - Dashboard composition and management
        - Embedded chart/dashboard viewer
        - Multi-company support with RLS

        Integrates with:
        - FastAPI agent service
        - Apache Superset (self-hosted or cloud)
        - OpenAI GPT-4o-mini for NL processing
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "depends": ["base", "web"],
    "data": [
        "security/bi_security.xml",
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "views/bi_analytics_views.xml",
        "views/bi_dashboard_views.xml",
        "views/res_config_settings_views.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "bi_superset_agent/static/src/css/bi_superset.css",
            "bi_superset_agent/static/src/components/bi_chart_viewer.js",
            "bi_superset_agent/static/src/components/bi_chart_viewer.xml",
        ]
    },
    "installable": True,
    "application": True,
    "license": "LGPL-3",
}

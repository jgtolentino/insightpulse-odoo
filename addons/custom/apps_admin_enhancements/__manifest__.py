{
    "name": "Apps Admin Enhancements",
    "version": "19.0.251026.1",
    "category": "Tools",
    "summary": "Enhanced Apps management with source tracking and accessibility",
    "description": """
    Enhanced Apps interface with:
    - Module source tracking (Odoo/OCA/Custom)
    - Accessibility status (module present on disk)
    - Effective website URLs for your domain
    - Automatic module index refresh
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/odoo/apps/apps_admin_enhancements",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_module_views.xml",
        "data/cron_refresh.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
}

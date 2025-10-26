{
    "name": "Microservices Connector",
    "version": "19.0.251026.2",
    "category": "Connectors",
    "summary": "Integration with OCR, LLM, and Agent microservices",
    "description": """
    Connect Odoo with your microservices ecosystem:
    - OCR Service integration for document processing
    - LLM Service integration for AI-powered features
    - Agent Service integration for workflow automation
    - API gateway and service discovery
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/odoo/apps/microservices_connector",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/microservices_config_views.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}

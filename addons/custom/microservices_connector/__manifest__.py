{
    "name": "Microservices Connector",
    "version": "18.0.251027.1",
    "category": "Connectors",
    "summary": "Integration with OCR, LLM, and Agent microservices",
    "description": """
    Connect Odoo with your microservices ecosystem:
    - OCR Service integration for document processing
    - LLM Service integration for AI-powered features
    - Agent Service integration for workflow automation
    - API gateway and service discovery
    - Encrypted credential storage with Fernet (CVSS 8.1 fix)
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/odoo/apps/microservices_connector",
    "depends": ["base", "web"],
    "external_dependencies": {
        "python": ["cryptography"],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/microservices_config_views.xml",
        "views/menus.xml",
        "data/migrate_credentials.xml",
    ],
    "demo": [],
    "installable": True,
    "application": True,
    "auto_install": False,
    "license": "AGPL-3",
}

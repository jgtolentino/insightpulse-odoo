{
    "name": "Security Hardening",
    "version": "18.0.251026.1",
    "category": "Security",
    "summary": "Security hardening features for Odoo deployment",
    "description": """
    Security hardening features:
    - Block database manager in production
    - Enhanced security headers
    - Audit trail enforcement
    - Security monitoring
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/odoo/apps/security_hardening",
    "depends": ["base", "web"],
    "data": [
        "security/ir.model.access.csv",
        "views/templates.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "AGPL-3",
}

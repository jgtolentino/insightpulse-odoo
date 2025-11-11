{
    "name": "Pulser Hub Sync",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "GitHub App integration for Pulser Hub webhook and OAuth",
    "description": """
GitHub App Integration
======================
This module provides integration with GitHub App "pulser-hub" for:
* OAuth 2.0 authentication flow
* Webhook event processing
* Installation token management
* Repository event handling

Configuration:
* App ID: 2191216
* PEM Path: ~/.github/apps/pulser-hub.pem (configured via environment variables)
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": ["base", "web", "queue_job"],
    "data": [
        "security/ir.model.access.csv",
        "views/github_integration_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

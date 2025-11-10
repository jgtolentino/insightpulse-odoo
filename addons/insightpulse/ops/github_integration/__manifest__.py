{
    "name": "GitHub Integration (pulser-hub)",
    "version": "1.0.0",
    "category": "Operations",
    "summary": "GitHub webhook and OAuth integration via pulser-hub app",
    "description": """
GitHub Integration Module
=========================

Integrates GitHub events with Odoo via the pulser-hub GitHub App.

Features:
---------
* Webhook endpoint (/odoo/github/webhook) for GitHub events
* OAuth callback handler (/odoo/github/auth/callback)
* Track pull requests, issues, and commits in Odoo
* Trigger Odoo automated actions from GitHub events
* Call GitHub API from Odoo
* Sync GitHub issues with Odoo tasks

Supported Events:
-----------------
* pull_request (opened, closed, merged, labeled)
* pull_request_review (submitted, approved)
* issues (opened, closed, labeled)
* push (to main/develop branches)
* issue_comment (bot commands)

Configuration:
--------------
Set these system parameters:
- github.app_id = 2191216
- github.client_id = Iv23liwGL7fnYySPPAjS
- github.client_secret = [SECRET]
- github.webhook_secret = [SECRET]
- github.private_key = [PEM]

GitHub App: pulser-hub
Owner: @jgtolentino
Homepage: https://insightpulseai.net/pulser-hub
    """,
    "author": "InsightPulse",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [
        "base",
        "project",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/github_repository_views.xml",
        "views/github_pull_request_views.xml",
        "views/github_issue_views.xml",
        "views/github_webhook_views.xml",
        "data/github_config.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "maintainers": ["jgtolentino"],
}

{
    "name": "InsightPulse Slack Bridge",
    "version": "19.0.1.0.0",
    "category": "Productivity",
    "summary": "Slack integration for InsightPulse AI agencies",
    "description": """
InsightPulse Slack Bridge
=========================

Slack bot integration for multi-agency Finance SSC operations:
- Event subscriptions (app_mention, message.channels)
- Slash commands (/odoo, /expense, /bir)
- Automated notifications for critical workflows
- Agency-specific channel mapping

Agencies supported: RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB
    """,
    "author": "Jake Tolentino",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/slack_channel_views.xml",
        "data/slack_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

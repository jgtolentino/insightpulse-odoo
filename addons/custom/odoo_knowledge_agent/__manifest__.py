# -*- coding: utf-8 -*-
{
    "name": "Odoo Knowledge Agent",
    "version": "18.0.1.0.0",
    "category": "Tools",
    "summary": "Forum scraper and error prevention for Odoo custom modules",
    "description": """
Odoo Knowledge Agent
====================

Scrapes solved issues from Odoo forum to build:
- Error prevention guardrails
- Auto-fix patches
- Knowledge base for troubleshooting

Features:
- Automated forum scraping via cron job
- Extracts ~1,100 solved issues
- Generates preventive guardrails
- Creates auto-patch scripts
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [
        "base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/cron_forum_scraper.xml",
        "views/knowledge_agent_views.xml",
    ],
    "external_dependencies": {
        "python": ["playwright"],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}

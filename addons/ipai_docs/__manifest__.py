# -*- coding: utf-8 -*-
{
    "name": "IPAI Docs",
    "summary": "Internal knowledge base and documentation pages for InsightPulseAI",
    "version": "18.0.1.0.0",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "category": "Knowledge",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/ipai_doc_views.xml",
        "views/ipai_doc_tag_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
}

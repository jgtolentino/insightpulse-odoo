# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance Monthly Closing",
    "summary": "Structured month-end closing and BIR filing on top of Projects (CE/OCA-only).",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "depends": ["project"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task_views.xml",
        "data/project_templates.xml",
    ],
    "installable": True,
    "application": False,
}

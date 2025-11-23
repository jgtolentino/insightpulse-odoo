# -*- coding: utf-8 -*-
{
    "name": "IPAI Finance PPM",
    "summary": "Finance Project Portfolio Management (Notion Parity).",
    "version": "18.0.1.0.0",
    "category": "Accounting/Finance",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/finance_person_views.xml",
        "views/finance_task_views.xml",
        "views/bir_schedule_views.xml",
        "views/ppm_dashboard_views.xml",
        "views/menus.xml",
        "data/bir_schedule_seed.xml",
    ],
    "installable": True,
    "application": True,
}

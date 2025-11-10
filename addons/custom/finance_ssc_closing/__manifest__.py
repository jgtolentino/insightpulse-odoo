# -*- coding: utf-8 -*-
{
    "name": "Finance SSC Month-End Closing",
    "version": "19.0.1.0.0",
    "category": "Accounting/Finance",
    "summary": "Month-end closing checklist and BIR compliance tracking for Finance Shared Service Center",
    "description": """
Finance SSC Month-End Closing Module
=====================================

This module provides comprehensive month-end closing workflow management for
Finance Shared Service Centers (SSC) handling multiple agencies.

Key Features:
-------------
* Month-end closing task management
* BIR compliance checklist (Forms 1601-C, 1702-RT, 2550Q, etc.)
* Multi-agency support (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
* Approval workflows
* Document attachment management
* Automated reminders and notifications
* Dashboard and reporting
* Integration with InsightPulse AI for OCR and automation

Notion Enterprise Equivalent:
-----------------------------
This module replaces Notion's database and workflow features specifically
tailored for Finance SSC operations, providing:
- Task databases with custom properties
- Kanban views for workflow management
- Multi-level approval workflows
- Document version control
- @mentions and notifications
- Timeline views
- Custom dashboards

Technical Details:
------------------
- Odoo Version: 19.0
- Depends on: account, project, mail
- OCA Dependencies: auditlog, approval_request (optional)
- License: LGPL-3
    """,
    "author": "InsightPulse AI",
    "website": "https://github.com/jgtolentino/insightpulse-odoo",
    "license": "LGPL-3",
    "depends": [
        "base",
        "account",
        "account_accountant",
        "project",
        "mail",
        "hr",
        "web",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        # Security
        "security/ir.model.access.csv",
        "security/security.xml",
        # Data
        "data/closing_task_templates.xml",
        "data/bir_form_templates.xml",
        "data/mail_templates.xml",
        "data/scheduled_actions.xml",
        # Views
        "views/closing_period_views.xml",
        "views/closing_task_views.xml",
        "views/bir_compliance_views.xml",
        "views/closing_dashboard_views.xml",
        "views/menus.xml",
        # Wizards
        "wizard/generate_closing_tasks_views.xml",
        "wizard/bulk_approve_views.xml",
        # Reports
        "reports/closing_report_template.xml",
        "reports/bir_compliance_report.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "finance_ssc_closing/static/src/css/closing_dashboard.css",
            "finance_ssc_closing/static/src/js/closing_dashboard.js",
        ],
    },
    "images": [
        "static/description/icon.png",
        "static/description/banner.png",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
    "post_init_hook": "post_init_hook",
}

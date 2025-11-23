# -*- coding: utf-8 -*-
{
    'name': 'PPM Monthly Close Scheduler',
    'version': '1.0.0',
    'category': 'Project Management',
    'summary': 'Automated monthly financial close scheduling with PPM and Notion workspace parity',
    'description': """
Monthly Financial Close Scheduler
==================================

Implements recurring monthly close workflow with:

* PPM-style project scheduling (Clarity parity)
* Task templates with owner/reviewer/approver roles
* Business day calculation (S = C - 3 working days)
* Automated task creation via cron
* Notion workspace parity (database view)
* n8n integration for notifications

Features:
---------
* Recurring schedule: 3rd business day before month-end
* Multi-agency support (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
* Role-based workflow (Owner → Reviewer → Approver)
* Gantt visualization
* Status tracking (To Do → In Progress → For Review → For Approval → Done)

Integration:
------------
* ipai_ppm_portfolio - Portfolio/program/project hierarchy
* project - Core Odoo project management
* mail - Activity tracking and notifications
* n8n - Automation workflows
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'project',
        'mail',
        'resource',  # For business day calculations
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ppm_close_template_data_REAL.xml',
        'data/ppm_close_cron.xml',
        'views/ppm_monthly_close_views.xml',
        'views/ppm_close_task_views.xml',
        'views/ppm_close_template_views.xml',
        'views/ppm_close_menu.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

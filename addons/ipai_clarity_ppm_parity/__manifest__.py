# -*- coding: utf-8 -*-
{
    'name': 'InsightPulse Clarity PPM Parity',
    'version': '18.0.1.0.0',
    'category': 'Project Management',
    'summary': (
        'Broadcom Clarity PPM feature parity for Odoo 18 CE '
        'with complete WBS hierarchy'
    ),
    'description': """
Clarity PPM Parity for Odoo
============================

Complete Broadcom Clarity PPM Work Breakdown Structure implementation:
- Project (root container)
- Phase (WBS grouping via parent tasks)
- Milestone (zero-duration progress markers)
- Task (units of work with dependencies)
- To-Do Item (granular checklists)

Features:
---------
* Clarity ID field for project tracking
* Health status indicators (Green/Yellow/Red)
* Baseline vs Actual variance tracking
* Phase progress rollup from child tasks
* Milestone gate workflows with approval
* Task dependencies (FS, SS, FF, SF)
* To-Do items with assignees and due dates
* Gantt chart visualization
* Finance PPM integration for BIR tax filing
* Mattermost notifications for phase gates

Dependencies:
-------------
* OCA project_key
* OCA project_category
* OCA project_wbs
* OCA project_parent_task_filter
* OCA project_milestone
* OCA project_task_milestone
* OCA project_task_dependency
* OCA project_task_checklist
* OCA project_timeline

Author: InsightPulse AI
License: AGPL-3
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'AGPL-3',
    'depends': [
        'project',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/ppm_seed_users.xml',
        'data/clarity_data.xml',
        'data/bir_schedule_2025_2026.xml',
        'data/month_end_closing_nov_dec_2025.xml',
        'data/month_end_closing_detailed_workflow.xml',
        'views/project_project_views.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

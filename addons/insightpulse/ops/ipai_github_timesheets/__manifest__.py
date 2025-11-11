# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "InsightPulse GitHub Timesheets",
    "version": "19.0.1.0.0",
    "category": "Project Management",
    "summary": "Sync GitHub PRs/Issues with Odoo timesheets for financial tracking",
    "description": """
        GitHub Timesheets Integration
        ==============================

        Automates the connection between GitHub development activity and Odoo financial tracking:

        **Features:**
        - Sync GitHub PRs → Odoo project tasks
        - Sync GitHub Issues → Odoo project tasks
        - Track GitHub Projects with budgets and spend
        - Prompt developers for timesheet entries on PR merge
        - Auto-calculate project costs based on employee rates
        - Sync cost data back to GitHub Projects API
        - Track CapEx vs OpEx expenses
        - Generate CFO dashboards in Superset

        **Use Cases:**
        - R&D cost tracking (CapEx/OpEx classification)
        - Project budget vs. actual spend monitoring
        - Developer productivity metrics
        - Feature ROI analysis
        - Automated timesheet reminders

        **Integration Flow:**
        1. GitHub webhook → Odoo controller
        2. Create/update Odoo task for PR/Issue
        3. Developer logs time in Odoo
        4. Cost auto-calculates (hours × rate)
        5. Sync back to GitHub Projects API

        **Setup Required:**
        - GitHub webhook configured to point to /github/webhook
        - GitHub Personal Access Token with repo and project permissions
        - Odoo employees with hourly rates configured
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulse.ai",
    "license": "LGPL-3",
    "depends": [
        "ipai_core",
        "base",
        "project",
        "hr_timesheet",
        "account",  # For CapEx/OpEx tracking
    ],
    "external_dependencies": {
        "python": [
            "requests",
            "PyGithub",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/github_expense_types.xml",
        "views/github_project_views.xml",
        "views/github_pull_request_views.xml",
        "views/github_issue_views.xml",
        "views/github_timesheet_views.xml",
        "views/github_sync_log_views.xml",
        "views/github_config_views.xml",
        "views/github_menu.xml",
    ],
    "demo": [
        "demo/demo_github_projects.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

{
    "name": "IPAI Approvals",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "summary": "Unified Approvals Engine - Epic 1 (Clarity PPM Parity)",
    "description": """
Unified Approvals Engine
========================

Complete approval workflow system with:
- Purchase Order approvals
- Expense approvals
- Invoice approvals
- Custom approval rules
- Automated routing
- Escalation handling
- Chatter integration
- Activity tracking

Part of InsightPulse Enterprise SaaS Parity (Epic 1)
""",
    "author": "InsightPulse",
    "website": "https://insightpulse.ai",
    "license": "LGPL-3",
    "depends": [
        "ipai_core",
        "purchase",
        "hr_expense",
        "account",
        "queue_job",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order_views.xml",
        "views/hr_expense_views.xml",
        "views/account_move_views.xml",
        "data/approval_flows.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

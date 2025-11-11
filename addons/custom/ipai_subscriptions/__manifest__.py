{
    "name": "IPAI Subscriptions",
    "version": "18.0.20251026.1",
    "category": "Sales/Subscriptions",
    "summary": "Recurring revenue management with MRR/ARR tracking",
    "description": """
    Subscription and recurring revenue management.

    Features:
    - Recurring revenue tracking (MRR/ARR)
    - Subscription lifecycle management
    - Automated invoice generation
    - Contract renewal workflows
    - Churn analysis and metrics
    """,
    "license": "AGPL-3",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/odoo/apps/ipai_subscriptions",
    "depends": [
        "base",
        "mail",
        "account",
        "product",
        "uom",
        "contract",
        "contract_sale",
        "contract_invoice",
        "queue_job",
    ],
    "data": ["security/ir.model.access.csv", "data/sequence.xml", "data/cron.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}

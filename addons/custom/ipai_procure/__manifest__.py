{
    "name": "IPAI Procure",
    "version": "19.0.20251026.1",
    "category": "Inventory/Purchase",
    "summary": "PR → RFQ → PO → GRN → 3WM with approvals, catalogs, rounds",
    "description": """
    Strategic sourcing and supplier relationship management.

    Features:
    - Complete procurement cycle (PR → RFQ → PO → GRN → 3-way matching)
    - Multi-round RFQ support
    - Approval workflows with tier validation
    - Vendor catalogs and contract management
    - Quality control integration
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/odoo/apps/ipai_procure",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "purchase",
        "stock",
        "account",
        "product",
        "uom",
        "queue_job",
        "base_tier_validation",
        "report_xlsx",
        "server_environment",
    ],
    "data": ["security/ir.model.access.csv", "data/sequence.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}

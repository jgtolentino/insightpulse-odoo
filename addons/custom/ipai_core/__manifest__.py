{
    "name": "IPAI Core",
    "version": "19.0.1.0.0",
    "category": "Technical",
    "summary": "Core infrastructure for InsightPulse Enterprise SaaS Parity",
    "description": """
IPAI Core Infrastructure
========================
Foundation module providing shared infrastructure for all IPAI enterprise modules.

Features:
* Unified approval workflow engine
* Rate policy calculation framework
* AI workspace connector base
* Multi-tenancy utilities
* RLS policy templates
* Audit trail decorators
* Queue job utilities
* Chatter integration helpers

This module is required by:
- ipai_approvals
- ipai_ppm_costsheet
- ipai_rate_policy
- ipai_ppm
- ipai_knowledge_ai
- ipai_saas_ops
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "queue_job",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/approval_flow_views.xml",
        "data/sequence.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

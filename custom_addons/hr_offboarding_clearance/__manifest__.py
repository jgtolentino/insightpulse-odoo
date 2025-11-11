# -*- coding: utf-8 -*-
{
    "name": "HR Offboarding Clearance",
    "version": "18.0.1.0.0",
    "category": "Human Resources",
    "summary": "Employee offboarding clearance workflow with BIR compliance",
    "description": """
Employee Offboarding Clearance Management
==========================================

Features:
---------
* Multi-department clearance workflow (IT, Finance, Admin)
* Digital signature routing via Sign module
* Automated final pay computation with BIR withholding tax integration
* BIR Form 2316 generation trigger
* Helpdesk ticket creation for payroll processing
* Full audit trail with mail.thread integration

BIR Compliance:
--------------
* Integrates with scout.transactions for YTD withholding tax computation
* Supports 15th/30th cutoff proration logic
* Generates BIR-compliant final payslip breakdown
* Auto-triggers Form 2316 generation on exit

Technical:
----------
* Multi-tenant via company_id isolation
* Row-Level Security compatible
* Supabase integration for tax data
* OCA-compliant module structure
    """,
    "author": "InsightPulse AI",
    "website": "https://insightpulseai.net",
    "license": "LGPL-3",
    "depends": [
        "hr",
        "hr_contract",
        "mail",
        "portal",
    ],
    "external_dependencies": {
        "python": [],
    },
    "data": [
        # Security
        "security/ir.model.access.csv",
        "security/hr_offboarding_security.xml",
        # Data
        "data/ir_sequence_data.xml",
        "data/clearance_checklist_templates.xml",
        # Views
        "views/hr_offboarding_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}

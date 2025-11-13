{
    "name": "IPAI PPM Cost Sheets",
    "version": "18.0.1.0.0",
    "category": "Project Management",
    "summary": "Vendor-Privacy Cost Sheets - Epic 2 (Clarity PPM + SAP Ariba Parity)",
    "description": """
Vendor-Privacy Cost Sheets
===========================

Project cost management with vendor privacy:
- Account Managers see: Role-based rates only
- Finance Directors see: Actual vendor costs + profits
- Automated rate calculation (P60 + 25% markup)
- Cost sheet templates with role matrices
- Real-time profit margin tracking
- Budget vs actual analysis
- Multi-currency support
- Export to Excel/PDF

Part of InsightPulse Enterprise SaaS Parity (Epic 2)
""",
    "author": "InsightPulse",
    "website": "https://insightpulse.ai",
    "license": "LGPL-3",
    "depends": [
        "ipai_core",
        "project",
        "hr",
        "analytic",
        "queue_job",
    ],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        "security/record_rules.xml",
        "views/cost_sheet_views.xml",
        "views/cost_sheet_line_views.xml",
        "views/rate_card_views.xml",
        "views/project_views.xml",
        "report/cost_sheet_report.xml",
        "data/templates.xml",
    ],
    "demo": [
        "demo/demo_data.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}

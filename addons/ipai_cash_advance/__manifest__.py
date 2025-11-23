```json
{
    "name": "IPAI Cash Advance & Liquidation",
    "summary": "Manage cash advances and liquidations (replacing legacy x_cash_advance)",
    "version": "18.0.1.0.0",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "category": "Finance",
    "depends": ["hr", "account"],
    "data": [
        "security/ir.model.access.csv",
        "views/cash_advance_views.xml",
        "views/menu.xml",
    ],
    "installable": True,
    "application": True,
}

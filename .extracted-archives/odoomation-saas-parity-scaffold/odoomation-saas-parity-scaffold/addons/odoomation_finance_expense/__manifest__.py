{
    "name": "Odoomation Finance Expense",
    "summary": "Atomic expense actions + secure API for SAP Concur–style parity",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "author": "InsightPulseAI",
    "depends": ["base", "hr_expense"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "data/ir_cron.xml"
    ],
    "application": true,
    "installable": true
}

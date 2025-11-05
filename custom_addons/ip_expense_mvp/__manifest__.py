# -*- coding: utf-8 -*-
{
    "name": "InsightPulse – Expense MVP (Mobile + Dashboard)",
    "version": "0.1.0",
    "summary": "Mobile receipt capture + OCR, cash advance/liquidation scaffolds, admin dashboard",
    "category": "Human Resources/Expenses",
    "author": "InsightPulseAI",
    "license": "LGPL-3",
    "depends": ["base", "web", "hr", "hr_expense"],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/expense_views.xml",
        "views/templates.xml",
        "views/admin_dashboard.xml"
    ],
    "application": True,
}

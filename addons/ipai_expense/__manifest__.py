# -*- coding: utf-8 -*-
{
    "name": "IPAI Expense & Travel (PH)",
    "summary": "PH-focused expense & travel workflows (SAP Concur-style) on Odoo CE + OCA.",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "hr",
        "hr_expense",
        "account",
        "project",
    ],
    "data": [
        "security/ipai_expense_security.xml",
        "security/ir.model.access.csv",
        "data/ipai_expense_categories.xml",
        "views/ipai_expense_menus.xml",
        "views/ipai_expense_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}

# -*- coding: utf-8 -*-
{
    "name": "IPAI T&E Seed",
    "version": "1.0.0",
    "summary": "IPAI seed: T&E accounts, journals, categories, MIS KPIs",
    "category": "Human Resources/Expenses",
    "author": "InsightPulseAI",
    "license": "LGPL-3",
    "depends": [
        "account",
        "hr_expense",
        "mis_builder",  # OCA MIS Builder for KPIs
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/account_journal.xml",
        "data/account_account.xml",
        "data/product_category.xml",
        "data/hr_expense_category.xml",
        "data/mis_report.xml",
    ],
    "demo": [
        "data/demo_companies.xml",
        "data/demo_expenses.xml",
    ],
    "application": False,
    "installable": True,
    "auto_install": False,
}

# -*- coding: utf-8 -*-
{
    "name": "IPAI Expense OCR (CE)",
    "summary": "Use InsightPulse OCR service for expense digitization (no Odoo Enterprise/IAP).",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Expenses",
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net",
    "license": "AGPL-3",
    "depends": [
        "hr_expense",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ipai_ocr_settings_views.xml",
        "views/ipai_ocr_expense_views.xml",
        "views/ocr_expense_log_views.xml",
    ],
    "installable": True,
    "application": False,
}

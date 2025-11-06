{
    'name': 'InsightPulse Expense MVP',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Expenses',
    'summary': 'Mobile receipt upload → AI OCR → Admin review workflow',
    'description': """
InsightPulse Expense MVP
========================
* Mobile endpoint: /ip/mobile/receipt (POST with multipart file)
* OCR via AI Inference Hub (PaddleOCR)
* Supabase analytics sink (idempotent upsert)
* Admin views for receipt review and expense creation
    """,
    'author': 'InsightPulse AI',
    'website': 'https://insightpulseai.net',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'hr_expense',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/ocr_receipt_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

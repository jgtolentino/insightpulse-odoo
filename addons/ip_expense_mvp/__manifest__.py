{
    'name': 'IP Expense MVP',
    'version': '0.1.0',
    'category': 'Accounting/Expenses',
    'summary': 'Mobile receipt upload → OCR → admin review',
    'depends': ['hr_expense', 'web'],
    'data': ['security/ir.model.access.csv', 'views/ocr_receipt_views.xml', 'views/settings.xml'],
    'installable': True,
    'license': 'AGPL-3',
}

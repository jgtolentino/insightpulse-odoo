{
    "name": "IPAI Expense",
    "version": "19.0.20251026.1",
    "category": "Accounting/Expenses",
    "summary": "Cash advance lifecycle, expense policy, OCR audit",
    "description": """
    OCR-powered expense automation with policy validation.

    Features:
    - Multi-provider OCR (PaddleOCR-VL, Azure, Google Vision)
    - Policy validation engine
    - Automated expense creation from receipts
    - Real-time WebSocket notifications
    - Batch processing with retry logic
    """,
    "author": "InsightPulseAI",
    "website": "https://insightpulseai.net/apps/ipai_expense",
    "license": "AGPL-3",
    "depends": [
        "base",
        "mail",
        "hr",
        "hr_expense",
        "account",
        "report_xlsx",
        "queue_job",
        "server_environment",
    ],
    "data": ["security/ir.model.access.csv", "data/sequence.xml"],
    "installable": True,
    "application": False,
    "auto_install": False,
}

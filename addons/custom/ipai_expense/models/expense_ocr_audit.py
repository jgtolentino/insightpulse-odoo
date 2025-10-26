from odoo import fields, models


class IpaiExpenseOcrAudit(models.Model):
    _name = "ipai.expense.ocr.audit"
    _description = "IPAI Expense OCR Audit"

    expense_id = fields.Many2one("hr.expense", ondelete="set null")
    attachment_id = fields.Many2one("ir.attachment", required=True)
    ocr_payload = fields.Json()
    confidence = fields.Float()

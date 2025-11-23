from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    ocr_status = fields.Selection(
        [
            ("none", "No OCR"),
            ("pending", "Pending OCR"),
            ("processed", "Processed"),
            ("error", "Error"),
        ],
        string="OCR Status",
        default="none",
        tracking=True,
    )
    ocr_payload = fields.Text(
        string="OCR Raw Payload",
        help="Raw JSON payload returned by the OCR service",
    )
    ocr_error_message = fields.Char(string="OCR Error Message")
    ocr_amount_detected = fields.Monetary(string="OCR Amount")
    ocr_date_detected = fields.Date(string="OCR Date")
    ocr_vendor_detected = fields.Char(string="OCR Vendor")

    def action_send_to_ocr(self):
        """Mark expense as pending for OCR and trigger external webhook (n8n / OCR API)."""
        for expense in self:
            expense.write({"ocr_status": "pending"})

            # Option 1: Call n8n/OCR directly from Odoo via HTTP (simple but tight coupling)
            # Option 2: Just set status, and let an external worker (n8n) poll pending expenses.
            # For now, we implement Option 2 (simpler & safer).
        return True

    @api.model
    def apply_ocr_result(self, expense_id, payload):
        """Entry point callable from n8n via XML-RPC/JSON-RPC or server action wrapper."""
        expense = self.browse(expense_id).exists()
        if not expense:
            return False

        # payload expected as dict
        vals = {
            "ocr_status": "processed",
            "ocr_payload": self.env["ir.config_parameter"].sudo().get_param(
                "ipai_ocr_expense.store_raw_payload", "1"
            ) == "1" and repr(payload) or False,
            "ocr_error_message": False,
        }

        amount = payload.get("amount")
        date = payload.get("date")
        vendor = payload.get("vendor")

        if amount:
            vals["ocr_amount_detected"] = amount
            # Only overwrite if amount not set
            if not expense.total_amount:
                vals["total_amount"] = amount

        if date:
            vals["ocr_date_detected"] = date
            if not expense.date:
                vals["date"] = date

        if vendor:
            vals["ocr_vendor_detected"] = vendor
            if not expense.name:
                vals["name"] = vendor

        expense.write(vals)
        return True

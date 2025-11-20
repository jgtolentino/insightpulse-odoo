# -*- coding: utf-8 -*-
import logging
import requests
import time

from odoo import api, fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class HrExpense(models.Model):
    _inherit = "hr.expense"

    ocr_status = fields.Selection(
        [
            ("none", "Not Scanned"),
            ("pending", "Pending"),
            ("done", "Scanned"),
            ("error", "Error"),
        ],
        string="OCR Status",
        default="none",
        readonly=True,
    )

    def action_ipai_ocr_scan(self):
        """Send the first attached receipt to InsightPulse OCR and fill fields."""
        params = self.env["ir.config_parameter"].sudo()
        enabled = params.get_param("ipai_ocr_expense.ipai_ocr_enabled", "False") == "True"
        api_url = params.get_param("ipai_ocr_expense.ipai_ocr_api_url")
        api_key = params.get_param("ipai_ocr_expense.ipai_ocr_api_key")

        if not enabled:
            raise UserError(_("InsightPulse OCR is not enabled in settings."))
        if not api_url:
            raise UserError(_("InsightPulse OCR API URL is not configured."))

        for expense in self:
            attachments = self.env["ir.attachment"].search(
                [
                    ("res_model", "=", "hr.expense"),
                    ("res_id", "=", expense.id),
                    ("mimetype", "like", "image%"),
                ],
                limit=1,
            )
            if not attachments:
                raise UserError(_("Please attach a receipt image before running OCR."))

            # Get employee_id for logging
            employee = expense.employee_id or self.env.user.employee_id

            # Create log entry (will be updated later)
            log_vals = {
                "expense_id": expense.id,
                "user_id": self.env.uid,
                "employee_id": employee.id if employee else False,
                "source": "web",
                "status": "failed",  # default to failed, update on success
            }
            log = self.env["ocr.expense.log"].sudo().create(log_vals)

            expense.write({"ocr_status": "pending"})

            # Track duration
            start_time = time.time()

            try:
                file_content = attachments._file_read(attachments.store_fname)
                files = {
                    "file": (attachments.name or "receipt.jpg", file_content, attachments.mimetype),
                }
                headers = {}
                if api_key:
                    headers["X-API-Key"] = api_key

                resp = requests.post(api_url, files=files, headers=headers, timeout=30)
                resp.raise_for_status()
                data = resp.json()

                # Calculate duration
                duration_ms = int((time.time() - start_time) * 1000)

                # Map OCR JSON → fields (adjust as your OCR JSON evolves)
                vals = {}
                if data.get("total_amount"):
                    vals["total_amount"] = data["total_amount"]
                    vals["unit_amount"] = data["total_amount"]  # simple case 1 line = total

                if data.get("merchant_name"):
                    vals["name"] = data["merchant_name"]

                if data.get("invoice_date"):
                    vals["date"] = data["invoice_date"]

                expense.write(vals)
                expense.write({"ocr_status": "done"})

                # Determine status based on field extraction
                has_all_fields = all([
                    data.get("merchant_name"),
                    data.get("invoice_date"),
                    data.get("total_amount"),
                ])
                status = "success" if has_all_fields else "partial"

                # Update log with success data
                log.write({
                    "status": status,
                    "duration_ms": duration_ms,
                    "vendor_name_extracted": data.get("merchant_name"),
                    "total_extracted": data.get("total_amount"),
                    "currency_extracted": data.get("currency"),
                    "date_extracted": data.get("invoice_date"),
                    "confidence": data.get("confidence", 0.0),
                })

                _logger.info(
                    "OCR success for expense %s: %s (%.2f %s) in %dms",
                    expense.id,
                    data.get("merchant_name"),
                    data.get("total_amount", 0.0),
                    data.get("currency", "PHP"),
                    duration_ms,
                )

            except Exception as e:
                # Calculate duration even on failure
                duration_ms = int((time.time() - start_time) * 1000)

                # Update log with error
                log.write({
                    "status": "failed",
                    "duration_ms": duration_ms,
                    "error_message": str(e),
                })

                _logger.exception("Error calling InsightPulse OCR: %s", e)
                expense.write({"ocr_status": "error"})
                raise UserError(_("OCR failed: %s") % str(e))

# -*- coding: utf-8 -*-
"""
OCR Expense Log - Track every OCR call for observability and quality measurement
"""
from odoo import api, fields, models


class OcrExpenseLog(models.Model):
    _name = "ocr.expense.log"
    _description = "OCR Expense Call Log"
    _order = "created_at desc"

    # Core identifiers
    expense_id = fields.Many2one(
        "hr.expense",
        string="Expense",
        ondelete="set null",
        help="Related expense record (if applicable)"
    )
    user_id = fields.Many2one(
        "res.users",
        string="User",
        default=lambda self: self.env.uid,
        required=True
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="Employee",
        help="Employee who initiated OCR scan"
    )

    # Request metadata
    created_at = fields.Datetime(
        string="Timestamp",
        default=fields.Datetime.now,
        required=True
    )
    source = fields.Selection(
        [
            ("web", "Web UI"),
            ("mobile", "Mobile App"),
            ("api", "API"),
        ],
        string="Source",
        default="web",
        required=True
    )
    duration_ms = fields.Integer(
        string="Duration (ms)",
        help="Time taken for OCR processing"
    )

    # OCR results
    status = fields.Selection(
        [
            ("success", "Success"),
            ("partial", "Partial Success"),
            ("failed", "Failed"),
        ],
        string="Status",
        required=True,
        default="success"
    )
    vendor_name_extracted = fields.Char(
        string="Vendor Name",
        help="Extracted merchant/vendor name"
    )
    total_extracted = fields.Float(
        string="Total Amount",
        help="Extracted total amount"
    )
    currency_extracted = fields.Char(
        string="Currency",
        help="Extracted currency code"
    )
    date_extracted = fields.Date(
        string="Date",
        help="Extracted invoice/receipt date"
    )
    confidence = fields.Float(
        string="Confidence Score",
        help="Overall confidence score (0.0-1.0)"
    )

    # Error handling
    error_message = fields.Text(
        string="Error Message",
        help="Error details if OCR failed"
    )

    # Raw data (optional, for debugging)
    raw_payload_path = fields.Char(
        string="Raw Payload Path",
        help="Path to stored raw OCR response (S3/storage)"
    )
    request_id = fields.Char(
        string="Request ID",
        help="Unique request identifier for tracing"
    )

    # Computed fields for analytics
    is_successful = fields.Boolean(
        string="Successful",
        compute="_compute_is_successful",
        store=True
    )

    @api.depends("status")
    def _compute_is_successful(self):
        for record in self:
            record.is_successful = record.status == "success"

    def name_get(self):
        """Custom display name"""
        result = []
        for record in self:
            name = f"OCR Log #{record.id}"
            if record.vendor_name_extracted:
                name += f" - {record.vendor_name_extracted}"
            if record.status:
                name += f" [{record.status}]"
            result.append((record.id, name))
        return result

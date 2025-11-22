# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ipai_ocr_enabled = fields.Boolean(string="Enable InsightPulse OCR")
    ipai_ocr_api_url = fields.Char(
        string="InsightPulse OCR API URL",
        help="Base URL for the OCR endpoint, e.g. https://ocr.insightpulseai.net/api/expense/ocr",
    )
    ipai_ocr_api_key = fields.Char(
        string="InsightPulse OCR API Key",
        help="API key sent as X-API-Key header to the OCR service.",
    )

    def set_values(self):
        super().set_values()
        params = self.env["ir.config_parameter"].sudo()
        params.set_param("ipai_ocr_expense.ipai_ocr_enabled", self.ipai_ocr_enabled)
        params.set_param("ipai_ocr_expense.ipai_ocr_api_url", self.ipai_ocr_api_url or "")
        # Store key in ir.config_parameter; you can encrypt separately if needed
        params.set_param("ipai_ocr_expense.ipai_ocr_api_key", self.ipai_ocr_api_key or "")

    @api.model
    def get_values(self):
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            ipai_ocr_enabled=params.get_param("ipai_ocr_expense.ipai_ocr_enabled", "False") == "True",
            ipai_ocr_api_url=params.get_param("ipai_ocr_expense.ipai_ocr_api_url", ""),
            ipai_ocr_api_key=params.get_param("ipai_ocr_expense.ipai_ocr_api_key", ""),
        )
        return res

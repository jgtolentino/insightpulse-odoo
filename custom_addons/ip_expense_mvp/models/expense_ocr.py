# -*- coding: utf-8 -*-
import base64
import json
import logging
import requests
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class HrExpense(models.Model):
    _inherit = "hr.expense"

    ocr_status = fields.Selection([
        ("new", "New"),
        ("queued", "Queued"),
        ("parsed", "Parsed"),
        ("error", "Error"),
    ], default="new", string="OCR Status", tracking=True)
    ocr_confidence = fields.Float("OCR Confidence")
    ocr_merchant = fields.Char("Merchant")
    ocr_date = fields.Date("Receipt Date")
    ocr_payload = fields.Json("OCR Payload")
    ocr_job_id = fields.Char("OCR Job ID")

    def action_run_ocr(self):
        """Manual OCR trigger on an expense with an image attachment."""
        ICP = self.env["ir.config_parameter"].sudo()
        base_url = ICP.get_param("ip_ai_inference_base_url", "")
        token = ICP.get_param("ip_ai_inference_token", "")
        if not base_url:
            raise ValueError("System Parameter 'ip_ai_inference_base_url' is not set")

        for rec in self:
            # Find first image attachment for the expense
            att = self.env["ir.attachment"].search([
                ("res_model", "=", rec._name),
                ("res_id", "=", rec.id),
                ("mimetype", "ilike", "image/%")
            ], limit=1)
            if not att:
                raise ValueError("Attach a receipt image first before OCR.")

            headers = {"Authorization": f"Bearer {token}"} if token else {}
            files = {"file": base64.b64decode(att.datas or b"")}
            url = f"{base_url.rstrip('/')}/v1/ocr/receipt-parse"

            rec.write({"ocr_status": "queued"})
            try:
                resp = requests.post(url, headers=headers, files=files, timeout=60)
                resp.raise_for_status()
                payload = resp.json()
                rec._apply_ocr_payload(payload)
            except Exception as e:
                _logger.exception("OCR error")
                rec.write({"ocr_status": "error"})
                raise

    def _apply_ocr_payload(self, payload: dict):
        """Map OCR JSON → expense fields."""
        vals = {"ocr_status": "parsed", "ocr_payload": payload}
        # tolerant key lookups from sample schema provided
        def gv(path, default=None):
            cur = payload
            for k in path.split("."):
                if isinstance(cur, dict) and k in cur:
                    cur = cur[k]
                else:
                    return default
            return cur
        merchant = gv("merchant_name.value") or gv("merchant_name")
        total = gv("total_amount.value") or gv("total_amount")
        conf = gv("total_amount.confidence") or gv("confidence") or 0.0
        rdate = gv("date.value") or gv("date")

        if merchant: vals["ocr_merchant"] = merchant
        if conf is not None: vals["ocr_confidence"] = conf
        if rdate: vals["ocr_date"] = rdate
        if total:
            try:
                vals["total_amount"] = float(total)
                vals["unit_amount"] = float(total)
            except Exception:
                pass
        # Fill name if empty
        for rec in self:
            if not rec.name and merchant:
                vals["name"] = f"Receipt - {merchant}"
            rec.write(vals)

from odoo import models, fields, api
import json, hashlib, requests

def _get_cfg(env, key, default=None):
    return env["ir.config_parameter"].sudo().get_param(key, default)

class IpOcrReceipt(models.Model):
    _name = "ip.ocr.receipt"
    _description = "OCR Receipts"

    name = fields.Char(required=True)
    uploader_id = fields.Many2one("res.users", string="Uploaded By", readonly=True, default=lambda self: self.env.user)
    ocr_json = fields.Text(string="OCR Result (JSON)")
    line_count = fields.Integer(compute="_compute_line_count", store=False)
    expense_id = fields.Many2one("hr.expense", string="Linked Expense")

    @api.depends("ocr_json")
    def _compute_line_count(self):
        for rec in self:
            try:
                data = json.loads(rec.ocr_json or "{}")
                rec.line_count = len(data.get("lines", []))
            except Exception:
                rec.line_count = 0

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        # fire-and-forget sync; do not block UI
        try:
            rec._sync_to_supabase()
        except Exception as e:
            self.env["ir.logging"].sudo().create({
                "name": "ip_expense_mvp",
                "type": "server",
                "dbname": self._cr.dbname,
                "level": "WARNING",
                "message": f"Supabase sync failed: {e}",
                "path": __name__,
                "line": "create",
                "func": "_sync_to_supabase",
            })
        return rec

    def _sync_to_supabase(self):
        self.ensure_one()
        supa_url = _get_cfg(self.env, "ip.supabase_url")
        supa_key = _get_cfg(self.env, "ip.supabase_service_key")
        if not supa_url or not supa_key:
            return  # not configured yet

        payload = json.loads(self.ocr_json or "{}")
        # extract common fields when available; tolerate missing keys
        def gx(path, default=None):
            try:
                cur = payload
                for p in path:
                    cur = cur[p]
                return cur
            except Exception:
                return default

        total_amount = gx(["totals","total_amount","value"]) or gx(["total_amount","value"])
        vat_amount   = gx(["totals","vat_amount","value"])   or gx(["vat_amount","value"])
        bir_atp      = gx(["bir_atp","value"])
        tin          = gx(["tin","value"])
        receipt_date = gx(["date","value"])
        line_count   = len(payload.get("lines", [])) if isinstance(payload.get("lines"), list) else self.line_count or 0

        # dedupe key = hash(filename + first 100 bytes of json)
        raw = (self.name or "") + (self.ocr_json or "")[:100]
        dedupe_key = hashlib.sha1(raw.encode("utf-8")).hexdigest()

        rpc = f"{supa_url}/rest/v1/rpc/upsert_ip_ocr_receipt"
        headers = {
            "apikey": supa_key,
            "Authorization": f"Bearer {supa_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        body = {
            "p_filename": self.name,
            "p_uploaded_by": self.uploader_id.login if self.uploader_id else None,
            "p_line_count": line_count,
            "p_receipt_date": receipt_date,
            "p_total_amount": total_amount,
            "p_vat_amount": vat_amount,
            "p_bir_atp": bir_atp,
            "p_tin": tin,
            "p_payload": payload,
            "p_dedupe_key": dedupe_key
        }
        r = requests.post(rpc, headers=headers, data=json.dumps(body), timeout=20)
        r.raise_for_status()

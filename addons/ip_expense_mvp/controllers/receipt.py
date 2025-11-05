from odoo import http
from odoo.http import request
import requests

def _cfg(key, default=None):
    return request.env["ir.config_parameter"].sudo().get_param(key, default)

class IpReceiptController(http.Controller):
    @http.route("/ip/mobile/receipt", type="http", auth="user", methods=["POST"], csrf=False)
    def upload_receipt(self, **kw):
        f = request.httprequest.files.get("file")
        if not f:
            return request.make_response("No file provided", headers=[("Status","400 Bad Request")])

        ai_url = _cfg("ip.ai_ocr_url", "http://127.0.0.1:8100/v1/ocr/receipt")
        try:
            r = requests.post(ai_url, files={"file": (f.filename, f.stream, f.mimetype)}, timeout=60)
            r.raise_for_status()
        except Exception as e:
            return request.make_response(f"OCR error: {e}", headers=[("Status","502 Bad Gateway")])

        rec = request.env["ip.ocr.receipt"].sudo().create({
            "name": f.filename,
            "uploader_id": request.env.user.id,
            "ocr_json": r.text,
        })
        return request.redirect(f"/web#id={rec.id}&model=ip.ocr.receipt&view_type=form")

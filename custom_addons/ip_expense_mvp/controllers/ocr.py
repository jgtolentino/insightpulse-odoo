# -*- coding: utf-8 -*-
import base64

import werkzeug
from odoo.http import request

from odoo import http

MOBILE_TMPL = "ip_expense_mvp.mobile_receipt_form"


class IpExpenseController(http.Controller):

    @http.route(
        "/ip/mobile/receipt",
        type="http",
        auth="user",
        website=True,
        methods=["GET", "POST"],
    )
    def mobile_receipt(self, **kw):
        if request.httprequest.method == "GET":
            return request.render(MOBILE_TMPL, {})
        # POST
        file = kw.get("receipt")
        amount = kw.get("amount")
        if not file:
            return werkzeug.utils.redirect("/ip/mobile/receipt")
        # create expense
        exp = (
            request.env["hr.expense"]
            .sudo()
            .create(
                {
                    "name": kw.get("title") or "Mobile Receipt",
                    "employee_id": request.env.user.employee_id.id or False,
                    "unit_amount": float(amount) if amount else 0.0,
                }
            )
        )
        # attach the image
        request.env["ir.attachment"].sudo().create(
            {
                "name": file.filename,
                "res_model": "hr.expense",
                "res_id": exp.id,
                "type": "binary",
                "datas": base64.b64encode(file.read()),
                "mimetype": file.content_type or "image/jpeg",
            }
        )
        # try OCR immediately (best-effort)
        try:
            exp.action_run_ocr()
        except Exception:
            pass
        return werkzeug.utils.redirect(
            f"/web#id={exp.id}&model=hr.expense&view_type=form"
        )

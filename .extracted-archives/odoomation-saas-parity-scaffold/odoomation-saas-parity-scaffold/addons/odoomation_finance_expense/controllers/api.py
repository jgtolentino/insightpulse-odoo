from odoo import http
from odoo.http import request

class ExpenseApiController(http.Controller):

    @http.route('/odoomation/expense/stage', type='json', auth='user', methods=['POST'])
    def stage(self, **payload):
        rec = request.env['odoomation.expense.atomic'].sudo().atomic_stage_receipt(payload)
        return {"ok": True, "record": rec}

    @http.route('/odoomation/expense/post', type='json', auth='user', methods=['POST'])
    def post(self, **payload):
        rid = int(payload.get('id', 0))
        rec = request.env['odoomation.expense.atomic'].sudo().browse(rid)
        if not rec.exists():
            return {"ok": False, "error": "not_found"}
        rec.action_post()
        return {"ok": True, "state": rec.state}

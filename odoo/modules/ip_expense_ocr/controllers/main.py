from odoo import http
from odoo.http import request

class ExpenseOCR(http.Controller):
    @http.route('/ip/expense/intake', type='json', auth='user', csrf=False, methods=['POST'])
    def intake(self, **payload):
        user = request.env.user
        emp = user.employee_id
        if not emp:
            return {'ok': False, 'error': 'Employee not linked'}
        idem = (payload or {}).get('idempotency_key')
        if idem and request.env['hr.expense'].sudo().search([('x_idempotency_key', '=', idem)], limit=1):
            return {'ok': True, 'idempotent': True}
        vals = {
            'name': payload.get('merchant') or 'Receipt',
            'employee_id': emp.id,
            'total_amount': payload.get('total') or 0.0,
            'x_idempotency_key': idem,
            'x_merchant': payload.get('merchant'),
            'x_category': payload.get('category'),
            'x_ocr_confidence': payload.get('conf'),
        }
        exp = request.env['hr.expense'].sudo().create(vals)
        request.env['bus.bus']._sendone(user.partner_id, 'ip.expense.new', exp.id)
        return {'ok': True, 'expense_id': exp.id}

from odoo import api, fields, models

class ExpenseAtomic(models.Model):
    _name = "odoomation.expense.atomic"
    _description = "Atomic operations for expense parity"

    name = fields.Char(required=True)
    employee_id = fields.Many2one('hr.employee')
    amount = fields.Float(required=True)
    currency_id = fields.Many2one('res.currency', required=True, default=lambda s: s.env.company.currency_id.id)
    state = fields.Selection([('draft','Draft'),('staged','Staged'),('posted','Posted')], default='draft')

    @api.model
    def atomic_stage_receipt(self, vals):
        required = {'name','amount','currency_id'}
        if not required.issubset(vals.keys()):
            missing = required - set(vals.keys())
            raise ValueError("Missing fields: %s" % ", ".join(sorted(missing)))
        rec = self.create({
            'name': vals['name'],
            'amount': float(vals['amount']),
            'currency_id': int(vals['currency_id']),
            'employee_id': vals.get('employee_id'),
            'state': 'staged',
        })
        return {'id': rec.id, 'state': rec.state}

    def action_post(self):
        for rec in self:
            rec.state = 'posted'
        return True

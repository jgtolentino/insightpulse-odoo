"""OCR Receipt model for mobile receipt uploads."""
import json
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class IpOcrReceipt(models.Model):
    """OCR Receipt - stores uploaded receipts with OCR results."""

    _name = "ip.ocr.receipt"
    _description = "OCR Receipt"
    _order = "create_date desc"
    _rec_name = "name"

    name = fields.Char(string="Receipt Name", required=True, index=True)
    filename = fields.Char(string="Filename", readonly=True)
    uploaded_by = fields.Many2one('res.users', string="Uploaded By",
                                   default=lambda self: self.env.user,
                                   readonly=True, index=True)
    upload_date = fields.Datetime(string="Upload Date",
                                   default=fields.Datetime.now,
                                   readonly=True)

    # OCR Results
    ocr_json = fields.Text(string="OCR JSON", readonly=True)
    line_count = fields.Integer(string="Lines Detected", readonly=True, default=0)
    avg_confidence = fields.Float(string="Avg Confidence %", readonly=True, digits=(5, 2))

    # Optional parsed fields
    total_amount = fields.Monetary(string="Total Amount", currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string="Currency",
                                   default=lambda self: self.env.company.currency_id)

    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('processed', 'Processed'),
        ('expense_created', 'Expense Created'),
    ], string="Status", default='draft', index=True)

    expense_id = fields.Many2one('hr.expense', string="Linked Expense", readonly=True)

    # Computed
    ocr_text = fields.Text(string="Extracted Text", compute="_compute_ocr_text", store=False)

    @api.depends('ocr_json')
    def _compute_ocr_text(self):
        """Extract all text lines from OCR JSON for quick preview."""
        for rec in self:
            if not rec.ocr_json:
                rec.ocr_text = ""
                continue
            try:
                data = json.loads(rec.ocr_json)
                lines = data.get('lines', [])
                rec.ocr_text = "\n".join([line.get('text', '') for line in lines])
            except (json.JSONDecodeError, TypeError, AttributeError) as e:
                _logger.warning("Failed to parse OCR JSON for receipt %s: %s", rec.id, e)
                rec.ocr_text = ""

    def action_create_expense(self):
        """Create hr.expense from OCR receipt."""
        self.ensure_one()

        # Parse amount from OCR JSON
        amount = self._parse_amount_from_json() or 0.0

        # Get employee (current user's employee record)
        employee = self.env.user.employee_id
        if not employee:
            # Try to find or create employee for current user
            employee = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)

        # Create expense
        expense_vals = {
            'name': f"Receipt: {self.name}",
            'unit_amount': amount,
            'quantity': 1.0,
            'currency_id': self.currency_id.id,
            'date': fields.Date.context_today(self),
            'employee_id': employee.id if employee else False,
            'payment_mode': 'company_account',
        }

        expense = self.env['hr.expense'].create(expense_vals)

        # Update receipt status
        self.write({
            'state': 'expense_created',
            'expense_id': expense.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': 'Expense',
            'res_model': 'hr.expense',
            'view_mode': 'form',
            'res_id': expense.id,
            'target': 'current',
        }

    def _parse_amount_from_json(self):
        """Extract total_amount from OCR JSON."""
        if not self.ocr_json:
            return 0.0
        try:
            data = json.loads(self.ocr_json)
            # Try to get total_amount from root or lines
            total = data.get('total_amount')
            if total:
                return float(total)

            # Fallback: look for "TOTAL" in lines and parse
            lines = data.get('lines', [])
            for line in lines:
                text = line.get('text', '').upper()
                if 'TOTAL' in text:
                    # Simple regex to extract number
                    import re
                    numbers = re.findall(r'\d+\.?\d*', text)
                    if numbers:
                        return float(numbers[-1])

            return 0.0
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            _logger.warning("Failed to parse amount from OCR JSON: %s", e)
            return 0.0

    def action_view_expense(self):
        """Open linked expense."""
        self.ensure_one()
        if not self.expense_id:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expense',
            'res_model': 'hr.expense',
            'view_mode': 'form',
            'res_id': self.expense_id.id,
            'target': 'current',
        }

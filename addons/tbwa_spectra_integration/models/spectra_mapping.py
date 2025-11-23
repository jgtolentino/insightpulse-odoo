# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SpectraMapping(models.Model):
    """
    Master mapping table for Odoo → Spectra field transformations.

    Supports:
    - GL account mapping
    - Cost center/project code mapping
    - Employee code mapping
    - Category/expense type mapping
    """
    _name = 'tbwa.spectra.mapping'
    _description = 'Spectra Field Mapping Configuration'
    _order = 'sequence, id'

    name = fields.Char(string='Mapping Name', required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Mapping type
    mapping_type = fields.Selection([
        ('gl_account', 'GL Account'),
        ('cost_center', 'Cost Center / Project'),
        ('employee', 'Employee Code'),
        ('category', 'Expense Category'),
        ('vendor', 'Vendor/Supplier'),
        ('tax', 'Tax Code'),
    ], string='Mapping Type', required=True)

    # Odoo source
    odoo_field = fields.Char(string='Odoo Field', required=True,
                             help='Source field from Odoo (e.g., account_id.code)')
    odoo_value = fields.Char(string='Odoo Value',
                             help='Specific value to match (leave empty for all)')

    # Spectra target
    spectra_field = fields.Char(string='Spectra Field', required=True,
                                help='Target column in Spectra export')
    spectra_value = fields.Char(string='Spectra Value', required=True,
                                help='Transformed value for Spectra')
    spectra_format = fields.Selection([
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date (YYYY-MM-DD)'),
        ('datetime', 'DateTime (ISO)'),
        ('currency', 'Currency (2 decimals)'),
    ], default='text', string='Format')

    # Validation rules
    is_required = fields.Boolean(string='Required in Spectra', default=False)
    validation_rule = fields.Char(string='Validation Rule',
                                  help='Python expression for validation (e.g., len(value) == 10)')

    # Metadata
    notes = fields.Text(string='Notes')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company)

    @api.constrains('validation_rule')
    def _check_validation_rule(self):
        """Validate the validation rule is safe Python."""
        for record in self:
            if record.validation_rule:
                try:
                    compile(record.validation_rule, '<string>', 'eval')
                except SyntaxError as e:
                    raise ValidationError(_('Invalid validation rule: %s') % str(e))

    def apply_mapping(self, odoo_record, field_name):
        """
        Apply mapping transformation to an Odoo record field.

        Args:
            odoo_record: Odoo record (e.g., hr.expense.sheet)
            field_name: Field to map (e.g., 'employee_id')

        Returns:
            str: Mapped Spectra value
        """
        self.ensure_one()

        # Get source value
        field_path = self.odoo_field.split('.')
        value = odoo_record
        for part in field_path:
            value = getattr(value, part, None)
            if value is None:
                break

        # Apply transformation based on mapping type
        if self.mapping_type == 'employee':
            # Employee code mapping (e.g., 'John Doe' → 'JDOE')
            if hasattr(value, 'employee_code'):
                mapped_value = value.employee_code
            elif hasattr(value, 'login'):
                # Fallback to login username
                mapped_value = value.login.split('@')[0].upper()
            else:
                mapped_value = str(value.id).zfill(6)  # Fallback to ID

        elif self.mapping_type == 'gl_account':
            # GL account mapping
            mapped_value = self.spectra_value

        elif self.mapping_type == 'cost_center':
            # Project/cost center mapping
            if hasattr(value, 'code'):
                mapped_value = value.code
            else:
                mapped_value = self.spectra_value

        elif self.mapping_type == 'category':
            # Expense category mapping
            mapped_value = self.spectra_value

        else:
            # Default: use spectra_value directly
            mapped_value = self.spectra_value

        # Apply format
        if self.spectra_format == 'currency':
            try:
                mapped_value = "{:.2f}".format(float(mapped_value))
            except (ValueError, TypeError):
                mapped_value = "0.00"
        elif self.spectra_format == 'number':
            try:
                mapped_value = str(int(float(mapped_value)))
            except (ValueError, TypeError):
                mapped_value = "0"
        elif self.spectra_format == 'date':
            if isinstance(mapped_value, (fields.Date, fields.Datetime)):
                mapped_value = fields.Date.to_string(mapped_value)

        # Validate
        if self.is_required and not mapped_value:
            raise UserError(_('Required Spectra field %s is empty') % self.spectra_field)

        if self.validation_rule:
            try:
                # Safe eval with limited scope
                safe_dict = {'value': mapped_value, 'len': len, 'str': str, 'int': int}
                if not eval(self.validation_rule, {"__builtins__": {}}, safe_dict):
                    raise ValidationError(
                        _('Validation failed for %s: %s') % (self.spectra_field, mapped_value)
                    )
            except Exception as e:
                _logger.error(f"Validation error: {e}")
                raise ValidationError(_('Validation error: %s') % str(e))

        return mapped_value

    @api.model
    def get_mapping_for_export(self, export_type):
        """
        Get all active mappings for a specific export type.

        Args:
            export_type: Type of export (expense, cash_advance, journal_entry, etc.)

        Returns:
            recordset: Filtered mappings
        """
        domain = [('active', '=', True)]

        # Filter by export context
        if export_type == 'expense':
            domain.append(('mapping_type', 'in', ['employee', 'category', 'cost_center', 'gl_account']))
        elif export_type == 'cash_advance':
            domain.append(('mapping_type', 'in', ['employee', 'cost_center', 'gl_account']))
        elif export_type == 'journal_entry':
            domain.append(('mapping_type', 'in', ['gl_account', 'cost_center', 'vendor', 'tax']))

        return self.search(domain, order='sequence')


class SpectraGLCodeMapping(models.Model):
    """
    Specific GL code mapping for expense categories.
    Pre-configured based on TBWA Chart of Accounts.
    """
    _name = 'tbwa.spectra.gl.code'
    _description = 'Spectra GL Code Mapping'
    _order = 'sequence, expense_category'

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    expense_category = fields.Char(string='Expense Category', required=True,
                                   help='Odoo expense category name')
    expense_type = fields.Selection([
        ('travel', 'Travel'),
        ('meals', 'Meals & Entertainment'),
        ('supplies', 'Office Supplies'),
        ('utilities', 'Utilities'),
        ('professional', 'Professional Services'),
        ('other', 'Other'),
    ], string='Expense Type', required=True)

    # Spectra GL codes
    gl_account = fields.Char(string='GL Account', required=True,
                            help='Spectra GL account code (e.g., 6210-001)')
    sub_account = fields.Char(string='Sub Account',
                             help='Spectra sub-account if applicable')
    cost_center = fields.Char(string='Default Cost Center',
                             help='Default cost center if not specified')

    # Tax handling
    vat_applicable = fields.Boolean(string='VAT Applicable', default=True)
    vat_rate = fields.Float(string='VAT Rate %', default=12.0,
                           help='Philippine VAT rate (default 12%)')
    withholding_tax = fields.Float(string='Withholding Tax %', default=0.0)

    # Validation
    requires_receipt = fields.Boolean(string='Receipt Required', default=True)
    requires_approval = fields.Boolean(string='Requires Approval', default=True)
    max_amount = fields.Float(string='Max Amount (Single Transaction)',
                             help='Maximum allowed for single transaction')

    notes = fields.Text(string='Notes')

    _sql_constraints = [
        ('unique_category', 'UNIQUE(expense_category)',
         'Each expense category can only have one GL code mapping!')
    ]

    def get_gl_entry(self, expense_line):
        """
        Generate GL entry dictionary for a given expense line.

        Args:
            expense_line: hr.expense record

        Returns:
            dict: GL entry data for Spectra
        """
        self.ensure_one()

        # Calculate amounts
        net_amount = expense_line.total_amount
        vat_amount = 0.0
        if self.vat_applicable:
            vat_amount = net_amount * (self.vat_rate / 100)

        withholding_amount = 0.0
        if self.withholding_tax > 0:
            withholding_amount = net_amount * (self.withholding_tax / 100)

        gross_amount = net_amount + vat_amount - withholding_amount

        return {
            'gl_account': self.gl_account,
            'sub_account': self.sub_account or '',
            'cost_center': expense_line.analytic_account_id.code or self.cost_center or '',
            'net_amount': net_amount,
            'vat_amount': vat_amount,
            'withholding_amount': withholding_amount,
            'gross_amount': gross_amount,
            'description': expense_line.name,
            'reference': expense_line.reference or '',
        }

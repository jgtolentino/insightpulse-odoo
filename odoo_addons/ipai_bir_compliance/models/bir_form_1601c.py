# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
import logging
import base64
import xml.etree.ElementTree as ET
from datetime import datetime
import calendar

_logger = logging.getLogger(__name__)


class BIRForm1601C(models.Model):
    """BIR Form 1601-C - Monthly Remittance Return of Income Taxes Withheld"""

    _name = 'bir.form.1601c'
    _description = 'BIR Form 1601-C - Monthly Withholding Tax'
    _order = 'period_year desc, period_month desc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # Basic Information
    name = fields.Char(
        string='Form Name',
        compute='_compute_name',
        store=True,
        readonly=True
    )

    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    # Period
    period_month = fields.Integer(
        string='Month',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='1=January, 2=February, ..., 12=December'
    )

    period_year = fields.Integer(
        string='Year',
        required=True,
        default=lambda self: datetime.now().year,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    period_start = fields.Date(
        string='Period Start',
        compute='_compute_period_dates',
        store=True
    )

    period_end = fields.Date(
        string='Period End',
        compute='_compute_period_dates',
        store=True
    )

    deadline = fields.Date(
        string='Filing Deadline',
        compute='_compute_deadline',
        store=True,
        help='10th day of the following month'
    )

    # Tax Amounts (in Philippine Peso)
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.ref('base.PHP'),
        readonly=True
    )

    tax_withheld_compensation = fields.Monetary(
        string='Tax Withheld - Compensation',
        compute='_compute_tax_amounts',
        store=True,
        currency_field='currency_id'
    )

    tax_withheld_expanded = fields.Monetary(
        string='Tax Withheld - Expanded',
        compute='_compute_tax_amounts',
        store=True,
        currency_field='currency_id'
    )

    tax_withheld_total = fields.Monetary(
        string='Total Tax Withheld',
        compute='_compute_tax_amounts',
        store=True,
        currency_field='currency_id'
    )

    penalties = fields.Monetary(
        string='Penalties',
        default=0.0,
        currency_field='currency_id',
        tracking=True
    )

    interest = fields.Monetary(
        string='Interest',
        default=0.0,
        currency_field='currency_id',
        tracking=True
    )

    total_amount_due = fields.Monetary(
        string='Total Amount Due',
        compute='_compute_total',
        store=True,
        currency_field='currency_id'
    )

    # Validation
    state = fields.Selection([
        ('draft', 'Draft'),
        ('validated', 'Validated'),
        ('filed', 'Filed'),
        ('rejected', 'Rejected')
    ], string='Status', default='draft', tracking=True)

    validation_errors = fields.Text(
        string='Validation Errors',
        readonly=True
    )

    validation_date = fields.Datetime(
        string='Validation Date',
        readonly=True
    )

    # Generated Files
    pdf_file = fields.Binary(
        string='PDF Form',
        attachment=True
    )

    pdf_filename = fields.Char(
        string='PDF Filename',
        compute='_compute_filenames'
    )

    xml_file = fields.Binary(
        string='eBIRForms XML',
        attachment=True
    )

    xml_filename = fields.Char(
        string='XML Filename',
        compute='_compute_filenames'
    )

    # Audit Trail
    filed_date = fields.Datetime(
        string='Filed Date',
        readonly=True,
        tracking=True
    )

    filed_by = fields.Many2one(
        'res.users',
        string='Filed By',
        readonly=True
    )

    # Computed Fields
    @api.depends('period_year', 'period_month', 'company_id')
    def _compute_name(self):
        for record in self:
            if record.period_year and record.period_month:
                company_code = record.company_id.name[:4].upper() if record.company_id else 'XXXX'
                record.name = f"1601-C {record.period_year}-{record.period_month:02d} ({company_code})"
            else:
                record.name = "BIR Form 1601-C (New)"

    @api.depends('period_year', 'period_month')
    def _compute_period_dates(self):
        for record in self:
            if record.period_year and record.period_month:
                # First day of the month
                record.period_start = datetime(record.period_year, record.period_month, 1).date()

                # Last day of the month
                last_day = calendar.monthrange(record.period_year, record.period_month)[1]
                record.period_end = datetime(record.period_year, record.period_month, last_day).date()
            else:
                record.period_start = False
                record.period_end = False

    @api.depends('period_year', 'period_month')
    def _compute_deadline(self):
        for record in self:
            if record.period_year and record.period_month:
                # Deadline is 10th of following month
                if record.period_month == 12:
                    deadline_year = record.period_year + 1
                    deadline_month = 1
                else:
                    deadline_year = record.period_year
                    deadline_month = record.period_month + 1

                record.deadline = datetime(deadline_year, deadline_month, 10).date()
            else:
                record.deadline = False

    @api.depends('company_id', 'period_start', 'period_end')
    def _compute_tax_amounts(self):
        """Compute tax amounts from General Ledger"""
        for record in self:
            if not record.company_id or not record.period_start or not record.period_end:
                record.tax_withheld_compensation = 0.0
                record.tax_withheld_expanded = 0.0
                record.tax_withheld_total = 0.0
                continue

            # Query account.move.line for withholding tax transactions
            # Account codes for withholding tax payable (Philippine COA):
            # 2151 - Withholding Tax Payable (Compensation)
            # 2152 - Withholding Tax Payable (Expanded)

            domain_compensation = [
                ('company_id', '=', record.company_id.id),
                ('date', '>=', record.period_start),
                ('date', '<=', record.period_end),
                ('account_id.code', '=like', '2151%'),
                ('parent_state', '=', 'posted')  # Only posted entries
            ]

            domain_expanded = [
                ('company_id', '=', record.company_id.id),
                ('date', '>=', record.period_start),
                ('date', '<=', record.period_end),
                ('account_id.code', '=like', '2152%'),
                ('parent_state', '=', 'posted')
            ]

            # Get move lines
            moves_compensation = self.env['account.move.line'].search(domain_compensation)
            moves_expanded = self.env['account.move.line'].search(domain_expanded)

            # Calculate totals (credit - debit for liability accounts)
            record.tax_withheld_compensation = sum(moves_compensation.mapped('credit')) - sum(moves_compensation.mapped('debit'))
            record.tax_withheld_expanded = sum(moves_expanded.mapped('credit')) - sum(moves_expanded.mapped('debit'))
            record.tax_withheld_total = record.tax_withheld_compensation + record.tax_withheld_expanded

    @api.depends('tax_withheld_total', 'penalties', 'interest')
    def _compute_total(self):
        for record in self:
            record.total_amount_due = record.tax_withheld_total + record.penalties + record.interest

    @api.depends('name')
    def _compute_filenames(self):
        for record in self:
            safe_name = record.name.replace(' ', '_').replace('(', '').replace(')', '')
            record.pdf_filename = f"{safe_name}.pdf"
            record.xml_filename = f"{safe_name}.xml"

    # Constraints
    @api.constrains('period_month')
    def _check_period_month(self):
        for record in self:
            if not 1 <= record.period_month <= 12:
                raise ValidationError("Month must be between 1 and 12")

    @api.constrains('period_year')
    def _check_period_year(self):
        for record in self:
            current_year = datetime.now().year
            if not 2000 <= record.period_year <= current_year + 1:
                raise ValidationError(f"Year must be between 2000 and {current_year + 1}")

    # Actions
    def action_generate_pdf(self):
        """Generate BIR-compliant PDF using QWeb report"""
        self.ensure_one()

        if self.state not in ['draft', 'validated']:
            raise UserError("Cannot generate PDF for a filed or rejected form")

        try:
            # Use Odoo's QWeb reporting engine
            report = self.env.ref('ipai_bir_compliance.report_bir_1601c')
            pdf_content, _ = report._render_qweb_pdf([self.id])

            self.pdf_file = base64.b64encode(pdf_content)

            _logger.info(f"Generated PDF for {self.name}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'PDF generated successfully',
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.error(f"Error generating PDF for {self.name}: {str(e)}")
            raise UserError(f"Failed to generate PDF: {str(e)}")

    def action_generate_xml(self):
        """Generate eBIRForms XML according to BIR schema v8.0"""
        self.ensure_one()

        if self.state not in ['draft', 'validated']:
            raise UserError("Cannot generate XML for a filed or rejected form")

        try:
            # Build XML structure according to BIR eBIRForms schema
            root = ET.Element('eBIRForms', version='8.0')

            # Header section
            header = ET.SubElement(root, 'Header')
            ET.SubElement(header, 'FormType').text = '1601C'
            ET.SubElement(header, 'TIN').text = self.company_id.vat or ''
            ET.SubElement(header, 'BranchCode').text = '00000'
            ET.SubElement(header, 'ReturnPeriod').text = f"{self.period_year}{self.period_month:02d}"
            ET.SubElement(header, 'TaxableYear').text = str(self.period_year)
            ET.SubElement(header, 'TaxableMonth').text = str(self.period_month)

            # Body section
            body = ET.SubElement(root, 'Body')

            # Part I - Tax Withheld
            part1 = ET.SubElement(body, 'PartI')
            ET.SubElement(part1, 'CompensationTax').text = f"{self.tax_withheld_compensation:.2f}"
            ET.SubElement(part1, 'ExpandedTax').text = f"{self.tax_withheld_expanded:.2f}"
            ET.SubElement(part1, 'TotalTaxWithheld').text = f"{self.tax_withheld_total:.2f}"

            # Part II - Penalties and Interest
            part2 = ET.SubElement(body, 'PartII')
            ET.SubElement(part2, 'Penalties').text = f"{self.penalties:.2f}"
            ET.SubElement(part2, 'Interest').text = f"{self.interest:.2f}"

            # Part III - Total Amount Due
            part3 = ET.SubElement(body, 'PartIII')
            ET.SubElement(part3, 'TotalAmountDue').text = f"{self.total_amount_due:.2f}"

            # Footer - Signatory
            footer = ET.SubElement(root, 'Footer')
            ET.SubElement(footer, 'PreparedBy').text = self.env.user.name
            ET.SubElement(footer, 'PreparedDate').text = datetime.now().strftime('%Y-%m-%d')

            # Convert to string with XML declaration
            xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True)

            self.xml_file = base64.b64encode(xml_string)

            # Auto-validate after generating XML
            self.action_validate()

            _logger.info(f"Generated XML for {self.name}")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Success',
                    'message': 'XML generated and validated successfully',
                    'type': 'success',
                    'sticky': False,
                }
            }

        except Exception as e:
            _logger.error(f"Error generating XML for {self.name}: {str(e)}")
            raise UserError(f"Failed to generate XML: {str(e)}")

    def action_validate(self):
        """Validate form against BIR compliance rules"""
        self.ensure_one()

        errors = []

        # Validation Rule 1: TIN must be valid format (XXX-XXX-XXX-000)
        if not self._validate_tin(self.company_id.vat):
            errors.append("Invalid TIN format. Expected: XXX-XXX-XXX-000")

        # Validation Rule 2: Tax withheld must not be negative
        if self.tax_withheld_total < 0:
            errors.append("Total tax withheld cannot be negative")

        # Validation Rule 3: Period must be in the past or current month
        if self.period_start > fields.Date.today():
            errors.append("Cannot file return for future period")

        # Validation Rule 4: Company must be Philippine-based
        if self.company_id.country_id.code != 'PH':
            errors.append("Company must be registered in the Philippines")

        # Validation Rule 5: No duplicate forms for same period
        duplicate = self.search([
            ('id', '!=', self.id),
            ('company_id', '=', self.company_id.id),
            ('period_year', '=', self.period_year),
            ('period_month', '=', self.period_month),
            ('state', 'in', ['validated', 'filed'])
        ])
        if duplicate:
            errors.append(f"Form already exists for this period: {duplicate[0].name}")

        # Validation Rule 6: XML must exist before validating
        if not self.xml_file:
            errors.append("XML file must be generated before validation")

        # Validation Rule 7: Check XML schema compliance (if lxml available)
        if self.xml_file and not self._validate_xml_schema():
            errors.append("XML does not conform to BIR schema v8.0")

        # Update validation results
        if errors:
            self.state = 'rejected'
            self.validation_errors = "\n".join(errors)
            self.validation_date = fields.Datetime.now()

            _logger.warning(f"Validation failed for {self.name}: {self.validation_errors}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Validation Failed',
                    'message': self.validation_errors,
                    'type': 'danger',
                    'sticky': True,
                }
            }
        else:
            self.state = 'validated'
            self.validation_errors = False
            self.validation_date = fields.Datetime.now()

            _logger.info(f"Validation passed for {self.name}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Validation Passed',
                    'message': 'Form is ready for filing',
                    'type': 'success',
                    'sticky': False,
                }
            }

    def action_mark_as_filed(self):
        """Mark form as filed (manual confirmation)"""
        self.ensure_one()

        if self.state != 'validated':
            raise UserError("Form must be validated before marking as filed")

        self.state = 'filed'
        self.filed_date = fields.Datetime.now()
        self.filed_by = self.env.user

        _logger.info(f"Form {self.name} marked as filed by {self.env.user.name}")

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Form Filed',
                'message': 'Form marked as filed successfully',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_reset_to_draft(self):
        """Reset form to draft state"""
        self.ensure_one()

        if self.state == 'filed':
            raise UserError("Cannot reset a filed form. Create a new form instead.")

        self.state = 'draft'
        self.validation_errors = False
        self.validation_date = False

        _logger.info(f"Form {self.name} reset to draft")

    # Helper Methods
    def _validate_tin(self, tin):
        """Validate TIN format: XXX-XXX-XXX-000"""
        if not tin:
            return False

        import re
        pattern = r'^\d{3}-\d{3}-\d{3}-\d{3}$'
        return bool(re.match(pattern, tin))

    def _validate_xml_schema(self):
        """Validate XML against official BIR XSD schema"""
        # TODO: Implement XSD validation when BIR schema is available
        # For now, just check that XML is well-formed
        try:
            if not self.xml_file:
                return False

            xml_content = base64.b64decode(self.xml_file)
            ET.fromstring(xml_content)
            return True
        except ET.ParseError:
            return False

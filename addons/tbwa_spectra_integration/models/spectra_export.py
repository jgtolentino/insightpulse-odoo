# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import csv
import io
import base64
import logging

_logger = logging.getLogger(__name__)


class SpectraExport(models.Model):
    """
    Spectra export batch tracking and file generation.

    Workflow:
    1. Create export batch (manual or cron)
    2. Validate data completeness
    3. Apply mapping transformations
    4. Generate CSV files
    5. Store in Supabase archive
    6. Mark records as exported
    """
    _name = 'tbwa.spectra.export'
    _description = 'Spectra Export Batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'export_date desc, id desc'

    name = fields.Char(string='Export Reference', required=True, readonly=True,
                      default=lambda self: _('New'), copy=False)
    export_date = fields.Date(string='Export Date', required=True,
                             default=fields.Date.context_today, tracking=True)
    export_month = fields.Selection([
        ('01', 'January'), ('02', 'February'), ('03', 'March'),
        ('04', 'April'), ('05', 'May'), ('06', 'June'),
        ('07', 'July'), ('08', 'August'), ('09', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December'),
    ], string='Month', required=True, tracking=True)
    export_year = fields.Char(string='Year', size=4, required=True,
                             default=lambda self: str(fields.Date.today().year))

    state = fields.Selection([
        ('draft', 'Draft'),
        ('validating', 'Validating'),
        ('ready', 'Ready for Export'),
        ('exported', 'Exported'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='draft', tracking=True, string='Status')

    # Export types
    export_type = fields.Selection([
        ('expense', 'Expense Report'),
        ('cash_advance', 'Cash Advance'),
        ('journal_entry', 'Journal Entry'),
        ('audit_trail', 'Audit Trail'),
    ], string='Export Type', required=True)

    # Data selection
    expense_sheet_ids = fields.Many2many('hr.expense.sheet', string='Expense Reports')
    cash_advance_ids = fields.Many2many('hr.expense.advance', string='Cash Advances')
    journal_entry_ids = fields.Many2many('account.move', string='Journal Entries')

    # Statistics
    record_count = fields.Integer(string='Total Records', compute='_compute_statistics', store=True)
    total_amount = fields.Monetary(string='Total Amount', compute='_compute_statistics',
                                   store=True, currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id)

    # Export files
    export_file_expense = fields.Binary(string='Expense Export File', attachment=True)
    export_file_expense_name = fields.Char(string='Expense File Name')
    export_file_je = fields.Binary(string='Journal Entry Export File', attachment=True)
    export_file_je_name = fields.Char(string='JE File Name')
    export_file_audit = fields.Binary(string='Audit Trail File', attachment=True)
    export_file_audit_name = fields.Char(string='Audit File Name')

    # Archive
    supabase_url = fields.Char(string='Supabase Archive URL', readonly=True)
    archived_date = fields.Datetime(string='Archived Date', readonly=True)

    # Approval
    approved_by_finance = fields.Boolean(string='Approved by Finance', tracking=True)
    finance_approver_id = fields.Many2one('res.users', string='Finance Approver')
    finance_approval_date = fields.Datetime(string='Finance Approval Date')

    # Validation errors
    validation_errors = fields.Text(string='Validation Errors', readonly=True)
    error_count = fields.Integer(string='Error Count', default=0)

    # Metadata
    user_id = fields.Many2one('res.users', string='Created By', default=lambda self: self.env.user,
                             readonly=True)
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env.company, readonly=True)

    @api.model
    def create(self, vals):
        """Generate export reference on creation."""
        if vals.get('name', _('New')) == _('New'):
            export_type_code = {
                'expense': 'EXP',
                'cash_advance': 'CA',
                'journal_entry': 'JE',
                'audit_trail': 'AUD',
            }.get(vals.get('export_type', 'expense'), 'EXP')

            vals['name'] = self.env['ir.sequence'].next_by_code('tbwa.spectra.export') or \
                          f"SPECTRA_{export_type_code}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return super(SpectraExport, self).create(vals)

    @api.depends('expense_sheet_ids', 'cash_advance_ids', 'journal_entry_ids')
    def _compute_statistics(self):
        """Compute total records and amount."""
        for record in self:
            if record.export_type == 'expense':
                record.record_count = len(record.expense_sheet_ids)
                record.total_amount = sum(record.expense_sheet_ids.mapped('total_amount'))
            elif record.export_type == 'cash_advance':
                record.record_count = len(record.cash_advance_ids)
                record.total_amount = sum(record.cash_advance_ids.mapped('amount'))
            elif record.export_type == 'journal_entry':
                record.record_count = len(record.journal_entry_ids)
                record.total_amount = sum(record.journal_entry_ids.mapped('amount_total'))
            else:
                record.record_count = 0
                record.total_amount = 0.0

    def action_validate(self):
        """Validate export data before generating files."""
        self.ensure_one()
        errors = []

        # Check records exist
        if self.record_count == 0:
            errors.append("No records selected for export")

        # Validate expense sheets
        if self.export_type == 'expense':
            for sheet in self.expense_sheet_ids:
                # Check approval status
                if sheet.state != 'approve':
                    errors.append(f"Expense {sheet.name} not approved")

                # Check receipts
                for expense in sheet.expense_line_ids:
                    if expense.product_id.require_receipt and not expense.attachment_number:
                        errors.append(f"Missing receipt: {expense.name}")

                # Check GL mapping
                for expense in sheet.expense_line_ids:
                    gl_mapping = self.env['tbwa.spectra.gl.code'].search([
                        ('expense_category', '=', expense.product_id.name)
                    ], limit=1)
                    if not gl_mapping:
                        errors.append(f"No GL mapping for category: {expense.product_id.name}")

        # Validate cash advances
        elif self.export_type == 'cash_advance':
            for advance in self.cash_advance_ids:
                if advance.state not in ['approved', 'paid']:
                    errors.append(f"Cash advance {advance.name} not approved/paid")

                if not advance.employee_id.employee_code:
                    errors.append(f"Missing employee code: {advance.employee_id.name}")

        if errors:
            self.validation_errors = "\n".join(errors)
            self.error_count = len(errors)
            self.state = 'failed'
            raise UserError(_("Validation failed:\n%s") % self.validation_errors)
        else:
            self.validation_errors = False
            self.error_count = 0
            self.state = 'ready'

        return True

    def action_generate_export_files(self):
        """Generate Spectra-compliant export files."""
        self.ensure_one()

        if self.state != 'ready':
            raise UserError(_("Export must be validated before generating files"))

        # Generate expense export
        if self.export_type == 'expense':
            self._generate_expense_export()

        # Generate cash advance export
        elif self.export_type == 'cash_advance':
            self._generate_cash_advance_export()

        # Generate journal entry export
        elif self.export_type == 'journal_entry':
            self._generate_journal_entry_export()

        # Generate audit trail
        self._generate_audit_trail()

        self.state = 'exported'
        self.message_post(body=_("Export files generated successfully"))

        return True

    def _generate_expense_export(self):
        """Generate TBWA_EXPENSES_MMYY.csv file."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row (Spectra format)
        headers = [
            'DOC_DATE', 'EMPLOYEE_CODE', 'PROJECT_CODE', 'GL_ACCOUNT',
            'NET_AMOUNT', 'VAT', 'WITHHOLDING', 'GROSS_AMOUNT',
            'DESCRIPTION', 'FILE_REFERENCE'
        ]
        writer.writerow(headers)

        # Data rows
        for sheet in self.expense_sheet_ids:
            for expense in sheet.expense_line_ids:
                # Get GL mapping
                gl_mapping = self.env['tbwa.spectra.gl.code'].search([
                    ('expense_category', '=', expense.product_id.name)
                ], limit=1)

                if not gl_mapping:
                    continue  # Should have been caught in validation

                gl_entry = gl_mapping.get_gl_entry(expense)

                # Get employee code
                employee_code = expense.employee_id.employee_code or \
                               expense.employee_id.user_id.login.split('@')[0].upper()

                # Get project code
                project_code = expense.analytic_account_id.code if expense.analytic_account_id else ''

                # Get attachment reference
                attachment_ref = ''
                if expense.attachment_ids:
                    # Store in Supabase and get URL
                    attachment_ref = self._archive_attachment(expense.attachment_ids[0])

                row = [
                    fields.Date.to_string(expense.date),
                    employee_code,
                    project_code,
                    gl_entry['gl_account'],
                    "{:.2f}".format(gl_entry['net_amount']),
                    "{:.2f}".format(gl_entry['vat_amount']),
                    "{:.2f}".format(gl_entry['withholding_amount']),
                    "{:.2f}".format(gl_entry['gross_amount']),
                    expense.name,
                    attachment_ref,
                ]
                writer.writerow(row)

        # Save file
        filename = f"TBWA_EXPENSES_{self.export_month}{self.export_year[-2:]}.csv"
        self.export_file_expense = base64.b64encode(output.getvalue().encode('utf-8'))
        self.export_file_expense_name = filename

    def _generate_cash_advance_export(self):
        """Generate TBWA_CA_MMYY.csv file."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        headers = [
            'DOC_DATE', 'EMPLOYEE_CODE', 'AMOUNT', 'PURPOSE',
            'PROJECT_CODE', 'APPROVAL_DATE', 'PAYMENT_DATE', 'STATUS'
        ]
        writer.writerow(headers)

        # Data rows
        for advance in self.cash_advance_ids:
            employee_code = advance.employee_id.employee_code or \
                           advance.employee_id.user_id.login.split('@')[0].upper()

            project_code = advance.analytic_account_id.code if advance.analytic_account_id else ''

            row = [
                fields.Date.to_string(advance.date),
                employee_code,
                "{:.2f}".format(advance.amount),
                advance.description or '',
                project_code,
                fields.Datetime.to_string(advance.approval_date) if advance.approval_date else '',
                fields.Date.to_string(advance.payment_date) if advance.payment_date else '',
                advance.state,
            ]
            writer.writerow(row)

        # Save file
        filename = f"TBWA_CA_{self.export_month}{self.export_year[-2:]}.csv"
        self.export_file_je = base64.b64encode(output.getvalue().encode('utf-8'))
        self.export_file_je_name = filename

    def _generate_journal_entry_export(self):
        """Generate TBWA_JE_MMYY.csv file."""
        # TODO: Implement journal entry export format
        pass

    def _generate_audit_trail(self):
        """Generate TBWA_AUDIT_MMYY.csv file with approval history."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        headers = [
            'DOC_TYPE', 'DOC_REF', 'DOC_DATE', 'EMPLOYEE', 'AMOUNT',
            'APPROVER_L1', 'APPROVAL_L1_DATE', 'APPROVER_L2', 'APPROVAL_L2_DATE',
            'STATUS', 'NOTES'
        ]
        writer.writerow(headers)

        # Audit data from expense sheets
        if self.export_type == 'expense':
            for sheet in self.expense_sheet_ids:
                # Get approval history from chatter
                approvals = self._get_approval_history(sheet)

                row = [
                    'EXPENSE',
                    sheet.name,
                    fields.Date.to_string(sheet.accounting_date or sheet.create_date),
                    sheet.employee_id.name,
                    "{:.2f}".format(sheet.total_amount),
                    approvals.get('approver_1', ''),
                    approvals.get('approval_1_date', ''),
                    approvals.get('approver_2', ''),
                    approvals.get('approval_2_date', ''),
                    sheet.state,
                    sheet.notes or '',
                ]
                writer.writerow(row)

        # Save file
        filename = f"TBWA_AUDIT_{self.export_month}{self.export_year[-2:]}.csv"
        self.export_file_audit = base64.b64encode(output.getvalue().encode('utf-8'))
        self.export_file_audit_name = filename

    def _get_approval_history(self, record):
        """Extract approval history from mail.message chatter."""
        approvals = {}
        messages = self.env['mail.message'].search([
            ('model', '=', record._name),
            ('res_id', '=', record.id),
            ('message_type', '=', 'notification'),
        ], order='date asc')

        approval_count = 0
        for message in messages:
            if 'approved' in message.body.lower():
                approval_count += 1
                approvals[f'approver_{approval_count}'] = message.author_id.name
                approvals[f'approval_{approval_count}_date'] = fields.Datetime.to_string(message.date)

        return approvals

    def _archive_attachment(self, attachment):
        """Archive attachment to Supabase Storage and return URL."""
        # TODO: Implement Supabase upload
        # For now, return placeholder
        return f"supabase://tbwa-attachments/{attachment.id}/{attachment.name}"

    def action_approve_finance(self):
        """Finance approval to finalize export."""
        self.ensure_one()

        if self.state != 'exported':
            raise UserError(_("Export must be completed before approval"))

        self.approved_by_finance = True
        self.finance_approver_id = self.env.user
        self.finance_approval_date = fields.Datetime.now()

        # Mark source records as exported
        if self.export_type == 'expense':
            self.expense_sheet_ids.write({'exported_to_spectra': True})
        elif self.export_type == 'cash_advance':
            self.cash_advance_ids.write({'exported_to_spectra': True})

        self.message_post(
            body=_("Export approved by %s") % self.env.user.name,
            subtype_xmlid='mail.mt_comment'
        )

        return True

    @api.model
    def cron_auto_export(self):
        """
        Scheduled action to create monthly export batch.
        Runs on 1st business day of month at 06:30 AM.
        """
        today = fields.Date.today()
        last_month = today - timedelta(days=today.day)

        # Check if export already exists
        existing = self.search([
            ('export_month', '=', last_month.strftime('%m')),
            ('export_year', '=', str(last_month.year)),
            ('export_type', '=', 'expense'),
        ], limit=1)

        if existing:
            _logger.info(f"Export for {last_month.strftime('%B %Y')} already exists")
            return existing

        # Find approved, non-exported expense sheets
        expense_sheets = self.env['hr.expense.sheet'].search([
            ('state', '=', 'approve'),
            ('exported_to_spectra', '=', False),
            ('accounting_date', '>=', last_month.replace(day=1)),
            ('accounting_date', '<=', last_month),
        ])

        if not expense_sheets:
            _logger.info(f"No expense sheets to export for {last_month.strftime('%B %Y')}")
            return

        # Create export batch
        export_batch = self.create({
            'export_type': 'expense',
            'export_month': last_month.strftime('%m'),
            'export_year': str(last_month.year),
            'expense_sheet_ids': [(6, 0, expense_sheets.ids)],
        })

        # Auto-validate and generate
        try:
            export_batch.action_validate()
            export_batch.action_generate_export_files()

            # Send notification to finance
            finance_users = self.env.ref('tbwa_spectra_integration.group_finance_spectra').users
            export_batch.message_subscribe(partner_ids=finance_users.partner_id.ids)
            export_batch.message_post(
                body=_("Automatic Spectra export created. Please review and approve."),
                subtype_xmlid='mail.mt_comment'
            )

            _logger.info(f"Created Spectra export batch: {export_batch.name}")
        except Exception as e:
            _logger.error(f"Spectra export failed: {e}")
            export_batch.state = 'failed'
            export_batch.validation_errors = str(e)

        return export_batch

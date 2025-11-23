# -*- coding: utf-8 -*-
from odoo import models, fields, api


class HrExpenseSheet(models.Model):
    """
    Extend hr.expense.sheet with Spectra export tracking and canonical tags/labels.
    """
    _inherit = 'hr.expense.sheet'

    # Spectra export tracking
    exported_to_spectra = fields.Boolean(
        string='Exported to Spectra',
        default=False,
        readonly=True,
        tracking=True,
        help='Indicates if this expense report has been exported to Spectra GL'
    )
    export_batch_id = fields.Many2one(
        'tbwa.spectra.export',
        string='Export Batch',
        readonly=True,
        help='Link to Spectra export batch containing this expense'
    )
    export_date = fields.Datetime(
        string='Export Date',
        readonly=True,
        help='Date when exported to Spectra'
    )

    # Canonical tags (semantic markers)
    tag_ids = fields.Many2many(
        'tbwa.tag.vocabulary',
        'expense_sheet_tag_rel',
        'sheet_id',
        'tag_id',
        string='Tags',
        help='Semantic markers for filtering and grouping (e.g., closing-2025-11, agency/rim)'
    )

    # Workflow state label
    workflow_label = fields.Selection([
        ('exp:draft', '⚪ Draft'),
        ('exp:submitted', '🔵 Submitted'),
        ('exp:for-review', '🟡 Awaiting Reviewer'),
        ('exp:for-approval', '🟠 Awaiting Approver'),
        ('exp:approved', '🟢 Approved'),
        ('exp:for-posting', '📊 Ready for GL Posting'),
        ('exp:posted', '✅ Posted to GL'),
        ('exp:rejected', '🔴 Rejected'),
    ], string='Workflow Label', compute='_compute_workflow_label', store=True)

    # Priority label
    priority_label = fields.Selection([
        ('priority:critical', '🔴 Critical'),
        ('priority:high', '🟠 High'),
        ('priority:medium', '🟡 Medium'),
        ('priority:low', '🟢 Low'),
    ], string='Priority', default='priority:medium', tracking=True)

    # SLA tracking label
    sla_status = fields.Selection([
        ('sla:on-track', '🟢 On Track'),
        ('sla:at-risk', '🟡 At Risk'),
        ('sla:breach', '🔴 Breached'),
    ], string='SLA Status', compute='_compute_sla_status', store=True)

    # Compliance labels
    audit_flag = fields.Selection([
        ('audit:not-required', 'Not Required'),
        ('audit:required', '⚠️ Audit Required'),
        ('audit:sensitive', '🔒 Sensitive Data'),
    ], string='Audit Flag', compute='_compute_audit_flag', store=True)

    # Cash advance link
    cash_advance_id = fields.Many2one(
        'hr.expense.advance',
        string='Cash Advance',
        help='Link to cash advance being liquidated'
    )

    @api.depends('state')
    def _compute_workflow_label(self):
        """Map Odoo state to canonical workflow label."""
        state_mapping = {
            'draft': 'exp:draft',
            'submit': 'exp:submitted',
            'approve': 'exp:approved',
            'post': 'exp:posted',
            'done': 'exp:posted',
            'cancel': 'exp:rejected',
        }
        for record in self:
            record.workflow_label = state_mapping.get(record.state, 'exp:draft')

    @api.depends('create_date', 'approval_date', 'state')
    def _compute_sla_status(self):
        """
        Calculate SLA status based on submission age and approval time.

        SLA Targets:
        - Submission to approval: 48 hours
        - At risk: 80% of SLA (38.4 hours)
        - Breach: Over 48 hours
        """
        from datetime import timedelta

        for record in self:
            if record.state in ['draft', 'cancel']:
                record.sla_status = 'sla:on-track'
                continue

            if record.state in ['post', 'done']:
                record.sla_status = 'sla:on-track'
                continue

            # Calculate age in hours
            age = fields.Datetime.now() - record.create_date
            age_hours = age.total_seconds() / 3600

            if age_hours > 48:
                record.sla_status = 'sla:breach'
            elif age_hours > 38.4:  # 80% of 48 hours
                record.sla_status = 'sla:at-risk'
            else:
                record.sla_status = 'sla:on-track'

    @api.depends('total_amount', 'expense_line_ids.product_id')
    def _compute_audit_flag(self):
        """
        Determine audit requirements based on amount and categories.

        Audit required if:
        - Amount > ₱50,000
        - Professional services category
        - Employee is executive (job level)
        """
        for record in self:
            # High value
            if record.total_amount > 50000:
                record.audit_flag = 'audit:required'
                continue

            # Sensitive categories
            sensitive_categories = [
                'Professional Services',
                'Legal Fees',
                'Consulting',
            ]
            if any(line.product_id.name in sensitive_categories
                   for line in record.expense_line_ids):
                record.audit_flag = 'audit:sensitive'
                continue

            # Default
            record.audit_flag = 'audit:not-required'

    def action_export_to_spectra(self):
        """Mark expense as ready for Spectra export."""
        self.ensure_one()

        if self.state != 'approve':
            from odoo.exceptions import UserError
            raise UserError('Only approved expenses can be exported to Spectra')

        # Add export tag
        export_tag = self.env['tbwa.tag.vocabulary'].search([
            ('name', '=', 'spectra/export')
        ], limit=1)
        if export_tag:
            self.tag_ids = [(4, export_tag.id)]

        return True


class TBWATagVocabulary(models.Model):
    """
    Canonical tag vocabulary for finance operations.

    Tags are semantic markers used for:
    - Cross-platform filtering (Odoo, GitHub, Clarity PPM)
    - Automated workflow routing
    - Compliance tracking
    - Analytics and reporting
    """
    _name = 'tbwa.tag.vocabulary'
    _description = 'Tag Vocabulary'
    _order = 'domain, category, name'

    name = fields.Char(
        string='Tag Name',
        required=True,
        help='Format: {domain}/{category}/{identifier} (e.g., closing-2025-11, agency/rim)'
    )
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True,
        help='Human-readable name'
    )

    # Tag hierarchy
    domain = fields.Selection([
        ('finance', 'Finance'),
        ('agency', 'Agency'),
        ('compliance', 'Compliance'),
        ('integration', 'Integration'),
        ('operations', 'Operations'),
        ('dev', 'Development'),
        ('docs', 'Documentation'),
    ], string='Domain', required=True)

    category = fields.Char(
        string='Category',
        help='Second-level category (e.g., closing, bir, concur-parity)'
    )

    identifier = fields.Char(
        string='Identifier',
        help='Specific identifier (e.g., 2025-11, rim, expense)'
    )

    # Metadata
    active = fields.Boolean(default=True)
    color = fields.Integer(string='Color Index', default=0)
    description = fields.Text(
        string='Description',
        help='Usage guidelines and examples'
    )

    # Usage tracking
    usage_count = fields.Integer(
        string='Usage Count',
        compute='_compute_usage_count',
        store=False,
        help='Number of records using this tag'
    )

    # Relationships
    expense_sheet_ids = fields.Many2many(
        'hr.expense.sheet',
        'expense_sheet_tag_rel',
        'tag_id',
        'sheet_id',
        string='Expense Sheets'
    )
    cash_advance_ids = fields.Many2many(
        'hr.expense.advance',
        'cash_advance_tag_rel',
        'tag_id',
        'advance_id',
        string='Cash Advances'
    )

    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)',
         'Tag name must be unique!')
    ]

    @api.depends('name')
    def _compute_display_name(self):
        """Convert tag name to readable display name."""
        for record in self:
            # Remove domain prefix and capitalize
            display = record.name.replace('-', ' ').replace('/', ' - ').title()
            record.display_name = display

    def _compute_usage_count(self):
        """Count total usage across all models."""
        for record in self:
            count = 0
            count += len(record.expense_sheet_ids)
            count += len(record.cash_advance_ids)
            record.usage_count = count

    @api.model
    def create_standard_tags(self):
        """
        Create standard tag vocabulary from TAG_LABEL_VOCABULARY.md.

        Run this method after module installation to populate initial tags.
        """
        standard_tags = [
            # Finance - Closing
            {'name': 'closing-2025-11', 'domain': 'finance', 'category': 'closing',
             'description': 'November 2025 month-end close'},
            {'name': 'closing-2025-12', 'domain': 'finance', 'category': 'closing',
             'description': 'December 2025 month-end close'},
            {'name': 'month-end', 'domain': 'finance', 'category': 'closing',
             'description': 'General month-end activities'},

            # Agencies
            {'name': 'agency/rim', 'domain': 'agency', 'identifier': 'rim',
             'description': 'RIM agency'},
            {'name': 'agency/ckvc', 'domain': 'agency', 'identifier': 'ckvc',
             'description': 'CKVC agency'},
            {'name': 'agency/bom', 'domain': 'agency', 'identifier': 'bom',
             'description': 'BOM agency'},

            # Compliance
            {'name': 'bir/1601-c', 'domain': 'compliance', 'category': 'bir',
             'description': 'Monthly withholding tax'},
            {'name': 'bir/2550q', 'domain': 'compliance', 'category': 'bir',
             'description': 'Quarterly VAT'},

            # Integration
            {'name': 'concur-parity/expense', 'domain': 'integration',
             'category': 'concur-parity', 'description': 'Concur expense feature parity'},
            {'name': 'spectra/export', 'domain': 'integration', 'category': 'spectra',
             'description': 'Spectra GL export'},
        ]

        for tag_data in standard_tags:
            existing = self.search([('name', '=', tag_data['name'])], limit=1)
            if not existing:
                self.create(tag_data)

        return True

# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import api, fields, models


class SaaSTenant(models.Model):
    _name = 'saas.tenant'
    _description = 'SaaS Tenant'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(
        string='Tenant Name',
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        default=True,
        tracking=True,
    )
    tenant_code = fields.Char(
        string='Tenant Code',
        required=True,
        tracking=True,
    )
    subdomain = fields.Char(
        string='Subdomain',
        required=True,
        tracking=True,
        help='Tenant subdomain for multi-tenant setup',
    )
    database_name = fields.Char(
        string='Database Name',
        required=True,
        tracking=True,
    )
    admin_user_id = fields.Many2one(
        comodel_name='res.users',
        string='Tenant Admin',
        tracking=True,
    )
    admin_email = fields.Char(
        string='Admin Email',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('provisioning', 'Provisioning'),
            ('active', 'Active'),
            ('suspended', 'Suspended'),
            ('terminated', 'Terminated'),
        ],
        default='draft',
        required=True,
        tracking=True,
    )
    plan_id = fields.Selection(
        selection=[
            ('trial', 'Trial'),
            ('starter', 'Starter'),
            ('professional', 'Professional'),
            ('enterprise', 'Enterprise'),
        ],
        string='Subscription Plan',
        required=True,
        default='trial',
        tracking=True,
    )
    max_users = fields.Integer(
        string='Max Users',
        default=5,
        required=True,
    )
    current_users = fields.Integer(
        string='Current Users',
        compute='_compute_current_users',
    )
    storage_limit_gb = fields.Float(
        string='Storage Limit (GB)',
        default=10.0,
        required=True,
    )
    current_storage_gb = fields.Float(
        string='Current Storage (GB)',
        compute='_compute_current_storage',
    )
    created_date = fields.Datetime(
        string='Created Date',
        default=fields.Datetime.now,
        required=True,
    )
    expiry_date = fields.Date(
        string='Expiry Date',
        tracking=True,
    )
    backup_ids = fields.One2many(
        comodel_name='saas.backup',
        inverse_name='tenant_id',
        string='Backups',
    )
    usage_ids = fields.One2many(
        comodel_name='saas.usage',
        inverse_name='tenant_id',
        string='Usage Records',
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.depends('admin_user_id')
    def _compute_current_users(self):
        """Compute current number of users for tenant."""
        for tenant in self:
            # Placeholder - would query actual tenant database
            tenant.current_users = 1 if tenant.admin_user_id else 0

    @api.depends('database_name')
    def _compute_current_storage(self):
        """Compute current storage usage for tenant."""
        for tenant in self:
            # Placeholder - would query actual database size
            tenant.current_storage_gb = 0.0

    def action_provision(self):
        """Provision new tenant."""
        self.write({'state': 'provisioning'})
        # Actual provisioning logic would go here
        self.write({'state': 'active'})

    def action_activate(self):
        """Activate tenant."""
        self.write({'state': 'active'})

    def action_suspend(self):
        """Suspend tenant."""
        self.write({'state': 'suspended'})

    def action_terminate(self):
        """Terminate tenant."""
        self.write({'state': 'terminated', 'active': False})

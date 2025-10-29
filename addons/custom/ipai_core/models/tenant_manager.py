from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import psycopg2
import logging

_logger = logging.getLogger(__name__)


class TenantManager(models.Model):
    """Multi-tenancy manager for SaaS operations."""

    _name = "ipai.tenant.manager"
    _description = "Tenant Manager"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, index=True, tracking=True)
    code = fields.Char(
        required=True,
        index=True,
        help="Unique tenant code used for database naming",
    )
    active = fields.Boolean(default=True, tracking=True)
    description = fields.Text()

    # Database configuration
    database_name = fields.Char(compute="_compute_database_name", store=True)
    database_created = fields.Boolean(default=False, readonly=True)
    database_size_mb = fields.Float(readonly=True, help="Database size in MB")

    # Admin user
    admin_user_id = fields.Many2one(
        "res.users", string="Admin User", help="Tenant administrator"
    )
    admin_email = fields.Char(required=True)
    admin_login = fields.Char(required=True)

    # Plan & billing
    plan_id = fields.Many2one("ipai.tenant.plan", string="Subscription Plan")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("provisioning", "Provisioning"),
            ("active", "Active"),
            ("suspended", "Suspended"),
            ("terminated", "Terminated"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )

    # Usage tracking
    user_count = fields.Integer(readonly=True, help="Current active users")
    storage_mb = fields.Float(readonly=True, help="Storage usage in MB")
    api_calls_month = fields.Integer(readonly=True, help="API calls this month")

    # Dates
    provision_date = fields.Datetime(readonly=True)
    activation_date = fields.Datetime(readonly=True)
    termination_date = fields.Datetime(readonly=True)
    last_backup_date = fields.Datetime(readonly=True)

    _sql_constraints = [
        ("code_unique", "UNIQUE(code)", "Tenant code must be unique."),
        ("database_name_unique", "UNIQUE(database_name)", "Database name must be unique."),
    ]

    @api.depends("code")
    def _compute_database_name(self):
        for tenant in self:
            if tenant.code:
                # Sanitize code for database naming
                db_code = "".join(c for c in tenant.code if c.isalnum() or c == "_")
                tenant.database_name = f"odoo_{db_code.lower()}"
            else:
                tenant.database_name = False

    @api.constrains("code")
    def _check_code(self):
        for tenant in self:
            if tenant.code and not tenant.code.replace("_", "").isalnum():
                raise ValidationError(
                    _("Tenant code must contain only letters, numbers, and underscores.")
                )

    def action_provision(self):
        """Provision new tenant database."""
        self.ensure_one()
        if self.state != "draft":
            raise UserError(_("Only draft tenants can be provisioned."))

        self.write({"state": "provisioning"})

        try:
            # Create database
            self._create_database()

            # Initialize modules
            self._initialize_modules()

            # Create admin user
            self._create_admin_user()

            # Setup backup schedule
            self._setup_backup()

            self.write(
                {
                    "state": "active",
                    "database_created": True,
                    "provision_date": fields.Datetime.now(),
                    "activation_date": fields.Datetime.now(),
                }
            )

            self.message_post(
                body=_("Tenant provisioned successfully. Database: %s")
                % self.database_name,
                subject=_("Tenant Provisioned"),
            )

        except Exception as e:
            _logger.error(f"Tenant provisioning failed: {e}", exc_info=True)
            self.write({"state": "draft"})
            raise UserError(_("Provisioning failed: %s") % str(e))

        return True

    def action_suspend(self):
        """Suspend tenant access."""
        self.ensure_one()
        if self.state != "active":
            raise UserError(_("Only active tenants can be suspended."))

        self.write({"state": "suspended"})
        self.message_post(
            body=_("Tenant suspended."),
            subject=_("Tenant Suspended"),
        )
        return True

    def action_reactivate(self):
        """Reactivate suspended tenant."""
        self.ensure_one()
        if self.state != "suspended":
            raise UserError(_("Only suspended tenants can be reactivated."))

        self.write({"state": "active", "activation_date": fields.Datetime.now()})
        return True

    def action_terminate(self):
        """Terminate tenant and optionally delete database."""
        self.ensure_one()
        if self.state == "terminated":
            raise UserError(_("Tenant is already terminated."))

        # Create final backup before termination
        self._create_backup()

        self.write({"state": "terminated", "termination_date": fields.Datetime.now()})
        return True

    def _create_database(self):
        """Create PostgreSQL database for tenant."""
        self.ensure_one()
        # Implementation placeholder - actual DB creation logic
        _logger.info(f"Creating database: {self.database_name}")

    def _initialize_modules(self):
        """Initialize Odoo modules in tenant database."""
        self.ensure_one()
        # Implementation placeholder - module installation logic
        _logger.info(f"Initializing modules for: {self.database_name}")

    def _create_admin_user(self):
        """Create admin user in tenant database."""
        self.ensure_one()
        # Implementation placeholder - admin user creation logic
        _logger.info(f"Creating admin user: {self.admin_login}")

    def _setup_backup(self):
        """Setup automated backup schedule."""
        self.ensure_one()
        # Implementation placeholder - backup automation logic
        _logger.info(f"Setting up backup for: {self.database_name}")

    def _create_backup(self):
        """Create database backup."""
        self.ensure_one()
        # Implementation placeholder - backup creation logic
        _logger.info(f"Creating backup for: {self.database_name}")


class TenantPlan(models.Model):
    """Subscription plans for tenants."""

    _name = "ipai.tenant.plan"
    _description = "Tenant Subscription Plan"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    description = fields.Text()

    # Pricing
    price_monthly = fields.Float(required=True)
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )

    # Limits
    max_users = fields.Integer(
        default=10, required=True, help="Maximum active users"
    )
    max_storage_mb = fields.Integer(
        default=1024, required=True, help="Maximum storage in MB"
    )
    max_api_calls_month = fields.Integer(
        default=10000, required=True, help="Maximum API calls per month"
    )

    # Features
    enable_ai_workspace = fields.Boolean(default=False)
    enable_advanced_analytics = fields.Boolean(default=False)
    enable_api_access = fields.Boolean(default=True)

    # Statistics
    tenant_count = fields.Integer(compute="_compute_tenant_count", store=False)

    @api.depends()
    def _compute_tenant_count(self):
        for plan in self:
            plan.tenant_count = self.env["ipai.tenant.manager"].search_count(
                [("plan_id", "=", plan.id), ("state", "=", "active")]
            )

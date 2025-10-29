from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
import statistics


class RatePolicy(models.Model):
    """Rate policy calculation framework for vendor rate bands."""

    _name = "ipai.rate.policy"
    _description = "Rate Policy Configuration"
    _order = "name"

    name = fields.Char(required=True, index=True)
    active = fields.Boolean(default=True)
    description = fields.Text()

    # Configuration
    lookback_months = fields.Integer(
        default=18, required=True, help="Months of history to analyze"
    )
    markup_percentage = fields.Float(
        default=25.0, required=True, help="Markup percentage applied to vendor rates"
    )
    rounding_amount = fields.Float(
        default=100.0, required=True, help="Round public rate to nearest X"
    )
    percentile = fields.Selection(
        [
            ("50", "P50 (Median)"),
            ("60", "P60"),
            ("75", "P75"),
            ("90", "P90"),
        ],
        default="60",
        required=True,
        help="Percentile to use for rate calculation",
    )

    # Automation
    auto_update = fields.Boolean(
        default=True, help="Automatically update rates via cron"
    )
    cron_id = fields.Many2one("ir.cron", string="Scheduled Action", readonly=True)

    # Audit
    last_update_date = fields.Datetime(readonly=True)
    last_update_user_id = fields.Many2one("res.users", string="Last Updated By", readonly=True)
    update_count = fields.Integer(default=0, readonly=True)

    @api.model
    def create(self, vals):
        policy = super().create(vals)
        if policy.auto_update:
            policy._create_cron()
        return policy

    def write(self, vals):
        res = super().write(vals)
        if "auto_update" in vals:
            for policy in self:
                if policy.auto_update and not policy.cron_id:
                    policy._create_cron()
                elif not policy.auto_update and policy.cron_id:
                    policy.cron_id.unlink()
        return res

    def unlink(self):
        self.mapped("cron_id").unlink()
        return super().unlink()

    def _create_cron(self):
        """Create automated cron job for rate updates."""
        self.ensure_one()
        if self.cron_id:
            return

        cron = self.env["ir.cron"].create(
            {
                "name": f"Rate Policy: {self.name}",
                "model_id": self.env.ref("ipai_core.model_ipai_rate_policy").id,
                "state": "code",
                "code": f"model.browse({self.id}).action_update_rates()",
                "interval_number": 1,
                "interval_type": "days",
                "numbercall": -1,
                "active": True,
            }
        )
        self.cron_id = cron

    def action_update_rates(self):
        """Calculate and update public rate bands based on policy."""
        self.ensure_one()

        # Get historical rate data
        cutoff_date = datetime.now() - timedelta(days=30 * self.lookback_months)

        RateBand = self.env["ipai.rate.band"]
        RateCard = self.env.get("vendor.rate.card")  # May not exist yet

        if not RateCard:
            return

        # Get all unique roles
        roles = RateCard.search([("create_date", ">=", cutoff_date)]).mapped("role_id")

        for role in roles:
            # Get historical rates for this role
            rate_cards = RateCard.search(
                [("role_id", "=", role.id), ("create_date", ">=", cutoff_date)]
            )

            if not rate_cards:
                continue

            rates = rate_cards.mapped("rate")
            if not rates:
                continue

            # Calculate percentile
            percentile_map = {"50": 50, "60": 60, "75": 75, "90": 90}
            percentile_value = statistics.quantiles(
                rates, n=100, method="inclusive"
            )[percentile_map[self.percentile] - 1]

            # Apply markup and rounding
            public_rate = percentile_value * (1 + self.markup_percentage / 100)
            public_rate = round(public_rate / self.rounding_amount) * self.rounding_amount

            # Update or create rate band
            band = RateBand.search([("role_id", "=", role.id)], limit=1)
            if band:
                band.write(
                    {
                        "public_rate": public_rate,
                        "vendor_rate_p50": statistics.median(rates),
                        "vendor_rate_p60": percentile_value if self.percentile == "60" else None,
                        "vendor_rate_p75": statistics.quantiles(rates, n=4, method="inclusive")[2],
                        "sample_size": len(rates),
                        "last_update_date": fields.Datetime.now(),
                        "last_update_policy_id": self.id,
                    }
                )
            else:
                RateBand.create(
                    {
                        "role_id": role.id,
                        "public_rate": public_rate,
                        "vendor_rate_p50": statistics.median(rates),
                        "vendor_rate_p60": percentile_value if self.percentile == "60" else None,
                        "vendor_rate_p75": statistics.quantiles(rates, n=4, method="inclusive")[2],
                        "sample_size": len(rates),
                        "last_update_policy_id": self.id,
                    }
                )

        # Update audit fields
        self.write(
            {
                "last_update_date": fields.Datetime.now(),
                "last_update_user_id": self.env.user.id,
                "update_count": self.update_count + 1,
            }
        )

        return True


class RateBand(models.Model):
    """Public rate bands calculated from vendor rates."""

    _name = "ipai.rate.band"
    _description = "Public Rate Band"
    _order = "role_id"

    role_id = fields.Many2one("hr.job", required=True, string="Role", index=True)
    public_rate = fields.Float(
        required=True, help="Public rate shown to clients and account managers"
    )

    # Statistical data
    vendor_rate_p50 = fields.Float(string="Vendor P50 (Median)", readonly=True)
    vendor_rate_p60 = fields.Float(string="Vendor P60", readonly=True)
    vendor_rate_p75 = fields.Float(string="Vendor P75", readonly=True)
    sample_size = fields.Integer(readonly=True, help="Number of vendor rates analyzed")

    # Audit
    last_update_date = fields.Datetime(readonly=True)
    last_update_policy_id = fields.Many2one(
        "ipai.rate.policy", string="Updated By Policy", readonly=True
    )
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id
    )

    _sql_constraints = [
        ("role_unique", "UNIQUE(role_id)", "Rate band already exists for this role.")
    ]

    @api.constrains("public_rate")
    def _check_public_rate(self):
        for band in self:
            if band.public_rate <= 0:
                raise ValidationError(_("Public rate must be greater than zero."))

# ipai_workspace_core/models/workspace.py
from odoo import api, fields, models, _


class Workspace(models.Model):
    """
    Smart Delta 'Notion-style' workspace pivot.

    This model is intentionally generic and LEAN:
    - One record per client workspace (agency or firm)
    - Links to any Odoo object via the link table (res_model/res_id)
    - No heavy finance or industry logic here (that lives in vertical modules)
    """

    _name = "ipai.workspace"
    _description = "InsightPulse Workspace"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    # BASIC METADATA
    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True, tracking=True)
    sequence = fields.Integer(default=10)

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        default=lambda self: self.env.company,
        index=True,
    )

    # CLIENT / OWNERSHIP
    client_id = fields.Many2one(
        "res.partner",
        string="Client",
        domain=[("is_company", "=", True)],
        tracking=True,
        index=True,
    )
    account_manager_id = fields.Many2one(
        "res.users",
        string="Account Manager",
        tracking=True,
    )

    # INDUSTRY FLAG (used by vertical modules)
    industry = fields.Selection(
        [
            ("marketing_agency", "Marketing Agency"),
            ("accounting_firm", "Accounting Firm"),
            ("other", "Other"),
        ],
        string="Industry",
        default="marketing_agency",
        tracking=True,
        required=True,
    )

    # HIGH-LEVEL STATUS
    stage = fields.Selection(
        [
            ("prospect", "Prospect"),
            ("onboarding", "Onboarding"),
            ("active", "Active"),
            ("paused", "Paused"),
            ("closed", "Closed"),
        ],
        string="Lifecycle Stage",
        default="active",
        tracking=True,
    )
    color = fields.Integer("Color Index")  # kanban color

    # RELATION TO ANY ODOO OBJECT (GENERIC LINK TABLE)
    link_ids = fields.One2many(
        "ipai.workspace.link",
        "workspace_id",
        string="Linked Records",
    )

    # LIGHTWEIGHT METRICS (FILLED BY AUTOMATED ACTIONS / CRONS)
    project_count = fields.Integer(
        string="Projects",
        compute="_compute_counters",
        store=True,
    )
    engagement_count = fields.Integer(
        string="Engagements",
        compute="_compute_counters",
        store=True,
    )
    invoice_count = fields.Integer(
        string="Invoices",
        compute="_compute_counters",
        store=True,
    )

    _sql_constraints = [
        (
            "name_company_uniq",
            "unique(name, company_id)",
            "Workspace name must be unique per company.",
        ),
    ]

    @api.depends("link_ids.res_model", "link_ids.res_id")
    def _compute_counters(self):
        """Very conservative counter implementation.

        We *only* count links by res_model; no joins on foreign tables here.
        Vertical modules are free to add faster counters/views as needed.
        """
        for ws in self:
            projects = [l for l in ws.link_ids if l.res_model == "project.project"]
            engagements = [
                l
                for l in ws.link_ids
                if l.res_model
                in (
                    "ipai.af.engagement",  # accounting firm vertical
                    "ipai.ma.campaign",   # marketing agency vertical
                )
            ]
            invoices = [l for l in ws.link_ids if l.res_model == "account.move"]
            ws.project_count = len(projects)
            ws.engagement_count = len(engagements)
            ws.invoice_count = len(invoices)

    # SIMPLE DISPLAY HELPERS

    def action_open_links(self):
        """Fallback generic action – opens the link list.

        Vertical modules should provide richer actions on their own menus.
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Workspace Links"),
            "res_model": "ipai.workspace.link",
            "view_mode": "tree,form",
            "domain": [("workspace_id", "=", self.id)],
            "context": {"default_workspace_id": self.id},
        }


class WorkspaceLink(models.Model):
    """
    Generic link table: points a workspace at ANY object in Odoo.

    Smart Delta pattern:
    - No proliferation of many2one fields on ipai.workspace
    - Vertical modules consume this for their own dashboards/BI
    """

    _name = "ipai.workspace.link"
    _description = "Workspace Linked Record"
    _rec_name = "display_name"

    workspace_id = fields.Many2one(
        "ipai.workspace",
        string="Workspace",
        required=True,
        ondelete="cascade",
        index=True,
    )

    res_model = fields.Char(
        string="Model Technical Name",
        required=True,
        help="Technical model name, e.g. 'project.project' or 'account.move'.",
    )
    res_id = fields.Integer(
        string="Record ID",
        required=True,
        help="ID of the linked record in the target model.",
    )

    display_name = fields.Char(
        string="Label",
        compute="_compute_display_name",
        store=True,
    )

    link_type = fields.Selection(
        [
            ("project", "Project"),
            ("engagement", "Engagement"),
            ("invoice", "Invoice"),
            ("document", "Document"),
            ("other", "Other"),
        ],
        string="Link Type",
        default="other",
    )

    _sql_constraints = [
        (
            "workspace_res_uniq",
            "unique(workspace_id, res_model, res_id)",
            "This record is already linked to the workspace.",
        ),
    ]

    @api.depends("res_model", "res_id")
    def _compute_display_name(self):
        """Try to resolve the actual record name, but fail gracefully.

        No hard coupling – if the model disappears, we still keep the link row.
        """
        for link in self:
            name = f"{link.res_model},{link.res_id}"
            if link.res_model and link.res_id:
                try:
                    record = (
                        self.env[link.res_model]
                        .sudo()
                        .browse(link.res_id)
                    )
                    if record.exists():
                        name = record.display_name
                except Exception:
                    # Never break on missing model/access error
                    pass
            link.display_name = name

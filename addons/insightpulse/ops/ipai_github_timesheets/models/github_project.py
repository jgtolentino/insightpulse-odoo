# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)


class GitHubProject(models.Model):
    """GitHub Project (Org-level or Repo-level)"""

    _name = "github.project"
    _description = "GitHub Project"
    _rec_name = "title"
    _order = "create_date desc"

    # GitHub Fields
    github_project_id = fields.Integer(
        string="GitHub Project ID",
        required=True,
        index=True,
        help="GitHub Project ID (from API)",
    )

    github_node_id = fields.Char(
        string="GitHub Node ID",
        help="GraphQL Node ID for GitHub Projects V2",
    )

    title = fields.Char(
        string="Project Title",
        required=True,
    )

    description = fields.Text(
        string="Description",
    )

    github_url = fields.Char(
        string="GitHub URL",
        help="Link to GitHub Project",
    )

    project_number = fields.Integer(
        string="Project Number",
        help="Project number in GitHub (e.g., #1, #2)",
    )

    github_state = fields.Selection(
        [
            ("open", "Open"),
            ("closed", "Closed"),
        ],
        string="GitHub State",
        default="open",
    )

    # Financial Fields
    project_budget = fields.Monetary(
        string="Project Budget ($)",
        currency_field="currency_id",
        help="Total allocated budget for this project",
    )

    project_spend = fields.Monetary(
        string="Project Spend ($)",
        currency_field="currency_id",
        compute="_compute_project_spend",
        store=True,
        help="Actual spend from timesheets (auto-calculated)",
    )

    remaining_budget = fields.Monetary(
        string="Remaining Budget",
        currency_field="currency_id",
        compute="_compute_remaining_budget",
        store=True,
    )

    budget_utilization_pct = fields.Float(
        string="Budget Utilization %",
        compute="_compute_budget_utilization",
        store=True,
    )

    expense_type = fields.Selection(
        [
            ("opex_rd", "R&D (OpEx)"),
            ("capex_feature", "Capitalizable Feature (CapEx)"),
            ("opex_maintenance", "Maintenance (OpEx)"),
            ("opex_bugfix", "Bug Fix (OpEx)"),
        ],
        string="Expense Type",
        required=True,
        default="opex_rd",
        help="Classification for financial reporting (CapEx vs OpEx)",
    )

    # Odoo Mapping
    odoo_project_id = fields.Many2one(
        "project.project",
        string="Linked Odoo Project",
        required=True,
        ondelete="cascade",
        help="Odoo project for tracking tasks and timesheets",
    )

    task_ids = fields.One2many(
        "project.task",
        "github_project_id",
        string="Linked Tasks",
    )

    task_count = fields.Integer(
        string="Task Count",
        compute="_compute_task_count",
    )

    timesheet_ids = fields.One2many(
        related="odoo_project_id.timesheet_ids",
        string="Timesheets",
        readonly=True,
    )

    # Metadata
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )

    config_id = fields.Many2one(
        "github.config",
        string="GitHub Config",
        required=True,
        default=lambda self: self.env["github.config"].search([], limit=1),
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    last_synced = fields.Datetime(
        string="Last Synced",
        readonly=True,
    )

    @api.depends("odoo_project_id.timesheet_ids", "odoo_project_id.timesheet_ids.amount")
    def _compute_project_spend(self):
        """Calculate total spend from timesheets"""
        for record in self:
            # Sum of absolute timesheet amounts (costs)
            # Note: In Odoo timesheets, negative amounts are costs
            total_spend = sum(
                abs(line.amount)
                for line in record.odoo_project_id.timesheet_ids
                if line.amount < 0
            )
            record.project_spend = total_spend

    @api.depends("project_budget", "project_spend")
    def _compute_remaining_budget(self):
        """Calculate remaining budget"""
        for record in self:
            record.remaining_budget = record.project_budget - record.project_spend

    @api.depends("project_budget", "project_spend")
    def _compute_budget_utilization(self):
        """Calculate budget utilization percentage"""
        for record in self:
            if record.project_budget > 0:
                record.budget_utilization_pct = (
                    record.project_spend / record.project_budget
                ) * 100
            else:
                record.budget_utilization_pct = 0.0

    @api.depends("task_ids")
    def _compute_task_count(self):
        """Count linked tasks"""
        for record in self:
            record.task_count = len(record.task_ids)

    @api.constrains("project_budget")
    def _check_project_budget(self):
        """Validate budget is positive"""
        for record in self:
            if record.project_budget < 0:
                raise ValidationError(_("Project budget must be positive"))

    def action_view_tasks(self):
        """Open linked tasks"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("GitHub Tasks"),
            "res_model": "project.task",
            "view_mode": "tree,form,kanban",
            "domain": [("github_project_id", "=", self.id)],
            "context": {"default_github_project_id": self.id},
        }

    def action_view_timesheets(self):
        """Open related timesheets"""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Project Timesheets"),
            "res_model": "account.analytic.line",
            "view_mode": "tree,form",
            "domain": [("project_id", "=", self.odoo_project_id.id)],
            "context": {"default_project_id": self.odoo_project_id.id},
        }

    def sync_cost_to_github(self):
        """Sync project spend back to GitHub Projects API"""
        self.ensure_one()

        if not self.config_id.sync_costs_to_github:
            _logger.info("Cost sync to GitHub is disabled")
            return

        try:
            # GitHub Projects V2 uses GraphQL
            # For simplicity, we'll log this and provide the mutation
            # In production, you'd use PyGithub or GraphQL client

            _logger.info(
                "Syncing cost to GitHub Project #%s: Budget=%s, Spend=%s",
                self.project_number,
                self.project_budget,
                self.project_spend,
            )

            # Example GraphQL mutation (would need to be executed):
            mutation = f"""
            mutation {{
              updateProjectV2ItemFieldValue(
                input: {{
                  projectId: "{self.github_node_id}"
                  fieldId: "FIELD_ID_FOR_SPEND"
                  value: {{
                    number: {self.project_spend}
                  }}
                }}
              ) {{
                projectV2Item {{
                  id
                }}
              }}
            }}
            """

            # Log the mutation for manual execution or future implementation
            _logger.debug("GitHub GraphQL mutation: %s", mutation)

            self.write({"last_synced": fields.Datetime.now()})

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Cost Sync Logged"),
                    "message": _(
                        "Project spend: %s\nTo complete sync, use GitHub GraphQL API"
                    )
                    % self.project_spend,
                    "type": "info",
                },
            }

        except Exception as e:
            _logger.error("Failed to sync cost to GitHub: %s", str(e))
            raise ValidationError(_("Cost sync failed: %s") % str(e))

    @api.model
    def _sync_from_github(self, config):
        """Sync GitHub Projects from API"""
        try:
            headers = config.get_github_headers()

            # Fetch org-level projects
            url = f"{config.api_base_url}/orgs/{config.github_org}/projects"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            projects_data = response.json()

            for project in projects_data:
                existing = self.search(
                    [("github_project_id", "=", project["id"])], limit=1
                )

                vals = {
                    "github_project_id": project["id"],
                    "github_node_id": project.get("node_id"),
                    "title": project["name"],
                    "description": project.get("body", ""),
                    "github_url": project["html_url"],
                    "project_number": project["number"],
                    "github_state": project["state"],
                    "config_id": config.id,
                    "last_synced": fields.Datetime.now(),
                }

                if existing:
                    existing.write(vals)
                else:
                    # Create Odoo project if needed
                    if not vals.get("odoo_project_id"):
                        odoo_project = self.env["project.project"].create({
                            "name": f"[GitHub] {project['name']}",
                            "allow_timesheets": True,
                        })
                        vals["odoo_project_id"] = odoo_project.id

                    self.create(vals)

            _logger.info("Synced %d GitHub projects", len(projects_data))

        except Exception as e:
            _logger.error("Failed to sync GitHub projects: %s", str(e))
            raise

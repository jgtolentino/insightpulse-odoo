# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import requests
import logging

_logger = logging.getLogger(__name__)


class GitHubPullRequest(models.Model):
    """GitHub Pull Request"""

    _name = "github.pull.request"
    _description = "GitHub Pull Request"
    _rec_name = "title"
    _order = "github_updated_at desc"

    # GitHub Fields
    github_pr_number = fields.Integer(
        string="PR Number",
        required=True,
        index=True,
    )

    github_pr_id = fields.Integer(
        string="GitHub PR ID",
        required=True,
        index=True,
    )

    title = fields.Char(
        string="Title",
        required=True,
    )

    description = fields.Html(
        string="Description",
    )

    github_url = fields.Char(
        string="GitHub URL",
    )

    github_state = fields.Selection(
        [
            ("open", "Open"),
            ("closed", "Closed"),
            ("merged", "Merged"),
        ],
        string="State",
        required=True,
        default="open",
    )

    github_author = fields.Char(
        string="Author",
    )

    github_created_at = fields.Datetime(
        string="Created at",
    )

    github_updated_at = fields.Datetime(
        string="Updated at",
    )

    github_merged_at = fields.Datetime(
        string="Merged at",
    )

    github_closed_at = fields.Datetime(
        string="Closed at",
    )

    source_branch = fields.Char(
        string="Source Branch",
    )

    target_branch = fields.Char(
        string="Target Branch",
    )

    # Odoo Mapping
    task_id = fields.Many2one(
        "project.task",
        string="Linked Task",
        ondelete="set null",
        help="Odoo task created for this PR",
    )

    github_project_id = fields.Many2one(
        "github.project",
        string="GitHub Project",
        help="GitHub Project this PR belongs to",
    )

    odoo_project_id = fields.Many2one(
        related="github_project_id.odoo_project_id",
        string="Odoo Project",
        store=True,
        readonly=True,
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Assigned Employee",
        help="Odoo employee mapped from GitHub author",
    )

    timesheet_ids = fields.One2many(
        "account.analytic.line",
        "github_pr_id",
        string="Timesheets",
    )

    timesheet_hours = fields.Float(
        string="Logged Hours",
        compute="_compute_timesheet_hours",
        store=True,
    )

    timesheet_cost = fields.Monetary(
        string="Timesheet Cost",
        currency_field="currency_id",
        compute="_compute_timesheet_cost",
        store=True,
    )

    # Prompts
    timesheet_prompted = fields.Boolean(
        string="Timesheet Prompted",
        default=False,
        help="Whether we've posted a timesheet reminder comment",
    )

    timesheet_prompt_date = fields.Datetime(
        string="Prompt Date",
    )

    # Metadata
    config_id = fields.Many2one(
        "github.config",
        string="GitHub Config",
        required=True,
        default=lambda self: self.env["github.config"].search([], limit=1),
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )

    active = fields.Boolean(
        string="Active",
        default=True,
    )

    @api.depends("timesheet_ids", "timesheet_ids.unit_amount")
    def _compute_timesheet_hours(self):
        """Calculate total logged hours"""
        for record in self:
            record.timesheet_hours = sum(
                line.unit_amount for line in record.timesheet_ids
            )

    @api.depends("timesheet_ids", "timesheet_ids.amount")
    def _compute_timesheet_cost(self):
        """Calculate total timesheet cost"""
        for record in self:
            # Timesheet amounts are negative (costs)
            record.timesheet_cost = sum(
                abs(line.amount) for line in record.timesheet_ids
            )

    def action_create_task(self):
        """Create Odoo task for this PR"""
        self.ensure_one()

        if self.task_id:
            raise ValidationError(_("Task already exists for this PR"))

        # Find or create project
        if not self.github_project_id:
            # Use default project from config
            project = self.config_id.default_project_id
            if not project:
                raise ValidationError(
                    _("No GitHub Project or default Odoo project configured")
                )
        else:
            project = self.github_project_id.odoo_project_id

        # Create task
        task = self.env["project.task"].create({
            "name": f"PR #{self.github_pr_number}: {self.title}",
            "description": self.description or "",
            "project_id": project.id,
            "github_pr_id": self.id,
            "github_project_id": self.github_project_id.id if self.github_project_id else False,
            "user_ids": [(6, 0, [self.employee_id.user_id.id])] if self.employee_id and self.employee_id.user_id else [],
        })

        self.write({"task_id": task.id})

        return {
            "type": "ir.actions.act_window",
            "name": _("Odoo Task"),
            "res_model": "project.task",
            "res_id": task.id,
            "view_mode": "form",
            "target": "current",
        }

    def action_prompt_timesheet(self):
        """Post GitHub comment prompting timesheet entry"""
        self.ensure_one()

        if self.github_state != "merged":
            raise ValidationError(_("Can only prompt timesheets for merged PRs"))

        try:
            headers = self.config_id.get_github_headers()

            # Post comment on PR
            comment_url = (
                f"{self.config_id.api_base_url}/repos/"
                f"{self.config_id.github_org}/{self.config_id.github_repo}/"
                f"issues/{self.github_pr_number}/comments"
            )

            task_url = (
                f"{self.env['ir.config_parameter'].sudo().get_param('web.base.url')}"
                f"/web#id={self.task_id.id}&model=project.task&view_type=form"
                if self.task_id
                else "N/A"
            )

            comment_body = f"""## 📝 Timesheet Reminder

Hi @{self.github_author}! This PR has been merged. Please log your time in Odoo:

**Odoo Task**: {task_url}

**Instructions**:
1. Navigate to the Odoo task above
2. Click "Timesheets" tab
3. Log your hours spent on this PR
4. Add a description of work done

**Why?** This helps us:
- Track project costs accurately
- Calculate feature ROI
- Report R&D expenses (CapEx/OpEx)

---
*This is an automated reminder from InsightPulse GitHub Integration*
"""

            response = requests.post(
                comment_url,
                headers=headers,
                json={"body": comment_body},
                timeout=10,
            )
            response.raise_for_status()

            self.write({
                "timesheet_prompted": True,
                "timesheet_prompt_date": fields.Datetime.now(),
            })

            _logger.info(
                "Posted timesheet prompt on PR #%s", self.github_pr_number
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Timesheet Prompt Posted"),
                    "message": _("Comment posted on GitHub PR #%s")
                    % self.github_pr_number,
                    "type": "success",
                },
            }

        except Exception as e:
            _logger.error("Failed to post timesheet prompt: %s", str(e))
            raise ValidationError(_("Failed to post prompt: %s") % str(e))

    @api.model
    def _sync_from_github(self, config):
        """Sync PRs from GitHub"""
        try:
            headers = config.get_github_headers()

            # Fetch recent PRs (last 30 days)
            url = (
                f"{config.api_base_url}/repos/"
                f"{config.github_org}/{config.github_repo}/pulls"
            )
            params = {
                "state": "all",
                "sort": "updated",
                "direction": "desc",
                "per_page": 100,
            }

            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()

            prs_data = response.json()

            for pr in prs_data:
                existing = self.search(
                    [("github_pr_id", "=", pr["id"])], limit=1
                )

                # Determine state
                if pr.get("merged_at"):
                    state = "merged"
                elif pr["state"] == "closed":
                    state = "closed"
                else:
                    state = "open"

                # Map GitHub author to Odoo employee (by email or username)
                employee = self._find_employee_by_github_username(
                    pr["user"]["login"]
                )

                vals = {
                    "github_pr_number": pr["number"],
                    "github_pr_id": pr["id"],
                    "title": pr["title"],
                    "description": pr.get("body", ""),
                    "github_url": pr["html_url"],
                    "github_state": state,
                    "github_author": pr["user"]["login"],
                    "github_created_at": pr["created_at"],
                    "github_updated_at": pr["updated_at"],
                    "github_merged_at": pr.get("merged_at"),
                    "github_closed_at": pr.get("closed_at"),
                    "source_branch": pr["head"]["ref"],
                    "target_branch": pr["base"]["ref"],
                    "employee_id": employee.id if employee else False,
                    "config_id": config.id,
                }

                if existing:
                    existing.write(vals)

                    # Auto-prompt timesheet if newly merged
                    if (
                        state == "merged"
                        and not existing.timesheet_prompted
                        and config.prompt_timesheet_on_merge
                    ):
                        existing.action_prompt_timesheet()
                else:
                    pr_record = self.create(vals)

                    # Auto-create task if enabled
                    if config.auto_create_tasks:
                        pr_record.action_create_task()

            _logger.info("Synced %d GitHub PRs", len(prs_data))

        except Exception as e:
            _logger.error("Failed to sync GitHub PRs: %s", str(e))
            raise

    @api.model
    def _find_employee_by_github_username(self, github_username):
        """Find Odoo employee by GitHub username"""
        # Try to find by work_email matching GitHub username
        # In production, you'd maintain a mapping table
        employee = self.env["hr.employee"].search(
            [
                "|",
                ("work_email", "ilike", github_username),
                ("name", "ilike", github_username),
            ],
            limit=1,
        )
        return employee

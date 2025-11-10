# Copyright 2025 InsightPulse AI
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

from odoo import fields, models


class PPMRoadmap(models.Model):
    _name = "ppm.roadmap"
    _description = "PPM Roadmap"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence, name"

    name = fields.Char(
        string="Milestone Name",
        required=True,
        tracking=True,
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    program_id = fields.Many2one(
        comodel_name="ppm.program",
        string="Program",
        required=True,
        ondelete="cascade",
    )
    project_id = fields.Many2one(
        comodel_name="project.project",
        string="Project",
        ondelete="cascade",
    )
    milestone_type = fields.Selection(
        selection=[
            ("planning", "Planning"),
            ("development", "Development"),
            ("testing", "Testing"),
            ("deployment", "Deployment"),
            ("review", "Review"),
        ],
        string="Type",
        required=True,
        default="planning",
        tracking=True,
    )
    target_date = fields.Date(
        string="Target Date",
        required=True,
        tracking=True,
    )
    actual_date = fields.Date(
        string="Actual Date",
        tracking=True,
    )
    status = fields.Selection(
        selection=[
            ("not_started", "Not Started"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("delayed", "Delayed"),
        ],
        default="not_started",
        required=True,
        tracking=True,
    )
    progress = fields.Float(
        string="Progress %",
        default=0.0,
        tracking=True,
    )
    owner_id = fields.Many2one(
        comodel_name="res.users",
        string="Owner",
        tracking=True,
    )
    description = fields.Text(
        string="Description",
    )
    notes = fields.Text(
        string="Notes",
    )

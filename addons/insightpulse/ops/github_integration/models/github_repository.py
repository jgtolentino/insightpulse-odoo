# -*- coding: utf-8 -*-
"""GitHub repository model."""

from odoo import fields, models


class GitHubRepository(models.Model):
    """Track GitHub repositories."""

    _name = "github.repository"
    _description = "GitHub Repository"

    name = fields.Char("Repository Name", required=True)
    full_name = fields.Char("Full Name (owner/repo)", required=True)
    description = fields.Text("Description")
    url = fields.Char("URL")

    private = fields.Boolean("Private", default=False)
    fork = fields.Boolean("Is Fork", default=False)

    default_branch = fields.Char("Default Branch", default="main")
    language = fields.Char("Primary Language")

    stars_count = fields.Integer("Stars")
    forks_count = fields.Integer("Forks")
    open_issues_count = fields.Integer("Open Issues")

    created_at = fields.Datetime("Created At")
    updated_at = fields.Datetime("Updated At")
    pushed_at = fields.Datetime("Last Push")

    active = fields.Boolean("Active", default=True)

    _sql_constraints = [
        ("unique_repo", "unique(full_name)", "Repository must be unique!")
    ]

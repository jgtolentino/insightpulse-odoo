# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta


class ProjectProject(models.Model):
    _inherit = 'project.project'

    # Clarity Identification
    clarity_id = fields.Char(
        string="Clarity ID",
        required=True,
        copy=False,
        index=True,
        help="Unique Clarity project identifier (e.g., PRJ-2025-001)"
    )

    # Health & Status Indicators
    health_status = fields.Selection([
        ('green', 'Green - On Track'),
        ('yellow', 'Yellow - At Risk'),
        ('red', 'Red - Critical Issues')
    ], string="Health Status", default='green', tracking=True, required=True)

    overall_status = fields.Selection([
        ('on_track', 'On Track'),
        ('at_risk', 'At Risk'),
        ('off_track', 'Off Track')
    ], string="Overall Status", compute='_compute_overall_status', store=True)

    # Baseline Dates (Original Plan)
    baseline_start = fields.Date(
        string="Baseline Start",
        help="Original planned start date from approved baseline"
    )

    baseline_finish = fields.Date(
        string="Baseline Finish",
        help="Original planned finish date from approved baseline"
    )

    # Actual Dates
    actual_start = fields.Date(
        string="Actual Start",
        help="Date project actually started"
    )

    actual_finish = fields.Date(
        string="Actual Finish",
        help="Date project actually finished"
    )

    # Variance Calculations
    variance_start = fields.Integer(
        string="Start Variance (days)",
        compute='_compute_variances',
        store=True,
        help="Days difference between baseline and actual/current start"
    )

    variance_finish = fields.Integer(
        string="Finish Variance (days)",
        compute='_compute_variances',
        store=True,
        help="Days difference between baseline and actual/planned finish"
    )

    # Phase Rollup Fields
    phase_count = fields.Integer(
        string="Number of Phases",
        compute='_compute_phase_stats'
    )

    milestone_count = fields.Integer(
        string="Number of Milestones",
        compute='_compute_milestone_stats'
    )

    critical_milestone_count = fields.Integer(
        string="Critical Milestones",
        compute='_compute_milestone_stats',
        help="Milestones approaching deadline (< 7 days)"
    )

    # Progress Metrics
    overall_progress = fields.Float(
        string="Overall Progress (%)",
        compute='_compute_overall_progress',
        help="Weighted progress across all phases"
    )

    @api.depends('health_status', 'variance_finish')
    def _compute_overall_status(self):
        """Compute overall status based on health and schedule variance"""
        for project in self:
            if project.health_status == 'red' or (project.variance_finish and project.variance_finish > 14):
                project.overall_status = 'off_track'
            elif project.health_status == 'yellow' or (project.variance_finish and project.variance_finish > 7):
                project.overall_status = 'at_risk'
            else:
                project.overall_status = 'on_track'

    @api.depends('date_start', 'baseline_start', 'actual_start', 'date', 'baseline_finish', 'actual_finish')
    def _compute_variances(self):
        """Calculate variance between baseline and actual/current dates"""
        for project in self:
            # Start Variance
            if project.baseline_start:
                compare_start = project.actual_start or project.date_start or fields.Date.today()
                delta = (compare_start - project.baseline_start).days
                project.variance_start = delta
            else:
                project.variance_start = 0

            # Finish Variance
            if project.baseline_finish:
                compare_finish = project.actual_finish or project.date or fields.Date.today()
                delta = (compare_finish - project.baseline_finish).days
                project.variance_finish = delta
            else:
                project.variance_finish = 0

    def _compute_phase_stats(self):
        """Count phases in project"""
        for project in self:
            phases = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('is_phase', '=', True)
            ])
            project.phase_count = len(phases)

    def _compute_milestone_stats(self):
        """Count milestones and identify critical ones"""
        for project in self:
            milestones = self.env['project.milestone'].search([
                ('project_id', '=', project.id)
            ])
            project.milestone_count = len(milestones)

            # Critical milestones (deadline within 7 days, not reached)
            today = fields.Date.today()
            critical = milestones.filtered(
                lambda m: m.deadline and m.deadline <= today + timedelta(days=7) and not m.is_reached
            )
            project.critical_milestone_count = len(critical)

    def _compute_overall_progress(self):
        """Calculate weighted progress from all phases"""
        for project in self:
            phases = self.env['project.task'].search([
                ('project_id', '=', project.id),
                ('is_phase', '=', True)
            ])
            if phases:
                project.overall_progress = sum(phases.mapped('phase_progress')) / len(phases)
            else:
                project.overall_progress = 0.0

    def action_view_phases(self):
        """Open phases view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Phases',
            'res_model': 'project.task',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id), ('is_phase', '=', True)],
            'context': {'default_project_id': self.id, 'default_is_phase': True}
        }

    def action_view_milestones(self):
        """Open milestones view"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Milestones',
            'res_model': 'project.milestone',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id)],
            'context': {'default_project_id': self.id}
        }

    def action_set_baseline(self):
        """Set current plan as baseline"""
        for project in self:
            project.write({
                'baseline_start': project.date_start or fields.Date.today(),
                'baseline_finish': project.date or fields.Date.today() + timedelta(days=90),
            })
        return True

    def action_health_check(self):
        """Open wizard to update health status with notes"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Update Health Status',
            'res_model': 'project.health.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_project_id': self.id}
        }

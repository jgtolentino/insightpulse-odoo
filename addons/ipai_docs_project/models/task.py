from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    doc_ids = fields.Many2many(
        "ipai.doc",
        "ipai_doc_task_rel",
        "task_id",
        "doc_id",
        string="Documents",
    )
    doc_count = fields.Integer(
        string="Documents Count",
        compute="_compute_doc_count",
    )

    def _compute_doc_count(self):
        for task in self:
            task.doc_count = len(task.doc_ids)

    def action_view_docs(self):
        self.ensure_one()
        action = self.env.ref("ipai_docs.action_ipai_docs").read()[0]
        action["domain"] = [("id", "in", self.doc_ids.ids)]
        action["context"] = {
            "default_doc_type": "page",
        }
        return action

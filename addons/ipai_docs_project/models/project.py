from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    doc_ids = fields.Many2many(
        "ipai.doc",
        "ipai_doc_project_rel",
        "project_id",
        "doc_id",
        string="Documents",
    )
    doc_count = fields.Integer(
        string="Documents Count",
        compute="_compute_doc_count",
    )

    def _compute_doc_count(self):
        for project in self:
            project.doc_count = len(project.doc_ids)

    def action_view_docs(self):
        self.ensure_one()
        action = self.env.ref("ipai_docs.action_ipai_docs").read()[0]
        action["domain"] = [("id", "in", self.doc_ids.ids)]
        action["context"] = {
            "default_parent_id": False,
            "default_doc_type": "page",
        }
        return action

    def write(self, vals):
        res = super().write(vals)
        if "doc_ids" in vals:
            self._sync_doc_followers()
        return res

    def _sync_doc_followers(self):
        """Subscribe project members to linked docs."""
        for project in self:
            # Get all linked docs
            docs = project.doc_ids
            # Get project followers
            partners = project.message_partner_ids
            for doc in docs:
                doc.message_subscribe(partner_ids=partners.ids)

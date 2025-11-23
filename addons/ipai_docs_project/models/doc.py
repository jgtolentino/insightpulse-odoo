from odoo import fields, models


class IpaiDoc(models.Model):
    _inherit = "ipai.doc"

    project_ids = fields.Many2many(
        "project.project",
        "ipai_doc_project_rel",
        "doc_id",
        "project_id",
        string="Projects",
    )

    task_ids = fields.Many2many(
        "project.task",
        "ipai_doc_task_rel",
        "doc_id",
        "task_id",
        string="Tasks",
    )

    def write(self, vals):
        res = super().write(vals)
        if "project_ids" in vals:
            self._sync_project_followers()
        return res

    def _sync_project_followers(self):
        """Subscribe project members to the doc."""
        for doc in self:
            partners = doc.project_ids.mapped("message_partner_ids")
            # Odoo's message_subscribe is idempotent, but we can filter if needed
            doc.message_subscribe(partner_ids=partners.ids)

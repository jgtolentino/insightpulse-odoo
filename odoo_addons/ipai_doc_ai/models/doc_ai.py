from odoo import models, fields

class IpaiDocAiJob(models.Model):
    _name = "ipai.docai.job"
    _description = "Document AI job"

    state = fields.Selection([
        ("new","New"),
        ("processing","Processing"),
        ("done","Done"),
        ("error","Error")
    ], default="new")
    src_attachment_id = fields.Many2one("ir.attachment")
    result_json = fields.Text()

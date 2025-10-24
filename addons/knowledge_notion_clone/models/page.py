from odoo import fields, models

class KnowledgePage(models.Model):
    _name = "knowledge.page"
    _description = "Notion-like Page"
    _order = "is_favorite desc, name"

    name = fields.Char(required=True)
    parent_id = fields.Many2one("knowledge.page", ondelete="cascade")
    child_ids = fields.One2many("knowledge.page","parent_id")
    company_id = fields.Many2one("res.company", default=lambda s: s.env.company)
    owner_id = fields.Many2one("res.users", default=lambda s: s.env.user)
    is_favorite = fields.Boolean(default=False)
    icon = fields.Char()
    cover_url = fields.Char()
    block_ids = fields.One2many("knowledge.block","page_id", copy=True)

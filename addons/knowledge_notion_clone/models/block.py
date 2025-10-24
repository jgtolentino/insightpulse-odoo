from odoo import fields, models

BLOCK_TYPES = [
    ("text","Text"),("h1","Heading 1"),("h2","Heading 2"),
    ("todo","To-Do"),("bulleted","Bulleted List"),("numbered","Numbered List"),
    ("divider","Divider"),("callout","Callout"),("database","Database Embed")
]

class KnowledgeBlock(models.Model):
    _name = "knowledge.block"
    _description = "Page Blocks"
    _order = "sequence,id"

    page_id = fields.Many2one("knowledge.page", required=True, ondelete="cascade")
    sequence = fields.Integer(default=16)
    type = fields.Selection(BLOCK_TYPES, required=True, default="text")
    text = fields.Text()
    checked = fields.Boolean()
    db_id = fields.Many2one("knowledge.database")

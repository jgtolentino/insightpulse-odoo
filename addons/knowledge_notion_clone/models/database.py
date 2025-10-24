from odoo import fields, models

VIEW_TYPES = [("table","Table"),("board","Board"),("gallery","Gallery"),("calendar","Calendar")]

class KnowledgeDatabase(models.Model):
    _name = "knowledge.database"
    _description = "Notion-like Database"

    name = fields.Char(required=True)
    description = fields.Text()
    view_type = fields.Selection(VIEW_TYPES, default="table")
    record_ids = fields.One2many("knowledge.property","database_id")

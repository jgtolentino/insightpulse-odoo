from odoo import fields, models

class KnowledgeProperty(models.Model):
    _name = "knowledge.property"
    _description = "Database Rows / Properties"

    database_id = fields.Many2one("knowledge.database", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    props = fields.Json(default=dict)
    assignees = fields.Many2many("res.users")
    due_date = fields.Date()
    done = fields.Boolean()

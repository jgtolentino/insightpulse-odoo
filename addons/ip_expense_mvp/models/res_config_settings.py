from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ip_ai_ocr_url = fields.Char(
        string="AI OCR URL",
        config_parameter='ip.ai_ocr_url',
        default="http://127.0.0.1:8100/v1/ocr/receipt"
    )
    ip_supabase_url = fields.Char(
        string="Supabase URL",
        config_parameter='ip.supabase_url'
    )
    ip_supabase_key = fields.Char(
        string="Supabase Service Key",
        config_parameter='ip.supabase_service_key'
    )

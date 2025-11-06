"""Settings for AI OCR and Supabase integration."""
from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    """Add AI OCR and Supabase settings."""

    _inherit = 'res.config.settings'

    # AI Inference Hub
    ip_ai_ocr_url = fields.Char(
        string="AI OCR Endpoint URL",
        config_parameter='ip_expense_mvp.ai_ocr_url',
        default='http://127.0.0.1:8100/v1/ocr/receipt',
        help="Full URL to AI Inference Hub OCR endpoint (e.g., http://127.0.0.1:8100/v1/ocr/receipt)"
    )

    # Supabase
    ip_supabase_url = fields.Char(
        string="Supabase URL",
        config_parameter='ip_expense_mvp.supabase_url',
        help="Supabase project URL (e.g., https://xxx.supabase.co)"
    )

    ip_supabase_service_key = fields.Char(
        string="Supabase Service Role Key",
        config_parameter='ip_expense_mvp.supabase_service_key',
        help="Service role key (server-side only, NEVER expose to client). Used for analytics.upsert_ip_ocr_receipt RPC."
    )

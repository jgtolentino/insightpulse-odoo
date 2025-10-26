from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class MicroservicesHealthLog(models.Model):
    _name = 'microservices.health.log'
    _description = 'Microservices Health Check Log'
    _order = 'create_date desc'

    config_id = fields.Many2one(
        'microservices.config',
        string='Configuration',
        required=True,
        ondelete='cascade'
    )
    component = fields.Selection([
        ('ocr', 'OCR Service'),
        ('llm', 'LLM Service'),
        ('agent', 'Agent Service')
    ], string='Component', required=True)
    status = fields.Selection([
        ('healthy', 'Healthy'),
        ('unhealthy', 'Unhealthy'),
        ('error', 'Error'),
        ('unknown', 'Unknown')
    ], string='Status', required=True)
    response_time = fields.Float(
        string='Response Time (s)',
        help='Response time in seconds'
    )
    error_message = fields.Text(
        string='Error Message',
        help='Detailed error message if any'
    )
    total_check_time = fields.Float(
        string='Total Check Time (s)',
        help='Total time taken for the health check'
    )
    create_date = fields.Datetime(
        string='Check Date',
        default=fields.Datetime.now
    )

    @api.model
    def cleanup_old_logs(self, days=30):
        """Clean up health logs older than specified days"""
        cutoff_date = fields.Datetime.to_string(
            datetime.now() - timedelta(days=days)
        )
        old_logs = self.search([('create_date', '<', cutoff_date)])
        deleted_count = len(old_logs)
        old_logs.unlink()
        _logger.info(f"Cleaned up {deleted_count} old health logs")
        return deleted_count

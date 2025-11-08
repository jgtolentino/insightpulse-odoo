# -*- coding: utf-8 -*-
import logging
import requests
import json
from datetime import datetime, timedelta
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ProcessIntelMixin(models.AbstractModel):
    """Mixin for Process Intelligence capabilities"""
    _name = 'process.intel.mixin'
    _description = 'Process Intelligence Mixin'

    x_pi_last_analysis = fields.Datetime(
        string='Last PI Analysis',
        readonly=True,
        help='Timestamp of last process intelligence analysis'
    )
    x_pi_diagram_url = fields.Char(
        string='Process Diagram URL',
        readonly=True,
        help='URL to the generated process diagram'
    )
    x_pi_conformance_rate = fields.Float(
        string='Conformance Rate (%)',
        readonly=True,
        digits=(5, 2),
        help='Process conformance rate from variant analysis'
    )
    x_pi_top_bottleneck = fields.Char(
        string='Top Bottleneck',
        readonly=True,
        help='Activity with highest impact bottleneck'
    )
    x_pi_bottleneck_wait_hours = fields.Float(
        string='Bottleneck Wait (hours)',
        readonly=True,
        digits=(8, 2),
        help='P90 wait time for top bottleneck in hours'
    )
    x_pi_analysis_data = fields.Json(
        string='Analysis Data',
        readonly=True,
        help='Full JSON response from process intelligence analysis'
    )

    def _get_pi_api_base(self):
        """Get Process Intelligence API base URL"""
        return self.env['ir.config_parameter'].sudo().get_param(
            'ipai_process_intel.api_base',
            'http://process-intel-api:8090'
        )

    def _get_agent_gateway_base(self):
        """Get Agent Gateway base URL"""
        return self.env['ir.config_parameter'].sudo().get_param(
            'ipai_process_intel.agent_gateway_base',
            'http://agent-gateway:8080'
        )

    def _get_pi_process_id(self):
        """Override to provide process ID for analysis"""
        raise NotImplementedError("Subclass must implement _get_pi_process_id()")

    def _get_pi_process_type(self):
        """Override to provide process type (PROCURE_TO_PAY, ORDER_TO_CASH, etc)"""
        raise NotImplementedError("Subclass must implement _get_pi_process_type()")

    def _get_pi_date_range(self):
        """Get date range for analysis (default: last 30 days to today)"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        return f"{start_date.isoformat()}/{end_date.isoformat()}"

    def action_analyze_process_intelligence(self):
        """Trigger process intelligence analysis"""
        self.ensure_one()

        try:
            process_id = self._get_pi_process_id()
            process_type = self._get_pi_process_type()
            date_range = self._get_pi_date_range()

            # Call Agent Gateway (which orchestrates PI API)
            gateway_url = f"{self._get_agent_gateway_base()}/agent/pi/{process_type.lower()}"

            payload = {
                'process_id': process_id,
                'date_range': date_range,
                'process_type': process_type,
            }

            _logger.info(f"Triggering PI analysis: {payload}")

            response = requests.post(
                gateway_url,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            # Update record with results
            self.write({
                'x_pi_last_analysis': fields.Datetime.now(),
                'x_pi_conformance_rate': result.get('conformance_rate', 0.0),
                'x_pi_top_bottleneck': result.get('top_bottleneck', {}).get('activity', ''),
                'x_pi_bottleneck_wait_hours': result.get('top_bottleneck', {}).get('wait_hours', 0.0),
                'x_pi_diagram_url': result.get('diagram_url', ''),
                'x_pi_analysis_data': result,
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Process Intelligence Analysis Complete'),
                    'message': _(
                        'Conformance Rate: %.1f%%\n'
                        'Top Bottleneck: %s (%.1f hours P90 wait)'
                    ) % (
                        result.get('conformance_rate', 0.0),
                        result.get('top_bottleneck', {}).get('activity', 'N/A'),
                        result.get('top_bottleneck', {}).get('wait_hours', 0.0),
                    ),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.RequestException as e:
            _logger.error(f"PI analysis failed: {str(e)}")
            raise UserError(_(
                'Process Intelligence analysis failed.\n'
                'Error: %s\n\n'
                'Please check that the Agent Gateway and PI API are running.'
            ) % str(e))
        except Exception as e:
            _logger.exception("Unexpected error during PI analysis")
            raise UserError(_('Unexpected error: %s') % str(e))

    def action_view_process_diagram(self):
        """Open process diagram in new tab"""
        self.ensure_one()

        if not self.x_pi_diagram_url:
            raise UserError(_('No process diagram available. Run analysis first.'))

        return {
            'type': 'ir.actions.act_url',
            'url': self.x_pi_diagram_url,
            'target': 'new',
        }

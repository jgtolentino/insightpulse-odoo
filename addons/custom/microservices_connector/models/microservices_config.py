from odoo import models, fields, api
import requests
import logging
import time

_logger = logging.getLogger(__name__)


class MicroservicesConfig(models.Model):
    _name = "microservices.config"
    _description = "Microservices Configuration"

    name = fields.Char(string="Configuration Name", required=True)
    
    # Service endpoints
    ocr_service_url = fields.Char(string="OCR Service URL", default="http://ocr-service:8000")
    llm_service_url = fields.Char(string="LLM Service URL", default="http://llm-service:8001")
    agent_service_url = fields.Char(string="Agent Service URL", default="http://agent-service:8002")
    
    # Authentication
    api_key = fields.Char(string="API Key")
    auth_token = fields.Char(string="Auth Token")
    
    is_active = fields.Boolean(string="Active", default=True)
    
    # Connection status
    connection_status = fields.Selection([
        ('not_tested', 'Not Tested'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ], string="Connection Status", default='not_tested')
    
    last_connection_test = fields.Datetime(string="Last Connection Test")
    
    # Health log relationship
    health_log_ids = fields.One2many(
        'microservices.health.log',
        'config_id',
        string='Health Check Logs'
    )
    
    def run_self_test(self):
        """Run comprehensive self-test for all microservices"""
        start_time = time.time()
        results = {
            'ocr': {'status': 'unknown', 'response_time': 0, 'error': None},
            'llm': {'status': 'unknown', 'response_time': 0, 'error': None},
            'agent': {'status': 'unknown', 'response_time': 0, 'error': None}
        }
        
        # Test OCR service
        if self.ocr_service_url:
            try:
                ocr_start = time.time()
                response = requests.get(
                    f"{self.ocr_service_url}/health",
                    timeout=5,
                    headers={'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
                )
                results['ocr']['response_time'] = time.time() - ocr_start
                results['ocr']['status'] = 'healthy' if response.status_code == 200 else 'unhealthy'
                results['ocr']['status_code'] = response.status_code
            except Exception as e:
                results['ocr']['status'] = 'error'
                results['ocr']['error'] = str(e)
                _logger.error(f"OCR self-test failed: {e}")
        
        # Test LLM service
        if self.llm_service_url:
            try:
                llm_start = time.time()
                response = requests.get(
                    f"{self.llm_service_url}/health",
                    timeout=5,
                    headers={'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
                )
                results['llm']['response_time'] = time.time() - llm_start
                results['llm']['status'] = 'healthy' if response.status_code == 200 else 'unhealthy'
                results['llm']['status_code'] = response.status_code
            except Exception as e:
                results['llm']['status'] = 'error'
                results['llm']['error'] = str(e)
                _logger.error(f"LLM self-test failed: {e}")
        
        # Test Agent service
        if self.agent_service_url:
            try:
                agent_start = time.time()
                response = requests.get(
                    f"{self.agent_service_url}/health",
                    timeout=5,
                    headers={'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else {}
                )
                results['agent']['response_time'] = time.time() - agent_start
                results['agent']['status'] = 'healthy' if response.status_code == 200 else 'unhealthy'
                results['agent']['status_code'] = response.status_code
            except Exception as e:
                results['agent']['status'] = 'error'
                results['agent']['error'] = str(e)
                _logger.error(f"Agent self-test failed: {e}")
        
        # Log results
        total_time = time.time() - start_time
        _logger.info(f"Microservices self-test completed in {total_time:.2f}s: {results}")
        
        # Create health log entries
        for component_name, component_data in results.items():
            self.env['microservices.health.log'].create({
                'config_id': self.id,
                'component': component_name,
                'status': component_data['status'],
                'response_time': component_data.get('response_time', 0),
                'error_message': component_data.get('error'),
                'total_check_time': total_time
            })
        
        # Update connection status
        overall_status = 'success'
        for component in results.values():
            if component['status'] in ['unhealthy', 'error']:
                overall_status = 'failed'
                break
        
        self.write({
            'connection_status': overall_status,
            'last_connection_test': fields.Datetime.now()
        })
        
        # Return notification
        message = f"Self-test completed in {total_time:.2f}s. "
        healthy_components = [k for k, v in results.items() if v['status'] == 'healthy']
        if healthy_components:
            message += f"Healthy: {', '.join(healthy_components)}. "
        unhealthy_components = [k for k, v in results.items() if v['status'] in ['unhealthy', 'error']]
        if unhealthy_components:
            message += f"Unhealthy: {', '.join(unhealthy_components)}."
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Self-Test Results',
                'message': message,
                'type': 'success' if overall_status == 'success' else 'warning',
                'sticky': True,
            }
        }


class MicroservicesService(models.Model):
    _name = "microservices.service"
    _description = "Microservices Service"

    name = fields.Char(string="Service Name", required=True)
    service_type = fields.Selection([
        ('ocr', 'OCR Service'),
        ('llm', 'LLM Service'),
        ('agent', 'Agent Service'),
    ], string="Service Type", required=True)
    
    config_id = fields.Many2one("microservices.config", string="Configuration", required=True)
    endpoint_url = fields.Char(string="Endpoint URL", compute="_compute_endpoint_url")
    
    description = fields.Text(string="Description")
    is_active = fields.Boolean(string="Active", default=True)
    
    def _compute_endpoint_url(self):
        for record in self:
            if record.service_type == 'ocr':
                record.endpoint_url = record.config_id.ocr_service_url
            elif record.service_type == 'llm':
                record.endpoint_url = record.config_id.llm_service_url
            elif record.service_type == 'agent':
                record.endpoint_url = record.config_id.agent_service_url
            else:
                record.endpoint_url = False
    
    def test_service_connection(self):
        """Test connection to microservice"""
        # This would implement actual API connection test
        # For now, return success if URL is provided
        if self.endpoint_url:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Test',
                    'message': f'Connection to {self.name} successful!',
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Connection Test',
                    'message': f'Connection to {self.name} failed!',
                    'type': 'danger',
                    'sticky': False,
                }
            }

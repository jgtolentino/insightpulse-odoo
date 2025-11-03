# -*- coding: utf-8 -*-
import json
import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class ConnectionEndpoint(models.Model):
    _name = 'insightpulse.connection.endpoint'
    _description = 'Connection Endpoint'
    _order = 'sequence, name'

    name = fields.Char(string='Connection Name', required=True, help='Display name for this connection')
    sequence = fields.Integer(string='Sequence', default=10)
    active = fields.Boolean(string='Active', default=True)
    
    # Endpoint Configuration
    endpoint_type = fields.Selection([
        ('supabase', 'Supabase'),
        ('odoo', 'Odoo Database'),
        ('superset', 'Apache Superset'),
        ('mcp', 'MCP Server'),
        ('postgres', 'PostgreSQL'),
        ('api', 'REST API'),
        ('other', 'Other'),
    ], string='Connection Type', required=True, default='supabase')
    
    base_url = fields.Char(string='Base URL', help='Base URL or host for the connection')
    port = fields.Integer(string='Port', help='Connection port (if applicable)')
    database_name = fields.Char(string='Database Name', help='Database name (for DB connections)')
    username = fields.Char(string='Username')
    password = fields.Char(string='Password', help='Stored securely')
    api_key = fields.Char(string='API Key / Token', help='API key or auth token')
    
    # Advanced Configuration
    use_ssl = fields.Boolean(string='Use SSL/TLS', default=True)
    extra_params = fields.Text(string='Extra Parameters (JSON)', help='Additional connection parameters as JSON')
    
    # Connection String & Environment Variables
    connection_string = fields.Text(string='Connection String', compute='_compute_connection_string', store=True)
    env_vars = fields.Text(string='Environment Variables', compute='_compute_env_vars', store=True)
    docker_compose_snippet = fields.Text(string='Docker Compose Snippet', compute='_compute_docker_compose_snippet', store=True)
    
    # Status & Monitoring
    last_test_date = fields.Datetime(string='Last Test Date')
    last_test_result = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('untested', 'Not Tested'),
    ], string='Last Test Result', default='untested')
    last_test_message = fields.Text(string='Last Test Message')
    connection_count = fields.Integer(string='Active Connections', default=0, help='Number of active connections using this endpoint')
    
    # Documentation & Notes
    description = fields.Html(string='Description', help='Documentation for this connection')
    notes = fields.Text(string='Internal Notes')
    
    # Computed Fields for UI Display
    color = fields.Integer(string='Color Index', compute='_compute_color', store=True)
    icon = fields.Char(string='Icon', compute='_compute_icon', store=True)
    
    @api.depends('endpoint_type')
    def _compute_color(self):
        """Assign colors based on endpoint type"""
        color_map = {
            'supabase': 3,  # Green
            'odoo': 4,      # Blue
            'superset': 2,  # Orange
            'mcp': 5,       # Purple
            'postgres': 1,  # Red
            'api': 6,       # Cyan
            'other': 0,     # Gray
        }
        for record in self:
            record.color = color_map.get(record.endpoint_type, 0)
    
    @api.depends('endpoint_type')
    def _compute_icon(self):
        """Assign icons based on endpoint type"""
        icon_map = {
            'supabase': 'fa-database',
            'odoo': 'fa-odoo',
            'superset': 'fa-chart-line',
            'mcp': 'fa-server',
            'postgres': 'fa-database',
            'api': 'fa-plug',
            'other': 'fa-link',
        }
        for record in self:
            record.icon = icon_map.get(record.endpoint_type, 'fa-link')
    
    @api.depends('endpoint_type', 'base_url', 'port', 'database_name', 'username', 'password', 'use_ssl')
    def _compute_connection_string(self):
        """Generate connection string based on endpoint type"""
        for record in self:
            if record.endpoint_type == 'supabase':
                protocol = 'postgresql'
                host = record.base_url or ''
                port = record.port or 5432
                db = record.database_name or 'postgres'
                user = record.username or 'postgres'
                pwd = record.password or ''
                record.connection_string = f"{protocol}://{user}:{pwd}@{host}:{port}/{db}"
            
            elif record.endpoint_type == 'odoo':
                protocol = 'postgresql'
                host = record.base_url or 'localhost'
                port = record.port or 5432
                db = record.database_name or 'odoo19'
                user = record.username or 'odoo'
                pwd = record.password or ''
                record.connection_string = f"{protocol}://{user}:{pwd}@{host}:{port}/{db}"
            
            elif record.endpoint_type == 'superset':
                protocol = 'https' if record.use_ssl else 'http'
                host = record.base_url or ''
                port = f":{record.port}" if record.port else ''
                record.connection_string = f"{protocol}://{host}{port}"
            
            elif record.endpoint_type == 'mcp':
                protocol = 'wss' if record.use_ssl else 'ws'
                host = record.base_url or ''
                port = f":{record.port}" if record.port else ''
                record.connection_string = f"{protocol}://{host}{port}"
            
            elif record.endpoint_type == 'postgres':
                protocol = 'postgresql'
                host = record.base_url or 'localhost'
                port = record.port or 5432
                db = record.database_name or 'postgres'
                user = record.username or 'postgres'
                pwd = record.password or ''
                record.connection_string = f"{protocol}://{user}:{pwd}@{host}:{port}/{db}"
            
            elif record.endpoint_type == 'api':
                protocol = 'https' if record.use_ssl else 'http'
                host = record.base_url or ''
                port = f":{record.port}" if record.port else ''
                record.connection_string = f"{protocol}://{host}{port}"
            
            else:
                record.connection_string = ''
    
    @api.depends('name', 'endpoint_type', 'connection_string', 'api_key', 'username', 'password')
    def _compute_env_vars(self):
        """Generate environment variables for .env file"""
        for record in self:
            env_lines = []
            var_prefix = record.name.upper().replace(' ', '_').replace('-', '_')
            
            if record.connection_string:
                env_lines.append(f"{var_prefix}_URL=\"{record.connection_string}\"")
            if record.api_key:
                env_lines.append(f"{var_prefix}_API_KEY=\"{record.api_key}\"")
            if record.username:
                env_lines.append(f"{var_prefix}_USERNAME=\"{record.username}\"")
            if record.password:
                env_lines.append(f"{var_prefix}_PASSWORD=\"{record.password}\"")
            if record.database_name:
                env_lines.append(f"{var_prefix}_DATABASE=\"{record.database_name}\"")
            if record.base_url:
                env_lines.append(f"{var_prefix}_HOST=\"{record.base_url}\"")
            if record.port:
                env_lines.append(f"{var_prefix}_PORT={record.port}")
            
            record.env_vars = '\n'.join(env_lines)
    
    @api.depends('name', 'endpoint_type', 'connection_string', 'port')
    def _compute_docker_compose_snippet(self):
        """Generate Docker Compose service snippet"""
        for record in self:
            var_prefix = record.name.upper().replace(' ', '_').replace('-', '_')
            service_name = record.name.lower().replace(' ', '-').replace('_', '-')
            
            if record.endpoint_type in ['postgres', 'supabase', 'odoo']:
                snippet = f"""  {service_name}:
    image: postgres:16-alpine
    environment:
      - POSTGRES_DB=${{{{ {var_prefix}_DATABASE }}}}
      - POSTGRES_USER=${{{{ {var_prefix}_USERNAME }}}}
      - POSTGRES_PASSWORD=${{{{ {var_prefix}_PASSWORD }}}}
    ports:
      - "${{{{ {var_prefix}_PORT }}}}:5432"
    volumes:
      - {service_name}-data:/var/lib/postgresql/data"""
            
            elif record.endpoint_type == 'superset':
                snippet = f"""  {service_name}:
    image: apache/superset:latest
    environment:
      - SUPERSET_SECRET_KEY=${{{{ {var_prefix}_API_KEY }}}}
    ports:
      - "${{{{ {var_prefix}_PORT:-8088 }}}}:8088\""""
            
            elif record.endpoint_type == 'mcp':
                snippet = f"""  {service_name}:
    build: ./mcp-servers/{service_name}
    environment:
      - MCP_SERVER_URL=${{{{ {var_prefix}_URL }}}}
    ports:
      - "${{{{ {var_prefix}_PORT }}}}:{record.port or 8080}\""""
            
            else:
                snippet = f"""  {service_name}:
    image: custom/{service_name}:latest
    environment:
      - SERVICE_URL=${{{{ {var_prefix}_URL }}}}"
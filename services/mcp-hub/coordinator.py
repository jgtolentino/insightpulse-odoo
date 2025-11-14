#!/usr/bin/env python3
"""
MCP Coordinator - Intelligent routing hub for multiple MCP servers

Integrates:
- GitHub (pulser-hub GitHub App)
- DigitalOcean App Platform
- Supabase PostgreSQL
- Notion Workspace
- Apache Superset
- Tableau Cloud

Routes requests based on domain context and operation type.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, AsyncIterator
import httpx
import os
import logging
import json
import asyncio
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MCP Coordinator",
    description="Intelligent routing hub for MCP servers",
    version="1.0.0"
)

# Configuration
PULSER_HUB_URL = os.getenv("PULSER_HUB_URL", "http://localhost:8000")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
DO_API_TOKEN = os.getenv("DO_API_TOKEN", "")
SUPERSET_URL = os.getenv("SUPERSET_URL", "http://localhost:8088")
SUPERSET_USERNAME = os.getenv("SUPERSET_USERNAME", "admin")
SUPERSET_PASSWORD = os.getenv("SUPERSET_PASSWORD", "")
N8N_URL = os.getenv("N8N_URL", "https://ipa.insightpulseai.net")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")


class MCPRequest(BaseModel):
    """MCP protocol request."""
    method: str
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    server: Optional[str] = None  # Target server hint


class MCPResponse(BaseModel):
    """MCP protocol response."""
    result: Optional[Any] = None
    error: Optional[Dict[str, str]] = None


class MCPCoordinator:
    """Intelligent MCP server routing and coordination."""

    def __init__(self):
        self.servers = {
            'github': self._get_github_client(),
            'digitalocean': self._get_do_client(),
            'supabase': self._get_supabase_client(),
            'notion': self._get_notion_client(),
            'superset': self._get_superset_client(),
            'tableau': self._get_tableau_client(),
            'n8n': self._get_n8n_client()
        }

    def _get_github_client(self):
        """GitHub client via pulser-hub MCP."""
        return {
            'url': PULSER_HUB_URL,
            'endpoint': '/mcp/github',
            'domains': ['github', 'git', 'repo', 'pr', 'issue', 'branch', 'workflow'],
            'operations': ['create_branch', 'commit_files', 'create_pr', 'merge_pr',
                          'create_issue', 'trigger_workflow', 'read_file', 'search_code']
        }

    def _get_do_client(self):
        """DigitalOcean App Platform client."""
        return {
            'url': 'https://api.digitalocean.com/v2',
            'headers': {'Authorization': f'Bearer {DO_API_TOKEN}'},
            'domains': ['digitalocean', 'deploy', 'app', 'droplet', 'spaces'],
            'operations': ['list_apps', 'get_app', 'create_deployment', 'get_logs']
        }

    def _get_supabase_client(self):
        """Supabase PostgreSQL client."""
        return {
            'url': SUPABASE_URL,
            'headers': {
                'apikey': SUPABASE_SERVICE_ROLE_KEY,
                'Authorization': f'Bearer {SUPABASE_SERVICE_ROLE_KEY}'
            },
            'domains': ['supabase', 'database', 'postgres', 'sql', 'rpc'],
            'operations': ['query', 'insert', 'update', 'delete', 'rpc']
        }

    def _get_notion_client(self):
        """Notion workspace client."""
        return {
            'url': 'https://api.notion.com/v1',
            'headers': {
                'Authorization': f'Bearer {os.getenv("NOTION_TOKEN", "")}',
                'Notion-Version': '2022-06-28'
            },
            'domains': ['notion', 'page', 'database', 'block'],
            'operations': ['create_page', 'update_page', 'query_database']
        }

    def _get_superset_client(self):
        """Apache Superset client."""
        return {
            'url': SUPERSET_URL,
            'domains': ['superset', 'dashboard', 'chart', 'dataset', 'sql'],
            'operations': ['execute_sql', 'create_chart', 'create_dashboard', 'list_datasets']
        }

    def _get_tableau_client(self):
        """Tableau Cloud client."""
        return {
            'url': os.getenv("TABLEAU_SERVER_URL", ""),
            'domains': ['tableau', 'analytics', 'workbook', 'datasource'],
            'operations': ['query_datasource', 'get_workbook', 'get_view']
        }

    def _get_n8n_client(self):
        """n8n workflow automation client."""
        return {
            'url': N8N_URL,
            'headers': {
                'X-N8N-API-KEY': N8N_API_KEY,
                'Content-Type': 'application/json'
            },
            'domains': ['n8n', 'workflow', 'automation', 'finance', 'bir', 'expense'],
            'operations': ['trigger_workflow', 'list_workflows', 'get_execution',
                          'finance_month_end', 'bir_compliance', 'expense_approval']
        }

    async def route_request(self, method: str, params: Dict[str, Any], server_hint: Optional[str] = None) -> Dict[str, Any]:
        """
        Intelligently route request to appropriate MCP server.

        Args:
            method: MCP method (e.g., "tools/call")
            params: Method parameters
            server_hint: Optional server preference

        Returns:
            Result from target MCP server
        """
        # Extract operation context
        tool_name = params.get('name', '') if method == 'tools/call' else ''
        arguments = params.get('arguments', {})

        # Determine target server
        target_server = await self._select_server(tool_name, arguments, server_hint)

        logger.info(f"Routing {tool_name} to {target_server}")

        # Route to appropriate handler
        if target_server == 'github':
            return await self._call_pulser_hub(method, params)
        elif target_server == 'digitalocean':
            return await self._call_digitalocean(tool_name, arguments)
        elif target_server == 'supabase':
            return await self._call_supabase(tool_name, arguments)
        elif target_server == 'superset':
            return await self._call_superset(tool_name, arguments)
        elif target_server == 'n8n':
            return await self._call_n8n(tool_name, arguments)
        else:
            raise ValueError(f"Unsupported server: {target_server}")

    async def _select_server(self, tool_name: str, arguments: Dict[str, Any], hint: Optional[str]) -> str:
        """Select appropriate server based on operation context."""
        if hint and hint in self.servers:
            return hint

        # Pattern-based routing
        if any(x in tool_name.lower() for x in ['github', 'branch', 'pr', 'issue', 'repo']):
            return 'github'
        elif any(x in tool_name.lower() for x in ['deploy', 'app', 'digitalocean']):
            return 'digitalocean'
        elif any(x in tool_name.lower() for x in ['sql', 'database', 'supabase', 'postgres']):
            return 'supabase'
        elif any(x in tool_name.lower() for x in ['superset', 'dashboard', 'chart']):
            return 'superset'
        elif any(x in tool_name.lower() for x in ['notion', 'page']):
            return 'notion'
        elif any(x in tool_name.lower() for x in ['n8n', 'workflow', 'automation', 'bir', 'finance', 'expense']):
            return 'n8n'
        else:
            # Default to GitHub for unknown operations
            return 'github'

    async def _call_pulser_hub(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call pulser-hub GitHub MCP server."""
        client_config = self.servers['github']

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{client_config['url']}{client_config['endpoint']}",
                json={'method': method, 'params': params}
            )
            response.raise_for_status()
            return response.json()

    async def _call_digitalocean(self, operation: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call DigitalOcean API."""
        client_config = self.servers['digitalocean']

        # Map operation to DO API endpoint
        endpoint_map = {
            'list_apps': '/apps',
            'get_app': '/apps/{app_id}',
            'create_deployment': '/apps/{app_id}/deployments',
            'get_logs': '/apps/{app_id}/deployments/{deployment_id}/logs'
        }

        endpoint = endpoint_map.get(operation)
        if not endpoint:
            raise ValueError(f"Unknown DO operation: {operation}")

        # Replace path parameters
        endpoint = endpoint.format(**arguments)

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{client_config['url']}{endpoint}",
                headers=client_config['headers']
            )
            response.raise_for_status()
            return response.json()

    async def _call_supabase(self, operation: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call Supabase REST API."""
        client_config = self.servers['supabase']

        if operation == 'execute_sql' or operation == 'rpc':
            # RPC call
            function_name = arguments.get('function', 'rpc')
            params = arguments.get('params', {})

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{client_config['url']}/rest/v1/rpc/{function_name}",
                    headers=client_config['headers'],
                    json=params
                )
                response.raise_for_status()
                return response.json()
        else:
            # REST API operation
            table = arguments.get('table', '')
            method = arguments.get('method', 'GET')
            data = arguments.get('data', {})

            async with httpx.AsyncClient(timeout=30.0) as client:
                if method == 'GET':
                    response = await client.get(
                        f"{client_config['url']}/rest/v1/{table}",
                        headers=client_config['headers']
                    )
                elif method == 'POST':
                    response = await client.post(
                        f"{client_config['url']}/rest/v1/{table}",
                        headers=client_config['headers'],
                        json=data
                    )
                response.raise_for_status()
                return response.json()

    async def _call_superset(self, operation: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call Apache Superset API."""
        # First, get access token
        token = await self._get_superset_token()

        client_config = self.servers['superset']
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        # Map operation to Superset API endpoint
        endpoint_map = {
            'execute_sql': '/api/v1/sqllab/execute/',
            'list_datasets': '/api/v1/dataset/',
            'create_chart': '/api/v1/chart/',
            'create_dashboard': '/api/v1/dashboard/'
        }

        endpoint = endpoint_map.get(operation)
        if not endpoint:
            raise ValueError(f"Unknown Superset operation: {operation}")

        async with httpx.AsyncClient(timeout=30.0) as client:
            if operation == 'execute_sql':
                response = await client.post(
                    f"{client_config['url']}{endpoint}",
                    headers=headers,
                    json=arguments
                )
            else:
                response = await client.get(
                    f"{client_config['url']}{endpoint}",
                    headers=headers
                )
            response.raise_for_status()
            return response.json()

    async def _get_superset_token(self) -> str:
        """Get Superset access token."""
        client_config = self.servers['superset']

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{client_config['url']}/api/v1/security/login",
                json={
                    'username': SUPERSET_USERNAME,
                    'password': SUPERSET_PASSWORD,
                    'provider': 'db'
                }
            )
            response.raise_for_status()
            return response.json()['access_token']

    async def _call_n8n(self, operation: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call n8n API."""
        client_config = self.servers['n8n']

        # Map operations to n8n API endpoints
        endpoint_map = {
            'list_workflows': '/api/v1/workflows',
            'trigger_workflow': '/webhook/{workflow_id}',
            'get_execution': '/api/v1/executions/{execution_id}'
        }

        endpoint = endpoint_map.get(operation)
        if not endpoint:
            raise ValueError(f"Unknown n8n operation: {operation}")

        # Replace path parameters
        endpoint = endpoint.format(**arguments)

        async with httpx.AsyncClient(timeout=30.0) as client:
            if operation == 'trigger_workflow':
                # Webhook trigger
                response = await client.post(
                    f"{client_config['url']}{endpoint}",
                    json=arguments.get('data', {})
                )
            else:
                # API call
                response = await client.get(
                    f"{client_config['url']}{endpoint}",
                    headers=client_config['headers']
                )
            response.raise_for_status()
            return response.json()


# Initialize coordinator
coordinator = MCPCoordinator()


# ============================================================================
# MCP Protocol Handlers
# ============================================================================

@app.post("/mcp")
async def mcp_handler(request: Request):
    """Main MCP protocol handler with intelligent routing."""
    try:
        body = await request.json()
        mcp_request = MCPRequest(**body)

        logger.info(f"MCP request: {mcp_request.method}")

        # Handle method
        if mcp_request.method == "tools/list":
            result = await handle_tools_list()
        elif mcp_request.method == "tools/call":
            result = await coordinator.route_request(
                mcp_request.method,
                mcp_request.params,
                mcp_request.server
            )
        else:
            return MCPResponse(
                error={"code": "method_not_found", "message": f"Unknown method: {mcp_request.method}"}
            ).dict()

        return MCPResponse(result=result).dict()

    except Exception as e:
        logger.error(f"MCP handler error: {str(e)}")
        return MCPResponse(
            error={"code": "internal_error", "message": str(e)}
        ).dict()


async def handle_tools_list() -> List[Dict[str, Any]]:
    """Aggregate tool lists from all MCP servers."""
    all_tools = []

    # Add GitHub tools (from pulser-hub)
    all_tools.extend([
        {"name": "github_create_branch", "server": "github"},
        {"name": "github_commit_files", "server": "github"},
        {"name": "github_create_pr", "server": "github"},
        {"name": "github_merge_pr", "server": "github"},
        {"name": "github_create_issue", "server": "github"},
        {"name": "github_trigger_workflow", "server": "github"},
    ])

    # Add DigitalOcean tools
    all_tools.extend([
        {"name": "do_list_apps", "server": "digitalocean"},
        {"name": "do_get_app", "server": "digitalocean"},
        {"name": "do_create_deployment", "server": "digitalocean"},
    ])

    # Add Supabase tools
    all_tools.extend([
        {"name": "supabase_execute_sql", "server": "supabase"},
        {"name": "supabase_rpc", "server": "supabase"},
    ])

    # Add Superset tools
    all_tools.extend([
        {"name": "superset_execute_sql", "server": "superset"},
        {"name": "superset_list_datasets", "server": "superset"},
        {"name": "superset_create_chart", "server": "superset"},
    ])

    # Add n8n tools
    all_tools.extend([
        {"name": "n8n_list_workflows", "server": "n8n"},
        {"name": "n8n_trigger_workflow", "server": "n8n"},
        {"name": "finance_month_end_closing", "server": "n8n"},
        {"name": "bir_compliance", "server": "n8n"},
        {"name": "expense_approval", "server": "n8n"},
    ])

    return all_tools


@app.get("/sse")
async def sse_endpoint():
    """Server-Sent Events endpoint for ChatGPT MCP connector."""
    async def event_generator() -> AsyncIterator[str]:
        """Generate SSE events."""
        while True:
            # Send heartbeat
            yield f"data: {json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()})}\n\n"
            await asyncio.sleep(30)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "servers": list(coordinator.servers.keys()),
        "pulser_hub_url": PULSER_HUB_URL
    }


@app.get("/")
async def root():
    """Root endpoint with information."""
    return {
        "name": "MCP Coordinator",
        "version": "1.0.0",
        "servers": {
            "github": "pulser-hub GitHub App",
            "digitalocean": "App Platform API",
            "supabase": "PostgreSQL REST API",
            "notion": "Workspace API",
            "superset": "Apache Superset",
            "tableau": "Tableau Cloud",
            "n8n": "n8n Workflow Automation"
        },
        "endpoints": {
            "mcp": "/mcp",
            "sse": "/sse",
            "health": "/health"
        },
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

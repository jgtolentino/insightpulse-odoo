---
name: connector-integration-expert
description: Expert-level connector development, API integration, SDK creation, MCP protocols, and plugin architecture for Odoo
version: 1.0.0
tags: [connectors, api, sdk, mcp, plugins, integration, webhooks, rest, graphql]
requires:
  files:
    - superclaude/knowledge/ODOO_19_REFERENCE.md
    - vendor/oca-web/README.md
---

# Connector Integration Expert Skill

## Purpose

Provide expert-level capabilities for connector development, API integration, SDK creation, MCP protocol implementation, and plugin architecture for Odoo ecosystem integration.

## When to use

- Developing custom connectors for external systems
- Creating REST/GraphQL APIs and webhooks
- Building SDKs for Odoo integration
- Implementing MCP (Model Context Protocol) servers
- Developing plugins and extensions
- Integrating with third-party services and platforms

## Actions

1. **Connector Architecture**: Design and implement robust connector patterns
2. **API Development**: Create RESTful APIs, GraphQL endpoints, and webhooks
3. **SDK Creation**: Build software development kits for Odoo integration
4. **MCP Implementation**: Develop MCP servers and protocol integrations
5. **Plugin Development**: Create extensible plugin architectures
6. **Integration Testing**: Comprehensive testing for all integration points

## Inputs

- `integration_target`: Target system or platform to integrate with
- `connector_type`: Type of connector (API, database, file, message queue)
- `protocol_requirements`: Required protocols (REST, GraphQL, SOAP, MCP)
- `sdk_needs`: SDK development requirements
- `security_level`: Security and authentication requirements

## Outputs

- Connector architecture and implementation
- API specifications and documentation
- SDK packages with examples
- MCP server implementations
- Plugin frameworks and extensions
- Integration test suites

## Examples

### Example 1: E-commerce Connector
```
User: "Create a Shopify connector for Odoo with real-time sync"

Agent:
1. Designs Shopify API integration with webhooks
2. Implements product, order, and customer synchronization
3. Creates OCA-compliant connector module
4. Builds SDK for custom Shopify integrations
5. Implements MCP server for AI agent access
6. Provides comprehensive testing and documentation
```

### Example 2: Payment Gateway SDK
```
User: "Build Stripe payment SDK for Odoo with MCP integration"

Agent:
1. Creates Stripe REST API wrapper for Odoo
2. Implements payment processing and webhook handling
3. Builds Python SDK with type hints and documentation
4. Develops MCP server for payment operations
5. Creates plugin architecture for multiple payment providers
6. Provides security best practices and PCI compliance
```

### Example 3: MCP Server for AI Integration
```
User: "Create MCP server to expose Odoo data to AI agents"

Agent:
1. Implements MCP protocol for Odoo data access
2. Creates secure authentication and authorization
3. Exposes CRM, sales, and inventory data via MCP
4. Builds query optimization and caching
5. Provides agent tool definitions and examples
6. Implements real-time data streaming
```

## Connector Patterns & Architecture

### OCA Connector Framework
```python
# Base connector architecture following OCA patterns
class BaseConnector:
    """OCA-compliant base connector"""
    
    def __init__(self, environment):
        self.env = environment
        self.backend = None
        self.connector = None
        
    def _get_backend(self, backend_id):
        """Get backend configuration"""
        return self.env['connector.backend'].browse(backend_id)
    
    def _get_connector(self):
        """Get connector instance"""
        return self.connector_class(self.backend)
```

### REST API Integration
```python
# REST API connector pattern
class RestConnector:
    """Generic REST API connector"""
    
    def __init__(self, base_url, auth_method='oauth2'):
        self.base_url = base_url
        self.auth_method = auth_method
        self.session = requests.Session()
        
    def authenticate(self, credentials):
        """Handle authentication"""
        if self.auth_method == 'oauth2':
            return self._oauth2_authenticate(credentials)
        elif self.auth_method == 'api_key':
            return self._api_key_authenticate(credentials)
            
    def call_api(self, endpoint, method='GET', data=None):
        """Make API call with error handling"""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.request(method, url, json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise ConnectorError(f"API call failed: {e}")
```

## API Development Patterns

### RESTful API Design
```python
# Odoo REST API endpoint
from odoo import http
from odoo.http import request, Response

class CustomAPI(http.Controller):
    
    @http.route('/api/v1/customers', auth='user', methods=['GET'])
    def get_customers(self, **kwargs):
        """RESTful customer API"""
        try:
            customers = request.env['res.partner'].search([('customer', '=', True)])
            return Response(
                json.dumps({
                    'data': customers.read(['name', 'email', 'phone']),
                    'total': len(customers)
                }),
                content_type='application/json'
            )
        except Exception as e:
            return Response(
                json.dumps({'error': str(e)}),
                status=500,
                content_type='application/json'
            )
```

### GraphQL Integration
```python
# GraphQL schema and resolvers
import graphene
from graphene.types.objecttype import ObjectType

class PartnerType(ObjectType):
    """GraphQL partner type"""
    id = graphene.Int()
    name = graphene.String()
    email = graphene.String()
    
class Query(ObjectType):
    """GraphQL query definitions"""
    partners = graphene.List(PartnerType, limit=graphene.Int())
    
    def resolve_partners(self, info, limit=None):
        """Resolve partners query"""
        domain = [('customer', '=', True)]
        partners = info.context['env']['res.partner'].search(domain, limit=limit)
        return [PartnerType(**partner.read()[0]) for partner in partners]
```

## SDK Development

### Python SDK Structure
```python
# Odoo integration SDK
class OdooSDK:
    """Python SDK for Odoo integration"""
    
    def __init__(self, base_url, database, username, password):
        self.base_url = base_url
        self.database = database
        self.username = username
        self.password = password
        self.uid = None
        self.models = None
        
    def authenticate(self):
        """Authenticate with Odoo"""
        common = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/common')
        self.uid = common.authenticate(self.database, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(f'{self.base_url}/xmlrpc/2/object')
        return self.uid
        
    def execute_kw(self, model, method, args, kwargs=None):
        """Execute Odoo method"""
        return self.models.execute_kw(
            self.database, self.uid, self.password,
            model, method, args, kwargs or {}
        )
```

### TypeScript/JavaScript SDK
```typescript
// TypeScript SDK for Odoo
interface OdooConfig {
  baseUrl: string;
  database: string;
  username: string;
  password: string;
}

class OdooClient {
  private config: OdooConfig;
  private uid: number | null = null;
  
  constructor(config: OdooConfig) {
    this.config = config;
  }
  
  async authenticate(): Promise<number> {
    const response = await fetch(`${this.config.baseUrl}/web/session/authenticate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        params: {
          db: this.config.database,
          login: this.config.username,
          password: this.config.password,
        }
      })
    });
    
    const data = await response.json();
    this.uid = data.result.uid;
    return this.uid;
  }
  
  async call(model: string, method: string, args: any[]): Promise<any> {
    // Implementation for model method calls
  }
}
```

## MCP (Model Context Protocol) Implementation

### MCP Server Architecture
```python
# MCP server for Odoo integration
from mcp.server import MCPServer
from mcp.server.models import InitializationOptions
import mcp.types as types

app = MCPServer("odoo-mcp")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_customers",
            description="Get customer data from Odoo",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of customers to return"}
                }
            }
        ),
        types.Tool(
            name="create_sales_order",
            description="Create a new sales order",
            inputSchema={
                "type": "object",
                "properties": {
                    "partner_id": {"type": "integer", "description": "Customer ID"},
                    "order_lines": {"type": "array", "description": "Order line items"}
                }
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool execution"""
    if name == "get_customers":
        customers = await get_odoo_customers(arguments.get('limit', 10))
        return [types.TextContent(type="text", text=customers)]
    elif name == "create_sales_order":
        order_id = await create_odoo_sales_order(arguments)
        return [types.TextContent(type="text", text=f"Created order {order_id}")]
```

### MCP Resource Management
```python
# MCP resources for Odoo data
@app.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources"""
    return [
        types.Resource(
            uri="odoo://customers",
            name="Odoo Customers",
            description="Customer data from Odoo",
            mimeType="application/json"
        ),
        types.Resource(
            uri="odoo://products",
            name="Odoo Products",
            description="Product catalog from Odoo",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read resource data"""
    if uri == "odoo://customers":
        return await get_odoo_customers_json()
    elif uri == "odoo://products":
        return await get_odoo_products_json()
```

## Plugin Architecture

### Extensible Plugin System
```python
# Plugin base class and registry
class PluginBase:
    """Base class for all plugins"""
    
    name = "base_plugin"
    version = "1.0.0"
    
    def __init__(self, env):
        self.env = env
        
    def install(self):
        """Plugin installation"""
        pass
        
    def uninstall(self):
        """Plugin uninstallation"""
        pass
        
    def get_actions(self):
        """Get available actions"""
        return []

class PluginRegistry:
    """Plugin registry and manager"""
    
    def __init__(self):
        self.plugins = {}
        
    def register_plugin(self, plugin_class):
        """Register a plugin"""
        self.plugins[plugin_class.name] = plugin_class
        
    def get_plugin(self, name):
        """Get plugin instance"""
        return self.plugins.get(name)
```

### Hook System for Extensibility
```python
# Hook system for plugin integration
class HookManager:
    """Manage hooks for plugin extensibility"""
    
    def __init__(self):
        self.hooks = {}
        
    def register_hook(self, hook_name, callback):
        """Register a hook callback"""
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
        
    def execute_hook(self, hook_name, *args, **kwargs):
        """Execute all callbacks for a hook"""
        results = []
        for callback in self.hooks.get(hook_name, []):
            try:
                result = callback(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logging.error(f"Hook {hook_name} failed: {e}")
        return results
```

## Integration Testing

### Comprehensive Test Suite
```python
# Integration testing framework
import pytest
from unittest.mock import Mock, patch

class TestConnectorIntegration:
    """Integration tests for connectors"""
    
    @pytest.fixture
    def connector(self):
        """Fixture for connector instance"""
        return ShopifyConnector('https://api.shopify.com')
        
    def test_authentication(self, connector):
        """Test connector authentication"""
        with patch('requests.Session.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'access_token': 'test_token'}
            
            result = connector.authenticate({'api_key': 'test', 'password': 'test'})
            assert result is True
            
    def test_api_call_error_handling(self, connector):
        """Test API error handling"""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.RequestException("API Error")
            
            with pytest.raises(ConnectorError):
                connector.call_api('products')
```

## Security Best Practices

### Authentication & Authorization
```python
# Secure authentication patterns
class SecureConnector:
    """Connector with security best practices"""
    
    def __init__(self):
        self.encryption_key = None
        
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data"""
        fernet = Fernet(self.encryption_key)
        return fernet.encrypt(data.encode())
        
    def validate_api_permissions(self, user, endpoint):
        """Validate API permissions"""
        if not user.has_permission(f'api.{endpoint}'):
            raise PermissionError("Insufficient permissions")
            
    def rate_limit_check(self, user_id):
        """Implement rate limiting"""
        key = f"rate_limit:{user_id}"
        current = self.redis.incr(key)
        if current == 1:
            self.redis.expire(key, 3600)  # 1 hour
        if current > 1000:  # 1000 requests per hour
            raise RateLimitExceeded("Rate limit exceeded")
```

## Performance Optimization

### Caching Strategies
```python
# Advanced caching for connectors
class CachedConnector:
    """Connector with intelligent caching"""
    
    def __init__(self, cache_backend='redis'):
        self.cache_backend = cache_backend
        self.cache_ttl = 300  # 5 minutes
        
    def cached_api_call(self, endpoint, force_refresh=False):
        """Make cached API call"""
        cache_key = f"api:{endpoint}"
        
        if not force_refresh:
            cached = self.cache.get(cache_key)
            if cached:
                return cached
                
        # Make actual API call
        data = self.call_api(endpoint)
        
        # Cache the result
        self.cache.set(cache_key, data, self.cache_ttl)
        return data
```

## Success Metrics

### Integration Quality
- **API Reliability**: 99.9% uptime for connector services
- **Performance**: < 100ms response time for API calls
- **Security**: Zero security vulnerabilities in integration code
- **Maintainability**: Clean, documented, and testable code

### Developer Experience
- **SDK Usability**: Intuitive API with comprehensive documentation
- **Plugin Ecosystem**: Easy plugin development and deployment
- **MCP Integration**: Seamless AI agent access to Odoo data
- **Testing Coverage**: ≥ 90% test coverage for all integrations

## References

- [OCA Connector Framework](https://github.com/OCA/connector)
- [MCP Protocol Specification](https://spec.modelcontextprotocol.io/)
- [Odoo REST API Documentation](https://www.odoo.com/documentation/19.0/developer/api/external.html)
- [GraphQL Best Practices](https://graphql.org/learn/best-practices/)
- [API Security Guidelines](https://owasp.org/www-project-api-security/)

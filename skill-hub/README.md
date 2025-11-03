# Skill Hub - Odoo & Superset Integration API

Unified API server providing Claude Skills with direct access to Odoo ERP and Apache Superset analytics.

## Features

- **Odoo Integration**: XML-RPC client for Odoo 19 external API
- **Superset Integration**: REST API client for Apache Superset
- **Skills Catalog**: Unified catalog of 43+ Claude Skills
- **Authentication**: Bearer token security
- **DigitalOcean Ready**: Deployment configuration included

## Architecture

```
Claude Skills / Custom GPTs
        ↓
   Skill Hub API (FastAPI)
    ├─→ Odoo 19 (XML-RPC)
    │   └─→ erp.insightpulseai.net
    ├─→ Superset (REST API)
    │   └─→ insightpulseai.net/superset
    └─→ Skills Catalog (43 skills)
```

## Quick Start

### Local Development

1. **Install dependencies**:
   ```bash
   cd skill-hub
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Generate bearer token**:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

4. **Start server**:
   ```bash
   python server.py
   ```

5. **Test endpoints**:
   ```bash
   export BEARER_TOKEN="your-token-here"
   python test_integration.py http://localhost:8000
   ```

### Deploy to DigitalOcean

1. **Configure secrets** in DigitalOcean App Platform console:
   - `BEARER_TOKEN`
   - `ODOO_USERNAME`
   - `ODOO_PASSWORD`
   - `SUPERSET_USERNAME`
   - `SUPERSET_PASSWORD`

2. **Deploy**:
   ```bash
   ./deploy.sh
   ```

3. **Configure DNS**:
   Add CNAME: `mcp.insightpulseai.net` → `<your-app>.ondigitalocean.app`

4. **Verify**:
   ```bash
   curl https://mcp.insightpulseai.net/health
   ```

## API Endpoints

### Health Check
```bash
GET /health
```

Returns service status and integration configuration.

### Skills Catalog
```bash
GET /skills/catalog
Authorization: Bearer <token>
```

Returns unified catalog of all 43 skills organized by category.

### Odoo Integration

#### Get Odoo Version
```bash
GET /odoo/version
Authorization: Bearer <token>
```

#### Execute Odoo Method
```bash
POST /odoo/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "model": "crm.lead",
  "method": "create",
  "args": [{
    "name": "New Opportunity",
    "partner_name": "Acme Corp",
    "email_from": "contact@acme.com"
  }]
}
```

**Common Models**:
- `res.partner` - Customers/contacts
- `crm.lead` - Leads/opportunities
- `sale.order` - Sales orders
- `project.task` - Project tasks
- `hr.expense` - Expense reports

**Common Methods**:
- `search` - Find record IDs
- `read` - Get record data
- `search_read` - Combined search + read
- `create` - Create new records
- `write` - Update records
- `unlink` - Delete records

### Superset Integration

#### Query Superset
```bash
POST /superset/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "dashboards"
}
```

**Supported Actions**:
- `dashboards` - List all dashboards
- `dashboard` - Get specific dashboard (requires `dashboard_id`)
- `charts` - List all charts
- `chart_data` - Get chart data (requires `chart_id`)
- `execute_sql` - Run SQL query (requires `database_id`, `sql`)

## Examples

### Create a CRM Lead
```python
import requests

response = requests.post(
    "https://mcp.insightpulseai.net/odoo/execute",
    headers={"Authorization": "Bearer <token>"},
    json={
        "model": "crm.lead",
        "method": "create",
        "args": [{
            "name": "Enterprise Deal",
            "partner_name": "Big Corp Inc",
            "email_from": "sales@bigcorp.com",
            "phone": "+1-555-0123",
            "expected_revenue": 100000.0,
            "type": "opportunity"
        }]
    }
)

lead_id = response.json()["result"]
print(f"Created lead ID: {lead_id}")
```

### Search for Partners
```python
response = requests.post(
    "https://mcp.insightpulseai.net/odoo/execute",
    headers={"Authorization": "Bearer <token>"},
    json={
        "model": "res.partner",
        "method": "search_read",
        "args": [[("is_company", "=", True)]],
        "kwargs": {
            "fields": ["name", "email", "phone", "country_id"],
            "limit": 10,
            "order": "name"
        }
    }
)

partners = response.json()["result"]
for partner in partners:
    print(f"{partner['name']}: {partner['email']}")
```

### Get Superset Dashboards
```python
response = requests.post(
    "https://mcp.insightpulseai.net/superset/query",
    headers={"Authorization": "Bearer <token>"},
    json={"action": "dashboards"}
)

dashboards = response.json()["result"]
for dashboard in dashboards:
    print(f"Dashboard: {dashboard['dashboard_title']}")
    print(f"  URL: {dashboard['url']}")
```

### Execute SQL in Superset
```python
response = requests.post(
    "https://mcp.insightpulseai.net/superset/query",
    headers={"Authorization": "Bearer <token>"},
    json={
        "action": "execute_sql",
        "database_id": 1,
        "sql": "SELECT partner_name, COUNT(*) as lead_count FROM crm_lead GROUP BY partner_name ORDER BY lead_count DESC LIMIT 10"
    }
)

results = response.json()["result"]
```

## Skills Catalog

### Odoo Skills (6)
- `odoo19-oca-devops` - Odoo development with OCA modules
- `odoo-agile-scrum-devops` - Agile workflows for Odoo
- `odoo-app-automator-final` - Automated app scaffolding
- `odoo-finance-automation` - Financial automation
- `odoo-knowledge-agent` - AI knowledge management
- `bir-tax-filing` - BIR tax compliance

### Superset BI Skills (4)
- `superset-chart-builder` - Interactive charts
- `superset-dashboard-automation` - Automated dashboards
- `superset-dashboard-designer` - Dashboard design patterns
- `superset-sql-developer` - SQL dataset development

### Integration & Automation (5)
- `firecrawl-data-extraction` - Web scraping
- `insightpulse_connection_manager` - Connection management
- `mcp-complete-guide` - MCP server development
- `multi-agency-orchestrator` - Multi-agent workflows
- `supabase-rpc-manager` - Supabase RPC functions

### Plus 28 More Skills
Including document processing (PDF, DOCX, XLSX, PPTX), Notion integration, utilities, and Anthropic official skills.

## Security

- **Authentication**: Bearer token required for all protected endpoints
- **CORS**: Restricted to OpenAI origins
- **Secrets**: Store credentials as encrypted environment variables
- **Read-only recommended**: For production, use read-only Odoo/Superset users

## Monitoring

Health endpoint returns integration status:
```bash
curl https://mcp.insightpulseai.net/health

{
  "status": "healthy",
  "service": "skill-hub",
  "version": "1.0.0",
  "integrations": {
    "odoo": {
      "url": "https://erp.insightpulseai.net",
      "configured": true
    },
    "superset": {
      "url": "https://insightpulseai.net/superset",
      "configured": true
    }
  }
}
```

## Troubleshooting

### Authentication Errors
```
401 Unauthorized
```
- Check `BEARER_TOKEN` is set correctly
- Verify token format: `Bearer <token>`

### Odoo Connection Errors
```
500 Internal Server Error: Authentication failed
```
- Verify `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`
- Check Odoo server is accessible
- Confirm user has API access permissions

### Superset Connection Errors
```
500 Internal Server Error: Login failed
```
- Verify `SUPERSET_URL`, `SUPERSET_USERNAME`, `SUPERSET_PASSWORD`
- Check Superset is accessible at `/superset` path
- Confirm user credentials are correct

## Cost

- **Skill Hub**: $5/month (basic-xxs instance on DO App Platform)
- **Total InsightPulse Stack**: ~$25-40/month
  - Odoo droplet: $5-12/month
  - Superset (on Odoo droplet): $0
  - Supabase: $0 (free tier)
  - Skill Hub: $5/month

## Links

- [Claude Code Skills Setup](../docs/CLAUDE_CODE_WEB_SKILLS_SETUP.md)
- [Odoo 19 Documentation](https://www.odoo.com/documentation/19.0/)
- [Superset API Documentation](https://superset.apache.org/docs/rest-api)
- [DigitalOcean App Platform](https://docs.digitalocean.com/products/app-platform/)

## License

MIT

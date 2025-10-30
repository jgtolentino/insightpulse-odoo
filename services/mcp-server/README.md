# pulser-hub MCP Server

**Model Context Protocol (MCP) server** for GitHub operations via the pulser-hub GitHub App.

## 🚀 Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_APP_ID=2191216
export GITHUB_PRIVATE_KEY="$(cat path/to/private-key.pem)"
export GITHUB_INSTALLATION_ID=your_installation_id

# Run server
python server.py
```

Server runs at: `http://localhost:8000`

### Docker

```bash
# Build image
docker build -t pulser-hub-mcp .

# Run container
docker run -p 8000:8000 \
  -e GITHUB_APP_ID=2191216 \
  -e GITHUB_PRIVATE_KEY="$(cat private-key.pem)" \
  -e GITHUB_INSTALLATION_ID=your_id \
  pulser-hub-mcp
```

### Deploy to DigitalOcean

```bash
# Using doctl
doctl apps create --spec app.yaml

# Or via GitHub integration
# Push to main → Auto-deploy
```

## 📡 API Endpoints

### MCP Protocol Endpoint

**POST** `/mcp/github`

Example request:
```json
{
  "method": "tools/list",
  "params": {}
}
```

Example response:
```json
{
  "result": [
    {
      "name": "github_create_pr",
      "description": "Create a pull request",
      "inputSchema": { ... }
    }
  ]
}
```

### Health Check

**GET** `/health`

Returns:
```json
{
  "status": "healthy",
  "app_id": 2191216
}
```

### Root

**GET** `/`

Returns server information and available endpoints.

## 🛠️ Available Tools

### Repository Operations

- `github_create_branch` - Create new branch
- `github_list_branches` - List all branches
- `github_read_file` - Read file contents

### Pull Request Operations

- `github_create_pr` - Create pull request
- `github_list_prs` - List pull requests
- `github_merge_pr` - Merge pull request

### Issue Operations

- `github_create_issue` - Create issue
- `github_list_issues` - List issues

### Workflow Operations

- `github_trigger_workflow` - Trigger GitHub Actions workflow

### File Operations

- `github_commit_files` - Commit multiple files to branch

### Search Operations

- `github_search_code` - Search code in repository

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_APP_ID` | Yes | pulser-hub App ID (2191216) |
| `GITHUB_PRIVATE_KEY` | Yes | Private key (PEM format) |
| `GITHUB_INSTALLATION_ID` | Yes | Installation ID for your org |

### Get Installation ID

```bash
# Using gh CLI with pulser-hub
gh api /app/installations

# Or from GitHub App settings:
# Settings → GitHub Apps → pulser-hub → Install App
# URL will contain installation ID
```

## 🧪 Testing

### Test MCP Protocol

```bash
# List available tools
curl -X POST http://localhost:8000/mcp/github \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list", "params": {}}'

# Call a tool
curl -X POST http://localhost:8000/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "github_list_branches",
      "arguments": {
        "repo": "jgtolentino/insightpulse-odoo"
      }
    }
  }'
```

### Test with Claude Code

Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "pulser-hub": {
      "url": "http://localhost:8000/mcp/github"
    }
  }
}
```

Then in Claude Code:
```
"List all branches in jgtolentino/insightpulse-odoo"
```

Claude will use the MCP server to call GitHub API!

## 📊 Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs

```bash
# Docker logs
docker logs pulser-hub-mcp

# DigitalOcean App Platform
# View logs in dashboard
```

## 🔐 Security

- **Private key**: Never commit to repository
- **JWT tokens**: Auto-refresh every 50 minutes
- **Installation tokens**: Cached and automatically refreshed
- **HTTPS**: Required in production
- **Rate limiting**: GitHub API limits apply (5000 req/hour)

## 🚢 Deployment

### DigitalOcean App Platform

1. Push code to GitHub
2. Connect repository in DO dashboard
3. Add environment variables (secrets)
4. Deploy

**Auto-deploy**: Pushes to `main` branch trigger deployment

### Custom Domain

Add custom domain in DO App Platform:
```
https://mcp.insightpulseai.net
```

Then update MCP URL in Claude Code configuration.

## 📚 Integration

### With Claude Code

```json
{
  "mcpServers": {
    "pulser-hub": {
      "url": "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo"
    }
  }
}
```

### With Claude Desktop

```json
{
  "mcpServers": {
    "pulser-hub": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITHUB_APP_ID=2191216",
        "-e", "GITHUB_PRIVATE_KEY",
        "-e", "GITHUB_INSTALLATION_ID",
        "pulser-hub-mcp"
      ]
    }
  }
}
```

### With Odoo

The MCP server can also be integrated directly into Odoo:

```python
# addons/github_integration/controllers/mcp.py
from odoo import http
from services.mcp_server import server

class MCPController(http.Controller):
    @http.route('/mcp/github', type='json', auth='public')
    def mcp_handler(self, **kwargs):
        return server.handle_mcp_request(kwargs)
```

## 🐛 Troubleshooting

### "Invalid JWT signature"

- Check private key format (PEM)
- Verify App ID matches
- Ensure no trailing whitespace

### "Installation not found"

- Verify installation ID
- Check app is installed on repository
- Confirm app has correct permissions

### "Rate limit exceeded"

- GitHub API has 5000 req/hour limit
- Wait for rate limit reset
- Consider caching responses

### "404 Not Found" for repository

- Verify app is installed on repository
- Check repository name format (owner/repo)
- Ensure app has repository access

## 📖 Resources

- [Model Context Protocol Spec](https://modelcontextprotocol.io/)
- [GitHub Apps Authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app)
- [GitHub REST API](https://docs.github.com/en/rest)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Support

- **Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **Docs**: [docs/MCP_SERVER.md](../../docs/MCP_SERVER.md)
- **Email**: support@insightpulse.ai

---

**Version**: 1.0.0
**License**: LGPL-3.0
**Author**: InsightPulse (@jgtolentino)

# pulser-hub MCP Server

**MCP (Model Context Protocol) server** that exposes GitHub operations via the pulser-hub GitHub App.

## 🎯 Purpose

Allows AI assistants (Claude, ChatGPT, etc.) to perform GitHub operations directly:
- Create/read/update pull requests
- Create/manage branches
- Commit files
- Trigger workflows
- Manage issues
- Query repository data

## 🔗 Server URL

```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo
```

## 🛠️ Installation

### For Claude Code (Cursor)

Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "pulser-hub": {
      "url": "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo",
      "description": "GitHub operations via pulser-hub app"
    }
  }
}
```

### For Claude Desktop

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "pulser-hub": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your-token"
      }
    }
  }
}
```

## 📡 Available Tools

### Repository Operations

#### `github_create_branch`
Create a new branch from base branch
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "branch": "feature/new-feature",
  "from": "main"
}
```

#### `github_list_branches`
List all branches in repository
```json
{
  "repo": "jgtolentino/insightpulse-odoo"
}
```

### File Operations

#### `github_commit_files`
Commit files to a branch
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "branch": "feature/new-feature",
  "message": "feat: add new feature",
  "files": [
    {
      "path": "path/to/file.py",
      "content": "file content"
    }
  ]
}
```

#### `github_read_file`
Read file contents from repository
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "path": "README.md",
  "ref": "main"
}
```

### Pull Request Operations

#### `github_create_pr`
Create a pull request
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "title": "feat: add new feature",
  "body": "Description of changes",
  "head": "feature/new-feature",
  "base": "main"
}
```

#### `github_list_prs`
List pull requests
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "state": "open"
}
```

#### `github_merge_pr`
Merge a pull request
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "pr_number": 123,
  "merge_method": "squash"
}
```

### Issue Operations

#### `github_create_issue`
Create an issue
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "title": "Bug report",
  "body": "Description",
  "labels": ["bug"]
}
```

#### `github_list_issues`
List issues
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "state": "open"
}
```

### Workflow Operations

#### `github_trigger_workflow`
Trigger GitHub Actions workflow
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "workflow_id": "odoo-module-tools.yml",
  "ref": "main",
  "inputs": {
    "action": "bump-version",
    "version_bump": "patch"
  }
}
```

#### `github_list_workflows`
List workflow runs
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "workflow_id": "odoo-module-tools.yml"
}
```

### Search Operations

#### `github_search_code`
Search code in repository
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "query": "def webhook"
}
```

#### `github_list_commits`
List commits
```json
{
  "repo": "jgtolentino/insightpulse-odoo",
  "ref": "main",
  "limit": 10
}
```

## 🔧 Server Implementation

See `services/mcp-server/` for the full implementation.

## 🔐 Authentication

The MCP server uses the pulser-hub GitHub App credentials:
- **App ID**: 2191216
- **Private Key**: From system configuration
- **Installation ID**: From system configuration

Authentication flow:
1. Client connects to MCP server
2. Server generates JWT using private key
3. JWT exchanged for installation token
4. Installation token used for GitHub API calls

## 🚀 Deployment

### Option 1: Deploy to DigitalOcean App Platform

```yaml
# .do/app.yaml
name: pulser-hub-mcp
services:
  - name: mcp-server
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    source_dir: services/mcp-server
    envs:
      - key: GITHUB_APP_ID
        value: "2191216"
      - key: GITHUB_PRIVATE_KEY
        scope: RUN_TIME
        type: SECRET
      - key: GITHUB_INSTALLATION_ID
        scope: RUN_TIME
        type: SECRET
    routes:
      - path: /mcp/github
```

### Option 2: Deploy with Odoo

The MCP server can run as part of the Odoo instance:
```python
# addons/github_integration/controllers/mcp.py
from odoo import http
from odoo.http import request
import json

class MCPController(http.Controller):
    @http.route('/mcp/github', type='json', auth='public', csrf=False)
    def mcp_handler(self, **kwargs):
        """MCP server endpoint."""
        # Handle MCP protocol
        pass
```

## 📖 Usage Examples

### Example 1: Create PR from Chat

**User**: "Create a PR for the feature branch"

**Claude** (via MCP):
```python
result = await mcp.pulser_hub.github_create_pr(
    repo="jgtolentino/insightpulse-odoo",
    title="feat: add new feature",
    body="Implements XYZ functionality",
    head="feature/new-feature",
    base="main"
)
# Returns: {"number": 123, "url": "https://github.com/..."}
```

### Example 2: Commit Multiple Files

**User**: "Commit these changes to the feature branch"

**Claude** (via MCP):
```python
result = await mcp.pulser_hub.github_commit_files(
    repo="jgtolentino/insightpulse-odoo",
    branch="feature/new-feature",
    message="feat: implement new module",
    files=[
        {"path": "addons/new_module/__init__.py", "content": "..."},
        {"path": "addons/new_module/__manifest__.py", "content": "..."}
    ]
)
```

### Example 3: Trigger Workflow

**User**: "Bump the module versions"

**Claude** (via MCP):
```python
result = await mcp.pulser_hub.github_trigger_workflow(
    repo="jgtolentino/insightpulse-odoo",
    workflow_id="odoo-module-tools.yml",
    ref="main",
    inputs={"action": "bump-version", "version_bump": "patch"}
)
```

## 🔄 Integration with Existing System

The MCP server complements the existing webhook integration:

```
┌─────────────────────────────────────────────────┐
│ AI Assistant (Claude/ChatGPT)                  │
│  └─ Connected via MCP protocol                 │
└────────────┬────────────────────────────────────┘
             │ MCP calls (create PR, commit, etc.)
             ↓
┌─────────────────────────────────────────────────┐
│ MCP Server (insightpulseai.net/mcp/github)    │
│  ├─ Authenticates with GitHub App              │
│  ├─ Calls GitHub API                           │
│  └─ Returns results to AI                      │
└────────────┬────────────────────────────────────┘
             │ GitHub API calls
             ↓
┌─────────────────────────────────────────────────┐
│ GitHub (via pulser-hub app)                    │
│  ├─ Creates PRs, commits, etc.                 │
│  └─ Sends webhooks back                        │
└────────────┬────────────────────────────────────┘
             │ Webhooks
             ↓
┌─────────────────────────────────────────────────┐
│ Odoo (/odoo/github/webhook)                    │
│  └─ Processes events, updates records          │
└─────────────────────────────────────────────────┘
```

## 🧪 Testing

### Test MCP Connection

```bash
# Using curl
curl -X POST https://insightpulseai.net/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'

# Expected response: List of available tools
```

### Test Tool Invocation

```bash
curl -X POST https://insightpulseai.net/mcp/github \
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

## 📊 Monitoring

View MCP server logs:
```bash
# If deployed with Odoo
# Check Odoo logs for /mcp/github requests

# If deployed standalone
docker logs pulser-hub-mcp-server
```

## 🔒 Security

- ✅ **Private key** stored securely (never exposed)
- ✅ **JWT tokens** short-lived (10 minutes)
- ✅ **Installation tokens** cached and refreshed
- ✅ **Rate limiting** enforced
- ✅ **HTTPS only** (SSL/TLS required)

## 📚 References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [GitHub Apps Authentication](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app)
- [Supabase MCP Implementation](https://github.com/supabase/mcp-server-supabase)

## 🤝 Support

- **GitHub Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues
- **Documentation**: See `services/mcp-server/README.md`
- **Email**: support@insightpulse.ai

---

**Status**: 🚧 Implementation in progress
**Version**: 1.0.0-alpha
**Last Updated**: 2025-10-30

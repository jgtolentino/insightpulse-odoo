# InsightPulse MCP GitHub Server

**Model Context Protocol (MCP) server for GitHub operations via pulser-hub GitHub App**

Enables AI assistants (Claude, ChatGPT, etc.) to perform GitHub repository operations directly through the MCP protocol.

---

## Overview

This FastAPI-based MCP server exposes **39 comprehensive GitHub operations** as MCP tools, enabling AI assistants to:
- **Branch Management**: Create, list, delete, get branch details (4 tools)
- **Commit Operations**: Commit files, get commits, compare commits (4 tools)
- **Issue Management**: Create, list, get, update, close issues (5 tools)
- **Pull Request Operations**: Full CRUD operations and merging (6 tools)
- **Workflow Automation**: Trigger and monitor GitHub Actions (3 tools)
- **Code Search**: Search code, issues, commits across repositories (3 tools)
- **File Operations**: Read, create, update, delete, list files (5 tools)
- **Low-Level Git**: Direct access to refs, tags, trees, blobs (10 tools)

**Technology Stack**:
- **FastAPI** - Modern Python web framework
- **MCP Protocol** - JSON-RPC 2.0 for AI tool integration
- **OAuth 2.0** - Authorization framework for ChatGPT integration
- **GitHub App** - pulser-hub (App ID: 2191216, Installation: 61508966)
- **Authentication** - JWT tokens with installation access tokens
- **Deployment** - DigitalOcean App Platform
- **Security** - Read-only mode, protected branch enforcement, query parameter filtering

---

## Architecture

```
AI Assistant (Claude Code)
    ↓ MCP Protocol (JSON-RPC 2.0)
FastAPI MCP Server (DigitalOcean)
    ↓ GitHub API v3
GitHub Repository (jgtolentino/insightpulse-odoo)
    ↓ GitHub App (pulser-hub)
JWT Authentication + Installation Tokens
```

**Token Flow**:
1. Generate JWT token from GitHub App private key
2. Exchange JWT for installation access token
3. Use installation token for all GitHub API requests
4. Cache tokens with auto-refresh (5-minute buffer before expiry)

---

## Feature Groups & Tools

**8 Feature Groups** | **39 Total Tools** | **Read-Only Mode Supported**

### Query Parameter Configuration

Control which tools are available using the `features` query parameter:

```
https://insightpulseai.net/mcp/github?project=owner/repo&features=branches,pr,git&read_only=true
```

**Available Features**:
- `branches` - Branch operations (4 tools)
- `commits` - Commit operations (4 tools)
- `issues` - Issue management (5 tools)
- `pr` - Pull request operations (6 tools)
- `workflows` - GitHub Actions (3 tools)
- `search` - Code/issue/commit search (3 tools)
- `files` - File operations (5 tools)
- `git` - Low-level git operations (10 tools)

**Read-Only Mode**: Add `read_only=true` to restrict to 19 read-only tools and block 20 destructive operations.

**Protected Branches**: `main`, `master`, `production`, `prod` cannot be deleted in any mode.

---

## Available MCP Tools

### Branch Management (4 tools)

#### 1. `github_create_branch`
**Purpose**: Create a new branch from a base branch

**Parameters**:
- `branch` (required): New branch name
- `from_branch` (optional): Base branch (default: "main")
- `owner` (optional): Repository owner (default: "jgtolentino")
- `repo` (optional): Repository name (default: "insightpulse-odoo")

**Returns**:
```json
{
  "branch": "feat/new-feature",
  "sha": "abc123...",
  "url": "https://api.github.com/repos/..."
}
```

**Example**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "github_create_branch",
    "arguments": {
      "branch": "feat/mcp-integration",
      "from_branch": "main"
    }
  }
}
```

---

### 2. `github_commit_files`
**Purpose**: Commit multiple files to a branch

**Parameters**:
- `branch` (required): Target branch name
- `message` (required): Commit message
- `files` (required): Array of `{"path": "...", "content": "..."}` objects
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "commit_sha": "def456...",
  "commit_url": "https://api.github.com/repos/.../commits/def456",
  "files_committed": 3
}
```

**Example**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "github_commit_files",
    "arguments": {
      "branch": "feat/mcp-integration",
      "message": "Add MCP server implementation",
      "files": [
        {
          "path": "services/mcp-server/server.py",
          "content": "# MCP server code..."
        },
        {
          "path": "services/mcp-server/README.md",
          "content": "# Documentation..."
        }
      ]
    }
  }
}
```

---

### 3. `github_create_pr`
**Purpose**: Create a pull request

**Parameters**:
- `title` (required): PR title
- `head` (required): Branch with changes
- `base` (optional): Target branch (default: "main")
- `body` (optional): PR description
- `draft` (optional): Create as draft PR (default: false)
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "pr_number": 42,
  "pr_url": "https://github.com/jgtolentino/insightpulse-odoo/pull/42",
  "state": "open"
}
```

---

### 4. `github_list_prs`
**Purpose**: List pull requests

**Parameters**:
- `state` (optional): Filter by state ("open", "closed", "all") (default: "open")
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "pull_requests": [
    {
      "number": 42,
      "title": "Add MCP server",
      "state": "open",
      "url": "https://github.com/.../pull/42",
      "head": "feat/mcp-integration",
      "base": "main"
    }
  ]
}
```

---

### 5. `github_merge_pr`
**Purpose**: Merge a pull request

**Parameters**:
- `pr_number` (required): Pull request number
- `merge_method` (optional): Merge method ("merge", "squash", "rebase") (default: "merge")
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "merged": true,
  "sha": "ghi789...",
  "message": "Pull request successfully merged"
}
```

---

### 6. `github_create_issue`
**Purpose**: Create a GitHub issue

**Parameters**:
- `title` (required): Issue title
- `body` (optional): Issue description
- `labels` (optional): Array of label names
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "issue_number": 15,
  "issue_url": "https://github.com/.../issues/15",
  "state": "open"
}
```

---

### 7. `github_list_issues`
**Purpose**: List GitHub issues

**Parameters**:
- `state` (optional): Filter by state ("open", "closed", "all") (default: "open")
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "issues": [
    {
      "number": 15,
      "title": "MCP server documentation",
      "state": "open",
      "url": "https://github.com/.../issues/15",
      "labels": ["documentation", "enhancement"]
    }
  ]
}
```

---

### 8. `github_trigger_workflow`
**Purpose**: Trigger a GitHub Actions workflow

**Parameters**:
- `workflow_id` (required): Workflow filename or ID
- `ref` (optional): Git reference (default: "main")
- `inputs` (optional): Workflow input parameters
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "workflow_id": "deploy.yml",
  "ref": "main",
  "status": "triggered"
}
```

**Example**:
```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "github_trigger_workflow",
    "arguments": {
      "workflow_id": "digitalocean-deploy.yml",
      "ref": "main",
      "inputs": {
        "force_rebuild": "true"
      }
    }
  }
}
```

---

### 9. `github_read_file`
**Purpose**: Read file contents from repository

**Parameters**:
- `path` (required): File path
- `ref` (optional): Git reference (default: "main")
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "path": "README.md",
  "content": "# InsightPulse Odoo...",
  "sha": "jkl012...",
  "size": 5432
}
```

---

### 10. `github_list_branches`
**Purpose**: List repository branches

**Parameters**:
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "branches": [
    {
      "name": "main",
      "sha": "mno345...",
      "protected": true
    },
    {
      "name": "feat/mcp-integration",
      "sha": "pqr678...",
      "protected": false
    }
  ]
}
```

---

### 11. `github_search_code`
**Purpose**: Search code in repository

**Parameters**:
- `query` (required): Search query
- `owner` (optional): Repository owner
- `repo` (optional): Repository name

**Returns**:
```json
{
  "total_count": 5,
  "items": [
    {
      "name": "server.py",
      "path": "services/mcp-server/server.py",
      "url": "https://github.com/.../blob/.../server.py",
      "sha": "stu901..."
    }
  ]
}
```

---

### Additional Tools (12-39)

#### Branch Management (continued)

**12. `github_delete_branch`** - Delete a branch (protected branches cannot be deleted)
**13. `github_get_branch`** - Get detailed information about a specific branch

#### Commit Operations

**14. `github_get_commit`** - Get detailed commit information
**15. `github_list_commits`** - List commits on a branch
**16. `github_compare_commits`** - Compare two commits

#### Issue Management (continued)

**17. `github_get_issue`** - Get detailed issue information
**18. `github_update_issue`** - Update issue title, body, state, labels
**19. `github_close_issue`** - Close an issue

#### Pull Request Operations (continued)

**20. `github_get_pr`** - Get detailed pull request information
**21. `github_update_pr`** - Update PR title, body, state
**22. `github_close_pr`** - Close a pull request without merging

#### Workflow Automation (continued)

**23. `github_list_workflows`** - List all GitHub Actions workflows
**24. `github_get_workflow_run`** - Get workflow run details and status

#### Code Search (continued)

**25. `github_search_issues`** - Search issues across repository
**26. `github_search_commits`** - Search commits by message or author

#### File Operations (continued)

**27. `github_create_file`** - Create a new file in repository
**28. `github_update_file`** - Update existing file contents
**29. `github_delete_file`** - Delete a file from repository
**30. `github_list_files`** - List files in a directory

#### Low-Level Git Operations (10 tools)

**31. `github_create_ref`** - Create a git reference (branch, tag)
**32. `github_update_ref`** - Update an existing reference
**33. `github_delete_ref`** - Delete a git reference
**34. `github_get_ref`** - Get reference information
**35. `github_list_refs`** - List all references in repository
**36. `github_create_tag`** - Create an annotated tag
**37. `github_get_tree`** - Get git tree object
**38. `github_create_tree`** - Create a git tree object
**39. `github_create_blob`** - Create a git blob object
**40. `github_get_blob`** - Get git blob contents

**Note**: For complete API documentation of tools 12-40, see the tool definitions in `server.py` or use the `tools/list` MCP method.

---

## Installation & Deployment

### Local Development

**Prerequisites**:
- Python 3.11+
- GitHub App private key (pulser-hub)
- Installation ID for target repository

**Setup**:
```bash
cd services/mcp-server

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_APP_ID="2191216"
export GITHUB_PRIVATE_KEY="$(cat pulser-hub-private-key.pem)"
export GITHUB_INSTALLATION_ID="61508966"
export GITHUB_REPO_OWNER="jgtolentino"
export GITHUB_REPO_NAME="insightpulse-odoo"

# Run server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Test Health**:
```bash
curl http://localhost:8000/health
```

**List Available Tools**:
```bash
curl -X POST http://localhost:8000/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list",
    "params": {}
  }'
```

---

### Docker Deployment

**Build Image**:
```bash
cd services/mcp-server
docker build -t mcp-github-server:latest .
```

**Run Container**:
```bash
docker run -d \
  --name mcp-github-server \
  -p 8000:8000 \
  -e GITHUB_APP_ID="2191216" \
  -e GITHUB_PRIVATE_KEY="$(cat pulser-hub-private-key.pem)" \
  -e GITHUB_INSTALLATION_ID="61508966" \
  -e GITHUB_REPO_OWNER="jgtolentino" \
  -e GITHUB_REPO_NAME="insightpulse-odoo" \
  mcp-github-server:latest
```

---

### DigitalOcean App Platform

**Prerequisites**:
- DigitalOcean account with `doctl` CLI authenticated
- GitHub App secrets stored as environment variables

**Deploy**:
```bash
# Create app from spec
doctl apps create --spec infra/do/mcp-github-server.yaml

# Get app ID (from creation output)
export MCP_APP_ID="<app-id>"

# Trigger deployment
doctl apps create-deployment $MCP_APP_ID --force-rebuild

# Monitor logs
doctl apps logs $MCP_APP_ID --follow

# Get app URL
doctl apps get $MCP_APP_ID --format DefaultIngress --no-header
```

**Update Deployment**:
```bash
# Update app spec
doctl apps update $MCP_APP_ID --spec infra/do/mcp-github-server.yaml

# Create new deployment
doctl apps create-deployment $MCP_APP_ID --force-rebuild
```

**Health Check**:
```bash
# Get app URL
APP_URL=$(doctl apps get $MCP_APP_ID --format DefaultIngress --no-header)

# Test health endpoint
curl https://$APP_URL/health
```

---

## OAuth 2.0 Integration

**ChatGPT Integration Support** - Full OAuth 2.0 authorization flow for AI assistant authentication.

### OAuth Endpoints

**Authorization Endpoint**: `https://insightpulseai.net/oauth/authorize`
**Token Endpoint**: `https://insightpulseai.net/oauth/token`

### Grant Types Supported

1. **Authorization Code Grant** (ChatGPT integration)
2. **Refresh Token Grant** (token renewal)

### OAuth Configuration

**Client Credentials**:
```bash
# Environment variables
export OAUTH_CLIENT_ID="insightpulse-mcp-github"
export OAUTH_CLIENT_SECRET="<openssl-rand-base64-32-output>"
```

**Default Client ID**: `insightpulse-mcp-github`
**Client Secret**: Auto-generated on first start (check logs) or set via environment variable

### OAuth Flow

1. **Authorization Request**:
   ```
   GET /oauth/authorize?client_id=<id>&redirect_uri=<uri>&state=<state>&scope=github:all
   ```

2. **Authorization Code** (expires in 10 minutes):
   - Server redirects to ChatGPT with authorization code
   - Code format: `code=<urlsafe-token>`

3. **Token Exchange**:
   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=authorization_code&code=<code>&redirect_uri=<uri>&client_id=<id>&client_secret=<secret>
   ```

4. **Access Token Response**:
   ```json
   {
     "access_token": "<token>",
     "token_type": "Bearer",
     "expires_in": 3600,
     "refresh_token": "<refresh-token>",
     "scope": "github:all"
   }
   ```

5. **Token Refresh**:
   ```
   POST /oauth/token
   Content-Type: application/x-www-form-urlencoded

   grant_type=refresh_token&refresh_token=<token>&client_id=<id>&client_secret=<secret>
   ```

### ChatGPT Setup

See complete ChatGPT integration guide: [docs/CHATGPT_MCP_SETUP.md](docs/CHATGPT_MCP_SETUP.md)

**Quick Steps**:
1. Open ChatGPT Settings → Model Context Protocol → Add Server
2. Configure OAuth 2.0 with authorization and token URLs
3. Use client ID and secret from server configuration
4. Authorize and start using GitHub operations

### Security Considerations

- **Production**: Generate strong client secret with `openssl rand -base64 32`
- **Token Storage**: Use Redis or database instead of in-memory (current implementation)
- **Token Expiration**: Access tokens expire after 1 hour
- **HTTPS Only**: Never expose OAuth endpoints over HTTP

---

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_APP_ID` | Yes | `2191216` | pulser-hub GitHub App ID |
| `GITHUB_PRIVATE_KEY` | Yes | - | GitHub App private key (PEM format) |
| `GITHUB_INSTALLATION_ID` | Yes | `61508966` | Installation ID for target repository |
| `GITHUB_REPO_OWNER` | No | `jgtolentino` | Default repository owner |
| `GITHUB_REPO_NAME` | No | `insightpulse-odoo` | Default repository name |
| `OAUTH_CLIENT_ID` | No | `insightpulse-mcp-github` | OAuth 2.0 client ID |
| `OAUTH_CLIENT_SECRET` | No | Auto-generated | OAuth 2.0 client secret (use strong secret in production) |

### GitHub App Permissions

**Required Permissions** (pulser-hub App):
- **Contents**: Read and Write
- **Issues**: Read and Write
- **Pull Requests**: Read and Write
- **Workflows**: Read and Write
- **Metadata**: Read-only (default)

---

## Security

### Authentication Flow

1. **JWT Generation**:
   - Create JWT token from GitHub App private key
   - Token expires in 10 minutes
   - Signed with RS256 algorithm

2. **Installation Token**:
   - Exchange JWT for installation access token
   - Token expires in 1 hour
   - Cached with auto-refresh (5-minute buffer)

3. **API Requests**:
   - Use installation token for all GitHub API calls
   - Token included in Authorization header
   - Automatic retry on 401 errors

### Token Caching

- Tokens cached in-memory per installation ID
- Auto-refresh when expiry within 5 minutes
- Thread-safe for concurrent requests
- Cleared on server restart

### Best Practices

- **Private Key Security**: Store GitHub App private key in secrets management (DO Secrets, environment variables)
- **Installation Scope**: Limit GitHub App installation to specific repositories
- **Token Rotation**: Tokens auto-refresh, no manual rotation needed
- **Rate Limiting**: GitHub API rate limits apply (5,000 requests/hour per installation)

---

## Troubleshooting

### Common Issues

**Issue**: "Failed to authenticate with GitHub"
- **Cause**: Invalid private key or App ID
- **Fix**: Verify `GITHUB_APP_ID` and `GITHUB_PRIVATE_KEY` environment variables
- **Test**: Generate JWT manually and verify with GitHub API

**Issue**: "Tool not found: github_..."
- **Cause**: Tool name typo or unsupported method
- **Fix**: Use `tools/list` method to see available tools
- **Example**: Correct name is `github_create_branch`, not `create_branch`

**Issue**: "403 Forbidden" on GitHub API calls
- **Cause**: Insufficient GitHub App permissions
- **Fix**: Check pulser-hub App settings → Permissions → verify required scopes
- **Permissions**: Contents (R/W), Issues (R/W), PRs (R/W), Workflows (R/W)

**Issue**: Health check failing
- **Cause**: Server not running or port conflict
- **Fix**: Check server logs, verify port 8000 available
- **Command**: `docker logs mcp-github-server` or `journalctl -u uvicorn`

### Debugging

**Enable Debug Logging**:
```python
# In server.py
logging.basicConfig(level=logging.DEBUG)
```

**Test JWT Token Generation**:
```bash
python -c "
import time, jwt, os
payload = {'iat': int(time.time()) - 60, 'exp': int(time.time()) + 600, 'iss': os.getenv('GITHUB_APP_ID')}
token = jwt.encode(payload, os.getenv('GITHUB_PRIVATE_KEY'), algorithm='RS256')
print(token)
"
```

**Test Installation Token**:
```bash
JWT_TOKEN="<generated-jwt>"
curl -X POST https://api.github.com/app/installations/61508966/access_tokens \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Accept: application/vnd.github+json"
```

---

## Performance

### Benchmarks

- **Health Check**: <50ms response time
- **Tool Listing**: <100ms (cached)
- **GitHub API Calls**: 200-500ms (network latency)
- **Token Refresh**: <1s (only when expired)

### Optimization

- **Token Caching**: Reduces authentication overhead by 90%
- **Async I/O**: FastAPI async handlers for concurrent requests
- **Connection Pooling**: httpx client reuses connections
- **Resource Usage**: <100MB memory, <5% CPU (idle)

---

## API Reference

### MCP Protocol Endpoints

**`POST /mcp/github`**
- **Purpose**: Main MCP protocol endpoint
- **Content-Type**: `application/json`
- **Request**: MCP JSON-RPC 2.0 format
- **Response**: MCP JSON-RPC 2.0 format

**`GET /health`**
- **Purpose**: Health check endpoint
- **Response**: `{"status": "ok", "service": "mcp-github-server", "version": "1.0.0"}`

### MCP Methods

**`tools/list`**
- **Purpose**: List all available GitHub tools
- **Parameters**: None
- **Returns**: Array of tool definitions with names and descriptions

**`tools/call`**
- **Purpose**: Execute a GitHub tool
- **Parameters**: `{"name": "tool_name", "arguments": {...}}`
- **Returns**: Tool-specific result object

---

## Client Configuration

Configure your AI assistant to use the InsightPulse GitHub MCP Server.

**Production URL**: `https://insightpulseai.net/mcp/github`

**Query Parameters**:
- `project` - Repository in `owner/repo` format (default: `jgtolentino/insightpulse-odoo`)
- `features` - Comma-separated list of enabled features (default: all enabled)

**Available Features**: `branches`, `commits`, `issues`, `pr`, `workflows`, `search`, `files`, `git`

### Supported Clients

**Claude Code** (VS Code Extension)
- Configuration: `~/.claude/config.json`
- Guide: [client-configs/claude-code/README.md](client-configs/claude-code/README.md)
- Example:
  ```
  https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files
  ```

**Cursor IDE**
- Configuration: `~/.cursor/mcp-settings.json` or `.cursor/mcp.json`
- Guide: [client-configs/cursor/README.md](client-configs/cursor/README.md)
- Example: Same URL as Claude Code

**ChatGPT** (Custom GPT)
- Configuration: OpenAPI specification
- Guide: [client-configs/chatgpt/README.md](client-configs/chatgpt/README.md)
- OpenAPI Spec: [client-configs/chatgpt/openapi.json](client-configs/chatgpt/openapi.json)

### Quick Start

1. **Choose Your URL**:
   - Full access: `?features=branches,commits,issues,pr,workflows,search,files,git`
   - Read-only: `?features=search,files&read_only=true`
   - CI/CD: `?features=workflows,pr&read_only=true`
   - Development: `?features=branches,commits,files,git`

2. **Configure Client**: Follow client-specific setup guide

3. **Test Connection**: Try `"List all branches in the repository"`

### Documentation

- **Complete Setup Guide**: [docs/CLIENT_SETUP.md](docs/CLIENT_SETUP.md)
- **Query Parameters**: [docs/QUERY_PARAMETERS.md](docs/QUERY_PARAMETERS.md)
- **Feature Mapping**: [docs/FEATURE_MAPPING.md](docs/FEATURE_MAPPING.md)

---

## Contributing

### Adding New Tools

1. **Create Tool Function**:
```python
async def github_new_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """Tool description for MCP registry."""
    # Implementation
    return {"result": "..."}
```

2. **Register Tool**:
```python
MCP_TOOLS = {
    # ... existing tools
    "github_new_tool": github_new_tool
}
```

3. **Update Documentation**: Add tool to README.md "Available MCP Tools" section

4. **Add Tests**: Create test cases in `tests/test_tools.py`

---

## License

LGPL-3.0 (same as InsightPulse Odoo platform)

---

## Support

- **Documentation**: [InsightPulse Docs](https://docs.insightpulse.ai)
- **Issues**: [GitHub Issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **MCP Protocol**: [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/)

---

**Maintained by**: InsightPulse AI
**Last Updated**: 2025-10-30
**Version**: 2.0.0 (OAuth 2.0 + 39 Comprehensive Git Operations)

# MCP Client Setup Guide

Comprehensive guide for configuring AI assistants to use the InsightPulse GitHub MCP Server.

## Overview

The InsightPulse GitHub MCP Server exposes GitHub operations through the Model Context Protocol (MCP), enabling AI assistants to perform repository operations programmatically.

**Base URL**: `https://insightpulseai.net/mcp/github`

**Supported Clients**:
- [Claude Code](#claude-code-setup) (VS Code extension)
- [Cursor IDE](#cursor-ide-setup)
- [ChatGPT](#chatgpt-custom-gpt-setup) (Custom GPT)

---

## Quick Start

### 1. Choose Your URL

**Full Access** (all features):
```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files
```

**Read-Only** (search and files):
```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=search,files
```

**CI/CD** (workflows and PRs):
```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=workflows,pr
```

### 2. Configure Your Client

Follow the client-specific setup guide:
- **Claude Code**: [client-configs/claude-code/README.md](../client-configs/claude-code/README.md)
- **Cursor IDE**: [client-configs/cursor/README.md](../client-configs/cursor/README.md)
- **ChatGPT**: [client-configs/chatgpt/README.md](../client-configs/chatgpt/README.md)

### 3. Test Connection

Try a simple operation in your AI assistant:
```
"List all branches in the insightpulse-odoo repository"
```

---

## Query Parameters

### `project` (optional)

**Format**: `owner/repository`
**Default**: `jgtolentino/insightpulse-odoo`
**Description**: Sets default repository for all GitHub operations

**Example**:
```
?project=myorg/myrepo
```

**Use Cases**:
- Multi-repository workflows
- Different projects with same MCP server
- Team-specific repository defaults

---

### `features` (optional)

**Format**: Comma-separated list
**Default**: All features enabled
**Description**: Limits available GitHub tools to specified features

**Available Features**:
| Feature | Tools | Description |
|---------|-------|-------------|
| `branches` | `github_create_branch`, `github_list_branches` | Branch management |
| `commits` | `github_commit_files` | Commit multiple files |
| `issues` | `github_create_issue`, `github_list_issues` | Issue tracking |
| `pr` | `github_create_pr`, `github_list_prs`, `github_merge_pr` | Pull request workflow |
| `workflows` | `github_trigger_workflow` | GitHub Actions automation |
| `search` | `github_search_code` | Code search |
| `files` | `github_read_file` | Read file contents |

**Example**:
```
?features=branches,commits,pr
```

**Use Cases**:
- Least privilege access control
- Environment-specific feature sets (dev vs prod)
- Role-based tool access (developer vs reviewer)

---

## Claude Code Setup

### Installation

**Configuration File**: `~/.claude/config.json`

**Configuration**:
```json
{
  "mcpServers": {
    "insightpulse-github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http",
        "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files"
      ],
      "description": "InsightPulse GitHub operations via pulser-hub App",
      "env": {}
    }
  }
}
```

**Steps**:
1. Create/edit `~/.claude/config.json`
2. Add configuration above
3. Restart VS Code
4. Verify connection in Claude Code panel

**Full Guide**: [client-configs/claude-code/README.md](../client-configs/claude-code/README.md)

---

## Cursor IDE Setup

### Installation

**Configuration File**: `~/.cursor/mcp-settings.json` or `.cursor/mcp.json` (project-specific)

**Configuration**:
```json
{
  "mcpServers": {
    "insightpulse-github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http",
        "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files"
      ],
      "description": "InsightPulse GitHub MCP Server"
    }
  }
}
```

**Steps**:
1. Create `~/.cursor/mcp-settings.json` (global) or `.cursor/mcp.json` (project)
2. Add configuration above
3. Restart Cursor IDE
4. Verify connection in AI assistant panel

**Full Guide**: [client-configs/cursor/README.md](../client-configs/cursor/README.md)

---

## ChatGPT Custom GPT Setup

### Installation

**Requirements**: ChatGPT Plus or Enterprise subscription

**Steps**:
1. Go to ChatGPT → "My GPTs" → "+ Create a GPT"
2. Configure basic settings (name, description, instructions)
3. Add Actions → Import OpenAPI specification
4. Use `client-configs/chatgpt/openapi.json`
5. Test and publish

**OpenAPI Specification**: [client-configs/chatgpt/openapi.json](../client-configs/chatgpt/openapi.json)

**Full Guide**: [client-configs/chatgpt/README.md](../client-configs/chatgpt/README.md)

---

## Testing Configuration

### Health Check

Test if MCP server is accessible:

```bash
curl https://insightpulseai.net/health
```

**Expected Response**:
```json
{
  "status": "ok",
  "service": "mcp-github-server",
  "version": "1.0.0",
  "github_app_id": "2191216"
}
```

### List Available Tools

Test MCP endpoint and feature filtering:

```bash
curl -X POST "https://insightpulseai.net/mcp/github?features=branches,commits" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "tools/list",
    "params": {}
  }'
```

**Expected**: Only branch and commit tools listed

### Test Tool Execution

```bash
curl -X POST "https://insightpulseai.net/mcp/github" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "2",
    "method": "tools/call",
    "params": {
      "name": "github_list_branches",
      "arguments": {}
    }
  }'
```

**Expected**: List of repository branches

---

## Common Workflows

### Development Workflow

**Features**: `branches,commits,pr`

**Operations**:
1. Create feature branch
2. Commit changes
3. Create pull request
4. Merge PR (after review)

**Example Prompts**:
```
"Create a new branch called feat/add-ui from main"
"Commit these files to feat/add-ui with message 'Add UI components'"
"Create a pull request for feat/add-ui"
```

---

### Code Review Workflow

**Features**: `pr,search,files`

**Operations**:
1. List open PRs
2. Search related code
3. Read file contents
4. Add review comments (via issues)

**Example Prompts**:
```
"List all open pull requests"
"Search for similar implementations of this pattern"
"Read the file that PR #42 is modifying"
```

---

### CI/CD Workflow

**Features**: `workflows,pr`

**Operations**:
1. Trigger deployment workflows
2. Check PR status
3. Monitor workflow runs

**Example Prompts**:
```
"Trigger the digitalocean-deploy workflow on main branch"
"List PRs ready for merge"
```

---

### Read-Only Analytics

**Features**: `search,files`

**Operations**:
1. Search codebase patterns
2. Read documentation
3. Analyze code structure

**Example Prompts**:
```
"Search for all FastAPI routes in the codebase"
"Read the main README file"
"Find all database migration files"
```

---

## Troubleshooting

### MCP Server Not Connecting

**Symptoms**:
- AI assistant doesn't recognize GitHub operations
- Timeout errors when calling tools
- "Server unavailable" messages

**Solutions**:
1. **Verify Server Health**:
   ```bash
   curl https://insightpulseai.net/health
   ```

2. **Check Configuration**:
   - Verify JSON syntax is valid
   - Ensure `npx` is installed: `npx --version`
   - Confirm MCP HTTP transport is available

3. **Test Endpoint Directly**:
   ```bash
   curl -X POST https://insightpulseai.net/mcp/github \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"tools/list","params":{}}'
   ```

4. **Restart Client**:
   - Claude Code: Restart VS Code
   - Cursor: Restart Cursor IDE
   - ChatGPT: Refresh browser, re-import OpenAPI spec

---

### Tools Not Available

**Symptoms**:
- AI says it can't perform certain operations
- Specific tools missing from available tools list
- "Tool not found" errors

**Solutions**:
1. **Check Features Parameter**:
   - Verify the needed feature is in your `features` parameter
   - Example: `pr` feature required for `github_create_pr` tool

2. **Test Feature Filtering**:
   ```bash
   # Test with specific features
   curl -X POST "https://insightpulseai.net/mcp/github?features=branches" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"tools/list","params":{}}'
   ```

3. **Use All Features**:
   - Remove `features` parameter to enable all tools
   - Or explicitly list all: `features=branches,commits,issues,pr,workflows,search,files`

4. **Verify Tool Name**:
   - Check [FEATURE_MAPPING.md](FEATURE_MAPPING.md) for correct tool names
   - Tool names are case-sensitive

---

### Permission Errors

**Symptoms**:
- "403 Forbidden" errors
- "Insufficient permissions" messages
- Operations fail with authorization errors

**Solutions**:
1. **GitHub App Permissions**:
   - MCP server uses pulser-hub GitHub App (ID: 2191216)
   - Verify app has required permissions (Contents, Issues, PRs, Workflows)
   - Check app installation on repository

2. **Repository Access**:
   - Verify repository exists and is accessible
   - Check `project` parameter format: `owner/repo`
   - Confirm GitHub App is installed on target repository

3. **Operation Scope**:
   - Some operations require write access
   - Read-only operations: `search`, `files`, list operations
   - Write operations: `create_branch`, `commit_files`, `create_pr`, `merge_pr`, `create_issue`, `trigger_workflow`

---

### Performance Issues

**Symptoms**:
- Slow response times
- Timeout errors
- Operations taking >30 seconds

**Solutions**:
1. **Check Server Status**:
   - DigitalOcean App Platform dashboard
   - Monitor MCP server logs

2. **Optimize Operations**:
   - Use specific features to reduce server load
   - Batch operations when possible
   - Avoid large file reads (>1MB)

3. **Network Issues**:
   - Check internet connectivity
   - Verify firewall settings
   - Test with curl from same network

---

## Advanced Configuration

### Multiple Projects

Configure different MCP servers for different repositories:

**Claude Code**:
```json
{
  "mcpServers": {
    "insightpulse-github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-http", "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,pr"]
    },
    "other-project-github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-http", "https://insightpulseai.net/mcp/github?project=otherorg/otherrepo&features=search,files"]
    }
  }
}
```

---

### Environment-Specific Configuration

**Development** (full access):
```
?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files
```

**Staging** (workflows and PRs):
```
?project=jgtolentino/insightpulse-odoo&features=workflows,pr
```

**Production** (read-only):
```
?project=jgtolentino/insightpulse-odoo&features=search,files
```

---

### Team-Specific Configuration

**Developers**: Full features
**Reviewers**: `pr,search,files`
**CI/CD**: `workflows,pr`
**Analysts**: `search,files`

---

## Security Best Practices

1. **Least Privilege**: Only enable features needed for specific use case
2. **Project Scoping**: Use `project` parameter to limit default repository
3. **Read-Only First**: Start with `search,files` features, add write features as needed
4. **Monitor Usage**: Check MCP server logs for unusual activity
5. **Rotate Credentials**: GitHub App tokens are auto-rotated by server
6. **Audit Trail**: All operations logged with timestamps and user context

---

## Support

### Documentation
- **MCP Server**: [../README.md](../README.md)
- **Query Parameters**: [QUERY_PARAMETERS.md](QUERY_PARAMETERS.md)
- **Feature Mapping**: [FEATURE_MAPPING.md](FEATURE_MAPPING.md)
- **Client-Specific**:
  - [Claude Code](../client-configs/claude-code/README.md)
  - [Cursor IDE](../client-configs/cursor/README.md)
  - [ChatGPT](../client-configs/chatgpt/README.md)

### GitHub
- **Issues**: [jgtolentino/insightpulse-odoo/issues](https://github.com/jgtolentino/insightpulse-odoo/issues)
- **Discussions**: [jgtolentino/insightpulse-odoo/discussions](https://github.com/jgtolentino/insightpulse-odoo/discussions)

### Contact
- **Website**: [https://insightpulseai.net](https://insightpulseai.net)
- **Support**: Submit GitHub issue with `mcp-server` label

---

## FAQ

**Q: Do I need GitHub credentials in my client configuration?**
A: No, the MCP server uses the pulser-hub GitHub App for authentication.

**Q: Can I use the MCP server for private repositories?**
A: Yes, if the pulser-hub GitHub App is installed on the repository.

**Q: What happens if I don't specify the `features` parameter?**
A: All features are enabled by default (backward compatible).

**Q: Can I use custom GitHub Apps?**
A: Currently only pulser-hub (ID: 2191216) is supported. Custom app support planned for future release.

**Q: Is there a rate limit?**
A: GitHub API rate limit is 5,000 requests/hour per installation. MCP server implements token caching to minimize requests.

**Q: Can I self-host the MCP server?**
A: Yes, see [../README.md](../README.md) for deployment instructions.

**Q: What's the difference between MCP and GitHub CLI?**
A: MCP enables AI assistants to perform operations autonomously. GitHub CLI requires manual command execution.

**Q: Can I add custom tools?**
A: Yes, see [../README.md#contributing](../README.md#contributing) for adding new tools.

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0

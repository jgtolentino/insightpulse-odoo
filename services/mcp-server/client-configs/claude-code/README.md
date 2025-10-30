# Claude Code MCP Setup Guide

Configure Claude Code (VS Code extension) to use the InsightPulse GitHub MCP Server.

## Installation

### Step 1: Locate MCP Configuration File

Claude Code MCP servers are configured in:
```
~/.claude/config.json
```

If the file doesn't exist, create it with an empty object:
```bash
mkdir -p ~/.claude
echo '{}' > ~/.claude/config.json
```

### Step 2: Add InsightPulse GitHub MCP Server

Copy the configuration from `mcp-config.json` and add it to your `~/.claude/config.json`:

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

**Query Parameters Explained**:
- `project=jgtolentino/insightpulse-odoo` - Default repository for operations
- `features=branches,commits,issues,pr,workflows,search,files` - Enabled GitHub tools

### Step 3: Reload Claude Code

After updating the configuration:
1. Restart VS Code
2. Open Claude Code panel
3. Verify MCP server is connected (check status indicator)

## Customization

### Change Default Repository

Update the `project` parameter:
```json
"args": [
  "-y",
  "@modelcontextprotocol/server-http",
  "https://insightpulseai.net/mcp/github?project=myorg/myrepo&features=..."
]
```

### Limit Available Features

Remove features from the `features` parameter:

**Read-Only Configuration** (search and files only):
```
features=search,files
```

**CI/CD Configuration** (workflows and PRs only):
```
features=workflows,pr
```

**Full Development** (all features):
```
features=branches,commits,issues,pr,workflows,search,files
```

## Available Features

| Feature | Tools | Use Case |
|---------|-------|----------|
| `branches` | `github_create_branch`, `github_list_branches` | Branch management |
| `commits` | `github_commit_files` | Committing changes |
| `issues` | `github_create_issue`, `github_list_issues` | Issue tracking |
| `pr` | `github_create_pr`, `github_list_prs`, `github_merge_pr` | Pull request workflow |
| `workflows` | `github_trigger_workflow` | GitHub Actions |
| `search` | `github_search_code` | Code search |
| `files` | `github_read_file` | Reading file contents |

## Testing

### Test MCP Server Connection

In Claude Code, try these commands:

```
"List all branches in the repository"
"Create a new branch called test/mcp-integration from main"
"Read the contents of README.md"
"Search for 'FastAPI' in the codebase"
```

### Verify Available Tools

Ask Claude:
```
"What GitHub operations can you perform?"
```

Expected: Claude should list the enabled GitHub tools based on your `features` parameter.

## Troubleshooting

### MCP Server Not Connecting

**Symptom**: Claude Code doesn't recognize GitHub operations

**Solutions**:
1. Check configuration file syntax (valid JSON)
2. Verify `npx` is in your PATH: `which npx`
3. Check Claude Code logs: VS Code → Output → Claude Code
4. Test MCP server directly:
   ```bash
   curl -X POST "https://insightpulseai.net/mcp/github?features=branches" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
   ```

### Tools Not Available

**Symptom**: Claude says it can't perform certain operations

**Solutions**:
1. Check `features` parameter includes the needed feature
2. Verify MCP server is deployed: `curl https://insightpulseai.net/health`
3. Reload VS Code after configuration changes

### HTTP MCP Transport Issues

**Symptom**: `@modelcontextprotocol/server-http` not found

**Solution**: Install the HTTP MCP transport:
```bash
npm install -g @modelcontextprotocol/server-http
```

## Advanced Configuration

### Multiple MCP Servers

Add multiple GitHub MCP servers for different projects:

```json
{
  "mcpServers": {
    "insightpulse-github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http",
        "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files"
      ]
    },
    "other-project-github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http",
        "https://insightpulseai.net/mcp/github?project=otherorg/otherrepo&features=search,files"
      ]
    }
  }
}
```

### Environment Variables

Pass environment variables to the MCP HTTP transport:
```json
{
  "env": {
    "LOG_LEVEL": "debug",
    "TIMEOUT": "30000"
  }
}
```

## Security Notes

- MCP server uses pulser-hub GitHub App for authentication
- No GitHub tokens needed in client configuration
- All operations authorized via GitHub App installation
- Query parameters are informational, not authentication

## Support

- **MCP Server Documentation**: [services/mcp-server/README.md](../../README.md)
- **Query Parameters Guide**: [docs/QUERY_PARAMETERS.md](../../docs/QUERY_PARAMETERS.md)
- **Feature Mapping**: [docs/FEATURE_MAPPING.md](../../docs/FEATURE_MAPPING.md)
- **GitHub Issues**: [jgtolentino/insightpulse-odoo/issues](https://github.com/jgtolentino/insightpulse-odoo/issues)

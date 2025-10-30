# Cursor IDE MCP Setup Guide

Configure Cursor IDE to use the InsightPulse GitHub MCP Server.

## Installation

### Step 1: Locate Cursor MCP Configuration

Cursor MCP servers are configured in:
```
~/.cursor/mcp-settings.json
```

Or in your project's `.cursor` directory:
```
your-project/.cursor/mcp.json
```

### Step 2: Add InsightPulse GitHub MCP Server

Copy the configuration from `mcp.json`:

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

### Step 3: Reload Cursor

After updating the configuration:
1. Restart Cursor IDE
2. Open AI assistant panel
3. Verify MCP server connection (check status)

## Customization

### Project-Specific Configuration

For project-specific GitHub operations, create `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "insightpulse-github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http",
        "https://insightpulseai.net/mcp/github?project=myorg/myproject&features=branches,commits,pr"
      ]
    }
  }
}
```

### Feature Filtering

Limit available tools by adjusting the `features` parameter:

**Development Workflow**:
```
features=branches,commits,pr
```

**Code Review**:
```
features=pr,files,search
```

**CI/CD Integration**:
```
features=workflows,pr
```

**Read-Only**:
```
features=search,files
```

## Available Features

| Feature | GitHub Tools | Description |
|---------|--------------|-------------|
| `branches` | Create branch, List branches | Branch management |
| `commits` | Commit files | Create commits with multiple files |
| `issues` | Create issue, List issues | Issue tracking |
| `pr` | Create PR, List PRs, Merge PR | Pull request workflow |
| `workflows` | Trigger workflow | GitHub Actions automation |
| `search` | Search code | Code search across repository |
| `files` | Read file | Read file contents from repository |

## Testing

### Test MCP Server

In Cursor's AI assistant, try:

```
"List all branches in the insightpulse-odoo repository"
"Create a new branch called test/cursor-mcp from main"
"Search for 'FastAPI' in the codebase"
"Read the contents of README.md"
```

### Verify Tool Access

Ask the AI:
```
"What GitHub operations are available?"
```

Expected response should list the enabled GitHub tools.

## Troubleshooting

### MCP Server Not Available

**Symptom**: AI assistant doesn't recognize GitHub operations

**Solutions**:
1. Verify configuration file exists and has valid JSON
2. Check that `npx` is installed: `npx --version`
3. Restart Cursor IDE completely
4. Check Cursor logs: Help → Show Logs

### HTTP MCP Transport Missing

**Symptom**: Error about `@modelcontextprotocol/server-http` not found

**Solution**:
```bash
npm install -g @modelcontextprotocol/server-http
```

### Connection Timeout

**Symptom**: MCP server connection times out

**Solutions**:
1. Verify MCP server is deployed: `curl https://insightpulseai.net/health`
2. Check network connectivity
3. Try with explicit timeout in configuration:
   ```json
   {
     "command": "npx",
     "args": ["--", "timeout", "30", "npx", "-y", "@modelcontextprotocol/server-http", "..."],
     "timeout": 30000
   }
   ```

### Feature Not Available

**Symptom**: AI says it can't perform a specific operation

**Solutions**:
1. Check that the required feature is in your `features` parameter
2. Verify the operation maps to an available feature (see Feature Mapping table)
3. Try with all features enabled: `features=branches,commits,issues,pr,workflows,search,files`

## Advanced Configuration

### Multiple Repositories

Configure different MCP servers for different projects:

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
    "other-project": {
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

### Environment-Specific Configuration

Use different feature sets for different environments:

**Development**:
```json
{
  "mcpServers": {
    "insightpulse-github-dev": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http",
        "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files"
      ]
    }
  }
}
```

**Production** (read-only):
```json
{
  "mcpServers": {
    "insightpulse-github-prod": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-http",
        "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=search,files"
      ]
    }
  }
}
```

## Security

- **Authentication**: MCP server uses pulser-hub GitHub App (no tokens needed in client)
- **Authorization**: GitHub App permissions control what operations are allowed
- **Scope**: Query parameters define default repository and available features
- **Network**: All communication over HTTPS

## Support

- **MCP Server Documentation**: [../../README.md](../../README.md)
- **Query Parameters**: [../../docs/QUERY_PARAMETERS.md](../../docs/QUERY_PARAMETERS.md)
- **Feature Mapping**: [../../docs/FEATURE_MAPPING.md](../../docs/FEATURE_MAPPING.md)
- **GitHub Issues**: [https://github.com/jgtolentino/insightpulse-odoo/issues](https://github.com/jgtolentino/insightpulse-odoo/issues)

## Tips

1. **Start Simple**: Begin with read-only features (`search,files`) to test connectivity
2. **Incremental**: Add features as needed rather than enabling everything
3. **Project-Specific**: Use `.cursor/mcp.json` in each project for custom configurations
4. **Monitor Usage**: Check Cursor logs to see which tools are being used
5. **Test Locally**: Test MCP server endpoints with curl before configuring Cursor

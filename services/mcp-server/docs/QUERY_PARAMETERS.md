# Query Parameter Reference

Complete reference for MCP server URL query parameters.

## Overview

Query parameters customize MCP server behavior without code changes.

**Base URL**: `https://insightpulseai.net/mcp/github`

## Parameters

### `project`

**Type**: String
**Format**: `owner/repository`
**Default**: `jgtolentino/insightpulse-odoo`
**Required**: No

Sets default repository for all GitHub operations.

**Examples**:
```
?project=jgtolentino/insightpulse-odoo
?project=myorg/myrepo
?project=username/project
```

**Use Cases**:
- Multi-repository MCP server
- Team-specific defaults
- Project-scoped AI assistants

---

### `features`

**Type**: Comma-separated string
**Default**: All features enabled
**Required**: No

Limits available MCP tools to specified features.

**Available Values**:
- `branches` - Branch operations
- `commits` - Commit operations
- `issues` - Issue management
- `pr` - Pull request operations
- `workflows` - GitHub Actions
- `search` - Code search
- `files` - File reading

**Examples**:
```
?features=branches,commits,pr
?features=search,files
?features=workflows
```

**Use Cases**:
- Least privilege access control
- Environment-specific feature sets
- Role-based tool access

---

## Feature to Tool Mapping

| Feature | MCP Tools | Description |
|---------|-----------|-------------|
| `branches` | `github_create_branch`<br>`github_list_branches` | Create and list branches |
| `commits` | `github_commit_files` | Commit multiple files to branch |
| `issues` | `github_create_issue`<br>`github_list_issues` | Create and list issues |
| `pr` | `github_create_pr`<br>`github_list_prs`<br>`github_merge_pr` | Full PR workflow |
| `workflows` | `github_trigger_workflow` | Trigger GitHub Actions |
| `search` | `github_search_code` | Search code in repository |
| `files` | `github_read_file` | Read file contents |

---

## Common Configurations

### Full Development Access
```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files
```
**Use Case**: Full-stack development with all operations available

### Read-Only Analytics
```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=search,files
```
**Use Case**: Code analysis, documentation review, research

### CI/CD Integration
```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=workflows,pr
```
**Use Case**: Automated deployments, workflow triggers

### Code Review
```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=pr,search,files
```
**Use Case**: PR reviews, code analysis

### Issue Triage
```
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=issues,search,files
```
**Use Case**: Bug reporting, feature requests

---

## Security Implications

### Feature Filtering Benefits
- **Least Privilege**: Only enable tools needed
- **Attack Surface Reduction**: Limit exposed functionality
- **Audit Trail**: Track which features are used
- **Multi-Tenancy**: Different clients, different features

### Project Scoping Benefits
- **Repository Isolation**: Limit operations to specific repository
- **Access Control**: Combined with GitHub App permissions
- **Usage Tracking**: Per-project analytics
- **Team Boundaries**: Separate configurations per team

---

## Testing

### Test Health Endpoint
```bash
curl https://insightpulseai.net/health
```

### Test Feature Filtering
```bash
curl -X POST "https://insightpulseai.net/mcp/github?features=branches" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list","params":{}}'
```

**Expected**: Only branch tools listed

### Test Project Parameter
```bash
curl -X POST "https://insightpulseai.net/mcp/github?project=myorg/myrepo" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/call","params":{"name":"github_list_branches","arguments":{}}}'
```

**Expected**: Branches from `myorg/myrepo`

---

## Validation Rules

### Project Format
- **Valid**: `owner/repo`, `username/repository`
- **Invalid**: `repo-only`, `owner/`, `/repo`, `owner/repo/extra`

**Validation**: Server parses into owner and repository name

### Features List
- **Valid**: Comma-separated, lowercase, known features
- **Invalid**: Unknown features ignored, empty string disables filtering

**Validation**: Server filters to known features, falls back to all tools if no valid features

---

## Examples

### Multiple Projects in Same Client

**Claude Code `config.json`**:
```json
{
  "mcpServers": {
    "insightpulse": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-http", "https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,pr"]
    },
    "docs-site": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-http", "https://insightpulseai.net/mcp/github?project=jgtolentino/docs&features=search,files"]
    }
  }
}
```

### Role-Based Access

**Developer**:
```
?features=branches,commits,issues,pr,workflows,search,files
```

**Reviewer**:
```
?features=pr,search,files
```

**CI/CD Bot**:
```
?features=workflows,pr
```

**Analyst**:
```
?features=search,files
```

---

**Last Updated**: 2025-10-30
**Version**: 1.0.0

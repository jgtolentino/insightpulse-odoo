# MCP Server for GitHub Operations - Complete Reference

**Model Context Protocol (MCP) Server** for AI-driven GitHub operations via pulser-hub GitHub App.

---

## 🎯 Overview

This MCP server enables AI assistants (Claude, ChatGPT) to perform GitHub operations directly through conversation, similar to Supabase's MCP implementation.

### What is MCP?

**Model Context Protocol** is a standard for AI assistants to interact with external tools and services. It allows Claude Code and other AI assistants to:

- Call external APIs
- Perform actions in external systems
- Access real-time data
- Automate workflows

### What This MCP Server Provides

**11 GitHub Operations**:
- Repository management (branches, files)
- Pull request workflows (create, list, merge)
- Issue tracking (create, list)
- Workflow automation (trigger GitHub Actions)
- Code search

**Architecture**:
```
AI Assistant → MCP Protocol → MCP Server → GitHub API → GitHub Repository
```

**Result**: Complete AI-driven GitHub automation from chat!

---

## 🛠️ Available Tools

### 1. `github_create_branch`

**Description**: Create a new branch in a repository

**Input**:
```json
{
  "repo": "owner/name",
  "branch": "feature/new-feature",
  "from_branch": "main"  // optional, default: "main"
}
```

**Output**:
```json
{
  "branch": "feature/new-feature",
  "sha": "abc123...",
  "url": "https://api.github.com/repos/owner/name/git/refs/heads/feature/new-feature"
}
```

**Example Usage**:
```
You: "Create a branch called feature/authentication from develop"
Claude: [Calls github_create_branch(repo, branch, from_branch)]
Claude: "✅ Created branch feature/authentication from develop (SHA: abc123)"
```

---

### 2. `github_commit_files`

**Description**: Commit multiple files to a branch

**Input**:
```json
{
  "repo": "owner/name",
  "branch": "feature/new-feature",
  "files": [
    {
      "path": "src/auth.py",
      "content": "def authenticate():\n    pass"
    },
    {
      "path": "tests/test_auth.py",
      "content": "def test_auth():\n    pass"
    }
  ],
  "message": "Add authentication module"
}
```

**Output**:
```json
{
  "commit_sha": "def456...",
  "files_committed": 2,
  "message": "Add authentication module"
}
```

**Example Usage**:
```
You: "Commit these 3 files to feature-branch with message 'Add feature X'"
Claude: [Calls github_commit_files(repo, branch, files, message)]
Claude: "✅ Committed 3 files to feature-branch (SHA: def456)"
```

---

### 3. `github_create_pr`

**Description**: Create a pull request

**Input**:
```json
{
  "repo": "owner/name",
  "title": "Add authentication feature",
  "head": "feature/authentication",
  "base": "main",  // optional, default: "main"
  "body": "This PR adds user authentication with JWT tokens"  // optional
}
```

**Output**:
```json
{
  "number": 127,
  "url": "https://github.com/owner/name/pull/127",
  "state": "open"
}
```

**Example Usage**:
```
You: "Create a PR titled 'Add authentication' from feature/auth to develop"
Claude: [Calls github_create_pr(repo, title, head, base)]
Claude: "✅ Created PR #127: https://github.com/.../pull/127"
```

---

### 4. `github_list_prs`

**Description**: List pull requests in a repository

**Input**:
```json
{
  "repo": "owner/name",
  "state": "open"  // optional: "open", "closed", "all" (default: "open")
}
```

**Output**:
```json
[
  {
    "number": 127,
    "title": "Add authentication feature",
    "state": "open",
    "author": "jgtolentino",
    "url": "https://github.com/owner/name/pull/127"
  },
  ...
]
```

**Example Usage**:
```
You: "List all open PRs"
Claude: [Calls github_list_prs(repo, state="open")]
Claude: "Found 5 open PRs:\n- #127: Add authentication (by jgtolentino)\n- #126: Fix bug (by user2)"
```

---

### 5. `github_merge_pr`

**Description**: Merge a pull request

**Input**:
```json
{
  "repo": "owner/name",
  "pr_number": 127,
  "method": "merge"  // optional: "merge", "squash", "rebase" (default: "merge")
}
```

**Output**:
```json
{
  "merged": true,
  "sha": "ghi789...",
  "message": "Pull request successfully merged"
}
```

**Example Usage**:
```
You: "Merge PR #127 using squash method"
Claude: [Calls github_merge_pr(repo, pr_number=127, method="squash")]
Claude: "✅ Merged PR #127 (SHA: ghi789)"
```

---

### 6. `github_create_issue`

**Description**: Create an issue in a repository

**Input**:
```json
{
  "repo": "owner/name",
  "title": "Bug: Authentication fails on login",
  "body": "Steps to reproduce:\n1. Go to /login\n2. Enter credentials\n3. Click submit\n\nExpected: Login success\nActual: 500 error"
}
```

**Output**:
```json
{
  "number": 45,
  "url": "https://github.com/owner/name/issues/45",
  "state": "open"
}
```

**Example Usage**:
```
You: "Create an issue titled 'Bug in authentication' with description..."
Claude: [Calls github_create_issue(repo, title, body)]
Claude: "✅ Created issue #45: https://github.com/.../issues/45"
```

---

### 7. `github_list_issues`

**Description**: List issues in a repository

**Input**:
```json
{
  "repo": "owner/name",
  "state": "open"  // optional: "open", "closed", "all" (default: "open")
}
```

**Output**:
```json
[
  {
    "number": 45,
    "title": "Bug: Authentication fails on login",
    "state": "open",
    "author": "jgtolentino",
    "url": "https://github.com/owner/name/issues/45"
  },
  ...
]
```

**Example Usage**:
```
You: "Show me all open issues"
Claude: [Calls github_list_issues(repo, state="open")]
Claude: "Found 8 open issues:\n- #45: Bug: Authentication (by jgtolentino)\n- #44: Feature request (by user2)"
```

---

### 8. `github_trigger_workflow`

**Description**: Trigger a GitHub Actions workflow

**Input**:
```json
{
  "repo": "owner/name",
  "workflow_id": "odoo-module-tools.yml",
  "ref": "main",  // optional, default: "main"
  "inputs": {  // optional
    "module": "insightpulse",
    "action": "bump_version"
  }
}
```

**Output**:
```json
{
  "workflow_id": "odoo-module-tools.yml",
  "ref": "main",
  "status": "triggered"
}
```

**Example Usage**:
```
You: "Trigger the module-tools workflow with action bump_version"
Claude: [Calls github_trigger_workflow(repo, workflow_id, inputs)]
Claude: "✅ Triggered workflow odoo-module-tools.yml on main branch"
```

---

### 9. `github_read_file`

**Description**: Read file contents from a repository

**Input**:
```json
{
  "repo": "owner/name",
  "path": "src/auth.py",
  "ref": "main"  // optional: branch/tag/SHA, default: "main"
}
```

**Output**:
```json
{
  "path": "src/auth.py",
  "content": "def authenticate():\n    pass",
  "sha": "jkl012...",
  "size": 1024
}
```

**Example Usage**:
```
You: "Show me the contents of src/auth.py"
Claude: [Calls github_read_file(repo, path)]
Claude: "File contents:\n\`\`\`python\ndef authenticate():\n    pass\n\`\`\`"
```

---

### 10. `github_list_branches`

**Description**: List all branches in a repository

**Input**:
```json
{
  "repo": "owner/name"
}
```

**Output**:
```json
[
  {
    "name": "main",
    "sha": "mno345...",
    "protected": true
  },
  {
    "name": "develop",
    "sha": "pqr678...",
    "protected": false
  },
  ...
]
```

**Example Usage**:
```
You: "List all branches in the repo"
Claude: [Calls github_list_branches(repo)]
Claude: "Found 15 branches:\n- main (protected)\n- develop\n- feature/auth\n- feature/dashboard"
```

---

### 11. `github_search_code`

**Description**: Search code in a repository

**Input**:
```json
{
  "repo": "owner/name",
  "query": "authenticate"
}
```

**Output**:
```json
[
  {
    "path": "src/auth.py",
    "url": "https://github.com/owner/name/blob/main/src/auth.py",
    "repository": "owner/name"
  },
  ...
]
```

**Example Usage**:
```
You: "Search for 'authenticate' in the code"
Claude: [Calls github_search_code(repo, query)]
Claude: "Found 8 results:\n- src/auth.py\n- tests/test_auth.py\n- docs/AUTH.md"
```

---

## 🚀 Deployment

### Prerequisites

1. **GitHub App (pulser-hub)** - Already configured
   - App ID: 2191216
   - Installed on repository

2. **Private Key** - Generate from GitHub
   - Go to https://github.com/settings/apps/pulser-hub
   - Generate private key (download .pem file)

3. **Installation ID** - Find in GitHub
   - Go to https://github.com/settings/installations
   - Click "Configure" next to pulser-hub
   - Check URL: `/installations/<ID>`

### Deployment Options

#### Option 1: DigitalOcean App Platform (Recommended)

**Step 1**: Create App
```bash
cd services/mcp-server
doctl apps create --spec app.yaml
```

**Step 2**: Configure Secrets (DigitalOcean Dashboard)
1. Go to App Settings → Environment Variables
2. Add `GITHUB_PRIVATE_KEY`:
   - Type: SECRET
   - Value: Contents of your .pem file
3. Add `GITHUB_INSTALLATION_ID`:
   - Type: SECRET
   - Value: Your installation ID

**Step 3**: Deploy
- Auto-deploys on push to main branch
- Or trigger manually in dashboard

**Step 4**: Verify
```bash
curl https://mcp.insightpulseai.net/health
```

#### Option 2: Docker

**Step 1**: Build
```bash
cd services/mcp-server
docker build -t pulser-hub-mcp .
```

**Step 2**: Run
```bash
docker run -d -p 8000:8000 \
  --name mcp-server \
  -e GITHUB_APP_ID=2191216 \
  -e GITHUB_PRIVATE_KEY="$(cat private-key.pem)" \
  -e GITHUB_INSTALLATION_ID=your_id \
  pulser-hub-mcp
```

**Step 3**: Verify
```bash
curl http://localhost:8000/health
```

#### Option 3: Local Development

**Step 1**: Install Dependencies
```bash
cd services/mcp-server
pip install -r requirements.txt
```

**Step 2**: Configure Environment
```bash
export GITHUB_APP_ID=2191216
export GITHUB_PRIVATE_KEY="$(cat private-key.pem)"
export GITHUB_INSTALLATION_ID=your_id
```

**Step 3**: Run Server
```bash
python server.py
# Server starts at http://localhost:8000
```

**Step 4**: Test
```bash
curl http://localhost:8000/health
./test_mcp.sh http://localhost:8000
```

---

## 🔌 Integration with AI Assistants

### Claude Code Integration

**Step 1**: Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "pulser-hub": {
      "url": "https://mcp.insightpulseai.net/mcp/github",
      "description": "GitHub operations via pulser-hub app"
    }
  }
}
```

**Step 2**: Reload Claude Code
- Restart Claude Code
- MCP server will be available automatically

**Step 3**: Test
```
You: "List all branches in jgtolentino/insightpulse-odoo"
Claude: [Uses MCP server] → github_list_branches()
Claude: "Found 15 branches: main, develop, feature/auth, ..."
```

### Claude Desktop Integration

**Step 1**: Open Claude Desktop settings
**Step 2**: Add MCP server configuration (same as above)
**Step 3**: Restart Claude Desktop

### ChatGPT Integration (via Custom GPT)

**Step 1**: Create Custom GPT
- Name: "GitHub Operations"
- Description: "Perform GitHub operations via pulser-hub"

**Step 2**: Add Actions
- Import OpenAPI spec (generate from MCP server)
- Configure authentication

**Step 3**: Test
```
You: "Create a PR for my changes"
ChatGPT: [Calls MCP server] → github_create_pr()
```

---

## 🔐 Security

### Authentication Flow

1. **Private Key Storage**: Stored as environment variable (SECRET in DigitalOcean)
2. **JWT Generation**: Server generates short-lived JWT (10 min expiry)
3. **Installation Token**: Exchange JWT for installation access token (60 min expiry)
4. **Token Caching**: Cache installation token for 50 minutes (refresh before expiry)
5. **API Requests**: Use cached installation token for GitHub API calls

### Security Features

- ✅ **Private Key Protection**: Never exposed in logs or responses
- ✅ **Short-Lived JWTs**: 10-minute expiry reduces exposure window
- ✅ **Token Caching**: Minimizes API calls and improves performance
- ✅ **HTTPS Required**: Production deployment enforces HTTPS
- ✅ **Non-Root Container**: Docker runs as non-root user
- ✅ **Rate Limiting**: Respects GitHub API limits (5000/hour)
- ✅ **Audit Logging**: All requests logged for monitoring

### Security Best Practices

1. **Rotate Private Keys**: Generate new key every 90 days
2. **Monitor Installations**: Review installed apps regularly
3. **Separate Environments**: Use different installations for dev/staging/prod
4. **Least Privilege**: Grant minimum required permissions to GitHub App
5. **Secret Management**: Use DigitalOcean SECRET type for sensitive values
6. **Access Logs**: Monitor server logs for suspicious activity

---

## 📊 Monitoring & Observability

### Health Check

```bash
curl https://mcp.insightpulseai.net/health
```

**Response**:
```json
{
  "status": "healthy",
  "app_id": "2191216",
  "has_private_key": true,
  "installation_id": "12345678"
}
```

### Logging

Server logs all requests to stdout:

```
2025-10-30 14:00:00 - INFO - MCP Request: tools/list
2025-10-30 14:00:05 - INFO - GET https://api.github.com/repos/owner/repo/branches
2025-10-30 14:00:06 - INFO - Installation token cached until 2025-10-30 14:50:00
2025-10-30 14:00:10 - ERROR - Tool execution error: Repository not found
```

### DigitalOcean Monitoring

**View Logs**:
```bash
doctl apps logs <app-id> --follow
```

**Metrics Dashboard**:
- CPU usage
- Memory usage
- Request rate
- Error rate
- Response time

**Alerts** (configure in DO dashboard):
- Health check failures
- High error rate
- Resource exhaustion

---

## 🐛 Troubleshooting

### Common Issues

#### Issue 1: Authentication Failed
**Symptom**: "401 Unauthorized" errors

**Causes**:
- Invalid private key
- Wrong installation ID
- Expired token (clock skew)

**Solutions**:
1. Verify private key format (must start with `-----BEGIN RSA PRIVATE KEY-----`)
2. Regenerate private key in GitHub App settings
3. Verify installation ID at https://github.com/settings/installations
4. Check system clock synchronization

#### Issue 2: Rate Limiting
**Symptom**: "403 Rate limit exceeded" errors

**Causes**:
- Too many API calls (>5000/hour)
- Multiple clients using same installation

**Solutions**:
1. Wait for rate limit reset (check `X-RateLimit-Reset` header)
2. Implement request queuing in clients
3. Use multiple GitHub Apps for higher limits
4. Cache responses when possible

#### Issue 3: Server Crashes
**Symptom**: Container restarts, 502 errors

**Causes**:
- Memory exhaustion
- Unhandled exceptions
- Database connection issues (none in this case)

**Solutions**:
1. Check logs: `doctl apps logs <app-id> --tail 100`
2. Increase instance size if memory issues
3. Review error logs for stack traces
4. Ensure all environment variables are set

#### Issue 4: Slow Response Times
**Symptom**: Timeouts, slow tool calls

**Causes**:
- GitHub API latency
- Large file reads
- Network issues

**Solutions**:
1. Increase timeout in client configuration
2. Use pagination for large result sets
3. Implement caching for frequently accessed data
4. Monitor GitHub API status page

---

## 📚 Related Documentation

- [MCP Server README](../services/mcp-server/README.md) - Quick start guide
- [GitHub App Setup](./GITHUB_APP_SETUP.md) - pulser-hub configuration
- [GitHub Bot Documentation](./GITHUB_BOT.md) - GitHub Actions automation
- [Odoo Integration](../addons/insightpulse/ops/github_integration/) - Webhook handlers
- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/) - MCP standard

---

## 🎉 Complete Integration

With the MCP server deployed, you now have **complete bidirectional GitHub automation**:

### Before MCP Server
```
GitHub → (webhooks) → Odoo  ✅
Odoo → (manual) → GitHub    ❌
AI → (manual) → GitHub       ❌
```

### After MCP Server
```
GitHub → (webhooks) → Odoo  ✅
Odoo → (MCP) → GitHub        ✅
AI → (MCP) → GitHub          ✅
```

**Result**: Full automation from chat, code, and Odoo! 🚀

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-10-30

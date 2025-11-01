# MCP Server for GitHub Operations (pulser-hub)

Model Context Protocol (MCP) server that exposes GitHub operations through the pulser-hub GitHub App, enabling AI assistants (Claude, ChatGPT) to perform GitHub actions directly.

---

## 🎯 What This Does

Enables **AI-driven GitHub operations** from chat:

```
You: "Create a PR for the authentication feature"
Claude: [Calls MCP server → github_create_pr()]
Claude: "✅ Created PR #125: https://github.com/.../pull/125"
```

**No manual GitHub actions needed!**

---

## 📦 Available Operations (11 Tools)

### Repository Operations
- `github_create_branch` - Create new branches
- `github_list_branches` - List all branches
- `github_read_file` - Read file contents

### Pull Request Operations
- `github_create_pr` - Create pull requests
- `github_list_prs` - List pull requests
- `github_merge_pr` - Merge pull requests

### Issue Operations
- `github_create_issue` - Create issues
- `github_list_issues` - List issues

### Workflow Operations
- `github_trigger_workflow` - Trigger GitHub Actions workflows

### File Operations
- `github_commit_files` - Commit multiple files to a branch

### Search Operations
- `github_search_code` - Search code in repository

---

## 🚀 Quick Start

### Option 1: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GITHUB_APP_ID=2191216
export GITHUB_PRIVATE_KEY="$(cat path/to/private-key.pem)"
export GITHUB_INSTALLATION_ID=your_installation_id

# Run server
python server.py

# Test
curl http://localhost:8000/health
./test_mcp.sh http://localhost:8000
```

### Option 2: Docker

```bash
# Build
docker build -t pulser-hub-mcp .

# Run
docker run -p 8000:8000 \
  -e GITHUB_APP_ID=2191216 \
  -e GITHUB_PRIVATE_KEY="$(cat private-key.pem)" \
  -e GITHUB_INSTALLATION_ID=your_id \
  pulser-hub-mcp

# Test
curl http://localhost:8000/health
```

### Option 3: DigitalOcean App Platform (Production)

```bash
# Create app
doctl apps create --spec app.yaml

# Configure secrets in DO dashboard
# - GITHUB_PRIVATE_KEY (PEM format)
# - GITHUB_INSTALLATION_ID

# Deploy
# Auto-deploys on push to main branch
```

---

## 🔧 Configuration

### Required Environment Variables

```bash
# GitHub App ID (pulser-hub)
GITHUB_APP_ID=2191216

# GitHub App Private Key (PEM format)
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----"

# Installation ID (find in GitHub settings)
GITHUB_INSTALLATION_ID=12345678
```

### Optional Configuration

```bash
# Server port (default: 8000)
PORT=8000
```

### How to Get Credentials

#### 1. GITHUB_APP_ID
Already set: `2191216` (pulser-hub app)

#### 2. GITHUB_PRIVATE_KEY
1. Go to https://github.com/settings/apps/pulser-hub
2. Scroll to "Private keys"
3. Click "Generate a private key"
4. Download .pem file
5. Use file contents as environment variable

#### 3. GITHUB_INSTALLATION_ID
1. Go to https://github.com/settings/installations
2. Click "Configure" next to pulser-hub
3. Check URL: `/installations/<ID>`
4. Use that ID

---

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "app_id": "2191216",
#   "has_private_key": true,
#   "installation_id": "12345678"
# }
```

### List Available Tools
```bash
curl -X POST http://localhost:8000/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
```

### Call a Tool (List Branches)
```bash
curl -X POST http://localhost:8000/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "github_list_branches",
      "arguments": {
        "repo": "jgtolentino/insightpulse-odoo"
      }
    },
    "id": 2
  }'
```

### Automated Tests
```bash
# Test against local server
./test_mcp.sh http://localhost:8000

# Test with specific repository
REPO=owner/repo ./test_mcp.sh http://localhost:8000
```

---

## 🔌 Integration with Claude Code

### Add to `.cursor/mcp.json`:

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

Or for local development:

```json
{
  "mcpServers": {
    "pulser-hub": {
      "url": "http://localhost:8000/mcp/github"
    }
  }
}
```

### Usage in Claude Code

Once configured, I (Claude) can perform GitHub operations directly:

```
You: "List all branches in the repo"
Claude: [Uses pulser-hub MCP] → github_list_branches()
Claude: "Found 15 branches: main, develop, feature/auth, ..."

You: "Create a PR for the feature/auth branch"
Claude: [Uses pulser-hub MCP] → github_create_pr()
Claude: "✅ Created PR #127: https://github.com/.../pull/127"
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│ AI Assistant (Claude Code / Claude Desktop)│
│ └─ MCP client configured                   │
└────────────┬────────────────────────────────┘
             │ MCP Protocol (JSON-RPC)
             ↓
┌─────────────────────────────────────────────┐
│ MCP Server (FastAPI)                       │
│ ├─ MCP protocol handler                    │
│ ├─ GitHub API client (JWT auth)           │
│ └─ 11 tool implementations                 │
└────────────┬────────────────────────────────┘
             │ GitHub REST API
             ↓
┌─────────────────────────────────────────────┐
│ GitHub (via pulser-hub app)                │
│ ├─ Creates PRs, commits, etc.             │
│ └─ Sends webhooks back                     │
└────────────┬────────────────────────────────┘
             │ Webhooks
             ↓
┌─────────────────────────────────────────────┐
│ Odoo (/odoo/github/webhook)                │
│ └─ Processes events (existing integration)  │
└─────────────────────────────────────────────┘
```

**Complete bidirectional integration!**
- GitHub → Odoo (webhooks - existing)
- AI → GitHub (MCP server - new!)
- Odoo → GitHub (uses MCP server)

---

## 🔐 Security

### Authentication Flow
1. **JWT Token Generation**: Server generates JWT using private key
2. **Installation Token**: Exchange JWT for installation access token
3. **API Requests**: Use installation token for GitHub API calls
4. **Token Caching**: Cache tokens for 50 minutes (refresh before 60-min expiry)

### Security Features
- ✅ Private key stored as environment variable (never in code)
- ✅ JWT tokens expire in 10 minutes
- ✅ Installation tokens expire in 60 minutes (cached 50 min)
- ✅ Non-root user in Docker container
- ✅ HTTPS required in production
- ✅ Rate limiting follows GitHub API limits (5000/hour)

### Security Best Practices
1. Never commit private key to git
2. Use DigitalOcean SECRET type for GITHUB_PRIVATE_KEY
3. Rotate private keys periodically
4. Monitor GitHub App installations
5. Use separate installations for dev/staging/prod

---

## 📊 Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Returns server status and configuration (without secrets).

### Logging
Server logs all requests and errors to stdout:

```
2025-10-30 14:00:00 - INFO - MCP Request: tools/list
2025-10-30 14:00:05 - INFO - GET https://api.github.com/repos/owner/repo/branches
2025-10-30 14:00:06 - INFO - Installation token cached until 2025-10-30 14:50:00
```

### DigitalOcean Monitoring
- View logs: `doctl apps logs <app-id> --follow`
- View metrics: App Platform dashboard
- Health checks: Automatic via app.yaml configuration

---

## 🐛 Troubleshooting

### Issue: Server fails to start
**Cause**: Missing or invalid environment variables

**Solution**:
```bash
# Check configuration
echo "App ID: $GITHUB_APP_ID"
echo "Has key: ${GITHUB_PRIVATE_KEY:+YES}"
echo "Installation ID: $GITHUB_INSTALLATION_ID"

# Verify private key format
echo "$GITHUB_PRIVATE_KEY" | head -1  # Should be: -----BEGIN RSA PRIVATE KEY-----
```

### Issue: Authentication errors
**Cause**: Invalid private key or installation ID

**Solution**:
1. Regenerate private key in GitHub App settings
2. Verify installation ID at https://github.com/settings/installations
3. Check logs for specific JWT errors

### Issue: Rate limiting
**Cause**: Exceeded GitHub API rate limit (5000/hour)

**Solution**:
1. Wait for rate limit reset (check response headers)
2. Implement request queuing in clients
3. Use multiple GitHub Apps for higher limits

### Issue: Token expiry errors
**Cause**: Token cache expired or clock skew

**Solution**:
1. Server automatically refreshes tokens
2. Check system clock is synchronized
3. Review token cache logs

---

## 📚 Related Documentation

- [Main MCP Server Documentation](../../docs/MCP_SERVER.md) - Complete reference
- [GitHub App Setup](../../docs/GITHUB_APP_SETUP.md) - pulser-hub configuration
- [Odoo Integration](../../addons/insightpulse/ops/github_integration/) - Webhook handlers

---

## 🤝 Contributing

Contributions welcome! Please:
1. Test locally before submitting PR
2. Run `./test_mcp.sh` to verify functionality
3. Update documentation for new tools
4. Follow existing code style

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2025-10-30

# pulser-hub GitHub App Setup Guide

Complete guide to connect your **pulser-hub** GitHub App with the InsightPulse infrastructure.

## 🎯 What is pulser-hub?

**pulser-hub** is your custom GitHub App that enables:
- AI-driven GitHub operations (via MCP server)
- Automated deployments
- Repository automation
- Issue/PR management
- Workflow triggers

**Current Status:** ✅ Installed on your account (never used yet)

---

## 🔑 Step 1: Get Your pulser-hub Credentials

### A. Find Your App ID

1. Go to: https://github.com/settings/apps
2. Click **pulser-hub**
3. Look for **App ID** (top of the page)
4. Copy the number (e.g., `123456`)

### B. Get Installation ID

**Method 1: From URL**
1. Go to: https://github.com/settings/installations
2. Click **Configure** next to pulser-hub
3. Look at the URL: `https://github.com/settings/installations/[INSTALLATION_ID]`
4. Copy the installation ID number

**Method 2: Using GitHub CLI**
```bash
# Install gh CLI if needed
brew install gh  # macOS
# or: sudo apt install gh  # Linux

# Authenticate
gh auth login

# Get installations
gh api /user/installations
# Look for pulser-hub in the output, copy the "id" field
```

**Method 3: Using API**
```bash
# Get your personal access token from:
# https://github.com/settings/tokens

curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.github.com/user/installations \
  | jq '.installations[] | select(.app_slug=="pulser-hub") | .id'
```

### C. Generate Private Key

1. Go to: https://github.com/settings/apps/pulser-hub
2. Scroll to **Private keys**
3. Click **Generate a private key**
4. Save the downloaded `.pem` file securely
5. **IMPORTANT:** Never commit this file to git!

---

## 📝 Step 2: Configure MCP Server

### Update MCP Server Configuration

Edit `services/mcp-server/.env`:

```bash
cd services/mcp-server

# Create .env file
cat > .env << 'EOF'
# pulser-hub GitHub App Configuration
GITHUB_APP_ID=YOUR_APP_ID_HERE
GITHUB_INSTALLATION_ID=YOUR_INSTALLATION_ID_HERE

# Private key (paste entire key including BEGIN/END lines)
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
YOUR_KEY_CONTENT_HERE
-----END RSA PRIVATE KEY-----"

# Server configuration
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=info
EOF

# Secure the file
chmod 600 .env
```

**Example:**
```bash
GITHUB_APP_ID=123456
GITHUB_INSTALLATION_ID=98765432
GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
...long key content...
...ends with...
-----END RSA PRIVATE KEY-----"
```

### Update server.py (if needed)

Check the App ID in `services/mcp-server/server.py`:

```python
# Line 30 - Update if different from 2191216
GITHUB_APP_ID = int(os.getenv("GITHUB_APP_ID", "YOUR_ACTUAL_APP_ID"))
```

---

## 🚀 Step 3: Deploy MCP Server

You have 3 deployment options:

### Option A: DigitalOcean App Platform (Recommended)

**1. Update app.yaml**

```bash
cd services/mcp-server
nano app.yaml
```

Add your App ID:
```yaml
envs:
  - key: GITHUB_APP_ID
    value: "123456"  # Your actual App ID
    scope: RUN_TIME
```

**2. Deploy**
```bash
# Using doctl
doctl apps create --spec app.yaml

# Get the app ID
APP_ID=$(doctl apps list --format ID --no-header | head -1)

# Add secrets in dashboard
echo "Go to: https://cloud.digitalocean.com/apps/$APP_ID"
echo "Settings → Environment Variables → Add:"
echo "  - GITHUB_PRIVATE_KEY (paste your key)"
echo "  - GITHUB_INSTALLATION_ID (your installation ID)"
```

**3. Verify deployment**
```bash
# Get app URL
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)

# Test health
curl https://$APP_URL/health
# Should return: {"status": "healthy", "app_id": 123456}
```

### Option B: Local Development

```bash
cd services/mcp-server

# Install dependencies
pip install -r requirements.txt

# Create .env (see Step 2)
nano .env

# Run server
python server.py

# Test
curl http://localhost:8000/health
```

### Option C: Docker

```bash
cd services/mcp-server

# Build
docker build -t pulser-hub-mcp .

# Run with environment variables
docker run -d --name pulser-hub-mcp \
  -p 8000:8000 \
  -e GITHUB_APP_ID=123456 \
  -e GITHUB_INSTALLATION_ID=98765432 \
  -e GITHUB_PRIVATE_KEY="$(cat /path/to/private-key.pem)" \
  pulser-hub-mcp

# Check logs
docker logs -f pulser-hub-mcp

# Test
curl http://localhost:8000/health
```

---

## 🧪 Step 4: Test pulser-hub Integration

### Test 1: Health Check

```bash
# Replace with your MCP server URL
MCP_URL="https://your-mcp-server.ondigitalocean.app"

curl $MCP_URL/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "app_id": 123456
}
```

### Test 2: List Available Tools

```bash
curl -X POST $MCP_URL/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/list",
    "params": {}
  }'
```

**Expected output:**
```json
{
  "result": [
    {
      "name": "github_create_branch",
      "description": "Create a new branch from base branch",
      ...
    },
    {
      "name": "github_create_pr",
      "description": "Create a pull request",
      ...
    }
  ]
}
```

### Test 3: List Branches (Real GitHub Operation)

```bash
curl -X POST $MCP_URL/mcp/github \
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

**Expected output:**
```json
{
  "result": [
    {"name": "main", "sha": "abc123..."},
    {"name": "claude/code-quality-audit-improvements-011CUeg3N1EoL3A9w1XSi41M", "sha": "def456..."}
  ]
}
```

### Test 4: Create an Issue (Full Integration Test)

```bash
curl -X POST $MCP_URL/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "github_create_issue",
      "arguments": {
        "repo": "jgtolentino/insightpulse-odoo",
        "title": "Test: pulser-hub MCP Integration",
        "body": "This issue was created via pulser-hub MCP server to test integration.",
        "labels": ["test", "automation"]
      }
    }
  }'
```

Check GitHub: https://github.com/jgtolentino/insightpulse-odoo/issues

---

## 🤖 Step 5: Connect to AI Assistants

### A. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pulser-hub": {
      "url": "https://your-mcp-server.ondigitalocean.app/mcp/github",
      "description": "GitHub operations for insightpulse-odoo"
    }
  }
}
```

**On Windows:**
`%APPDATA%\Claude\claude_desktop_config.json`

**On Linux:**
`~/.config/claude/claude_desktop_config.json`

### B. Configure Claude Code (VS Code Extension)

Copy `.claude/mcp-config.json` to your project:

```bash
mkdir -p .claude
cat > .claude/mcp-config.json << 'EOF'
{
  "mcpServers": {
    "pulser-hub": {
      "url": "https://your-mcp-server.ondigitalocean.app/mcp/github",
      "description": "GitHub operations via pulser-hub"
    }
  }
}
EOF
```

### C. Test AI Integration

**In Claude Desktop:**
```
You: "List all branches in jgtolentino/insightpulse-odoo"

Claude: [Uses pulser-hub MCP server]
Found 15 branches:
- main
- claude/code-quality-audit-improvements-011CUeg3N1EoL3A9w1XSi41M
- feature/new-module
...
```

**More examples:**
```
You: "Create a PR for my changes"
Claude: [Creates branch, commits, opens PR via pulser-hub]

You: "Show me all open issues with label 'bug'"
Claude: [Lists issues via GitHub API through pulser-hub]

You: "Merge PR #123 if all checks pass"
Claude: [Checks status, merges PR via pulser-hub]
```

---

## 🔧 Step 6: Integrate with Odoo (Optional)

### A. Add Webhook Handler in Odoo

```python
# addons/github_integration/controllers/webhook.py
from odoo import http
import hmac
import hashlib

class GitHubWebhook(http.Controller):
    @http.route('/oauth/callback', type='http', auth='public', methods=['GET', 'POST'])
    def github_callback(self, **kwargs):
        """Handle GitHub OAuth callback from pulser-hub"""
        code = kwargs.get('code')
        state = kwargs.get('state')

        # Exchange code for access token
        # Store installation_id in Odoo
        # Redirect to success page

        return http.request.redirect('/web')

    @http.route('/github/webhook', type='json', auth='public', csrf=False)
    def github_webhook(self, **kwargs):
        """Handle GitHub webhooks from pulser-hub"""
        payload = http.request.jsonrequest

        # Verify webhook signature
        signature = http.request.httprequest.headers.get('X-Hub-Signature-256')

        # Process events: push, pull_request, issues, etc.
        event_type = payload.get('action')

        # Store in Odoo (e.g., create issue, update task, etc.)

        return {'status': 'success'}
```

### B. Configure Odoo to Use pulser-hub

```python
# addons/github_integration/models/github_config.py
from odoo import models, fields

class GitHubConfig(models.Model):
    _name = 'github.config'

    name = fields.Char("Configuration Name")
    app_id = fields.Char("GitHub App ID")
    installation_id = fields.Char("Installation ID")
    private_key = fields.Text("Private Key", required=True)
    webhook_secret = fields.Char("Webhook Secret")
    mcp_server_url = fields.Char("MCP Server URL")
```

---

## 📊 Monitoring & Troubleshooting

### Check MCP Server Logs

**DigitalOcean:**
```bash
doctl apps logs $APP_ID --type RUN --follow
```

**Docker:**
```bash
docker logs -f pulser-hub-mcp
```

**Local:**
```bash
# Logs are in console
python server.py
```

### Common Issues

#### 1. "Invalid JWT signature"

**Cause:** Wrong App ID or private key format

**Fix:**
```bash
# Verify App ID
cat services/mcp-server/.env | grep APP_ID

# Check private key format (must have BEGIN/END lines)
cat /path/to/private-key.pem | head -1
# Should show: -----BEGIN RSA PRIVATE KEY-----
```

#### 2. "Installation not found"

**Cause:** Wrong installation ID

**Fix:**
```bash
# Get correct installation ID
gh api /user/installations | jq '.installations[] | .id'

# Update .env
nano services/mcp-server/.env
```

#### 3. "403 Forbidden" when accessing repo

**Cause:** pulser-hub doesn't have access to repository

**Fix:**
1. Go to: https://github.com/settings/installations
2. Click **Configure** next to pulser-hub
3. Under **Repository access**, select:
   - All repositories, OR
   - Select repositories → Add `insightpulse-odoo`
4. Save

#### 4. "Rate limit exceeded"

**Cause:** Too many API requests (GitHub limit: 5000/hour)

**Fix:**
- Wait for rate limit reset
- Implement caching in MCP server
- Use conditional requests (ETags)

### Debug Mode

Enable verbose logging:

```bash
# .env
LOG_LEVEL=debug

# Restart server
docker restart pulser-hub-mcp
```

---

## 🔐 Security Best Practices

### 1. Private Key Storage

**DO:**
- ✅ Store in environment variables
- ✅ Use secrets management (DO secrets, AWS Secrets Manager)
- ✅ Restrict file permissions: `chmod 600 private-key.pem`
- ✅ Rotate keys periodically

**DON'T:**
- ❌ Commit to git
- ❌ Share in plain text
- ❌ Store in application code
- ❌ Log the private key

### 2. Webhook Security

```python
# Verify webhook signatures
def verify_signature(payload, signature, secret):
    mac = hmac.new(secret.encode(), payload, hashlib.sha256)
    return hmac.compare_digest(
        f'sha256={mac.hexdigest()}',
        signature
    )
```

### 3. Access Control

- Limit repository access to only what's needed
- Use least-privilege permissions
- Monitor access logs
- Revoke unused installations

### 4. Network Security

- Use HTTPS only
- Enable rate limiting
- Implement request validation
- Use firewall rules

---

## 📚 Available GitHub Operations

Once deployed, pulser-hub MCP server provides these tools:

| Tool | Description |
|------|-------------|
| `github_create_branch` | Create new branch |
| `github_list_branches` | List all branches |
| `github_read_file` | Read file contents |
| `github_commit_files` | Commit multiple files |
| `github_create_pr` | Create pull request |
| `github_list_prs` | List pull requests |
| `github_merge_pr` | Merge pull request |
| `github_create_issue` | Create issue |
| `github_list_issues` | List issues |
| `github_trigger_workflow` | Trigger GitHub Actions |
| `github_search_code` | Search code in repo |

---

## 🎯 Next Steps

After setup:

1. **Test Integration**
   - Create test issue via MCP
   - List branches
   - Read a file

2. **Configure AI Assistants**
   - Set up Claude Desktop
   - Test AI-driven operations

3. **Add to Odoo**
   - Implement webhook handler
   - Store installation in Odoo
   - Sync GitHub ↔ Odoo

4. **Monitor Usage**
   - Check logs
   - Monitor rate limits
   - Track performance

---

## 🆘 Support

- **MCP Server**: [services/mcp-server/README.md](../services/mcp-server/README.md)
- **GitHub Apps**: https://docs.github.com/en/apps
- **Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues

---

**Status:** pulser-hub installed ✅, needs configuration ⏳
**Next:** Get credentials (Step 1) → Configure (Step 2) → Deploy (Step 3)

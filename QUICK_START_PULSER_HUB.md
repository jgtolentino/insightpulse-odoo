# Quick Start: Leverage pulser-hub GitHub App

You have **pulser-hub** installed on your GitHub account. Here's how to activate it in 10 minutes.

## 🎯 What pulser-hub Enables

Once configured, you can:

✅ **AI-driven GitHub operations** - "Claude, create a PR for my changes"
✅ **Automated workflows** - Issue creation, PR management, branch operations
✅ **Odoo ↔ GitHub sync** - Bidirectional integration
✅ **Infrastructure automation** - Trigger deployments, manage releases

## 🚀 Setup in 4 Steps

### Step 1: Get Your Credentials (5 min)

```bash
cd services/mcp-server

# Run automated setup
./setup-pulser-hub.sh

# It will ask for:
# 1. App ID (from https://github.com/settings/apps/pulser-hub)
# 2. Private key path (download from same URL)
# 3. Installation ID (auto-detected or enter manually)
```

**Manual alternative:**

1. **App ID**: Go to https://github.com/settings/apps/pulser-hub → Top of page
2. **Installation ID**:
   ```bash
   gh api /user/installations | jq '.installations[] | select(.app_slug=="pulser-hub") | .id'
   ```
3. **Private Key**: https://github.com/settings/apps/pulser-hub → Generate a private key

### Step 2: Test Locally (2 min)

```bash
cd services/mcp-server

# Install dependencies
pip install -r requirements.txt

# Run server
python server.py

# In another terminal, test:
curl http://localhost:8000/health
# Should return: {"status": "healthy", "app_id": YOUR_APP_ID}

# Test GitHub operation:
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

### Step 3: Deploy to Production (2 min)

**Option A: DigitalOcean (Recommended)**

```bash
# Deploy app
doctl apps create --spec services/mcp-server/app.yaml

# Get app ID
APP_ID=$(doctl apps list --format ID --no-header | head -1)

# Add secrets in dashboard
echo "Add secrets at: https://cloud.digitalocean.com/apps/$APP_ID"
# Settings → Environment Variables:
#   - GITHUB_PRIVATE_KEY (paste from .pem file)
#   - GITHUB_INSTALLATION_ID (your installation ID)
```

**Option B: Docker**

```bash
cd services/mcp-server

docker build -t pulser-hub-mcp .

docker run -d --name pulser-hub \
  -p 8000:8000 \
  --env-file .env \
  pulser-hub-mcp

# Test
curl http://localhost:8000/health
```

### Step 4: Connect to AI (1 min)

**For Claude Desktop:**

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pulser-hub": {
      "url": "https://your-mcp-server.ondigitalocean.app/mcp/github",
      "description": "GitHub ops for insightpulse-odoo"
    }
  }
}
```

**For Claude Code (VS Code):**

Already configured in `.claude/mcp-config.json`! Just update the URL:

```json
{
  "mcpServers": {
    "github-pulser-hub": {
      "url": "https://your-mcp-server.ondigitalocean.app/mcp/github"
    }
  }
}
```

## 🎮 Try It Out

### In Claude Desktop

```
You: "List all branches in insightpulse-odoo"
Claude: [Uses pulser-hub] Found 12 branches: main, claude/..., feature/...

You: "Create an issue titled 'Test pulser-hub integration'"
Claude: [Creates issue] ✅ Issue #45 created: https://github.com/.../issues/45

You: "Show me all open PRs"
Claude: [Lists PRs] You have 3 open pull requests...

You: "Create a PR for my changes with title 'Add new feature'"
Claude: [Creates branch, commits, opens PR] ✅ PR #46 created
```

### In Your Code

```python
# Example: Use pulser-hub in your Odoo addon
import httpx

MCP_URL = "https://your-mcp-server.ondigitalocean.app/mcp/github"

async def create_github_issue(title, body):
    """Create GitHub issue via pulser-hub MCP"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            MCP_URL,
            json={
                "method": "tools/call",
                "params": {
                    "name": "github_create_issue",
                    "arguments": {
                        "repo": "jgtolentino/insightpulse-odoo",
                        "title": title,
                        "body": body,
                        "labels": ["odoo", "automation"]
                    }
                }
            }
        )
        return response.json()

# Usage in Odoo
# When a critical error occurs, auto-create GitHub issue
await create_github_issue(
    "Production Error: Database connection lost",
    "Error details: ..."
)
```

## 📊 What You Can Do

### Repository Operations
- ✅ Create branches
- ✅ List branches
- ✅ Read files
- ✅ Commit multiple files
- ✅ Search code

### Pull Request Operations
- ✅ Create PRs
- ✅ List PRs
- ✅ Merge PRs (with checks)
- ✅ Review PRs
- ✅ Comment on PRs

### Issue Operations
- ✅ Create issues
- ✅ List issues
- ✅ Add labels
- ✅ Close issues
- ✅ Add comments

### Workflow Operations
- ✅ Trigger GitHub Actions
- ✅ Check workflow status
- ✅ Get workflow logs

## 🔧 Troubleshooting

### "Invalid JWT signature"
```bash
# Verify credentials
cat services/mcp-server/.env | grep APP_ID
cat services/mcp-server/.env | grep INSTALLATION_ID

# Regenerate private key if needed
# https://github.com/settings/apps/pulser-hub
```

### "Installation not found"
```bash
# Get correct installation ID
gh api /user/installations | jq '.installations[] | .id'

# Update .env
nano services/mcp-server/.env
# Change GITHUB_INSTALLATION_ID
```

### "403 Forbidden"
```bash
# pulser-hub needs repo access
# Go to: https://github.com/settings/installations
# Click Configure → Select repositories → Add insightpulse-odoo
```

## 📚 Complete Documentation

- **[PULSER_HUB_SETUP.md](docs/PULSER_HUB_SETUP.md)** - Complete setup guide
- **[MCP Server README](services/mcp-server/README.md)** - Technical details
- **[INTEGRATIONS_GUIDE.md](docs/INTEGRATIONS_GUIDE.md)** - All integrations

## 🎯 Next Steps

After setup:

1. **Test all operations**
   ```bash
   cd services/mcp-server
   ./test_mcp.sh http://localhost:8000
   ```

2. **Add to Odoo** (optional)
   - Implement webhook handler
   - Sync issues ↔ tasks
   - Auto-create PRs from Odoo

3. **Automate workflows**
   - Auto-create issues on errors
   - Trigger deploys from Odoo
   - Sync data bidirectionally

4. **Monitor usage**
   ```bash
   # DigitalOcean
   doctl apps logs $APP_ID --type RUN --follow

   # Docker
   docker logs -f pulser-hub
   ```

---

**Status:** pulser-hub installed ✅, needs configuration ⏳

**Quick setup:** `cd services/mcp-server && ./setup-pulser-hub.sh`

**Full guide:** [docs/PULSER_HUB_SETUP.md](docs/PULSER_HUB_SETUP.md)

# 🚀 Activating pulser-hub NOW

Follow these steps to activate your pulser-hub GitHub App and enable AI-driven GitHub operations.

## Step 1: Get Your App ID (30 seconds)

1. Open: https://github.com/settings/apps/pulser-hub
2. Look at the top of the page for **"App ID"**
3. Copy the number (e.g., `123456`)

**Screenshot location:**
```
GitHub Apps
├── pulser-hub
    └── App ID: [YOUR_APP_ID]  ← Copy this!
```

---

## Step 2: Get Installation ID (30 seconds)

**Option A: From URL (Easiest)**
1. Go to: https://github.com/settings/installations
2. Click **Configure** next to pulser-hub
3. Look at the URL: `https://github.com/settings/installations/[INSTALLATION_ID]`
4. Copy the number from the URL

**Option B: Using GitHub CLI**
```bash
gh api /user/installations | jq '.installations[] | select(.app_slug=="pulser-hub") | .id'
```

---

## Step 3: Generate Private Key (1 minute)

1. Go to: https://github.com/settings/apps/pulser-hub
2. Scroll down to **"Private keys"** section
3. Click **"Generate a private key"**
4. A `.pem` file will download to your computer
5. Save it somewhere secure (e.g., `~/Downloads/pulser-hub.pem`)

**IMPORTANT:**
- Never commit this file to git
- Never share it publicly
- You can generate multiple keys if needed

---

## Step 4: Create Configuration (2 minutes)

```bash
cd services/mcp-server

# Copy example
cp .env.example .env

# Edit with your credentials
nano .env
```

**Replace these values in .env:**
```bash
GITHUB_APP_ID=YOUR_APP_ID_FROM_STEP_1
GITHUB_INSTALLATION_ID=YOUR_INSTALLATION_ID_FROM_STEP_2
GITHUB_PRIVATE_KEY="$(cat ~/Downloads/pulser-hub.pem)"
```

**Or use the automated script:**
```bash
./setup-pulser-hub.sh
# It will prompt you for each value
```

**Secure the file:**
```bash
chmod 600 .env
```

---

## Step 5: Test Locally (2 minutes)

```bash
# Still in services/mcp-server/

# Install dependencies
pip install -r requirements.txt

# Run server
python server.py
```

**You should see:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**In another terminal, test:**
```bash
# Test health
curl http://localhost:8000/health
# Expected: {"status": "healthy", "app_id": YOUR_APP_ID}

# Test GitHub operation
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

# Expected: List of all branches in your repo
```

**If you see branch list → ✅ It works!**

---

## Step 6: Deploy to DigitalOcean (5 minutes)

### Option A: Using doctl (Recommended)

```bash
cd services/mcp-server

# Deploy app
doctl apps create --spec app.yaml

# Get app ID
APP_ID=$(doctl apps list --format ID --no-header | grep -v insightpulse-odoo | head -1)

# Set environment variables in DO dashboard
echo "Add secrets at: https://cloud.digitalocean.com/apps/$APP_ID"
echo ""
echo "Settings → Environment Variables → Add:"
echo "  1. GITHUB_APP_ID = YOUR_APP_ID"
echo "  2. GITHUB_INSTALLATION_ID = YOUR_INSTALLATION_ID"
echo "  3. GITHUB_PRIVATE_KEY = (paste entire .pem file content)"
echo ""
echo "Then click 'Save' and wait for redeploy"
```

### Option B: Using Dashboard

1. Go to: https://cloud.digitalocean.com/apps
2. Click **"Create App"**
3. Select **GitHub** as source
4. Choose repo: `jgtolentino/insightpulse-odoo`
5. Select directory: `services/mcp-server`
6. Click **"Next"** through steps
7. At Environment Variables, add:
   - `GITHUB_APP_ID`
   - `GITHUB_INSTALLATION_ID`
   - `GITHUB_PRIVATE_KEY` (paste entire key)
8. Click **"Create Resources"**

**Wait 5-10 minutes for deployment...**

---

## Step 7: Verify Production Deployment (1 minute)

```bash
# Get your app URL
APP_URL=$(doctl apps get $APP_ID --format DefaultIngress --no-header)

# Test health
curl https://$APP_URL/health

# Test GitHub operation
curl -X POST https://$APP_URL/mcp/github \
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

**If you see branches → ✅ Production is live!**

---

## Step 8: Connect to Claude Desktop (2 minutes)

### macOS
```bash
# Edit config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### Linux
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

### Windows
```powershell
notepad %APPDATA%\Claude\claude_desktop_config.json
```

**Add this:**
```json
{
  "mcpServers": {
    "pulser-hub": {
      "url": "https://YOUR_APP_URL/mcp/github",
      "description": "GitHub operations for insightpulse-odoo"
    }
  }
}
```

**Replace `YOUR_APP_URL` with your actual DO app URL**

**Restart Claude Desktop**

---

## Step 9: Test AI Integration (1 minute)

**In Claude Desktop, try:**

```
You: List all branches in jgtolentino/insightpulse-odoo
```

**Claude should respond with:**
```
I'll use the pulser-hub MCP server to list branches...

Found 15 branches:
- main
- claude/code-quality-audit-improvements-011CUeg3N1EoL3A9w1XSi41M
- feature/new-module
...
```

**More tests:**
```
You: Create an issue titled "Test pulser-hub integration"
Claude: [Creates issue] ✅ Issue #45 created

You: Show me all open PRs
Claude: [Lists PRs] You have 3 open pull requests...

You: Read the README.md file
Claude: [Reads file via GitHub API] Here's the content...
```

---

## ✅ Success! What You Can Do Now

### In Claude Desktop/Code
```
✅ "List all branches"
✅ "Create a PR for my changes"
✅ "Show me open issues with label 'bug'"
✅ "Read the Dockerfile"
✅ "Create an issue for this error"
✅ "Merge PR #123 if checks pass"
✅ "Search for 'wkhtmltopdf' in the codebase"
✅ "Create a branch called 'feature/new-addon'"
```

### In Your Code (Odoo/Python)
```python
import httpx

MCP_URL = "https://your-mcp-server.ondigitalocean.app"

# Auto-create GitHub issue on error
async def log_error(error):
    await httpx.post(f"{MCP_URL}/mcp/github", json={
        "method": "tools/call",
        "params": {
            "name": "github_create_issue",
            "arguments": {
                "repo": "jgtolentino/insightpulse-odoo",
                "title": f"Error: {error.type}",
                "body": error.traceback,
                "labels": ["bug", "auto-generated"]
            }
        }
    })
```

---

## 🔧 Troubleshooting

### "Invalid JWT signature"
```bash
# Check App ID matches
cat services/mcp-server/.env | grep APP_ID

# Verify private key format
cat services/mcp-server/.env | grep "BEGIN RSA"
# Should show: -----BEGIN RSA PRIVATE KEY-----
```

### "Installation not found"
```bash
# Get correct ID
gh api /user/installations

# Or check URL at:
# https://github.com/settings/installations
# Click Configure → Look at URL
```

### "403 Forbidden"
```bash
# pulser-hub needs repo access
# 1. Go to: https://github.com/settings/installations
# 2. Click Configure next to pulser-hub
# 3. Repository access → Select repositories
# 4. Add: jgtolentino/insightpulse-odoo
# 5. Save
```

### Server won't start locally
```bash
# Check Python version
python --version  # Should be 3.11+

# Install missing dependencies
pip install -r requirements.txt

# Check .env exists
ls -la .env

# Check logs
python server.py 2>&1 | tee server.log
```

---

## 📊 Checklist

- [ ] Got App ID from GitHub
- [ ] Got Installation ID
- [ ] Downloaded private key (.pem)
- [ ] Created .env file
- [ ] Tested locally (health check passed)
- [ ] Tested GitHub operation (list branches worked)
- [ ] Deployed to DigitalOcean
- [ ] Configured secrets in DO
- [ ] Verified production deployment
- [ ] Updated Claude Desktop config
- [ ] Tested AI integration (list branches via Claude)

---

## 🎉 You're Done!

pulser-hub is now active and connected to AI assistants.

**What changed:**
- ✅ MCP server deployed and running
- ✅ pulser-hub authenticated and authorized
- ✅ Claude can now perform GitHub operations
- ✅ You can automate workflows

**Next steps:**
- Create automation workflows
- Integrate with Odoo
- Monitor usage and logs

---

## 📞 Need Help?

- **Setup guide**: [docs/PULSER_HUB_SETUP.md](../docs/PULSER_HUB_SETUP.md)
- **MCP server docs**: [README.md](README.md)
- **GitHub Issues**: https://github.com/jgtolentino/insightpulse-odoo/issues

---

**Time to complete:** ~15 minutes
**Difficulty:** Medium (requires GitHub credentials)
**Result:** AI-powered GitHub automation ✨

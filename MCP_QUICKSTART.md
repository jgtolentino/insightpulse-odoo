# MCP Server Quick Start Guide

## 🎯 What You Have Now

✅ **MCP Server**: GitHub operations via pulser-hub App at `services/mcp-server/server.py`
✅ **MCP Config**: Docker Desktop integration at `~/.mcp/config.json`
✅ **Catalog Endpoint**: `/mcp/catalog` for tool discovery
✅ **Health Check**: `/health` for monitoring

## 🚀 Quick Start

### 1. Set Environment Variables

Add to `~/.zshrc` (or export in terminal):

```bash
export GITHUB_APP_ID="2191216"
export GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----\n...\n-----END RSA PRIVATE KEY-----"
export GITHUB_INSTALLATION_ID="your_installation_id"
```

**To find your installation ID:**
```bash
curl -s -H "Authorization: Bearer $(python3 -c 'import jwt, time; print(jwt.encode({"iat": int(time.time()), "exp": int(time.time()) + 600, "iss": 2191216}, open("path/to/private-key.pem").read(), algorithm="RS256"))')" https://api.github.com/app/installations | jq '.[0].id'
```

### 2. Start the MCP Server

```bash
cd /Users/tbwa/insightpulse-odoo/services/mcp-server
python3 -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Test Endpoints

```bash
# Health check
curl -s http://127.0.0.1:8000/health | jq

# Catalog (list available tools)
curl -s http://127.0.0.1:8000/mcp/catalog | jq

# Root info
curl -s http://127.0.0.1:8000/ | jq
```

### 4. Docker Desktop MCP Toolkit Integration

Your config is already set up at `~/.mcp/config.json`:

1. Open **Docker Desktop**
2. Go to **Extensions** → **MCP Toolkit (Beta)**
3. Click **My Servers**
4. You should see **"Pulser Hub GitHub MCP"**
5. Click to view available tools

**If not showing:**
- Restart Docker Desktop
- Verify the server is running: `curl -s http://127.0.0.1:8000/health`
- Check the config: `cat ~/.mcp/config.json | jq`

## 🛠️ Available GitHub Tools

The MCP server exposes these tools via `/mcp/github`:

### Branch Operations
- `github_create_branch` - Create new branch
- `github_list_branches` - List all branches

### File Operations
- `github_commit_files` - Commit multiple files
- `github_read_file` - Read file contents
- `github_search_code` - Search code in repo

### Pull Request Operations
- `github_create_pr` - Create PR
- `github_list_prs` - List PRs
- `github_merge_pr` - Merge PR

### Issue Operations
- `github_create_issue` - Create issue
- `github_list_issues` - List issues

### Workflow Operations
- `github_trigger_workflow` - Trigger GitHub Actions

## 📋 Example: Create Branch and PR

```bash
# 1. Create branch
curl -s -X POST http://127.0.0.1:8000/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "github_create_branch",
      "arguments": {
        "repo": "your-org/your-repo",
        "branch": "feature/new-feature",
        "from_branch": "main"
      }
    }
  }' | jq

# 2. Commit files
curl -s -X POST http://127.0.0.1:8000/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "github_commit_files",
      "arguments": {
        "repo": "your-org/your-repo",
        "branch": "feature/new-feature",
        "message": "Add new feature",
        "files": [
          {
            "path": "README.md",
            "content": "# New Feature\n\nDescription here."
          }
        ]
      }
    }
  }' | jq

# 3. Create PR
curl -s -X POST http://127.0.0.1:8000/mcp/github \
  -H "Content-Type: application/json" \
  -d '{
    "method": "tools/call",
    "params": {
      "name": "github_create_pr",
      "arguments": {
        "repo": "your-org/your-repo",
        "title": "Add new feature",
        "body": "This PR adds a new feature",
        "head": "feature/new-feature",
        "base": "main"
      }
    }
  }' | jq
```

## 🔍 Troubleshooting

### Server won't start
```bash
# Check dependencies
python3 -c "import fastapi, jwt, httpx, uvicorn"

# Check syntax
python3 -m py_compile services/mcp-server/server.py

# Check environment
env | grep GITHUB_
```

### Docker Desktop not showing server
```bash
# Verify config
cat ~/.mcp/config.json | jq

# Restart Docker Desktop
osascript -e 'quit app "Docker"'
open -a Docker

# Check server is running
curl -s http://127.0.0.1:8000/health
```

### Authentication errors
```bash
# Verify GitHub App ID
echo $GITHUB_APP_ID

# Test JWT generation
python3 -c "import jwt, time; print(jwt.encode({'iat': int(time.time()), 'exp': int(time.time()) + 600, 'iss': int('$GITHUB_APP_ID')}, '$GITHUB_PRIVATE_KEY', algorithm='RS256'))"

# Verify installation ID
curl -s -H "Authorization: Bearer <JWT_TOKEN>" \
  https://api.github.com/app/installations | jq
```

## 📚 Next Steps

1. **Set up environment variables** (see section 1)
2. **Start the server** and verify health
3. **Test in Docker Desktop** MCP Toolkit
4. **Create automation workflows** using the tools

## 🔗 Related Documentation

- Main MCP Guide: `MCP_SETUP_GUIDE.md`
- Server Implementation: `services/mcp-server/server.py`
- MCP Config: `~/.mcp/config.json`
- Test Script: `test_mcp_setup.sh`

---

**Status**: ✅ Server configured and ready to use
**Port**: 8000
**Base URL**: http://127.0.0.1:8000
**MCP Endpoint**: /mcp/github
**Catalog**: /mcp/catalog
**Health**: /health

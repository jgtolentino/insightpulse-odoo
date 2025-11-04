# Setup GitHub App Credentials for MCP Server

## Step 1: Download Private Key

1. Go to: **https://github.com/organizations/YOUR_ORG/settings/apps/pulser-hub**
   (Replace YOUR_ORG with your actual organization name)

2. Scroll down to **"Private keys"** section

3. You should see:
   ```
   Private key
   SHA256:9pue1oClMRDLWHsK2RtgNvcT+CPODKHhtt7WYPZIHnQ=
   Added 5 days ago by jgtolentino
   ```

4. Click **"Generate a private key"** button (if you need a new one)
   - OR if you already downloaded it 5 days ago, find the `.pem` file

5. Save the file somewhere safe (e.g., `~/.ssh/pulser-hub-private-key.pem`)

## Step 2: Find Installation ID

**Option A: Using the script**
```bash
cd /Users/tbwa/insightpulse-odoo
./find_installation_id.sh ~/.ssh/pulser-hub-private-key.pem
```

**Option B: Manual lookup**
1. Go to: https://github.com/settings/installations
2. Find "pulser-hub" in the list
3. Click "Configure"
4. Look at the URL: `https://github.com/settings/installations/XXXXX`
5. The number `XXXXX` is your INSTALLATION_ID

## Step 3: Set Environment Variables

### Quick Setup (Copy & Paste)

```bash
# 1. Read your private key into a variable
PRIVATE_KEY_CONTENT=$(cat ~/.ssh/pulser-hub-private-key.pem)

# 2. Add to ~/.zshrc
cat >> ~/.zshrc << EOF

# Pulser Hub MCP Server - GitHub App Credentials
export GITHUB_APP_ID="2191216"
export GITHUB_PRIVATE_KEY="$PRIVATE_KEY_CONTENT"
export GITHUB_INSTALLATION_ID="REPLACE_WITH_ACTUAL_ID"  # Get from find_installation_id.sh
EOF

# 3. Reload shell
source ~/.zshrc
```

### Manual Setup

Edit `~/.zshrc` and add:

```bash
# Pulser Hub MCP Server - GitHub App Credentials
export GITHUB_APP_ID="2191216"
export GITHUB_PRIVATE_KEY="-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA...
... paste all lines here ...
-----END RSA PRIVATE KEY-----"
export GITHUB_INSTALLATION_ID="12345678"  # Replace with actual ID
```

## Step 4: Verify Setup

```bash
# Reload shell
source ~/.zshrc

# Run test
cd /Users/tbwa/insightpulse-odoo
./test_mcp_setup.sh
```

You should see:
```
✅ Checking environment variables...
   GITHUB_APP_ID is set
   GITHUB_PRIVATE_KEY is set
   GITHUB_INSTALLATION_ID is set
```

## Step 5: Start MCP Server

```bash
cd /Users/tbwa/insightpulse-odoo/services/mcp-server
python3 -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

## Step 6: Test It Works

In another terminal:
```bash
# Health check
curl -s http://127.0.0.1:8000/health | jq

# Should return:
# {
#   "status": "healthy",
#   "app_id": 2191216
# }

# List available tools
curl -s http://127.0.0.1:8000/mcp/catalog | jq '.tools[].name'
```

## Troubleshooting

### "Private key file not found"
- Check if you downloaded the `.pem` file 5 days ago
- Search your Downloads folder: `ls -la ~/Downloads/*.pem`
- If not found, generate a new one from GitHub App settings

### "JWT token error"
- Make sure the private key includes the BEGIN/END lines
- Verify no extra spaces or line breaks
- Private key should be exactly as downloaded from GitHub

### "Installation not found"
- Verify the app is installed on your organization
- Go to: https://github.com/settings/installations
- If not listed, install it from the GitHub App settings page

---

**Next**: Once credentials are set, open Docker Desktop → MCP Toolkit to see "Pulser Hub GitHub MCP" listed! 🚀

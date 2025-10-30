# ChatGPT MCP Setup Guide

Configure ChatGPT to use the InsightPulse MCP GitHub Server with OAuth 2.0 authentication.

## Prerequisites

1. **MCP Server Running**: Either local or deployed to production
2. **OAuth Credentials**: Client ID and Client Secret configured
3. **ChatGPT Account**: Access to ChatGPT settings

## Step 1: Get Your OAuth Credentials

The MCP server generates OAuth credentials automatically:

**Client ID**: `insightpulse-mcp-github` (default)
**Client Secret**: Auto-generated on first start (check server logs or environment)

### Option A: Use Default Credentials (Local Development)

The server generates a random client secret on startup. Check logs:
```bash
# Your MCP server logs will show the auto-generated secret
echo $OAUTH_CLIENT_SECRET
```

### Option B: Set Custom Credentials (Production)

```bash
# Add to environment variables
export OAUTH_CLIENT_ID="insightpulse-mcp-github"
export OAUTH_CLIENT_SECRET="your-secure-random-secret-here"

# Or add to .env file
OAUTH_CLIENT_ID=insightpulse-mcp-github
OAUTH_CLIENT_SECRET=your-secure-random-secret-here
```

## Step 2: Configure ChatGPT

1. **Open ChatGPT Settings** → **Model Context Protocol** → **Add Server**

2. **Fill in MCP Server Details**:

   **Production URL** (after deployment):
   ```
   Name: InsightPulse GitHub
   MCP Server URL: https://insightpulseai.net
   Authentication: OAuth 2.0
   ```

   **Local Development** (with ngrok):
   ```
   Name: InsightPulse GitHub (Dev)
   MCP Server URL: https://your-ngrok-url.ngrok.io
   Authentication: OAuth 2.0
   ```

3. **OAuth Configuration**:
   - **Authorization URL**: `https://insightpulseai.net/oauth/authorize`
   - **Token URL**: `https://insightpulseai.net/oauth/token`
   - **Client ID**: `insightpulse-mcp-github`
   - **Client Secret**: `<your-client-secret>`
   - **Scope**: `github:all` (or specific: `github:branches,github:pr`)

4. **Click "Authorize"** and follow the OAuth flow

## Step 3: Test the Integration

Once authorized, you can ask ChatGPT to perform GitHub operations:

```
"List all open pull requests in jgtolentino/insightpulse-odoo"

"Create a new branch called 'feature/chatgpt-test' from main"

"Create a pull request from feat/parity-live-sync to main with title 'Test PR from ChatGPT'"

"Search for TODO comments in the codebase"
```

## Available GitHub Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| **github_list_branches** | List repository branches | "Show me all branches" |
| **github_create_branch** | Create new branch | "Create branch feature/xyz from main" |
| **github_commit_files** | Commit files to branch | "Commit README.md to feature/xyz" |
| **github_create_pr** | Create pull request | "Create PR from feature/xyz to main" |
| **github_list_prs** | List pull requests | "Show open PRs" |
| **github_merge_pr** | Merge pull request | "Merge PR #123" |
| **github_create_issue** | Create issue | "Create issue about bug" |
| **github_list_issues** | List issues | "Show open issues" |
| **github_trigger_workflow** | Run GitHub Action | "Trigger deployment workflow" |
| **github_search_code** | Search code | "Find all console.log statements" |
| **github_read_file** | Read file contents | "Show me package.json" |

## Query Parameters

You can filter available tools using query parameters:

```
# Only enable PR and branch operations
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=pr,branches

# Enable all features
https://insightpulseai.net/mcp/github?project=jgtolentino/insightpulse-odoo&features=branches,commits,issues,pr,workflows,search,files
```

## Security Considerations

### Production Deployment

1. **Use HTTPS Only**: Never expose OAuth endpoints over HTTP
2. **Strong Client Secret**: Generate with `openssl rand -base64 32`
3. **Persistent Storage**: Use Redis or database instead of in-memory storage
4. **Token Expiration**: Tokens expire after 1 hour (configurable)
5. **Rate Limiting**: Implement rate limiting on OAuth endpoints

### Recommended Environment Variables

```bash
# Production configuration
OAUTH_CLIENT_ID=insightpulse-mcp-github
OAUTH_CLIENT_SECRET=<openssl-rand-base64-32-output>
GITHUB_APP_ID=2191216
GITHUB_INSTALLATION_ID=61508966
GITHUB_PRIVATE_KEY=<your-private-key>
```

## Troubleshooting

### Error: "MCP server does not implement OAuth"

**Solution**: Ensure OAuth endpoints are available:
```bash
curl https://insightpulseai.net/oauth/authorize
curl -X POST https://insightpulseai.net/oauth/token
```

### Error: "Invalid client credentials"

**Solution**: Verify client_id and client_secret match server configuration:
```bash
# Check server logs for actual credentials
docker logs <container-id> | grep "OAUTH_CLIENT"
```

### Error: "Authorization code expired"

**Solution**: Authorization codes expire after 10 minutes. Complete the OAuth flow faster or increase expiration time in server code.

### Error: "Redirect URI mismatch"

**Solution**: Ensure ChatGPT's redirect URI matches what you configured. Typical ChatGPT redirect URI:
```
https://chatgpt.com/oauth/callback
```

## Local Development with ngrok

1. **Start MCP server locally**:
   ```bash
   cd services/mcp-server
   uvicorn server:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Expose with ngrok**:
   ```bash
   ngrok http 8000
   ```

3. **Configure ChatGPT with ngrok URL**:
   ```
   MCP Server URL: https://abc123.ngrok.io
   Authorization URL: https://abc123.ngrok.io/oauth/authorize
   Token URL: https://abc123.ngrok.io/oauth/token
   ```

4. **Test OAuth flow**:
   - ChatGPT will redirect to ngrok URL for authorization
   - Server will redirect back to ChatGPT with authorization code
   - ChatGPT exchanges code for access token

## Production Deployment

See [DEPLOY_MCP_SERVER.md](../docs/DEPLOY_MCP_SERVER.md) for production deployment instructions.

## Support

For issues or questions:
- GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- MCP Documentation: https://modelcontextprotocol.io
- ChatGPT MCP Guide: https://help.openai.com/en/articles/mcp-integration

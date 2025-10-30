# Docker MCP Toolkit Integration

Integration guide for using InsightPulse GitHub MCP Server with Docker MCP Toolkit.

## Overview

The InsightPulse GitHub MCP Server can be deployed in two ways:

1. **Docker MCP Gateway** - Via Docker Desktop's MCP Toolkit (local development)
2. **Direct HTTP** - Via DigitalOcean App Platform (production)

This document covers Docker MCP Toolkit integration for local development.

## Architecture

```
┌─────────────────┐
│   VS Code       │
│   Claude Code   │
│   Cursor IDE    │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ Docker MCP Gateway      │
│ docker mcp gateway run  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ InsightPulse GitHub MCP Server  │
│ Container: mcp-github           │
│ Port: 8000                      │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ GitHub API                      │
│ via pulser-hub App (2191216)   │
└─────────────────────────────────┘
```

## Prerequisites

### 1. Docker Desktop with MCP Toolkit
- Docker Desktop 4.37+ (with MCP Toolkit enabled)
- Docker MCP Gateway installed

**Verify Installation**:
```bash
docker mcp --version
docker mcp gateway --help
```

### 2. GitHub App Credentials
Required environment variables:
- `GITHUB_APP_ID=2191216` (pulser-hub App)
- `GITHUB_PRIVATE_KEY` (PEM format, base64 encoded)
- `GITHUB_INSTALLATION_ID=61508966` (jgtolentino/insightpulse-odoo)

**Verify Credentials**:
```bash
echo "App ID: ${GITHUB_APP_ID}"
echo "Private Key: ${GITHUB_PRIVATE_KEY:0:50}..."
echo "Installation ID: ${GITHUB_INSTALLATION_ID}"
```

### 3. Build Docker Image
```bash
cd services/mcp-server
docker build -t insightpulse/mcp-github-server:latest .
```

## Configuration

### Option 1: VS Code with Docker Gateway

**Global Configuration** (`~/.vscode/mcp.json`):
```json
{
  "mcpServers": {
    "MCP_DOCKER": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"],
      "type": "stdio"
    }
  }
}
```

**Project Configuration** (`.vscode/mcp.json`):
```json
{
  "mcpServers": {
    "insightpulse-github": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-p", "8000:8000",
        "-e", "GITHUB_APP_ID=2191216",
        "-e", "GITHUB_PRIVATE_KEY=${GITHUB_PRIVATE_KEY}",
        "-e", "GITHUB_INSTALLATION_ID=61508966",
        "-e", "GITHUB_REPO_OWNER=jgtolentino",
        "-e", "GITHUB_REPO_NAME=insightpulse-odoo",
        "insightpulse/mcp-github-server:latest"
      ],
      "description": "InsightPulse GitHub MCP Server"
    }
  }
}
```

**Important**: Add `.vscode/mcp.json` to `.gitignore` (contains sensitive credentials).

### Option 2: Claude Desktop with Docker Toolkit

**Install via Docker Desktop**:
1. Open Docker Desktop → MCP Toolkit
2. Click "Add MCP Server"
3. Select "Custom Image"
4. Image: `insightpulse/mcp-github-server:latest`
5. Configure environment variables
6. Click "Install"

**Add Claude Desktop as Client**:
1. Docker Desktop → MCP Toolkit → Clients tab
2. Click "Add Client"
3. Select "Claude Desktop"
4. Restart Claude Desktop

### Option 3: Cursor IDE

**Project Configuration** (`.cursor/mcp.json`):
```json
{
  "mcpServers": {
    "insightpulse-github": {
      "command": "docker",
      "args": ["mcp", "gateway", "run"],
      "type": "stdio"
    }
  }
}
```

Or use direct connection:
```bash
docker mcp client connect cursor
```

## Usage

### VS Code Agent Mode

1. Open VS Code with configured project
2. Open Chat interface (Cmd+Shift+I / Ctrl+Shift+I)
3. Switch to **Agent mode**
4. Type: "List all branches in insightpulse-odoo repository"
5. VS Code will automatically use MCP tools

### Claude Desktop

1. Start conversation in Claude Desktop
2. Type: "Create a new branch called feature/test in insightpulse-odoo"
3. Claude will automatically detect and use MCP tools

### Cursor IDE

1. Open Cursor IDE with configured project
2. Use Cursor's AI chat feature
3. Request GitHub operations
4. Cursor will route through Docker MCP gateway

## Query Parameters

The InsightPulse GitHub MCP Server supports query parameters for feature filtering:

**URL Format**:
```
http://localhost:8000/mcp/github?project=owner/repo&features=branches,commits,issues,pr,workflows,search,files
```

**Available Features**:
- `branches` - Branch operations (create, list)
- `commits` - Commit operations
- `issues` - Issue management
- `pr` - Pull request operations
- `workflows` - GitHub Actions workflows
- `search` - Code search
- `files` - File operations

**Example Configurations**:

**Read-Only Access**:
```
?features=search,files
```

**CI/CD Operations**:
```
?features=workflows,pr
```

**Full Access**:
```
?features=branches,commits,issues,pr,workflows,search,files
```

## Docker MCP Gateway Commands

### Start Gateway
```bash
docker mcp gateway run
```

### List Installed Servers
```bash
docker mcp server list
```

### Install Server from Catalog
```bash
docker mcp server install <server-name>
```

### Remove Server
```bash
docker mcp server remove <server-name>
```

### View Server Logs
```bash
docker logs <container-id>
```

## Security

### Container Isolation
The Docker MCP Toolkit enforces resource limits:
- **CPU**: 1 core maximum
- **Memory**: 2 GB maximum
- **Filesystem**: Read-only by default
- **Network**: Isolated unless explicitly configured

### Credential Management
- Store credentials in environment variables
- Use Docker secrets for production
- Never commit credentials to version control
- Rotate GitHub App private keys regularly

### Image Verification
For production use, sign and verify Docker images:
```bash
# Sign image
docker trust sign insightpulse/mcp-github-server:latest

# Verify signature
docker trust inspect insightpulse/mcp-github-server:latest
```

## Troubleshooting

### Gateway Not Starting
```bash
# Check Docker Desktop MCP Toolkit status
docker mcp status

# Verify Docker daemon running
docker ps

# Check gateway logs
docker logs $(docker ps -q --filter ancestor=docker-mcp-gateway)
```

### Server Not Responding
```bash
# Check server health
curl http://localhost:8000/health

# View server logs
docker logs $(docker ps -q --filter ancestor=insightpulse/mcp-github-server)

# Restart server
docker restart $(docker ps -q --filter ancestor=insightpulse/mcp-github-server)
```

### Authentication Failures
```bash
# Verify GitHub App credentials
curl -H "Authorization: Bearer $(generate_jwt_token)" \
  https://api.github.com/app

# Test GitHub API access
curl -H "Authorization: token ${GITHUB_TOKEN}" \
  https://api.github.com/user
```

### VS Code Not Detecting MCP
1. Verify `.vscode/mcp.json` exists and is valid JSON
2. Restart VS Code
3. Check VS Code Output → MCP for error messages
4. Ensure Docker Desktop is running

## Deployment Comparison

| Feature | Docker MCP Toolkit | DigitalOcean App Platform |
|---------|-------------------|--------------------------|
| **Use Case** | Local development | Production deployment |
| **Availability** | Local only | Public HTTPS endpoint |
| **Scaling** | Single instance | Auto-scaling |
| **Authentication** | Local credentials | Environment secrets |
| **Cost** | Free (local Docker) | $5/month basic-xxs |
| **Setup** | Docker Desktop required | CLI or web dashboard |
| **Updates** | Manual image rebuild | Auto-deploy on push |

## Next Steps

1. **Local Development**: Use Docker MCP Toolkit for development and testing
2. **Production Deployment**: Deploy to DigitalOcean for production use
3. **CI/CD**: Set up GitHub Actions for automated image builds
4. **Monitoring**: Configure health checks and logging

## Resources

- [Docker MCP Toolkit Documentation](https://docs.docker.com/ai/mcp-catalog-and-toolkit/toolkit/)
- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [InsightPulse MCP Server README](../README.md)
- [Client Setup Guide](CLIENT_SETUP.md)
- [Query Parameters Reference](QUERY_PARAMETERS.md)

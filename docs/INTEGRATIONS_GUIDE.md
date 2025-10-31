# GitHub App Integrations Guide

This guide shows how to leverage your installed GitHub Apps and integrations for automated deployment and development workflows.

## 🎯 Overview

You have these integrations available:

| Integration | Purpose | Status |
|------------|---------|--------|
| **DigitalOcean GitHub App** | Auto-deploy from GitHub | ✅ Installed |
| **Docker Desktop** | Local development + MCP | Available |
| **MCP Server** | AI-driven operations | Optional |
| **GitHub Actions** | CI/CD automation | Active |

---

## 1️⃣ DigitalOcean GitHub App Integration

**What it does:** Automatically deploys your app to DigitalOcean when you push to main branch.

### Current Setup

Your DO GitHub App has access to:
- ✅ `jgtolentino/insightpulse-odoo`
- ✅ `jgtolentino/odoboo-workspace`

**Permissions:**
- ✅ Read/Write: checks, commit statuses, issues, PRs, repository hooks
- ✅ Read: Dependabot alerts, code, metadata, security events

### How to Leverage It

#### A. Auto-Deploy from GitHub Pushes

```yaml
# .do/app.yaml
name: insightpulse-odoo
region: sgp
services:
  - name: odoo
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true  # Auto-deploy on push
    dockerfile_path: Dockerfile
    http_port: 8069
    health_check:
      http_path: /web/health
    envs:
      - key: POSTGRES_PASSWORD
        scope: RUN_TIME
        type: SECRET
      - key: ODOO_ADMIN_PASSWORD
        scope: RUN_TIME
        type: SECRET
    instance_count: 1
    instance_size_slug: basic-xs

databases:
  - name: db
    engine: PG
    version: "15"
    production: true
    cluster_name: insightpulse-db
```

**Workflow:**
```bash
# 1. Make changes locally
git add .
git commit -m "feat: add feature X"

# 2. Push to main
git push origin main

# 3. DigitalOcean GitHub App detects push
#    → Builds Docker image
#    → Runs health checks
#    → Deploys if successful
#    → Posts status check to GitHub

# 4. Check deployment status on GitHub PR/commit
```

#### B. Deploy Previews for Pull Requests

Enable preview deployments for every PR:

```yaml
# .do/app.yaml
services:
  - name: odoo
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    # Preview deployments for PRs
    routes:
      - path: /
        preserve_path_prefix: false
```

**In DO Dashboard:**
1. Go to your app
2. Settings → App-Level Configuration
3. Enable "Deploy Pull Request Previews"

**Result:**
- Each PR gets a unique URL: `pr-123-insightpulse.ondigitalocean.app`
- Test changes before merging
- Automatic cleanup when PR closes

#### C. Commit Status Checks

The DO GitHub App posts build/deploy status to your commits:

```bash
# GitHub UI shows:
✅ DigitalOcean - Build successful
✅ DigitalOcean - Deploy successful
✅ DigitalOcean - Health check passed

# Or if failed:
❌ DigitalOcean - Build failed
```

**Protect main branch** with required status checks:

```yaml
# .github/branch-protection.yml
rules:
  - pattern: main
    required_status_checks:
      - "DigitalOcean - Build"
      - "DigitalOcean - Deploy"
      - "CI / lint"
      - "CI / test"
```

---

## 2️⃣ Docker Desktop + Extensions

### Docker Desktop MCP Extension

**What it does:** Manage containers directly from AI assistants (Claude, etc.)

#### Install Docker MCP Extension

1. **Open Docker Desktop**
2. **Extensions** → Search "MCP" or "Model Context Protocol"
3. **Install** the extension

#### Configure Claude Desktop with Docker MCP

Create `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": ["extension", "mcp"]
    }
  }
}
```

#### What You Can Do

**In Claude Desktop/Code:**
```
You: "Show me running containers for insightpulse"
Claude: [Uses Docker MCP]
  - insightpulse-odoo (running, healthy)
  - insightpulse-db (running, 15m ago)
  - insightpulse-redis (running)

You: "Check Odoo logs from the last hour"
Claude: [Fetches docker logs --since 1h insightpulse-odoo]

You: "Restart the Odoo container"
Claude: [Executes docker restart insightpulse-odoo]
```

### Docker Compose Watch (Live Reload)

Edit `docker-compose.yml` to enable live reload:

```yaml
services:
  odoo:
    build: .
    develop:
      watch:
        - action: sync
          path: ./addons/custom
          target: /mnt/extra-addons/custom
        - action: rebuild
          path: requirements.txt
        - action: sync+restart
          path: ./config/odoo
          target: /etc/odoo
```

**Usage:**
```bash
# Start with watch mode
docker compose watch

# Now edit files in addons/custom/
# → Changes sync instantly to container
# → Odoo reloads automatically
```

---

## 3️⃣ MCP Server for AI-Driven Operations

### Architecture

```
┌────────────────┐
│ Claude Desktop │ ← You interact here
└───────┬────────┘
        │ MCP Protocol
        ↓
┌────────────────┐
│  MCP Servers   │
├────────────────┤
│ 1. Docker      │ ← Manage containers
│ 2. GitHub      │ ← GitHub operations (our custom server)
│ 3. Filesystem  │ ← File operations
└───────┬────────┘
        │
   ┌────┴────┐
   ↓         ↓
┌────────┐ ┌────────┐
│ Docker │ │ GitHub │
│Desktop │ │  API   │
└────────┘ └────────┘
```

### A. GitHub MCP Server (Custom)

**Deploy your custom MCP server** (from `services/mcp-server/`):

```bash
# Option 1: Deploy to DigitalOcean
doctl apps create --spec services/mcp-server/app.yaml

# Option 2: Run locally with Docker
cd services/mcp-server
docker compose up -d

# The MCP server URL will be:
# Production: https://mcp.insightpulseai.net
# Local: http://localhost:8000
```

**Configure in Claude Desktop:**

```json
{
  "mcpServers": {
    "docker": {
      "command": "docker",
      "args": ["extension", "mcp"]
    },
    "pulser-hub-github": {
      "url": "https://mcp.insightpulseai.net/mcp/github",
      "description": "GitHub operations via pulser-hub app"
    }
  }
}
```

### B. Combined Workflow Examples

**Example 1: Deploy a Feature**
```
You: "Deploy my feature branch to a preview environment"

Claude:
1. [Docker MCP] Build image locally
2. [Docker MCP] Run tests in container
3. [GitHub MCP] Create PR from feature branch
4. [DigitalOcean] Auto-creates preview deployment
5. Returns preview URL: https://pr-123-insightpulse.ondigitalocean.app
```

**Example 2: Debug Production Issue**
```
You: "Something's wrong with the production Odoo container"

Claude:
1. [Docker MCP] Check container health status
2. [Docker MCP] Get last 100 log lines
3. [Docker MCP] Check resource usage (CPU, memory)
4. [GitHub MCP] Search recent commits for related changes
5. [GitHub MCP] Create issue with logs attached
```

**Example 3: Update Dependencies**
```
You: "Update Odoo to 19.0.1"

Claude:
1. [GitHub MCP] Create new branch 'upgrade-odoo-19.0.1'
2. [GitHub MCP] Update Dockerfile
3. [GitHub MCP] Update requirements.txt
4. [GitHub MCP] Commit changes
5. [Docker MCP] Build and test locally
6. [GitHub MCP] Create PR
7. [DigitalOcean] Auto-deploy preview for testing
```

---

## 4️⃣ GitHub Actions Integration

### Leverage DO GitHub App in Actions

The DO GitHub App can **trigger your GitHub Actions workflows** and vice versa.

#### A. Deploy from Actions to DigitalOcean

```yaml
# .github/workflows/deploy-to-do.yml
name: Deploy to DigitalOcean

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Deploy to DigitalOcean App Platform
        uses: digitalocean/app_action@v1
        with:
          app_name: insightpulse-odoo
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Post status to GitHub
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.repos.createCommitStatus({
              owner: context.repo.owner,
              repo: context.repo.repo,
              sha: context.sha,
              state: 'success',
              target_url: 'https://insightpulseai.net',
              description: 'Deployed to production',
              context: 'DigitalOcean / Deploy'
            })
```

#### B. Trigger Actions from DO App

Configure webhook in `.do/app.yaml`:

```yaml
services:
  - name: odoo
    # ... other config
    alerts:
      - rule: DEPLOYMENT_FAILED
        webhook: https://api.github.com/repos/jgtolentino/insightpulse-odoo/dispatches
```

Then catch it in Actions:

```yaml
# .github/workflows/on-deploy-failed.yml
name: Deploy Failure Handler

on:
  repository_dispatch:
    types: [deployment_failed]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Create issue for failed deployment
        uses: actions/github-script@v7
        with:
          script: |
            await github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: '🚨 Production Deploy Failed',
              body: 'Deployment to DigitalOcean failed. Check logs.',
              labels: ['deployment', 'bug']
            })
```

---

## 5️⃣ Complete Integration Workflow

### End-to-End Example: "Ship a Feature"

**Step 1: Develop Locally with Docker Desktop**
```bash
# Clone repo
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo

# Start local environment with live reload
docker compose watch

# Make changes to addons/custom/my_module/
# → Changes sync instantly
```

**Step 2: Test with AI Assistant (Claude + Docker MCP)**
```
You: "Run tests for my_module and show results"

Claude [via Docker MCP]:
→ docker exec insightpulse-odoo pytest addons/custom/my_module/tests
→ Shows: ✅ 15 tests passed
```

**Step 3: Commit & Create PR (via GitHub MCP)**
```
You: "Create a PR for my changes with title 'Add my_module feature'"

Claude [via GitHub MCP]:
1. Commits changes
2. Pushes to new branch
3. Creates PR
4. Returns: PR #125 created: https://github.com/.../pull/125
```

**Step 4: DigitalOcean Auto-Preview**
- DO GitHub App detects PR
- Builds preview deployment
- Posts comment with preview URL
- Updates PR status checks

**Step 5: CI/CD Runs**
- GitHub Actions CI runs (lint, test, build)
- Trivy security scan
- Coverage report
- All checks must pass

**Step 6: Review & Merge**
```
You: "Merge PR #125 if all checks pass"

Claude [via GitHub MCP]:
→ Checks status: All checks passed ✅
→ Merges PR with squash
→ Deletes feature branch
```

**Step 7: Auto-Deploy to Production**
- DO GitHub App detects merge to main
- Builds production image
- Runs health checks
- Deploys with zero downtime
- Posts success status

**Step 8: Monitor with Docker MCP**
```
You: "Check production container health"

Claude [via Docker MCP]:
→ Container: healthy
→ Uptime: 2m
→ Memory: 512MB / 2GB
→ Health check: passing
```

---

## 6️⃣ Configuration Checklist

### DigitalOcean GitHub App
- [x] Installed on insightpulse-odoo repo
- [ ] Create `.do/app.yaml` spec file
- [ ] Configure secrets in DO dashboard
- [ ] Enable PR preview deployments
- [ ] Set up custom domain (insightpulseai.net)

### Docker Desktop
- [ ] Install Docker Desktop
- [ ] Enable Docker Extensions
- [ ] Install MCP extension (if available)
- [ ] Configure docker compose watch

### GitHub MCP Server
- [ ] Deploy MCP server to DO
- [ ] Configure environment variables
- [ ] Add custom domain (mcp.insightpulseai.net)
- [ ] Test health endpoint

### Claude Desktop MCP Config
- [ ] Create claude_desktop_config.json
- [ ] Add Docker MCP server
- [ ] Add GitHub MCP server
- [ ] Test connections

### GitHub Actions
- [ ] Configure DO access token
- [ ] Set up CI/CD workflows
- [ ] Configure branch protection
- [ ] Enable required status checks

---

## 7️⃣ Troubleshooting

### DigitalOcean GitHub App Issues

**Problem: Deploy not triggering on push**
```bash
# Check webhook deliveries
# GitHub → Settings → Webhooks → Recent Deliveries

# Verify app.yaml is valid
doctl apps spec validate .do/app.yaml

# Check DO app logs
doctl apps logs <app-id> --type BUILD
```

**Problem: Status checks not appearing**
```bash
# Ensure DO GitHub App has correct permissions:
# - Read/write access to checks
# - Read/write access to commit statuses
```

### Docker Desktop MCP Issues

**Problem: MCP not connecting**
```bash
# Check Docker Desktop is running
docker ps

# Verify MCP extension is installed
docker extension ls

# Check Claude config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

### GitHub MCP Server Issues

**Problem: MCP server not responding**
```bash
# Check server health
curl https://mcp.insightpulseai.net/health

# Check DO app logs
doctl apps logs $(doctl apps list --format ID --no-header) --type RUN

# Verify environment variables are set
doctl apps spec get <app-id> | grep -A 3 envs
```

---

## 8️⃣ Next Steps

### Immediate Actions

1. **Create `.do/app.yaml`** (see below)
2. **Test local deployment** with docker compose
3. **Deploy MCP server** to DigitalOcean
4. **Configure Claude Desktop** with MCP servers
5. **Enable PR previews** in DO dashboard

### Future Enhancements

- [ ] Set up Dependabot with DO GitHub App
- [ ] Configure auto-merge for passing PRs
- [ ] Add deployment notifications to Slack
- [ ] Set up staging environment
- [ ] Configure blue-green deployments

---

## 📄 Sample `.do/app.yaml`

```yaml
name: insightpulse-odoo
region: sgp

services:
  - name: odoo
    github:
      repo: jgtolentino/insightpulse-odoo
      branch: main
      deploy_on_push: true
    dockerfile_path: Dockerfile
    http_port: 8069
    instance_count: 1
    instance_size_slug: professional-xs

    health_check:
      http_path: /web/health
      initial_delay_seconds: 60
      period_seconds: 30
      timeout_seconds: 10
      success_threshold: 1
      failure_threshold: 3

    envs:
      - key: ODOO_ADMIN_PASSWORD
        scope: RUN_TIME
        type: SECRET
      - key: DATABASE_URL
        scope: RUN_TIME
        type: SECRET
        value: "${db.DATABASE_URL}"
      - key: REDIS_URL
        scope: RUN_TIME
        type: SECRET
        value: "${redis.DATABASE_URL}"
      - key: ODOO_WORKERS
        scope: RUN_TIME
        value: "4"

    routes:
      - path: /

    alerts:
      - rule: DEPLOYMENT_FAILED
      - rule: DOMAIN_FAILED

databases:
  - name: db
    engine: PG
    version: "15"
    production: true
    cluster_name: insightpulse-db

  - name: redis
    engine: REDIS
    version: "7"
    production: true

domains:
  - domain: insightpulseai.net
    type: PRIMARY
    zone: insightpulseai.net
```

---

## 🔗 Resources

- [DigitalOcean App Platform Docs](https://docs.digitalocean.com/products/app-platform/)
- [Docker Desktop Extensions](https://www.docker.com/products/extensions/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [GitHub Apps Documentation](https://docs.github.com/en/apps)
- [Your MCP Server README](../services/mcp-server/README.md)

---

**Questions?** Open an issue or check the troubleshooting section above.

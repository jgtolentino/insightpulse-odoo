# Odoo Spark Subagents v0.2.0

## Executive Summary

This document provides a **single-source inventory** of all **skills** and **deployable agents** for the InsightPulse Odoo Spark Subagents system (v0.2.0), including the new **Draxlr** integration, **n8n CLI**, and **Mattermost** (Slack alternative) chat platform.

---

## Skills Inventory

### Available Skills

| Skill ID                   | Path                                      | Purpose                                                                                | Category                              |
| -------------------------- | ----------------------------------------- | -------------------------------------------------------------------------------------- | ------------------------------------- |
| `automation_executor`      | `skills/automation_executor/`             | Invoke atomic Odoo tools (OpenAPI-first, idempotent, dry-run by default)              | Automation, Odoo                      |
| `git_specialist`           | `skills/git_specialist/`                  | Git/PR planner: branch, commit, draft PR with RL score + traceparent                  | Git, Automation                       |
| `automation_gap_analyzer`  | `skills/automation_gap_analyzer/`         | Scan repo for CI/CD gaps; emit gap_plan (adds CodeQL/Dependabot/CI/etc.)              | DevOps, CI/CD                         |
| `conflict_manager`         | `skills/conflict_manager/`                | Detect OCA/deps/migration/docker conflicts; produce fix_plan                          | Odoo, DevOps                          |
| `draxlr_integration`       | `skills/integrations/draxlr/`             | Low-lift analytics/BI integration helpers (Draxlr alternative to Tableau/Power BI)    | Analytics, Business Intelligence      |
| `github-api-integration`   | `skills/proposed/github-api-integration/` | GitHub REST/GraphQL API integration with auth, rate limiting, pagination              | GitHub Developer Program, API         |
| `github-apps-development`  | `skills/proposed/github-apps-development/`| Production-grade GitHub Apps with Probot, FastAPI, webhooks                           | GitHub Developer Program, Apps        |
| `github-actions-workflows` | `skills/proposed/github-actions-workflows/` | Advanced CI/CD workflows, reusable workflows, composite actions               | GitHub Developer Program, CI/CD       |
| `github-webhooks-integration` | `skills/proposed/github-webhooks-integration/` | Event-driven integrations with signature verification, idempotency        | GitHub Developer Program, Events      |

### Skills Management

```bash
# Consolidate all skills into registries
make skills-consolidate

# Show skill count
make skills-open

# Validate skill metadata
make skills-validate
```

**Generated Artifacts:**
- `skills/REGISTRY.json` - Canonical registry for agents/CI
- `skills/REGISTRY.mcp.json` - MCP usage map (service → actions)
- `docs/claude-code-skills/Section19.generated.md` - Claude Code Section 19

---

## Agents to Deploy (v0.2.0)

| Agent                      | Role                                | Required Env                                                | Safety                                |
| -------------------------- | ----------------------------------- | ----------------------------------------------------------- | ------------------------------------- |
| **automation-executor**    | OpenAPI-first Odoo tool invoker     | `ODOO_BASE_URL`, `ODOO_BOT_TOKEN`                           | `require_dry_run=true`, `max_batch=5` |
| **git-specialist**         | Git/PR sub-agent (plan-only)        | `GITHUB_TOKEN`, `GITHUB_REPO_SLUG`, `GITHUB_DEFAULT_BRANCH` | No force-push; draft PRs only         |
| **automation-gap-analyzer**| Repo automation scanner             | *(none)*                                                    | Routes to `git-specialist`            |
| **conflict-manager**       | Stack conflict triage → fix plan    | *(none)*                                                    | Routes to `git-specialist`            |

---

## n8n CLI Tool

### Installation

```bash
# Install CLI
make n8n-cli

# Configure
export IP_N8N_CONFIG=~/.config/ip-n8n/config.json
./ip-n8n login --base https://n8n.insightpulseai.net --key $N8N_API_KEY
```

### Usage

```bash
# List workflows
make n8n-list
./ip-n8n list

# Run workflow
make n8n-run ID=12
./ip-n8n run 12

# Import workflow
make n8n-import FILE=workflow.json
./ip-n8n import workflow.json

# Export workflow
./ip-n8n export 12 --out backup.json

# Activate/deactivate
./ip-n8n activate 12
./ip-n8n deactivate 12

# Execute webhook
./ip-n8n exec-webhook https://n8n.../webhook/TOKEN --data '{"text":"deploy"}'
```

### Configuration

Config file: `~/.config/ip-n8n/config.json`

```json
{
  "base_url": "https://n8n.insightpulseai.net",
  "api_key": "YOUR_N8N_API_KEY"
}
```

**Security:**
- Store config with `chmod 600`
- Never commit API keys to version control
- Use environment-specific keys

---

## Mattermost (Slack Alternative)

### Deployment

```bash
# Start Mattermost
make chat-up

# Configure Nginx + TLS
make chat-tls

# Run certbot for SSL
sudo certbot --nginx -d chat.insightpulseai.net
```

### Access

- **Local:** http://localhost:8065
- **Remote:** https://chat.insightpulseai.net

### First-Time Setup

1. Visit web UI and create admin user
2. Enable Integrations (System Console → Integrations)
3. Create Slash Commands for n8n integration
4. Create Incoming Webhooks for alerts

### Mattermost ↔ n8n Integration

#### Outgoing Slash Commands → n8n

**In Mattermost:**
1. System Console → Integrations → Slash Commands
2. Create new slash command:
   - Command: `/ops`
   - Request URL: `https://n8n.insightpulseai.net/webhook/OPS_TOKEN`
   - Method: POST
   - Response Username: `ops-bot`
   - Autocomplete: `health|deploy|status`

**In n8n:**
1. Create Webhook node:
   - Path: `OPS_TOKEN`
   - Method: POST
   - Parse `body.text` from Mattermost
2. Branch on commands (`deploy`, `health`, etc.)
3. Return JSON:
   ```json
   {
     "response_type": "in_channel",
     "text": "✅ Deployment started..."
   }
   ```

#### Incoming Alerts from n8n → Mattermost

**In Mattermost:**
1. Create Incoming Webhook:
   - Channel: `#ops`
   - URL: `https://chat.insightpulseai.net/hooks/INCOMING_TOKEN`

**In n8n:**
1. Add HTTP Request node
2. POST to webhook URL:
   ```json
   {
     "text": ":white_check_mark: OCR service healthy"
   }
   ```

### Management Commands

```bash
# View logs
make chat-logs

# Stop
make chat-down

# Restart
make chat-down && make chat-up
```

---

## CI/CD Workflows

### Skills Consolidation Workflow

**File:** `.github/workflows/skills-consolidate.yml`

**Triggers:**
- Push to `main`/`develop` with changes to `skills/**`
- Pull requests to `main` with changes to `skills/**`
- Manual workflow dispatch

**Actions:**
1. Run `scripts/skills/consolidate.py`
2. Generate registry files
3. Upload artifacts
4. Auto-commit to branch (on push)
5. Comment on PR with skill count (on PR)

### n8n CLI CI

**File:** `.github/workflows/n8n-cli-ci.yml`

**Triggers:**
- Changes to `tools/ip-n8n/**`

**Actions:**
1. Test CLI help commands
2. Test subcommands
3. Verify executable permissions
4. Test config file creation

---

## Environment Variables

### Required for Agents

```bash
# GitHub
export GITHUB_TOKEN=ghp_xxxxx
export GITHUB_REPO_SLUG=jgtolentino/insightpulse-odoo
export GITHUB_DEFAULT_BRANCH=main

# Odoo
export ODOO_BASE_URL=https://erp.insightpulseai.net
export ODOO_BOT_TOKEN=xxxxx

# n8n (optional for CLI)
export N8N_API_KEY=xxxxx

# Mattermost (optional, defaults provided)
export MM_DB_PASSWORD=secure_password
```

---

## Deployment Checklist

### 1. Skills Consolidation

```bash
# Generate registries
make skills-consolidate

# Verify skill count (should show 9 skills)
make skills-open

# Validate all skills
make skills-validate
```

### 2. n8n CLI Setup

```bash
# Install CLI
make n8n-cli

# Configure
./ip-n8n login --base https://n8n.insightpulseai.net --key $N8N_API_KEY

# Test
./ip-n8n list
```

### 3. Mattermost Deployment

```bash
# Start Mattermost
make chat-up

# Configure Nginx
make chat-tls

# Get SSL certificate
sudo certbot --nginx -d chat.insightpulseai.net

# Create admin user via web UI
# Enable integrations
# Create slash commands and webhooks
```

### 4. n8n Workflows

1. Create webhook-triggered workflows in n8n
2. Configure slash commands in Mattermost
3. Test with `/ops health` command
4. Set up incoming webhooks for alerts

---

## Testing

### Skills Registry

```bash
# Test consolidation
make skills-consolidate

# Verify files exist
test -f skills/REGISTRY.json && echo "✅ REGISTRY.json"
test -f skills/REGISTRY.mcp.json && echo "✅ REGISTRY.mcp.json"
test -f docs/claude-code-skills/Section19.generated.md && echo "✅ Section19"
```

### n8n CLI

```bash
# Test commands
./ip-n8n --help
./ip-n8n list --help
./ip-n8n run --help
```

### Mattermost

```bash
# Check status
docker compose -f infra/docker/mattermost.compose.yml ps

# View logs
make chat-logs

# Test health
curl http://localhost:8065/api/v4/system/ping
```

---

## Troubleshooting

### Skills Consolidation Fails

**Issue:** Script errors or missing skills

**Solution:**
```bash
# Check Python version (requires 3.8+)
python3 --version

# Verify skill files have proper frontmatter
grep -r "**Skill ID:**" skills/
```

### n8n CLI Connection Failed

**Issue:** Cannot connect to n8n instance

**Solution:**
```bash
# Check n8n is running
curl https://n8n.insightpulseai.net/rest/version

# Verify API key is set
cat ~/.config/ip-n8n/config.json

# Re-login
./ip-n8n login --base https://n8n.insightpulseai.net --key $N8N_API_KEY
```

### Mattermost Won't Start

**Issue:** Docker containers fail to start

**Solution:**
```bash
# Check logs
docker compose -f infra/docker/mattermost.compose.yml logs

# Reset volumes (WARNING: deletes data)
docker compose -f infra/docker/mattermost.compose.yml down -v
make chat-up
```

### Slash Commands Not Working

**Issue:** `/ops` command returns error

**Solution:**
1. Verify webhook URL is correct in Mattermost
2. Check n8n workflow is activated
3. Test webhook directly:
   ```bash
   ./ip-n8n exec-webhook https://n8n.../webhook/OPS_TOKEN --data '{"text":"test"}'
   ```

---

## Security Recommendations

### API Keys
- Store in config files with `chmod 600`
- Use environment-specific keys
- Rotate keys quarterly
- Never commit to version control

### Webhooks
- Use random, long tokens in webhook URLs
- Restrict slash commands to specific channels
- Validate webhook signatures in n8n workflows
- Rate limit webhook endpoints

### Mattermost
- Enable TLS/HTTPS only
- Use strong database passwords
- Enable 2FA for admin accounts
- Restrict integration creation to admins

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     InsightPulse Stack                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐ │
│  │   Mattermost │────▶│     n8n      │────▶│    Odoo    │ │
│  │  (Slack Alt) │     │  Workflows   │     │    ERP     │ │
│  └──────────────┘     └──────────────┘     └────────────┘ │
│         │                    │                    │        │
│         │                    │                    │        │
│  ┌──────▼────────────────────▼────────────────────▼──────┐ │
│  │           Skills Registry (9 skills)                  │ │
│  │  - automation_executor    - draxlr_integration        │ │
│  │  - git_specialist         - github-*                  │ │
│  │  - automation_gap_analyzer                            │ │
│  │  - conflict_manager                                   │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Deployment Agents (4)                  │   │
│  │  - automation-executor  - automation-gap-analyzer   │   │
│  │  - git-specialist       - conflict-manager          │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Version History

### v0.2.0 (Current)
- ✅ Added Draxlr integration skill
- ✅ Created skills consolidation system
- ✅ Built n8n CLI tool (`ip-n8n`)
- ✅ Deployed Mattermost (Slack alternative)
- ✅ Integrated Mattermost ↔ n8n workflows
- ✅ Added 4 GitHub Developer Program skills
- ✅ CI/CD workflows for skills and n8n CLI

### v0.1.0
- Initial skills: automation_executor, git_specialist, automation_gap_analyzer, conflict_manager

---

## References

- [Skills Registry](../skills/REGISTRY.json)
- [MCP Registry](../skills/REGISTRY.mcp.json)
- [Section 19 (Generated)](./claude-code-skills/Section19.generated.md)
- [n8n CLI README](../tools/ip-n8n/README.md)
- [Mattermost Documentation](https://docs.mattermost.com/)
- [Draxlr Integration Guide](../skills/integrations/draxlr/SKILL.md)

---

**Maintained by:** InsightPulse AI Team
**License:** AGPL-3.0
**Version:** 0.2.0

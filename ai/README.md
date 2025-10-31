# Trusted AI Agent for Odoo Development

Reference implementation of Section 14 from the SaaS Replication Playbook.

## Architecture

```
┌─────────────────┐      ┌──────────────┐      ┌─────────────┐
│  Agent Service  │─────▶│ MCP Gateway  │─────▶│ Curated     │
│  (Python)       │      │ (Allowlist)  │      │ Tools       │
└─────────────────┘      └──────────────┘      └─────────────┘
        │
        ▼
┌─────────────────┐      ┌──────────────┐
│ E2B Sandbox     │─────▶│ GitHub API   │
│ (Isolated Exec) │      │ (HTTPS only) │
└─────────────────┘      └──────────────┘
        │
        ▼
┌─────────────────┐
│ Structured Logs │
│ (Correlation ID)│
└─────────────────┘
```

## Components

### `agent/main.py`
Minimal trusted agent stub demonstrating:
- **Sandbox abstraction** (E2B-ready with local mode fallback)
- **MCP Client** placeholder for tool routing
- **GitHub Client** via sandboxed HTTPS calls
- **Structured logging** with correlation IDs
- **CLI** for creating PRs

### `policy/policy.yaml`
E2B sandbox policy enforcing:
- Read-only filesystem (except /workspace, /tmp)
- Deny private CIDRs (prevents SSRF)
- Allowlist for public APIs only
- Resource limits (1 CPU, 1Gi RAM, 120s timeout)
- Audit logging

## Quick Start

### Local Mode (No E2B)

```bash
# Install dependencies
pip install -r agent/requirements.txt

# Create a demo PR
python -m ai.agent.main create-pr \
  --repo your-org/your-repo \
  --base main \
  --branch agent-demo-$(date +%s) \
  --file DEMO.md \
  --content "# Agent Test\n\nCreated by trusted agent" \
  --message "docs: agent demo" \
  --title "Demo PR from Trusted Agent" \
  --body "This PR demonstrates safe agent-driven PRs"
```

### Docker Mode

```bash
# Build agent image
cd ai/agent
docker build -t odoo-agent:latest .

# Run
docker run --rm \
  -e GITHUB_TOKEN=ghp_xxx \
  -e GITHUB_REPO=your-org/your-repo \
  odoo-agent:latest create-pr \
    --file DEMO.md \
    --content "# Test" \
    --message "test" \
    --title "Test" \
    --body "Test"
```

### Full Stack (Docker Compose AI Profile)

```bash
# Start MCP Gateway + Model Runner + Agent
make ai-up

# Or manually
docker compose --profile ai up -d

# Check logs
docker compose logs agent

# Stop
make ai-down
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GITHUB_TOKEN` | GitHub PAT or App token | Required |
| `GITHUB_REPO` | Repository (owner/repo) | Required |
| `GITHUB_BASE` | Base branch | main |
| `E2B_API_KEY` | E2B API key | Optional (local mode) |
| `E2B_API_URL` | E2B API endpoint | https://api.e2b.dev |
| `MCP_SERVER_URL` | MCP Gateway URL | http://mcp-gateway:8080 |
| `MODEL_RUNNER_URL` | Model Runner URL | http://model-runner:8080 |

### Sandbox Policy

Edit `policy/policy.yaml` to:
- Add allowed API endpoints
- Adjust resource limits
- Configure audit logging

## Security

### Threat Model

**Protected Against:**
- ✅ Shell injection (no shell access)
- ✅ SSRF to internal services (deny private CIDRs)
- ✅ File system tampering (read-only FS)
- ✅ Secret exfiltration (no secret mounting)
- ✅ Resource exhaustion (CPU/memory/timeout limits)

**Out of Scope:**
- ❌ GitHub token compromise (use read-only tokens)
- ❌ MCP Gateway bypass (enforce allowlist at infra level)
- ❌ Model prompt injection (separate concern)

### Best Practices

1. **Use read-only GitHub tokens** where possible
2. **Enforce PR-based workflow** (no direct pushes)
3. **Enable branch protection** (require tests + reviews)
4. **Run SBOM + vuln scans** in CI
5. **Audit agent actions** via structured logs
6. **Red-team periodically** (try to bypass sandbox)

## Development

### Adding Features

1. Add new methods to `TrustedAgent` class
2. Update CLI parser with new subcommand
3. Add integration tests
4. Update MCP allowlist if new tools needed

### Testing

```bash
# Unit tests (TODO: add pytest tests)
pytest agent/tests/

# Integration test (requires GITHUB_TOKEN)
export GITHUB_TOKEN=ghp_xxx
export GITHUB_REPO=test-org/test-repo
python -m ai.agent.main create-pr --help
```

### Logging

All logs are JSON-structured with correlation IDs:

```json
{
  "ts": 1730361611000,
  "level": "INFO",
  "cid": "cid-1730361611000",
  "msg": "sandbox.created",
  "run_id": "local-1730361611000"
}
```

Ship to Loki/ELK for observability.

## Integration with Odoo

### Odoo Model Extension

Add agent traceability to your models:

```python
class SaaSRequest(models.Model):
    _name = 'saas.request'

    agent_id = fields.Char(string='Agent ID')
    sandbox_run_id = fields.Char(string='Sandbox Run ID')
    correlation_id = fields.Char(string='Correlation ID')
```

Display in chatter for audit trail.

### Workflow Example

1. **User submits** SaaS feature request in Odoo
2. **Agent analyzes** OCA modules via `search-oca-modules.sh`
3. **Agent proposes** module composition in PR
4. **CI validates** (tests, lint, SBOM, vulns)
5. **Human reviews** and merges
6. **Odoo links** to PR via `sandbox_run_id`

## Troubleshooting

### "GITHUB_TOKEN is required"
Set the token: `export GITHUB_TOKEN=ghp_xxx`

### "E2B_API_KEY not set; running in LOCAL_MODE"
This is normal. The agent works in local mode without E2B.

### "GitHub API error 404"
Check repo exists and token has access: `owner/repo`

### "MCP Gateway connection refused"
MCP Gateway only runs in Docker Compose AI profile: `make ai-up`

## References

- [SaaS Replication Playbook - Section 14](../SAAS_REPLICATION_PLAYBOOK.md#14-trusted-ai-with-docker--e2b-agents-mcp-model-runner)
- [E2B Sandbox Documentation](https://e2b.dev/docs)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [GitHub REST API](https://docs.github.com/en/rest)

## License

LGPL-3 (same as parent project)

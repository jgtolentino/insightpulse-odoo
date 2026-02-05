# Odoo Developer Agent

**AI-powered senior Odoo developer replacing $120K/year salary with $2K/year in API costs**

A production-ready MCP (Model Context Protocol) server that generates, debugs, optimizes, and reviews Odoo 18 CE modules with 95%+ OCA compliance.

---

## Features

### 🏗️ Module Generation
- Complete Odoo module scaffolding (models, views, security, tests)
- OCA-compliant code structure
- Automatic README and i18n setup
- Quality checks (pylint-odoo, pre-commit)

### 🐛 Error Debugging
- Parse and analyze Odoo error tracebacks
- Search similar past errors and solutions
- Auto-fix code when confidence > 90%
- Store solutions in knowledge base

### ⚡ Code Optimization
- Eliminate N+1 queries
- Proper @api.depends usage
- Batch operations
- SQL query optimization

### 👀 Code Review
- OCA standard compliance
- Security vulnerability detection
- Performance issue identification
- Breaking change detection

### 📚 Knowledge Search
- Odoo 18 CE documentation
- OCA module examples
- Past error solutions
- Custom module patterns

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│  MCP Server (Claude Sonnet 4.5)                  │
│  - Tool routing & orchestration                  │
│  - Context management                            │
└──────────────────────────────────────────────────┘
                      ↓
┌─────────────────┬─────────────────┬──────────────┐
│ Module Gen      │ Code Analyzer   │ RAG System   │
│ - Scaffolding   │ - Debugging     │ - Supabase   │
│ - OCA Checks    │ - Optimization  │ - pgvector   │
│ - Tests         │ - Reviews       │ - Embeddings │
└─────────────────┴─────────────────┴──────────────┘
```

---

## Quick Start

### 1. Prerequisites

- Docker & Docker Compose
- Anthropic API key ([get one](https://console.anthropic.com))
- Supabase account ([sign up](https://supabase.com))

### 2. Setup

```bash
# Clone repository
git clone https://github.com/jgtolentino/odoo-developer-agent.git
cd odoo-developer-agent

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env
```

### 3. Initialize Knowledge Base

```bash
# Start database
docker-compose up -d knowledge-db

# Wait for database to be ready
sleep 10

# Run knowledge base indexer
python scripts/index_knowledge_base.py
```

This will index:
- Odoo 18 CE core documentation
- Top 50 OCA modules
- Common error patterns

### 4. Start Agent

```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f odoo-developer-agent

# Verify health
curl http://localhost:3001/health
```

---

## Usage Examples

### Example 1: Generate a BIR Compliance Module

```python
# Using the MCP client
from mcp import ClientSession

async with ClientSession() as session:
    result = await session.call_tool(
        "generate_odoo_module",
        {
            "module_name": "insightpulse_bir_1601c",
            "description": "Philippine BIR 1601-C monthly tax filing automation",
            "models": [
                {
                    "name": "bir_1601c",
                    "description": "BIR Form 1601-C model",
                    "fields": [
                        {"name": "tin", "type": "Char", "required": True},
                        {"name": "filing_month", "type": "Date", "required": True},
                        {"name": "total_tax_withheld", "type": "Float"},
                        {"name": "state", "type": "Selection", 
                         "options": ["draft", "filed", "paid"]}
                    ],
                    "methods": [
                        "compute_total_tax",
                        "generate_dat_file",
                        "submit_to_efps"
                    ]
                }
            ],
            "views": [
                {
                    "model": "bir_1601c",
                    "type": "form",
                    "fields": ["tin", "filing_month", "total_tax_withheld", "state"]
                },
                {
                    "model": "bir_1601c",
                    "type": "tree",
                    "fields": ["tin", "filing_month", "total_tax_withheld", "state"]
                }
            ],
            "dependencies": ["account"],
            "category": "Accounting/Localization"
        }
    )
    
    print(result)
    # ✅ Module Generated Successfully
    # Module: /odoo/custom-addons/insightpulse_bir_1601c
    # Files Created: 15 files
    # Quality Score: 98%
```

### Example 2: Debug an Error

```python
error_log = """
Traceback (most recent call last):
  File "/odoo/odoo/models.py", line 6104, in write
    self._write(vals)
  File "/odoo/addons/account/models/account_move.py", line 1234, in _write
    lines = self.line_ids.filtered(lambda l: l.account_id.internal_type == 'receivable')
AttributeError: 'bool' object has no attribute 'internal_type'
"""

result = await session.call_tool(
    "debug_odoo_error",
    {
        "error_log": error_log,
        "module_name": "account",
        "auto_fix": True
    }
)

# ✅ Error Analysis Complete
# Root Cause: Accessing internal_type on account_id when it's False
# Fix Applied: Yes (confidence 95%)
# Files Modified: 1 (account_move.py)
```

### Example 3: Optimize Code

```python
result = await session.call_tool(
    "optimize_odoo_code",
    {
        "file_path": "/odoo/custom-addons/my_module/models/sale_order.py",
        "optimization_goals": ["performance", "sql"]
    }
)

# ✅ Code Optimization Complete
# Improvements:
# - [PERFORMANCE] Replaced loop with batch operation (Impact: high)
# - [SQL] Added index on frequently queried field (Impact: high)
# - [PERFORMANCE] Used read_group instead of search + read (Impact: medium)
# Estimated Speedup: 5x faster
```

### Example 4: Review Pull Request

```python
result = await session.call_tool(
    "review_code_changes",
    {
        "changed_files": ["models/account_move.py", "views/account_move_views.xml"],
        "diff_content": open("my-pr.diff").read()
    }
)

# ✅ Code Review Complete
# Status: NEEDS_CHANGES
# Comments: 3
# 🟡 [WARNING] Missing _() wrapper for translatable strings (Line 45)
# 🔵 [SUGGESTION] Consider using @api.depends instead of compute (Line 78)
# 🔴 [CRITICAL] SQL injection vulnerability (Line 102)
```

---

## Integration with Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "odoo-developer": {
      "command": "docker",
      "args": ["exec", "-i", "odoo-dev-agent", "python", "server.py"]
    }
  }
}
```

Now you can use the agent in Claude Desktop:

```
User: Generate a module for tracking employee expense reimbursements

Claude: I'll use the odoo-developer agent to generate that module.
[Calls generate_odoo_module tool]
✅ Module created at /odoo/custom-addons/insightpulse_hr_expense
```

---

## Knowledge Base Management

### Add Custom Documentation

```bash
# Add your own modules to knowledge base
python scripts/index_custom_modules.py \
  --module-path /path/to/your/module \
  --description "Your module description"

# Add error solutions
python scripts/add_error_solution.py \
  --error "Your error message" \
  --solution "How you fixed it"
```

### Update Knowledge Base

```bash
# Re-index Odoo documentation (after upgrades)
python scripts/index_knowledge_base.py --force

# Index new OCA modules
python scripts/index_oca_modules.py --repos "OCA/repo-name"
```

---

## Monitoring & Metrics

### Prometheus Metrics

Available at `http://localhost:9090`:

- `agent_tool_calls_total` - Total tool invocations
- `agent_tool_duration_seconds` - Tool execution time
- `agent_auto_fix_success_rate` - % of successful auto-fixes
- `agent_quality_score_avg` - Average module quality score

### Grafana Dashboards

Access at `http://localhost:3000` (default: admin/admin):

- **Agent Performance** - Tool usage, latency, success rates
- **Module Generation** - Modules created, quality trends
- **Error Resolution** - Errors fixed, confidence scores
- **Cost Tracking** - API usage, cost per tool call

---

## Cost Analysis

### Monthly Cost Breakdown (100 clients)

| Activity | API Calls/Month | Cost |
|----------|-----------------|------|
| Module Generation | 20 modules × 10 calls | $3.00 |
| Error Debugging | 50 errors × 5 calls | $3.75 |
| Code Optimization | 30 files × 4 calls | $1.80 |
| Code Reviews | 100 PRs × 3 calls | $4.50 |
| Knowledge Search | 500 searches × 1 call | $7.50 |
| **Total** | **~2,000 calls** | **$20.55** |

**Annual Cost:** $246.60  
**Human Developer Cost:** $120,000  
**Savings:** $119,753.40 (99.8%)

---

## Advanced Configuration

### Custom Prompts

Edit prompt templates in `prompts/`:

```python
# prompts/module_templates.py
CUSTOM_MODULE_PROMPT = """
Your custom instructions for module generation...
"""
```

### Quality Thresholds

Adjust in `.env`:

```bash
# Only auto-fix errors with 95%+ confidence
AUTO_FIX_CONFIDENCE_THRESHOLD=0.95

# Require 90%+ quality score for generated modules
MODULE_QUALITY_THRESHOLD=0.90
```

### OCA Integration

Install OCA quality tools:

```bash
pip install pylint-odoo
pip install odoo-module-migrator

# Run checks on generated modules
pre-commit run --all-files
```

---

## Deployment to Production

### DigitalOcean Deployment

```bash
# Create Droplet (4GB RAM, 2 vCPUs)
doctl compute droplet create odoo-agent \
  --image docker-20-04 \
  --size s-2vcpu-4gb \
  --region sgp1

# Deploy via Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Setup auto-scaling
doctl compute droplet-action resize <droplet-id> \
  --size s-4vcpu-8gb
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n odoo-agents
```

---

## Continuous Learning

The agent improves over time through:

1. **Feedback Loop** - Human corrections stored in knowledge base
2. **Solution Storage** - Every fixed error becomes training data
3. **Module Examples** - Generated modules indexed for future reference
4. **Usage Analytics** - Track which patterns work best

View learning metrics:

```bash
python scripts/show_learning_metrics.py
```

---

## Troubleshooting

### Agent not starting?

```bash
# Check logs
docker-compose logs odoo-developer-agent

# Verify environment variables
docker-compose config

# Test Anthropic API
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY"
```

### Low quality scores?

```bash
# Re-index knowledge base with more examples
python scripts/index_knowledge_base.py --sources oca,custom

# Add your best modules as examples
python scripts/add_quality_examples.py --path /your/best/module
```

### High API costs?

```bash
# Enable caching for repeated queries
ENABLE_PROMPT_CACHING=true

# Reduce context size
MAX_CONTEXT_TOKENS=4000

# Use smaller model for simple tasks
SIMPLE_TASK_MODEL=claude-3-haiku-20240307
```

---

## Roadmap

- [ ] Fine-tuning on InsightPulse AI codebase
- [ ] Integration with GitHub Copilot Workspace
- [ ] Multi-agent collaboration (dev + QA + devops)
- [ ] Automated module marketplace submission
- [ ] Real-time pair programming mode
- [ ] Custom model training for domain-specific code

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

AGPL-3.0 License - See [LICENSE](LICENSE)

---

## Support

- **Documentation:** https://docs.insightpulseai.net/agents/odoo-developer
- **Issues:** https://github.com/jgtolentino/odoo-developer-agent/issues
- **Discussions:** https://github.com/jgtolentino/odoo-developer-agent/discussions
- **Email:** support@insightpulseai.net

---

## Acknowledgments

Built by [InsightPulse AI](https://insightpulseai.net) as part of our mission to make enterprise software development accessible through AI automation.

Powered by:
- [Anthropic Claude](https://anthropic.com)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Odoo Community (OCA)](https://odoo-community.org)
- [Supabase](https://supabase.com)

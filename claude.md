# Claude AI Assistant Context
**Last Updated:** 2026-01-27
**Purpose:** AI assistant instructions for code generation and architectural guidance
**Freshness:** Maximum 7 days (enforced by CI/CD)

> For operational tasks (installation, monitoring, troubleshooting), see [README.md](README.md).

---

## Section 0: Repository Overview

### Project Mission
InsightPulse Odoo is a **multi-tenant, BIR-compliant Finance Shared Service Center (SSC)** platform built on Odoo 18 CE, replacing expensive SaaS tools like SAP Ariba, Concur, and QuickBooks with 100% open-source alternatives.

### Core Principles
1. **Multi-Tenant First** - Legal entity isolation via `company_id`, not organizational routing
2. **BIR Compliance** - Immutable records, audit trails, e-invoicing ready
3. **Automation-First** - CI/CD, documentation, and deployment fully automated
4. **OCA Standards** - Follow Odoo Community Association conventions strictly
5. **Security by Default** - SQL injection prevention, XSS protection, CSRF tokens

### Key Technologies
- **ERP:** Odoo 18.0 Community Edition
- **Database:** PostgreSQL 15.6 with multi-tenant RLS
- **BI/Analytics:** Apache Superset (Tableau alternative)
- **Backend:** Supabase (auth, storage, edge functions)
- **OCR:** PaddleOCR with DeepSeek LLM validation
- **Infrastructure:** DigitalOcean (Docker, App Platform)

---

## Section 10: Code Generation Guidelines

### When Asked to Write Code

#### 1. Always Check Context First
```bash
# Check if module exists
ls -la odoo/addons/module_name/

# Check existing patterns
grep -r "class.*Model" odoo/addons/module_name/

# Review OCA conventions
cat .github/PLANNING.md
```

#### 2. Follow Odoo Conventions

**Model Structure:**
```python
# âœ… CORRECT: Multi-tenant model
from odoo import models, fields, api

class ExpenseReport(models.Model):
    _name = 'expense.report'
    _description = 'Expense Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_submitted desc'

    # Multi-tenant isolation (REQUIRED)
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        index=True
    )

    # BIR compliance fields
    bir_form_2307 = fields.Binary('BIR Form 2307 (Withholding Tax)')
    audit_trail = fields.Text('Audit Trail', readonly=True)

    @api.model
    def create(self, vals):
        # Log audit trail
        vals['audit_trail'] = f"Created by {self.env.user.name} at {fields.Datetime.now()}"
        return super().create(vals)
```

**❌ WRONG: Not multi-tenant**
```python
# Missing company_id
class ExpenseReport(models.Model):
    _name = 'expense.report'
    # Missing: company_id field
    # This violates multi-tenant requirement!
```

#### 3. Security Checklist

Before generating any code, ensure:

- [ ] **SQL Injection:** Use ORM methods, never raw SQL with user input
- [ ] **XSS Prevention:** Escape HTML in templates (`t-esc` not `t-raw`)
- [ ] **CSRF Protection:** Use Odoo's built-in CSRF tokens for forms
- [ ] **Access Rights:** Define `ir.model.access.csv` and record rules
- [ ] **Multi-Tenant Isolation:** Add `company_id` filter to all queries

**âœ… Safe SQL:**
```python
# Use ORM
self.env['expense.report'].search([('company_id', '=', self.env.company.id)])

# If raw SQL is unavoidable (rare), use parameterized queries
self.env.cr.execute("SELECT * FROM expense_report WHERE company_id = %s", (company_id,))
```

**❌ Unsafe SQL:**
```python
# NEVER do this - SQL injection vulnerability!
query = f"SELECT * FROM expense_report WHERE name = '{user_input}'"
self.env.cr.execute(query)
```

#### 4. BIR Compliance Patterns

**Immutable Records (Forms 2307, 2316):**
```python
class BIRForm2307(models.Model):
    _name = 'bir.form.2307'
    _description = 'BIR Form 2307 - Certificate of Creditable Tax Withheld at Source'
    _rec_name = 'certificate_number'

    # Immutable after submission
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('cancelled', 'Cancelled')
    ], default='draft', tracking=True)

    # Prevent modification after submission
    @api.constrains('state')
    def _check_immutable(self):
        for record in self:
            if record.state == 'submitted' and self._origin.state == 'submitted':
                raise ValidationError("Cannot modify submitted BIR forms")
```

#### 5. Include Tests

Every module MUST have tests:

```python
# tests/__init__.py
from . import test_expense_report

# tests/test_expense_report.py
from odoo.tests import TransactionCase

class TestExpenseReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.expense_model = self.env['expense.report']

    def test_multi_tenant_isolation(self):
        """Test company_id isolation"""
        company1 = self.env['res.company'].create({'name': 'Company 1'})
        company2 = self.env['res.company'].create({'name': 'Company 2'})

        expense1 = self.expense_model.create({
            'name': 'Expense 1',
            'company_id': company1.id
        })

        # Switch to company2 context
        expense_search = self.expense_model.with_context(
            allowed_company_ids=[company2.id]
        ).search([('id', '=', expense1.id)])

        self.assertFalse(expense_search, "Should not find expense from another company")
```

#### 6. Document as You Go

Every module needs:

```markdown
# odoo/addons/expense_mgmt/README.md

# Expense Management Module

## Overview
Multi-tenant expense reporting with BIR compliance (Forms 2307, 2316).

## Features
- Multi-level approval workflows
- BIR withholding tax calculation
- OCR receipt scanning (PaddleOCR)
- Superset analytics integration

## Installation
See [INSTALLATION.md](../../docs/INSTALLATION.md)

## Configuration
1. Navigate to Settings > Expense Management
2. Configure approval levels per company
3. Upload BIR tax tables

## Usage
See [USER_GUIDE.md](docs/USER_GUIDE.md)

## API Reference
See [API.md](docs/API.md)

## Testing
```bash
./automate.sh test expense_mgmt
```

## BIR Compliance
- Form 2307: Automated generation
- Form 2316: Annual summary
- e-Invoicing: Ready for 2025 BIR rollout

## License
LGPL-3.0
# Claude / GPT Assistant Context – InsightPulse AI Monorepo

**Purpose**: Operating contract + context for AI assistants working in this repo
**Audience**: Claude 4 (Sonnet/Opus) and compatible assistants
**Last Updated**: 2025-11-08
**Primary ERP Target**: **Odoo 18 CE** (consistent across project; do not mix APIs—see version matrix)

---

## 0) Normative Rules (Read First)

* **MUST** default to **Odoo CE + OCA** modules; no Enterprise calls or APIs.
* **MUST** treat **multi-tenancy as separate legal entities** (company/db isolation), **NOT** user routing.
* **MUST** keep **BIR compliance**: immutable accounting trail; corrections via reversal entries, not in-place edits.
* **MUST** add **tests** for any code output (unit or HttpCase as applicable).
* **MUST** keep **OpenAPI x-atomic + x-role-scopes** on any new controller you propose.
* **MUST NOT** hardcode secrets/URLs; use env or `ir.config_parameter`.
* **SHOULD** propose a CI gate or eval when adding any new capability.
* **SHOULD** prefer **self-hosted** alternatives and list annual savings when suggesting replacements.

---

## 1) Repository Mission

Build an **enterprise-grade Finance Shared Service Center (SSC)** for the Philippines:

* **ERP**: Odoo CE (v18 now; v19 later) + OCA.
* **SaaS parity**: Odoo modules replace Concur/Ariba, Superset replaces Tableau.
* **BIR compliant** processes (2307, 2316, e-invoicing, immutable audit).
* **Multi-tenant** = per-legal-entity isolation (DB/company), not department routing.

**Cost Objective**: prefer open-source to save **$50k+/year** (details in SaaS table below).

---

## 2) Versioning & API Matrix

| Area     | Primary       | Notes                                                            |
| -------- | ------------- | ---------------------------------------------------------------- |
| Odoo     | **18 CE**     | Use Odoo 18.0 docs & APIs exclusively; ignore any Odoo 19 references. |
| OCA      | 18.0 branches | Match module branches to Odoo 18.0.                                |
| Docs     | Odoo **18.0** | Link to odoo.com/documentation/18.0/ for controllers/QWeb.                            |
| Superset | latest        | Official image behind Nginx `/superset`.                         |

> **Odoo 19 References**: If you encounter "Odoo 19" in project files, treat them as **planning artifacts**. Active implementation uses **Odoo 18 CE only**.

---

## 3) Multi-Tenant vs Agencies (Do/Don't)

**Tenancy (legal entities)**

* ✅ Separate DB or strict `company_id` isolation
* ✅ Separate books, taxes, numbering, reports
* ✅ Per-company config via `ir.config_parameter`

**Agencies (internal units)**

* ✅ Stored as org structure/tags under one company
* ❌ Not a tenant, no cross-db split
* ❌ No security boundaries beyond role/rules

**Code cue**

```python
# ✅ Tenant isolation (legal entity)
company_id = fields.Many2one('res.company', required=True)

# ❌ Not tenancy
agency_id = fields.Many2one('hr.department')  # internal only
```

---

## 4) BIR Compliance (PH)

* **Immutable** accounting: corrections via reversal entries (no mutation).
* **2307 / 2316** generation pipeline.
* **Audit trail**: chatter + mail.activity + journal entries produce immutable evidence.
* **E-invoice**: pluggable connector, never hardcode endpoints.

**Compliance cue**

```python
# ✅ Reverse + rebook
def action_correct(self, new_amount):
    self.copy({'amount': -self.amount, 'is_correction': True})
    return self.copy({'amount': new_amount})
```

---

## 5) Assistant Operating Modes

### Write Code

1. Inspect context: paths, module patterns, manifests.
2. Use `_inherit` vs `_name` correctly; add `__manifest__.py`.
3. Always add tests (unit/HttpCase) and a brief module README.
4. Output OpenAPI with **x-atomic** and **x-role-scopes** for controllers.

### Architecture

1. Cite **existing docs** in `docs/` and `claudedocs/`.
2. Check **tenancy impact** and **BIR** implications.
3. Add a CI/eval gate for any new surface.

### Deploy

* Only when **explicitly requested** or deployment keywords are present (Odoo/InsightPulse/SaaS replacement/Finance SSC/BIR).
* Sequence: generate → deploy → health → smoke → verify → stop.

---

## 6) Repo Layout (authoritative)

```
insightpulse-odoo/
├── .github/                # CI, skillsmith, evals, planning
├── odoo/
│   ├── addons/             # Custom modules (18.0)
│   └── tests/              # Odoo HttpCase/integration tests
├── docs/                   # Architecture, API, deployment guides
├── superset/               # Compose + dashboards
├── warehouse/              # Supabase SQL views & MVs
├── skillsmith/             # Error→skill miner & templates
├── scripts/                # Validation, scaffolds, docs generators
└── claude.md               # This file (assistant contract)
```

---

## 7) Development Commands

```bash
# Validate repo structure
python scripts/validate-repo-structure.py

# Run Odoo tests (HttpCase etc.)
pytest odoo/tests -q

# Full evals (OCR + Warehouse)
pytest tests/test_ocr_endpoints.py tests/test_warehouse_views.py -q

# Lint
black odoo/ --check && flake8 odoo/ && pylint odoo/addons/
```

---

## Section 11: Conditional Deployment Mode

### When to Auto-Deploy vs Just Advise

**Auto-Deploy Triggers (use automation):**
- Query mentions: "Odoo", "InsightPulse AI", "Finance SSC", "BIR compliance"
- Task type: "create module", "deploy", "add feature", "fix bug"
- User says: "automate this", "deploy now", "production ready"

**Just Advise (conversational mode):**
- General questions: "How does Odoo work?", "What is multi-tenancy?"
- Exploratory: "Should I use Odoo or NetSuite?"
- Learning: "Explain BIR Form 2307"

**Example Auto-Deploy:**
```
User: "Create a travel request module with multi-level approval"
## 8) Controllers & QWeb (Odoo 18 Canon)

* JSON routes: `@http.route(..., type='json', auth='user', csrf=False)`
* Login page inheritance: extend **the active** template:

  * `auth_signup.login`, `website.login`, or `web.login`
  * Inject OAuth block after `.o_login_buttons`
* OAuth: Odoo **Google provider** uses `/auth_oauth/signin` (never alternate paths)

**Contract cue (OpenAPI)**

```json
{
  "paths": {
    "/ip/expense/intake": {
      "post": {
        "x-atomic": true,
        "x-role-scopes": ["employee","erp.bot.expense"]
      }
    }
  }
}
```

---

## 9) SaaS Replacement Table (savings)

| SaaS                          | Replacement            | Savings/yr |
| ----------------------------- | ---------------------- | ---------- |
| SAP Concur                    | Odoo Expense           | $15k       |
| SAP Ariba                     | Odoo Procurement       | $12k       |
| Tableau                       | Superset               | $8.4k      |
| Slack Ent                     | Mattermost/Rocket.Chat | $12.6k     |
| Odoo Enterprise               | Odoo CE+OCA            | $4.7k      |
| **Total Est.**: **$52.7k/yr** |                        |            |

---

## 10) Evals (Blocking)

Your code must keep these **green**:

1. **OpenAPI contract** (CI gate)

   * `x-atomic` + `x-role-scopes` on all new ops

2. **Login OAuth block present** (Odoo HttpCase)

   * `#ip-oauth-buttons` renders on compiled `/web/login?debug=assets`
   * `/auth_oauth/signin?provider=` link is present if any provider is enabled

3. **Expense intake idempotency** (Odoo HttpCase)

   * 2nd POST with same `idempotency_key` returns `idempotent: true`

4. **OCR service health & contract** (pytest)

   * `GET /health` → `{ok:true}`
   * `POST /classify/expense` → `{category, conf:[0..1]}`

5. **Warehouse view exists** (pytest + psycopg)

   * `vw_expense_fact` visible; MVs refresh scheduled

---

## 11) Deployment Guardrails

* **SSO**: unified cookie `ip_sso` (HttpOnly; `Domain=.insightpulseai.net`; `SameSite=None`; `Secure`).
* **Nginx**: OCR host `client_max_body_size 10m`.
* **Secrets**: env vars or `ir.config_parameter`; never hardcode.
* **Rollbacks**: module upgrade with `--stop-after-init` + restart; revert via Git/CI.

---

## 12) Code Style (OCA-aligned)

* Python: docstrings, `mail.thread` for audit where relevant, no raw SQL with user input.
* XML: explicit comments for XPaths; put buttons under proper states; use `statusbar` for state.
* Manifests: correct `depends`, license `LGPL-3`, version bump on breaking changes.

---

## 13) Common Pitfalls (and fixes)

* **Tenancy drift**: don't gate by agency—use company; if multi-company rules missing, add `groups="base.group_multi_company"`.
* **Mutable finance**: no edits to posted entries—use reversals.
* **Manual deploys**: CI handles; local SCP is forbidden.
* **Hardcoded config**: use env/ICP; surface toggles in Settings.

---

## 14) Success Metrics (track)

* Perf: <200 ms CRUD, <3 s dashboards p95, <10 queries/page
* Quality: >80% coverage on module logic
* Compliance: BIR docs generatable; posted moves immutable
* Uptime: >99.9%; error rate trends down; Skillsmith proposes ≥1 skill/week

---

## 15) When Unsure—Ask High-Leverage Questions

* "Will this cross company boundaries or is it per-entity?"
* "What BIR artifact is affected (2307/2316/e-invoice)?"
* "Which OCA module covers 80% so we customize the last 20%?"

---

## 16) Pinned External References

* Odoo **18.0** docs (controllers, QWeb, testing)
* OCA GitHub org
* BIR public pages (PH)
* Superset official

---

## 17) MCP Server Registry (Canonical)

**7 MCP Servers** configured for VSCode interface:

### pulser-hub (Odoo & Ecosystem Integration)
- **Command**: `docker run -i --rm pulser-hub-mcp:latest`
- **Purpose**: Pulser Hub MCP Server for Odoo and ecosystem integration
- **Tools**: 5 tools (odoo, deployment, ecosystem)
- **DO App ID**: 60a13dec-1b31-4daf-b4c3-bfe8ca0dbfc8
- **Status**: ✅ Deployed (GitHub App: 2191216)

### digitalocean (App Platform Management)
- **Command**: `npx -y @modelcontextprotocol/server-digitalocean`
- **Env**: `DIGITALOCEAN_TOKEN` (from env)
- **Purpose**: DigitalOcean App Platform infrastructure management
- **Tools**: 3 tools (infrastructure, kubernetes, database)
- **Use Cases**: App deployment, log monitoring, metrics

### kubernetes (Cluster Operations)
- **Command**: `npx -y @modelcontextprotocol/server-kubernetes`
- **Env**: `KUBECONFIG` (from env)
- **Purpose**: Kubernetes cluster operations
- **Tools**: 22 tools (cluster, deployment, monitoring, networking)
- **Cluster**: do-nyc3-superset-ai-cluster (nyc3 region)

### docker (Container Management)
- **Command**: `npx -y @modelcontextprotocol/server-docker`
- **Purpose**: Docker container management
- **Tools**: 1 tool (container operations)
- **Registry**: docker.io

### github (Repository Management)
- **Command**: `npx -y @modelcontextprotocol/server-github`
- **Env**: `GITHUB_TOKEN` (from env)
- **Purpose**: GitHub repository management
- **Tools**: 40 tools (repository, ci_cd, issues, actions)

### superset (Apache Superset Analytics)
- **Command**: `npx -y @modelcontextprotocol/server-superset`
- **Env**: `SUPERSET_URL`, `SUPERSET_USERNAME`, `SUPERSET_PASSWORD`
- **URL**: https://insightpulseai.net/odoo/superset
- **Purpose**: Apache Superset analytics, dashboard creation, SQL execution
- **Tools**: 3+ tools (analytics, dashboard, chart)
- **App ID**: bc1764a5-b48e-4bec-aa72-8a22cab141bc

**MCP Configuration**: Auto-starts with VSCode, log level: info, total tools: 98

---

## 18) Agent Definitions (Multi-Agent System)

**SuperClaude Architecture**: 4 specialized domain agents

### 1. odoo_developer
- **Location**: `~/.claude/superclaude/agents/domain/odoo-developer.agent.yaml`
- **Expertise**: Odoo 18.0 CE module development, OCA standards, Python 3.11, XML views
- **Skills**: `odoo-module-scaffold`, `odoo-finance-automation`, `odoo-agile-scrum-devops`
- **MCP Servers**: GitHub, DigitalOcean (App Platform), Supabase
- **Context**: 8 agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB), BIR compliance, AGPL-3 license, Odoo 18.0 CE only
- **Auto-Activation**: Keywords: "odoo module", "scaffold", "manifest.py", "models", "views", "controller"

### 2. finance_ssc_expert
- **Location**: `~/.claude/superclaude/agents/domain/finance-ssc-expert.agent.yaml`
- **Expertise**: Philippine BIR compliance (Forms 1601-C, 1702-RT, 2550Q, 2550M), multi-agency Finance SSC operations, month-end closing
- **Skills**: `odoo-finance-automation`, `bir-tax-filing`
- **MCP Servers**: Supabase (Warehouse), Superset (Analytics), Notion (Documentation)
- **Context**: 8 agencies with TIN numbers, quarterly/monthly BIR deadlines, withholding tax compliance
- **Auto-Activation**: Keywords: "BIR", "1601-C", "2550Q", "2550M", "agency", "month-end", "finance", "tax", "withholding"

### 3. bi_architect
- **Location**: `~/.claude/superclaude/agents/domain/bi-architect.agent.yaml`
- **Expertise**: Apache Superset 3.0, Tableau Cloud, SQL (PostgreSQL), RLS (Row-Level Security), data modeling
- **Skills**: `superset-dashboard-automation`, `superset-chart-builder`, `superset-sql-developer`
- **MCP Servers**: Superset (Chart/Dashboard creation), Tableau (Published sources), Supabase (Direct PostgreSQL)
- **Context**: Scout transaction data, Odoo analytics integration, MindsDB predictive analytics
- **Auto-Activation**: Keywords: "superset", "dashboard", "sql view", "analytics", "metrics", "chart", "tableau"

### 4. devops_engineer
- **Location**: `~/.claude/superclaude/agents/domain/devops-engineer.agent.yaml`
- **Expertise**: DigitalOcean App Platform, Docker containerization, CI/CD pipelines, GitHub Actions
- **Skills**: `odoo-agile-scrum-devops`, `github-actions-ci`
- **MCP Servers**: DigitalOcean (App Platform API), GitHub (Repository management, CI/CD), Docker Hub (Image registry)
- **Context**: Production deployments (SFO2, SGP regions), zero-downtime strategies, infrastructure as code
- **Auto-Activation**: Keywords: "deploy", "docker", "ci/cd", "pipeline", "digitalocean", "github actions", "deployment"

**Agent Coordination**: Orchestrated via MCP Coordinator (https://mcp.insightpulseai.net)

---

## 19) Skills Inventory (Auto-Linked)

**46 Skills Total** (auto-synced via SessionStart hook in `.claude/settings.json`)

### Categories
- **Anthropic Official**: 15 skills (document-skills: docx, pdf, pptx, xlsx)
- **Community**: 24 skills (odoo, bir-tax-filing, superset-*, supabase-automation)
- **Notion**: 4 skills (notion-knowledge-capture, notion-meeting-intelligence, etc.)
- **Other**: 3 skills

### Key Skills for This Project
- `odoo-module-scaffold` - OCA-compliant Odoo 19.0 module scaffolding
- `odoo-finance-automation` - BIR tax filing automation (1601-C, 1702-RT, 2550Q)
- `odoo-agile-scrum-devops` - Sprint planning, CI/CD, DORA metrics
- `superset-dashboard-automation` - Dashboard creation and metrics
- `superset-chart-builder` - Chart creation (10+ types)
- `superset-sql-developer` - SQL execution and query optimization

### Auto-Linking Mechanism
```bash
# Runs on SessionStart (configured in .claude/settings.json)
~/insightpulse-odoo/link_skills.sh

# Links all skills from docs/claude-code-skills/ to .claude/skills/
find docs/claude-code-skills -name "SKILL.md" -exec dirname {} \; | while read skill_dir; do
  skill_name=$(basename "$skill_dir")
  ln -sf "../../$skill_dir" ".claude/skills/$skill_name"
done
```

**Skills Storage**: `docs/claude-code-skills/` (central library)
**Skills Symlinks**: `.claude/skills/` (auto-linked on session start)

---

## 20) GitHub Workflow Integration

**CI Workflows** (`.github/workflows/`)

### assistant-context-freshness.yml
- **Purpose**: Ensure `claude.md` stays fresh (<7 days old)
- **Triggers**: Pull requests, push to main, daily at 03:00 UTC
- **Action**: Fail if `claude.md` last modified >7 days ago
- **Required Sections**: 0 (Normative Rules), 10 (Evals), 11 (Deployment Guardrails)

### skillsmith-integration.yml
- **Purpose**: Error-to-skill mining automation
- **Triggers**: Workflow dispatch, schedule (weekly)
- **Actions**: Run skill miner, approve skills, sync training data
- **Output**: New skill templates in `docs/claude-code-skills/`

### claude-autofix-bot.yml
- **Purpose**: Automated PR fixes using Claude Code
- **Model**: claude-sonnet-4-5-20250929 (read from claude.md section 22)
- **Triggers**: PR creation, issue labeled "autofix"
- **Permissions**: Read/write on contents, pull requests, issues

**Model Version Management**:
- Primary model defined in section 22 (this file)
- CI workflows read model from `claude.md` for consistency
- No hardcoded model versions in workflow files

---

## 21) Permissions Model

**118 Permission Grants** (`.claude/settings.local.json`)

### Bash Command Permissions
- **Git Operations**: add, pull, commit, push, merge, stash, checkout, fetch, log, rm, mv
- **GitHub CLI**: issue, pr, run, secret, workflow, release operations
- **DigitalOcean**: `doctl apps *`, `doctl projects *`, `doctl agent *`
- **Docker**: ps, exec, stop, rm, logs, run, pull, cp, inspect, compose, system
- **Database**: `psql *` with full connection strings for both Supabase projects
- **Python**: `python3 *`, `pip install *`, `pylint *`, `flake8 *`
- **File Operations**: find, tree, tar, cat, echo, chmod, mkdir, rm, mv, xargs, ls

### Secret Management (Allowed in Bash)
```bash
# Supabase (SpendFlow)
export POSTGRES_URL="postgres://postgres.spdtwktxdalcfigzeqrz:SHWYXDMFAwXI1drT@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

# GitHub
export GITHUB_TOKEN="github_pat_11AJXBTXY0..."

# DigitalOcean
export DIGITALOCEAN_ACCESS_TOKEN=dop_v1_...
```

### Read Permissions
- Full read access to `~/` and all subdirectories
- Temporary file read access: `/tmp/**`

### WebFetch Permissions
- `github.com`, `raw.githubusercontent.com`, `api.github.com`
- `aitmpl.com`

**Security Notes**:
- Secrets stored in environment variables, never in code
- Database passwords managed via `~/.zshrc` and macOS Keychain
- All tokens validated before use with prefix-only debugging

---

## 22) Interface Hierarchy

**Precedence Order** (highest to lowest):

1. **`/claude.md`** (this file) - Canonical assistant context
   - Odoo version targets (18 CE primary)
   - BIR compliance rules
   - Multi-tenancy definitions
   - Deployment guardrails
   - Evaluation requirements

2. **`/.claude/settings.json`** - Session hooks and automation
   - SessionStart hook for skill linking
   - MCP server auto-start configuration
   - Log level settings

3. **`/.claude/settings.local.json`** - Permissions model
   - 118 permission grants for Bash commands
   - Read/write file access patterns
   - Secret management patterns

4. **`/mcp/vscode-mcp-config.json`** - MCP server definitions
   - 7 server configurations
   - Tool registry (98 total tools)
   - Workflow orchestration patterns

5. **`/docs/SUPERCLAUDE_ARCHITECTURE.md`** - Agent architecture
   - 4 agent definitions
   - MCP integration patterns
   - Success metrics

**Conflict Resolution**:
- `claude.md` normative rules override all other configs
- MCP server settings in `vscode-mcp-config.json` override defaults
- Permissions in `settings.local.json` are additive (allow-list)

**Model Configuration**:
- **Primary Model**: `claude-sonnet-4-5-20250929` (Claude Sonnet 4.5)
- **Fallback Models**: `claude-opus-4-20250514` (Claude Opus 4)
- **Usage**: CI workflows read model version from this section
- **Context Window**: 200K tokens (budget management in ORCHESTRATOR.md)

---

## 23) Sync Automation

**Synchronization Scripts** (to be created in Phase 2)

### scripts/sync-claude-configs.sh
- **Purpose**: Synchronize `/claude.md` changes to all interface touchpoints
- **Triggers**: Manual execution, post-commit hook, CI workflow
- **Actions**:
  1. Validate `/claude.md` structure (sections 0-23 present)
  2. Extract model version (section 22) → update CI workflows
  3. Extract MCP servers (section 17) → validate against `mcp/vscode-mcp-config.json`
  4. Extract agent definitions (section 18) → validate against `~/.claude/superclaude/agents/`
  5. Extract skills inventory (section 19) → validate against `docs/claude-code-skills/`
  6. Generate drift report → commit if no conflicts

### scripts/validate-claude-config.py
- **Purpose**: Validate consistency across all Claude interface configurations
- **Actions**:
  1. Parse `/claude.md` sections 17-23
  2. Compare MCP servers with `vscode-mcp-config.json`
  3. Compare agent definitions with `~/.claude/superclaude/agents/`
  4. Compare skills with `docs/claude-code-skills/` inventory
  5. Compare model version with CI workflow files
  6. Report conflicts and suggest resolutions

### .github/workflows/claude-config-sync.yml
- **Purpose**: Automated config sync on push to main
- **Triggers**: Push to main, manual dispatch
- **Actions**:
  1. Run `scripts/validate-claude-config.py`
  2. Run `scripts/sync-claude-configs.sh`
  3. Create PR if drift detected
  4. Notify on Slack if conflicts require manual resolution

**Validation Frequency**:
- On commit: `scripts/validate-claude-config.py` (pre-commit hook)
- On push: GitHub Actions drift detection
- Daily: Scheduled sync audit at 02:00 UTC

**Skillsmith Integration**:
- Monitors `/claude.md` section 19 for skill inventory changes
- Auto-generates skill templates when new categories added
- Updates skill symlinks via `link_skills.sh` on SessionStart

---

### Footer

**Maintainer**: InsightPulse AI Team
**Assistant Targets**: Claude 4 (Sonnet/Opus), GPT-compatible agents
**Repo**: `https://github.com/jgtolentino/insightpulse-odoo`
**Version**: `assistant-context@2025-11-08` (**Odoo 18 CE only - consistent**)
**Last Sync**: 2025-11-08 (sections 17-23 added, Odoo 18 CE enforced)

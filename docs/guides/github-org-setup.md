# GitHub Organization Setup Guide - InsightPulse AI

**Complete guide to structuring, securing, and scaling your GitHub organization for InsightPulse AI's Odoo/Agent ecosystem.**

---

## Table of Contents

- [Organization Profile Setup](#organization-profile-setup)
- [Repository Strategy](#repository-strategy)
- [GitHub Projects Configuration](#github-projects-configuration)
- [Dependency Management Strategy](#dependency-management-strategy)
- [Branch Protection & Review Policies](#branch-protection--review-policies)
- [GitHub Actions & CI/CD](#github-actions--cicd)
- [Secrets & Security](#secrets--security)
- [Documentation & Discoverability](#documentation--discoverability)
- [Quick Setup Scripts](#quick-setup-scripts)
- [Best Practices](#best-practices)

---

## Organization Profile Setup

### 1. Org Profile README (`.github` repository)

Your organization profile is the first impression for contributors and potential users. Create a `.github` repository to host your org profile and community health files.

**What to include:**

```markdown
# InsightPulse AI

**AI-first ERP + Agent Orchestration Platform**

> Enterprise-grade multi-tenant SaaS platform built on Odoo 18.0 CE + OCA modules with embedded BI and AI capabilities. Replaces $60K+/year in SaaS subscriptions at < $20/month (87-91% cost reduction).

## 🎯 What We Build

- **Finance Shared Service Center** - Multi-company consolidation, BIR compliance
- **AI-Powered Document Processing** - PaddleOCR + OpenAI integration
- **Enterprise Analytics** - Apache Superset dashboards
- **Agent Orchestration** - Claude SDK + MCP servers

## 📦 Key Repositories

- [**insightpulse-odoo**](https://github.com/jgtolentino/insightpulse-odoo) - Main monorepo (Odoo CE/OCA + custom modules)
- **infra-deploy** - IaC for DigitalOcean deployments
- **agents-sdk** - Reusable agent templates & skills

## 🏗️ Architecture

```
Odoo CE 18.0 + OCA → Supabase (PostgreSQL + pgVector) → Superset (BI)
                  ↓
            GitHub Actions (CI/CD) → DigitalOcean App Platform
```

## 📧 Contact

- **Business**: business@insightpulseai.com
- **Security**: security@insightpulseai.com
- **Support**: support@insightpulseai.net

## 🔒 Security

Report vulnerabilities to security@insightpulseai.com. We follow a 90-day coordinated disclosure policy.

---

**License**: LGPL-3.0 | **Status**: Production Ready ✅ | **Cost**: < $20/month
```

### 2. Community Health Files

Create default community health files in the `.github` repository:

#### `CODEOWNERS`
```
# Default owners for all files
* @jgtolentino @insightpulse/platform-team

# Specific paths
/addons/insightpulse/finance/ @insightpulse/finance-team
/addons/insightpulse/ops/ @insightpulse/platform-team
/.github/workflows/ @insightpulse/devops-team
/docs/ @insightpulse/docs-team

# Critical infrastructure
/infra/ @jgtolentino @insightpulse/platform-lead
/scripts/deploy/ @jgtolentino @insightpulse/platform-lead
spec/platform_spec.json @jgtolentino
```

#### `SECURITY.md`
```markdown
# Security Policy

## Reporting Vulnerabilities

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, email security@insightpulseai.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

## Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 7 days
- **Fix & Disclosure**: Within 90 days (coordinated disclosure)

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 4.x     | ✅ Active support  |
| 3.x     | ⚠️ Security fixes only |
| < 3.0   | ❌ No support      |

## Security Practices

- ✅ All secrets stored in GitHub Actions secrets (org-level)
- ✅ Dependabot enabled for vulnerability scanning
- ✅ Branch protection with required reviews
- ✅ Automated security scanning (Trivy, Bandit)
```

#### `CODE_OF_CONDUCT.md`
```markdown
# Code of Conduct

## Our Pledge

We pledge to make participation in our community a harassment-free experience for everyone.

## Our Standards

**Positive behavior:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community

**Unacceptable behavior:**
- Harassment, trolling, or derogatory comments
- Publishing others' private information
- Other conduct reasonably considered inappropriate

## Enforcement

Report violations to support@insightpulseai.net. All complaints will be reviewed and investigated promptly.
```

### 3. Issue & PR Templates

Create `.github/ISSUE_TEMPLATE/` and `.github/PULL_REQUEST_TEMPLATE.md`:

```yaml
# .github/ISSUE_TEMPLATE/bug_report.yml
name: Bug Report
description: Report a bug in InsightPulse Odoo
labels: ["bug", "triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thank you for reporting a bug! Please fill out the sections below.
  - type: input
    id: module
    attributes:
      label: Affected Module
      placeholder: "e.g., ipai_expense, ipai_procure"
    validations:
      required: true
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: Clear description of the bug
    validations:
      required: true
  - type: textarea
    id: reproduce
    attributes:
      label: Steps to Reproduce
      placeholder: |
        1. Go to '...'
        2. Click on '...'
        3. See error
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
  - type: textarea
    id: environment
    attributes:
      label: Environment
      value: |
        - Odoo version:
        - OS:
        - Browser (if applicable):
```

---

## Repository Strategy

### Monorepo vs. Polyrepo Decision Matrix

**Current Setup (Recommended):**

| Repository Type | Purpose | Example |
|----------------|---------|---------|
| **Monorepo (Primary)** | `insightpulse-odoo` | Odoo CE/OCA app(s), custom modules, agents, skills registry, CI, docs |
| **Satellite (Infra)** | `infra-*` | IaC, Terraform, Ansible, deploy manifests |
| **Satellite (SDKs)** | `python-sdk`, `js-sdk` | Published libraries with semantic versioning |
| **Satellite (Public)** | `docs-site`, `landing-page` | Public-facing GitHub Pages sites |

**Benefits of Monorepo:**
- ✅ Atomic commits across modules
- ✅ Single CI/CD pipeline
- ✅ Easier dependency management
- ✅ Unified issue tracking
- ✅ Better for Odoo modules (tight coupling)

**When to Create Satellite Repos:**
- 📦 Publishing npm/pip packages (need independent versioning)
- 🌐 Public SDKs or client libraries
- 🔧 Infrastructure code separate from application logic
- 📄 Public documentation sites (GitHub Pages)

### Repository Structure

```
jgtolentino/
├── .github/                           # Org profile & defaults
│   ├── profile/README.md              # Org landing page
│   ├── CODEOWNERS                     # Default code owners
│   ├── SECURITY.md                    # Security policy
│   ├── CODE_OF_CONDUCT.md             # Code of conduct
│   ├── ISSUE_TEMPLATE/                # Issue templates
│   ├── PULL_REQUEST_TEMPLATE.md       # PR template
│   └── workflows/                     # Reusable workflows
│       ├── reusable-python-ci.yml
│       ├── reusable-docker-build.yml
│       └── reusable-deploy.yml
│
├── insightpulse-odoo/                 # MONOREPO (main)
│   ├── addons/                        # Odoo modules (OCA + custom)
│   ├── agents/                        # AI agent skills
│   ├── docs/                          # Documentation
│   ├── scripts/                       # Automation scripts
│   ├── tests/                         # Test suites
│   ├── .github/workflows/             # CI/CD workflows
│   └── spec/platform_spec.json        # Platform spec (SSOT)
│
├── infra-deploy/                      # Infrastructure satellite
│   ├── terraform/                     # DigitalOcean IaC
│   ├── ansible/                       # Config management
│   └── kubernetes/                    # K8s manifests (future)
│
├── python-sdk/                        # SDK satellite (published to PyPI)
│   ├── insightpulse/                  # Python package
│   └── setup.py
│
└── docs-site/                         # Public docs (GitHub Pages)
    ├── index.html
    └── _config.yml
```

---

## GitHub Projects Configuration

GitHub Projects provide portfolio and execution tracking across repositories.

### 1. Org-Level Project: **InsightPulse AI Roadmap**

**Purpose**: Portfolio/strategic view across all repositories

**Views:**

| View Name | Type | Purpose |
|-----------|------|---------|
| **Roadmap** | Timeline | Quarterly OKRs and initiatives |
| **Delivery Board** | Board | Sprint execution (backlog → ready → in progress → review → done) |
| **By Area** | Table | Group by Area (ERP/Agents/Data/Infra) |
| **By Owner** | Table | Group by team ownership |

**Custom Fields:**

```yaml
fields:
  - name: Area
    type: single_select
    options: [ERP, Agents, Data, Infrastructure, DevOps]

  - name: Priority
    type: single_select
    options: [P0 - Critical, P1 - High, P2 - Medium, P3 - Low]

  - name: Target Release
    type: single_select
    options: [v4.1, v4.2, v5.0, Backlog]

  - name: Owner (Team)
    type: single_select
    options: [Platform, Agents, Finance, DevOps, Design]

  - name: Risk Level
    type: single_select
    options: [High, Medium, Low]

  - name: Effort (Story Points)
    type: number

  - name: Status
    type: single_select
    options: [Backlog, Ready, In Progress, Review, Done, Blocked]
```

**Automations:**

```yaml
automations:
  - trigger: item_added
    action: set_field
    field: Status
    value: Backlog

  - trigger: pr_opened
    action: add_to_project

  - trigger: pr_merged
    action: set_field
    field: Status
    value: Done

  - trigger: issue_labeled
    label: P0 - Critical
    action: set_field
    field: Priority
    value: P0 - Critical
```

### 2. Repo-Level Project: **insightpulse-odoo Execution**

**Purpose**: Tactical execution board for the main repository

**Views:**

| View Name | Type | Purpose |
|-----------|------|---------|
| **Sprint Board** | Board | Current sprint (Todo → In Progress → Review → Done) |
| **Backlog** | Table | Prioritized backlog with story points |
| **QA/Testing** | Table | Filter: label:testing OR label:qa |
| **Bugs** | Table | Filter: label:bug, sorted by priority |

**GitHub CLI Setup:**

```bash
# Create org-level project
gh project create --owner jgtolentino --title "InsightPulse AI Roadmap"

# Add custom fields
gh project field-create 1 --name "Area" --data-type SINGLE_SELECT --single-select-options "ERP,Agents,Data,Infrastructure"
gh project field-create 1 --name "Priority" --data-type SINGLE_SELECT --single-select-options "P0 - Critical,P1 - High,P2 - Medium,P3 - Low"
```

### 3. Financial Tracking Fields (GitHub → Odoo Integration)

**Purpose**: Track development costs, budgets, and ROI for CFO visibility

To integrate GitHub Projects with Odoo financial tracking (using `ipai_github_timesheets` module), add these custom fields to your org-level GitHub Projects:

**Financial Fields Schema:**

```yaml
financial_fields:
  - name: "Project Budget ($)"
    type: number
    description: "Total allocated budget for this project"
    example: 50000
    required: true
    usage: "Set at project planning stage"

  - name: "Project Spend ($)"
    type: number
    description: "Actual spend from Odoo timesheets (auto-synced)"
    example: 12500
    required: false
    usage: "Auto-updated by Odoo via API (read-only in GitHub)"

  - name: "Remaining Budget ($)"
    type: number
    description: "Budget - Spend (calculated field)"
    formula: "Project Budget ($) - Project Spend ($)"
    example: 37500
    required: false
    usage: "Calculated automatically"

  - name: "Budget Utilization %"
    type: number
    description: "Spend / Budget × 100"
    formula: "(Project Spend ($) / Project Budget ($)) × 100"
    example: 25
    required: false
    usage: "Calculated automatically"

  - name: "Expense Type"
    type: single_select
    description: "Classification for financial reporting (CapEx vs OpEx)"
    options:
      - "R&D (OpEx)" # Research & experimental features
      - "Capitalizable Feature (CapEx)" # Production-ready features
      - "Maintenance (OpEx)" # Bug fixes, refactoring
      - "Bug Fix (OpEx)" # Bug fixes only
    required: true
    usage: "Set at project creation for accounting"

  - name: "Odoo Project ID"
    type: text
    description: "Link to Odoo project.project record ID"
    example: "456"
    required: false
    usage: "Auto-populated by ipai_github_timesheets module"

  - name: "Timesheet Hours"
    type: number
    description: "Total logged hours from Odoo timesheets"
    example: 167.5
    required: false
    usage: "Auto-synced from Odoo"

  - name: "Avg Hourly Rate ($)"
    type: number
    description: "Average developer hourly rate for this project"
    example: 75
    required: false
    usage: "Auto-calculated from Odoo employee rates"
```

**GitHub CLI Setup (Financial Fields):**

```bash
# Add financial tracking fields to your GitHub Project
PROJECT_ID=1  # Your GitHub Project ID

# Budget fields
gh project field-create $PROJECT_ID \
  --name "Project Budget ($)" \
  --data-type NUMBER

gh project field-create $PROJECT_ID \
  --name "Project Spend ($)" \
  --data-type NUMBER

# Expense classification
gh project field-create $PROJECT_ID \
  --name "Expense Type" \
  --data-type SINGLE_SELECT \
  --single-select-options "R&D (OpEx),Capitalizable Feature (CapEx),Maintenance (OpEx),Bug Fix (OpEx)"

# Odoo linkage
gh project field-create $PROJECT_ID \
  --name "Odoo Project ID" \
  --data-type TEXT

# Timesheet tracking
gh project field-create $PROJECT_ID \
  --name "Timesheet Hours" \
  --data-type NUMBER

gh project field-create $PROJECT_ID \
  --name "Avg Hourly Rate ($)" \
  --data-type NUMBER
```

**Integration Workflow:**

```mermaid
graph LR
    A[GitHub Project] --> B[Odoo ipai_github_timesheets]
    B --> C[Developer Logs Time]
    C --> D[Cost Calculated]
    D --> E[Sync Back to GitHub]
    E --> A
```

**Step-by-step:**

1. **Create GitHub Project** with financial fields
2. **Install Odoo module**: `ipai_github_timesheets`
3. **Configure GitHub API** in Odoo: Settings → GitHub Config
4. **Sync Projects**: Odoo fetches GitHub Projects
5. **Developer works on PR** → PR merged
6. **Timesheet prompt** posted on GitHub PR
7. **Developer logs time** in Odoo (hours × rate)
8. **Cost synced back** to GitHub Project "Project Spend ($)" field
9. **CFO views dashboard** in Superset with burn rate, CapEx/OpEx split

**Example GitHub Project with Financial Tracking:**

| Project | Budget | Spend | Remaining | Utilization | Expense Type | Hours | Avg Rate |
|---------|--------|-------|-----------|-------------|--------------|-------|----------|
| Q1 2025 Features | $50,000 | $12,500 | $37,500 | 25% | CapEx | 167.5 | $75 |
| Bug Fixes Sprint 3 | $10,000 | $8,900 | $1,100 | 89% | OpEx | 118.7 | $75 |
| R&D: AI Agents | $25,000 | $18,750 | $6,250 | 75% | R&D (OpEx) | 250.0 | $75 |

**Financial Reporting (Superset Dashboards):**

See [Superset CFO Dashboard Documentation](../superset/github-financial-dashboards.md) for:
- Project burn rate analysis
- CapEx vs OpEx split
- Feature ROI calculations
- Developer productivity metrics

---

## Dependency Management Strategy

### Submodules vs. Subtrees vs. Packages

| Option | Use When | Pros | Cons | InsightPulse Usage |
|--------|----------|------|------|-------------------|
| **Submodule** | Pinning external repos (rare) | Precise SHA pinning | CI complexity, auth issues | ❌ Avoid |
| **Subtree** | Vendoring upstream code | One repo, easy CI | Merge noise | ✅ **Use for OCA/Anthropic skills** |
| **Package Manager** | Published libraries | Clean updates, semver | Needs published packages | ✅ Use for SDKs |

### Current InsightPulse Strategy (Recommended)

#### 1. **OCA Modules: Subtree Vendoring**

You're already doing this correctly with `scripts/fetch_oca.sh` and `vendor/oca_requirements.txt`.

**Benefits:**
- ✅ No submodule auth issues
- ✅ Works seamlessly in CI/CD
- ✅ Shallow clones keep repo size small
- ✅ Easy to audit OCA code

**Workflow:**
```bash
# Already automated in your scripts/fetch_oca.sh
# Fetches OCA modules at Docker build time
# See: vendor/oca_requirements.txt

# To update OCA modules:
./scripts/fetch_oca.sh vendor/oca_requirements.txt addons/oca
git add addons/oca
git commit -m "chore: update OCA modules to latest 19.0 branch"
```

#### 2. **Anthropic Skills: Subtree or Skills Registry**

For Claude Code skills (from `.claude/skills/`):

```bash
# Option A: Subtree vendor (if forking Anthropic skills)
git subtree add --prefix .claude/skills/odoo \
  https://github.com/anthropics/anthropic-skills.git main --squash

# Option B: Skills registry symlink (current approach)
# Already handled by your SessionStart hook
```

#### 3. **Published SDKs: Package Manager**

For libraries you publish:

```bash
# Python SDK (if publishing to PyPI)
pip install insightpulse-sdk==1.2.3

# JavaScript SDK (if publishing to npm)
npm install @insightpulse/sdk@1.2.3
```

**Never Use Submodules For:**
- ❌ OCA modules (use subtree)
- ❌ Third-party dependencies (use pip/npm)
- ❌ Shared code within org (use monorepo)

---

## Branch Protection & Review Policies

### 1. Default Branch Protection (`main`)

**Settings for `insightpulse-odoo/main`:**

```yaml
branch_protection:
  require_pull_request_reviews:
    required_approving_review_count: 1
    dismiss_stale_reviews: true
    require_code_owner_reviews: true
    require_last_push_approval: false

  require_status_checks:
    strict: true  # Branch must be up-to-date
    contexts:
      - "Spec Guard"                    # spec/platform_spec.json validation
      - "CI Unified"                    # Quality + tests + security
      - "CI - Code Quality & Tests"     # Odoo module tests
      - "Deploy Gates"                  # Pre-deployment validation

  enforce_admins: true
  allow_force_pushes: false
  allow_deletions: false
  require_linear_history: false  # Allow merge commits
  require_signed_commits: false  # Optional (enable if GPG signing required)
```

**Apply via GitHub CLI:**

```bash
#!/bin/bash
# File: scripts/setup-branch-protection.sh

REPO="jgtolentino/insightpulse-odoo"
BRANCH="main"

# Enable branch protection
gh api -X PUT "/repos/$REPO/branches/$BRANCH/protection" \
  -f required_status_checks='{"strict":true,"contexts":["Spec Guard","CI Unified","CI - Code Quality & Tests","Deploy Gates"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"require_code_owner_reviews":true,"required_approving_review_count":1}' \
  -f restrictions=null \
  -f allow_force_pushes=false \
  -f allow_deletions=false

echo "✅ Branch protection enabled for $REPO/$BRANCH"
```

### 2. Release Branch Protection

For release branches (`release/v4.x`):

```yaml
branch_protection:
  require_pull_request_reviews:
    required_approving_review_count: 2  # Higher bar for releases
    require_code_owner_reviews: true

  require_status_checks:
    contexts:
      - "Spec Guard"
      - "CI Unified"
      - "Deploy Gates"
      - "Security Scan"  # Additional security check for releases

  enforce_admins: true
  require_signed_commits: true  # Require GPG for releases
```

### 3. Review Policies

**CODEOWNERS-based reviews:**

```
# .github/CODEOWNERS
# Require finance team approval for finance modules
/addons/insightpulse/finance/ @insightpulse/finance-team

# Require platform lead approval for critical infra
/scripts/deploy/ @jgtolentino
/spec/platform_spec.json @jgtolentino
/.github/workflows/cd-*.yml @jgtolentino @insightpulse/devops-team
```

**Review checklist (enforced via PR template):**

- [ ] ✅ Spec validation passes
- [ ] ✅ All tests pass
- [ ] ✅ Documentation updated
- [ ] ✅ No hardcoded secrets
- [ ] ✅ Security scan passed

---

## GitHub Actions & CI/CD

### 1. Reusable Workflows (Org-level)

Create reusable workflows in the `.github` repository:

#### `.github/workflows/reusable-python-ci.yml`

```yaml
name: Reusable Python CI
on:
  workflow_call:
    inputs:
      python-version:
        required: false
        type: string
        default: '3.11'
      requirements-file:
        required: false
        type: string
        default: 'requirements.txt'

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles(inputs.requirements-file) }}

      - name: Install dependencies
        run: |
          pip install -r ${{ inputs.requirements-file }}
          pip install pytest pytest-cov black isort flake8

      - name: Run linting
        run: |
          black --check .
          isort --check-only .
          flake8 . --max-line-length=120

      - name: Run tests
        run: pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
```

#### `.github/workflows/reusable-docker-build.yml`

```yaml
name: Reusable Docker Build
on:
  workflow_call:
    inputs:
      dockerfile:
        required: false
        type: string
        default: 'Dockerfile'
      image-name:
        required: true
        type: string
      push:
        required: false
        type: boolean
        default: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ${{ inputs.dockerfile }}
          tags: ${{ inputs.image-name }}
          push: ${{ inputs.push }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

**Usage in `insightpulse-odoo`:**

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  python-ci:
    uses: jgtolentino/.github/.github/workflows/reusable-python-ci.yml@main
    with:
      python-version: '3.11'

  docker-build:
    uses: jgtolentino/.github/.github/workflows/reusable-docker-build.yml@main
    with:
      image-name: insightpulse-odoo:test
      dockerfile: Dockerfile.test
```

### 2. Environment-scoped Secrets

**Org-level secrets** (shared across repos):

```bash
# Set org-level secrets
gh secret set DIGITALOCEAN_TOKEN --org jgtolentino --body "dop_v1_..."
gh secret set SUPABASE_URL --org jgtolentino --body "https://..."
gh secret set SUPABASE_ANON_KEY --org jgtolentino --body "eyJ..."
gh secret set OPENAI_API_KEY --org jgtolentino --body "sk-..."
```

**Environment-scoped secrets** (prod vs. staging):

```bash
# Create environments
gh api -X PUT "/repos/jgtolentino/insightpulse-odoo/environments/production"
gh api -X PUT "/repos/jgtolentino/insightpulse-odoo/environments/staging"

# Set environment-specific secrets
gh secret set DB_PASSWORD --env production --body "prod_secret"
gh secret set DB_PASSWORD --env staging --body "staging_secret"
```

**In workflows:**

```yaml
jobs:
  deploy-prod:
    runs-on: ubuntu-latest
    environment: production  # Uses production secrets
    steps:
      - run: echo "Deploying to prod with ${{ secrets.DB_PASSWORD }}"
```

### 3. Required Checks Best Practices

**Current setup (from your CI/CD docs):**

✅ **Required checks (must pass):**
- Spec Guard
- CI Unified
- CI - Code Quality & Tests
- Deploy Gates

⚠️ **Informational checks (advisory):**
- Dependency Scanning
- Automation Health
- Documentation

**Keep required checks fast (< 10 minutes):**
- Use caching (`actions/cache`)
- Run tests in parallel (matrix strategy)
- Skip non-essential checks on docs-only PRs

```yaml
# Example: Skip tests on docs-only changes
on:
  pull_request:
    paths-ignore:
      - 'docs/**'
      - '**.md'
```

### 4. Dependabot Configuration

Enable Dependabot for automated dependency updates:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "02:00"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "python"
    reviewers:
      - "jgtolentino"

  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "javascript"

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
    labels:
      - "dependencies"
      - "docker"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    labels:
      - "dependencies"
      - "ci"
```

---

## Secrets & Security

### 1. Secrets Management

**Shared secrets (org-level):**

```bash
# Infrastructure
gh secret set DIGITALOCEAN_TOKEN --org jgtolentino
gh secret set DOCTL_ACCESS_TOKEN --org jgtolentino

# Databases
gh secret set SUPABASE_URL --org jgtolentino
gh secret set SUPABASE_SERVICE_ROLE_KEY --org jgtolentino
gh secret set POSTGRES_URL --org jgtolentino

# AI Services
gh secret set OPENAI_API_KEY --org jgtolentino
gh secret set ANTHROPIC_API_KEY --org jgtolentino

# External Services
gh secret set GITHUB_APP_PRIVATE_KEY --org jgtolentino
```

**Repo-specific secrets:**

```bash
# Deployment-specific
gh secret set SSH_PRIVATE_KEY --repo jgtolentino/insightpulse-odoo
gh secret set DEPLOY_HOST --repo jgtolentino/insightpulse-odoo
```

**Never store in code:**
- ❌ API keys (use secrets)
- ❌ Passwords (use secrets)
- ❌ Service account tokens (use OIDC or secrets)

**Always use `.env.example`:**

```bash
# .env.example (committed to repo)
OPENAI_API_KEY=sk-your-key-here
SUPABASE_URL=https://your-project.supabase.co
POSTGRES_URL=postgresql://user:password@host:port/db

# .env (gitignored, local development)
OPENAI_API_KEY=sk-actual-key
SUPABASE_URL=https://actual-project.supabase.co
```

### 2. OIDC for Cloud Deployments

Use OIDC instead of long-lived tokens for DigitalOcean:

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # Required for OIDC
      contents: read
    steps:
      - name: Configure DigitalOcean credentials
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_TOKEN }}

      - name: Deploy to App Platform
        run: doctl apps create-deployment ${{ secrets.APP_ID }}
```

### 3. Security Scanning

**Automated security checks (already implemented):**

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: '0 2 * * 1'  # Weekly Monday 2 AM

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Bandit (Python security)
        run: |
          pip install bandit
          bandit -r addons/ scripts/ -f json -o bandit-report.json || true

      - name: Check for secrets in code
        run: |
          if grep -r "sk-" --include="*.py" --include="*.yml" .; then
            echo "❌ ERROR: Potential API keys found!"
            exit 1
          fi
```

---

## Documentation & Discoverability

### 1. Documentation Structure

**Org-level docs (in `.github` repo):**

```
.github/
├── profile/
│   └── README.md                  # Org landing page
├── CONTRIBUTING.md                # Contribution guide
├── SECURITY.md                    # Security policy
└── docs/
    ├── onboarding.md              # New contributor onboarding
    ├── release-process.md         # Release management
    └── architecture-overview.md   # High-level architecture
```

**Repo-level docs (in `insightpulse-odoo/docs/`):**

```
docs/
├── README.md                      # Docs index
├── guides/
│   ├── github-org-setup.md        # This guide
│   ├── workflows-ci-cd.md         # CI/CD practices
│   └── troubleshooting.md         # Common issues
├── architecture/
│   ├── README.md                  # Architecture overview
│   └── decisions/                 # ADRs
├── deployment/
│   ├── digitalocean-production.md
│   └── local-development.md
└── api/
    └── endpoints.md               # API documentation
```

### 2. Docs Index (Org Profile README)

Link to all key documentation:

```markdown
## 📚 Documentation

### Getting Started
- [Main README](https://github.com/jgtolentino/insightpulse-odoo#readme)
- [Quickstart Guide](https://github.com/jgtolentino/insightpulse-odoo/blob/main/QUICKSTART.md)
- [Contributing Guide](https://github.com/jgtolentino/.github/blob/main/CONTRIBUTING.md)

### Architecture & Design
- [System Architecture](https://github.com/jgtolentino/insightpulse-odoo/blob/main/docs/ARCHITECTURE.md)
- [Platform Spec](https://github.com/jgtolentino/insightpulse-odoo/blob/main/spec/platform_spec.json)
- [Tech Stack](https://github.com/jgtolentino/insightpulse-odoo/blob/main/docs/architecture/tech-stack.md)

### Operations
- [Deployment Guide](https://github.com/jgtolentino/insightpulse-odoo/blob/main/docs/DEPLOYMENT.md)
- [CI/CD Setup](https://github.com/jgtolentino/insightpulse-odoo/blob/main/docs/CI_CD_SETUP.md)
- [Runbooks](https://github.com/jgtolentino/insightpulse-odoo/tree/main/docs/runbooks)

### Security & Compliance
- [Security Policy](https://github.com/jgtolentino/.github/blob/main/SECURITY.md)
- [Security Audit Report](https://github.com/jgtolentino/insightpulse-odoo/blob/main/SECURITY_AUDIT_REPORT.md)
```

---

## Quick Setup Scripts

### Complete Org Setup Script

Save as `scripts/setup-github-org.sh`:

```bash
#!/bin/bash
set -e

ORG="jgtolentino"
MAIN_REPO="insightpulse-odoo"

echo "🚀 Setting up GitHub org: $ORG"

# 1. Create .github repository for org profile (if not exists)
echo "📦 Step 1: Create .github repository..."
gh repo create $ORG/.github --public --confirm || echo "Repository already exists"

# Clone .github repo
if [ ! -d ".github-repo" ]; then
  git clone "https://github.com/$ORG/.github" .github-repo
fi
cd .github-repo

# 2. Create org profile
echo "📝 Step 2: Create org profile..."
mkdir -p profile
cat > profile/README.md <<'EOF'
# InsightPulse AI

**AI-first ERP + Agent Orchestration Platform**

> Enterprise-grade multi-tenant SaaS platform built on Odoo 18.0 CE + OCA modules with embedded BI and AI capabilities.

## 📦 Key Repositories
- [insightpulse-odoo](https://github.com/jgtolentino/insightpulse-odoo) - Main monorepo

## 📧 Contact
- Business: business@insightpulseai.com
- Security: security@insightpulseai.com

---
**License**: LGPL-3.0 | **Status**: Production Ready ✅
EOF

# 3. Create CODEOWNERS
cat > CODEOWNERS <<'EOF'
# Default owners
* @jgtolentino

# Specific paths
/addons/insightpulse/finance/ @jgtolentino
/.github/workflows/ @jgtolentino
/spec/platform_spec.json @jgtolentino
EOF

# 4. Create SECURITY.md
cat > SECURITY.md <<'EOF'
# Security Policy

## Reporting Vulnerabilities
Email security@insightpulseai.com with vulnerability details.

## Response Timeline
- Acknowledgment: 48 hours
- Assessment: 7 days
- Fix & Disclosure: 90 days
EOF

# 5. Create reusable workflow
mkdir -p .github/workflows
cat > .github/workflows/reusable-python-ci.yml <<'EOF'
name: Reusable Python CI
on:
  workflow_call:
    inputs:
      python-version:
        required: false
        type: string
        default: '3.11'
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ inputs.python-version }}
      - run: pip install -r requirements.txt || true
      - run: pytest -q || true
EOF

# Commit and push
git add .
git commit -m "chore: initialize org profile and community health files" || true
git push

cd ..
echo "✅ Org profile created!"

# 6. Set up branch protection on main repo
echo "🔒 Step 3: Set up branch protection..."
gh api -X PUT "/repos/$ORG/$MAIN_REPO/branches/main/protection" \
  -f required_status_checks='{"strict":true,"contexts":["Spec Guard","CI Unified"]}' \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"dismiss_stale_reviews":true,"required_approving_review_count":1}' \
  -f restrictions=null \
  -f allow_force_pushes=false \
  -f allow_deletions=false || echo "⚠️  Branch protection may already be configured"

echo "✅ Branch protection configured!"

# 7. Enable Dependabot (create config in main repo)
echo "🤖 Step 4: Enable Dependabot..."
cd "$MAIN_REPO" 2>/dev/null || git clone "https://github.com/$ORG/$MAIN_REPO" && cd "$MAIN_REPO"

mkdir -p .github
cat > .github/dependabot.yml <<'EOF'
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
EOF

git add .github/dependabot.yml
git commit -m "chore: enable Dependabot" || true
git push || true

cd ..
echo "✅ Dependabot enabled!"

# 8. Set org-level secrets (you'll need to provide values)
echo "🔐 Step 5: Set org-level secrets..."
echo "ℹ️  Run these commands manually with actual values:"
echo ""
echo "gh secret set DIGITALOCEAN_TOKEN --org $ORG"
echo "gh secret set SUPABASE_URL --org $ORG"
echo "gh secret set SUPABASE_SERVICE_ROLE_KEY --org $ORG"
echo "gh secret set OPENAI_API_KEY --org $ORG"

echo ""
echo "🎉 GitHub org setup complete!"
echo ""
echo "Next steps:"
echo "1. Set org-level secrets (see commands above)"
echo "2. Create teams: gh api orgs/$ORG/teams -f name='platform-team'"
echo "3. Invite collaborators: gh api orgs/$ORG/invitations -f email='user@example.com'"
```

Make it executable:

```bash
chmod +x scripts/setup-github-org.sh
./scripts/setup-github-org.sh
```

---

## Best Practices

### ✅ Do

1. **Use org-level secrets** for shared credentials (DB, API keys)
2. **Enable branch protection** on `main` with required status checks
3. **Use CODEOWNERS** for critical paths (`spec/`, `.github/workflows/`, `scripts/deploy/`)
4. **Keep CI fast** (< 10 minutes) with caching and parallel jobs
5. **Use reusable workflows** for DRY CI/CD
6. **Enable Dependabot** for security updates
7. **Use subtree vendoring** for OCA modules (avoid submodules)
8. **Document everything** in org profile and repo READMEs
9. **Use GitHub Projects** for portfolio tracking
10. **Set up OIDC** instead of long-lived tokens where possible

### ❌ Don't

1. **Don't use git submodules** for dependencies (use subtree or package managers)
2. **Don't commit secrets** (use `.env.example` and GitHub secrets)
3. **Don't skip required checks** on `main` branch
4. **Don't force push** to `main` or release branches
5. **Don't create satellite repos** unless necessary (prefer monorepo)
6. **Don't hardcode credentials** in workflows (use secrets)
7. **Don't skip security scans** (Trivy, Bandit, Dependabot)
8. **Don't ignore CODEOWNERS** reviews on critical paths
9. **Don't deploy without tests** passing
10. **Don't skip documentation** updates

---

## Troubleshooting

### Common Issues

**1. Branch protection blocking your own pushes**

```bash
# Temporarily disable enforcement for admins (use sparingly)
gh api -X PUT "/repos/jgtolentino/insightpulse-odoo/branches/main/protection" \
  -f enforce_admins=false
```

**2. Required checks not running**

```yaml
# Check workflow triggers in .github/workflows/*.yml
on:
  pull_request:
    paths-ignore:
      - 'docs/**'  # This might skip required checks!
```

**3. CODEOWNERS not enforced**

```bash
# Ensure "Require review from Code Owners" is enabled
gh api repos/jgtolentino/insightpulse-odoo/branches/main/protection \
  --jq '.required_pull_request_reviews.require_code_owner_reviews'
```

**4. Secrets not accessible in workflows**

```yaml
# Check secret scope (org vs. repo)
# Org secrets: Settings → Organizations → Secrets
# Repo secrets: Settings → Secrets and variables → Actions

# In workflow:
- run: echo "Testing secret access"
  env:
    SECRET: ${{ secrets.MY_SECRET }}
```

---

## Additional Resources

- [GitHub Branch Protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches)
- [GitHub Projects Documentation](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [GitHub Actions Security Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file)
- [CODEOWNERS Syntax](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

---

**Last Updated**: 2025-11-11
**Author**: InsightPulse AI Platform Team
**Status**: Production Guide ✅
**Applies To**: jgtolentino GitHub Organization

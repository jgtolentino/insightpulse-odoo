# Odoo Agile Scrum DevOps Master Skill

A comprehensive Claude AI skill for managing Agile Scrum development workflows with Odoo ERP, specifically designed for Finance Shared Service Centers with multi-agency operations.

## 🎯 What This Skill Does

This skill teaches Claude how to:
- **Plan Sprints** following Agile Scrum methodology with Finance SSC context
- **Manage Odoo Development** using OCA (Odoo Community Association) standards
- **Automate DevOps** with CI/CD pipelines for DigitalOcean and Supabase
- **Handle BIR Compliance** (Philippine tax forms: 1601-C, 1702-RT, 2550Q)
- **Coordinate Multi-Agency** workflows across 8 affiliated agencies
- **Integrate with Notion** for task management via MCP tools

## 📁 Skill Structure

```
odoo-agile-scrum-devops/
├── SKILL.md                          # Main skill instructions
├── README.md                         # This file
├── sprint-planning-template.md       # Sprint planning guide
├── scripts/
│   ├── create_sprint.py             # Automate Odoo sprint creation
│   └── git_branch.sh                # OCA-compliant Git branching
└── resources/                        # Additional resources (add as needed)
```

## 🚀 Quick Start

### Installation

1. **For Claude.ai Users:**
   - Go to Settings → Skills
   - Click "Create Skill"
   - Upload this folder as a zip file
   - Enable the skill in your workspace

2. **For Claude Code Users:**
   ```bash
   # Copy skill to Claude Code skills directory
   cp -r odoo-agile-scrum-devops ~/.claude/skills/
   
   # The skill will auto-load when relevant
   ```

3. **For API Users:**
   - Use the Skills API endpoint
   - Upload skill via console or API
   - Include skill in agent configuration

### Usage Examples

**Example 1: Plan a Sprint**
```
Use the odoo-agile-scrum-devops skill to help me plan Sprint 12 
for November 1-15, 2025. We need to complete BIR Form 1601-C 
automation for all 8 agencies.
```

**Example 2: Create User Stories**
```
Create a user story for automating month-end bank reconciliation 
across all agencies. Format it according to the Finance SSC template 
in the skill.
```

**Example 3: Set Up CI/CD**
```
Help me set up GitHub Actions CI/CD pipeline for my odoboo-workspace 
project. Include OCA pre-commit hooks and DigitalOcean deployment.
```

**Example 4: Notion Integration**
```
Use the skill to help me sync Odoo sprint tasks to my Notion database. 
Use External ID pattern for deduplication.
```

## 🏢 Multi-Agency Context

This skill is designed for managing 8 affiliated agencies:
- **RIM** - Research Institute Manila
- **CKVC** - Centro Kingsford Ventures Corporation
- **BOM** - Bureau of Management
- **JPAL** - J-PAL Southeast Asia
- **JLI** - Justice Leadership Initiative
- **JAP** - Justice Action Program
- **LAS** - Legal Aid Society
- **RMQB** - Research Management Quality Bureau

Each agency has separate:
- TIN (Tax Identification Number)
- Bank accounts
- Financial reporting requirements
- Month-end closing schedules

## 🔧 Automation Scripts

### 1. Create Odoo Sprint

Automatically creates a sprint in Odoo Project module with Finance SSC tasks:

```bash
python scripts/create_sprint.py \
  --url http://localhost:8069 \
  --db odoo \
  --username admin \
  --password YOUR_PASSWORD \
  --sprint-number 12 \
  --start-date 2025-11-01 \
  --end-date 2025-11-15
```

**What it does:**
- Creates project "InsightPulse AI - Finance SSC"
- Creates sprint milestone
- Adds default Finance SSC tasks:
  - BIR Form 1601-C Automation (8 points)
  - Month-End Bank Reconciliation (13 points)
  - Multi-Agency Consolidation (5 points)
  - PaddleOCR Improvement (8 points)
  - CI/CD Optimization (5 points)

### 2. Create OCA-Compliant Git Branch

Automatically creates properly named feature branches:

```bash
# Make script executable
chmod +x scripts/git_branch.sh

# Create feature branch
./scripts/git_branch.sh \
  --version 19.0 \
  --type feature \
  --module finance_bir_compliance

# Create bug fix branch with issue number
./scripts/git_branch.sh \
  -v 18.0 \
  -t fix \
  -m expense_ocr \
  -i 123
```

**Branch naming convention:**
- Format: `{version}-{type}-{module_name}[-{issue}]`
- Examples:
  - `19.0-feature-finance_bir_compliance`
  - `18.0-fix-expense_ocr-123`
  - `19.0-refactor-multi_agency`

## 📋 Sprint Planning Workflow

### 1. Sprint Planning Meeting (2 hours)

**Agenda:**
1. Review product backlog (30 min)
2. Define sprint goal (15 min)
3. Estimate user stories (45 min)
4. Commit to sprint backlog (30 min)

**Estimation:**
- Use Fibonacci sequence: 1, 2, 3, 5, 8, 13, 21
- Planning poker for team consensus
- Story points = effort + complexity + risk

### 2. Daily Standup (15 min, async via Notion)

Each team member updates:
- **Yesterday:** What did I complete?
- **Today:** What will I work on?
- **Blockers:** Any impediments?

### 3. Sprint Review (1.5 hours)

- Demo completed features
- Stakeholder feedback
- Update product backlog

### 4. Sprint Retrospective (1 hour)

- What went well?
- What needs improvement?
- Action items for next sprint

## 🔄 CI/CD Pipeline

The skill includes GitHub Actions workflow for:

### Pipeline Stages

1. **Lint** (3-5 min)
   - pre-commit hooks
   - pylint-odoo
   - flake8, black, isort

2. **Test** (5-8 min)
   - Unit tests (pytest)
   - Integration tests (Odoo test framework)
   - Code coverage report

3. **Security Scan** (2-3 min)
   - Trivy vulnerability scanner
   - SARIF upload to GitHub Security

4. **Build & Push** (5-7 min)
   - Docker image build
   - Push to DigitalOcean Container Registry

5. **Deploy Staging** (3-5 min)
   - Deploy to staging.insightpulseai.net
   - Run database migrations
   - Smoke tests

6. **Deploy Production** (3-5 min)
   - Database backup
   - Deploy to insightpulseai.net
   - Create Sentry release

**Total Time:** < 15 minutes from commit to production

### Required Secrets

```bash
# GitHub Secrets to configure
DO_API_TOKEN            # DigitalOcean API token
DO_REGISTRY_TOKEN       # DigitalOcean Container Registry
DO_PROJECT_ID           # 29cde7a1-8280-46ad-9fdf-dea7b21a7825
DO_STAGING_APP_ID       # Staging app ID
DO_PROD_APP_ID          # Production app ID
DO_DATABASE_ID          # Managed PostgreSQL database ID
SENTRY_AUTH_TOKEN       # Sentry authentication token
SENTRY_ORG              # Sentry organization slug
```

## 🔗 Notion Integration

### Using MCP Tools

The skill provides patterns for Notion integration:

```python
# Example: Create sprint tasks in Notion

# 1. Fetch database structure
notion-fetch database_id="your-sprint-db-id"

# 2. Create tasks with External ID
notion-create-pages {
  "parent": {"data_source_id": "collection-id"},
  "pages": [{
    "properties": {
      "Task Name": "BIR Form 1601-C Generator",
      "Sprint": "Sprint 12 - Nov 2025",
      "Status": "In Progress",
      "Story Points": 8,
      "Agency": "All Agencies",
      "date:Due Date:start": "2025-11-15",
      "External ID": "ODOO-TASK-1234"
    }
  }]
}

# 3. Upsert pattern for updates
# Check External ID, update if exists, create if not
```

## 📊 DORA Metrics

Track DevOps performance:

| Metric | Target | Description |
|--------|--------|-------------|
| **Deployment Frequency** | Daily | How often code reaches production |
| **Lead Time for Changes** | < 1 day | Commit to production time |
| **Mean Time to Recovery** | < 1 hour | Incident to resolution time |
| **Change Failure Rate** | < 5% | % of deployments causing failures |

Monitor via Superset dashboard or Grafana.

## 🧪 Testing Standards

### Test Coverage Requirements

- **Unit Tests:** >= 80% coverage
- **Integration Tests:** All critical paths
- **End-to-End Tests:** Key user workflows

### Running Tests Locally

```bash
# Run all tests
docker-compose run --rm odoo odoo \
  -d test_db \
  -i module_name \
  --test-enable \
  --stop-after-init

# Run specific test file
pytest tests/test_bir_forms.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

## 📝 Commit Message Convention

Follow OCA standards:

```bash
[TAG] module_name: Brief description

# Tags:
[ADD]   # New features
[FIX]   # Bug fixes
[REF]   # Refactoring
[REM]   # Removed features
[I18N]  # Translations
[DOC]   # Documentation

# Examples:
[ADD] finance_bir_compliance: BIR Form 1601-C XML generator
[FIX] expense_ocr: Handle rotated receipt images
[REF] multi_agency: Optimize database queries
[I18N] finance_bir: Add Filipino translations
```

## 🏗️ Project Structure

### odoboo-workspace Architecture

```
odoboo-workspace/
├── addons/                    # OCA and custom modules
│   ├── finance_bir_compliance/
│   ├── expense_management_ocr/
│   └── multi_agency_reports/
├── docker-compose.yml         # Local development
├── Dockerfile                 # Production image
├── .github/
│   └── workflows/
│       └── odoo-ci-cd.yml    # CI/CD pipeline
├── .pre-commit-config.yaml   # Code quality hooks
├── odoo.conf                  # Odoo configuration
└── requirements.txt           # Python dependencies
```

## 🌐 Infrastructure

### DigitalOcean Setup

- **Project ID:** 29cde7a1-8280-46ad-9fdf-dea7b21a7825
- **App Platform:** Odoo 19 deployment
- **Database:** Managed PostgreSQL 15
- **Storage:** Spaces (S3-compatible) for attachments
- **Registry:** Private container registry

### Supabase Setup

- **Project:** spdtwktxdalcfigzeqrz
- **Database:** PostgreSQL with pgvector extension
- **Use Cases:**
  - Receipt embeddings for deduplication
  - Real-time task updates
  - Semantic search across documents

## 📚 Resources

### Documentation
- [Odoo 19 Docs](https://www.odoo.com/documentation/19.0/)
- [OCA Guidelines](https://github.com/OCA/odoo-community.org)
- [Scrum Guide](https://scrumguides.org/)
- [DORA Metrics](https://dora.dev/)

### Tools
- [Notion API](https://developers.notion.com/)
- [Supabase Docs](https://supabase.com/docs)
- [DigitalOcean API](https://docs.digitalocean.com/reference/api/)
- [Sentry Python SDK](https://docs.sentry.io/platforms/python/)

## 🤝 Contributing

To improve this skill:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/improvement`
3. Make your changes
4. Submit pull request

## 📄 License

MIT License - feel free to adapt for your organization.

## 🆘 Support

For questions or issues:
- Check the SKILL.md for detailed instructions
- Review sprint-planning-template.md for examples
- Consult OCA documentation for Odoo standards

---

**Created by:** Jake Tolentino  
**Version:** 1.0.0  
**Last Updated:** November 1, 2025

**Designed for:**
- InsightPulse AI (insightpulseai.net)
- odoboo-workspace (Odoo 18/19)
- Finance Shared Service Center operations
- Multi-agency management (8 agencies)
- Philippine BIR tax compliance

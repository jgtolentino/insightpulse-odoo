# DeepWiki Knowledge Management Strategy

## Our Custom Repository

**Primary Repository:** `github.com/jgtolentino/insightpulse-odoo`

### Custom Modules Inventory

**Finance SSC Modules:**
- `ipai_ppm` - Project Portfolio Management
- `ipai_rate_policy` - Billing rate policies
- `ipai_statement_engine` - Financial statements
- `ipai_concur_bridge` - SAP Concur integration
- `ipai_ariba_cxml` - Ariba cXML procurement

**Operations Modules:**
- `ipai_saas_ops` - SaaS operations management
- `github_integration` - GitHub webhook integration
- `odoo_knowledge_agent` - AI knowledge extraction

**AI/Document Processing:**
- `ipai_doc_ai` - Document intelligence
- `ipai_visual_gate` - Visual document processing
- `ipai_consent_manager` - GDPR compliance

**Enterprise Integrations:**
- `ipai_salesforce_sync` - Salesforce synchronization
- `ipai_clarity_ppm_sync` - Clarity PPM integration
- `pulser_hub_sync` - Pulse Hub synchronization
- `pulser_webhook` - Webhook management

**Infrastructure:**
- `mcp-server` - Model Context Protocol server
- `pulse-hub-api` - Pulse Hub REST API
- `insightpulse-monitor` - Monitoring service

---

## DeepWiki Indexing Priority

### 🔴 URGENT - Index First (This Week)

**Core Odoo (Our Foundation):**
```
deepwiki.com/odoo/odoo (branch: 19.0)
```
**Why:** Every custom module depends on core Odoo API. Critical for understanding base classes, ORM, and framework.

**Priority Actions:**
1. Read: deepwiki.com/odoo/odoo for ORM reference
2. Read: deepwiki.com/odoo/odoo for model inheritance patterns
3. Read: deepwiki.com/odoo/odoo for QWeb templating

**OCA Finance Tools (Finance SSC Core):**
```
deepwiki.com/OCA/account-financial-tools
deepwiki.com/OCA/account-invoicing
deepwiki.com/OCA/account-closing
```
**Why:** Building Finance SSC modules. Need patterns for financial reports, invoice workflows, month-end closing.

**Priority Actions:**
1. Check existing modules before building custom
2. Learn OCA financial report patterns
3. Understand closing workflow automation

**Philippine Localization (BIR Compliance):**
```
deepwiki.com/OCA/l10n-philippines
```
**Why:** BIR tax compliance is legal requirement for Philippines operations.

**Priority Actions:**
1. Check BIR form implementations (1601-C, 2550Q, 1702-RT)
2. Learn Philippine chart of accounts structure
3. Understand withholding tax calculations

### 🟡 HIGH PRIORITY - Index Next (This Month)

**OCA Server Tools (Backend Utilities):**
```
deepwiki.com/OCA/server-tools
```
**Why:** Contains utilities for scheduled actions, server actions, database queries used across all modules.

**Use Cases:**
- Base technical user patterns
- Sentry error tracking integration
- Database cleanup utilities
- Scheduled action helpers

**OCA Web (Frontend Enhancements):**
```
deepwiki.com/OCA/web
```
**Why:** Custom UI widgets, JS framework enhancements, dashboard components.

**Use Cases:**
- Custom dashboard widgets
- Advanced search filters
- List view enhancements
- Form view customizations

**OCA Reporting Engine:**
```
deepwiki.com/OCA/reporting-engine
```
**Why:** Generate financial reports, export to Excel/PDF, MIS Builder for management reports.

**Use Cases:**
- Financial statement generation
- Excel export templates
- Management dashboards
- KPI reporting

**OCA Bank Payment:**
```
deepwiki.com/OCA/bank-payment
```
**Why:** Bank reconciliation, payment processing, SEPA integration.

**Use Cases:**
- Bank statement import
- Payment batch processing
- Reconciliation automation

### 🟢 MEDIUM PRIORITY - Index When Needed (Next Quarter)

**Document Processing (AI Stack):**
```
deepwiki.com/PaddlePaddle/PaddleOCR
deepwiki.com/PaddlePaddle/PaddleNLP
```
**Why:** OCR for receipts/invoices, NLP for document understanding.

**Use Cases:**
- Receipt scanning (`ipai_doc_ai`)
- BIR form extraction
- Invoice data extraction
- Document classification

**Supabase Stack (Database & Storage):**
```
deepwiki.com/supabase/supabase
deepwiki.com/pgvector/pgvector
```
**Why:** Vector search for semantic document retrieval, database backend.

**Use Cases:**
- Document similarity search
- Semantic invoice matching
- Knowledge base RAG
- Embeddings storage

**Docker Deployment:**
```
deepwiki.com/Tecnativa/docker-odoo-base
deepwiki.com/camptocamp/docker-odoo
```
**Why:** Production-ready Docker configurations, multi-worker setup.

**Use Cases:**
- DigitalOcean deployment
- Worker configuration
- Performance tuning
- Production best practices

### 🔵 LOW PRIORITY - Reference Only (As Needed)

**AI SDK (When Building AI Features):**
```
deepwiki.com/anthropics/anthropic-sdk-python
```

**OCA Development Tools:**
```
deepwiki.com/OCA/maintainer-tools
deepwiki.com/OCA/pylint-odoo
```

**Frontend Framework (If Using):**
```
deepwiki.com/vercel/next.js
```

---

## DeepWiki Usage Patterns

### Pattern 1: Before Building a Module

**Workflow:**
```bash
# 1. Check OCA for existing module
Visit: deepwiki.com/OCA/[category]

# 2. Search for similar implementations
Search: "expense approval workflow"

# 3. Read relevant module code
Read: deepwiki.com/OCA/hr-expense/hr_expense_advance_clearing

# 4. Extract patterns
- Model structure
- View layouts
- Business logic
- Security rules
```

**Example: Building Travel Expense Module**
```
1. Check deepwiki.com/OCA/hr-expense
2. Find: hr_expense_advance_clearing
3. Learn: Advance payment workflow
4. Extend: Add OCR capability (custom)
5. Result: 80% OCA + 20% custom = 2 weeks instead of 3 months
```

### Pattern 2: Debugging Issues

**Workflow:**
```bash
# 1. Identify error in Odoo logs
Error: "ValidationError: Invalid field 'partner_id' on model 'account.move'"

# 2. Search DeepWiki
Visit: deepwiki.com/odoo/odoo
Search: "account.move partner_id validation"

# 3. Read source code
Understand: Field definition, constraints, compute methods

# 4. Fix in custom module
Override: Add missing field or fix constraint
```

### Pattern 3: Learning New Odoo API

**Workflow:**
```bash
# Need: Understand how to create scheduled actions programmatically

# 1. Visit DeepWiki
Visit: deepwiki.com/odoo/odoo
Search: "ir.cron create scheduled action"

# 2. Find examples
Read: addons/base/models/ir_cron.py

# 3. Check OCA patterns
Visit: deepwiki.com/OCA/server-tools
Search: "scheduled action"

# 4. Implement in custom module
Apply: Pattern learned from DeepWiki
```

### Pattern 4: Migration Research

**Workflow:**
```bash
# Need: Migrate module from Odoo 16.0 to 19.0

# 1. Check migration guide
Visit: deepwiki.com/odoo/odoo
Search: "migration 16.0 19.0 breaking changes"

# 2. Check OCA migrator
Visit: deepwiki.com/OCA/odoo-module-migrator
Read: Migration scripts for 16.0 → 19.0

# 3. Run migrator
odoo-module-migrate --init-version 16.0 --target-version 19.0

# 4. Fix manual issues
Use DeepWiki to understand new API requirements
```

---

## Internal Documentation Strategy

### Using Librarian-Indexer Skill

**For Private Repos (Can't Use DeepWiki):**

Our `insightpulse-odoo` repo contains proprietary code. Use **librarian-indexer** skill to create internal documentation.

**Setup Workflow:**
```bash
# 1. Invoke librarian-indexer skill
Use skill: librarian-indexer

# 2. Index custom modules
Target: /home/user/insightpulse-odoo/odoo_addons/
Target: /home/user/insightpulse-odoo/addons/insightpulse/

# 3. Generate documentation
Output: docs/internal/
- API reference
- Module dependencies
- Database schema
- Integration points

# 4. Create searchable index
Tool: grep-friendly markdown
Storage: Git repo (version controlled)
```

**What to Document Internally:**

**1. Custom Module APIs**
```markdown
# ipai_doc_ai API Reference

## Models

### `ipai.document`
- Fields: name, content, ocr_result, confidence
- Methods: extract_text(), classify_document()
- Security: document.manager group required

## Usage Examples

### Extract Text from Image
```python
doc = env['ipai.document'].create({
    'name': 'Receipt',
    'content': base64_image
})
doc.extract_text()  # Returns OCR result
```
```

**2. Integration Patterns**
```markdown
# Salesforce Sync Integration

## Architecture
Odoo → Webhook → Pulse Hub API → Salesforce

## Configuration
- Webhook URL: /api/v1/salesforce/sync
- Auth: API key in header
- Frequency: Real-time on record change

## Data Mapping
Odoo Partner → Salesforce Account
- name → Name
- email → Email
- phone → Phone
```

**3. Deployment Procedures**
```markdown
# DigitalOcean Deployment

## Prerequisites
- DigitalOcean API token
- Supabase connection string
- SSL certificate (Let's Encrypt)

## Steps
1. Provision droplet (4GB RAM)
2. Install Docker + Docker Compose
3. Copy deployment files
4. Configure .env
5. Run: docker-compose up -d
6. Initialize database
7. Install modules
8. Configure Nginx
9. Setup SSL with certbot
```

**4. Database Schema**
```markdown
# ipai_ppm Database Schema

## Tables

### `ipai_ppm_project`
- id (INTEGER, PK)
- name (VARCHAR)
- budget (NUMERIC)
- start_date (DATE)
- end_date (DATE)
- status (VARCHAR) - draft, active, closed

### `ipai_ppm_timesheet`
- id (INTEGER, PK)
- project_id (INTEGER, FK → ipai_ppm_project)
- user_id (INTEGER, FK → res_users)
- hours (NUMERIC)
- date (DATE)
```

---

## Knowledge Management Workflow

### Daily Development Flow

**Morning (Research Phase):**
```bash
# 1. Check DeepWiki for relevant modules
Visit: deepwiki.com/OCA/[category]

# 2. Review internal docs
Read: docs/internal/[module]/README.md

# 3. Plan implementation
Create: Feature branch with clear requirements
```

**During Development:**
```bash
# 1. Reference DeepWiki for API usage
Example: How to create Many2one field?
Search: deepwiki.com/odoo/odoo "Many2one field definition"

# 2. Check OCA patterns
Example: How do other modules handle approvals?
Search: deepwiki.com/OCA/server-tools "approval workflow"

# 3. Document as you build
Update: docs/internal/[module]/IMPLEMENTATION.md
```

**Evening (Documentation):**
```bash
# 1. Update internal docs with learnings
Add: Common issues encountered
Add: Solutions discovered
Add: API patterns used

# 2. Commit documentation with code
git add docs/ odoo_addons/
git commit -m "feat: add expense OCR + documentation"
```

### Weekly Review

**Every Friday:**
```bash
# 1. Review week's DeepWiki usage
Questions answered?
Patterns learned?
Time saved vs manual search?

# 2. Update internal wiki
New modules documented?
Integration guides updated?
Deployment procedures current?

# 3. Share learnings with team
Team meeting: Show DeepWiki workflow
Demo: How to use librarian-indexer
Discussion: Knowledge gaps to fill
```

---

## Priority Actions This Week

### Monday
```bash
✅ Index core Odoo in DeepWiki workflow
✅ Bookmark: deepwiki.com/odoo/odoo

Example queries:
- "How to create computed field?"
- "Many2one vs One2many relationship?"
- "QWeb report template syntax?"
```

### Tuesday
```bash
✅ Index OCA finance tools
✅ Bookmark: deepwiki.com/OCA/account-financial-tools

Research:
- Financial report patterns
- Invoice workflow automation
- Month-end closing procedures
```

### Wednesday
```bash
✅ Check Philippine localization
✅ Bookmark: deepwiki.com/OCA/l10n-philippines

Learn:
- BIR form implementations
- Withholding tax calculations
- Chart of accounts structure
```

### Thursday
```bash
✅ Use librarian-indexer for internal docs
✅ Generate API reference for custom modules

Document:
- ipai_doc_ai module
- ipai_ppm module
- Integration patterns
```

### Friday
```bash
✅ Review and consolidate learnings
✅ Update team wiki
✅ Plan next week's research topics
```

---

## Measuring Success

### Metrics to Track

**Development Speed:**
- Time to find relevant code: Before vs After DeepWiki
- Time to understand API: Manual docs vs DeepWiki search
- Time to implement feature: From scratch vs OCA pattern

**Code Quality:**
- Following OCA standards: % of modules compliant
- Reusing existing code: % OCA vs custom
- Documentation coverage: % modules documented

**Knowledge Retention:**
- Team members using DeepWiki: Count
- Internal docs accessed: Page views
- Questions answered without senior dev: Count

**Example Targets:**
```
Month 1:
- 50% of lookups use DeepWiki
- 10 custom modules documented internally
- 2 hours/week saved per developer

Month 3:
- 80% of lookups use DeepWiki
- All modules documented
- 5 hours/week saved per developer

Month 6:
- 95% of lookups use DeepWiki
- Auto-generated API docs
- 10 hours/week saved per developer
- 30% less time asking senior devs
```

---

## Resources

### DeepWiki Bookmarks
```
Core:
- deepwiki.com/odoo/odoo
- deepwiki.com/OCA/account-financial-tools
- deepwiki.com/OCA/server-tools

AI Stack:
- deepwiki.com/PaddlePaddle/PaddleOCR
- deepwiki.com/supabase/supabase

DevOps:
- deepwiki.com/Tecnativa/docker-odoo-base
```

### Internal Documentation
```
Location: /home/user/insightpulse-odoo/docs/internal/

Structure:
- modules/      # Per-module API docs
- integrations/ # Integration guides
- deployment/   # Deployment procedures
- schema/       # Database schemas
- workflows/    # Business workflows
```

### Skills to Use
```
- librarian-indexer: Generate internal docs
- odoo-devops-professional: OCA workflows
- oca-github-bot: Automated PR management
- odoo-studio: No-code customizations
```

---

**Next Action:** Which module are you building next? Let's start with the right DeepWiki research! 🚀

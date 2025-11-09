# 🛠️ InsightPulse Developer Tools

Custom-built tools for accelerating InsightPulse Odoo development. Better than generic tools because they understand Odoo patterns, BIR compliance, and Finance SSC workflows.

## 📚 Odoo Documentation Generator

Auto-generate comprehensive API documentation from your Odoo modules.

### Features

- **Module Inventory** - All modules with dependencies, versions, and categories
- **Model Schemas** - Complete field definitions with types, constraints
- **Method Discovery** - Extract compute methods, API decorators, onchange handlers
- **BIR/Finance Detection** - Automatically categorize compliance modules
- **Multiple Formats** - Markdown, HTML, JSON

### Usage

```bash
# Generate all formats
python scripts/generate_odoo_docs.py

# Generate specific format
python scripts/generate_odoo_docs.py --format html
python scripts/generate_odoo_docs.py --format markdown
python scripts/generate_odoo_docs.py --format json

# Custom output path
python scripts/generate_odoo_docs.py --output custom/path/docs.md
```

### Output

- `docs/GENERATED_ODOO_DOCS.md` - Markdown documentation
- `docs/GENERATED_ODOO_DOCS.html` - Interactive HTML with stats
- `docs/GENERATED_ODOO_DOCS.json` - Machine-readable API spec

### Automatic Generation

Docs are auto-generated on every push to `main` via GitHub Actions:

```yaml
# .github/workflows/generate-docs.yml
on:
  push:
    branches: [main]
    paths:
      - 'custom-addons/**'
      - 'workflows/**'
```

View live docs at: https://docs.insightpulseai.net/GENERATED_ODOO_DOCS.html

---

## 🔍 InsightPulse Code Search

AI-powered semantic code search using Claude + pgvector.

### Features

- **Semantic Search** - Natural language queries ("How to generate BIR 1601-C?")
- **Ask Claude** - Get explanations with relevant code context
- **Odoo-Aware** - Understands models, fields, compute methods, workflows
- **BIR/Finance Context** - Knows about month-end closing, tax forms, compliance
- **Interactive Mode** - REPL for exploring codebase

### Setup

1. **Install PostgreSQL with pgvector**:
```bash
# Add to Supabase or local Postgres
CREATE EXTENSION vector;
```

2. **Set environment variables**:
```bash
export POSTGRES_URL="postgresql://user:pass@host:5432/db?sslmode=require"
export ANTHROPIC_API_KEY="sk-ant-..."
```

3. **Index codebase** (run once):
```bash
python scripts/insightpulse_code_search.py --index
```

### Usage

**Search for code**:
```bash
python scripts/insightpulse_code_search.py --search "BIR form generation"
python scripts/insightpulse_code_search.py --search "month-end closing workflow"
python scripts/insightpulse_code_search.py --search "compute tax withholding"
```

**Ask Claude**:
```bash
python scripts/insightpulse_code_search.py --ask "How does month-end closing work?"
python scripts/insightpulse_code_search.py --ask "Where are BIR 1601-C forms generated?"
python scripts/insightpulse_code_search.py --ask "How do I add a new company?"
```

**Interactive mode**:
```bash
python scripts/insightpulse_code_search.py --interactive

📝 > search BIR automation
📝 > ask How are Notion tasks synced?
📝 > quit
```

### Example Queries

```bash
# Find specific implementations
--search "Odoo RPC connection"
--search "Notion database upsert"
--search "Multi-company data isolation"

# Ask conceptual questions
--ask "How does the BIR Notion sync work?"
--ask "What's the difference between manager_code and company_code?"
--ask "How are month-end tasks generated?"

# Find by metadata
--search "compute methods for tax calculation"
--search "API decorators for expense approval"
--search "workflows with BIR compliance"
```

### How It Works

1. **Chunking** - Extracts functions, classes, workflows from code
2. **Embedding** - Generates semantic embeddings (currently using hash, upgrade to OpenAI/Claude embeddings)
3. **Indexing** - Stores in pgvector with metadata (file, type, name, line numbers)
4. **Search** - Cosine similarity search across embeddings
5. **Claude Integration** - Fetches top results, asks Claude for explanation

### Database Schema

```sql
CREATE TABLE insightpulse_code_embeddings (
    id SERIAL PRIMARY KEY,
    chunk_hash TEXT UNIQUE NOT NULL,
    file_path TEXT NOT NULL,
    chunk_type TEXT NOT NULL,  -- function, class, workflow, model
    name TEXT NOT NULL,
    code TEXT NOT NULL,
    line_start INTEGER,
    line_end INTEGER,
    metadata JSONB,            -- is_model, is_api, is_compute, etc.
    embedding vector(1024),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ON insightpulse_code_embeddings
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
```

---

## 🆚 Why Build Custom Tools?

### vs GitToDoc / GitSearchAI

| Feature | Generic Tools | InsightPulse Tools |
|---------|---------------|-------------------|
| **Odoo Understanding** | ❌ Generic AST parsing | ✅ Odoo models, fields, methods |
| **BIR Compliance** | ❌ No domain knowledge | ✅ Tax forms, compliance workflows |
| **Finance SSC** | ❌ Generic business logic | ✅ Month-end, multi-company, agencies |
| **Workflow Support** | ❌ JSON files only | ✅ Workflow steps, BIR triggers |
| **Integration** | ❌ Standalone | ✅ Supabase, Claude, Odoo RPC |
| **Cost** | 💰 SaaS pricing | ✅ Self-hosted, $0 |

### Examples of Odoo-Specific Features

**Generic tool**:
```python
# Just sees a class
class BIRForm(models.Model):
    name = fields.Char()
```

**InsightPulse tool**:
```python
# Understands:
- This is an Odoo model (models.Model)
- _name = 'insightpulse.bir.form'
- It's a BIR compliance module
- Has Many2one to res.company (multi-company)
- Uses compute methods for tax calculation
- Related to workflows/bir-filing-1601c.json
```

---

## 🚀 Integration Examples

### 1. Auto-Update OCA Modules

```bash
# scripts/oca_auto_update.sh
#!/bin/bash

# Search for OCA module usage
python scripts/insightpulse_code_search.py --search "OCA modules" --limit 20 > /tmp/oca_usage.txt

# Check for updates
python scripts/vendor_oca.py --check-updates

# Generate PR with updated docs
python scripts/generate_odoo_docs.py --format all
git add docs/
git commit -m "docs: Update after OCA sync"
```

### 2. Pre-Commit Hook for Docs

```bash
# .git/hooks/pre-commit
#!/bin/bash

# Check if custom-addons changed
if git diff --cached --name-only | grep -q "custom-addons/"; then
    echo "Regenerating Odoo docs..."
    python scripts/generate_odoo_docs.py --format markdown
    git add docs/GENERATED_ODOO_DOCS.md
fi
```

### 3. CI/CD Integration

```yaml
# .github/workflows/pr-docs-check.yml
name: PR Documentation Check

on: pull_request

jobs:
  check-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate docs
        run: python scripts/generate_odoo_docs.py --format markdown
      - name: Check if docs are up-to-date
        run: |
          git diff --exit-code docs/GENERATED_ODOO_DOCS.md || \
          (echo "::error::Docs are out of date. Run: python scripts/generate_odoo_docs.py" && exit 1)
```

---

## 📈 Performance

### Documentation Generator

- **15 modules** → ~3 seconds
- **45 models** → Full AST parsing
- **393 fields** → Type extraction
- **Output**: 250KB markdown, 350KB HTML

### Code Search

- **Index time**: ~2 minutes for 500 Python files
- **Search latency**: <100ms (pgvector)
- **Claude response**: 2-5 seconds

---

## 🔧 Customization

### Add New Code Patterns

```python
# scripts/generate_odoo_docs.py

def _extract_bir_metadata(self, class_node: ast.ClassDef) -> Dict:
    """Extract BIR-specific metadata"""
    metadata = {}

    # Check for BIR form fields
    for node in class_node.body:
        if isinstance(node, ast.Assign):
            if 'bir_' in str(node.targets[0]):
                metadata['has_bir_fields'] = True

    return metadata
```

### Add Search Filters

```python
# scripts/insightpulse_code_search.py

def search_by_company(self, company_code: str) -> List[Dict]:
    """Find code related to specific company"""
    return self.search(
        query=f"company {company_code}",
        chunk_type='class',
        filter={'metadata.company_code': company_code}
    )
```

---

## 🎯 Roadmap

- [ ] **Real embeddings** - OpenAI/Claude API for better semantic search
- [ ] **Dependency graph** - Visualize module dependencies
- [ ] **Code diff search** - "Find similar changes to this PR"
- [ ] **Multi-repo support** - Index OCA, custom-addons, scripts separately
- [ ] **VSCode extension** - Inline code search while coding
- [ ] **Slack bot** - `/ipai-search "month-end closing"`
- [ ] **Auto-PR descriptions** - Generate PR descriptions from code changes

---

## 📚 Related Documentation

- [KNOWLEDGE.md](../docs/KNOWLEDGE.md) - Architecture and design principles
- [SKILLS.md](../docs/SKILLS.md) - Claude Code skills for Odoo development
- [OCA Integration](../scripts/vendor_oca.py) - OCA module vendoring
- [Deployment Guide](../docs/DEPLOYMENT.md) - Production deployment

---

**Built with ❤️ for InsightPulse AI**

*Accelerating Finance SSC development with AI-powered tooling*

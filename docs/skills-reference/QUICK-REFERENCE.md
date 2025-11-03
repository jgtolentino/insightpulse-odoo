# Odoomation Skills - Quick Reference

## 🚀 Fast Command Reference

### Development Commands
| Command | Result |
|---------|--------|
| "Scaffold Odoo module [name]" | Creates OCA-compliant module structure |
| "Generate .do/app.yaml" | Produces DigitalOcean deployment spec |
| "Create docker-compose.yml" | Builds multi-service container setup |
| "Build MCP server for [X]" | Generates Model Context Protocol server |
| "Generate OpenAPI 3.1 spec" | Creates API documentation |

### Finance SSC Commands
| Command | Result |
|---------|--------|
| "Create month-end closing wizard" | Builds Odoo wizard with checklist |
| "Generate BIR Form [1601-C/2550Q]" | Produces tax form automation |
| "Build expense report workflow" | Creates T&E approval chain |
| "Set up bank reconciliation" | Implements bank sync logic |
| "Create trial balance view" | Generates GL reporting view |

### Analytics Commands
| Command | Result |
|---------|--------|
| "Build Superset dashboard for [X]" | Creates complete dashboard JSON |
| "Generate SQL dataset for [Y]" | Writes optimized SQL query |
| "Create AR aging chart" | Builds aging bucket visualization |
| "Set up BIR compliance dashboard" | Produces tax compliance dashboard |

### Integration Commands
| Command | Result |
|---------|--------|
| "Sync Notion tasks to Odoo" | Creates bidirectional sync |
| "Set up Supabase RPC functions" | Generates PostgreSQL functions |
| "Build OCR receipt extraction" | Implements PaddleOCR pipeline |
| "Create vector search for docs" | Sets up pgvector semantic search |

---

## 📋 Skill Selection Guide

### "I need to..." → Use These Skills

**"...build a complete Odoo module"**
- Primary: `odoo19-oca-devops`
- Supporting: `odoo-agile-scrum-devops`

**"...automate month-end closing"**
- Primary: `odoo-finance-automation`
- Supporting: `multi-agency-orchestrator`, `superset-dashboard-automation`

**"...create expense management system"**
- Primary: `travel-expense-management`
- Supporting: `paddle-ocr-validation`, `superset-dashboard-automation`

**"...build analytics dashboards"**
- Primary: `superset-dashboard-automation`
- Supporting: `superset-chart-builder`, `superset-sql-developer`, `superset-dashboard-designer`

**"...sync with external systems"**
- Primary: `notion-workflow-sync` or `mcp-complete-guide`
- Supporting: `supabase-rpc-manager`

**"...extract data from receipts/forms"**
- Primary: `paddle-ocr-validation`
- Supporting: `supabase-rpc-manager`

**"...manage procurement workflows"**
- Primary: `procurement-sourcing`
- Supporting: `multi-agency-orchestrator`

**"...plan projects properly"**
- Primary: `pmbok-project-management`
- Supporting: `drawio-diagrams-enhanced`, `project-portfolio-management`

**"...deploy to production"**
- Primary: `odoo19-oca-devops`
- Supporting: `odoo-agile-scrum-devops`

---

## 🎯 Common Workflows

### Workflow 1: New Odoo Module
```
1. "Scaffold Odoo module [name]"
2. Review generated structure
3. "Add [models/views/security] to module"
4. "Generate unit tests"
5. "Create .do/app.yaml for deployment"
```

### Workflow 2: BIR Compliance Dashboard
```
1. "Create SQL dataset for BIR Form 2550Q"
2. "Build pivot table chart for VAT by month"
3. "Add time series for tax trends"
4. "Create dashboard layout"
5. "Set up exception alerts"
```

### Workflow 3: T&E System
```
1. "Create expense report model"
2. "Build approval workflow"
3. "Integrate PaddleOCR for receipts"
4. "Add policy validation rules"
5. "Create Superset dashboard"
```

### Workflow 4: Full Deployment
```
1. "Generate docker-compose.yml"
2. "Create .do/app.yaml"
3. "Build CI/CD pipeline"
4. "Generate deployment docs"
5. "Create monitoring setup"
```

---

## 💡 Pro Tips

### Getting Better Results

**✅ DO:**
- Specify agency codes (RIM, CKVC, etc.) when relevant
- Mention BIR form numbers (1601-C, 2550Q)
- Request OCA compliance for Odoo modules
- Ask for production-ready code
- Request unit tests
- Ask for documentation

**❌ DON'T:**
- Mix development and production configs
- Skip security configurations
- Forget database migrations
- Ignore BIR compliance requirements
- Overlook multi-agency support

### Common Pitfalls

**Problem**: Module doesn't install
**Solution**: Ask for "__manifest__.py validation"

**Problem**: SQL query is slow
**Solution**: Request "optimized SQL with indexes"

**Problem**: Dashboard doesn't show data
**Solution**: Check "dataset permissions and RLS"

**Problem**: OCR accuracy is low
**Solution**: Ask for "preprocessing pipeline"

---

## 📊 Cost Savings Tracker

| Replaced Tool | Self-Hosted Alternative | Annual Savings |
|---------------|-------------------------|----------------|
| SAP Concur | Odoo T&E Module | $15,000 |
| SAP Ariba | Odoo Procurement | $10,000 |
| Tableau | Apache Superset | $8,400 |
| **Total** | **Odoomation MVP** | **$27,500** |

---

## 🔧 Environment Variables

Common variables you'll need:

```bash
# Odoo
ODOO_VERSION=19
ODOO_WORKERS=4
ODOO_DB_HOST=postgres
ODOO_DB_PORT=5432

# Supabase
SUPABASE_URL=https://spdtwktxdalcfigzeqrz.supabase.co
SUPABASE_ANON_KEY=your_key
SUPABASE_SERVICE_KEY=your_service_key

# DigitalOcean
DO_PROJECT_ID=29cde7a1-8280-46ad-9fdf-dea7b21a7825
DO_REGION=sgp1

# BIR
BIR_TIN=123-456-789-000
BIR_RDO=123
```

---

## 📖 Essential Patterns

### Odoo Model Pattern
```python
from odoo import models, fields, api

class MyModel(models.Model):
    _name = 'my.model'
    _description = 'My Model Description'
    
    name = fields.Char(required=True)
    agency_id = fields.Many2one('res.company')
```

### Superset SQL Pattern
```sql
-- Finance SSC Dataset
SELECT
  agency_code,
  account_code,
  SUM(debit) - SUM(credit) AS balance
FROM account_move_line
WHERE date >= '{{ from_dttm }}'
GROUP BY 1, 2;
```

### Docker Compose Pattern
```yaml
version: '3.8'
services:
  odoo:
    image: odoo:19
    depends_on:
      - postgres
  postgres:
    image: postgres:16
```

---

## 🆘 Troubleshooting

### "Module not found"
→ Check `__manifest__.py` dependencies

### "Permission denied"
→ Verify `ir.model.access.csv`

### "SQL error"
→ Run "validate SQL syntax"

### "OCR not working"
→ Check PaddleOCR installation

### "Dashboard empty"
→ Verify dataset has data

---

## 📞 Need Help?

1. Check skill-specific SKILL.md
2. Review implementation examples
3. Ask GPT: "Show me example for [X]"
4. Request: "Debug [issue]"
5. Consult: MANIFEST.json for skill paths

---

**Version**: 1.0.0  
**Last Updated**: 2025-11-03  
**Total Skills**: 19  
**Target**: Odoomation MVP

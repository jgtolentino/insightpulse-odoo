# Skillsmith - Error Mining and Auto-Skill Generation

Mines production errors and generates preventive guardrails and auto-fix scripts.

## Components

- `sql/skillsmith.sql` - Error normalization and fingerprinting functions
- `miner.py` - Error mining and skill generation script
- `templates/` - Jinja2 templates for guardrails and fixers

## Usage

### Initialize Database

```bash
psql "$POSTGRES_URL" -f skillsmith/sql/skillsmith.sql
```

### Mine Errors

```bash
python3 skillsmith/miner.py --min_hits 2 --top 50
```

This will:
1. Refresh error signatures materialized view
2. Find top 50 error patterns with 2+ hits in last 7 days
3. Generate YAML skill files in `skills/proposed/`

### Skill Types

- **Guardrails** (GR-*): Preventive checks for common errors
- **Fixers** (FX-*): Auto-patch scripts for known issues

## Automation

Skills are automatically generated via GitHub Actions:
- **Schedule**: Every 6 hours
- **Workflow**: `.github/workflows/skillsmith.yml`
- **Output**: `skills/proposed/*.yaml`

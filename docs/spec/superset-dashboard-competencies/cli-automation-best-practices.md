# Superset CLI & Automation Best Practices

> Comprehensive guide for managing Apache Superset dashboards as code

## Overview

This guide covers three CLI approaches for dashboard automation:

| Tool | Use Case | Auth Method |
|------|----------|-------------|
| `superset` (native) | Server-side operations | Runs in server context |
| `preset-cli` | Preset Cloud + self-hosted | API token/secret |
| `sup!` (superset-sup) | Modern CLI, AI-agent ready | API token |

---

## 1. Native Superset CLI

### Export Dashboards (YAML Bundle)

```bash
# Export all dashboards to ZIP (contains YAML files)
superset export-dashboards -f /tmp/dashboard_bundle.zip

# Structure inside ZIP:
# dashboard_export_20241228/
# ├── dashboards/
# │   ├── sales_overview.yaml
# │   └── executive_summary.yaml
# ├── charts/
# │   ├── revenue_by_region.yaml
# │   └── monthly_trends.yaml
# ├── datasets/
# │   └── sales_data.yaml
# └── databases/
#     └── analytics_db.yaml
```

### Import Dashboards

```bash
# Import bundle to Superset (assign to admin user)
superset import-dashboards -p /tmp/dashboard_bundle.zip -u admin

# Via Docker
docker compose exec superset superset import-dashboards \
  -p /tmp/dashboard_bundle.zip -u admin
```

**Key behaviors:**
- **Upsert by UUID**: Existing dashboards with same UUID are updated (no duplicates)
- **No prompts**: CLI assumes you want to deploy (no confirmation dialogs)
- **Deletions don't propagate**: Removed items won't be deleted on target

### Import Datasources (Separate Command)

```bash
# Import databases and datasets with sync options
superset import_datasources -p datasources.yaml -s columns -s metrics

# -s columns: Sync column deletions
# -s metrics: Sync metric deletions
```

---

## 2. Jinja2 Templating in YAML

### Why Template?

- **Environment-specific configs**: Different DB URIs for dev/staging/prod
- **Multi-tenant deployments**: Same dashboard, different workspaces
- **DRY principle**: One template, multiple rendered outputs

### Database Template Example

```yaml
# databases/analytics_db.yaml
database_name: Analytics DB
sqlalchemy_uri: >-
  postgresql+psycopg2://{{ env('DB_USER') }}:{{ env('DB_PASSWORD') }}@{{ env('DB_HOST') }}:{{ env('DB_PORT', '5432') }}/{{ env('DB_NAME') }}

expose_in_sqllab: true
allow_ctas: {{ env('ALLOW_CTAS', 'false') | lower == 'true' }}
allow_cvas: {{ env('ALLOW_CVAS', 'false') | lower == 'true' }}
allow_dml: {{ env('ALLOW_DML', 'false') | lower == 'true' }}

extra:
  allows_virtual_table_explore: true
  {% if env('DB_SSL_MODE') %}
  engine_params:
    connect_args:
      sslmode: {{ env('DB_SSL_MODE') }}
  {% endif %}
```

### Dataset Template Example

```yaml
# datasets/sales_data.yaml
table_name: {{ env('TABLE_PREFIX', '') }}sales_data
schema: {{ env('SCHEMA', 'public') }}
database_uuid: {{ env('DATABASE_UUID') }}

description: |
  Sales transaction data
  Environment: {{ env('ENVIRONMENT', 'development') }}

columns:
  - column_name: order_date
    type: TIMESTAMP
    filterable: true
    is_dttm: true
  - column_name: revenue
    type: NUMERIC
    filterable: true
    groupby: false

metrics:
  - metric_name: total_revenue
    expression: SUM(revenue)
    metric_type: sum
  - metric_name: order_count
    expression: COUNT(*)
    metric_type: count
```

### Dashboard Template with Conditionals

```yaml
# dashboards/sales_overview.yaml
dashboard_title: >-
  {% if env('ENVIRONMENT') == 'production' %}
  Sales Overview
  {% else %}
  [{{ env('ENVIRONMENT') | upper }}] Sales Overview
  {% endif %}

slug: sales-overview-{{ env('ENVIRONMENT', 'dev') }}
published: {{ env('ENVIRONMENT') == 'production' }}

metadata:
  color_scheme: {{ env('COLOR_SCHEME', 'supersetColors') }}
  native_filter_configuration:
    {% if env('ENABLE_FILTERS', 'true') | lower == 'true' %}
    - id: date_filter
      name: Date Range
      filterType: filter_time
      targets:
        - datasetId: {{ env('SALES_DATASET_ID') }}
    {% endif %}
```

### Rendering Templates

**With preset-cli:**
```bash
# Set environment variables
export DB_HOST="prod-db.example.com"
export DB_USER="superset_user"
export DB_PASSWORD="$VAULT_DB_PASSWORD"
export ENVIRONMENT="production"

# CLI renders Jinja2 automatically during sync
preset-cli superset sync native ./superset_assets
```

**Manual rendering (for native CLI):**
```bash
# Using Python + Jinja2
python3 <<'EOF'
import os
from jinja2 import Environment, FileSystemLoader
import yaml

env = Environment(loader=FileSystemLoader('superset_assets'))
env.globals['env'] = os.environ.get

template = env.get_template('databases/analytics_db.yaml')
rendered = template.render()

with open('rendered/databases/analytics_db.yaml', 'w') as f:
    f.write(rendered)
EOF

# Then import the rendered files
superset import-dashboards -p rendered/dashboard_bundle.zip -u admin
```

---

## 3. Multi-Environment Promotion

### Environment Strategy

```
┌─────────────────────────────────────────────────────────────┐
│  DEV (Local/Feature Branch)                                 │
│  - Rapid iteration in Superset UI                           │
│  - Export to YAML after changes                             │
└─────────────────────────────────────────────────────────────┘
                              ↓ git push
┌─────────────────────────────────────────────────────────────┐
│  GIT REPOSITORY (Source of Truth)                           │
│  - Jinja2 templates in superset_assets/                     │
│  - PR review for dashboard changes                          │
└─────────────────────────────────────────────────────────────┘
                              ↓ merge to main
┌─────────────────────────────────────────────────────────────┐
│  STAGING                                                    │
│  - CI/CD renders templates with staging vars                │
│  - Automated smoke tests                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓ approval + tag
┌─────────────────────────────────────────────────────────────┐
│  PRODUCTION                                                 │
│  - CI/CD renders templates with prod vars                   │
│  - --disallow-edits flag prevents UI changes                │
└─────────────────────────────────────────────────────────────┘
```

### Consistent Naming Strategy

**Best practice**: Use identical names across environments

```yaml
# All environments use the same database name
database_name: Analytics DB

# Connection details come from environment-specific config
sqlalchemy_uri: {{ env('ANALYTICS_DB_URI') }}
```

This ensures exported dashboards import cleanly across environments.

### Environment-Specific Config Files

```
superset_assets/
├── databases/
│   └── analytics_db.yaml          # Template
├── datasets/
│   └── sales_data.yaml            # Template
├── charts/
│   └── revenue_chart.yaml         # Template
├── dashboards/
│   └── sales_overview.yaml        # Template
└── envs/
    ├── dev.env
    ├── staging.env
    └── production.env
```

**env files:**
```bash
# envs/production.env
DB_HOST=prod-db.example.com
DB_NAME=analytics
DB_USER=superset_prod
ENVIRONMENT=production
ENABLE_FILTERS=true
COLOR_SCHEME=supersetColors
```

---

## 4. CI/CD Pipeline Patterns

### GitHub Actions: Complete Workflow

```yaml
# .github/workflows/deploy-dashboards.yml
name: Deploy Dashboards

on:
  push:
    branches: [main]
    paths:
      - 'superset_assets/**'
  workflow_dispatch:
    inputs:
      environment:
        description: 'Target environment'
        required: true
        default: 'staging'
        type: choice
        options: [staging, production]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ github.event.inputs.environment || 'staging' }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install preset-cli jinja2 pyyaml

      - name: Load environment config
        run: |
          ENV_NAME="${{ github.event.inputs.environment || 'staging' }}"
          if [ -f "superset_assets/envs/${ENV_NAME}.env" ]; then
            export $(cat superset_assets/envs/${ENV_NAME}.env | xargs)
          fi

      - name: Validate templates
        run: |
          python3 <<'EOF'
          import os
          from pathlib import Path
          from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError

          env = Environment(loader=FileSystemLoader('superset_assets'))
          env.globals['env'] = os.environ.get

          errors = []
          for yaml_file in Path('superset_assets').rglob('*.yaml'):
              try:
                  template = env.get_template(str(yaml_file.relative_to('superset_assets')))
                  template.render()  # Test render
              except TemplateSyntaxError as e:
                  errors.append(f"{yaml_file}: {e}")

          if errors:
              print("Template validation failed:")
              for e in errors:
                  print(f"  ❌ {e}")
              exit(1)
          print("✅ All templates valid")
          EOF

      - name: Deploy to Superset
        env:
          SUPERSET_URL: ${{ secrets.SUPERSET_URL }}
          SUPERSET_API_TOKEN: ${{ secrets.SUPERSET_API_TOKEN }}
          SUPERSET_API_SECRET: ${{ secrets.SUPERSET_API_SECRET }}
        run: |
          # For Preset Cloud
          if [ -n "$SUPERSET_API_TOKEN" ]; then
            preset-cli \
              --workspaces="$SUPERSET_URL" \
              superset sync native ./superset_assets \
              --overwrite \
              --disallow-edits
          else
            # For self-hosted (using superset-cli wrapper)
            superset-cli "$SUPERSET_URL" sync native ./superset_assets \
              --username "${{ secrets.SUPERSET_ADMIN_USER }}" \
              --password "${{ secrets.SUPERSET_ADMIN_PASS }}"
          fi

      - name: Verify deployment
        env:
          SUPERSET_URL: ${{ secrets.SUPERSET_URL }}
        run: |
          # Get auth token
          TOKEN=$(curl -s -X POST "$SUPERSET_URL/api/v1/security/login" \
            -H "Content-Type: application/json" \
            -d '{"username":"${{ secrets.SUPERSET_ADMIN_USER }}","password":"${{ secrets.SUPERSET_ADMIN_PASS }}","provider":"db"}' \
            | jq -r '.access_token')

          # Verify dashboards exist
          DASHBOARD_COUNT=$(curl -s "$SUPERSET_URL/api/v1/dashboard/" \
            -H "Authorization: Bearer $TOKEN" \
            | jq '.count')

          echo "✅ Deployed. Dashboard count: $DASHBOARD_COUNT"
```

### Handling Deletions

**Problem**: Import doesn't delete removed assets

**Solutions**:

1. **Full reset approach** (simple but destructive):
```bash
# Delete all dashboards first, then import
superset-cli $URL delete-dashboards --all
superset-cli $URL sync native ./superset_assets
```

2. **Sync with deletion flags** (for datasources):
```bash
superset import_datasources -p datasources.yaml -s columns -s metrics
# -s flags sync deletions for columns/metrics
```

3. **Track deletions in Git**:
```yaml
# superset_assets/deletions.yaml
deleted:
  dashboards:
    - uuid: "abc-123-def"  # Removed in PR #45
  charts:
    - uuid: "xyz-789-ghi"  # Deprecated Q4 2024
```

Then process deletions in CI:
```python
# delete_removed.py
import yaml
import requests

with open('superset_assets/deletions.yaml') as f:
    deletions = yaml.safe_load(f)

for dashboard_uuid in deletions.get('deleted', {}).get('dashboards', []):
    requests.delete(f"{SUPERSET_URL}/api/v1/dashboard/{dashboard_uuid}",
                   headers={"Authorization": f"Bearer {token}"})
```

---

## 5. Advanced Patterns

### Disallow UI Edits (Production Protection)

```bash
# Mark dashboards as externally managed
preset-cli superset sync native ./superset_assets \
  --overwrite \
  --disallow-edits

# Users see: "This dashboard is managed externally.
#             View source: https://github.com/your-repo"
```

### dbt Integration

```bash
# Sync dbt models → Superset datasets
preset-cli superset sync dbt-core ./dbt_project \
  --project ./dbt_project \
  --profiles ~/.dbt/profiles.yml \
  --target prod
```

### Scheduled Exports (Backup)

```yaml
# .github/workflows/backup-dashboards.yml
name: Backup Dashboards

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Export dashboards
        run: |
          superset-cli ${{ secrets.SUPERSET_URL }} export-assets \
            ./backups/$(date +%Y%m%d) \
            --username "${{ secrets.SUPERSET_ADMIN_USER }}" \
            --password "${{ secrets.SUPERSET_ADMIN_PASS }}"

      - name: Commit backup
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add backups/
          git commit -m "chore: daily dashboard backup $(date +%Y-%m-%d)" || exit 0
          git push
```

---

## 6. Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Database not found" | Missing dependency | Import databases before dashboards |
| Duplicate dashboards | Different UUIDs | Use consistent UUIDs across envs |
| Stale charts remain | Deletions don't sync | Manually delete or use reset approach |
| Template render error | Missing env var | Set all required variables |
| Auth failure | Token expired | Refresh API token |

### Debug Template Rendering

```bash
# Dry-run to see rendered output
preset-cli superset sync native ./superset_assets --dry-run

# Or render manually
python3 -c "
from jinja2 import Environment, FileSystemLoader
import os
env = Environment(loader=FileSystemLoader('.'))
env.globals['env'] = os.environ.get
print(env.get_template('superset_assets/databases/db.yaml').render())
"
```

### Validate YAML Structure

```bash
# Check YAML syntax
python3 -c "
import yaml
from pathlib import Path
for f in Path('superset_assets').rglob('*.yaml'):
    try:
        yaml.safe_load(f.read_text())
        print(f'✅ {f}')
    except yaml.YAMLError as e:
        print(f'❌ {f}: {e}')
"
```

---

## 7. Quick Reference

### Export Commands

```bash
# Native Superset CLI
superset export-dashboards -f bundle.zip
superset export-datasources -f datasources.yaml

# preset-cli (self-hosted)
superset-cli https://superset.example.com export-assets ./superset_assets

# preset-cli (Preset Cloud)
preset-cli --workspaces=https://workspace.us1a.app.preset.io/ \
  superset export-assets ./superset_assets
```

### Import Commands

```bash
# Native Superset CLI
superset import-dashboards -p bundle.zip -u admin
superset import_datasources -p datasources.yaml

# preset-cli (self-hosted)
superset-cli https://superset.example.com sync native ./superset_assets

# preset-cli (Preset Cloud)
preset-cli --workspaces=https://workspace.us1a.app.preset.io/ \
  superset sync native ./superset_assets
```

---

## Resources

- [Superset SQL Templating Docs](https://superset.apache.org/docs/configuration/sql-templating)
- [preset-cli / backend-sdk](https://github.com/preset-io/backend-sdk)
- [Preset Blog: Assets as Code](https://preset.io/blog/managing-superset-assets-as-code/)
- [Preset Blog: dbt Integration](https://preset.io/blog/dbt-superset-integration/)

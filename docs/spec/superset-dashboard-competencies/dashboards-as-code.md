# Superset Dashboards-as-Code Guide

> Infrastructure-as-Code workflow for Apache Superset using preset-cli / backend-sdk

## Overview

The [preset-io/backend-sdk](https://github.com/preset-io/backend-sdk) provides a CLI for managing Superset assets (databases, datasets, charts, dashboards) as YAML files under version control.

**Key Benefits:**
- Dashboard definitions stored in Git
- PRs show exactly what changed in dashboards
- CI/CD-friendly deployment to multiple environments
- Works with both Preset Cloud and self-hosted Superset

---

## 1. Installation

```bash
# Install from PyPI
pip install -U setuptools setuptools_scm wheel
pip install preset-cli

# Or install directly from repo
pip install "git+https://github.com/preset-io/backend-sdk.git"
```

---

## 2. Authentication

### For Preset Cloud

```bash
# Interactive auth (opens browser)
preset-cli auth
# Generates token/secret → stored in credentials.yaml

# Or via environment variables
export PRESET_API_TOKEN="your-token"
export PRESET_API_SECRET="your-secret"
```

### For Self-Hosted Superset

Use the `superset-cli` wrapper with your Superset URL:

```bash
# Self-hosted Superset (e.g., DigitalOcean deployment)
superset-cli https://superset.insightpulseai.net export-assets ./superset_assets
```

---

## 3. Core Workflow: Export → Git → Sync

### Step 1: Export Assets to YAML

**From Preset Cloud:**
```bash
preset-cli \
  --workspaces=https://YOUR_WORKSPACE.us1a.app.preset.io/ \
  superset export-assets ./superset_assets
```

**From Self-Hosted Superset:**
```bash
superset-cli https://superset.insightpulseai.net export-assets ./superset_assets
```

**Output Structure:**
```
superset_assets/
├── databases/
│   └── examples_postgres.yaml
├── datasets/
│   ├── birth_names.yaml
│   ├── flights.yaml
│   └── channels.yaml
├── charts/
│   ├── sales_by_region.yaml
│   └── monthly_trends.yaml
└── dashboards/
    ├── sales_overview.yaml
    └── executive_summary.yaml
```

### Step 2: Version Control

```bash
# Add to Git
git add superset_assets/
git commit -m "feat(dashboards): export current dashboard definitions"
git push
```

**Recommended Practice:**
- Store `superset_assets/` in your infrastructure/analytics repo
- Treat YAMLs as canonical definitions
- PRs = dashboard changes with visible diffs

### Step 3: Sync to Target Environment

**To Preset Cloud:**
```bash
preset-cli \
  --workspaces=https://YOUR_WORKSPACE.us1a.app.preset.io/ \
  superset sync native ./superset_assets
```

**To Self-Hosted Superset:**
```bash
superset-cli https://superset.insightpulseai.net sync native ./superset_assets
```

**Multi-Environment Sync:**
```bash
# Sync to multiple workspaces in one command
preset-cli \
  --workspaces=https://dev.us1a.app.preset.io/,https://prod.us1a.app.preset.io/ \
  superset sync native ./superset_assets
```

---

## 4. CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/deploy-dashboards.yml
name: Deploy Dashboards

on:
  push:
    branches: [main]
    paths:
      - 'superset_assets/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install preset-cli
        run: pip install preset-cli

      - name: Deploy to Superset
        env:
          PRESET_API_TOKEN: ${{ secrets.PRESET_API_TOKEN }}
          PRESET_API_SECRET: ${{ secrets.PRESET_API_SECRET }}
        run: |
          preset-cli \
            --workspaces=https://prod-workspace.us1a.app.preset.io/ \
            superset sync native ./superset_assets
```

### Self-Hosted Superset CI/CD

```yaml
# .github/workflows/deploy-dashboards-selfhosted.yml
name: Deploy to Self-Hosted Superset

on:
  push:
    branches: [main]
    paths:
      - 'superset_assets/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install preset-cli
        run: pip install preset-cli

      - name: Deploy to Superset
        env:
          SUPERSET_URL: ${{ secrets.SUPERSET_URL }}
          SUPERSET_ADMIN_USER: ${{ secrets.SUPERSET_ADMIN_USER }}
          SUPERSET_ADMIN_PASS: ${{ secrets.SUPERSET_ADMIN_PASS }}
        run: |
          superset-cli $SUPERSET_URL sync native ./superset_assets
```

---

## 5. CLI Command Reference

### Export Commands

```bash
# Export all assets
superset-cli <URL> export-assets ./output_dir

# Export specific asset types
superset-cli <URL> export-assets ./output_dir --asset-type dashboard
superset-cli <URL> export-assets ./output_dir --asset-type chart
superset-cli <URL> export-assets ./output_dir --asset-type dataset
```

### Sync Commands

```bash
# Sync all native assets (YAML → Superset)
superset-cli <URL> sync native ./superset_assets

# Dry run (preview changes)
superset-cli <URL> sync native ./superset_assets --dry-run
```

### SQL Commands

```bash
# Run SQL queries against Superset databases
superset-cli <URL> sql --database-id 1 "SELECT COUNT(*) FROM birth_names"
```

---

## 6. Asset YAML Structure

### Database Definition

```yaml
# superset_assets/databases/examples_postgres.yaml
database_name: Examples (Postgres)
sqlalchemy_uri: postgresql+psycopg2://user:pass@host:5432/db
expose_in_sqllab: true
allow_ctas: true
allow_cvas: true
allow_dml: false
extra:
  allows_virtual_table_explore: true
```

### Dataset Definition

```yaml
# superset_assets/datasets/birth_names.yaml
table_name: birth_names
schema: examples
database_uuid: abc-123-def
description: Baby names data from US Social Security
columns:
  - column_name: name
    type: VARCHAR(255)
    filterable: true
    groupby: true
  - column_name: num
    type: INTEGER
    filterable: true
metrics:
  - metric_name: count
    expression: COUNT(*)
    metric_type: count
```

### Chart Definition

```yaml
# superset_assets/charts/top_names.yaml
slice_name: Top Baby Names
viz_type: bar
datasource_type: table
datasource_name: birth_names
params:
  metrics:
    - count
  groupby:
    - name
  row_limit: 10
  order_desc: true
```

### Dashboard Definition

```yaml
# superset_assets/dashboards/names_dashboard.yaml
dashboard_title: Baby Names Analysis
slug: baby-names-analysis
published: true
position_json: |
  {
    "DASHBOARD_VERSION_KEY": "v2",
    "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
    ...
  }
metadata:
  native_filter_configuration: []
  color_scheme: supersetColors
slices:
  - top_names
  - names_by_year
  - names_by_state
```

---

## 7. Environment Promotion Pattern

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   DEV       │────▶│   STAGING   │────▶│   PROD      │
│ (authoring) │     │  (testing)  │     │  (live)     │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   ▲                   ▲
       │                   │                   │
       ▼                   │                   │
┌─────────────┐            │                   │
│    Git      │────────────┴───────────────────┘
│ (source of  │         sync native
│   truth)    │
└─────────────┘
```

### Workflow Steps

1. **Author** dashboards in DEV environment
2. **Export** assets to Git: `export-assets ./superset_assets`
3. **PR Review** - diffs show exactly what changed
4. **Merge** → triggers CI/CD
5. **Sync** to STAGING for testing
6. **Promote** to PROD via another sync

---

## 8. Best Practices

### Git Workflow

| Practice | Description |
|----------|-------------|
| **Branch per feature** | `feat/sales-dashboard-v2` |
| **Meaningful commits** | `feat(dashboards): add regional breakdown chart` |
| **PR reviews** | Review YAML diffs before merging |
| **Protected branches** | Require approval for main/prod |

### Security

| Practice | Description |
|----------|-------------|
| **Never commit credentials** | Use env vars or secrets |
| **Mask database URIs** | Use `${DB_URI}` placeholders |
| **Separate credentials** | Different tokens per environment |
| **Audit trail** | Git history = deployment history |

### Reliability

| Practice | Description |
|----------|-------------|
| **Dry runs first** | `--dry-run` before actual sync |
| **Backup before sync** | Export before overwriting |
| **Incremental changes** | Small PRs over big bangs |
| **Rollback plan** | Git revert + sync if needed |

---

## 9. Troubleshooting

### Authentication Errors

```bash
# Check credentials are set
echo $PRESET_API_TOKEN | head -c 10

# Re-authenticate
preset-cli auth --force
```

### Sync Conflicts

```bash
# Export current state first
superset-cli <URL> export-assets ./current_state

# Compare with your repo
diff -r ./current_state ./superset_assets

# Force sync (careful!)
superset-cli <URL> sync native ./superset_assets --force
```

### Missing Dependencies

```bash
# Sync in order: databases → datasets → charts → dashboards
superset-cli <URL> sync native ./superset_assets/databases
superset-cli <URL> sync native ./superset_assets/datasets
superset-cli <URL> sync native ./superset_assets/charts
superset-cli <URL> sync native ./superset_assets/dashboards
```

---

## 10. Integration with Existing Competencies

This Dashboards-as-Code workflow maps to competency levels:

| Level | Skills |
|-------|--------|
| **L1** | Can export/import assets manually |
| **L2** | Understands YAML structure, can edit assets |
| **L3** | Can design CI/CD pipelines, multi-env promotion |
| **L4** | Defines organizational DAC standards |

---

## Resources

- **Repository**: [preset-io/backend-sdk](https://github.com/preset-io/backend-sdk)
- **README**: Full CLI documentation
- **Examples**: `examples/exports/` for sample YAML structures
- **Docs**: Advanced patterns (dbt integration, multi-workspace)

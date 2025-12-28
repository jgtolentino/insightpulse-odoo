# Preset/Superset Hybrid Control Plane

> GitOps-first dashboard management with templating, promotion, and drift detection

## Overview

The Hybrid Control Plane sits above Preset/Superset to provide:

1. **Dashboard-as-Code**: Versioned Jinja2 templates in Git
2. **Multi-Environment Promotion**: dev → staging → prod via CLI
3. **Drift Detection**: Compare runtime state vs compiled bundle
4. **UI-to-Git Roundtrip**: Export → normalize → PR automation
5. **Translate**: Convert raw exports to reusable templates

```
┌─────────────────────────────────────────────────────────────────┐
│  GIT REPOSITORY (Source of Truth)                               │
│  assets/*.yaml.j2 + env/*.yaml + mappings/*.yaml                │
└─────────────────────────────────────────────────────────────────┘
         │ compile                                    ▲ translate
         ▼                                            │
┌─────────────────────────────────────────────────────────────────┐
│  BUNDLES (Rendered YAML)                                        │
│  bundles/{dev,staging,prod}/*.yaml                              │
└─────────────────────────────────────────────────────────────────┘
         │ apply                                      │ export
         ▼                                            │
┌─────────────────────────────────────────────────────────────────┐
│  SUPERSET / PRESET RUNTIME                                      │
│  Dashboards, Charts, Datasets, Databases                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Repository Structure

```
preset-hybrid/
├── hybrid.yaml                    # Control plane config
├── pyproject.toml                 # Python package
├── src/hybrid/                    # CLI source
│   ├── cli.py                     # Main CLI
│   ├── compiler.py                # Jinja2 renderer
│   ├── normalize.py               # YAML normalizer
│   ├── translate.py               # Export → template converter
│   ├── superset.py                # Runtime sync wrapper
│   └── validators.py              # Schema validation
├── assets/                        # Source of truth (templates)
│   ├── databases/
│   │   └── analytics_db.yaml.j2
│   ├── datasets/
│   │   └── fact_sales.yaml.j2
│   ├── charts/
│   │   └── revenue_over_time.yaml.j2
│   └── dashboards/
│       └── overview.yaml.j2
├── env/                           # Environment variables
│   ├── dev.yaml
│   ├── staging.yaml
│   └── prod.yaml
├── mappings/                      # Schema retarget mappings
│   └── client_a.yaml
├── bundles/                       # Compiled output (gitignored)
│   ├── dev/
│   ├── staging/
│   └── prod/
├── ui_exports/                    # Normalized runtime exports
│   └── dev/
├── scripts/
│   └── export_to_pr.sh            # UI → Git automation
└── .github/workflows/
    ├── hybrid.yml                 # CI: compile/validate/plan
    └── ui-export-pr.yml           # Export → PR workflow
```

---

## Configuration

### `hybrid.yaml`

```yaml
# Control plane configuration
mode: superset          # superset | preset

superset:
  # For self-hosted Superset
  url: "https://superset.insightpulseai.net"

preset:
  # For Preset Cloud workspaces
  workspaces:
    dev: "https://workspace-dev.us1a.app.preset.io/"
    staging: "https://workspace-staging.us1a.app.preset.io/"
    prod: "https://workspace-prod.us1a.app.preset.io/"

# Default environment for commands
default_env: dev

# Asset directories
assets_dir: "assets"
bundles_dir: "bundles"
```

### Environment Variables (`env/dev.yaml`)

```yaml
# Template variables for dev bundles
ENV: dev
DB_HOST: "db-dev.example.com"
DB_NAME: "analytics_dev"
SCHEMA: "public"
TENANT_KEY: "customer_id"
```

---

## CLI Commands

### Core Workflow

```bash
# Initialize repo structure
hybrid init

# Compile templates → rendered bundles
hybrid compile --env dev
hybrid compile --env prod

# Validate bundle (schema + policy checks)
hybrid validate --env dev

# Plan (show manifest + drift detection)
hybrid plan --env dev

# Apply bundle to target runtime
hybrid apply --env dev

# Export runtime state to local bundle
hybrid export --env dev --out .hybrid/exports/dev
```

### Drift Detection

```bash
# Compare compiled bundle vs runtime state
hybrid drift-plan --env dev

# Output:
# - NO_DRIFT if identical
# - DRIFT_FOUND with diff output if different
```

### Environment Promotion

```bash
# Promote through default chain (dev → staging → prod)
hybrid promote

# Custom chain
hybrid promote --chain dev,prod

# Stop on drift
hybrid promote --drift
```

### UI-to-Git Roundtrip

```bash
# Export runtime → normalize → translate → PR
./scripts/export_to_pr.sh dev

# Just translate (convert exports to templates)
hybrid translate --env dev
```

---

## Asset Templates

### Database Template

```yaml
# assets/databases/analytics_db.yaml.j2
database_name: "analytics_{{ ENV }}"
sqlalchemy_uri: "postgresql+psycopg2://{{ DB_HOST }}/{{ DB_NAME }}"
cache_timeout: null
extra:
  metadata_params: {}
  engine_params: {}
```

### Dataset Template

```yaml
# assets/datasets/fact_sales.yaml.j2
table_name: "fact_sales"
schema: "{{ SCHEMA }}"
database: "analytics_{{ ENV }}"
columns:
  - column_name: "order_date"
    is_dttm: true
  - column_name: "{{ TENANT_KEY }}"
    filterable: true
  - column_name: "brand"
  - column_name: "revenue"
metrics:
  - metric_name: "Total Revenue"
    expression: "SUM(revenue)"
```

### Chart Template

```yaml
# assets/charts/revenue_over_time.yaml.j2
slice_name: "Revenue Over Time ({{ ENV }})"
viz_type: "{{ viz_type | default('echarts_timeseries_line') }}"
datasource: "fact_sales"
params:
  x_axis: "order_date"
  time_grain_sqla: "P1D"
  metrics:
    - "Total Revenue"
  adhoc_filters: []
  row_limit: 1000
cache_timeout: null
```

### Dashboard Template

```yaml
# assets/dashboards/overview.yaml.j2
dashboard_title: "Overview ({{ ENV }})"
slug: "overview-{{ ENV }}"
description: "Auto-generated dashboard"
css: ""
metadata:
  default_filters: "{}"
  native_filter_configuration:
    {% if ENABLE_FILTERS | default(true) %}
    - id: date_filter
      name: Date Range
      filterType: filter_time
    {% endif %}
position:
  ROOT_ID:
    type: ROOT
    id: ROOT_ID
    children: [GRID_ID]
  GRID_ID:
    type: GRID
    id: GRID_ID
    children: [CHART-1]
  CHART-1:
    type: CHART
    id: CHART-1
    meta:
      sliceName: "Revenue Over Time ({{ ENV }})"
    columns: 12
    rows: 6
```

---

## Schema Retargeting

### Mapping File (`mappings/client_a.yaml`)

```yaml
# Retarget mappings for Client A
source:
  database: "analytics_dev"
  schema: "public"
  tables:
    fact_sales: "fact_sales"
  columns:
    customer_id: "customer_id"
    order_date: "order_date"

target:
  database: "client_a_warehouse"
  schema: "analytics"
  tables:
    fact_sales: "client_a_transactions"
  columns:
    customer_id: "client_customer_id"
    order_date: "transaction_date"

# Metric renames
metrics:
  "Total Revenue": "Client A Revenue"
```

### Usage

```bash
# Apply mapping during compile
hybrid compile --env prod --mapping mappings/client_a.yaml
```

---

## CI/CD Workflows

### Compile/Validate/Plan (`.github/workflows/hybrid.yml`)

```yaml
name: hybrid

on:
  push:
    paths:
      - "assets/**"
      - "env/**"
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install
        run: pip install -e .

      - name: Compile
        run: hybrid compile --env dev

      - name: Validate
        run: hybrid validate --env dev

      - name: Plan
        run: hybrid plan --env dev
```

### UI Export → PR (`.github/workflows/ui-export-pr.yml`)

```yaml
name: ui-export-pr

on:
  workflow_dispatch:
    inputs:
      env:
        description: "Environment"
        required: true
        default: "dev"
  schedule:
    - cron: "0 2 * * *"  # Nightly

permissions:
  contents: write
  pull-requests: write

jobs:
  export_pr:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install
        run: |
          pip install -e .
          pip install preset-cli

      - name: Export → PR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          ./scripts/export_to_pr.sh "${{ inputs.env }}"
```

---

## Translate: Export → Templates

The `translate` command converts raw exports to reusable templates:

### Translation Rules (Default)

```python
DEFAULT_RULES = [
    # Replace environment markers with Jinja vars
    (re.compile(r"\bdev\b", re.IGNORECASE), "{{ ENV }}"),
    (re.compile(r"\bstaging\b", re.IGNORECASE), "{{ ENV }}"),
    (re.compile(r"\bprod\b", re.IGNORECASE), "{{ ENV }}"),
]
```

### Custom Rules

```python
# Add DB-specific replacements
CUSTOM_RULES = DEFAULT_RULES + [
    (re.compile(r"db-dev\.example\.com"), "{{ DB_HOST }}"),
    (re.compile(r"analytics_dev"), "{{ DB_NAME }}"),
    (re.compile(r'"public"'), '"{{ SCHEMA }}"'),
]
```

### Usage

```bash
# Export runtime
hybrid export --env dev --out ui_exports/dev

# Translate to templates
hybrid translate --env dev

# Result: assets/{charts,dashboards,...}/*.yaml.j2
```

---

## Embedding with Tenant Enforcement

### Token Minting

```bash
# Mint embed token with tenant context
hybrid embed mint-token \
  --dashboard-id 42 \
  --tenant-id "customer_123" \
  --user-id "user_456" \
  --expires 3600
```

### Embed Policy (`assets/embeds/policy.yaml`)

```yaml
# Embed security policy
allowed_domains:
  - "app.example.com"
  - "*.example.com"

tenant_enforcement:
  required: true
  injection_method: "where_clause"  # or "parameterized_view"
  tenant_column: "customer_id"

token_policy:
  max_ttl: 86400
  require_user_id: true
  require_roles: ["viewer", "analyst"]
```

---

## Observability

### Metrics Endpoints

```bash
# Query execution stats
GET /api/metrics/queries

# Embed token stats
GET /api/metrics/embeds

# Deploy audit logs
GET /api/audit/deploys
```

### Audit Log Fields

```json
{
  "timestamp": "2024-12-28T10:30:00Z",
  "actor": "ci-bot",
  "action": "deploy",
  "env": "prod",
  "git_sha": "abc123",
  "assets": {
    "dashboards": 5,
    "charts": 20,
    "datasets": 10
  },
  "status": "success"
}
```

---

## Quick Start

```bash
# 1. Clone/init repo
git clone <your-hybrid-repo>
cd preset-hybrid

# 2. Install CLI
pip install -e .

# 3. Configure target
vim hybrid.yaml  # Set superset.url or preset.workspaces

# 4. Create environment config
cp env/dev.yaml env/prod.yaml
vim env/prod.yaml

# 5. Compile and deploy
hybrid compile --env dev
hybrid validate --env dev
hybrid apply --env dev

# 6. Verify
hybrid export --env dev --out .hybrid/verify
diff -r bundles/dev .hybrid/verify
```

---

## Comparison: Raw Superset CLI vs Hybrid

| Operation | Raw CLI | Hybrid CLI |
|-----------|---------|------------|
| Export | `superset-cli export-assets` | `hybrid export` |
| Import | `superset-cli sync native` | `hybrid apply` |
| Templating | Manual Jinja2 | Built-in `compile` |
| Validation | None | `hybrid validate` |
| Drift detection | None | `hybrid drift-plan` |
| Multi-env promotion | Manual per-env | `hybrid promote` |
| UI → Git | Manual copy | `export_to_pr.sh` |
| Export → Template | Manual | `hybrid translate` |

---

## Resources

- [Preset Assets as Code](https://preset.io/blog/managing-superset-assets-as-code/)
- [preset-cli / backend-sdk](https://github.com/preset-io/backend-sdk)
- [Superset Export/Import Docs](https://superset.apache.org/docs/miscellaneous/importing-exporting-datasources)
- [ECharts Examples](https://echarts.apache.org/examples/en/)

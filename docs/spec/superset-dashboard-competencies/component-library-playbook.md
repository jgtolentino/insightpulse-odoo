# Superset Component Library Playbook

> Build a reusable chart/dashboard component library from existing dashboards

## Overview

This playbook describes how to:
1. **Harvest** components from "good" dashboards (official samples, demos)
2. **Decompose** into a normalized component library
3. **Templatize** with Jinja2 for reusability
4. **Generate** new dashboards from templates
5. **Deploy** via CLI pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  HARVEST                                                        │
│  Export from multiple Superset instances                        │
│  (official samples, demos, your experiments)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  DECOMPOSE                                                      │
│  Curate into component library                                  │
│  (best time-series, top-N, heatmaps, funnels, etc.)            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  TEMPLATIZE                                                     │
│  Convert to Jinja2 templates with parameters                    │
│  (datasource, metrics, dimensions, filters)                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  GENERATE                                                       │
│  Render templates → plain YAML per use case                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  DEPLOY                                                         │
│  superset-cli sync native → dashboards appear                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 1. Harvest Components from Good Dashboards

### Export from Multiple Sources

```bash
# Official Superset samples
superset-cli https://demo.superset.apache.org export-assets ./raw/official_samples

# Your production instance
superset-cli https://superset.insightpulseai.net export-assets ./raw/production

# Other demo/reference instances
superset-cli https://demo.preset.io export-assets ./raw/preset_demos
```

### Resulting Structure

```
raw/
├── official_samples/
│   ├── databases/
│   ├── datasets/
│   ├── charts/
│   └── dashboards/
├── production/
│   ├── databases/
│   ├── datasets/
│   ├── charts/
│   └── dashboards/
└── preset_demos/
    ├── databases/
    ├── datasets/
    ├── charts/
    └── dashboards/
```

---

## 2. Decompose into Component Library

### Curate Best Components

Review exported charts and select the best examples of each pattern:

| Pattern | Description | Keep Best Example |
|---------|-------------|-------------------|
| Time Series | Line/area over time | `revenue_trend.yaml` |
| Top-N Bar | Ranked bar chart | `top_products.yaml` |
| Heatmap | 2D color matrix | `activity_heatmap.yaml` |
| Funnel | Conversion funnel | `sales_funnel.yaml` |
| Big Number | KPI card | `total_revenue.yaml` |
| Pie/Donut | Part-to-whole | `category_split.yaml` |
| Table | Data table | `transactions_table.yaml` |
| Map | Geographic viz | `sales_by_region.yaml` |

### Normalize into Library Structure

```bash
mkdir -p superset_library/{databases,datasets,charts/{time_series,top_n,heatmaps,funnels,kpi,tables,maps},dashboards/templates}
```

```
superset_library/
├── databases/
│   └── analytics_db.yaml.j2
├── datasets/
│   ├── sales_data.yaml.j2
│   └── user_events.yaml.j2
├── charts/
│   ├── time_series/
│   │   ├── line_trend.yaml.j2
│   │   └── area_stacked.yaml.j2
│   ├── top_n/
│   │   ├── bar_horizontal.yaml.j2
│   │   └── bar_vertical.yaml.j2
│   ├── heatmaps/
│   │   └── calendar_heatmap.yaml.j2
│   ├── funnels/
│   │   └── conversion_funnel.yaml.j2
│   ├── kpi/
│   │   ├── big_number.yaml.j2
│   │   └── big_number_trend.yaml.j2
│   ├── tables/
│   │   └── data_table.yaml.j2
│   └── maps/
│       └── choropleth.yaml.j2
├── dashboards/
│   └── templates/
│       ├── executive_summary.yaml.j2
│       └── operational_overview.yaml.j2
└── use_cases/
    ├── retail/
    ├── saas/
    └── finance/
```

---

## 3. Templatize with Jinja2

### Chart Template: Time Series

```yaml
# charts/time_series/line_trend.yaml.j2
slice_name: "{{ chart_title | default('Trend Over Time') }}"
viz_type: line
datasource_type: table
datasource_id: {{ datasource_id }}

params:
  # Time configuration
  time_grain_sqla: "{{ time_grain | default('P1D') }}"
  granularity_sqla: "{{ time_column | default('ds') }}"

  # Metrics
  metrics:
    {% for metric in metrics %}
    - {{ metric }}
    {% endfor %}

  # Grouping (optional)
  {% if group_by %}
  groupby:
    {% for dim in group_by %}
    - {{ dim }}
    {% endfor %}
  {% endif %}

  # Filters
  adhoc_filters:
    {% for filter in filters | default([]) %}
    - clause: WHERE
      subject: "{{ filter.column }}"
      operator: "{{ filter.operator | default('==') }}"
      comparator: "{{ filter.value }}"
      expressionType: SIMPLE
    {% endfor %}

  # Styling
  color_scheme: "{{ color_scheme | default('supersetColors') }}"
  show_legend: {{ show_legend | default(true) | lower }}
  rich_tooltip: true
  line_interpolation: linear

  # Time range
  time_range: "{{ time_range | default('Last 30 days') }}"
```

### Chart Template: Top-N Bar

```yaml
# charts/top_n/bar_horizontal.yaml.j2
slice_name: "{{ chart_title | default('Top Items') }}"
viz_type: echarts_bar
datasource_type: table
datasource_id: {{ datasource_id }}

params:
  # Metric
  metrics:
    - {{ metric }}

  # Dimension
  groupby:
    - {{ dimension }}

  # Limit
  row_limit: {{ limit | default(10) }}
  order_desc: {{ order_desc | default(true) | lower }}

  # Orientation
  orientation: horizontal

  # Filters
  adhoc_filters:
    {% for filter in filters | default([]) %}
    - clause: WHERE
      subject: "{{ filter.column }}"
      operator: "{{ filter.operator | default('==') }}"
      comparator: "{{ filter.value }}"
      expressionType: SIMPLE
    {% endfor %}

  # Styling
  color_scheme: "{{ color_scheme | default('supersetColors') }}"
  show_legend: false
  show_value: {{ show_values | default(true) | lower }}
```

### Chart Template: KPI Big Number

```yaml
# charts/kpi/big_number_trend.yaml.j2
slice_name: "{{ chart_title | default('KPI') }}"
viz_type: big_number
datasource_type: table
datasource_id: {{ datasource_id }}

params:
  metric: {{ metric }}
  granularity_sqla: "{{ time_column | default('ds') }}"
  time_range: "{{ time_range | default('Last 7 days') }}"

  # Comparison
  compare_lag: {{ compare_lag | default(7) }}
  compare_suffix: "{{ compare_suffix | default('w/w') }}"

  # Formatting
  y_axis_format: "{{ format | default('SMART_NUMBER') }}"
  {% if prefix %}
  metric_format_prefix: "{{ prefix }}"
  {% endif %}
  {% if suffix %}
  metric_format_suffix: "{{ suffix }}"
  {% endif %}

  # Styling
  header_font_size: {{ header_font_size | default(0.4) }}
  subheader_font_size: {{ subheader_font_size | default(0.15) }}
```

### Dataset Template

```yaml
# datasets/generic_dataset.yaml.j2
table_name: {{ table_name }}
schema: {{ schema | default('public') }}
database_uuid: {{ database_uuid }}

description: |
  {{ description | default('Auto-generated dataset') }}
  Generated: {{ now().strftime('%Y-%m-%d') }}

columns:
  {% for col in columns %}
  - column_name: {{ col.name }}
    type: {{ col.type | default('VARCHAR') }}
    filterable: {{ col.filterable | default(true) | lower }}
    groupby: {{ col.groupby | default(true) | lower }}
    {% if col.is_dttm %}
    is_dttm: true
    {% endif %}
  {% endfor %}

metrics:
  {% for m in metrics %}
  - metric_name: {{ m.name }}
    expression: {{ m.expression }}
    metric_type: {{ m.type | default('') }}
    {% if m.description %}
    description: {{ m.description }}
    {% endif %}
  {% endfor %}
```

### Dashboard Template

```yaml
# dashboards/templates/executive_summary.yaml.j2
dashboard_title: "{{ dashboard_title }}"
slug: "{{ slug | default(dashboard_title | lower | replace(' ', '-')) }}"
published: {{ published | default(false) | lower }}

metadata:
  color_scheme: "{{ color_scheme | default('supersetColors') }}"
  refresh_frequency: {{ refresh_frequency | default(0) }}

  {% if native_filters %}
  native_filter_configuration:
    {% for filter in native_filters %}
    - id: "{{ filter.id }}"
      name: "{{ filter.name }}"
      filterType: "{{ filter.type | default('filter_select') }}"
      targets:
        - datasetId: {{ filter.dataset_id }}
          column:
            name: "{{ filter.column }}"
    {% endfor %}
  {% endif %}

# Chart references (IDs resolved at deploy time)
slices:
  {% for chart in charts %}
  - {{ chart }}
  {% endfor %}

position:
  DASHBOARD_VERSION_KEY: v2
  ROOT_ID:
    type: ROOT
    id: ROOT_ID
    children:
      - GRID_ID
  GRID_ID:
    type: GRID
    id: GRID_ID
    children:
      {% for row in layout %}
      - ROW_{{ loop.index }}
      {% endfor %}
  {% for row in layout %}
  ROW_{{ loop.index }}:
    type: ROW
    id: ROW_{{ loop.index }}
    children:
      {% for chart in row.charts %}
      - CHART_{{ chart.id }}
      {% endfor %}
    meta:
      background: BACKGROUND_TRANSPARENT
  {% for chart in row.charts %}
  CHART_{{ chart.id }}:
    type: CHART
    id: CHART_{{ chart.id }}
    meta:
      sliceName: "{{ chart.name }}"
      width: {{ chart.width | default(4) }}
      height: {{ chart.height | default(50) }}
  {% endfor %}
  {% endfor %}
```

---

## 4. Define Use Cases

### Use Case Config: Retail Revenue

```yaml
# use_cases/retail/revenue_dashboard.yaml
name: Retail Revenue Dashboard
database_uuid: "abc-123-def"
datasource_id: 42

# Dataset config
dataset:
  table_name: sales_transactions
  schema: retail
  columns:
    - name: transaction_date
      type: TIMESTAMP
      is_dttm: true
    - name: product_name
      type: VARCHAR
      filterable: true
    - name: category
      type: VARCHAR
      filterable: true
    - name: revenue
      type: NUMERIC
      groupby: false
  metrics:
    - name: total_revenue
      expression: SUM(revenue)
      type: sum
    - name: order_count
      expression: COUNT(*)
      type: count
    - name: avg_order_value
      expression: AVG(revenue)
      type: avg

# Chart variants
charts:
  - template: charts/time_series/line_trend.yaml.j2
    output: charts/retail_revenue_trend.yaml
    params:
      chart_title: "Revenue Trend"
      time_column: transaction_date
      metrics: [total_revenue]
      time_grain: P1D

  - template: charts/top_n/bar_horizontal.yaml.j2
    output: charts/retail_top_products.yaml
    params:
      chart_title: "Top 10 Products"
      dimension: product_name
      metric: total_revenue
      limit: 10

  - template: charts/top_n/bar_horizontal.yaml.j2
    output: charts/retail_top_categories.yaml
    params:
      chart_title: "Revenue by Category"
      dimension: category
      metric: total_revenue
      limit: 5

  - template: charts/kpi/big_number_trend.yaml.j2
    output: charts/retail_total_revenue_kpi.yaml
    params:
      chart_title: "Total Revenue"
      metric: total_revenue
      time_column: transaction_date
      prefix: "$"
      compare_lag: 7

  - template: charts/kpi/big_number_trend.yaml.j2
    output: charts/retail_order_count_kpi.yaml
    params:
      chart_title: "Orders"
      metric: order_count
      time_column: transaction_date
      compare_lag: 7

# Dashboard config
dashboard:
  template: dashboards/templates/executive_summary.yaml.j2
  output: dashboards/retail_revenue.yaml
  params:
    dashboard_title: "Retail Revenue Dashboard"
    published: true
    charts:
      - retail_total_revenue_kpi
      - retail_order_count_kpi
      - retail_revenue_trend
      - retail_top_products
      - retail_top_categories
    layout:
      - charts:
          - { id: kpi_revenue, name: "Total Revenue", width: 3, height: 30 }
          - { id: kpi_orders, name: "Orders", width: 3, height: 30 }
      - charts:
          - { id: trend, name: "Revenue Trend", width: 6, height: 50 }
      - charts:
          - { id: top_products, name: "Top Products", width: 3, height: 50 }
          - { id: top_categories, name: "Revenue by Category", width: 3, height: 50 }
    native_filters:
      - id: date_filter
        name: Date Range
        type: filter_time
        dataset_id: 42
        column: transaction_date
      - id: category_filter
        name: Category
        type: filter_select
        dataset_id: 42
        column: category
```

---

## 5. Generate from Templates

### Generator Script

```python
#!/usr/bin/env python3
# scripts/generate_dashboard.py
"""Generate Superset assets from use case config."""

import yaml
import os
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)

def render_template(env: Environment, template_path: str, params: dict) -> str:
    template = env.get_template(template_path)
    return template.render(**params)

def generate_assets(config_path: str, output_dir: str = "superset_assets"):
    config = load_config(config_path)
    env = Environment(loader=FileSystemLoader('.'))

    # Create output directories
    output_path = Path(output_dir)
    (output_path / "charts").mkdir(parents=True, exist_ok=True)
    (output_path / "datasets").mkdir(parents=True, exist_ok=True)
    (output_path / "dashboards").mkdir(parents=True, exist_ok=True)

    # Generate dataset if defined
    if 'dataset' in config:
        dataset_params = {
            'database_uuid': config['database_uuid'],
            **config['dataset']
        }
        dataset_yaml = render_template(
            env,
            'superset_library/datasets/generic_dataset.yaml.j2',
            dataset_params
        )
        dataset_output = output_path / "datasets" / f"{config['dataset']['table_name']}.yaml"
        dataset_output.write_text(dataset_yaml)
        print(f"✅ Generated: {dataset_output}")

    # Generate charts
    for chart_config in config.get('charts', []):
        chart_params = {
            'datasource_id': config['datasource_id'],
            **chart_config['params']
        }
        chart_yaml = render_template(env, chart_config['template'], chart_params)
        chart_output = output_path / chart_config['output']
        chart_output.parent.mkdir(parents=True, exist_ok=True)
        chart_output.write_text(chart_yaml)
        print(f"✅ Generated: {chart_output}")

    # Generate dashboard
    if 'dashboard' in config:
        dashboard_params = config['dashboard']['params']
        dashboard_yaml = render_template(
            env,
            config['dashboard']['template'],
            dashboard_params
        )
        dashboard_output = output_path / config['dashboard']['output']
        dashboard_output.parent.mkdir(parents=True, exist_ok=True)
        dashboard_output.write_text(dashboard_yaml)
        print(f"✅ Generated: {dashboard_output}")

    print(f"\n🎉 All assets generated in {output_dir}/")

if __name__ == "__main__":
    import sys
    config_file = sys.argv[1] if len(sys.argv) > 1 else "use_cases/retail/revenue_dashboard.yaml"
    generate_assets(config_file)
```

### Usage

```bash
# Generate assets for a use case
python scripts/generate_dashboard.py use_cases/retail/revenue_dashboard.yaml

# Output:
# ✅ Generated: superset_assets/datasets/sales_transactions.yaml
# ✅ Generated: superset_assets/charts/retail_revenue_trend.yaml
# ✅ Generated: superset_assets/charts/retail_top_products.yaml
# ✅ Generated: superset_assets/charts/retail_top_categories.yaml
# ✅ Generated: superset_assets/charts/retail_total_revenue_kpi.yaml
# ✅ Generated: superset_assets/charts/retail_order_count_kpi.yaml
# ✅ Generated: superset_assets/dashboards/retail_revenue.yaml
```

---

## 6. Deploy via CLI Pipeline

### Makefile

```makefile
# Makefile
SUPERSET_URL ?= https://superset.insightpulseai.net
USE_CASE ?= use_cases/retail/revenue_dashboard.yaml

.PHONY: generate deploy clean

generate:
	python scripts/generate_dashboard.py $(USE_CASE)

deploy: generate
	superset-cli $(SUPERSET_URL) sync native ./superset_assets

clean:
	rm -rf superset_assets/

# Generate multiple use cases
generate-all:
	@for config in use_cases/*/*.yaml; do \
		echo "Generating: $$config"; \
		python scripts/generate_dashboard.py "$$config"; \
	done

deploy-all: generate-all
	superset-cli $(SUPERSET_URL) sync native ./superset_assets
```

### Usage

```bash
# Single use case
make generate USE_CASE=use_cases/retail/revenue_dashboard.yaml
make deploy

# All use cases
make deploy-all
```

---

## 7. CI/CD Integration

```yaml
# .github/workflows/generate-deploy.yml
name: Generate and Deploy Dashboards

on:
  push:
    paths:
      - 'use_cases/**'
      - 'superset_library/**'
  workflow_dispatch:
    inputs:
      use_case:
        description: 'Use case config path'
        required: false

jobs:
  generate-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install jinja2 pyyaml preset-cli

      - name: Generate assets
        run: |
          if [ -n "${{ inputs.use_case }}" ]; then
            python scripts/generate_dashboard.py "${{ inputs.use_case }}"
          else
            make generate-all
          fi

      - name: Deploy to Superset
        env:
          SUPERSET_URL: ${{ secrets.SUPERSET_URL }}
          SUPERSET_ADMIN_USER: ${{ secrets.SUPERSET_ADMIN_USER }}
          SUPERSET_ADMIN_PASS: ${{ secrets.SUPERSET_ADMIN_PASS }}
        run: |
          superset-cli "$SUPERSET_URL" sync native ./superset_assets \
            --username "$SUPERSET_ADMIN_USER" \
            --password "$SUPERSET_ADMIN_PASS"
```

---

## 8. Component Library Summary

### What You Get

| Component | Description |
|-----------|-------------|
| **Chart Templates** | Reusable Jinja2 templates for common viz patterns |
| **Dataset Templates** | Schema-agnostic dataset definitions |
| **Dashboard Templates** | Standard layouts (executive, operational, etc.) |
| **Use Case Configs** | Per-client/domain parameter files |
| **Generator Script** | Render templates → plain YAML |
| **CLI Pipeline** | One-command deploy to any Superset |

### Benefits

- **Zero UI clicks**: Everything is code-driven
- **Reusability**: Same chart pattern, different data sources
- **Consistency**: Standardized look across dashboards
- **Version control**: Full Git history of all changes
- **Multi-tenant**: Same templates, different clients/brands
- **Rapid iteration**: Add use case config → deploy

---

## Quick Start

```bash
# 1. Clone your component library
git clone https://github.com/your-org/superset-components.git
cd superset-components

# 2. Create a new use case
cp use_cases/retail/revenue_dashboard.yaml use_cases/my_client/dashboard.yaml
# Edit with your datasource_id, metrics, dimensions

# 3. Generate and deploy
make deploy USE_CASE=use_cases/my_client/dashboard.yaml

# 4. View in Superset
open https://superset.insightpulseai.net/dashboard/list/
```

# Power BI to Superset Migration Playbook

> Convert Power BI dashboards to Superset using pbi-tools and templated generation

## Overview

This playbook describes how to:
1. **Extract** Power BI PBIX files to JSON using `pbi-tools`
2. **Transform** to a neutral BI spec format
3. **Generate** Superset assets from templates
4. **Deploy** via CLI pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  POWER BI PBIX                                                  │
│  (Microsoft samples, production reports)                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓ pbi-tools extract
┌─────────────────────────────────────────────────────────────────┐
│  RAW JSON                                                       │
│  Model/database.json + Report/Layout                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓ translator script
┌─────────────────────────────────────────────────────────────────┐
│  NEUTRAL BI SPEC                                                │
│  bi-spec/layouts/*.json (platform-agnostic)                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓ powerbi_to_superset.py
┌─────────────────────────────────────────────────────────────────┐
│  SUPERSET YAML                                                  │
│  superset_assets/charts/*.yaml + dashboards/*.yaml              │
└─────────────────────────────────────────────────────────────────┘
                              ↓ superset-cli sync
┌─────────────────────────────────────────────────────────────────┐
│  LIVE SUPERSET DASHBOARD                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Tools Required

```bash
# Superset CLI
pip install preset-cli

# pbi-tools (Windows only, or via Wine/Docker)
# Download from: https://pbi.tools
pbi-tools info  # Verify installation

# Power BI samples
git clone https://github.com/microsoft/powerbi-desktop-samples.git
```

---

## Project Structure

```
powerbi-to-superset/
├── powerbi-desktop-samples/     # Microsoft sample PBIX files
│   └── Sample Reports/
│       └── Customer Profitability Sample.pbix
├── bi-spec/                     # Neutral BI spec (intermediate)
│   └── layouts/
│       └── customer_profitability.json
├── superset-assets-kit/
│   ├── templates/
│   │   ├── charts/
│   │   │   ├── bar_category_metric.yaml.j2
│   │   │   ├── line_timeseries_metric.yaml.j2
│   │   │   ├── big_number_metric.yaml.j2
│   │   │   └── pie_category_metric.yaml.j2
│   │   └── dashboards/
│   │       └── dashboard_grid.yaml.j2
│   ├── generators/
│   │   ├── pbix_to_bispec.py        # PBIX → neutral spec
│   │   └── powerbi_to_superset.py   # neutral spec → Superset YAML
│   └── superset_assets/             # Generated output
│       ├── databases/
│       ├── datasets/
│       ├── charts/
│       └── dashboards/
└── Makefile
```

---

## Step 1: Extract PBIX to JSON

### Using pbi-tools

```bash
cd powerbi-desktop-samples/Sample\ Reports

# Extract PBIX to folder
pbi-tools extract "Customer Profitability Sample.pbix"

# Output structure:
# Customer Profitability Sample/
#   Model/
#     database.json      # Tables, measures, relationships
#   Report/
#     Layout             # Report pages and visuals
```

### Key Files from Extraction

| File | Contains |
|------|----------|
| `Model/database.json` | Tables, columns, DAX measures, relationships |
| `Report/Layout` | Page definitions, visual configs, filters |

---

## Step 2: Define Neutral BI Spec

Create a platform-agnostic intermediate format:

### Example: `bi-spec/layouts/customer_profitability.json`

```json
{
  "dashboard_slug": "customer_profitability",
  "dashboard_title": "Customer Profitability Overview",
  "datasource_id": 42,
  "pages": [
    {
      "name": "Overview",
      "charts": [
        {
          "id": "rev_by_segment",
          "template": "bar_category_metric.yaml.j2",
          "title": "Revenue by Segment",
          "metric_name": "Total Revenue",
          "category_col": "Segment",
          "adhoc_filters": [],
          "row": 0,
          "col": 0,
          "width": 6,
          "height": 3
        },
        {
          "id": "rev_by_customer",
          "template": "bar_category_metric.yaml.j2",
          "title": "Revenue by Customer",
          "metric_name": "Total Revenue",
          "category_col": "Customer",
          "adhoc_filters": [],
          "row": 0,
          "col": 6,
          "width": 6,
          "height": 3
        },
        {
          "id": "rev_over_time",
          "template": "line_timeseries_metric.yaml.j2",
          "title": "Revenue Over Time",
          "metric_name": "Total Revenue",
          "time_col": "order_date",
          "time_grain": "P1M",
          "adhoc_filters": [],
          "row": 3,
          "col": 0,
          "width": 12,
          "height": 3
        }
      ]
    }
  ],
  "model": {
    "tables": [
      {
        "name": "fact_sales",
        "columns": ["order_date", "customer_id", "segment", "revenue"]
      }
    ],
    "measures": [
      {
        "name": "Total Revenue",
        "expression": "SUM(revenue)",
        "dax_original": "CALCULATE(SUM(Sales[Revenue]))"
      }
    ]
  }
}
```

### Visual Type Mapping

| Power BI Visual | Superset viz_type | Template |
|-----------------|-------------------|----------|
| `clusteredColumnChart` | `bar` | `bar_category_metric.yaml.j2` |
| `lineChart` | `line` | `line_timeseries_metric.yaml.j2` |
| `card` | `big_number` | `big_number_metric.yaml.j2` |
| `pieChart` | `pie` | `pie_category_metric.yaml.j2` |
| `table` | `table` | `data_table.yaml.j2` |
| `map` | `deck_geojson` | `map_geo.yaml.j2` |
| `funnel` | `funnel` | `funnel_chart.yaml.j2` |

---

## Step 3: Chart Templates

### Bar Chart Template

```yaml
# templates/charts/bar_category_metric.yaml.j2
slice_name: "{{ title }}"
viz_type: bar
datasource_type: table
datasource_id: {{ datasource_id }}

params:
  metrics:
    - "{{ metric_name }}"
  groupby:
    - "{{ category_col }}"
  adhoc_filters: {{ adhoc_filters | default([]) | tojson }}
  row_limit: {{ row_limit | default(1000) }}
  order_desc: true
  color_scheme: "{{ color_scheme | default('supersetColors') }}"
  show_legend: {{ show_legend | default(true) | lower }}

cache_timeout: null
description: "Migrated from Power BI"
```

### Time Series Template

```yaml
# templates/charts/line_timeseries_metric.yaml.j2
slice_name: "{{ title }}"
viz_type: line
datasource_type: table
datasource_id: {{ datasource_id }}

params:
  x_axis: "{{ time_col }}"
  time_grain_sqla: "{{ time_grain | default('P1D') }}"
  granularity_sqla: "{{ time_col }}"
  metrics:
    - "{{ metric_name }}"
  {% if group_by %}
  groupby:
    {% for dim in group_by %}
    - {{ dim }}
    {% endfor %}
  {% endif %}
  adhoc_filters: {{ adhoc_filters | default([]) | tojson }}
  row_limit: {{ row_limit | default(1000) }}
  time_range: "{{ time_range | default('Last year') }}"
  color_scheme: "{{ color_scheme | default('supersetColors') }}"
  show_legend: true
  rich_tooltip: true

cache_timeout: null
description: "Migrated from Power BI"
```

### KPI Card Template

```yaml
# templates/charts/big_number_metric.yaml.j2
slice_name: "{{ title }}"
viz_type: big_number
datasource_type: table
datasource_id: {{ datasource_id }}

params:
  metric: "{{ metric_name }}"
  {% if time_col %}
  granularity_sqla: "{{ time_col }}"
  time_range: "{{ time_range | default('Last 7 days') }}"
  compare_lag: {{ compare_lag | default(7) }}
  compare_suffix: "{{ compare_suffix | default('w/w') }}"
  {% endif %}
  y_axis_format: "{{ format | default('SMART_NUMBER') }}"
  header_font_size: 0.4
  subheader_font_size: 0.15

cache_timeout: null
description: "Migrated from Power BI"
```

### Dashboard Grid Template

```yaml
# templates/dashboards/dashboard_grid.yaml.j2
dashboard_title: "{{ dashboard_title }}"
slug: "{{ dashboard_slug }}"
published: {{ published | default(false) | lower }}
css: ""
description: "Migrated from Power BI"

metadata:
  native_filter_configuration: []
  timed_refresh_immune_slices: []
  expanded_slices: []
  default_filters: "{}"
  refresh_frequency: 0
  shared_label_colors: {}

position: {{ position | tojson }}
```

---

## Step 4: Generator Script

### `powerbi_to_superset.py`

```python
#!/usr/bin/env python3
"""Generate Superset assets from neutral BI spec."""

import json
from pathlib import Path
from typing import Dict, Any, List

from jinja2 import Environment, FileSystemLoader, StrictUndefined
import yaml


BASE_DIR = Path(__file__).resolve().parents[1]
TEMPLATES_DIR = BASE_DIR / "templates"
BI_SPEC_LAYOUTS_DIR = BASE_DIR.parent / "bi-spec" / "layouts"
OUTPUT_ASSETS_DIR = BASE_DIR / "superset_assets"

CHARTS_OUT_DIR = OUTPUT_ASSETS_DIR / "charts"
DASHBOARDS_OUT_DIR = OUTPUT_ASSETS_DIR / "dashboards"


def make_env() -> Environment:
    """Create Jinja2 environment with custom filters."""
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        undefined=StrictUndefined,
        autoescape=False,
    )
    env.filters["tojson"] = lambda v: yaml.safe_dump(
        v, default_flow_style=True
    ).strip()
    return env


def load_layout_specs() -> List[Dict[str, Any]]:
    """Load all neutral BI spec files."""
    specs: List[Dict[str, Any]] = []
    for path in sorted(BI_SPEC_LAYOUTS_DIR.glob("*.json")):
        with path.open("r", encoding="utf-8") as f:
            specs.append(json.load(f))
    return specs


def render_chart_template(
    env: Environment,
    chart_spec: Dict[str, Any],
    layout_spec: Dict[str, Any],
) -> Path:
    """Render a single chart from spec using referenced template."""
    template_name = f"charts/{chart_spec['template']}"
    template = env.get_template(template_name)

    ctx = {
        "title": chart_spec["title"],
        "metric_name": chart_spec["metric_name"],
        "datasource_id": layout_spec["datasource_id"],
        "category_col": chart_spec.get("category_col"),
        "time_col": chart_spec.get("time_col"),
        "time_grain": chart_spec.get("time_grain"),
        "group_by": chart_spec.get("group_by"),
        "adhoc_filters": chart_spec.get("adhoc_filters", []),
        "row_limit": chart_spec.get("row_limit", 1000),
        "color_scheme": chart_spec.get("color_scheme", "supersetColors"),
        "show_legend": chart_spec.get("show_legend", True),
    }

    rendered = template.render(**ctx)

    dashboard_slug = layout_spec["dashboard_slug"]
    chart_id = chart_spec["id"]
    out_path = CHARTS_OUT_DIR / f"{dashboard_slug}__{chart_id}.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered + "\n", encoding="utf-8")

    return out_path


def build_dashboard_position(layout_spec: Dict[str, Any]) -> Dict[str, Any]:
    """Build Superset dashboard position grid from chart specs."""
    position: Dict[str, Any] = {}

    root_id = "ROOT_ID"
    grid_id = "GRID_ID"

    position[root_id] = {
        "type": "ROOT",
        "id": root_id,
        "children": [grid_id],
    }

    position[grid_id] = {
        "type": "GRID",
        "id": grid_id,
        "children": [],
    }

    # Build rows from chart positions
    row_tracker = {}  # row_num -> list of chart_ids

    for page in layout_spec["pages"]:
        for chart in page["charts"]:
            row_num = chart.get("row", 0)
            if row_num not in row_tracker:
                row_tracker[row_num] = []
            row_tracker[row_num].append(chart)

    # Create row components
    for row_num in sorted(row_tracker.keys()):
        row_id = f"ROW-{row_num}"
        position[row_id] = {
            "type": "ROW",
            "id": row_id,
            "children": [],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        position[grid_id]["children"].append(row_id)

        for chart in sorted(row_tracker[row_num], key=lambda c: c.get("col", 0)):
            chart_id = f"CHART-{chart['id']}"
            position[chart_id] = {
                "type": "CHART",
                "id": chart_id,
                "children": [],
                "meta": {
                    "sliceName": chart["title"],
                    "width": chart.get("width", 6),
                    "height": chart.get("height", 50),
                },
            }
            position[row_id]["children"].append(chart_id)

    return position


def render_dashboard(
    env: Environment,
    layout_spec: Dict[str, Any],
) -> Path:
    """Render dashboard YAML from layout spec."""
    template = env.get_template("dashboards/dashboard_grid.yaml.j2")
    position = build_dashboard_position(layout_spec)

    ctx = {
        "dashboard_title": layout_spec["dashboard_title"],
        "dashboard_slug": layout_spec["dashboard_slug"],
        "position": position,
        "published": layout_spec.get("published", False),
    }

    rendered = template.render(**ctx)

    out_path = DASHBOARDS_OUT_DIR / f"{layout_spec['dashboard_slug']}.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered + "\n", encoding="utf-8")
    return out_path


def main() -> None:
    """Main entry point."""
    env = make_env()
    CHARTS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    DASHBOARDS_OUT_DIR.mkdir(parents=True, exist_ok=True)

    layout_specs = load_layout_specs()
    if not layout_specs:
        print(f"No layout specs found in {BI_SPEC_LAYOUTS_DIR}")
        return

    for layout_spec in layout_specs:
        print(f"[INFO] Processing: {layout_spec['dashboard_slug']}")

        for page in layout_spec["pages"]:
            for chart in page["charts"]:
                chart_path = render_chart_template(env, chart, layout_spec)
                print(f"  ✅ chart: {chart['id']} -> {chart_path.name}")

        dashboard_path = render_dashboard(env, layout_spec)
        print(f"  ✅ dashboard -> {dashboard_path.name}")

    print(f"\n🎉 Assets generated in {OUTPUT_ASSETS_DIR}/")


if __name__ == "__main__":
    main()
```

---

## Step 5: DAX to SQL Translation

### Common DAX → SQL Mappings

| DAX Pattern | SQL Equivalent |
|-------------|----------------|
| `SUM(Sales[Revenue])` | `SUM(revenue)` |
| `COUNT(Orders[ID])` | `COUNT(id)` |
| `AVERAGE(Sales[Price])` | `AVG(price)` |
| `DISTINCTCOUNT(Customers[ID])` | `COUNT(DISTINCT customer_id)` |
| `CALCULATE(SUM(...), Filter)` | `SUM(...) FILTER (WHERE ...)` |
| `DIVIDE(A, B, 0)` | `COALESCE(A / NULLIF(B, 0), 0)` |
| `RELATED(Table[Column])` | JOIN in dataset definition |
| `DATEADD(...)` | `DATE_ADD(...)` or interval arithmetic |

### Dataset with Translated Metrics

```yaml
# superset_assets/datasets/fact_sales.yaml
table_name: fact_sales
schema: analytics
database_uuid: "{{ database_uuid }}"

columns:
  - column_name: order_date
    type: TIMESTAMP
    is_dttm: true
  - column_name: customer_id
    type: INTEGER
    filterable: true
  - column_name: segment
    type: VARCHAR
    filterable: true
    groupby: true
  - column_name: revenue
    type: NUMERIC
    filterable: true
    groupby: false

metrics:
  # DAX: SUM(Sales[Revenue])
  - metric_name: Total Revenue
    expression: SUM(revenue)
    metric_type: sum

  # DAX: DISTINCTCOUNT(Sales[CustomerID])
  - metric_name: Unique Customers
    expression: COUNT(DISTINCT customer_id)
    metric_type: count_distinct

  # DAX: DIVIDE(SUM(Sales[Profit]), SUM(Sales[Revenue]), 0)
  - metric_name: Profit Margin
    expression: COALESCE(SUM(profit) / NULLIF(SUM(revenue), 0), 0)
    metric_type: expression
```

---

## Step 6: Deploy Pipeline

### Makefile

```makefile
# Makefile
SUPERSET_URL ?= https://superset.insightpulseai.net

.PHONY: extract transform generate deploy clean

# Step 1: Extract PBIX (Windows/pbi-tools required)
extract:
	@echo "Run on Windows: pbi-tools extract <file.pbix>"

# Step 2: Generate Superset assets from bi-spec
generate:
	cd superset-assets-kit && python generators/powerbi_to_superset.py

# Step 3: Deploy to Superset
deploy: generate
	superset-cli $(SUPERSET_URL) sync native superset-assets-kit/superset_assets

# Clean generated files
clean:
	rm -rf superset-assets-kit/superset_assets/*

# Full pipeline
all: generate deploy
```

### Usage

```bash
# Generate assets from bi-spec
make generate

# Deploy to Superset
make deploy SUPERSET_URL=https://superset.insightpulseai.net
```

---

## Step 7: CI/CD Integration

```yaml
# .github/workflows/powerbi-to-superset.yml
name: Power BI to Superset Migration

on:
  push:
    paths:
      - 'bi-spec/**'
      - 'superset-assets-kit/templates/**'
  workflow_dispatch:

jobs:
  migrate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install preset-cli jinja2 pyyaml

      - name: Generate Superset assets
        run: |
          cd superset-assets-kit
          python generators/powerbi_to_superset.py

      - name: Deploy to Superset
        env:
          SUPERSET_URL: ${{ secrets.SUPERSET_URL }}
          SUPERSET_ADMIN_USER: ${{ secrets.SUPERSET_ADMIN_USER }}
          SUPERSET_ADMIN_PASS: ${{ secrets.SUPERSET_ADMIN_PASS }}
        run: |
          superset-cli "$SUPERSET_URL" sync native \
            superset-assets-kit/superset_assets \
            --username "$SUPERSET_ADMIN_USER" \
            --password "$SUPERSET_ADMIN_PASS"

      - name: Upload generated assets
        uses: actions/upload-artifact@v4
        with:
          name: superset-assets
          path: superset-assets-kit/superset_assets/
```

---

## Advanced: PBIX Extractor Script

### `pbix_to_bispec.py` (Skeleton)

```python
#!/usr/bin/env python3
"""Extract Power BI PBIX to neutral BI spec format.

Requires pbi-tools output directory as input.
"""

import json
from pathlib import Path
from typing import Dict, Any, List


# Power BI visual type to template mapping
VISUAL_TYPE_MAP = {
    "clusteredColumnChart": "bar_category_metric.yaml.j2",
    "clusteredBarChart": "bar_category_metric.yaml.j2",
    "lineChart": "line_timeseries_metric.yaml.j2",
    "areaChart": "line_timeseries_metric.yaml.j2",
    "card": "big_number_metric.yaml.j2",
    "multiRowCard": "big_number_metric.yaml.j2",
    "pieChart": "pie_category_metric.yaml.j2",
    "donutChart": "pie_category_metric.yaml.j2",
    "tableEx": "data_table.yaml.j2",
    "pivotTable": "pivot_table.yaml.j2",
    "map": "map_geo.yaml.j2",
    "funnel": "funnel_chart.yaml.j2",
}


def extract_visuals(layout_path: Path) -> List[Dict[str, Any]]:
    """Extract visual definitions from Report/Layout."""
    # pbi-tools outputs Layout as a folder with section files
    visuals = []

    for section_file in layout_path.glob("*.json"):
        with section_file.open() as f:
            section = json.load(f)

        for visual in section.get("visualContainers", []):
            config = json.loads(visual.get("config", "{}"))
            visual_type = config.get("singleVisual", {}).get("visualType", "")

            if visual_type in VISUAL_TYPE_MAP:
                visuals.append({
                    "id": visual.get("id", ""),
                    "type": visual_type,
                    "template": VISUAL_TYPE_MAP[visual_type],
                    "title": extract_title(config),
                    "fields": extract_fields(config),
                    "position": extract_position(visual),
                })

    return visuals


def extract_measures(model_path: Path) -> List[Dict[str, Any]]:
    """Extract DAX measures from Model/database.json."""
    db_file = model_path / "database.json"
    if not db_file.exists():
        return []

    with db_file.open() as f:
        model = json.load(f)

    measures = []
    for table in model.get("model", {}).get("tables", []):
        for measure in table.get("measures", []):
            measures.append({
                "name": measure.get("name"),
                "dax": measure.get("expression"),
                "table": table.get("name"),
            })

    return measures


def translate_dax_to_sql(dax: str) -> str:
    """Basic DAX to SQL translation."""
    # Simple pattern matching - extend as needed
    sql = dax
    sql = sql.replace("SUM(", "SUM(")
    sql = sql.replace("COUNT(", "COUNT(")
    sql = sql.replace("AVERAGE(", "AVG(")
    sql = sql.replace("DISTINCTCOUNT(", "COUNT(DISTINCT ")
    # Add more translations...
    return sql


def generate_bispec(
    pbix_extract_dir: Path,
    dashboard_slug: str,
    datasource_id: int,
) -> Dict[str, Any]:
    """Generate neutral BI spec from pbi-tools extraction."""
    model_path = pbix_extract_dir / "Model"
    layout_path = pbix_extract_dir / "Report" / "Layout"

    visuals = extract_visuals(layout_path)
    measures = extract_measures(model_path)

    # Build neutral spec
    spec = {
        "dashboard_slug": dashboard_slug,
        "dashboard_title": dashboard_slug.replace("_", " ").title(),
        "datasource_id": datasource_id,
        "pages": [
            {
                "name": "Main",
                "charts": [
                    {
                        "id": v["id"],
                        "template": v["template"],
                        "title": v["title"],
                        "metric_name": v["fields"].get("metric", ""),
                        "category_col": v["fields"].get("category", ""),
                        "time_col": v["fields"].get("time", ""),
                        "row": v["position"]["row"],
                        "col": v["position"]["col"],
                        "width": v["position"]["width"],
                        "height": v["position"]["height"],
                    }
                    for v in visuals
                ],
            }
        ],
        "model": {
            "measures": [
                {
                    "name": m["name"],
                    "expression": translate_dax_to_sql(m["dax"]),
                    "dax_original": m["dax"],
                }
                for m in measures
            ]
        },
    }

    return spec


# Helper functions (implement based on pbi-tools output structure)
def extract_title(config: Dict) -> str:
    return config.get("singleVisual", {}).get("title", {}).get("text", "Untitled")

def extract_fields(config: Dict) -> Dict[str, str]:
    # Parse prototypeQuery or other field bindings
    return {"metric": "", "category": "", "time": ""}

def extract_position(visual: Dict) -> Dict[str, int]:
    return {"row": 0, "col": 0, "width": 6, "height": 3}
```

---

## Summary

### What You Get

| Artifact | Description |
|----------|-------------|
| **Visual type mapping** | Power BI visuals → Superset chart types |
| **DAX translation guide** | Common DAX → SQL patterns |
| **Neutral BI spec format** | Platform-agnostic layout DSL |
| **Chart templates** | Jinja2 templates for each viz type |
| **Generator script** | bi-spec → Superset YAML |
| **CI/CD workflow** | Automated migration pipeline |

### Migration Workflow

```bash
# 1. Extract PBIX (Windows)
pbi-tools extract "Report.pbix"

# 2. Create/update bi-spec from extraction
python generators/pbix_to_bispec.py Report/ --output bi-spec/layouts/

# 3. Generate Superset assets
python generators/powerbi_to_superset.py

# 4. Deploy
superset-cli https://superset.example.com sync native superset_assets/
```

---

## Advanced: ECharts-First Viz Type Resolution

### Viz Type Discovery Script

Discover available viz types from the running Superset backend:

```bash
# Run inside Superset container
docker compose exec superset python /app/scripts/discover_viz_types.py \
  /app/available_viz_types.json

# Or via kubectl
kubectl exec -it superset-pod -- python /app/scripts/discover_viz_types.py \
  /app/available_viz_types.json
```

**Output (`available_viz_types.json`):**
```json
{
  "count": 45,
  "echarts_count": 15,
  "classic_count": 30,
  "viz_types": ["echarts_bar", "echarts_pie", "echarts_timeseries_line", ...],
  "echarts_types": ["echarts_bar", "echarts_pie", ...],
  "classic_types": ["line", "bar", "pie", ...]
}
```

### Viz Catalog with ECharts-First Fallback

Use `viz_catalog.yaml` to define ECharts preferences with automatic fallback:

```yaml
# viz_catalog.yaml
version: 2
defaults:
  library: echarts
  reference_gallery: "https://echarts.apache.org/examples/en/"

charts:
  line:
    echarts_candidates:
      - "echarts_timeseries_line"
      - "echarts_line"
    superset_fallback:
      - "line"
    template: "echarts_timeseries.yaml.j2"
    requires: ["metric_name", "time_col"]

  bar:
    echarts_candidates:
      - "echarts_bar"
      - "echarts_timeseries_bar"
    superset_fallback:
      - "bar"
    template: "echarts_bar.yaml.j2"
    requires: ["metric_name", "category_col"]

  pie:
    echarts_candidates:
      - "echarts_pie"
    superset_fallback:
      - "pie"
    template: "echarts_pie.yaml.j2"
    requires: ["metric_name", "category_col"]
```

### Viz Type Resolver in Generator

```python
import re
import yaml

def load_available_viz_types():
    """Load discovered viz types from JSON file."""
    avail_path = BASE_DIR / "available_viz_types.json"
    if avail_path.exists():
        data = json.loads(avail_path.read_text())
        return data.get("viz_types", [])
    # Fallback defaults
    return [
        "echarts_timeseries_line", "echarts_bar", "echarts_pie",
        "line", "bar", "pie", "scatter", "heatmap"
    ]

def pick_viz_type(available: list, candidates: list) -> str | None:
    """Pick first matching viz type from candidates."""
    avail_set = set(available)
    # Exact match
    for c in candidates:
        if c in avail_set:
            return c
    # Fuzzy match
    for c in candidates:
        pattern = re.sub(r"[_\-]+", ".*", re.escape(c))
        rx = re.compile(pattern, re.IGNORECASE)
        for a in available:
            if rx.search(a):
                return a
    return None

def resolve_viz_type(kind: str, catalog: dict, available: list) -> str:
    """Resolve viz_type with ECharts-first, fallback to classic."""
    kind_entry = catalog["charts"].get(kind, {})

    # Try ECharts candidates first
    viz = pick_viz_type(available, kind_entry.get("echarts_candidates", []))
    if viz:
        return viz

    # Fallback to classic types
    viz = pick_viz_type(available, kind_entry.get("superset_fallback", []))
    if viz:
        return viz

    # Last resort
    fallbacks = kind_entry.get("superset_fallback", ["line"])
    return fallbacks[0]
```

### Power BI to Superset Visual Mapping

| Power BI Visual | Neutral Kind | ECharts Candidate | Classic Fallback |
|-----------------|--------------|-------------------|------------------|
| `clusteredColumnChart` | `bar` | `echarts_bar` | `bar` |
| `lineChart` | `line` | `echarts_timeseries_line` | `line` |
| `pieChart` | `pie` | `echarts_pie` | `pie` |
| `card` | `kpi` | - | `big_number` |
| `gauge` | `gauge` | `echarts_gauge` | `big_number` |
| `funnel` | `funnel` | `echarts_funnel` | `funnel` |
| `treemap` | `treemap` | `echarts_treemap` | `treemap` |
| `scatterChart` | `scatter` | `echarts_scatter` | `scatter` |

---

## Resources

- [pbi-tools](https://pbi.tools) - PBIX extraction tool
- [Power BI Desktop Samples](https://github.com/microsoft/powerbi-desktop-samples)
- [ECharts Examples Gallery](https://echarts.apache.org/examples/en/) - Canonical chart patterns
- [DAX to SQL Guide](https://docs.microsoft.com/en-us/dax/)
- [preset-cli](https://github.com/preset-io/backend-sdk)

# Sample Data for InsightPulse

This directory contains sample data sets for testing and demonstration purposes.

## Structure

```
sample_data/
├── ops/              # Operations schema sample data
│   ├── task_queue.json
│   ├── workflow_runs.json
│   └── forum_posts.json
├── analytics/        # Analytics schema sample data
│   ├── sales_daily.json
│   ├── customer_ltv.json
│   └── product_performance.json
├── ai/               # AI schema sample data
│   ├── training_runs.json
│   └── embeddings.json
└── odoo_demo/        # Odoo demo company data
    ├── partners.csv
    ├── products.csv
    └── sales_orders.csv
```

## Usage

Install all sample data:
```bash
python3 scripts/db_upgrader.py install-sample-data --schema all
```

Install specific schema:
```bash
python3 scripts/db_upgrader.py install-sample-data --schema ops
python3 scripts/db_upgrader.py install-sample-data --schema analytics
```

## Data Sets

### ops.task_queue
- Sample deployment and build tasks
- Various statuses (pending, processing, completed, failed)
- Linked to sample PR numbers

### ops.workflow_runs
- CI/CD workflow execution history
- Success/failure metrics
- Duration tracking

### analytics.* views
- Populated from Odoo demo data
- Sales KPIs, customer LTV, product performance
- Time-series data for dashboard testing

### ai.training_runs
- Model training metadata
- Embedding generation logs
- Performance metrics

## Generating Custom Sample Data

Use the `generate_sample_data.py` script:

```bash
python3 scripts/generate_sample_data.py --schema ops --rows 100
python3 scripts/generate_sample_data.py --schema analytics --days 365
```

## Resetting Sample Data

To remove all sample data:

```bash
python3 scripts/db_upgrader.py reset-sample-data
```

This will truncate all sample data tables but preserve the schema and migrations.

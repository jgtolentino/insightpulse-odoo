# Superset BI Developer Agent

Natural language → SQL → Superset charts and dashboards for Odoo 19.

## Features

- 🤖 **Natural Language Processing**: Convert questions to SQL queries
- 📊 **Automatic Chart Generation**: Create Superset charts from NL
- 📈 **Dashboard Composition**: Multi-chart dashboards with auto-layout
- 🔍 **Dataset Management**: Register Odoo tables as Superset datasets
- 🎨 **Visual Parity**: Matches Odoo 19 design system

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Superset and Odoo credentials
```

### 2. Run Locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

### 3. Test

```bash
curl -s -X POST http://localhost:8001/agent/run \
  -H 'content-type: application/json' \
  -d '{"query":"Show top 10 expense categories by total amount"}' | jq
```

### 4. Docker

```bash
docker build -t superset-bi-agent:latest .
docker run --rm -p 8001:8001 --env-file .env superset-bi-agent:latest
```

## API Endpoints

### `POST /agent/run`

Execute BI agent: NL → SQL → Chart

**Request**:
```json
{
  "query": "Show monthly expense trends for the last year",
  "dataset_id": 1,
  "create_dashboard": false
}
```

**Response**:
```json
{
  "sql": "SELECT DATE_TRUNC('month', date) AS month, ...",
  "chart_spec": {...},
  "chart_id": 42,
  "chart_url": "https://insightpulseai.net/superset/explore/p/42/"
}
```

### `POST /dataset/create`

Register Odoo table as Superset dataset

**Request**:
```json
{
  "database_id": 1,
  "schema": "public",
  "table_name": "hr_expense"
}
```

### `POST /dashboard/create`

Create multi-chart dashboard

**Request**:
```json
{
  "title": "Expense Analytics",
  "chart_ids": [1, 2, 3]
}
```

### `GET /datasets`

List available datasets

## Integration with Odoo 19

Install the `bi_superset_agent` addon in Odoo 19:

```bash
cp -r addons/bi_superset_agent /opt/bundle/addons/
docker compose restart odoo
```

Then in Odoo:
1. Apps → Update Apps List
2. Search "BI Superset Agent"
3. Install
4. Configure in Settings

## Environment Variables

- `SUPERSET_URL` - Superset instance URL
- `SUPERSET_USERNAME` - Superset admin username
- `SUPERSET_PASSWORD` - Superset admin password
- `DATASET_ID` - Default dataset ID
- `ODOO_DB_URL` - Odoo PostgreSQL connection string
- `OPENAI_API_KEY` - OpenAI API key for NL processing
- `REDIS_URL` - Redis URL for caching

## Architecture

```
User (Odoo 19) → FastAPI Agent → OpenAI (NL→SQL) → Superset API → Chart/Dashboard
                    ↓                                    ↓
                PostgreSQL (Odoo data)            Redis (cache)
```

## Performance

- **NL Processing**: <2s (OpenAI gpt-4o-mini)
- **Chart Creation**: <3s (Superset REST API)
- **Total Response**: <5s for 90th percentile

## License

LGPL-3

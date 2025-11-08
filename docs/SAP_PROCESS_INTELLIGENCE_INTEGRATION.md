# SAP Process Intelligence Integration Guide

Complete end-to-end integration guide for SAP S/4HANA process mining in InsightPulse Odoo platform.

---

## 🚀 Quick Start

### 1. Bootstrap

```bash
# Fetch and check out the SAP PI branch
git fetch origin claude/sap-process-intelligence-skills-011CUv5QmyTPy2kDkz2ATjSM
git checkout -b sap-pi-int origin/claude/sap-process-intelligence-skills-011CUv5QmyTPy2kDkz2ATjSM

# Smoke test the skill pack
make sap-help
make sap-spec-verify
make drawio-validate
make sap-simulate-trace PROCESS_ID=PO_DEMO DATE_RANGE=2025-01-01/2025-01-31
```

### 2. Environment Configuration

Create `.env.sap`:

```bash
cat > .env.sap <<'EOF'
SAP_ODATA_ENDPOINT=https://<sap-host>/sap/opu/odata
SAP_CLIENT=001
SAP_AUTH_MODE=oauth        # oauth|basic
SAP_OAUTH_TOKEN_URL=https://<sap-auth>/oauth/token
SAP_OAUTH_CLIENT_ID=__vault__
SAP_OAUTH_CLIENT_SECRET=__vault__
SAP_BASIC_USER=__vault__
SAP_BASIC_PASS=__vault__
PI_EXPORT_DIR=/opt/insightpulse-odoo/exports/process-intel
EOF

mkdir -p /opt/insightpulse-odoo/exports/process-intel
```

### 3. Start Process Intelligence API

```bash
# Validate configuration
make pi-env

# Start service
make pi-up

# Test health
make pi-test

# Run demo
make pi-demo
```

---

## 📦 What's Included

### Skills Package

- **SAP Process Intelligence** (`skills/integrations/sap-process-intelligence/`)
  - Event extraction from SAP via OData/BAPI
  - Process variant analysis with conformance checking
  - Bottleneck detection (P90 wait time analysis)
  - KPI prediction (throughput, delay, anomaly risk, cost)
  - Process map generation (Mermaid, BPMN, Draw.io, JSON)

- **Draw.io Adapter** (`skills/integrations/drawio-adapter/`)
  - Create diagrams from Mermaid, BPMN, JSON, CSV
  - Validate diagram structure
  - Export to PNG, SVG, PDF
  - URL encoding for diagrams.net sharing
  - Auto-generation from SAP event traces

### Services

- **Process Intelligence API** (`services/process-intel-api/`)
  - FastAPI wrapper around SAP skills
  - Endpoints: `/pi/extract`, `/pi/analyze`, `/pi/predict`, `/pi/diagram`
  - Health check at `/health`
  - Docker containerized

### Odoo Module

- **ipai_process_intel** (`addons/ipai_process_intel/`)
  - Purchase Order P2P analysis buttons
  - Sales Order O2C analysis buttons
  - Process Intelligence tab on PO/SO forms
  - Menu: Process Intelligence → Analytics
  - Configuration settings for API endpoints

### Database Schema

- **Supabase/PostgreSQL** (`sql/process_intelligence_schema.sql`)
  - `pi.events` - Raw SAP event traces
  - `pi.variants` - Process variant analysis
  - `pi.bottlenecks` - Detected bottlenecks
  - `pi.kpi_forecasts` - Predicted KPIs
  - `pi.resource_utilization` - Resource metrics
  - `pi.diagrams` - Generated diagrams
  - Materialized views for Superset

### Superset Dashboard

- **Process Intelligence - SAP Analytics** (`superset/dashboards/process-intelligence.json`)
  - P2P conformance rate trend
  - Top bottlenecks by impact
  - Process variant distribution
  - KPI forecast - Delay risk
  - Resource utilization heatmap
  - Event volume by activity

---

## 🔧 Usage

### Command Line

```bash
# Extract SAP events
make sap-extract PROCESS_ID=PO_4500012345 DATE_RANGE=2025-01-01/2025-01-31

# Analyze process
make sap-analyze

# Generate and export diagram
make drawio-export FILE=diagrams/sap-p2p.drawio FORMAT=png
```

### Python API

```python
from skills.integrations.sap_process_intelligence.sap_executor import SAPProcessIntelligence
from skills.integrations.sap_process_intelligence.models.sap_event_model import *

engine = SAPProcessIntelligence()

# Extract events
events_req = ExtractEventsRequest(
    process_id="PO_4500012345",
    date_range="2025-01-01/2025-01-31",
    process_type="PROCURE_TO_PAY"
)
events_resp = engine.extract_process_events(events_req)

# Analyze variants
variants_req = CorrelateVariantsRequest(events=events_resp.events)
variants_resp = engine.correlate_variants(variants_req)

print(f"Conformance: {variants_resp.variant_summary.conformance_rate:.1f}%")
```

### REST API

```bash
# Extract events
curl -X POST http://localhost:8090/pi/extract \
  -H 'Content-Type: application/json' \
  -d '{
    "process_id": "PO_4500012345",
    "date_range": "2025-01-01/2025-01-31",
    "process_type": "PROCURE_TO_PAY"
  }'

# Analyze
curl -X POST http://localhost:8090/pi/analyze \
  -H 'Content-Type: application/json' \
  -d '{"events": [...]}'

# Generate diagram
curl -X POST http://localhost:8090/pi/diagram \
  -H 'Content-Type: application/json' \
  -d '{
    "process_id": "PO_4500012345",
    "events": [...],
    "output_format": "mermaid"
  }'
```

### Odoo UI

1. Open Purchase Order or Sales Order
2. Click **"Analyze P2P Process"** or **"Analyze O2C Process"** button
3. View results in **Process Intelligence** tab:
   - Conformance rate
   - Top bottleneck
   - Bottleneck wait time
   - Process diagram URL
4. Click **"View Process Diagram"** to open diagram in new tab

### Mattermost ChatOps

```
/agent pi p2p PO_4500012345 2025-01-01/2025-01-31
```

Response:
```
**P2P Process Intelligence**
Process: `PO_4500012345` Range: `2025-01-01/2025-01-31`
- Conformance: 87.5%
- Top bottleneck: Approve Purchase Requisition (4.2h P90)
- Diagram: `/exports/process-intel/sap-PO_4500012345.png`
```

---

## 🗄️ Database Setup

### Initialize Schema

```bash
# Set Supabase connection string
export SUPABASE_DB_URL="postgresql://postgres.xxx:yyy@aws-1-us-east-1.pooler.supabase.com:6543/postgres?sslmode=require"

# Run schema migration
make pi-db-setup
```

### Refresh Views (for Superset)

```bash
# Manual refresh
make pi-db-refresh

# Or setup cron job (daily at 2 AM)
0 2 * * * cd /opt/insightpulse-odoo && make pi-db-refresh
```

---

## 📊 Superset Dashboard

### Import Dashboard

1. Open Superset
2. Go to **Dashboards → Import**
3. Upload `superset/dashboards/process-intelligence.json`
4. Connect to Supabase database
5. Verify charts load

### Available Charts

- **P2P Conformance Rate Trend** - Line chart showing conformance over time
- **Top Bottlenecks by Impact** - Table of highest-impact bottlenecks
- **Process Variant Distribution** - Pie chart of variant types
- **KPI Forecast - Delay Risk** - Big number showing predicted delays
- **Resource Utilization Heatmap** - Heatmap of resource usage
- **Event Volume by Activity** - Bar chart of event distribution

---

## 🔐 Security

### SAP Bot User Setup

1. Create dedicated bot user in SAP
2. Grant read-only access to OData entities:
   - Purchase Orders
   - Sales Orders
   - Material Documents
   - Accounting Documents
3. Limit to specific company codes/plants if needed
4. Enable OAuth (recommended) or basic auth
5. IP allowlist for production

### Secrets Management

**DO NOT** commit secrets to git. Use:

- **Local development**: `.env.sap` (gitignored)
- **Production**: GitHub Secrets or HashiCorp Vault
- **Docker**: env_file or secrets mount

### Data Privacy

- Process diagrams stored locally in `PI_EXPORT_DIR`
- No third-party uploads
- PII redaction before persistence (if needed)
- SOC2-compliant local quantized models

---

## 🧪 Testing

### Unit Tests

```bash
# Run SAP PI tests
make sap-test

# Run specific test
pytest tests/test_sap_process_intelligence.py::test_variant_analysis -v
```

### Simulation Mode

```bash
# Test without SAP connection
make sap-simulate-trace PROCESS_ID=PO_TEST DATE_RANGE=2025-01-01/2025-01-07
```

### Integration Test

```bash
# Full stack test
make pi-up
make pi-test
make pi-demo
make pi-down
```

---

## 🔄 CI/CD

### GitHub Actions

Workflow: `.github/workflows/sap-spec-validate.yml`

**Runs on:**
- Push to SAP PI skill paths
- Pull requests

**Steps:**
1. Validate Pydantic models
2. Run unit tests
3. Generate OpenAPI spec
4. Verify spec freshness
5. Validate Draw.io diagrams

### Pre-merge Checklist

- [ ] `/health` endpoint green
- [ ] `make sap-spec-verify` passes
- [ ] `make drawio-validate` passes
- [ ] `make sap-simulate-trace` works
- [ ] Unit tests pass
- [ ] Odoo module installs without errors

---

## 📈 Monitoring

### OpenTelemetry Tracing

All `/pi/*` endpoints emit spans:

```python
with tracer.start_as_current_span("pi.extract"):
    # ... extraction logic
```

**Trace attributes:**
- `pi.process_id`
- `pi.process_type`
- `pi.date_range`
- `pi.event_count`

### Health Checks

```bash
# API health
curl http://localhost:8090/health

# Service status
make pi-status

# Docker logs
docker compose -f docker-compose.pi.yml logs -f
```

---

## 🐛 Troubleshooting

### API not starting

```bash
# Check logs
docker compose -f docker-compose.pi.yml logs process-intel-api

# Common issues:
# 1. .env.sap not found → run: make pi-env
# 2. Port 8090 in use → change PORT in .env.sap
# 3. Skills path not mounted → check docker-compose.pi.yml volumes
```

### SAP connection failed

```bash
# Test SAP connectivity
curl -v https://<sap-host>/sap/opu/odata

# Check credentials in .env.sap
# Verify SAP bot user has OData access
# Check firewall/IP allowlist
```

### Diagram export fails

```bash
# Install Draw.io CLI (optional)
brew install --cask drawio  # macOS
# or
apt-get install draw.io     # Linux

# Set path in .env.sap
DRAWIO_CLI_PATH=/usr/local/bin/drawio
```

---

## 📚 Documentation

- **Skills**: `skills/integrations/sap-process-intelligence/SKILL.md`
- **Draw.io Adapter**: `skills/integrations/drawio-adapter/SKILL.md`
- **Agent**: `.superclaude/agents/sap-executor-agent.yml`
- **Models**: `skills/integrations/sap-process-intelligence/models/sap_event_model.py`
- **API**: http://localhost:8090/docs (OpenAPI/Swagger UI)

---

## 🗺️ Roadmap

### v0.2.0 (Q2 2025)
- Real-time event streaming via SAP Event Mesh
- Advanced conformance checking with Petri nets
- Multi-tenant support for SaaS deployments
- GPU-accelerated variant mining

### v0.3.0 (Q3 2025)
- Integration with SAP Signavio Process Manager
- Predictive process simulation
- Automated RPA bot generation for deviations
- Natural language query interface

---

## 📞 Support

- **Documentation**: See files above
- **Issues**: Create GitHub issue in main repo
- **Contact**: InsightPulse AI Team

---

## 📝 License

Copyright © 2025 InsightPulse AI. All rights reserved.

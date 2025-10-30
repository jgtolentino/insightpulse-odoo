# InsightPulse Monitor MCP Server

Enterprise-grade Model Context Protocol (MCP) server for real-time monitoring of Odoo, Supabase, and Finance SSC operations with BIR compliance tracking.

## Features

### 🏥 System Health Monitoring
- **Odoo ERP**: Database health, response times, service status
- **Supabase**: API connectivity, database performance
- **Infrastructure**: DigitalOcean services monitoring

### 📋 BIR Compliance Tracking
- **Filing Deadlines**: Track upcoming BIR filing deadlines (1601-C, 1702-RT, 2550M, 2550Q)
- **Multi-Agency Support**: Monitor 8 agencies (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- **Smart Alerts**: Automatic flagging of due-soon and overdue filings

### 📊 Operations Monitoring
- **Month-End Closing**: Real-time task status, completion tracking, blocker identification
- **Background Jobs**: Failed job monitoring (PaddleOCR, email, webhooks)
- **Error Tracking**: Stack trace retrieval, context analysis

### ✅ Compliance Status
- **ATP Validity**: Authorization to Print tracking by agency
- **Certificate Monitoring**: SSL/TLS certificate expiration alerts
- **Regulatory Compliance**: BIR registration, DOLE requirements

### 📈 Performance Analytics
- **Database Performance**: Slow query detection, lock contention analysis
- **Agency KPIs**: Financial, operational, and compliance metrics
- **Trend Analysis**: Month-over-month and year-over-year comparisons

## Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/jgtolentino/insightpulse-odoo.git
cd insightpulse-odoo/services/insightpulse-monitor
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Run with Docker Compose**
```bash
docker-compose up --build
```

4. **Test the server**
```bash
curl http://localhost:8000/health
```

### Production Deployment (DigitalOcean)

1. **Set up secrets in GitHub**
   - `DO_ACCESS_TOKEN`: DigitalOcean API token
   - `DO_MONITOR_APP_ID`: App Platform app ID
   - `DOCKERHUB_USERNAME`: DockerHub username
   - `DOCKERHUB_TOKEN`: DockerHub token
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_SERVICE_KEY`: Supabase service role key
   - `ODOO_URL`: Your Odoo instance URL
   - `ODOO_API_KEY`: Odoo API key

2. **Deploy via GitHub Actions**
   - Push to `main` branch
   - Or manually trigger via Actions tab

3. **Monitor deployment**
   - Check GitHub Actions for deployment status
   - Verify health at `https://your-app.ondigitalocean.app/health`

## MCP Tools Reference

### System Monitoring

#### `get_system_health`
Check health of all infrastructure components.

**Returns:**
```json
{
  "timestamp": "2025-10-30T12:00:00Z",
  "overall_status": "healthy",
  "services": {
    "odoo": {
      "status": "healthy",
      "response_time_ms": 234,
      "database": "postgres"
    },
    "supabase": {
      "status": "healthy",
      "response_time_ms": 123,
      "project": "your-project"
    }
  }
}
```

#### `track_bir_filing_deadlines`
Monitor upcoming BIR filing deadlines.

**Parameters:**
- `agency_code` (optional): Filter by specific agency
- `months_ahead` (default: 3): How many months to look ahead

**Returns:**
```json
[
  {
    "agency": "RIM",
    "form": "1601-C",
    "description": "Monthly Withholding Tax",
    "deadline": "2025-11-10T00:00:00",
    "days_until": 11,
    "status": "upcoming"
  }
]
```

#### `get_month_end_status`
Get real-time status of month-end closing tasks.

**Parameters:**
- `month` (optional): YYYY-MM format (default: current month)
- `agency_code` (optional): Filter by specific agency

**Returns:**
```json
{
  "month": "2025-10",
  "total_tasks": 45,
  "by_status": {
    "pending": 10,
    "in_progress": 15,
    "completed": 18,
    "blocked": 2
  },
  "by_agency": {
    "RIM": {"total": 8, "completed": 6}
  },
  "critical_blockers": [],
  "completion_percentage": 40.0
}
```

### Operational Monitoring

#### `list_failed_jobs`
List failed background jobs.

**Parameters:**
- `hours` (default: 24): Look back this many hours
- `job_type` (optional): Filter by type (paddleocr, email, webhook, export)

**Returns:**
```json
[
  {
    "job_id": "uuid",
    "job_type": "paddleocr",
    "job_name": "Invoice OCR Processing",
    "failure_reason": "Connection timeout",
    "failed_at": "2025-10-30T11:30:00Z",
    "retry_count": 2,
    "max_retries": 3,
    "can_retry": true
  }
]
```

#### `get_error_traces`
Retrieve stack traces from service logs.

**Parameters:**
- `service`: Which service (odoo, supabase, api)
- `limit` (default: 10): Maximum errors to return
- `since_hours` (default: 24): Look back this many hours

#### `check_database_performance`
Check for slow queries and performance issues.

**Returns:**
```json
{
  "timestamp": "2025-10-30T12:00:00Z",
  "slow_queries": [],
  "recommendations": [
    {
      "query": "SELECT * FROM...",
      "recommendation": "Consider adding an index",
      "reason": "Called 500 times with avg 1500ms"
    }
  ]
}
```

### Compliance Monitoring

#### `monitor_compliance_status`
Monitor ATP validity and compliance status.

**Parameters:**
- `agency_code` (optional): Filter by specific agency

**Returns:**
```json
{
  "timestamp": "2025-10-30T12:00:00Z",
  "overall_status": "compliant",
  "agencies": {
    "RIM": {
      "atp_valid": true,
      "bir_registered": true,
      "dole_compliant": true,
      "expiring_soon": []
    }
  }
}
```

### Analytics

#### `get_agency_metrics`
Get KPIs and metrics by agency.

**Parameters:**
- `agency_code`: Agency code (RIM, CKVC, BOM, JPAL, JLI, JAP, LAS, RMQB)
- `metric_type` (default: "all"): Type of metrics (financial, operational, compliance, all)

**Returns:**
```json
{
  "agency": "RIM",
  "period": "2025-10",
  "financial": {
    "revenue": 5000000,
    "expenses": 3000000,
    "profit_margin": 40.0,
    "budget_variance": -5.2
  },
  "operational": {
    "tasks_completed": 234,
    "sla_adherence": 98.5,
    "avg_resolution_time": 2.3,
    "employee_count": 45
  },
  "compliance": {
    "bir_filings_on_time": 100,
    "dole_compliant": true,
    "audit_findings": 0
  },
  "trends": {
    "revenue_change_pct": 12.5,
    "efficiency_change_pct": 8.2
  }
}
```

## Architecture

```
┌─────────────────────────────────────────────┐
│   GitHub Actions CI/CD Pipeline             │
│   ├─ Validate Code                          │
│   ├─ Build Docker Image                     │
│   ├─ Deploy to DigitalOcean                 │
│   └─ Verify Deployment                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   DigitalOcean App Platform                 │
│   ├─ Auto-scaling (basic-xxs)               │
│   ├─ Health monitoring                      │
│   ├─ Zero-downtime deployment               │
│   └─ SSL/TLS termination                    │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│   InsightPulse Monitor MCP Server           │
│   ├─ FastMCP Framework                      │
│   ├─ 9 Monitoring Tools                     │
│   └─ Health Check Endpoints                 │
└─────────────────────────────────────────────┘
         ↓              ↓              ↓
┌───────────────┐ ┌──────────┐ ┌─────────────┐
│  Odoo ERP     │ │ Supabase │ │ DigitalOcean│
│  - Database   │ │ - DB     │ │ - Infra     │
│  - API        │ │ - API    │ │ - Metrics   │
└───────────────┘ └──────────┘ └─────────────┘
```

## Database Schema Requirements

The MCP server expects the following Supabase tables:

### `month_end_tasks`
```sql
CREATE TABLE month_end_tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  month TEXT NOT NULL,
  agency TEXT NOT NULL,
  name TEXT NOT NULL,
  status TEXT CHECK (status IN ('pending', 'in_progress', 'completed', 'blocked')),
  assigned_to TEXT,
  block_reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `background_jobs`
```sql
CREATE TABLE background_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_type TEXT NOT NULL,
  name TEXT NOT NULL,
  status TEXT CHECK (status IN ('pending', 'running', 'completed', 'failed')),
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  max_retries INTEGER DEFAULT 3,
  next_retry_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `error_logs`
```sql
CREATE TABLE error_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  service TEXT NOT NULL,
  error_message TEXT NOT NULL,
  stack_trace TEXT,
  context JSONB,
  timestamp TIMESTAMPTZ DEFAULT NOW()
);
```

### `compliance_tracking`
```sql
CREATE TABLE compliance_tracking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agency TEXT NOT NULL,
  compliance_type TEXT NOT NULL,
  expiry_date DATE,
  status TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### `agency_metrics`
```sql
CREATE TABLE agency_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agency TEXT NOT NULL,
  period TEXT NOT NULL,
  revenue DECIMAL,
  expenses DECIMAL,
  profit_margin DECIMAL,
  budget_variance DECIMAL,
  tasks_completed INTEGER,
  sla_adherence DECIMAL,
  avg_resolution_time DECIMAL,
  employee_count INTEGER,
  bir_filings_on_time INTEGER,
  dole_compliant BOOLEAN,
  audit_findings INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## CI/CD Pipeline

### Automatic Deployment
The server automatically deploys on push to `main` branch when:
- Changes are made to `services/insightpulse-monitor/**`
- Changes are made to the workflow file

### Manual Deployment
Trigger via GitHub Actions:
1. Go to Actions tab
2. Select "InsightPulse Monitor - Deploy"
3. Click "Run workflow"
4. Choose branch and force rebuild option

### Deployment Steps
1. **Validate**: Code linting, type checking, YAML validation
2. **Build**: Docker image build and push to DockerHub
3. **Deploy**: Update app spec, create deployment, wait for completion
4. **Verify**: Health checks, MCP endpoint tests

## Monitoring

### Health Endpoint
```bash
curl https://your-app.ondigitalocean.app/health
```

### Logs
View logs in DigitalOcean dashboard or via doctl:
```bash
doctl apps logs $DO_MONITOR_APP_ID --type run --follow
```

### Metrics
Monitor via DigitalOcean App Platform dashboard:
- Request count
- Response times
- Error rates
- Resource usage

## Security

- All secrets managed via GitHub Secrets
- Environment variables injected at runtime
- Service role keys for Supabase (full access)
- HTTPS only (enforced by App Platform)
- OAuth support ready (see OAuth setup below)

## OAuth Setup (Optional)

To add OAuth authentication to your MCP server:

1. **Register OAuth application**
   - DigitalOcean: https://cloud.digitalocean.com/account/api/applications
   - Set redirect URI: `https://your-app.ondigitalocean.app/oauth/callback`

2. **Add environment variables**
   ```yaml
   - key: OAUTH_CLIENT_ID
     scope: RUN_TIME
     type: SECRET

   - key: OAUTH_CLIENT_SECRET
     scope: RUN_TIME
     type: SECRET
   ```

3. **Implement OAuth flow** (example in `oauth_example.py`)

## Troubleshooting

### Health check fails
- Check Supabase credentials
- Verify Odoo URL is accessible
- Review app logs for errors

### Deployment timeout
- Check if tables exist in Supabase
- Verify environment variables are set
- Review build logs for errors

### MCP tools not responding
- Ensure database schema is created
- Check Supabase RLS policies
- Verify service role key has correct permissions

## Support

For issues or questions:
- GitHub Issues: https://github.com/jgtolentino/insightpulse-odoo/issues
- Documentation: https://docs.insightpulseai.net

## License

MIT License - see LICENSE file for details

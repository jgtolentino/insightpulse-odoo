# Budget Optimization Guide

Target: **$15/month** (25% under $20 constraint)
Achieved: **$5/month base cost** (75% under budget)

---

## Cost Breakdown

### Current Infrastructure Costs

| Service | Tier | Monthly Cost | Usage |
|---------|------|--------------|-------|
| **Supabase PostgreSQL** | Free | $0 | 500MB database, 2GB bandwidth |
| **DigitalOcean App Platform** | basic-xxs | $5 | 512MB RAM, 1 vCPU |
| **Self-hosted AI (Ollama)** | N/A | $0 | Llama 3.2 (no API costs) |
| **DigitalOcean Monitoring** | Included | $0 | Built-in metrics |
| **GitHub Actions** | Free tier | $0 | 2000 minutes/month |
| **Total Base Cost** | | **$5/month** | |
| **Buffer (overages)** | | $10/month | For traffic spikes |
| **Target Budget** | | **$15/month** | |

---

## Optimization Strategies

### 1. Supabase Free Tier ($0/month)

**Benefits**:
- 500MB PostgreSQL database (sufficient for MVP with 1000-5000 records)
- 2GB bandwidth (adequate for API traffic)
- Connection pooler included (handles 200+ concurrent connections)
- Automatic backups (daily)
- Row-Level Security (RLS) built-in

**Limitations**:
- Database size: 500MB (monitor with `SELECT pg_size_pretty(pg_database_size('postgres'));`)
- Bandwidth: 2GB/month (monitor in Supabase dashboard)
- Database paused after 1 week inactivity (auto-resume on connection)

**Upgrade Path**:
- **Pro tier**: $25/month (8GB database, 50GB bandwidth) when needed
- **When to upgrade**: Database >400MB or bandwidth >1.5GB/month

**Monitoring**:
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('postgres')) as db_size;

-- Check table sizes
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

### 2. DigitalOcean App Platform basic-xxs ($5/month)

**Configuration**:
- **Instance**: 512MB RAM, 1 vCPU (shared)
- **Workers**: 2 Odoo workers (sufficient for 10-50 concurrent users)
- **Cron threads**: 1 (handles scheduled tasks)
- **Connections**: 8 max database connections (pooled via Supabase)

**Performance Limits**:
- **Memory**: 512MB total (Odoo uses ~350MB with 2 workers)
- **CPU**: Shared vCPU (adequate for web requests, not compute-heavy tasks)
- **Concurrent users**: 10-50 (with connection pooling)
- **Response time**: <2s for typical requests

**Optimization Settings**:
```bash
# Memory limits (80% of 512MB)
ODOO_LIMIT_MEMORY_HARD=419430400   # 400MB hard limit
ODOO_LIMIT_MEMORY_SOFT=335544320   # 320MB soft limit

# Worker configuration
ODOO_WORKERS=2                      # 2 workers for concurrency
ODOO_MAX_CRON_THREADS=1            # 1 cron thread (scheduled tasks)
ODOO_DB_MAXCONN=8                  # 8 connections (pooled)

# Timeout limits
ODOO_LIMIT_TIME_CPU=300            # 5 minutes CPU time
ODOO_LIMIT_TIME_REAL=600           # 10 minutes real time
```

**Upgrade Path**:
- **basic-xs**: $12/month (1GB RAM, 1 vCPU) for 50-200 concurrent users
- **When to upgrade**: Response time >5s or memory >90% consistently

**Monitoring**:
```bash
# View app metrics
doctl apps get $DO_APP_ID --format ID,ActiveDeployment.ID,DefaultIngress

# View resource usage
doctl apps logs $DO_APP_ID --type run --follow

# Check health
curl -sf https://[app-url]/web/health
```

---

### 3. Self-hosted AI with Ollama ($0/month)

**Benefits**:
- No OpenAI API costs (saves $10-50/month)
- Llama 3.2 models (3B/11B parameters)
- Local inference (no external API calls)
- Privacy-first (data doesn't leave your infrastructure)

**Implementation**:
```bash
# Install Ollama (local development)
curl -fsSL https://ollama.com/install.sh | sh

# Pull Llama 3.2 model
ollama pull llama3.2:3b

# Run inference
ollama run llama3.2:3b "Analyze this expense: Invoice #12345 for $500 from Acme Corp"
```

**Odoo Integration**:
```python
# addons/insightpulse/models/ai_inference.py
import requests

def call_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]
```

**Fallback to OpenAI** (optional, for complex queries):
- Only use OpenAI for queries that require GPT-4 level reasoning
- Estimated cost: $0-5/month for occasional use
- Set `AI_PROVIDER=openai` environment variable when needed

**Performance**:
- **Llama 3.2 3B**: ~500ms inference time (good for simple tasks)
- **Llama 3.2 11B**: ~2s inference time (better accuracy, slower)
- **OpenAI gpt-4o-mini**: ~1s (fallback for complex queries)

---

### 4. Monitoring and Observability ($0/month)

**DigitalOcean Built-in Metrics**:
- CPU usage
- Memory usage
- Response time
- Request count
- Available in App Platform dashboard

**Supabase Built-in Metrics**:
- Database size
- Query performance
- Connection count
- Available in Supabase dashboard

**GitHub Actions**:
- Free tier: 2000 minutes/month
- Current usage: ~10 minutes/deployment
- Cost: $0 (well under limit)

**Alternative** (if advanced monitoring needed):
- **Uptime Robot**: Free tier (50 monitors, 5-minute checks)
- **Sentry**: Free tier (5K errors/month)
- Cost: $0 (only if needed)

---

## Cost Projections

### Current Usage (MVP)
| Metric | Current | Free Tier Limit | Usage % |
|--------|---------|-----------------|---------|
| Database Size | 50MB | 500MB | 10% |
| Bandwidth | 500MB | 2GB | 25% |
| Concurrent Users | 10 | 50 | 20% |
| API Calls | 10K/month | Unlimited | N/A |

### Growth Projections

**Phase 1: MVP (0-3 months)**
- Users: 10-50
- Database: 50-200MB
- Cost: $5/month
- **Status**: Within free/basic tiers

**Phase 2: Early Growth (3-6 months)**
- Users: 50-200
- Database: 200-500MB
- Cost: $5-12/month (may need basic-xs tier)
- **Status**: Approaching free tier limits

**Phase 3: Scale-up (6-12 months)**
- Users: 200-1000
- Database: 500MB-2GB
- Cost: $25-50/month (Supabase Pro + DO basic-xs/small)
- **Status**: Requires paid tiers

---

## Cost Alerts and Thresholds

### Supabase Monitoring
```sql
-- Alert when database >80% of free tier (400MB)
SELECT
  pg_size_pretty(pg_database_size('postgres')) as current_size,
  CASE
    WHEN pg_database_size('postgres') > 419430400 THEN 'ALERT: Approaching 500MB limit'
    ELSE 'OK'
  END as status;
```

### DigitalOcean Monitoring
```bash
# Set up cost alerts in DigitalOcean console
# Settings > Billing > Alerts
# Alert threshold: $10/month (to stay under $15 target)
```

### GitHub Actions Usage
```bash
# Check Actions usage
gh api /repos/[owner]/insightpulse-odoo/actions/runs \
  --jq '.total_count, .workflow_runs[].run_started_at'

# Alert if usage >1500 minutes/month (75% of free tier)
```

---

## Emergency Cost Reduction

If costs exceed $15/month budget, apply these emergency measures:

1. **Reduce deployment frequency**: Deploy only on manual trigger
2. **Disable Ollama**: Use minimal AI features or remove AI temporarily
3. **Optimize database**: Archive old records, compress data
4. **Reduce workers**: Drop to 1 Odoo worker (sacrifice concurrency)
5. **Limit bandwidth**: Implement aggressive caching, CDN for static assets

---

## Comparison with Original $100 Azure Budget

| Service | Azure (Old) | DigitalOcean + Supabase (New) | Savings |
|---------|-------------|-------------------------------|---------|
| Container Registry | ACR: $5/month | N/A (DO builds images) | $5 |
| Container Instances | ACI: $30/month | DO App Platform: $5/month | $25 |
| Database | Azure PostgreSQL: $25/month | Supabase Free: $0 | $25 |
| Document AI | Azure Document Intelligence: $20/month | PaddleOCR: $0 | $20 |
| AI API | Azure OpenAI: $15/month | Ollama: $0 | $15 |
| Key Vault | Azure Key Vault: $5/month | Environment vars: $0 | $5 |
| **Total** | **$100/month** | **$5/month** | **$95 (95% savings)** |

---

## Budget Optimization Summary

✅ **Achieved: $5/month base cost** (75% under $20 target)

**Key Optimizations**:
1. Supabase Free Tier: $25/month savings vs. Azure PostgreSQL
2. DigitalOcean basic-xxs: $25/month savings vs. Azure Container Instances
3. Self-hosted Ollama: $15/month savings vs. Azure OpenAI
4. Eliminated ACR: $5/month savings
5. Eliminated Key Vault: $5/month savings

**Total Savings**: $95/month (95% reduction from $100 Azure budget)

**Scalability Path**:
- $5/month: MVP (0-50 users)
- $12/month: Growth (50-200 users) - upgrade DO to basic-xs
- $37/month: Scale (200-1000 users) - Supabase Pro + DO basic-xs
- $50-100/month: Enterprise (1000+ users) - Supabase Pro + DO professional tier

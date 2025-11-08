# MINIMUM VIABLE AUTOMATION INFRASTRUCTURE
## Production-Ready Baseline for InsightPulse AI

**Version:** 1.0
**Date:** 2025-11-08
**Purpose:** Define the non-negotiable automation required for production readiness

---

## TABLE OF CONTENTS

1. [Automation Primitives](#automation-primitives)
2. [Edge Functions](#edge-functions)
3. [Cron Jobs](#cron-jobs)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Self-Healing](#self-healing)
7. [Implementation Roadmap](#implementation-roadmap)

---

## AUTOMATION PRIMITIVES

### Decision Matrix: What to Automate

```yaml
Priority_P0_Critical:
  description: "System doesn't work without these"
  examples:
    - Database backups
    - Health checks
    - Security patches
    - SSL renewal
  consequence_if_missing: "Data loss, security breach, downtime"
  must_implement: YES

Priority_P1_High:
  description: "Manual workarounds possible but painful"
  examples:
    - Deployment automation
    - Test execution
    - Log aggregation
    - Monitoring alerts
  consequence_if_missing: "Slow releases, bugs in production, blind spots"
  must_implement: HIGHLY_RECOMMENDED

Priority_P2_Medium:
  description: "Quality of life improvements"
  examples:
    - Auto-scaling
    - Performance optimization
    - Cost optimization
    - Advanced analytics
  consequence_if_missing: "Higher costs, slower performance"
  must_implement: OPTIONAL

Priority_P3_Nice_To_Have:
  description: "Can be added later"
  examples:
    - AI-powered anomaly detection
    - Predictive scaling
    - Self-optimizing queries
  consequence_if_missing: "Miss optimization opportunities"
  must_implement: FUTURE
```

---

## EDGE FUNCTIONS

### What Are Edge Functions?

Edge functions run at Cloudflare's global network (150+ locations), providing:
- **Ultra-low latency** (<50ms globally)
- **Global availability** (multi-region by default)
- **Zero server management** (serverless)
- **Cost-effective** (pay per request, not per server)

### Use Cases for InsightPulse AI

#### 1. Webhook Receiver

**Purpose:** Accept webhooks from external services (banks, expense apps, BIR portal)

**File:** `cloudflare-workers/webhook-receiver.js`

```javascript
// ============================================
// WEBHOOK RECEIVER EDGE FUNCTION
// ============================================
// Receives webhooks from external services and queues for processing
// Deployed at: https://webhooks.insightpulseai.net

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  // Only accept POST requests
  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 })
  }

  const url = new URL(request.url)
  const webhookType = url.pathname.split('/')[1]  // e.g., /bank, /expense, /bir

  // Parse payload
  let payload
  try {
    payload = await request.json()
  } catch (e) {
    return new Response('Invalid JSON', { status: 400 })
  }

  // Validate webhook signature (HMAC)
  const signature = request.headers.get('X-Webhook-Signature')
  const isValid = await validateSignature(payload, signature, webhookType)

  if (!isValid) {
    return new Response('Invalid signature', { status: 401 })
  }

  // Queue for async processing (don't block webhook response)
  await queueEvent({
    type: webhookType,
    data: payload,
    timestamp: Date.now(),
    source: request.headers.get('User-Agent')
  })

  // Respond immediately (< 100ms)
  return new Response(JSON.stringify({
    status: 'queued',
    id: generateUUID()
  }), {
    status: 202,
    headers: { 'Content-Type': 'application/json' }
  })
}

async function validateSignature(payload, signature, webhookType) {
  // Get secret from environment
  const secret = await WEBHOOK_SECRETS.get(webhookType)

  if (!secret) {
    console.error(`No secret configured for webhook type: ${webhookType}`)
    return false
  }

  // Compute HMAC-SHA256
  const encoder = new TextEncoder()
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  )

  const signatureBuffer = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(JSON.stringify(payload))
  )

  const expectedSignature = btoa(String.fromCharCode(...new Uint8Array(signatureBuffer)))

  return signature === expectedSignature
}

async function queueEvent(event) {
  // Send to backend queue (Redis or database)
  await fetch('https://api.insightpulseai.net/internal/queue/add', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_SECRET}`
    },
    body: JSON.stringify(event)
  })
}

function generateUUID() {
  return crypto.randomUUID()
}
```

**Deployment:**
```bash
# Install Wrangler (Cloudflare Workers CLI)
npm install -g wrangler

# Deploy
wrangler publish cloudflare-workers/webhook-receiver.js

# Set secrets
wrangler secret put WEBHOOK_SECRET_BANK
wrangler secret put WEBHOOK_SECRET_EXPENSE
wrangler secret put API_SECRET
```

#### 2. API Gateway (Rate Limiting + Auth)

**Purpose:** Protect backend APIs from abuse, add authentication layer

**File:** `cloudflare-workers/api-gateway.js`

```javascript
// ============================================
// API GATEWAY EDGE FUNCTION
// ============================================
// Rate limiting, authentication, request transformation

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request))
})

const RATE_LIMITS = {
  'free': 100,      // 100 requests/minute
  'paid': 1000,     // 1000 requests/minute
  'enterprise': -1  // Unlimited
}

async function handleRequest(request) {
  const url = new URL(request.url)

  // 1. Rate limiting
  const clientIP = request.headers.get('CF-Connecting-IP')
  const rateLimitResult = await checkRateLimit(clientIP)

  if (!rateLimitResult.allowed) {
    return new Response('Too many requests', {
      status: 429,
      headers: {
        'Retry-After': rateLimitResult.retryAfter.toString(),
        'X-RateLimit-Limit': rateLimitResult.limit.toString(),
        'X-RateLimit-Remaining': '0'
      }
    })
  }

  // 2. Authentication
  const authHeader = request.headers.get('Authorization')
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return new Response('Unauthorized', { status: 401 })
  }

  const token = authHeader.substring(7)
  const authResult = await validateToken(token)

  if (!authResult.valid) {
    return new Response('Invalid token', { status: 401 })
  }

  // 3. Forward to origin with user context
  const modifiedRequest = new Request(request)
  modifiedRequest.headers.set('X-User-ID', authResult.userId)
  modifiedRequest.headers.set('X-User-Plan', authResult.plan)

  // 4. Proxy to backend
  const response = await fetch(`https://api.insightpulseai.net${url.pathname}${url.search}`, modifiedRequest)

  // 5. Add rate limit headers to response
  const modifiedResponse = new Response(response.body, response)
  modifiedResponse.headers.set('X-RateLimit-Limit', RATE_LIMITS[authResult.plan].toString())
  modifiedResponse.headers.set('X-RateLimit-Remaining', rateLimitResult.remaining.toString())

  return modifiedResponse
}

async function checkRateLimit(clientIP) {
  const key = `ratelimit:${clientIP}`
  const now = Math.floor(Date.now() / 1000 / 60)  // Current minute

  // Get current count from KV storage
  const count = await RATE_LIMIT_KV.get(`${key}:${now}`) || 0
  const limit = 100  // Default limit

  if (count >= limit) {
    return {
      allowed: false,
      retryAfter: 60 - (Math.floor(Date.now() / 1000) % 60),
      limit,
      remaining: 0
    }
  }

  // Increment counter
  await RATE_LIMIT_KV.put(`${key}:${now}`, (parseInt(count) + 1).toString(), {
    expirationTtl: 120  // Expire after 2 minutes
  })

  return {
    allowed: true,
    limit,
    remaining: limit - count - 1
  }
}

async function validateToken(token) {
  // JWT validation (simplified - use proper JWT library in production)
  try {
    const response = await fetch('https://api.insightpulseai.net/auth/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    })

    if (!response.ok) {
      return { valid: false }
    }

    const data = await response.json()
    return {
      valid: true,
      userId: data.user_id,
      plan: data.plan
    }
  } catch (e) {
    console.error('Token validation error:', e)
    return { valid: false }
  }
}
```

#### 3. Multi-Region Health Check

**Purpose:** Monitor service health from multiple global locations

**File:** `cloudflare-workers/health-check.js`

```javascript
// ============================================
// MULTI-REGION HEALTH CHECK
// ============================================
// Monitors critical services from Cloudflare edge locations

addEventListener('scheduled', event => {
  event.waitUntil(runHealthChecks())
})

const SERVICES = [
  { name: 'Odoo', url: 'https://erp.insightpulseai.net/web/health' },
  { name: 'API', url: 'https://api.insightpulseai.net/health' },
  { name: 'Superset', url: 'https://superset.insightpulseai.net/health' },
  { name: 'OCR', url: 'https://ocr.insightpulseai.net/health' },
  { name: 'MCP', url: 'https://mcp.insightpulseai.net/health' }
]

async function runHealthChecks() {
  const results = await Promise.allSettled(
    SERVICES.map(service => checkService(service))
  )

  const unhealthy = []

  results.forEach((result, index) => {
    if (result.status === 'rejected' || !result.value.healthy) {
      unhealthy.push({
        service: SERVICES[index].name,
        error: result.reason || result.value.error
      })
    }
  })

  if (unhealthy.length > 0) {
    await alertUnh healthy(unhealthy)
  }

  // Log results to analytics
  await logHealthCheckResults(results)
}

async function checkService(service) {
  const startTime = Date.now()

  try {
    const response = await fetch(service.url, {
      method: 'GET',
      headers: { 'User-Agent': 'InsightPulse-HealthCheck/1.0' },
      timeout: 5000  // 5 second timeout
    })

    const latency = Date.now() - startTime

    if (!response.ok) {
      return {
        healthy: false,
        error: `HTTP ${response.status}`,
        latency
      }
    }

    return {
      healthy: true,
      latency
    }
  } catch (e) {
    return {
      healthy: false,
      error: e.message,
      latency: Date.now() - startTime
    }
  }
}

async function alertUnhealthy(unhealthy) {
  // Send to Slack
  await fetch(SLACK_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      text: '🚨 Services Unhealthy',
      blocks: [
        {
          type: 'section',
          text: {
            type: 'mrkdwn',
            text: `*Unhealthy Services:*\n${unhealthy.map(s => `- ${s.service}: ${s.error}`).join('\n')}`
          }
        }
      ]
    })
  })

  // Send to PagerDuty (for critical services)
  const criticalServices = ['Odoo', 'API']
  const criticalUnhealthy = unhealthy.filter(s => criticalServices.includes(s.service))

  if (criticalUnhealthy.length > 0) {
    await fetch('https://events.pagerduty.com/v2/enqueue', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        routing_key: PAGERDUTY_ROUTING_KEY,
        event_action: 'trigger',
        payload: {
          summary: `Critical services unhealthy: ${criticalUnhealthy.map(s => s.service).join(', ')}`,
          severity: 'critical',
          source: 'healthcheck-edge',
          custom_details: unhealthy
        }
      })
    })
  }
}

async function logHealthCheckResults(results) {
  // Send to analytics/time-series database
  await fetch('https://api.insightpulseai.net/internal/metrics/healthcheck', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_SECRET}`
    },
    body: JSON.stringify({
      timestamp: Date.now(),
      results: results.map((r, i) => ({
        service: SERVICES[i].name,
        healthy: r.status === 'fulfilled' && r.value.healthy,
        latency: r.value?.latency
      }))
    })
  })
}
```

**Cron Trigger:**
```toml
# wrangler.toml
[triggers]
crons = ["*/5 * * * *"]  # Every 5 minutes
```

### Edge Functions Summary

```yaml
Minimum_Edge_Functions_Required: 3
  webhook_receiver:
    purpose: "Accept webhooks from external services"
    latency: "< 50ms"
    cost: "~$0.50/million requests"

  api_gateway:
    purpose: "Rate limiting, authentication"
    latency: "< 30ms overhead"
    cost: "~$0.50/million requests"

  health_checker:
    purpose: "Multi-region service monitoring"
    frequency: "Every 5 minutes"
    cost: "~$5/month"

Total_Edge_Cost: "< $10/month for 1M requests"
```

---

## CRON JOBS

### Essential Scheduled Tasks

#### P0: Critical (Cannot Ship Without)

##### 1. Database Backups

**File:** `automation/cron/backup_postgres.py`

```python
#!/usr/bin/env python3
"""
P0 CRITICAL: Daily PostgreSQL backups

Frequency: 2 AM daily
Consequence if missed: CATASTROPHIC DATA LOSS
Retention: 30 days daily, then monthly for 1 year
"""

import os
import subprocess
from datetime import datetime
import boto3  # For DigitalOcean Spaces (S3-compatible)

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
BACKUP_BUCKET = "insightpulse-backups"
DATABASES = ["odoo_prod", "agents_state", "analytics"]

def backup_database(db_name):
    """Backup a single database."""
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_file = f"/tmp/{db_name}_{timestamp}.sql.gz"

    print(f"Backing up {db_name}...")

    # pg_dump with compression
    env = os.environ.copy()
    env["PGPASSWORD"] = POSTGRES_PASSWORD

    result = subprocess.run([
        "pg_dump",
        "-h", POSTGRES_HOST,
        "-U", POSTGRES_USER,
        "-d", db_name,
        "-Fc",  # Custom format (compressed)
        "-f", backup_file
    ], env=env, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"pg_dump failed: {result.stderr}")

    # Upload to DigitalOcean Spaces
    s3 = boto3.client('s3',
        endpoint_url='https://sgp1.digitaloceanspaces.com',
        aws_access_key_id=os.getenv("SPACES_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SPACES_SECRET_KEY")
    )

    s3.upload_file(
        backup_file,
        BACKUP_BUCKET,
        f"{db_name}/{timestamp}.sql.gz"
    )

    # Verify backup integrity
    result = subprocess.run([
        "pg_restore",
        "--list",
        backup_file
    ], capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Backup verification failed: {result.stderr}")

    # Delete local file
    os.remove(backup_file)

    print(f"✅ {db_name} backed up successfully")

    return f"{db_name}/{timestamp}.sql.gz"

def cleanup_old_backups():
    """Delete backups older than retention policy."""
    s3 = boto3.client('s3',
        endpoint_url='https://sgp1.digitaloceanspaces.com',
        aws_access_key_id=os.getenv("SPACES_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SPACES_SECRET_KEY")
    )

    # Retention: 30 days
    cutoff = datetime.utcnow().timestamp() - (30 * 24 * 60 * 60)

    for db in DATABASES:
        response = s3.list_objects_v2(
            Bucket=BACKUP_BUCKET,
            Prefix=f"{db}/"
        )

        if 'Contents' not in response:
            continue

        for obj in response['Contents']:
            if obj['LastModified'].timestamp() < cutoff:
                print(f"Deleting old backup: {obj['Key']}")
                s3.delete_object(Bucket=BACKUP_BUCKET, Key=obj['Key'])

def test_restore(backup_key):
    """Test backup restoration on staging (weekly)."""
    if datetime.utcnow().weekday() != 0:  # Only on Mondays
        return

    print("Testing backup restoration...")

    s3 = boto3.client('s3',
        endpoint_url='https://sgp1.digitaloceanspaces.com',
        aws_access_key_id=os.getenv("SPACES_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SPACES_SECRET_KEY")
    )

    # Download backup
    backup_file = "/tmp/test_restore.sql.gz"
    s3.download_file(BACKUP_BUCKET, backup_key, backup_file)

    # Restore to test database
    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("POSTGRES_PASSWORD_STAGING")

    result = subprocess.run([
        "pg_restore",
        "-h", os.getenv("POSTGRES_HOST_STAGING"),
        "-U", os.getenv("POSTGRES_USER_STAGING"),
        "-d", "test_restore",
        "--clean",
        "--if-exists",
        backup_file
    ], env=env, capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(f"Restore test failed: {result.stderr}")

    os.remove(backup_file)

    print("✅ Backup restoration test passed")

if __name__ == "__main__":
    try:
        for db in DATABASES:
            backup_key = backup_database(db)

        cleanup_old_backups()

        # Test restore (weekly)
        if datetime.utcnow().weekday() == 0:
            test_restore(backup_key)

        print("\n✅ All backups completed successfully")

    except Exception as e:
        print(f"\n❌ Backup failed: {e}")

        # Alert on-call
        import requests
        requests.post(os.getenv("SLACK_WEBHOOK_URL"), json={
            "text": f"🚨 Database backup failed: {e}"
        })

        exit(1)
```

**Crontab entry:**
```cron
0 2 * * * /usr/bin/python3 /opt/insightpulse/automation/cron/backup_postgres.py >> /var/log/backup.log 2>&1
```

##### 2. Health Check (Every 5 Minutes)

**File:** `automation/cron/health_check.py`

```python
#!/usr/bin/env python3
"""
P0 CRITICAL: Monitor critical services

Frequency: Every 5 minutes
Consequence if missed: Undetected outages
"""

import asyncio
import aiohttp
import asyncpg
import redis.asyncio as redis
from datetime import datetime

SERVICES = {
    "odoo": "https://erp.insightpulseai.net/web/health",
    "api": "https://api.insightpulseai.net/health",
    "superset": "https://superset.insightpulseai.net/health",
    "ocr": "https://ocr.insightpulseai.net/health",
    "mcp": "https://mcp.insightpulseai.net/health"
}

async def check_http_service(session, name, url):
    """Check HTTP service health."""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
            if response.status == 200:
                return {"service": name, "status": "healthy"}
            else:
                return {"service": name, "status": "unhealthy", "error": f"HTTP {response.status}"}
    except Exception as e:
        return {"service": name, "status": "unhealthy", "error": str(e)}

async def check_postgres():
    """Check PostgreSQL health."""
    try:
        conn = await asyncpg.connect(
            host=os.getenv("POSTGRES_HOST"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            database="odoo_prod",
            timeout=5
        )
        result = await conn.fetchval("SELECT 1")
        await conn.close()

        if result == 1:
            return {"service": "postgres", "status": "healthy"}
        else:
            return {"service": "postgres", "status": "unhealthy", "error": "Query failed"}
    except Exception as e:
        return {"service": "postgres", "status": "unhealthy", "error": str(e)}

async def check_redis():
    """Check Redis health."""
    try:
        r = redis.from_url(os.getenv("REDIS_URL"))
        pong = await r.ping()
        await r.close()

        if pong:
            return {"service": "redis", "status": "healthy"}
        else:
            return {"service": "redis", "status": "unhealthy", "error": "Ping failed"}
    except Exception as e:
        return {"service": "redis", "status": "unhealthy", "error": str(e)}

async def alert_unhealthy(unhealthy_services):
    """Send alerts for unhealthy services."""
    message = f"🚨 Unhealthy services detected:\n"
    for service in unhealthy_services:
        message += f"- {service['service']}: {service.get('error', 'Unknown error')}\n"

    # Slack alert
    async with aiohttp.ClientSession() as session:
        await session.post(
            os.getenv("SLACK_WEBHOOK_URL"),
            json={"text": message}
        )

    # PagerDuty (for critical services)
    critical_services = ["odoo", "postgres"]
    critical_unhealthy = [s for s in unhealthy_services if s['service'] in critical_services]

    if critical_unhealthy:
        async with aiohttp.ClientSession() as session:
            await session.post(
                "https://events.pagerduty.com/v2/enqueue",
                json={
                    "routing_key": os.getenv("PAGERDUTY_ROUTING_KEY"),
                    "event_action": "trigger",
                    "payload": {
                        "summary": f"Critical services unhealthy: {', '.join(s['service'] for s in critical_unhealthy)}",
                        "severity": "critical",
                        "source": "healthcheck-cron"
                    }
                }
            )

async def main():
    results = []

    async with aiohttp.ClientSession() as session:
        # Check HTTP services
        http_checks = [check_http_service(session, name, url) for name, url in SERVICES.items()]
        results.extend(await asyncio.gather(*http_checks))

    # Check databases
    results.append(await check_postgres())
    results.append(await check_redis())

    # Filter unhealthy
    unhealthy = [r for r in results if r['status'] != 'healthy']

    if unhealthy:
        print(f"❌ {len(unhealthy)} unhealthy services:")
        for service in unhealthy:
            print(f"  - {service['service']}: {service.get('error')}")

        await alert_unhealthy(unhealthy)
    else:
        print(f"✅ All services healthy at {datetime.utcnow().isoformat()}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Crontab entry:**
```cron
*/5 * * * * /usr/bin/python3 /opt/insightpulse/automation/cron/health_check.py >> /var/log/healthcheck.log 2>&1
```

##### 3. SSL Certificate Renewal

**File:** `automation/cron/renew_ssl.sh`

```bash
#!/bin/bash
# P0 CRITICAL: Auto-renew SSL certificates
# Frequency: Daily check (certbot handles 30-day window)
# Consequence if missed: Site goes offline when cert expires

set -e

echo "Checking SSL certificate expiry..."

# Check certificate expiry for all domains
DOMAINS=("insightpulseai.net" "*.insightpulseai.net")

for DOMAIN in "${DOMAINS[@]}"; do
    CERT_INFO=$(certbot certificates -d "$DOMAIN" 2>&1)

    # Extract expiry date
    EXPIRY_DATE=$(echo "$CERT_INFO" | grep "Expiry Date:" | awk '{print $3, $4}')

    if [ -z "$EXPIRY_DATE" ]; then
        echo "⚠️ No certificate found for $DOMAIN"
        continue
    fi

    # Calculate days until expiry
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
    NOW_EPOCH=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_EPOCH - $NOW_EPOCH) / 86400 ))

    echo "$DOMAIN expires in $DAYS_UNTIL_EXPIRY days"

    # Renew if < 30 days
    if [ $DAYS_UNTIL_EXPIRY -lt 30 ]; then
        echo "Renewing certificate for $DOMAIN..."

        certbot renew \
            --nginx \
            --non-interactive \
            --agree-tos

        # Reload nginx
        systemctl reload nginx

        echo "✅ Certificate renewed for $DOMAIN"

        # Alert Slack
        curl -X POST "$SLACK_WEBHOOK_URL" \
            -H 'Content-Type: application/json' \
            -d "{\"text\": \"✅ SSL certificate renewed for $DOMAIN (was expiring in $DAYS_UNTIL_EXPIRY days)\"}"
    fi
done

echo "✅ SSL certificate check completed"
```

**Crontab entry:**
```cron
0 1 * * * /opt/insightpulse/automation/cron/renew_ssl.sh >> /var/log/ssl_renewal.log 2>&1
```

### Cron Jobs Summary

```yaml
Minimum_Cron_Jobs_Required: 6

P0_Critical:
  backup_postgres:
    frequency: "Daily at 2 AM"
    duration: "~10 minutes"
    consequence_if_failed: "DATA LOSS"

  health_check:
    frequency: "Every 5 minutes"
    duration: "< 30 seconds"
    consequence_if_failed: "Undetected outages"

  renew_ssl:
    frequency: "Daily at 1 AM"
    duration: "< 2 minutes"
    consequence_if_failed: "Site goes offline"

P1_High:
  cleanup_temp_files:
    frequency: "Daily at 3 AM"
    duration: "~5 minutes"
    consequence_if_failed: "Disk fills up"

  process_queued_jobs:
    frequency: "Every 15 minutes"
    duration: "Variable"
    consequence_if_failed: "Jobs pile up"

  optimize_database:
    frequency: "Weekly (Sunday midnight)"
    duration: "~30 minutes"
    consequence_if_failed: "Degraded performance"

Total_Cron_Overhead: "< 2 hours/week"
```

---

## CI/CD PIPELINE

### Minimum Viable Pipeline

**File:** `.github/workflows/production_deploy.yml`

```yaml
name: Production Deployment

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  DOCKER_REGISTRY: registry.digitalocean.com/insightpulse
  DEPLOY_HOST: erp.insightpulseai.net

jobs:
  # ==========================================
  # STAGE 1: VALIDATE (< 2 minutes)
  # ==========================================

  validate:
    runs-on: ubuntu-latest
    timeout-minutes: 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install linting tools
        run: |
          pip install ruff bandit

      - name: Lint code
        run: |
          ruff check . --output-format=github

      - name: Security scan
        run: |
          bandit -r . -f json -o bandit-report.json || true

          # Fail if high severity issues found
          HIGH_SEVERITY=$(jq '[.results[] | select(.issue_severity == "HIGH")] | length' bandit-report.json)
          if [ "$HIGH_SEVERITY" -gt 0 ]; then
            echo "❌ $HIGH_SEVERITY high-severity security issues found"
            jq '.results[] | select(.issue_severity == "HIGH")' bandit-report.json
            exit 1
          fi

      - name: Secrets scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD

  # ==========================================
  # STAGE 2: TEST (< 10 minutes)
  # ==========================================

  test:
    runs-on: ubuntu-latest
    needs: validate
    timeout-minutes: 15

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/unit/ \
            --cov=agents \
            --cov=workflows \
            --cov-report=xml \
            --cov-report=term \
            --cov-fail-under=80 \
            -v

      - name: Run integration tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379
        run: |
          pytest tests/integration/ \
            --maxfail=5 \
            --timeout=300 \
            -v

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  # ==========================================
  # STAGE 3: BUILD (< 5 minutes)
  # ==========================================

  build:
    runs-on: ubuntu-latest
    needs: test
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to DigitalOcean Container Registry
        uses: docker/login-action@v3
        with:
          registry: registry.digitalocean.com
          username: ${{ secrets.DO_REGISTRY_TOKEN }}
          password: ${{ secrets.DO_REGISTRY_TOKEN }}

      - name: Build Docker image
        uses: docker/build-push-action@v5
        with:
          context: .
          push: false
          load: true
          tags: |
            ${{ env.DOCKER_REGISTRY }}/odoo:${{ github.sha }}
            ${{ env.DOCKER_REGISTRY }}/odoo:latest
          cache-from: type=registry,ref=${{ env.DOCKER_REGISTRY }}/odoo:latest
          cache-to: type=inline

      - name: Scan image for vulnerabilities
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.DOCKER_REGISTRY }}/odoo:${{ github.sha }}
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'HIGH,CRITICAL'
          exit-code: '1'  # Fail on vulnerabilities

      - name: Push Docker image
        run: |
          docker push ${{ env.DOCKER_REGISTRY }}/odoo:${{ github.sha }}
          docker push ${{ env.DOCKER_REGISTRY }}/odoo:latest

  # ==========================================
  # STAGE 4: DEPLOY (< 5 minutes)
  # ==========================================

  deploy:
    runs-on: ubuntu-latest
    needs: build
    environment: production
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ env.DEPLOY_HOST }}
          username: deploy
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            # Pull latest image
            docker pull ${{ env.DOCKER_REGISTRY }}/odoo:${{ github.sha }}

            # Rolling update (zero downtime)
            docker service update \
              --image ${{ env.DOCKER_REGISTRY }}/odoo:${{ github.sha }} \
              --update-parallelism 1 \
              --update-delay 30s \
              --update-monitor 60s \
              --rollback-monitor 120s \
              --rollback-parallelism 1 \
              --rollback-delay 30s \
              odoo_web

            echo "✅ Deployment initiated"

      - name: Wait for deployment
        run: sleep 90

      - name: Smoke tests
        run: |
          # Test critical endpoints
          curl -f https://erp.insightpulseai.net/web/health || exit 1
          curl -f https://api.insightpulseai.net/health || exit 1

          echo "✅ Smoke tests passed"

      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "✅ Production deployed: ${{ github.sha }}",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Deployment Complete*\n\nCommit: <https://github.com/${{ github.repository }}/commit/${{ github.sha }}|${{ github.sha }}>\nDeployed by: ${{ github.actor }}"
                  }
                }
              ]
            }

  # ==========================================
  # STAGE 5: ROLLBACK (If deploy fails)
  # ==========================================

  rollback:
    runs-on: ubuntu-latest
    needs: deploy
    if: failure()
    timeout-minutes: 5

    steps:
      - name: Rollback deployment
        uses: appleboy/ssh-action@master
        with:
          host: ${{ env.DEPLOY_HOST }}
          username: deploy
          key: ${{ secrets.DEPLOY_SSH_KEY }}
          script: |
            echo "🔄 Rolling back deployment..."

            # Rollback to previous version
            docker service rollback odoo_web

            # Wait for rollback
            sleep 60

            # Verify rollback
            curl -f https://erp.insightpulseai.net/web/health || exit 1

            echo "✅ Rollback complete"

      - name: Alert on-call
        run: |
          curl -X POST https://events.pagerduty.com/v2/enqueue \
            -H 'Content-Type: application/json' \
            -d '{
              "routing_key": "${{ secrets.PAGERDUTY_ROUTING_KEY }}",
              "event_action": "trigger",
              "payload": {
                "summary": "Production deployment failed and rolled back",
                "severity": "critical",
                "source": "GitHub Actions",
                "custom_details": {
                  "commit": "${{ github.sha }}",
                  "actor": "${{ github.actor }}",
                  "run_url": "${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}"
                }
              }
            }'
```

### CI/CD Summary

```yaml
Pipeline_Stages: 5
  1_Validate: "< 2 minutes"
  2_Test: "< 10 minutes"
  3_Build: "< 5 minutes"
  4_Deploy: "< 5 minutes"
  5_Rollback: "< 2 minutes (if needed)"

Total_Pipeline_Time: "< 25 minutes"

Success_Criteria:
  - All tests pass (>= 80% coverage)
  - No HIGH/CRITICAL vulnerabilities
  - No hardcoded secrets
  - Smoke tests pass
  - Zero downtime deployment

Rollback_Triggers:
  - Deployment failure
  - Health check failure after 90 seconds
  - Smoke test failure
```

---

## IMPLEMENTATION ROADMAP

### Week 1: Essential Infrastructure

**Hours:** 16 hours
**Team:** DevOps Engineer

```yaml
Day_1_2:
  - Set up DigitalOcean Spaces for backups
  - Create backup script (backup_postgres.py)
  - Test backup restoration
  - Configure daily cron job

Day_3:
  - Deploy health check script
  - Configure 5-minute cron job
  - Set up Slack webhook for alerts

Day_4:
  - Configure SSL auto-renewal
  - Test renewal process
  - Set up daily cron job

Day_5:
  - Review and test all cron jobs
  - Document procedures
  - Create runbook

Deliverables:
  ✅ Automated daily backups
  ✅ Health monitoring every 5 minutes
  ✅ SSL auto-renewal
  ✅ Alert notifications
```

### Week 2: CI/CD Pipeline

**Hours:** 24 hours
**Team:** DevOps + Full-stack Engineer

```yaml
Day_1_2:
  - Create GitHub Actions workflow
  - Set up test environment
  - Configure secrets

Day_3:
  - Implement validation stage (lint, security scan)
  - Implement test stage (unit, integration)
  - Add coverage reporting

Day_4:
  - Implement build stage (Docker build, vulnerability scan)
  - Set up DigitalOcean Container Registry
  - Test image build

Day_5:
  - Implement deploy stage (SSH, rolling update)
  - Implement rollback stage
  - Test end-to-end pipeline

Deliverables:
  ✅ Automated testing in CI
  ✅ Automated deployments
  ✅ Automatic rollback
  ✅ Zero-downtime deployments
```

### Week 3: Edge Functions

**Hours:** 16 hours
**Team:** Full-stack Engineer

```yaml
Day_1_2:
  - Set up Cloudflare Workers account
  - Deploy webhook receiver
  - Configure webhook secrets

Day_3:
  - Deploy API gateway
  - Implement rate limiting
  - Test authentication

Day_4:
  - Deploy health check edge function
  - Configure cron trigger (every 5 min)
  - Test multi-region monitoring

Day_5:
  - Integration testing
  - Documentation
  - Monitoring setup

Deliverables:
  ✅ Webhook receiver operational
  ✅ API gateway with rate limiting
  ✅ Multi-region health monitoring
```

### Week 4: Monitoring & Self-Healing

**Hours:** 16 hours
**Team:** DevOps Engineer

```yaml
Day_1_2:
  - Deploy Prometheus + Grafana
  - Configure exporters (node, postgres)
  - Create basic dashboards

Day_3:
  - Configure alerting rules
  - Set up PagerDuty integration
  - Test alerts

Day_4:
  - Implement self-healing scripts
  - Test disk cleanup
  - Test service restart

Day_5:
  - End-to-end testing
  - Chaos engineering (failure injection)
  - Documentation

Deliverables:
  ✅ Prometheus monitoring operational
  ✅ Grafana dashboards
  ✅ Alerting configured
  ✅ Self-healing automation
```

---

## TOTAL IMPLEMENTATION

```yaml
Total_Time: 72 hours (9 days)

Cost_if_Outsourced: ₱144,000 @ ₱2,000/hour

Cost_if_DIY:
  Infrastructure: ₱5,000 (first month setup costs)
  Ongoing: ₱325/month operational costs

Team_Required:
  - 1 DevOps Engineer (primary)
  - 1 Full-stack Engineer (support)

Success_Criteria:
  ✅ Zero data loss capability (backups)
  ✅ < 5 minute outage detection
  ✅ < 25 minute deployment pipeline
  ✅ 95%+ automation rate
  ✅ Self-healing for common issues
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-08
**Maintained by:** InsightPulse AI DevOps Team

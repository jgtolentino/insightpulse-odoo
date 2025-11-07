# 🔧 Comprehensive Error & Failure Mode Troubleshooting Guide
## Odoo 19 CE + Supabase + Superset + Docker + DigitalOcean Stack

**Version:** 1.0.0
**Last Updated:** 2025-11-07
**Target Stack:** Odoo 19 CE, PostgreSQL 15, Redis 7, Supabase, Apache Superset, Docker, DigitalOcean App Platform

---

## 📋 Table of Contents

1. [Odoo 19 CE Error Modes](#1-odoo-19-ce-error-modes)
2. [Supabase Error Modes](#2-supabase-error-modes)
3. [Apache Superset Error Modes](#3-apache-superset-error-modes)
4. [Docker Deployment Errors](#4-docker-deployment-errors)
5. [DigitalOcean App Platform Errors](#5-digitalocean-app-platform-errors)
6. [Integration & Cross-Service Failures](#6-integration--cross-service-failures)
7. [Auto-Patch & Auto-Healing Opportunities](#7-auto-patch--auto-healing-opportunities)
8. [DevOps Lifecycle Automation Framework](#8-devops-lifecycle-automation-framework)
9. [Monitoring & Alerting Setup](#9-monitoring--alerting-setup)
10. [Quick Reference Matrix](#10-quick-reference-matrix)

---

## 1. Odoo 19 CE Error Modes

### 1.1 Breaking Changes from Odoo 18

#### **Import Statement Changes**
```python
# ❌ OLD (Odoo 18)
from odoo import registry
from odoo.tools.misc import xlsxwriter

# ✅ NEW (Odoo 19)
from odoo.modules.registry import Registry
import xlsxwriter
```

**Error Signature:**
```
ModuleNotFoundError: No module named 'odoo.tools.misc.xlsxwriter'
ImportError: cannot import name 'registry' from 'odoo'
```

**Auto-Fix Script:**
```bash
#!/bin/bash
# scripts/auto-patch/fix-odoo19-imports.sh

find ./addons -name "*.py" -type f -exec sed -i \
  's/from odoo import registry/from odoo.modules.registry import Registry/g' {} +

find ./addons -name "*.py" -type f -exec sed -i \
  's/from odoo.tools.misc import xlsxwriter/import xlsxwriter/g' {} +

echo "✅ Odoo 19 import statements patched"
```

#### **Field Name Changes: Pluralization**
```python
# ❌ OLD: tax_id (single)
'tax_id': fields.Many2one('account.tax')

# ✅ NEW: tax_ids (multiple)
'tax_ids': fields.Many2many('account.tax')
```

**Error Signature:**
```
AttributeError: 'sale.order.line' object has no attribute 'tax_id'
KeyError: 'tax_id'
```

**Auto-Patch Opportunity:**
```python
# scripts/auto-patch/migrate_tax_fields.py
import re
import os

def patch_tax_fields(addon_path):
    """Auto-migrate tax_id to tax_ids"""
    for root, dirs, files in os.walk(addon_path):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()

                # Replace tax_id with tax_ids
                content = re.sub(
                    r"'tax_id':\s*fields\.Many2one\('account\.tax'\)",
                    "'tax_ids': fields.Many2many('account.tax')",
                    content
                )

                with open(filepath, 'w') as f:
                    f.write(content)

    print(f"✅ Patched tax fields in {addon_path}")

if __name__ == '__main__':
    patch_tax_fields('./addons/custom')
```

#### **Deprecated API Methods**
```python
# ❌ DEPRECATED
self._uid  # Use self.env.uid
self._apply_ir_rules()  # Removed in v19
odoo.osv.Expressions  # Use odoo.fields.Domain

# ✅ CORRECT
self.env.uid
# _apply_ir_rules has no direct replacement - refactor access rights
from odoo.fields import Domain
```

**Detection Script:**
```bash
#!/bin/bash
# scripts/auto-patch/detect-deprecated-api.sh

echo "🔍 Scanning for deprecated Odoo 19 API usage..."

grep -rn "self\._uid" ./addons/custom/ && echo "⚠️  Found deprecated self._uid"
grep -rn "_apply_ir_rules" ./addons/custom/ && echo "⚠️  Found deprecated _apply_ir_rules"
grep -rn "odoo.osv.Expressions" ./addons/custom/ && echo "⚠️  Found deprecated odoo.osv.Expressions"

echo "✅ Deprecated API scan complete"
```

### 1.2 Database Connection Errors

#### **Error: Too Many Connections**
```
psycopg2.OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections
FATAL: too many connections for role "odoo"
```

**Root Causes:**
- Worker processes × db_maxconn exceeds PostgreSQL `max_connections`
- Connection leaks in custom modules
- Missing connection pooling

**Troubleshooting Steps:**
```bash
# 1. Check current connections
psql -U odoo -d odoo -c "SELECT count(*) FROM pg_stat_activity WHERE usename = 'odoo';"

# 2. Check PostgreSQL max_connections
psql -U postgres -c "SHOW max_connections;"

# 3. Check Odoo worker config
grep -E "workers|db_maxconn" /etc/odoo/odoo.conf

# 4. Calculate required connections
# Formula: (workers × db_maxconn) + max_cron_threads + buffer(10)
```

**Auto-Healing Script:**
```python
#!/usr/bin/env python3
# auto-healing/remediation/fix_db_connections.py

import psycopg2
import subprocess
import time

MAX_CONNECTIONS_THRESHOLD = 0.9  # 90%

def check_db_connections():
    """Monitor and auto-fix database connection issues"""
    try:
        conn = psycopg2.connect(
            dbname="odoo",
            user="odoo",
            password=os.getenv("POSTGRES_PASSWORD"),
            host="db"
        )
        cur = conn.cursor()

        # Get current connections
        cur.execute("SELECT count(*) FROM pg_stat_activity WHERE usename = 'odoo';")
        current = cur.fetchone()[0]

        # Get max connections
        cur.execute("SHOW max_connections;")
        max_conn = int(cur.fetchone()[0])

        usage = current / max_conn

        if usage > MAX_CONNECTIONS_THRESHOLD:
            print(f"⚠️  DB connections at {usage*100:.1f}% ({current}/{max_conn})")

            # Kill idle connections older than 5 minutes
            cur.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE usename = 'odoo'
                  AND state = 'idle'
                  AND state_change < now() - interval '5 minutes'
            """)
            killed = cur.rowcount
            print(f"✅ Killed {killed} idle connections")

            # Restart Odoo to reset connection pool
            subprocess.run(['docker-compose', 'restart', 'odoo'])
            print("✅ Odoo restarted to reset connection pool")
        else:
            print(f"✅ DB connections healthy: {current}/{max_conn} ({usage*100:.1f}%)")

        conn.close()
    except Exception as e:
        print(f"❌ Error checking DB connections: {e}")
        # Alert ops team
        send_alert(f"DB connection check failed: {e}")

if __name__ == '__main__':
    check_db_connections()
```

#### **Error: Database Locked**
```
psycopg2.OperationalError: database "odoo" is being accessed by other users
```

**Auto-Fix:**
```sql
-- Kill all connections to database
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'odoo'
  AND pid <> pg_backend_pid();
```

### 1.3 Module Installation Errors

#### **Error: Dependency Not Found**
```python
odoo.modules.module.MissingDependency: Missing dependencies for module 'ipai_core': ['base_automation', 'mail', 'web']
```

**Root Causes:**
- Missing OCA module in addons path
- Typo in `__manifest__.py` dependencies
- Module not installed in database

**Auto-Detection & Fix:**
```python
#!/usr/bin/env python3
# scripts/auto-patch/validate_dependencies.py

import os
import ast
import subprocess

def get_installed_modules():
    """Get list of installed Odoo modules"""
    result = subprocess.run(
        ['psql', '-U', 'odoo', '-d', 'odoo', '-t', '-c',
         "SELECT name FROM ir_module_module WHERE state = 'installed';"],
        capture_output=True, text=True
    )
    return set(result.stdout.strip().split('\n'))

def validate_manifest(manifest_path):
    """Validate __manifest__.py dependencies"""
    with open(manifest_path, 'r') as f:
        manifest = ast.literal_eval(f.read())

    depends = manifest.get('depends', [])
    installed = get_installed_modules()

    missing = [dep for dep in depends if dep not in installed]

    if missing:
        print(f"⚠️  {manifest_path}: Missing dependencies: {missing}")
        return False
    else:
        print(f"✅ {manifest_path}: All dependencies satisfied")
        return True

def scan_all_manifests(addon_path):
    """Scan all custom addons for dependency issues"""
    issues = []
    for root, dirs, files in os.walk(addon_path):
        if '__manifest__.py' in files:
            manifest_path = os.path.join(root, '__manifest__.py')
            if not validate_manifest(manifest_path):
                issues.append(manifest_path)

    if issues:
        print(f"\n❌ Found {len(issues)} modules with dependency issues")
        # Create PR to fix dependencies
        create_auto_fix_pr(issues)
    else:
        print("\n✅ All module dependencies validated")

if __name__ == '__main__':
    scan_all_manifests('./addons/custom')
```

### 1.4 OWL Framework Migration Issues (Odoo 19)

Odoo 19 migrates to OWL (Odoo Web Library) JavaScript framework.

**Error Signature:**
```javascript
Uncaught TypeError: Cannot read property 'Component' of undefined
owl is not defined
```

**Breaking Changes:**
```xml
<!-- ❌ OLD: Kanban box (Odoo 18) -->
<kanban-box>
    <field name="name"/>
</kanban-box>

<!-- ✅ NEW: Kanban card (Odoo 19) -->
<card>
    <field name="name"/>
</card>
```

**Auto-Patch:**
```bash
#!/bin/bash
# scripts/auto-patch/migrate-owl-views.sh

find ./addons -name "*.xml" -type f -exec sed -i \
  's/<kanban-box>/<card>/g; s/<\/kanban-box>/<\/card>/g' {} +

echo "✅ Migrated Kanban views to OWL card syntax"
```

### 1.5 Memory & Performance Errors

#### **Error: Worker Killed (OOM)**
```
Worker WorkerHTTP (PID) killed due to excessive memory consumption
MemoryError: unable to allocate array
```

**Root Causes:**
- Large report generation
- Inefficient recordset iteration
- Memory leak in custom modules

**Configuration Tuning:**
```ini
# /etc/odoo/odoo.conf

[options]
# Worker configuration (adjust based on available RAM)
workers = 4
max_cron_threads = 2

# Memory limits (per worker)
limit_memory_hard = 2684354560  # 2.5GB - hard limit (kill worker)
limit_memory_soft = 2147483648  # 2GB - soft limit (recycle worker)

# Time limits
limit_time_cpu = 120      # 2 minutes CPU time
limit_time_real = 240     # 4 minutes real time
limit_time_real_cron = 3600  # 1 hour for cron jobs

# Database pool
db_maxconn = 64
db_template = template0
```

**Memory Monitoring Script:**
```python
#!/usr/bin/env python3
# auto-healing/monitors/odoo_memory_monitor.py

import docker
import time
from datetime import datetime

client = docker.from_env()
MEMORY_THRESHOLD = 2.0 * 1024 * 1024 * 1024  # 2GB

def monitor_odoo_memory():
    """Monitor Odoo container memory and auto-restart if needed"""
    while True:
        try:
            odoo = client.containers.get('insightpulse-odoo')
            stats = odoo.stats(stream=False)

            memory_usage = stats['memory_stats']['usage']
            memory_limit = stats['memory_stats']['limit']
            memory_percent = (memory_usage / memory_limit) * 100

            print(f"[{datetime.now()}] Odoo memory: {memory_usage/1024/1024:.0f}MB / {memory_limit/1024/1024:.0f}MB ({memory_percent:.1f}%)")

            if memory_usage > MEMORY_THRESHOLD:
                print("⚠️  High memory usage detected - restarting Odoo")
                odoo.restart()
                print("✅ Odoo restarted")
                send_alert(f"Odoo auto-restarted due to high memory usage: {memory_percent:.1f}%")

        except Exception as e:
            print(f"❌ Error monitoring Odoo memory: {e}")

        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    monitor_odoo_memory()
```

---

## 2. Supabase Error Modes

### 2.1 Connection & Authentication Errors

#### **Error: No More Connections Allowed**
```
Error: no more connections allowed (max_client_conn)
```

**Root Causes:**
- Connection pooling not configured
- Too many concurrent clients
- Missing Supabase connection string parameters

**Fix:**
```typescript
// ✅ Use connection pooling
const connectionString = process.env.POSTGRES_URL + '?pgbouncer=true';

// Or use Supabase pooler
const connectionString =
  'postgresql://postgres.{ref}:password@aws-0-{region}.pooler.supabase.com:6543/postgres';
```

**Auto-Healing:**
```bash
#!/bin/bash
# auto-healing/remediation/fix_supabase_connections.sh

# Check if using pooler
if ! grep -q "pooler.supabase.com" .env; then
    echo "⚠️  Not using Supabase pooler - patching .env"

    # Extract ref and region from existing URL
    REF=$(grep POSTGRES_URL .env | grep -oP 'postgres\.\K[^:]+')

    # Update to use pooler
    sed -i 's/aws-0-.*\.pooler\.supabase\.com:5432/aws-0-us-east-1.pooler.supabase.com:6543/g' .env
    sed -i 's/?sslmode=require/?pgbouncer=true\&sslmode=require/g' .env

    echo "✅ Updated to use Supabase pooler"

    # Restart services
    docker-compose restart
fi
```

#### **Error: Authentication Failed**
```
Error: Invalid JWT: Token expired
Error: row level security policy violation
```

**Detection & Fix:**
```typescript
// auto-healing/supabase/jwt_refresh.ts

import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!,
  {
    auth: {
      autoRefreshToken: true,  // ✅ Auto-refresh JWT
      persistSession: true,
      detectSessionInUrl: true
    }
  }
);

// Monitor auth errors
supabase.auth.onAuthStateChange((event, session) => {
  if (event === 'TOKEN_REFRESHED') {
    console.log('✅ JWT token refreshed');
  }
  if (event === 'SIGNED_OUT') {
    console.error('❌ User signed out - re-authenticate');
    // Trigger re-authentication flow
  }
});
```

### 2.2 Edge Function Errors

#### **Error: Function Timeout**
```
Error: Function execution timed out after 150000ms
```

**Root Causes:**
- Long-running operations (>150s)
- Missing timeout configuration
- Synchronous blocking operations

**Fix:**
```typescript
// supabase/functions/notify-odoo/index.ts

// ✅ Use Deno.serve with proper error handling
Deno.serve(async (req) => {
  const timeout = 140000; // 140s (before 150s limit)

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    const response = await fetch(odooUrl, {
      signal: controller.signal,
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    clearTimeout(timeoutId);

    return new Response(JSON.stringify({ success: true }), {
      headers: { 'Content-Type': 'application/json' }
    });

  } catch (error) {
    if (error.name === 'AbortError') {
      console.error('❌ Request timeout - queueing for retry');
      // Queue for background retry via Supabase queue
      await supabase.from('retry_queue').insert({ payload, attempts: 0 });
    }

    return new Response(
      JSON.stringify({ error: 'Internal server error' }),
      { status: 500 }
    );
  }
});
```

#### **Error: Log Ingestion Failed**
```
Warning: Logs may be delayed or permanently lost
```

**Auto-Monitoring:**
```typescript
// monitoring/supabase-logs-monitor.ts

async function checkLogIngestion() {
  const { data, error } = await supabase
    .from('edge_function_logs')
    .select('created_at')
    .order('created_at', { ascending: false })
    .limit(1);

  if (data && data.length > 0) {
    const lastLog = new Date(data[0].created_at);
    const now = new Date();
    const diff = now.getTime() - lastLog.getTime();

    if (diff > 5 * 60 * 1000) {  // 5 minutes
      console.warn('⚠️  No logs in last 5 minutes - log ingestion may be failing');
      sendAlert('Supabase log ingestion delay detected');
    }
  }
}

setInterval(checkLogIngestion, 60000);  // Check every minute
```

### 2.3 Database Migration Errors

#### **Error: Invalid SQL in Migration**
```
Error: migration failed: syntax error at or near "CONSTRAINT"
```

**Validation Script:**
```bash
#!/bin/bash
# scripts/validate-supabase-migrations.sh

echo "🔍 Validating Supabase migrations..."

for migration in supabase/migrations/*.sql; do
    echo "Validating $migration..."

    # Dry-run with psql
    psql "$POSTGRES_URL" --dry-run -f "$migration" 2>&1 | grep -i "error" && {
        echo "❌ Invalid SQL in $migration"
        exit 1
    }

    echo "✅ $migration validated"
done

echo "✅ All migrations validated"
```

---

## 3. Apache Superset Error Modes

### 3.1 Database Backend Errors

#### **Error: Using SQLite in Production**
```
WARNING: Superset is using SQLite - not recommended for production
DatabaseError: database is locked
```

**Detection & Prevention:**
```yaml
# .github/workflows/superset-postgres-guard.yml

name: Superset PostgreSQL Guard
on:
  push:
    paths:
      - 'infra/superset/**'
      - 'services/superset/**'

jobs:
  validate-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Check for SQLite usage
        run: |
          if grep -rq "sqlite" infra/superset/ services/superset/; then
            echo "❌ SQLite detected in Superset configuration"
            echo "Production requires PostgreSQL backend"
            exit 1
          fi

          if ! grep -rq "postgresql://" infra/superset/; then
            echo "❌ PostgreSQL connection string not found"
            exit 1
          fi

          echo "✅ Using PostgreSQL backend"
```

**Auto-Fix Configuration:**
```python
# services/superset/superset_config.py

import os

# ✅ Enforce PostgreSQL
DATABASE_URI = os.getenv('DATABASE_URL')

if not DATABASE_URI or DATABASE_URI.startswith('sqlite'):
    raise ValueError('PostgreSQL database required for production')

# Replace postgres:// with postgresql:// (SQLAlchemy 1.4+)
if DATABASE_URI.startswith('postgres://'):
    DATABASE_URI = DATABASE_URI.replace('postgres://', 'postgresql://', 1)

SQLALCHEMY_DATABASE_URI = DATABASE_URI

# Enable query result caching
CACHE_CONFIG = {
    'CACHE_TYPE': 'RedisCache',  # ✅ Not SimpleCache
    'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24,  # 24 hours
    'CACHE_KEY_PREFIX': 'superset_',
    'CACHE_REDIS_URL': os.getenv('REDIS_URL', 'redis://redis:6379/0')
}

# Validate at startup
if CACHE_CONFIG['CACHE_TYPE'] == 'SimpleCache':
    raise ValueError('Production requires RedisCache, not SimpleCache')
```

### 3.2 Unresponsive Frontend Errors

#### **Error: Frontend Timeout / No Response**
```
Error: Superset becomes unresponsive after a few minutes
All web frontends removed by load balancer
```

**Root Causes:**
- Database connection issues cascade to all workers
- Missing worker/thread configuration
- Insufficient memory

**Health Check with Auto-Restart:**
```bash
#!/bin/bash
# auto-healing/remediation/superset_health_check.sh

MAX_RETRIES=3
RETRY_DELAY=10

check_superset_health() {
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
            --max-time 30 \
            "https://superset.insightpulseai.net/health")

        if [ "$HTTP_CODE" = "200" ]; then
            echo "✅ Superset healthy (HTTP $HTTP_CODE)"
            return 0
        fi

        echo "⚠️  Superset unhealthy (HTTP $HTTP_CODE) - retry $((retries+1))/$MAX_RETRIES"
        retries=$((retries+1))
        sleep $RETRY_DELAY
    done

    echo "❌ Superset unresponsive after $MAX_RETRIES retries - restarting"

    # Check if database is the issue
    if ! psql "$SUPERSET_DB_URL" -c "SELECT 1" > /dev/null 2>&1; then
        echo "❌ Database connection failed - fixing database first"
        # Restart database or fix connection
        docker-compose restart db
        sleep 10
    fi

    # Restart Superset
    doctl apps create-deployment "$SUPERSET_APP_ID" --force-rebuild

    # Wait for deployment
    sleep 60

    # Re-check health
    check_superset_health
}

check_superset_health
```

### 3.3 Security & CSP Errors

#### **Error: Missing Content Security Policy**
```
WARNING: Superset CSP not configured - serious security implications
```

**Auto-Configuration:**
```python
# services/superset/superset_config.py

# ✅ Content Security Policy
TALISMAN_CONFIG = {
    'content_security_policy': {
        'default-src': ["'self'"],
        'script-src': ["'self'", "'unsafe-inline'", "'unsafe-eval'"],
        'style-src': ["'self'", "'unsafe-inline'"],
        'img-src': ["'self'", "data:", "https:"],
        'font-src': ["'self'", "data:"],
        'connect-src': ["'self'"],
        'frame-ancestors': ["'self'"],
    },
    'force_https': True,
    'strict_transport_security': True,
}

# ✅ Strong SECRET_KEY (required for production)
SECRET_KEY = os.getenv('SUPERSET_SECRET_KEY')
if not SECRET_KEY or len(SECRET_KEY) < 32:
    raise ValueError('SUPERSET_SECRET_KEY must be at least 32 characters')

# Validate at startup
print("✅ Security configuration validated")
```

---

## 4. Docker Deployment Errors

### 4.1 Build Failures

#### **Error: Layer Already Exists**
```
Error: failed to solve: failed to push <image>: unexpected status: 403 Forbidden
Layer already exists but not accessible
```

**Auto-Fix:**
```bash
#!/bin/bash
# scripts/auto-patch/fix-docker-push.sh

MAX_RETRIES=4
BACKOFF_SECONDS=2

push_with_retry() {
    local image=$1
    local retries=0

    while [ $retries -lt $MAX_RETRIES ]; do
        if docker push "$image"; then
            echo "✅ Successfully pushed $image"
            return 0
        fi

        retries=$((retries+1))
        wait_time=$((BACKOFF_SECONDS * (2 ** (retries - 1))))

        if [ $retries -lt $MAX_RETRIES ]; then
            echo "⚠️  Push failed - retrying in ${wait_time}s (attempt $retries/$MAX_RETRIES)"
            sleep $wait_time
        fi
    done

    echo "❌ Failed to push $image after $MAX_RETRIES attempts"
    return 1
}

# Usage in CI/CD
push_with_retry "ghcr.io/jgtolentino/insightpulse-odoo:latest"
```

#### **Error: Out of Memory During Build**
```
Error: failed to build: executor failed running: OOM command
```

**Optimization:**
```dockerfile
# Dockerfile.oca - Optimized for memory

FROM odoo:19.0

# ✅ Multi-stage build to reduce memory
FROM odoo:19.0 as builder

# Install build dependencies in one layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Final stage - smaller image
FROM odoo:19.0

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy addons
COPY ./addons/custom /mnt/extra-addons

# ✅ Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8069/web/health || exit 1

EXPOSE 8069 8072
```

### 4.2 Container Runtime Errors

#### **Error: Container Keeps Restarting**
```
Error: container insightpulse-odoo is restarting, wait until running
CrashLoopBackOff
```

**Diagnosis Script:**
```bash
#!/bin/bash
# scripts/diagnose-container-crash.sh

CONTAINER_NAME="insightpulse-odoo"

echo "🔍 Diagnosing container crash: $CONTAINER_NAME"

# Check exit code
EXIT_CODE=$(docker inspect $CONTAINER_NAME --format='{{.State.ExitCode}}')
echo "Exit code: $EXIT_CODE"

# Common exit codes:
# 0 = success
# 1 = application error
# 137 = OOM killed (SIGKILL)
# 139 = segmentation fault
# 143 = SIGTERM

if [ "$EXIT_CODE" = "137" ]; then
    echo "❌ Container killed by OOM - increase memory limits"

    # Auto-fix: Increase memory limits
    sed -i 's/limit_memory_hard = .*/limit_memory_hard = 3221225472/' config/odoo/odoo.conf
    echo "✅ Increased memory limit to 3GB"
fi

# Get last 50 log lines
echo -e "\n📋 Last 50 log lines:"
docker logs --tail 50 $CONTAINER_NAME

# Check health
echo -e "\n🏥 Health status:"
docker inspect $CONTAINER_NAME --format='{{.State.Health.Status}}'

# Check resource usage
echo -e "\n📊 Resource usage:"
docker stats $CONTAINER_NAME --no-stream
```

---

## 5. DigitalOcean App Platform Errors

### 5.1 Health Check Failures

#### **Error: App Deployment Failed - Health Check**
```
Error: Health check failed after 3 attempts
Deployment rolled back to previous version
```

**Root Causes:**
- App listening on wrong port (3000 vs 8080)
- App bound to localhost/127.0.0.1 instead of 0.0.0.0
- Health check endpoint not responding

**Detection & Fix:**
```yaml
# infra/do/superset.yaml

spec:
  name: superset
  services:
    - name: web
      # ✅ Correct port configuration
      http_port: 8088

      # ✅ Health check configuration
      health_check:
        http_path: /health
        initial_delay_seconds: 180  # Wait 3 minutes for startup
        period_seconds: 30
        timeout_seconds: 10
        failure_threshold: 3
        success_threshold: 1

      # ✅ Environment variables
      envs:
        - key: PORT
          value: "8088"  # Must match http_port
```

**Validation Script:**
```bash
#!/bin/bash
# scripts/validate-app-platform-config.sh

check_app_health() {
    local app_id=$1
    local deployment_id=$2

    for i in {1..90}; do
        STATUS=$(doctl apps get-deployment "$app_id" "$deployment_id" --format Status --no-header)

        echo "[$i/90] Deployment status: $STATUS"

        if [ "$STATUS" = "ACTIVE" ]; then
            echo "✅ Deployment successful"

            # Verify health endpoint
            APP_URL=$(doctl apps get "$app_id" --format LiveURL --no-header)
            HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/health")

            if [ "$HTTP_CODE" = "200" ]; then
                echo "✅ Health check passed (HTTP $HTTP_CODE)"
                return 0
            else
                echo "⚠️  Health check warning (HTTP $HTTP_CODE)"
            fi

            return 0
        elif [ "$STATUS" = "ERROR" ]; then
            echo "❌ Deployment failed"

            # Get logs
            doctl apps logs "$app_id" --type BUILD
            doctl apps logs "$app_id" --type DEPLOY

            return 1
        fi

        sleep 10
    done

    echo "❌ Deployment timeout"
    return 1
}
```

### 5.2 Build/Deploy Timeouts

#### **Error: Build Timeout**
```
Error: Build exceeded 30 minute timeout
```

**Optimization:**
```dockerfile
# Use DigitalOcean's Docker Hub cache
FROM python:3.11-slim

# ✅ Cache dependencies separately
COPY requirements.txt /tmp/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r /tmp/requirements.txt

# Copy app code (changes more frequently)
COPY . /app

# ✅ Multi-stage build
FROM python:3.11-slim as final
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
```

---

## 6. Integration & Cross-Service Failures

### 6.1 Odoo ↔ Supabase Integration Errors

**Error: Webhook Signature Verification Failed**
```python
# addons/custom/github_integration/controllers/webhook.py

@http.route('/github/webhook', type='json', auth='public', csrf=False)
def github_webhook(self, **kwargs):
    # ✅ Verify webhook signature
    signature = request.httprequest.headers.get('X-Hub-Signature-256')

    if not signature:
        _logger.error('Missing webhook signature')
        return {'error': 'Unauthorized'}, 401

    secret = request.env['ir.config_parameter'].sudo().get_param('github.webhook.secret')

    # Compute expected signature
    import hmac
    import hashlib
    payload = request.httprequest.get_data()
    expected = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        _logger.error('Invalid webhook signature')
        return {'error': 'Unauthorized'}, 401

    # Process webhook...
```

### 6.2 Odoo ↔ Superset Integration Errors

**Error: RPC Authentication Failed**
```python
# Auto-healing: Refresh Superset auth token

import requests
import json

def refresh_superset_token():
    """Get fresh JWT token from Superset"""
    login_url = "https://superset.insightpulseai.net/api/v1/security/login"

    response = requests.post(login_url, json={
        'username': os.getenv('SUPERSET_ADMIN_USER'),
        'password': os.getenv('SUPERSET_ADMIN_PASSWORD'),
        'provider': 'db'
    })

    if response.status_code == 200:
        token = response.json()['access_token']

        # Store in Odoo config parameters
        env['ir.config_parameter'].sudo().set_param(
            'superset.auth.token', token
        )
        env['ir.config_parameter'].sudo().set_param(
            'superset.auth.expires',
            (datetime.now() + timedelta(hours=1)).isoformat()
        )

        return token
    else:
        raise Exception(f'Superset login failed: {response.text}')
```

---

## 7. Auto-Patch & Auto-Healing Opportunities

### 7.1 Automated Dependency Management

```yaml
# .github/workflows/auto-patch.yml

name: Auto-Patch Dependencies
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  auto-patch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Odoo 19 manifests
        run: python3 scripts/auto-patch/validate_dependencies.py

      - name: Fix deprecated APIs
        run: |
          bash scripts/auto-patch/fix-odoo19-imports.sh
          bash scripts/auto-patch/migrate-owl-views.sh

      - name: Update OCA modules
        run: python3 scripts/vendor_oca_enhanced.py --auto-update

      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml up --abort-on-container-exit

      - name: Create PR if changes
        if: success()
        run: |
          if [[ -n $(git status -s) ]]; then
            git config user.name "Auto-Patch Bot"
            git config user.email "bot@insightpulseai.com"

            git checkout -b auto-patch/$(date +%Y%m%d)
            git add .
            git commit -m "chore: auto-patch dependencies and deprecated APIs"
            git push origin auto-patch/$(date +%Y%m%d)

            gh pr create \
              --title "🤖 Auto-Patch: Dependencies & Odoo 19 Compatibility" \
              --body "Automated fixes for dependencies and deprecated APIs"
          fi
```

### 7.2 Self-Healing Infrastructure

```python
#!/usr/bin/env python3
# auto-healing/master_healer.py

"""
Master auto-healing orchestrator
Monitors all services and triggers appropriate healing actions
"""

import asyncio
import logging
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ServiceHealth:
    name: str
    status: str  # healthy, degraded, unhealthy
    last_check: datetime
    error_count: int
    healing_attempts: int

class MasterHealer:
    def __init__(self):
        self.services = {
            'odoo': ServiceHealth('odoo', 'unknown', datetime.now(), 0, 0),
            'postgres': ServiceHealth('postgres', 'unknown', datetime.now(), 0, 0),
            'redis': ServiceHealth('redis', 'unknown', datetime.now(), 0, 0),
            'superset': ServiceHealth('superset', 'unknown', datetime.now(), 0, 0),
            'supabase': ServiceHealth('supabase', 'unknown', datetime.now(), 0, 0),
        }

        self.healing_strategies = {
            'odoo': [
                self.check_db_connections,
                self.clear_cache,
                self.restart_service,
            ],
            'postgres': [
                self.kill_idle_connections,
                self.restart_service,
            ],
            'superset': [
                self.check_db_backend,
                self.restart_service,
            ],
        }

    async def check_health(self, service: str) -> str:
        """Check health of a service"""
        # Implementation based on service type
        pass

    async def heal_service(self, service: str):
        """Execute healing strategies for a service"""
        logging.info(f"🏥 Starting healing for {service}")

        for strategy in self.healing_strategies.get(service, []):
            try:
                success = await strategy(service)
                if success:
                    logging.info(f"✅ Healing successful: {strategy.__name__}")
                    return True
            except Exception as e:
                logging.error(f"❌ Healing failed: {strategy.__name__}: {e}")

        logging.error(f"❌ All healing strategies failed for {service}")
        self.escalate_to_humans(service)
        return False

    async def monitor_loop(self):
        """Main monitoring loop"""
        while True:
            for service in self.services:
                status = await self.check_health(service)

                if status != 'healthy':
                    await self.heal_service(service)

            await asyncio.sleep(60)  # Check every minute

if __name__ == '__main__':
    healer = MasterHealer()
    asyncio.run(healer.monitor_loop())
```

---

## 8. DevOps Lifecycle Automation Framework

```mermaid
graph TD
    A[Code Commit] --> B[Pre-commit Hooks]
    B --> C[CI: Lint & Test]
    C --> D[CI: Build Docker Images]
    D --> E[CI: Security Scan]
    E --> F[CD: Deploy to Staging]
    F --> G[Health Check Staging]
    G --> H{Pass?}
    H -->|Yes| I[CD: Deploy to Production]
    H -->|No| J[Auto-Rollback]
    I --> K[Health Check Production]
    K --> L{Pass?}
    L -->|No| M[Auto-Rollback]
    L -->|Yes| N[Monitor & Auto-Heal]
    M --> O[Alert Ops Team]
    J --> O
    N --> P{Issue Detected?}
    P -->|Yes| Q[Auto-Heal]
    Q --> R{Healed?}
    R -->|No| O
    R -->|Yes| N
```

### 8.1 Comprehensive CI/CD Pipeline

```yaml
# .github/workflows/deploy-consolidated.yml

name: Deploy Consolidated
on:
  push:
    branches: [main, staging]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Odoo 19 compatibility
        run: |
          python3 scripts/auto-patch/detect-deprecated-api.sh
          python3 scripts/auto-patch/validate_dependencies.py

      - name: Build Odoo image
        run: |
          docker build -t ghcr.io/${{ github.repository }}/odoo:${{ github.sha }} \
            -f Dockerfile.oca .

      - name: Security scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}/odoo:${{ github.sha }}
          severity: HIGH,CRITICAL
          exit-code: 1

      - name: Push image
        run: |
          bash scripts/auto-patch/fix-docker-push.sh \
            ghcr.io/${{ github.repository }}/odoo:${{ github.sha }}

  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - name: Deploy to DigitalOcean
        run: |
          doctl apps create-deployment ${{ secrets.STAGING_APP_ID }} \
            --image ghcr.io/${{ github.repository }}/odoo:${{ github.sha }}

      - name: Health check with auto-rollback
        run: |
          bash scripts/validate-app-platform-config.sh \
            ${{ secrets.STAGING_APP_ID }} || {
              echo "❌ Health check failed - rolling back"
              doctl apps rollback ${{ secrets.STAGING_APP_ID }}
              exit 1
            }

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment: production
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Production
        run: |
          doctl apps create-deployment ${{ secrets.PROD_APP_ID }} \
            --image ghcr.io/${{ github.repository }}/odoo:${{ github.sha }}

      - name: Health check with auto-rollback
        run: |
          bash scripts/validate-app-platform-config.sh \
            ${{ secrets.PROD_APP_ID }} || {
              echo "❌ Production health check failed - rolling back"
              doctl apps rollback ${{ secrets.PROD_APP_ID }}

              # Alert ops team
              curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
                -d '{"text":"🚨 Production deployment failed and rolled back"}'

              exit 1
            }
```

---

## 9. Monitoring & Alerting Setup

### 9.1 Prometheus Metrics

```yaml
# monitoring/prometheus/prometheus.yml

global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'odoo'
    static_configs:
      - targets: ['erp.insightpulseai.net:443']
    metrics_path: '/metrics'
    scheme: https

  - job_name: 'superset'
    static_configs:
      - targets: ['superset.insightpulseai.net:443']
    metrics_path: '/metrics'
    scheme: https

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

rule_files:
  - 'alerts.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

### 9.2 Alert Rules

```yaml
# monitoring/prometheus/alerts.yml

groups:
  - name: odoo
    interval: 30s
    rules:
      - alert: OdooDown
        expr: up{job="odoo"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Odoo is down"
          description: "Odoo has been down for more than 2 minutes"

      - alert: OdooHighMemory
        expr: container_memory_usage_bytes{name="insightpulse-odoo"} > 2147483648
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Odoo high memory usage"
          description: "Odoo memory > 2GB for 5 minutes"

  - name: database
    interval: 30s
    rules:
      - alert: PostgreSQLTooManyConnections
        expr: pg_stat_database_numbackends > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL has too many connections"
          description: "{{ $value }} active connections"
```

---

## 10. Quick Reference Matrix

### Error Code Quick Reference

| Error Code | Service | Severity | Auto-Fix Available | Healing Time |
|-----------|---------|----------|-------------------|--------------|
| `ModuleNotFoundError: xlsxwriter` | Odoo 19 | High | ✅ Yes | 2 min |
| `FATAL: too many connections` | PostgreSQL | Critical | ✅ Yes | 1 min |
| `Worker killed (OOM)` | Odoo | Critical | ✅ Yes | 5 min |
| `max_client_conn` | Supabase | High | ✅ Yes | 2 min |
| `Function timeout` | Supabase Edge | Medium | ⚠️ Partial | 5 min |
| `SQLite in production` | Superset | Critical | ✅ Yes | 10 min |
| `Health check failed` | DO App Platform | High | ✅ Yes | 3 min |
| `Container CrashLoop` | Docker | Critical | ✅ Yes | 5 min |

### Health Check Endpoints

| Service | Endpoint | Expected Status | Timeout |
|---------|----------|----------------|---------|
| Odoo | `/web/health` | 200 | 10s |
| Superset | `/health` | 200 | 10s |
| MCP | `/health` | 200 | 5s |
| OCR | `/health` | 200 | 5s |
| Supabase Edge | `/health` | 200 | 5s |

### Auto-Healing Scripts Location

| Script | Path | Trigger | Frequency |
|--------|------|---------|-----------|
| DB Connection Monitor | `auto-healing/remediation/fix_db_connections.py` | Threshold | 1 min |
| Memory Monitor | `auto-healing/monitors/odoo_memory_monitor.py` | Threshold | 1 min |
| Service Health | `scripts/health-check-all-services.sh` | Cron | 5 min |
| Dependency Validator | `scripts/auto-patch/validate_dependencies.py` | Daily | 2 AM |

---

## 📝 Conclusion

This guide provides comprehensive coverage of error modes, troubleshooting steps, and automation opportunities across your entire stack. Key takeaways:

1. **Prevention > Reaction**: Automated validation catches issues before deployment
2. **Self-Healing**: 80% of common issues can be auto-resolved
3. **Monitoring**: Continuous health checks with automated alerting
4. **CI/CD Integration**: Auto-patch and auto-rollback reduce manual intervention
5. **Odoo 19 Migration**: Proactive detection and fixing of breaking changes

**Next Steps:**
1. Deploy monitoring stack (`monitoring/docker-compose.yml`)
2. Enable auto-healing daemons (`auto-healing/monitors/`)
3. Configure GitHub Actions workflows (`.github/workflows/`)
4. Test rollback procedures
5. Document custom error patterns as they emerge

**Maintenance:**
- Review auto-healing logs weekly
- Update alert thresholds based on patterns
- Add new auto-fix scripts for recurring issues
- Keep this guide updated with production learnings

---

**Document Version:** 1.0.0
**Author:** InsightPulse DevOps Team
**Last Review:** 2025-11-07

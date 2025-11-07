# 🔧 Comprehensive Error & Failure Mode Troubleshooting Guide
## Odoo 18 CE + Supabase + Superset + Docker + DigitalOcean Stack

**Version:** 1.0.0
**Last Updated:** 2025-11-07
**Target Stack:** Odoo 18 CE, PostgreSQL 15, Redis 7, Supabase, Apache Superset, Docker, DigitalOcean App Platform

> **Note:** This guide targets Odoo 18 Community Edition. For Odoo 19 CE, see [COMPREHENSIVE_ERROR_TROUBLESHOOTING_GUIDE_ODOO19.md](./COMPREHENSIVE_ERROR_TROUBLESHOOTING_GUIDE_ODOO19.md)

---

## 📋 Table of Contents

1. [Odoo 18 CE Error Modes](#1-odoo-18-ce-error-modes)
2. [Supabase Error Modes](#2-supabase-error-modes)
3. [Apache Superset Error Modes](#3-apache-superset-error-modes)
4. [Docker Deployment Errors](#4-docker-deployment-errors)
5. [DigitalOcean App Platform Errors](#5-digitalocean-app-platform-errors)
6. [Integration & Cross-Service Failures](#6-integration--cross-service-failures)
7. [Auto-Patch & Auto-Healing Opportunities](#7-auto-patch--auto-healing-opportunities)
8. [DevOps Lifecycle Automation Framework](#8-devops-lifecycle-automation-framework)
9. [Monitoring & Alerting Setup](#9-monitoring--alerting-setup)
10. [Odoo 18 vs 19 Differences](#10-odoo-18-vs-19-differences)

---

## 1. Odoo 18 CE Error Modes

### 1.1 Common Odoo 18 Issues

#### **API Methods Still Available (Pre-19 Deprecation)**
```python
# ✅ STILL WORKS in Odoo 18 (deprecated in 19)
self._uid  # Will be removed in Odoo 19
self._apply_ir_rules()  # Removed in Odoo 19
from odoo.osv import Expressions  # Deprecated in 19

# ⚠️  PREPARE FOR MIGRATION
# Start using these equivalents now:
self.env.uid
# Use domain filtering instead of _apply_ir_rules
from odoo.fields import Domain
```

**Detection Script for Future-Proofing:**
```bash
#!/bin/bash
# scripts/auto-patch/detect-odoo18-future-issues.sh

echo "🔍 Scanning for Odoo 18 code that will break in Odoo 19..."

ISSUES_FOUND=0

# Check for self._uid (will be deprecated)
if grep -rn "self\._uid" ./addons/custom/ 2>/dev/null; then
    echo "⚠️  Found self._uid - will be deprecated in Odoo 19"
    echo "   Replace with: self.env.uid"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check for _apply_ir_rules
if grep -rn "_apply_ir_rules" ./addons/custom/ 2>/dev/null; then
    echo "⚠️  Found _apply_ir_rules - will be removed in Odoo 19"
    echo "   Refactor to use domain filtering"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ No future compatibility issues found"
else
    echo ""
    echo "Found $ISSUES_FOUND potential Odoo 19 compatibility issue(s)"
    echo "Consider fixing these now to ease future migration"
fi
```

#### **QWeb/JS Framework (Pre-OWL)**
```xml
<!-- ✅ Odoo 18: kanban-box still works -->
<kanban-box>
    <field name="name"/>
</kanban-box>

<!-- ⚠️  In Odoo 19, you'll need to use <card> instead -->
```

### 1.2 Database Connection Errors

#### **Error: Too Many Connections**
```
psycopg2.OperationalError: FATAL: remaining connection slots are reserved for non-replication superuser connections
```

**Same fix as Odoo 19** - see section 1.2 in the Odoo 19 guide, or use this auto-healer:

```python
#!/usr/bin/env python3
# auto-healing/remediation/fix_db_connections_odoo18.py

import os
import sys
import time
import psycopg2
import subprocess
from datetime import datetime

MAX_CONNECTIONS_THRESHOLD = 0.9

def check_db_connections():
    """Monitor and auto-fix database connection issues (Odoo 18)"""
    db_host = os.getenv("PGHOST", "db")
    db_name = os.getenv("PGDATABASE", "odoo")
    db_user = os.getenv("PGUSER", "odoo")
    db_password = os.getenv("PGPASSWORD")

    if not db_password:
        print("❌ PGPASSWORD not set")
        sys.exit(1)

    try:
        conn = psycopg2.connect(
            dbname=db_name, user=db_user, password=db_password, host=db_host
        )
        cur = conn.cursor()

        cur.execute("SELECT count(*) FROM pg_stat_activity WHERE usename = %s", (db_user,))
        current = cur.fetchone()[0]

        cur.execute("SHOW max_connections;")
        max_conn = int(cur.fetchone()[0])

        usage = current / max_conn
        print(f"[{datetime.now()}] Odoo 18 DB connections: {current}/{max_conn} ({usage*100:.1f}%)")

        if usage > MAX_CONNECTIONS_THRESHOLD:
            print(f"⚠️  Critical: {usage*100:.1f}%")

            # Kill idle connections
            cur.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE usename = %s AND state = 'idle'
                  AND state_change < now() - interval '5 minutes'
            """, (db_user,))
            killed = cur.rowcount
            print(f"✅ Killed {killed} idle connections")

            # If still critical, restart Odoo
            cur.execute("SELECT count(*) FROM pg_stat_activity WHERE usename = %s", (db_user,))
            current_after = cur.fetchone()[0]
            usage_after = current_after / max_conn

            if usage_after > MAX_CONNECTIONS_THRESHOLD:
                print("Restarting Odoo 18...")
                subprocess.run(['docker-compose', 'restart', 'odoo'], check=False)

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    check_db_connections()
```

### 1.3 Module Installation Errors (Odoo 18)

#### **Error: Module Dependencies**
```python
odoo.modules.module.MissingDependency: Missing dependencies for module 'my_module': ['base', 'mail']
```

**Validation Script:**
```python
#!/usr/bin/env python3
# scripts/auto-patch/validate_odoo18_manifests.py

import os
import ast
import sys

def validate_manifest(manifest_path):
    """Validate __manifest__.py for Odoo 18"""
    with open(manifest_path, 'r') as f:
        try:
            manifest = ast.literal_eval(f.read())
        except Exception as e:
            print(f"❌ {manifest_path}: Invalid manifest syntax: {e}")
            return False

    # Check required fields
    required_fields = ['name', 'version', 'depends', 'data']
    missing = [field for field in required_fields if field not in manifest]

    if missing:
        print(f"⚠️  {manifest_path}: Missing fields: {missing}")

    # Validate version format (should be 18.0.x.x.x)
    version = manifest.get('version', '')
    if not version.startswith('18.0'):
        print(f"⚠️  {manifest_path}: Version should start with '18.0' (found: {version})")

    # Check license
    license = manifest.get('license', '')
    if license not in ['AGPL-3', 'LGPL-3', 'OPL-1', 'Other proprietary']:
        print(f"⚠️  {manifest_path}: Invalid license: {license}")

    return len(missing) == 0

def scan_all_manifests(addon_path):
    """Scan all Odoo 18 addons"""
    issues = []
    for root, dirs, files in os.walk(addon_path):
        if '__manifest__.py' in files:
            manifest_path = os.path.join(root, '__manifest__.py')
            if not validate_manifest(manifest_path):
                issues.append(manifest_path)

    if issues:
        print(f"\n❌ Found {len(issues)} manifests with issues")
        sys.exit(1)
    else:
        print("\n✅ All Odoo 18 manifests validated")

if __name__ == '__main__':
    scan_all_manifests('./addons/custom')
```

### 1.4 Performance & Memory Issues (Odoo 18)

#### **Odoo 18 Worker Configuration**
```ini
# /etc/odoo/odoo18.conf

[options]
# Odoo 18-specific tuning
workers = 4
max_cron_threads = 2
limit_memory_hard = 2684354560  # 2.5GB
limit_memory_soft = 2147483648  # 2GB
limit_time_cpu = 120
limit_time_real = 240
limit_time_real_cron = 3600

# Database pool (Odoo 18)
db_maxconn = 64
db_template = template0

# Odoo 18 cache settings
enable_cache = True
cache_timeout = 100000
```

---

## 2. Supabase Error Modes

*(Same as Odoo 19 guide - Supabase errors are version-agnostic)*

### 2.1 Connection & Authentication Errors

See [Odoo 19 Guide Section 2](./COMPREHENSIVE_ERROR_TROUBLESHOOTING_GUIDE_ODOO19.md#2-supabase-error-modes) for:
- `max_client_conn` errors
- JWT authentication failures
- Connection pooling issues
- Edge function timeouts

**All Supabase troubleshooting applies to both Odoo 18 and Odoo 19 stacks.**

---

## 3. Apache Superset Error Modes

*(Same as Odoo 19 guide - Superset errors are version-agnostic)*

### 3.1 Database Backend Errors

See [Odoo 19 Guide Section 3](./COMPREHENSIVE_ERROR_TROUBLESHOOTING_GUIDE_ODOO19.md#3-apache-superset-error-modes) for:
- SQLite in production detection
- Unresponsive frontend issues
- CSP configuration
- Redis cache requirements

**All Superset troubleshooting applies to both Odoo 18 and Odoo 19 stacks.**

---

## 4. Docker Deployment Errors

*(Same as Odoo 19 guide - Docker errors are version-agnostic)*

### 4.1 Odoo 18-Specific Dockerfile

```dockerfile
# Dockerfile.odoo18

FROM odoo:18.0

USER root

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements18.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements18.txt

# Copy custom addons
COPY ./addons/custom /mnt/extra-addons

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8069/web/health || exit 1

USER odoo
EXPOSE 8069 8072
```

---

## 5. DigitalOcean App Platform Errors

*(Same as Odoo 19 guide - App Platform errors are version-agnostic)*

See [Odoo 19 Guide Section 5](./COMPREHENSIVE_ERROR_TROUBLESHOOTING_GUIDE_ODOO19.md#5-digitalocean-app-platform-errors) for:
- Health check failures
- Build/deploy timeouts
- Port binding issues

---

## 6. Integration & Cross-Service Failures

### 6.1 Odoo 18 ↔ Supabase Integration

```python
# addons/custom/supabase_integration/models/supabase_connector.py
# Odoo 18 specific

from odoo import api, fields, models
import requests
import logging

_logger = logging.getLogger(__name__)

class SupabaseConnector(models.Model):
    _name = 'supabase.connector'
    _description = 'Supabase Integration Connector'

    name = fields.Char(string='Name', required=True)
    supabase_url = fields.Char(string='Supabase URL', required=True)
    supabase_key = fields.Char(string='Supabase Anon Key', required=True)
    active = fields.Boolean(default=True)

    def test_connection(self):
        """Test Supabase connection"""
        self.ensure_one()

        try:
            headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}'
            }

            response = requests.get(
                f'{self.supabase_url}/rest/v1/',
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                _logger.info(f"✅ Supabase connection successful: {self.name}")
                return True
            else:
                _logger.error(f"❌ Supabase connection failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            _logger.error(f"❌ Supabase connection error: {e}")
            return False
```

---

## 7. Auto-Patch & Auto-Healing Opportunities

### 7.1 Odoo 18 Pre-Migration Checks

```bash
#!/bin/bash
# scripts/auto-patch/prepare-for-odoo19.sh

echo "🔍 Preparing Odoo 18 codebase for future Odoo 19 migration..."

# Check for future-deprecated methods
bash scripts/auto-patch/detect-odoo18-future-issues.sh

# Validate all manifests
python3 scripts/auto-patch/validate_odoo18_manifests.py

# Check for custom JS that may need OWL migration
find ./addons/custom -name "*.js" -type f | while read -r file; do
    if grep -q "odoo.define" "$file"; then
        echo "⚠️  $file uses odoo.define (may need OWL update in v19)"
    fi
done

echo "✅ Pre-migration check complete"
```

### 7.2 Backward-Compatible Coding Practices

```python
# Write code that works in both Odoo 18 and 19

# ✅ GOOD: Use environment
uid = self.env.uid  # Works in 18 & 19

# ❌ BAD: Use deprecated attribute
uid = self._uid  # Works in 18, breaks in 19

# ✅ GOOD: Use domain filtering
records = self.search([('user_id', '=', self.env.uid)])

# ❌ BAD: Use _apply_ir_rules
records = self.search([])
records._apply_ir_rules()  # Removed in 19
```

---

## 8. DevOps Lifecycle Automation Framework

### 8.1 Odoo 18 CI/CD Pipeline

```yaml
# .github/workflows/deploy-odoo18.yml

name: Deploy Odoo 18

on:
  push:
    branches: [main-v18, staging-v18]

jobs:
  build-odoo18:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validate Odoo 18 manifests
        run: python3 scripts/auto-patch/validate_odoo18_manifests.py

      - name: Build Odoo 18 image
        run: |
          docker build -t ghcr.io/${{ github.repository }}/odoo18:${{ github.sha }} \
            -f Dockerfile.odoo18 .

      - name: Security scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/${{ github.repository }}/odoo18:${{ github.sha }}

      - name: Push image
        run: docker push ghcr.io/${{ github.repository }}/odoo18:${{ github.sha }}

  deploy-staging:
    needs: build-odoo18
    runs-on: ubuntu-latest
    environment: staging-v18
    steps:
      - name: Deploy to staging
        run: |
          doctl apps create-deployment ${{ secrets.STAGING_APP_ID_V18 }} \
            --image ghcr.io/${{ github.repository }}/odoo18:${{ github.sha }}
```

---

## 9. Monitoring & Alerting Setup

### 9.1 Odoo 18 Metrics Endpoint

```python
# addons/custom/prometheus_metrics/controllers/metrics.py

from odoo import http
from prometheus_client import Counter, Gauge, generate_latest

# Odoo 18 specific metrics
odoo18_requests = Counter('odoo18_http_requests_total', 'Total HTTP requests')
odoo18_active_users = Gauge('odoo18_active_users', 'Active users')

class MetricsController(http.Controller):

    @http.route('/metrics', type='http', auth='none')
    def metrics(self):
        """Prometheus metrics endpoint for Odoo 18"""
        odoo18_requests.inc()

        # Get active users
        users = http.request.env['res.users'].sudo().search_count([
            ('active', '=', True)
        ])
        odoo18_active_users.set(users)

        return http.request.make_response(
            generate_latest(),
            headers=[('Content-Type', 'text/plain')]
        )
```

---

## 10. Odoo 18 vs 19 Differences

### 10.1 Key Differences Summary

| Feature | Odoo 18 | Odoo 19 |
|---------|---------|---------|
| **Import: registry** | `from odoo import registry` ✅ | `from odoo.modules.registry import Registry` |
| **Import: xlsxwriter** | `from odoo.tools.misc import xlsxwriter` ✅ | `import xlsxwriter` |
| **self._uid** | Available ✅ | Removed ❌ |
| **_apply_ir_rules** | Available ✅ | Removed ❌ |
| **odoo.osv.Expressions** | Available ✅ | Deprecated ⚠️ |
| **Kanban Views** | `<kanban-box>` ✅ | `<card>` (OWL) |
| **JS Framework** | QWeb/Legacy | OWL Framework |
| **tax_id** | Single tax ✅ | `tax_ids` (Many2many) |
| **product_uom** | Direct field ✅ | `product_uom_id` |

### 10.2 Migration Planning Checklist

**Before migrating from Odoo 18 → 19:**

- [ ] Run `scripts/auto-patch/detect-odoo18-future-issues.sh`
- [ ] Update all manifests to version 19.0.x.x.x
- [ ] Test all custom modules in Odoo 19 staging
- [ ] Migrate custom JavaScript to OWL framework
- [ ] Update `tax_id` fields to `tax_ids`
- [ ] Replace `self._uid` with `self.env.uid`
- [ ] Remove usages of `_apply_ir_rules()`
- [ ] Update Docker images to `odoo:19.0`
- [ ] Run full test suite
- [ ] Create database backup
- [ ] Plan rollback procedure

---

## Quick Reference: Odoo 18 Specific

### Error Codes

| Error | Severity | Auto-Fix | Odoo 19 Impact |
|-------|----------|----------|----------------|
| `Missing module dependency` | High | ✅ Yes | Same |
| `Invalid __manifest__.py version` | Medium | ✅ Yes | Must be 19.0.x |
| `self._uid usage` | Low | N/A | ❌ Breaks in 19 |
| `_apply_ir_rules usage` | Medium | N/A | ❌ Breaks in 19 |

### Health Check Endpoints

Same as Odoo 19:
- Odoo: `/web/health`
- Superset: `/health`
- Supabase Edge: Function-specific

### Useful Commands

```bash
# Validate Odoo 18 setup
make odoo18:validate

# Prepare for Odoo 19 migration
bash scripts/auto-patch/prepare-for-odoo19.sh

# Check manifests
python3 scripts/auto-patch/validate_odoo18_manifests.py

# Test database connections
python3 auto-healing/remediation/fix_db_connections_odoo18.py
```

---

## 📝 Conclusion

This Odoo 18 guide provides:
1. **Version-specific troubleshooting** for Odoo 18 CE
2. **Future-proofing strategies** for Odoo 19 migration
3. **Backward-compatible patterns** that work in both versions
4. **Pre-migration checks** to identify issues early
5. **Auto-healing scripts** adapted for Odoo 18

**Key Takeaway:** Start preparing for Odoo 19 now by avoiding deprecated APIs and following forward-compatible coding practices.

---

**Related Documents:**
- [Odoo 19 Troubleshooting Guide](./COMPREHENSIVE_ERROR_TROUBLESHOOTING_GUIDE_ODOO19.md)
- [Auto-Healing README](../auto-healing/README.md)
- [SystemD Units README](../auto-healing/systemd/README.md)

**Document Version:** 1.0.0
**Author:** InsightPulse DevOps Team
**Last Review:** 2025-11-07

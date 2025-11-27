# Agent Services Hard Delete Checklist

**Created**: 2025-11-27
**Decommission Date**: 2025-11-27 22:34 UTC
**Stability Period**: 7 days (until 2025-12-04)
**Hard Delete**: After 2025-12-11 (2 weeks post-decommission)

---

## Background

On 2025-11-27, two dead agent services were decommissioned from the primary droplet (159.223.75.148):

- **agent-service** (port 8001): 7-line stub service with no business logic
- **ocr-adapter** (port 8002): Broken service (missing python-dateutil dependency)

Containers were stopped and removed, but **service directories remain on disk** for rollback capability.

---

## Removed Services Summary

| Service | Port | Location | Size (estimated) | Reason for Removal |
|---------|------|----------|------------------|--------------------|
| agent-service | 8001 | `/opt/services/services/agent-service/` | ~5MB | Stub service (7 lines, no functionality) |
| ocr-adapter | 8002 | `/opt/ocr-adapter/` | ~20MB | Broken (missing dependency, no callers) |

---

## 7-Day Stability Checklist

**Period**: 2025-11-27 to 2025-12-04

Track daily monitoring for any issues that might indicate the removed services were needed:

- [ ] **Day 1** (2025-11-28): ✅ No errors in Odoo logs, n8n workflows operational
- [ ] **Day 2** (2025-11-29): ✅ OCR service healthy, tax rules service healthy
- [ ] **Day 3** (2025-11-30): ✅ No unexpected Docker container restarts
- [ ] **Day 4** (2025-12-01): ✅ No service discovery errors or missing endpoint errors
- [ ] **Day 5** (2025-12-02): ✅ Mattermost notifications working (n8n workflows)
- [ ] **Day 6** (2025-12-03): ✅ BIR automation workflows operational
- [ ] **Day 7** (2025-12-04): ✅ Final health check - all services stable

**Verification Commands**:

```bash
# Daily health checks
ssh root@159.223.75.148 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
ssh root@159.223.75.148 "curl -sf http://127.0.0.1:8000/health"
ssh root@159.223.75.148 "curl -sf http://127.0.0.1:8003/health"

# Check for errors mentioning removed services
ssh root@159.223.75.148 "docker logs odoo-ce --since 24h | grep -iE 'agent-service|ocr-adapter|8001|8002' || echo 'No mentions found'"
ssh root@159.223.75.148 "docker logs n8n-n8n-1 --since 24h | grep -iE 'agent-service|ocr-adapter|8001|8002' || echo 'No mentions found'"
```

---

## Nginx Config Cleanup (Optional - P2)

**When**: After 7-day stability period (after 2025-12-04)

Check if nginx configs reference removed services:

```bash
# Search for references
ssh root@159.223.75.148 "grep -rn 'agent-service\|ocr-adapter\|:8001\|:8002' /etc/nginx/ || echo 'No references found'"

# If found, remove references (example)
ssh root@159.223.75.148 "
  cd /etc/nginx/sites-available
  sed -i.bak '/agent-service:8001/d' *.conf
  sed -i.bak '/ocr-adapter:8002/d' *.conf
  nginx -t && systemctl reload nginx
"
```

**Expected**: No references should be found (services were internal-only)

---

## Hard Delete Procedure

**Timing**: After 2025-12-11 (2 weeks post-decommission)

**Prerequisites**:
- [ ] 7-day stability checklist completed (all ✅)
- [ ] No errors or issues reported
- [ ] Final verification complete

### Step 1: Final Backup

```bash
# Create final archive before deletion
ssh root@159.223.75.148 "
  cd /opt
  tar czf /tmp/agent-services-final-backup-$(date +%Y%m%d).tar.gz \
    services/services/agent-service \
    ocr-adapter
"

# Copy to local machine
scp root@159.223.75.148:/tmp/agent-services-final-backup-*.tar.gz ~/backups/
```

### Step 2: Delete Service Directories

```bash
# Delete agent-service
ssh root@159.223.75.148 "
  rm -rf /opt/services/services/agent-service
  echo 'agent-service directory deleted'
"

# Delete ocr-adapter
ssh root@159.223.75.148 "
  rm -rf /opt/ocr-adapter
  echo 'ocr-adapter directory deleted'
"

# Verify deletion
ssh root@159.223.75.148 "
  ls -la /opt/services/services/ | grep agent-service || echo 'agent-service: NOT FOUND (deleted)'
  ls -la /opt/ | grep ocr-adapter || echo 'ocr-adapter: NOT FOUND (deleted)'
"
```

**Expected Output**:
```
agent-service: NOT FOUND (deleted)
ocr-adapter: NOT FOUND (deleted)
```

### Step 3: Docker Cleanup

```bash
# Remove unused images and volumes
ssh root@159.223.75.148 "docker system prune -a --volumes -f"

# Verify no dangling resources
ssh root@159.223.75.148 "
  docker images | grep -E 'agent-service|ocr-adapter' || echo 'No images found'
  docker volume ls | grep -E 'agent-service|ocr-adapter' || echo 'No volumes found'
"
```

**Expected**: No images or volumes related to removed services

### Step 4: Remove Docker Compose Backups (Optional)

```bash
# List backups
ssh root@159.223.75.148 "cd /opt/services && ls -la docker-compose.yml*"

# Keep only the latest backup, remove older ones
ssh root@159.223.75.148 "
  cd /opt/services
  # Keep docker-compose.yml and docker-compose.yml.bak-2025-11-28-063325
  rm -f docker-compose.yml.bak2 docker-compose.yml.bak3
  echo 'Removed old backups, kept latest'
"
```

### Step 5: Final Verification

```bash
# Verify all services still healthy after cleanup
ssh root@159.223.75.148 "
  echo '=== Container Status ==='
  docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
  echo ''
  echo '=== Health Checks ==='
  curl -sf http://127.0.0.1:8000/health && echo '✅ OCR service healthy'
  curl -sf http://127.0.0.1:8003/health && echo '✅ Tax rules service healthy'
  echo ''
  echo '=== Disk Space Freed ==='
  df -h / | tail -1
"
```

---

## Rollback (If Issues Arise)

If any issues are discovered during the stability period:

```bash
# Restore from backup
ssh root@159.223.75.148 "
  cd /opt/services
  cp docker-compose.yml.bak-2025-11-28-063325 docker-compose.yml
  docker compose up -d
"

# Verify services restarted
ssh root@159.223.75.148 "docker ps | grep -E 'agent-service|ocr-adapter'"
```

---

## Future Use of Port 8001

Once hard deletion is complete, port 8001 becomes available for the planned **ai-gateway** service:

**Proposed ai-gateway Architecture**:
```
ai-gateway (port 8001)
├─ /llm/chat → LLM routing (Anthropic, OpenAI, DeepSeek)
├─ /tools/ocr → Proxy to ocr-service (port 8000)
└─ /tools/tax → Proxy to tax_rules_service (port 8003)
```

This provides a unified API gateway for all AI/ML services.

---

## Completion Sign-off

After all steps complete:

- [ ] **Hard delete completed**: (Date: _________)
- [ ] **Final verification passed**: All services healthy
- [ ] **Backup archived**: Final backup stored at `~/backups/agent-services-final-backup-*.tar.gz`
- [ ] **Disk space freed**: ~25MB reclaimed
- [ ] **Port 8001 available**: Ready for ai-gateway service

**Signed off by**: _________________
**Date**: _________________

---

## Reference Documents

- INFRASTRUCTURE_PLAN.md - Section: "2025-11-27 – Agent Services Decommissioning (Post-Audit)"
- /tmp/decommission_complete.md - Complete decommissioning report
- /tmp/agent_services_analysis.md - Investigation findings
- /tmp/infra-decom-agents.sh - Decommissioning automation script

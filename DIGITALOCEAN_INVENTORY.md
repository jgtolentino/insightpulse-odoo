# DigitalOcean Resource Inventory

**Project:** fin-workspace (29cde7a1-8280-46ad-9fdf-dea7b21a7825)
**Environment:** Production
**Last Updated:** 2025-11-04

---

## 📊 Resource Summary

| Resource Type | Count | Monthly Cost (Est.) |
|--------------|-------|---------------------|
| Droplets | 2 | $48 ($24 × 2) |
| App Platform Apps | 2 | $10 ($5 × 2 basic-xxs) |
| Volumes | 1 | $10 (100GB) |
| Container Registry | 1 | $0 (free tier) |
| Databases | 0 | $0 |
| Load Balancers | 0 | $0 |
| **TOTAL** | **6** | **~$68/month** |

---

## 💧 Droplets (2)

### 1. ocr-service-droplet
```yaml
ID: 525178434
IP: 188.166.237.231
Region: sgp1 (Singapore)
Size: 4GB RAM / 2 vCPU / 80GB Disk
Status: active
Tags: [ocr, odoo, prod]
Cost: $24/month
```

**Services Running:**
- ✅ PaddleOCR-VL (Docker container, port 8000)
- ✅ DeepSeek-OCR-7B (systemd service, port 9888)
- ✅ Nginx reverse proxy
- ✅ Odoo (odoo-bundle, odoobo-odoo-1 containers)
- ✅ PostgreSQL (odoo-db, odoobo-db-1 containers)
- ✅ Superset (container, exited)

**DNS:** ocr.insightpulseai.net

**Attached Volumes:**
- odoobo-backup (100GB) - ID: 8b8b827e-afe3-11f0-93c2-0a58ac12c695

---

### 2. ipai-odoo-erp
```yaml
ID: 527891549
IP: 165.227.10.178
Region: sfo2 (San Francisco)
Size: 4GB RAM / 2 vCPU / 120GB Disk
Status: active
Tags: [clean-19-image-init]
Cost: $24/month
```

**Services Running:**
- ✅ Odoo 19 ERP with @ipai-bot (Mode 1)
- ✅ PostgreSQL database
- ✅ Custom IPAI modules

**DNS:** erp.insightpulseai.net

**Purpose:** Primary Odoo ERP instance with AI automation

---

## 🚀 App Platform (2 Apps)

### 1. superset
```yaml
App ID: 73af11cb-dab2-4cb1-9770-291c536531e6
Name: superset
URL: https://superset-nlavf.ondigitalocean.app
Custom Domain: superset.insightpulseai.net
Active Deployment: b4e709e0-9ab1-4629-87f7-f05c18bf0861
Tier: basic-xxs
Cost: $5/month
```

**Purpose:** Apache Superset BI dashboards for analytics

**Tech Stack:**
- Apache Superset 3.0
- PostgreSQL (connected to Supabase)
- Python 3.11

---

### 2. mcp (Pulse Hub Web)
```yaml
App ID: 844b0bb2-0208-4694-bf86-12e750b7f790
Name: mcp
URL: https://pulse-hub-web-an645.ondigitalocean.app
Custom Domain: mcp.insightpulseai.net
Active Deployment: a341cb21-2f75-4db9-b53c-25ac4fc7fa07
Tier: basic-xxs
Cost: $5/month
```

**Purpose:** Pulse Hub Web UI (Automation Mode 2)

**Tech Stack:**
- Next.js / React
- Vercel-compatible build
- One-click deployment interface

---

## 💾 Volumes (1)

### odoobo-backup
```yaml
ID: 8b8b827e-afe3-11f0-93c2-0a58ac12c695
Size: 100 GiB
Region: sgp1
Attached To: ocr-service-droplet (525178434)
Cost: $10/month
```

**Purpose:** Backup storage for Odoo filestore and database backups

**Mount Point:** /mnt/odoobo-backup (on droplet)

---

## 🐳 Container Registry (1)

### fin-workspace
```yaml
Name: fin-workspace
Endpoint: registry.digitalocean.com/fin-workspace
Region: sfo2
Storage: Free tier (500MB)
Cost: $0/month
```

**Purpose:** Docker image storage for custom builds

**Images:**
- jgtolentino/insightpulse-odoo:main (Odoo 19 custom image)
- Other custom containers

---

## 🔥 Firewalls (1)

### odoobo-fw
```yaml
ID: fb77861f-8402-44d3-b4c4-3e71696ac3fb
Name: odoobo-fw
Status: succeeded
```

**Inbound Rules:**
- TCP/22 (SSH)
- TCP/80 (HTTP)
- TCP/443 (HTTPS)

**Outbound Rules:**
- ICMP (all)
- TCP (all ports)
- UDP (all ports)

**Applied To:** ocr-service-droplet (likely)

---

## 🌐 VPCs (2)

### 1. default-sfo2
```yaml
ID: 810501ec-9ee6-47e1-b02c-cf42b3a942a7
Region: sfo2
IP Range: 10.120.0.0/20
```

**Purpose:** Default VPC for San Francisco region

**Resources:**
- ipai-odoo-erp droplet
- mcp App Platform app (likely)

---

### 2. default-sgp1
```yaml
ID: 0d3ec42e-f3ec-4c99-97ef-aa62d5db6b09
Region: sgp1
IP Range: 10.104.0.0/20
```

**Purpose:** Default VPC for Singapore region

**Resources:**
- ocr-service-droplet
- superset App Platform app (likely)

---

## 🤖 AI Agent Platform

### InsightPulse AI Agent
```yaml
Agent URL: https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/chat
Model: Claude 3.5 Sonnet
Purpose: Automation Mode 3 (AI Agent API)
Custom Domain: agent.insightpulseai.net (needs DNS fix)
Cost: Included in DO credits / pay-per-use
```

**Note:** AI Agents don't appear in standard `doctl apps list` - they're managed separately via DigitalOcean Agent Platform.

**Capabilities:**
- Natural language automation
- DigitalOcean infrastructure control
- Supabase database operations
- GitHub integration
- Odoo RPC operations

---

## 📦 Databases

**Managed Databases:** None (using external Supabase)

**Database Services:**
- **Supabase PostgreSQL:** spdtwktxdalcfigzeqrz (external, not in DO)
  - Project: InsightPulse
  - Region: AWS us-east-1
  - Connection: Pooler (port 6543)

**Self-Hosted Databases:**
- PostgreSQL 15 (on ocr-service-droplet) - Odoo database
- PostgreSQL 15 (on ipai-odoo-erp) - Odoo database

---

## 🌍 Geographic Distribution

### Singapore (sgp1)
- ✅ ocr-service-droplet (188.166.237.231)
- ✅ odoobo-backup volume
- ✅ superset App Platform app
- **Purpose:** OCR services, Odoo backup, BI analytics

### San Francisco (sfo2)
- ✅ ipai-odoo-erp (165.227.10.178)
- ✅ mcp (Pulse Hub Web) App Platform app
- ✅ Container Registry (fin-workspace)
- **Purpose:** Primary Odoo ERP, web UI, image storage

---

## 🔗 External Services (Not in DO)

### Supabase
```yaml
Project: spdtwktxdalcfigzeqrz
Service: PostgreSQL 15 + pgvector
Region: AWS us-east-1
URL: https://xkxyvboeubffxxbebsll.supabase.co
Connection: aws-1-us-east-1.pooler.supabase.com:6543
Cost: $0/month (free tier)
```

**Purpose:**
- Task queue (task_queue table)
- Visual parity baselines
- Scout transaction data
- Multi-tenant data storage

### Vercel (Frontend Alternative)
```yaml
Project: atomic-crm
URL: https://atomic-crm.vercel.app
Cost: $0/month (hobby tier)
```

**Purpose:** Alternative frontend deployment (if not using DO App Platform)

---

## 💰 Monthly Cost Breakdown

| Category | Service | Cost |
|----------|---------|------|
| **Compute** | ocr-service-droplet (4GB) | $24 |
| **Compute** | ipai-odoo-erp (4GB) | $24 |
| **App Platform** | superset (basic-xxs) | $5 |
| **App Platform** | mcp/Pulse Hub (basic-xxs) | $5 |
| **Storage** | odoobo-backup (100GB volume) | $10 |
| **Registry** | fin-workspace (free tier) | $0 |
| **AI Agent** | Claude 3.5 Sonnet API | ~$0-5 (usage-based) |
| **Supabase** | PostgreSQL + pgvector | $0 (free tier) |
| **Vercel** | Frontend hosting | $0 (hobby tier) |
| **Domain** | insightpulseai.net | $2/month |
| | **TOTAL** | **~$70/month** |

---

## 🎯 Four Automation Modes Mapping

| Mode | Interface | Infrastructure | URL |
|------|-----------|----------------|-----|
| **Mode 1** | Odoo Discuss (`@ipai-bot`) | ipai-odoo-erp droplet | https://erp.insightpulseai.net |
| **Mode 2** | Pulse Hub Web UI | mcp App Platform | https://mcp.insightpulseai.net |
| **Mode 3** | AI Agent API | DO Agent Platform | https://agent.insightpulseai.net |
| **Mode 4** | GitHub PR Bot (`@claude`) | GitHub webhooks | (no infrastructure) |

---

## 🔧 Management Commands

### Droplets
```bash
# List droplets
doctl compute droplet list

# Get droplet details
doctl compute droplet get 525178434
doctl compute droplet get 527891549

# SSH access
ssh root@188.166.237.231  # ocr-service-droplet
ssh root@165.227.10.178   # ipai-odoo-erp
```

### App Platform
```bash
# List apps
doctl apps list

# Get app details
doctl apps get 73af11cb-dab2-4cb1-9770-291c536531e6  # superset
doctl apps get 844b0bb2-0208-4694-bf86-12e750b7f790  # mcp

# View logs
doctl apps logs 73af11cb-dab2-4cb1-9770-291c536531e6 --follow
doctl apps logs 844b0bb2-0208-4694-bf86-12e750b7f790 --follow

# Create deployment
doctl apps create-deployment 73af11cb-dab2-4cb1-9770-291c536531e6 --force-rebuild
```

### Volumes
```bash
# List volumes
doctl compute volume list

# Snapshot volume
doctl compute volume-snapshot create odoobo-backup --snapshot-name odoobo-backup-$(date +%Y%m%d)
```

### Registry
```bash
# Login to registry
doctl registry login

# List repositories
doctl registry repository list

# List tags
doctl registry repository list-tags fin-workspace/insightpulse-odoo
```

---

## 🚨 Critical Resources

**DO NOT DELETE:**
1. ✅ ocr-service-droplet (525178434) - Hosts critical OCR services
2. ✅ ipai-odoo-erp (527891549) - Primary Odoo ERP instance
3. ✅ odoobo-backup volume - Contains critical backups
4. ✅ fin-workspace registry - Custom Docker images

**Can be recreated:**
- App Platform apps (superset, mcp) - Can redeploy from specs
- Firewalls - Rules can be recreated
- VPCs - Default VPCs auto-created

---

## 📋 Backup Strategy

### Daily Backups
- ✅ Odoo database → /mnt/odoobo-backup on ocr-service-droplet
- ✅ Odoo filestore → /mnt/odoobo-backup on ocr-service-droplet
- ⚠️ TODO: Automated volume snapshots

### Weekly Backups
- ⚠️ TODO: Volume snapshots to DigitalOcean Spaces
- ⚠️ TODO: Off-site backup to external storage

### Recovery Plan
1. Create new droplet from snapshot (if available)
2. Restore database from backup
3. Restore filestore from backup
4. Redeploy App Platform apps from specs

---

## 🔍 Health Monitoring

### Endpoints to Monitor
```bash
# Droplets
curl https://erp.insightpulseai.net/web/health
curl http://ocr.insightpulseai.net/health

# App Platform
curl https://superset.insightpulseai.net/health
curl https://mcp.insightpulseai.net/api/health

# OCR Services
curl http://ocr.insightpulseai.net/paddle/health
curl http://ocr.insightpulseai.net/deepseek/health

# AI Agent
curl https://wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run/health
```

### Resource Monitoring
```bash
# Droplet resource usage
ssh root@188.166.237.231 'free -h && df -h && uptime'
ssh root@165.227.10.178 'free -h && df -h && uptime'

# App Platform metrics (via DO dashboard)
# https://cloud.digitalocean.com/apps
```

---

**Maintained by:** Jake Tolentino
**Contact:** jgtolentino_rn@yahoo.com
**Last Audit:** 2025-11-04

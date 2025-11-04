# DNS Mapping for insightpulseai.net

**Domain:** insightpulseai.net
**Registrar:** Namecheap
**Last Updated:** 2025-11-04

---

## Current DNS Configuration

### ✅ Correct Records

| Subdomain | Type | Points To | Purpose | Status |
|-----------|------|-----------|---------|--------|
| `ocr.insightpulseai.net` | A | 188.166.237.231 | OCR Services (PaddleOCR + DeepSeek) | ✅ WORKING |
| `mcp.insightpulseai.net` | CNAME | pulse-hub-web-an645.ondigitalocean.app | Pulse Hub Web UI (Mode 2) | ✅ WORKING |
| `superset.insightpulseai.net` | CNAME | superset-nlavf.ondigitalocean.app | Apache Superset BI | ✅ WORKING |
| `erp.insightpulseai.net` | A | 165.227.10.178 | Odoo ERP (Mode 1: @ipai-bot) | ✅ WORKING |
| `www.insightpulseai.net` | CNAME | insightpulseai.net | WWW redirect | ✅ WORKING |
| `@` (root) | CAA | 0 issue "letsencrypt.org" | SSL certificate authority | ✅ WORKING |

### ⚠️ Issues Found

| Issue | Current State | Recommended Fix |
|-------|---------------|-----------------|
| **Duplicate `@` A records** | Two identical `@` → 165.227.10.178 | Keep only ONE |
| **Duplicate `agent` A records** | Two `agent` → 165.227.10.178 | Keep only ONE |
| **Wrong IP in agent record** | One `agent` → **65**.227.10.178 (typo) | Delete this (wrong IP) |
| **agent should use CNAME** | Currently A record | Change to CNAME → AI Agent URL |

---

## Recommended DNS Configuration

### Clean Configuration (Remove Duplicates)

```
Host: @
Type: A
Data: 165.227.10.178
Purpose: Root domain → Odoo ERP
Action: Keep only ONE, delete duplicate

Host: agent
Type: CNAME
Data: wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run
Purpose: AI Agent API (Mode 3)
Action: Delete both A records, add CNAME

Host: erp
Type: A
Data: 165.227.10.178
Purpose: Odoo ERP with @ipai-bot (Mode 1)
Action: Keep as-is ✓

Host: mcp
Type: CNAME
Data: pulse-hub-web-an645.ondigitalocean.app
Purpose: Pulse Hub Web UI (Mode 2)
Action: Keep as-is ✓

Host: ocr
Type: A
Data: 188.166.237.231
Purpose: OCR services (PaddleOCR + DeepSeek)
Action: Keep as-is ✓

Host: superset
Type: CNAME
Data: superset-nlavf.ondigitalocean.app
Purpose: Apache Superset BI
Action: Keep as-is ✓

Host: www
Type: CNAME
Data: insightpulseai.net
Purpose: WWW redirect
Action: Keep as-is ✓

Host: @
Type: CAA
Data: 0 issue "letsencrypt.org"
Purpose: SSL certificate authority
Action: Keep as-is ✓
```

---

## Four Automation Modes Mapping

| Mode | Interface | URL | DNS Record | Status |
|------|-----------|-----|------------|--------|
| **Mode 1** | Odoo Discuss (`@ipai-bot`) | https://erp.insightpulseai.net | `erp` → 165.227.10.178 | ✅ READY |
| **Mode 2** | Pulse Hub Web UI | https://mcp.insightpulseai.net | `mcp` → pulse-hub-web-an645.ondigitalocean.app | ✅ READY |
| **Mode 3** | AI Agent API | https://agent.insightpulseai.net | `agent` → wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run | ⚠️ NEEDS FIX |
| **Mode 4** | GitHub PR Bot (`@claude`) | (GitHub webhooks) | N/A - no DNS needed | ✅ READY |

---

## DNS Changes Required

### Step 1: Delete Duplicate Records

**In Namecheap DNS Settings:**

1. **Delete duplicate `@` A record:**
   - You have TWO `@` A records pointing to 165.227.10.178
   - Keep only ONE

2. **Delete BOTH `agent` A records:**
   - Delete `agent` → 65.227.10.178 (wrong IP - typo)
   - Delete `agent` → 165.227.10.178 (will replace with CNAME)

### Step 2: Add New CNAME for AI Agent

**Add this record:**
```
Host: agent
Type: CNAME
TTL: 1 hr
Data: wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run
```

This enables: https://agent.insightpulseai.net → AI Agent API

---

## Infrastructure Map

```
┌─────────────────────────────────────────────────┐
│         insightpulseai.net (Root Domain)        │
│              165.227.10.178                     │
│                  (Odoo ERP)                     │
└─────────────────────────────────────────────────┘
                       │
       ┌───────────────┼───────────────────┐
       │               │                   │
       ▼               ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ erp.         │ │ mcp.         │ │ ocr.         │
│ Mode 1       │ │ Mode 2       │ │ OCR Services │
│ @ipai-bot    │ │ Web UI       │ │ PaddleOCR    │
│              │ │              │ │ DeepSeek     │
│ 165.227.     │ │ DO App       │ │ 188.166.     │
│ 10.178       │ │ Platform     │ │ 237.231      │
└──────────────┘ └──────────────┘ └──────────────┘
       │               │                   │
       │               │                   │
       ▼               ▼                   ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ agent.       │ │ superset.    │ │ www.         │
│ Mode 3       │ │ BI           │ │ (redirect)   │
│ AI Agent API │ │ Dashboard    │ │              │
│              │ │              │ │              │
│ DO Agent     │ │ DO App       │ │ CNAME to @   │
│ Platform     │ │ Platform     │ │              │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## IP Address Inventory

| IP Address | Hostname | Services | Provider |
|------------|----------|----------|----------|
| **165.227.10.178** | erp.insightpulseai.net | Odoo ERP, @ipai-bot | DigitalOcean Droplet |
| **188.166.237.231** | ocr.insightpulseai.net | PaddleOCR-VL, DeepSeek-OCR-7B | DigitalOcean Droplet |

## DigitalOcean App Platform Apps

| App Name | App URL | Custom Domain | Purpose |
|----------|---------|---------------|---------|
| pulse-hub-web | pulse-hub-web-an645.ondigitalocean.app | mcp.insightpulseai.net | Web UI (Mode 2) |
| superset | superset-nlavf.ondigitalocean.app | superset.insightpulseai.net | BI Dashboard |
| ipai-agent | wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run | agent.insightpulseai.net | AI Agent API (Mode 3) |

---

## SSL/TLS Status

| Domain | SSL Provider | Status | Renewal |
|--------|--------------|--------|---------|
| erp.insightpulseai.net | Let's Encrypt | ⚠️ NEEDS SETUP | Manual |
| ocr.insightpulseai.net | Let's Encrypt | ⚠️ NEEDS SETUP | Manual |
| mcp.insightpulseai.net | DigitalOcean | ✅ AUTO | Auto |
| superset.insightpulseai.net | DigitalOcean | ✅ AUTO | Auto |
| agent.insightpulseai.net | DigitalOcean | ⚠️ AFTER DNS FIX | Auto |

---

## Next Steps

### Immediate Actions

1. **Fix DNS duplicates** (5 minutes)
   - Delete duplicate `@` A record
   - Delete both `agent` A records
   - Add `agent` CNAME → wr2azp5dsl6mu6xvxtpglk5v.agents.do-ai.run

2. **Add SSL for droplets** (10 minutes)
   - `ssh root@165.227.10.178` → Install certbot for erp.insightpulseai.net
   - `ssh root@188.166.237.231` → Install certbot for ocr.insightpulseai.net

3. **Test all 4 automation modes** (5 minutes)
   - Mode 1: Login to https://erp.insightpulseai.net → Test @ipai-bot
   - Mode 2: Open https://mcp.insightpulseai.net
   - Mode 3: Test https://agent.insightpulseai.net (after DNS fix)
   - Mode 4: Comment @claude in any GitHub PR

---

**Maintained by:** Jake Tolentino
**Last DNS Change:** 2025-11-04
**DNS Propagation:** ~5 minutes (Namecheap)
